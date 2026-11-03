# ADR-14 — Idempotência
**Architecture Decision Record · Projeto Steely · Escola de TI · UniCesumar**

| Campo | Valor | Campo | Valor |
| --- | --- | --- | --- |
| **Status** | ☒ Proposto  ☐ Aceito  ☐ Rejeitado  ☐ Substituído pelo ADR-___ | **Data** | 01/11/2026 |
| **Responsável** | Thiago Lopes Martins | **Sprint** | Sprint 8–9 / 15–17 (Entrega até 23/11) |
| **Participantes** | Thiago Lopes Martins, Fabrício Notoya Thomas, Augusto Palma Guglielmi, Pietro Pasqual Silva, Rafael Tudela Rizental | | |
| **Vínculos** | RNF-09 · RF-11 · RF-13..15 · RB-07..09 · STY037 · STY043 · STY044 · ADR-03 · ADR-10 · ADR-13 · ADR-15 · ADR-16 · ADR-23 | | |

## 1. Contexto *(obrigatória)*

O `RNF-09` exige chave de idempotência e trava de concorrência nas operações financeiras, de moedas e de leilão, para que falhas de rede não dupliquem lançamentos. No Steely há reenvio automático após uso offline (`STY028`, `ADR-23`), duplo toque em mobile e jobs agendados que podem rodar mais de uma vez (`ADR-16`).

Operações que não podem ser aplicadas duas vezes: crédito e débito de moedas (`RF-14`, `RB-08`, `RB-09`, `STY043`, `STY044`), confirmação de entrega por QR Code de uso único e retenção em escrow (`RF-11`, `RB-07`, `ADR-03`), liberação após 7 dias ou estorno em disputa (`RF-13`, `ADR-03`, `ADR-16`) e lance e encerramento de leilão (`RF-15`, `STY037`, `ADR-15`).

**Definido pelo grupo (`ADR-03`, `ADR-08`, `ADR-09`, `ADR-10`):** PostgreSQL no Supabase, sem Redis; ledger append-only no schema `ledger` (`ADR-10`); escrow simulado em `escrow.escrow` e `escrow.escrow_evento` no mesmo banco, operado por `private.reter_escrow`, `private.release_escrow` e `private.estornar_escrow` (`ADR-03`).

## 2. Direcionadores da decisão *(recomendada)*

- **Cumprir o `RNF-09` com zero duplicidade:** proteger reenvio de cliente, fila offline e jobs internos.
- **Funcionar para requisições HTTP e para jobs internos:** jobs não trazem cabeçalho de cliente, exigindo chave natural no banco.
- **Suportar a fila offline do app (`ADR-23`):** retenção de 72 h alinhada ao tempo máximo offline.
- **Custo zero e simplicidade:** usar transações e locks nativos do PostgreSQL sem Redis externo.

## 3. Opções consideradas *(obrigatória)*

| Opção A — Header Idempotency-Key + tabela de chaves | Opção B — Chaves naturais de negócio (constraints UNIQUE) | Opção C — Redis com lock distribuído (Redlock) |
| --- | --- | --- |
| **Descrição:** O cliente gera um UUID v4 por intenção. O servidor grava chave, hash do corpo e resposta numa tabela, na mesma transação do efeito.<br>**Prós:**<br>• Padrão conhecido.<br>• Devolve a mesma resposta no reenvio.<br>• Atende o RNF-09 literalmente.<br>**Contras:**<br>• Exige o cliente gerar a chave.<br>• Cria tabela e limpeza periódica (72 h). | **Descrição:** Cada operação tem identidade própria (ex. um único RELEASE por escrow) garantida por UNIQUE no banco.<br>**Prós:**<br>• Protege também jobs e processos internos.<br>• Sem coordenação com o cliente.<br>**Contras:**<br>• Sozinha não devolve o snapshot da resposta HTTP original; lances exigem chave por tentativa. | **Descrição:** Cache de chaves de idempotência e locks distribuídos Redlock em instância Redis externa.<br>**Prós:**<br>• Atende a letra de lock externo.<br>**Contras:**<br>• Infra extra fora do plano gratuito.<br>• Lock não é transacional com o PostgreSQL.<br>• Exagero para banco único. |

