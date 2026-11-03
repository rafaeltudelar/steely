# ADR-15 — Concorrência dos lances
**Architecture Decision Record · Projeto Steely · Escola de TI · UniCesumar**

| Campo | Valor | Campo | Valor |
| --- | --- | --- | --- |
| **Status** | ☒ Proposto  ☐ Aceito  ☐ Rejeitado  ☐ Substituído pelo ADR-___ | **Data** | 01/11/2026 |
| **Responsável** | Thiago Lopes Martins | **Sprint** | Sprint 8–9 / 15–17 (Entrega até 23/11) |
| **Participantes** | Thiago Lopes Martins, Fabrício Notoya Thomas, Augusto Palma Guglielmi, Pietro Pasqual Silva, Rafael Tudela Rizental | | |
| **Vínculos** | RF-15 · R-08 · RNF-04 · RNF-06 · RNF-09 · STY037 · RB-09 · ADR-08..10 · ADR-13 · ADR-14 · ADR-16 · ADR-18 · ADR-25 | | |

## 1. Contexto *(obrigatória)*

Nos segundos finais de um leilão (`RF-15`), vários usuários dão lance ao mesmo tempo. O `R-08` (Matriz GUT, score 75) trata de lances simultâneos, queda de conexão e anti-sniping; o `RNF-06` pede propagação em tempo real ≤ 100 ms; o `RNF-09` pede idempotência e trava; o `RNF-04` pede escrita p99 ≤ 500 ms.

Regras de negócio: lance exige KYC, Trust Score ≥ 70% e método de pagamento cadastrado como garantia antifraude (`STY037`), além de bloquear a taxa de participação de 5 moedas da carteira na hora (`HOLD`) e devolver a do licitante superado (`RELEASE`), sem converter moedas em dinheiro nem abater do preço do lote (`RB-09`); lance nos minutos finais prorroga o término (anti-sniping, `STY037-RN02`).

Parâmetros confirmados (`PRM-56..58`, `ADR-08`, `ADR-10`): janela anti-sniping de **60 s**, extensão de **+120 s** sem teto de extensões, incremento mínimo configurável (padrão R$ 5,00 = 500 centavos) e taxa fixa de 5 moedas em `BID_HOLD`.

## 2. Direcionadores da decisão *(recomendada)*

- **Um único lance vencedor por nível de preço** e ordem determinística definida pelo servidor.
- **Transação única:** lance, reserva das 5 moedas (`BID_HOLD`), devolução ao líder anterior (`BID_RELEASE`) e prorrogação anti-sniping na mesma transação SQL, sem saldo negativo e sem deadlock.
- **Baixa latência (`RNF-04`, `RNF-06`) e Custo Zero:** escrita p99 ≤ 500 ms e propagação ≤ 100 ms via Supabase Realtime, sem infraestrutura extra.

## 3. Opções consideradas *(obrigatória)*

| Opção A — Bloqueio otimista (compare-and-set) | Opção B — Fila serializada por leilão | Opção C — Bloqueio pessimista (SELECT ... FOR UPDATE) + lastSeenBid |
| --- | --- | --- |
| **Descrição:** Um UPDATE condicional na linha do leilão só vence se o lance ainda for válido; quem perde recebe 409 com o estado atual.<br>**Prós:**<br>• Sem lock longo na linha do leilão.<br>• Simples em SQL.<br>**Contras:**<br>• O bloqueio da carteira para o HOLD já exige lock na mesma transação, então A não elimina o lock. | **Descrição:** Lances entram numa fila externa e um único consumidor por leilão os processa em ordem.<br>**Prós:**<br>• Ordem determinística sem retentativa.<br>**Contras:**<br>• Exige fila e worker sempre ligado (fora do plano gratuito).<br>• Ponto único de falha e maior latência. | **Descrição:** A função SQL trava a linha do leilão e depois as carteiras em ordem de user_id, valida lastSeenBid e grava tudo na mesma transação.<br>**Prós:**<br>• Serializa no próprio PostgreSQL sem retentativa cega.<br>• Ordem determinística de locks evita deadlock.<br>• Zero infra extra.<br>**Contras:**<br>• Transações concorrentes no mesmo leilão aguardam em fila de micro-segundos no banco. |

## 4. Decisão *(obrigatória)*

**Opção escolhida:** ☐ A  ☐ B  ☒ C (com verificação de versão `lastSeenBid` da A)