## 4. Decisão *(obrigatória)*

**Opção escolhida:** ☒ A (com ☒ B como segunda camada)  ☐ C

**Opção escolhida: A (Header `Idempotency-Key`), combinada com B (Chaves naturais UNIQUE) como segunda camada.** A Opção A cobre qualquer reenvio de cliente (web e fila offline Android). A Opção B garante que mesmo um job ou bug interno nunca duplique o efeito. C foi descartada: a trava do `RNF-09` é implementada com bloqueios nativos do PostgreSQL (`SELECT ... FOR UPDATE` e `pg_advisory_xact_lock`).

**Regras da Opção A:**
1. `Idempotency-Key` (UUID v4) obrigatório nos `POST` de lance, gasto/resgate de moedas, confirmação de entrega, boost e devolução (ausente → `400 IDEMPOTENCY_KEY_REQUIRED`).
2. Escopo por usuário e rota: mesma chave + mesmo corpo devolve a resposta gravada com `Idempotent-Replayed: true`; corpo diferente → `422 IDEMPOTENCY_KEY_REUSED`; ainda em processamento → `409 IDEMPOTENCY_IN_PROGRESS` com `Retry-After`.
3. Retenção de **72 h** (alinhada ao tempo máximo offline do `ADR-23`; após isso o `jti` único da `RB-07` ainda impede confirmação duplicada).

| Operação | Chave natural (UNIQUE — Opção B) |
| --- | --- |
| Retenção em escrow ao confirmar entrega (`ADR-03`) | `escrow.transaction_id`; o `jti` do QR é de uso único (`RB-07`) |
| Liberação ou estorno do escrow (`ADR-03`) | `UNIQUE (escrow_id, tipo_final)`, com máquina de estados de uma só saída |
| Crédito de moedas (Scanner, Captcha, laudo, cashback) | `UNIQUE (user_id, source_type, source_id)` |
| Débito de moedas e Lance | `UNIQUE (user_id, entry_type, idempotency_key)` e `UNIQUE (auction_id, user_id, idempotency_key)` |
| Arremate e débito do vencedor | `(auction_id, 'CLOSE')` e `(auction_id, 'WINNER_DEBIT')` |

**Execução e Armazenamento (`ADR-09`, `ADR-10`):** O FastAPI repassa `Idempotency-Key` à função SQL `SECURITY DEFINER` no schema `private` (que lê o usuário de `auth.uid()`). Nas operações de moedas, a chave fica no próprio `wallet_ledger` (`idempotency_key`, `request_hash`, `response_snapshot`). A tabela `idempotency_keys` fica para operações fora do ledger (entrega, devolução, Boost).

## 5. Consequências *(obrigatória)*

- **Positivas:** Reenvio, duplo toque e job duplicado deixam de gerar efeito duplo; demonstração simples; zero infraestrutura nova.
- **Negativas ou riscos aceitos:** Armazenamento do snapshot de resposta por 72 h (limpo por job no `ADR-16`); cliente precisa gerar e reaproveitar a chave no retry e na fila offline.
- **O que muda no código, banco e diagramas:** Tabela `idempotency_keys`; colunas de idempotência no ledger (`ADR-10`) e no escrow (`ADR-03`); funções SQL transacionais em `private`.

## 6. Validação *(recomendada)*

- Mesma chave enviada 2 vezes ou 50 requisições paralelas com a mesma chave: um único efeito no banco e a mesma resposta HTTP.
- Job de liberação (`sweep_custodia_7d`) executado duas vezes: uma única liberação.
- Mesma chave com corpo diferente: `422 IDEMPOTENCY_KEY_REUSED`.
- Confirmação de entrega offline reenviada após 24 h: aceita sem duplicar.

## 7. Plano de implementação *(recomendada)*

| Tarefa | Responsável | Sprint |
| --- | --- | --- |
| Tabela idempotency_keys e função SQL comum | Thiago | Sprint 8 (15) |
| Colunas e constraints no ledger (ADR-10) | Fabrício | Sprint 8 (15) |
| Funções de escrow e liberação conforme o ADR-03 | Augusto | Sprint 8 (16) |
| Geração e reuso da chave no cliente, incluindo fila offline | Pietro (web), Rafael (Android) | Sprint 8 (15–16) |
| Testes de reenvio e concorrência | Thiago | Sprint 9 (17) |

## 8. Referências *(recomendada)*

- IETF draft The Idempotency-Key HTTP Header Field; documentação de idempotência da Stripe.
- PostgreSQL: Explicit Locking e Advisory Locks.
- RNF-09, RF-11, RF-13, RF-14, RF-15, RB-07; ADR-03, ADR-10, ADR-13, ADR-15, ADR-16, ADR-23.

## Histórico de revisões

| Versão | Data | Autor | Alteração |
| --- | --- | --- | --- |
| 0.1 | 31/10/2026 | Thiago Lopes Martins | Rascunho inicial |
| 0.2 | 31/10/2026 | Thiago Lopes Martins | Cabeçalho lido pelo FastAPI e validado em função SQL (RPC); escrow simulado e banco alinhados ao ADR-08/09 |
| 0.3 | 31/10/2026 | Thiago Lopes Martins | Funções SECURITY DEFINER leem o usuário de auth.uid() (2º alinhamento do Fabrício) |
| 0.5 | 31/10/2026 | Thiago Lopes Martins | Chaves no wallet_ledger (ADR-10 v1.1) e chaves determinísticas para lançamentos internos |
| 0.6 | 31/10/2026 | Thiago Lopes Martins | Funções SQL no schema private, fora da Data API (ADR-09 v1.3) |
| 0.7 | 01/11/2026 | Thiago Lopes Martins | Retenção de 72 h alinhada ao tempo offline do Rafael (ADR-23) e tratamento das respostas na fila offline |
| 0.8 | 01/11/2026 | Thiago Lopes Martins | Escrow do ADR-03 confirmado: schema escrow e funções private.reter_escrow, release_escrow e estornar_escrow |

---

## Anexo — Texto Integral Detalhado (Documento Original)