**Opção escolhida: C — Bloqueio pessimista (`SELECT ... FOR UPDATE`) combinado com a verificação de versão (`lastSeenBid`) da Opção A.** O FastAPI recebe o lance e chama a função SQL `private.rpc_place_auction_bid` (`place_bid`), que trava a linha do leilão e depois as carteiras sempre em ordem de `user_id` para evitar deadlock. Se `lastSeenBid` estiver defasado, responde `409 BID_OUTDATED` com o estado atual e não tenta de novo.

**Passos de `private.rpc_place_auction_bid(auction_id, valor, lastSeenBid, idempotency_key)` numa única transação:**
1. Confere a chave de idempotência (`ADR-14`) e lê o usuário de `auth.uid()`.
2. Trava a linha do leilão (`FOR UPDATE`) e depois as carteiras do licitante e do líder anterior em ordem de `user_id` (`ORDER BY user_id FOR UPDATE`).
3. Confere leilão aberto, `now() < ends_at`, valor ≥ vigente + incremento e `lastSeenBid` atual; repete no SQL `status = 'ACTIVE'`, `kyc_verified = TRUE` (`RB-01`) e `trust_score >= 70` (`RB-10`) como defesa em profundidade (`ADR-09`). Se o usuário já for o líder vigente, recusa com `409 ALREADY_LEADING`.
4. **Reserva de moedas (`ADR-10`):** Debita 5 moedas do novo licitante como `BID_HOLD` (movendo de `balance_available` para `balance_locked`) e devolve as 5 moedas do líder anterior com `BID_RELEASE` (chave determinística `release:<bid_id>`). Lance automático fica fora do MVP.
5. **Anti-sniping (`STY037-RN02`):** Se `ends_at - now() <= 60s`, atualiza `ends_at = ends_at + interval '120 seconds'` e incrementa `extension_count`.
6. Insere o lance como `LEADING`, marca o anterior como `OUTBID` e atualiza a linha do leilão, disparando evento no Supabase Realtime para clientes abertos (≤ 100 ms, `RNF-06`) e reagendando o push de encerramento (`ADR-25`).

**Encerramento (`close_auction`, `ADR-16`):** Quando `now() >= ends_at`, fecha o leilão e converte o `BID_HOLD` do vencedor em `BID_CAPTURE_BURN` (chave `close:<auction_id>`). Se o vencedor não confirmar a retirada em 48 h (`STY037-RN04`), aplica penalidade e oferece ao 2º colocado.

## 5. Consequências *(obrigatória)*

- **Positivas:** Impossível ter dois vencedores no mesmo preço ou saldo negativo; lance, reserva de moedas e anti-sniping são atômicos; uma escrita no leilão dispara um único evento no Realtime.
- **Negativas ou riscos aceitos:** Em disputa no último segundo, um usuário vence e os demais recebem `409 BID_OUTDATED` já com o valor atualizado para confirmarem se desejam cobrir; plano gratuito do Supabase Realtime suporta 200 conexões simultâneas (aceito até a defesa em 23/11).
- **O que muda no código, banco e diagramas:** Tabelas `auctions` e `bids`; funções `private.rpc_place_auction_bid` e `close_auction`; canal Realtime do leilão.

## 6. Validação *(recomendada)*

- 50 clientes enviando o mesmo valor ao mesmo tempo (k6, `ADR-17`): exatamente 1 recebe `201` e 49 recebem `409 BID_OUTDATED`.
- Ao fim do teste, apenas o líder atual tem `BID_HOLD` ativo; todos os anteriores receberam `BID_RELEASE`; nenhum saldo ficou negativo.
- Lance nos últimos 60 s prorroga `ends_at` em +120 s e propaga via Realtime em ≤ 100 ms p95 (`RNF-06`).

## 7. Plano de implementação *(recomendada)*

| Tarefa | Responsável | Sprint |
| --- | --- | --- |
| Modelo auctions e bids | Thiago e Fabrício | Sprint 8 (15) |
| Função private.rpc_place_auction_bid e close_auction | Thiago | Sprint 8 (16) |
| BID_HOLD / BID_RELEASE / BID_CAPTURE_BURN no ledger (ADR-10) | Fabrício | Sprint 8 (15–16) |
| Tela do leilão: tratamento de 409 e contagem regressiva | Pietro e Rafael | Sprint 8–9 (16–17) |
| Testes de concorrência e carga (k6 / pgTAP) | Thiago | Sprint 9 (17) |

## 8. Referências *(recomendada)*

- PostgreSQL: Concurrency Control e Explicit Locking; Supabase Realtime.
- RF-15, R-08, RNF-04, RNF-06, RNF-09, STY037, RB-09; ADR-08, ADR-09, ADR-10, ADR-13, ADR-14, ADR-16, ADR-18, ADR-25.

## Histórico de revisões

| Versão | Data | Autor | Alteração |
| --- | --- | --- | --- |
| 0.1 | 31/10/2026 | Thiago Lopes Martins | Rascunho inicial |
| 0.2 | 31/10/2026 | Thiago Lopes Martins | Opção escolhida mudou de A para C (SELECT FOR UPDATE), alinhada ao ADR-09; limites do Realtime gratuito registrados |
| 0.3 | 31/10/2026 | Thiago Lopes Martins | Parâmetros do leilão confirmados; usuário lido de auth.uid(); limite do Realtime gratuito aceito até 23/11 |
| 0.4 | 31/10/2026 | Thiago Lopes Martins | Ausência de taxa em dinheiro registrada; lance automático segue em aberto |
| 0.5 | 31/10/2026 | Thiago Lopes Martins | Ordem de lock com duas carteiras, lançamentos BID_* do ADR-10 v1.1, regra do líder e lance automático fora do MVP |
| 0.6 | 31/10/2026 | Thiago Lopes Martins | Função em private.rpc_place_auction_bid com checagens repetidas (status, KYC, Trust Score); STY037-RN04 como prazo de 48 h para retirada; lance automático fora do MVP aprovado |

---

## Anexo — Texto Integral Detalhado (Documento Original)