ADR-14 — Idempotência
Architecture Decision Record · Projeto Steely · Escola de TI · UniCesumar
Versão Data Autor Alteração
0.1 31/10/2026 Thiago Lopes
Martins
Rascunho inicial
0.2 31/10/2026 Thiago Lopes
Martins
Decisão alterada de OpenAPI design-first para
code-first no FastAPI, alinhada ao ADR-09
(Fabrício)
0.3 31/10/2026 Thiago Lopes
Martins
Autenticação pelo FastAPI, limite de taxa,
health check; OpenAPI 3.1 e RFC 9457
padronizados (2º alinhamento do Fabrício)
0.4 31/10/2026 Thiago Lopes
Martins
Nome do snapshot igual ao da equipe
(openapi.snapshot.json); limites do slowapi
registrados
0.5 31/10/2026 Thiago Lopes
Martins
Cloudflare na borda (IP real, CORS), endpoints
internos com segredo e keep-alive por monitor
externo (3º alinhamento do Fabrício)
0.6 31/10/2026 Thiago Lopes
Martins
Data API desabilitada, IP real com CF-
Connecting-IP e fallback, token interno com
compare_digest e 202, Render como host e
health nos dois projetos com monitor
redundante
Campo Valor
Status ☒  Proposto ☐  Aceito ☐  Rejeitado ☐  Substituído
pelo ADR-___
Page 6 of 29
--- Page 7 ---
1. Contexto
O RNF-09 exige que retenção em escrow (7 dias), débitos e créditos de moedas e
arremates de leilão sejam atômicos e idempotentes, com Idempotency Key  e travas
distribuídas. O risco real é o reenvio: o app Android confirma entregas offline e sincroniza
depois (RNF-07, STY028), o WebSocket reconecta e pode reenviar um lance, o usuário
toca duas vezes, e as tarefas agendadas (ADR-16) podem rodar duas vezes. Cada reenvio
sem proteção credita, debita ou libera a custódia em dobro.
O sistema tem um único banco relacional (PostgreSQL, ADR-08), então a trava
"distribuída" pode ser entregue pelo próprio banco. Definido: PostgreSQL no Supabase
(ADR-08), FastAPI chamando funções SQL (RPC) do schema não exposto private (ADR-
09 v1.3) para tudo que mexe em moedas, e escrow como saldo contábil simulado no
schema escrow (ADR-03), movido por private.reter_escrow, private.release_escrow e
private.estornar_escrow. O ledger do ADR-10 v1.1 já traz a reserva do lance e as colunas de
idempotência.
2. Direcionadores da decisão
Correção: nunca creditar, debitar ou liberar duas vezes.
Sem infraestrutura nova nem custo (plano gratuito).
Cobrir reenvio de cliente e reexecução de job.
Esforço até 23/11 e facilidade de demonstrar: reenviar a mesma requisição e mostrar um
só efeito.
Compatibilidade com o ledger imutável (ADR-10).
Campo Valor
Data 31/10/2026
Responsável Thiago Lopes Martins
Sprint A definir (pergunta em aberto)
Participantes Thiago (autor). Revisão sugerida: Fabrício (ledger,
ADR-10), Augusto (escrow, ADR-03), Rafael
(reenvio offline)
Vínculos RNF-09 · RF-11, RF-13, RF-14, RF-15 · RB-07, RB-08,
RB-09 · STY037, STY043, STY044 · ADR-03, ADR-10,
ADR-13, ADR-15, ADR-16
Page 7 of 29
--- Page 8 ---
3. Opções consideradas
4. Decisão
Opção escolhida: ☒  A, com B como segunda camada. A cobre qualquer reenvio de
cliente. B garante que mesmo um job ou um bug interno não duplique o efeito. C foi
descartada: a trava distribuída do RNF-09 é implementada com bloqueios do PostgreSQL
( SELECT ... FOR UPDATE  e pg_advisory_xact_lock ), o que precisa ser aceito pela
equipe como atendimento do requisito.
Regras da Opção A.
1 . Idempotency-Key  (UUID v4) é obrigatório nos POST de: lance, gasto e resgate de
moedas, confirmação de entrega, pagamento de boost, pedido de devolução. Ausente:
400 IDEMPOTENCY_KEY_REQUIRED .
2. A chave vale por usuário e rota. Mesma chave com mesmo corpo devolve a resposta
gravada com o cabeçalho Idempotent-Replayed: true . Mesma chave com corpo
diferente: 422 IDEMPOTENCY_KEY_REUSED . Mesma chave ainda em processamento: 409
IDEMPOTENCY_IN_PROGRESS  com Retry-After .
3. A chave e o efeito de negócio gravam na mesma transação de banco. Retenção das
chaves: 72 h, que é o tempo máximo offline sugerido pelo Rafael para o ADR-23 (a
confirmar quando ele aplicar); depois disso o jti do QR, de uso único (RB-07), ainda
Opção A — Header
Idempotency-Key  +
tabela de chaves
Opção B — Chaves
naturais de negócio
(constraints únicas)
Opção C — Redis com
lock distribuído
Descrição O cliente gera um UUID
por intenção. O servidor
grava chave, hash do
corpo e resposta numa
tabela, na mesma
transação do efeito.
Cada operação tem
identidade própria (ex.
um único RELEASE por
escrow) garantida por
UNIQUE no banco.
Cache de chaves e
locks Redlock em um
Redis.
Prós Padrão conhecido.
Devolve a mesma
resposta no reenvio.
Atende o RNF-09
literalmente.
Protege também jobs e
processos internos. Sem
coordenação com o
cliente.
Atende a letra do RNF-
09.
Contras Exige o cliente gerar a
chave. Cria tabela e
limpeza periódica.
Não devolve a resposta
original. Lances não têm
chave natural.
Infra extra e fora do
plano gratuito. Lock
não é durável. Exagero
para um banco único.
Page 8 of 29
--- Page 9 ---
impede a confirmação duplicada. A fila offline reaproveita o mesmo Idempotency-Key
e trata as respostas assim: 409 IDEMPOTENCY_IN_PROGRESS espera o Retry-After,
Idempotent-Replayed: true conta como sucesso e 422 descarta o item da fila.
Chaves naturais da Opção B.
O FastAPI lê o cabeçalho Idempotency-Key e o repassa à função SQL (RPC), que valida a
chave e aplica o efeito na mesma transação. Transações de vários passos ficam dentro
dessas funções, nunca em chamadas separadas do FastAPI. Como as funções são
SECURITY DEFINER (ADR-09), o usuário é lido de auth.uid() e nunca de um parâmetro da
chamada. Elas ficam no schema private, fora da Data API (desabilitada), com search_path
= public, private, pg_temp (ADR-09 v1.3).
Onde ficam as chaves (ADR-10 v1.1). Nas operações de moedas, a chave fica no próprio
public.wallet_ledger : idempotency_key  (NOT NULL), request_hash  (SHA-256 do
corpo) e response_snapshot , com UNIQUE (user_id, entry_type, idempotency_key) .
A tabela idempotency_keys  fica só para as operações fora do ledger (confirmação de
entrega, devolução, pagamento de Boost). Lançamentos internos, sem cabeçalho do
cliente, usam uma chave determinística no mesmo campo: source_type:source_id  nos
créditos (ex. CAPTCHA_TASK:123 ), release:<bid_id>  no BID_RELEASE  e close:
<auction_id>  no BID_CAPTURE_BURN .
5. Consequências
Positivas: reenvio, duplo toque e job duplicado deixam de gerar efeito duplo; a
demonstração é simples; zero infraestrutura nova.
Operação Chave natural (UNIQUE)
Retenção em escrow ao confirmar entrega escrow.transaction_id ; o jti  do QR é de
uso único (RB-07)
Liberação ou estorno do escrow (escrow_id, tipo_final) , com máquina de
estados de uma só saída
Crédito de moedas (Scanner, Captcha,
laudo, cashback)
(user_id, source_type, source_id)
Débito de moedas (user_id, idempotency_key)
Lance (auction_id, user_id, idempotency_key)
Arremate e débito do vencedor (auction_id, 'CLOSE')  e (auction_id,
'WINNER_DEBIT')
Page 9 of 29
--- Page 10 ---
Negativas ou riscos aceitos: cada endpoint crítico guarda a resposta (mais
armazenamento); a limpeza das chaves vira um job (ADR-16); o cliente precisa gerar e
reaproveitar a chave no retry, inclusive na fila offline; a leitura do RNF-09 (trava no banco,
não Redis) pode ser questionada na banca.
O que muda: nova tabela idempotency_keys ; colunas idempotency_key , source_type  e
source_id  no ledger (definidas no ADR-10 v1.1); funções SQL transacionais para escrow,
moedas e leilão; parâmetro e códigos de erro no contrato (ADR-13).
6. Validação
Mesma chave enviada 2 vezes: um único lançamento no ledger e a mesma resposta.
50 requisições paralelas com a mesma chave: um único efeito.
Job de liberação executado duas vezes: uma única liberação.
Mesma chave com corpo diferente: 422.
Falha injetada após o commit e antes da resposta: o retry devolve a resposta original.
Confirmação de entrega offline reenviada após 24 h: aceita sem duplicar.
7. Plano de implementação
8. Referências
IETF draft The Idempotency-Key HTTP Header Field; documentação de idempotência
da Stripe.
PostgreSQL: Explicit Locking e Advisory Locks.
RNF-09, RF-11, RF-13, RF-14, RF-15, RB-07; ADR-03, ADR-10, ADR-13, ADR-15, ADR-16.
Tarefa Responsável Sprint
Tabela idempotency_keys  e função SQL comum Thiago A
definir
Colunas e constraints no ledger Fabrício (ADR-10) A
definir
Funções de escrow e liberação conforme o ADR-
03
Augusto A
definir
Geração e reuso da chave no cliente, incluindo
fila offline
Pietro (web), Rafael
(Android)
A
definir
Testes de reenvio e concorrência Thiago A
definir
Page 10 of 29
--- Page 11 ---
Histórico de revisões