ADR-15 — Concorrência dos lances
Architecture Decision Record · Projeto Steely · Escola de TI · UniCesumar
Versão Data Autor Alteração
0.1 31/10/2026 Thiago Lopes
Martins
Rascunho inicial
0.2 31/10/2026 Thiago Lopes
Martins
Cabeçalho lido pelo FastAPI e validado em
função SQL (RPC); escrow simulado e banco
alinhados ao ADR-08/09
0.3 31/10/2026 Thiago Lopes
Martins
Funções SECURITY DEFINER leem o usuário
de auth.uid() (2º alinhamento do Fabrício)
0.5 31/10/2026 Thiago Lopes
Martins
Chaves no wallet_ledger (ADR-10 v1.1) e
chaves determinísticas para lançamentos
internos
0.6 31/10/2026 Thiago Lopes
Martins
Funções SQL no schema private, fora da Data
API (ADR-09 v1.3)
0.7 01/11/2026 Thiago Lopes
Martins
Retenção de 72 h alinhada ao tempo offline do
Rafael (ADR-23) e tratamento das respostas
na fila offline
0.8 01/11/2026 Thiago Lopes
Martins
Escrow do ADR-03 confirmado: schema
escrow e funções private.reter_escrow,
release_escrow e estornar_escrow
Campo Valor
Status ☒  Proposto ☐  Aceito ☐  Rejeitado ☐  Substituído
pelo ADR-___
Data 31/10/2026
Responsável Thiago Lopes Martins
Sprint A definir (pergunta em aberto)
Participantes Thiago (autor). Revisão sugerida: Fabrício (banco e
ledger, ADR-08/10), Pietro (tela do leilão), Rafael
(app)
Page 11 of 29
--- Page 12 ---
1. Contexto
O RF-15 define leilões com lances só em moedas virtuais, incremento mínimo de 3% sobre
o valor vigente ou 10 moedas (o que for maior) e anti-sniping: lance válido nos últimos
minutos prorroga o cronômetro em 3 minutos. O RNF-06 exige propagação em até 100 ms
para 1.000 conexões por leilão. O R-08 não está nos documentos que recebi; assumo que
trata de inconsistência em operações concorrentes e preciso do texto para confirmar.
O perfil de disputa é de poucos licitantes ativos por leilão (muitos espectadores) e pico
nos segundos finais. Invariantes que nunca podem quebrar: o lance aceito supera o
vigente mais o incremento no instante da gravação; o saldo cobre o lance; o prazo
estendido muda na mesma transação do lance; o leilão fecha uma única vez; o relógio é o
do servidor. Definido: PostgreSQL no Supabase (ADR-08), escrita pelo FastAPI e eventos
pelo Supabase Realtime (ADR-09).
2. Direcionadores da decisão
Correção sob concorrência (nenhum lance perdido, duplicado ou fora de ordem).
Latência de escrita p99 ≤ 500 ms (RNF-04) e propagação ≤ 100 ms (RNF-06).
Sem fila ou worker extra: infraestrutura mínima no plano gratuito.
Esforço até 23/11 e facilidade de demonstrar a disputa na defesa.
Compatibilidade com idempotência (ADR-14) e com o ledger (ADR-10).
3. Opções consideradas
Campo Valor
Vínculos RF-15, R-08 · RNF-06, RNF-09, RNF-04 · STY037 ·
RB-09 · ADR-08, ADR-10, ADR-13, ADR-14, ADR-16
Opção A — Bloqueio
otimista (compare-and-
set no banco)
Opção B — Fila
serializada por leilão
Opção C — Bloqueio
pessimista ( SELECT ...
FOR UPDATE )
Descrição Um UPDATE  condicional
na linha do leilão só
vence se o lance ainda
for válido; quem perde
recebe 409 com o
estado atual.
Lances entram numa fila
e um único consumidor
por leilão os processa
em ordem.
A transação trava a
linha do leilão, valida e
grava.
Page 12 of 29
--- Page 13 ---
4. Decisão
Opção escolhida: ☒  C, com a verificação de versão da A. Alinhada ao ADR-09 do Fabrício:
o FastAPI recebe o lance e chama a função SQL private.rpc_place_auction_bid
(chamada de place_bid no resto desta ADR) , que trava a linha do leilão com SELECT
... FOR UPDATE  e depois a da carteira, sempre nessa ordem, para evitar deadlock. O
cliente envia lastSeenBid , o último valor que viu; se estiver defasado, a função responde
409 BID_OUTDATED  com o estado atual e não tenta de novo. Esta ADR chegou a propor a
Opção A ( UPDATE  condicional sem lock); troquei para C porque o bloqueio da carteira
para o HOLD  já é necessário na mesma transação, então A não eliminaria o lock e ainda
trataria as duas linhas por caminhos diferentes. B foi descartada pelo custo de
infraestrutura. Gatilho de revisão: se o p99 de escrita passar de 500 ms ou a espera por
lock aparecer num teste de carga, reavaliar A.
Função place_bid(auction_id, valor, lastSeenBid, idempotency_key) , numa
transação:
1 . Confere a chave de idempotência (ADR-14) e lê o usuário de auth.uid(), nunca de um
parâmetro.
2. Trava a linha do leilão ( FOR UPDATE ) e depois as carteiras do licitante e do líder
anterior, em ordem de user_id (ORDER BY user_id FOR UPDATE), para não haver
deadlock.
3. Confere leilão aberto, now() < ends_at , valor igual ou maior que o vigente mais o
incremento e lastSeenBid  atual; o FastAPI valida KYC, Trust Score ≥ 70% e método de
pagamento cadastrado (garantia antifraude, STY037) antes da chamada, e a própria
função repete status = 'ACTIVE', kyc_verified = TRUE (RB-01) e trust_score ≥ 70 (RB-
10), como defesa em profundidade (ADR-09 v1.3). Qualquer falha: 409 ou 422 conforme
o ADR-13.
Opção A — Bloqueio
otimista (compare-and-
set no banco)
Opção B — Fila
serializada por leilão
Opção C — Bloqueio
pessimista ( SELECT ...
FOR UPDATE )
Prós Sem lock longo. Simples
em SQL. A ordem é a do
commit. Sem
infraestrutura nova.
Ordem determinística e
sem retentativa. Fácil de
raciocinar.
Serializa sem
retentativa de
aplicação. Sem
infraestrutura nova.
Contras O perdedor refaz a
tentativa; sob disputa
quente no fim
aparecem mais 409.
Exige fila e processo
sempre ligado (cai no
ADR-16). Ponto único de
falha. Mais latência e
complexidade.
Transações esperam
umas pelas outras no
pico. Risco de lock
prolongado se a
transação demorar.
Page 13 of 29
--- Page 14 ---
4. Bloqueia as moedas do líder e libera as do líder anterior ( HOLD  e RELEASE  no ledger).
Lançamentos do ADR-10 v1.1: BID_HOLD (disponível menos o lance, bloqueado mais o
lance) e BID_RELEASE para o líder superado, na mesma transação.
5. Grava o lance, atualiza valor vigente, líder e ends_at ; o Supabase Realtime avisa a sala
depois do commit.
Regra anti-sniping (janela e teto alinhados com o Fabrício; o RF-15 e o BPMN P6a fixam 3
minutos):
Janela: lance nos últimos 3 minutos antes do fim.
Efeito: ends_at = ends_at + 3 min , como no RF-15.
Teto: no máximo 10 prorrogações (30 minutos), sugestão do Fabrício aceita aqui.
Relógio: só o do servidor decide; o cliente apenas mostra a contagem, ajustada por um
deslocamento enviado pelo servidor.
Lance automático (previsto no STY037) fica fora do MVP até 23/11, por decisão da
equipe (o RF-15 e o BPMN P6a só exigem lance manual); o STY037 passa a prever só o
lance manual síncrono. Não há taxa em dinheiro para participar; o método de
pagamento cadastrado é só garantia antifraude (STY037-RN01, confirmado com o
Fabrício).
Fechamento: a tarefa do ADR-16 só fecha se ends_at <= now()  (a prorrogação pode ter
movido o fim), de forma idempotente (chave natural (auction_id, 'CLOSE') , ADR-14).
Captura e líder. No fechamento, o vencedor recebe BID_CAPTURE_BURN , que queima o
valor bloqueado e abate os lotes de crédito mais antigos primeiro (FIFO, ADR-10). Quem já
lidera não pode dar outro lance (409 ALREADY_LEADING ), para BID_HOLD  e BID_RELEASE
nunca disputarem a mesma carteira. Decisão da equipe para o STY037-RN04: como as
moedas já foram queimadas no fechamento, o prazo passa a ser de 48 h após o arremate
para o vencedor confirmar o resgate ou agendar a retirada do hardware. Se desistir ou não
agendar, aplica-se a penalidade prevista (retenção de multa e queda no Trust Score),
estorna-se o saldo remanescente e o lote é oferecido ao 2º colocado pelo valor do seu
último lance (ADR-10 v1.2).
5. Consequências
Positivas: sem fila nem worker; ordem dos lances igual à do commit; regra única no banco,
usada por web e Android; fácil de testar com concorrência real.
Negativas ou riscos aceitos: o cliente precisa tratar 409 e mostrar o valor atual; em
disputa quente os lances esperam na fila do lock, o que aumenta a latência; o teto de
prorrogações é uma regra nova sobre o RF-15; o plano gratuito do Supabase Realtime
permite 200 conexões simultâneas e 100 mensagens por segundo, abaixo das 1.000
Page 14 of 29
--- Page 15 ---
conexões do RNF-06; esse desvio é aceito até 23/11 e fica registrado. Chegar a 1.000
conexões exige o plano Pro sem teto de gastos (10.000 conexões e 2.500 mensagens por
segundo), com custo variável.
O que muda: tabelas auctions  (valor vigente, líder, ends_at , contagem de prorrogações,
status) e bids ; função SQL place_bid ; lançamentos HOLD , RELEASE  e CAPTURE  no
ledger (ADR-10); eventos bid.accepted , auction.extended  e auction.closed  no
AsyncAPI (ADR-13); tentativas rejeitadas vão para o log de auditoria (RNF-05), não para
bids .
6. Validação
50 lances simultâneos no mesmo leilão: valores aceitos estritamente crescentes,
exatamente um líder, saldo bloqueado coerente e nenhum saldo negativo.
Anti-sniping com relógio controlado nos testes: prorroga na janela, não prorroga fora
dela, para no teto.
Fechamento executado duas vezes: um único vencedor e um único débito.
Carga: p99 de escrita ≤ 500 ms e propagação ≤ 100 ms medidos com k6; o número de
conexões suportado no plano gratuito é registrado, mesmo que fique abaixo de 1.000.
7. Plano de implementação
8. Referências
PostgreSQL: Concurrency Control (Read Committed) e Explicit Locking.
RF-15, RNF-04, RNF-06, RNF-09, RB-09; STY037.
ADR-08, ADR-10, ADR-13, ADR-14, ADR-16.
Histórico de revisões
Tarefa Responsável Sprint
Modelo auctions  e bids Thiago com Fabrício A definir
Função place_bid  e close_auction Thiago A definir
HOLD/RELEASE/CAPTURE no ledger Fabrício (ADR-10) A definir
Tela do leilão: tratamento de 409 e contagem
regressiva
Pietro e Rafael A definir
Testes de concorrência e carga Thiago A definir
Page 15 of 29
--- Page 16 ---
