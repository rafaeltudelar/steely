# ADR-16 — Tarefas agendadas
**Architecture Decision Record · Projeto Steely · Escola de TI · UniCesumar**

| Campo | Valor | Campo | Valor |
| --- | --- | --- | --- |
| **Status** | ☒ Proposto  ☐ Aceito  ☐ Rejeitado  ☐ Substituído pelo ADR-___ | **Data** | 01/11/2026 |
| **Responsável** | Thiago Lopes Martins | **Sprint** | Sprint 8–9 / 15–17 (Entrega até 23/11) |
| **Participantes** | Thiago Lopes Martins, Fabrício Notoya Thomas, Augusto Palma Guglielmi, Pietro Pasqual Silva, Rafael Tudela Rizental | | |
| **Vínculos** | STY028 · C3 Matriz CSD · RNF-09 · RB-03 · RB-13..14 · RF-09..11 · RF-13..15 · ADR-03..08 · ADR-10 · ADR-14 · ADR-15 · ADR-21 · ADR-22 · ADR-25 | | |

## 1. Contexto *(obrigatória)*

Várias regras do Steely acontecem quando um prazo vence, sem ninguém clicar em nada. O banco é PostgreSQL com `pg_cron` e `pg_net` no Supabase (`ADR-08`) e a custódia é um saldo contábil simulado no schema `escrow` (`ADR-03`):

| Prazo / Job | Origem | Efeito | Precisão |
| --- | --- | --- | --- |
| 48 h sem resposta do vendedor | `RB-03` | Cancela reserva; oferta volta a Disponível; lembrete 6 h antes (`ADR-25`) | Minutos |
| 7 dias após a entrega (`sweep_custodia_7d`) | `RF-11`, `RF-13`, `ADR-03` | Chama `private.release_escrow(transaction_id)` se não houver devolução, laudo ou disputa; `entregue_em` definido pelo servidor | Minutos |
| 24 h de proposta de lote / Agendamento sem resposta | `RF-09`, `STY025`, `RB-05` | Cancela proposta de lote; expira agendamento sem resposta; tolerância de 1 h no encontro aplica strike | Minutos |
| 3 dias de mediação e resposta à devolução; 72 h SLA moderador | `RF-13`, `BPMN P5b`, `ADR-06` | Revelia do vendedor (3 dias) gera estorno automático auditado com direito a recurso em 10 dias (`STY034`); SLA de 72 h do moderador em `app_config` | Minutos |
| Fim do leilão (a cada 10 s) e 48 h para retirada | `RF-15`, `STY037`, `ADR-15` | Fecha leilão (`ends_at <= now()`); se vencedor não agendar em 48 h, aplica penalidade e oferece ao 2º colocado (`STY037-RN04`) | Segundos |
| 30 dias sem solicitação; 15 dias inativa | `RB-13`, `RB-14` | Expira oferta; sugere Ecoponto | Diária |
| 365 dias expiração FIFO de moedas (alertas 30 e 7 dias) | `RF-14`, `ADR-10` | Expira lote vencido (`expires_at`) ou carteira inativa há 365 dias (`last_activity_at`); moedas em `BID_HOLD` não expiram | Diária |
| Carência de exclusão em 30 dias (`sweep_exclusao_30d`) | `STY010`, `RNF-03`, `ADR-07` | Aviso por e-mail 7 dias antes; ao vencer 30 dias chama `private.anonimizar_usuario(user_id)`; avaliações viram `"Usuário removido"` | Diária |
| Sincronização DaaS (`/api/v1/internal/jobs/sync-daas`) | `ADR-04` | Agrega no Projeto 1 (`k >= 30` transações e `>= 3` vendedores distintos por recorte) e grava no Projeto 2 via `asyncpg` | Diária |
| Partições de logs (12 m / 60 m) e `private.audit_verify` | `ADR-05`, `RNF-11` | Cria partição do mês seguinte, descarta > 12 m (sistema) e > 60 m (financeiro) e valida a cadeia de hash diariamente | Diária |
| Limpeza de `idempotency_keys` (72 h), `auth_login_attempts` (24 h) e `cron.job_run_details` (7 d) | `ADR-14`, `ADR-21` | Remove chaves expiradas, bloqueios de login antigos (LGPD) e histórico verboso do cron | Horas |
| Refresh horário do schema `esg` e Keep-alive externo (10 min) | `ADR-08`, `ADR-22` | `REFRESH MATERIALIZED VIEW CONCURRENTLY` em `esg.*`; UptimeRobot + GitHub Actions chamam `GET /api/v1/health` (Core + DaaS) | Horas / Min |

## 2. Direcionadores da decisão *(recomendada)*

- **Idempotência e consistência transacional com o dado (`RNF-09`, `ADR-14`):** rodar dentro do PostgreSQL 24/7 sem depender de processo Node/Python sempre acordado.
- **Efeitos externos confiáveis (push, e-mail, DaaS):** outbox + `pg_net` acionando webhooks internos do FastAPI (`ADR-25`).
- **Demonstrabilidade na banca:** simular o vencimento de 48 h e 7 dias ao vivo em minutos via endpoint administrativo auditado.

## 3. Opções consideradas *(obrigatória)*

| Opção A — pg_cron com funções SQL + outbox + pg_net | Opção B — Edge Functions (Supabase) | Opção C — Worker dedicado com fila (BullMQ / Celery) |
| --- | --- | --- |
| **Descrição:** O pg_cron roda varreduras SQL idempotentes sobre colunas de prazo e usa tabela outbox + pg_net para acionar webhooks do FastAPI.<br>**Prós:**<br>• Sem servidor novo e gratuito.<br>• Transacional com os dados.<br>• Banco Supabase fica ativo 24/7.<br>**Contras:**<br>• Exige outbox + pg_net para efeitos externos (push, e-mail). | **Descrição:** Funções em TypeScript/Deno disparadas por agendamento ou HTTP.<br>**Prós:**<br>• Faz chamadas HTTP externas direto.<br>**Contras:**<br>• Segundo ambiente de código (Deno vs Python).<br>• Não é transacional com o banco e consome cota do plano gratuito. | **Descrição:** Processo sempre ligado com fila de jobs atrasados.<br>**Prós:**<br>• Controle por item em memória.<br>**Contras:**<br>• Exige hospedagem paga sempre ligada e Redis. |

## 4. Decisão *(obrigatória)*

**Opção escolhida:** ☒ A  ☐ B  ☐ C

**Opção escolhida: A — `pg_cron` com funções SQL `SECURITY DEFINER` no schema `private` + tabela `outbox` + `pg_net` chamando webhooks do FastAPI.** Os prazos ficam guardados no próprio dado (`responder_ate`, `custodia_libera_em`) em UTC (`now()` do banco; 7 dias = 168 h). As varreduras usam `FOR UPDATE SKIP LOCKED` e filtro pelo estado atual, tornando qualquer repetição inofensiva.

- **Outbox e Webhooks (`ADR-13`, `ADR-25`):** As varreduras gravam eventos na `outbox` e o `pg_net` chama `POST /api/v1/internal/jobs/*` com `X-Internal-Token` (validado com `secrets.compare_digest`), que responde `202 Accepted` e processa em `BackgroundTasks`. O FastAPI marca o status do evento na `outbox` antes de enviar o push para evitar duplicidade.
- **7 dias da garantia (`ADR-03`, `ADR-23`):** `custodia_libera_em = entregue_em + 168 h`, onde `entregue_em` é sempre definido pelo relógio do servidor ao receber a confirmação do QR Code (mesmo quando sincronizada depois pelo app offline).
- **Modo demonstração para a banca (`fast-forward-timers`):** O endpoint `POST /api/v1/admin/demo/fast-forward-timers` (restrito a `ADMIN`, aceitando `p_now` nas funções SQL) simula na defesa ao vivo o vencimento das 48 h (`RB-03`) e dos 7 dias (`ADR-03`), registrando tudo na auditoria. **Após a banca, o endpoint e a massa sintética `"DEMONSTRAÇÃO"` são desligados e removidos (`ADR-03`, `ADR-04`, `ADR-16`).**

## 5. Consequências *(obrigatória)*

- **Positivas:** Zero servidor novo; efeito e dado na mesma transação; todas as regras temporais do BPMN usam um único mecanismo; a defesa mostra o prazo vencendo ao vivo em minutos.
- **Negativas ou riscos aceitos:** Depende das extensões `pg_cron` e `pg_net` do Supabase; tolerância de até 5 min para regras de horas/dias (e 10 s para fechamento de leilão); exige limpeza semanal de `cron.job_run_details`.
- **O que muda no código, banco e diagramas:** Colunas de prazo, tabela `app_config`, tabela `outbox`, funções `sweep_*` no schema `private` e webhooks internos no FastAPI.

## 6. Validação *(recomendada)*

- Reserva com `responder_ate` no passado: a varredura `sweep_reservas_48h` devolve a oferta a Disponível na primeira execução e nada faz na segunda.
- Entrega com `custodia_libera_em` no passado sem disputa: `sweep_custodia_7d` libera o escrow uma única vez; com devolução ou disputa aberta, não libera.
- Demonstração na defesa: reserva criada → `POST /api/v1/admin/demo/fast-forward-timers` → expiração e notificação vistas ao vivo e auditadas.

## 7. Plano de implementação *(recomendada)*

| Tarefa | Responsável | Sprint |
| --- | --- | --- |
| Colunas de prazo e tabela app_config (incluindo SLA 72 h moderador e k ≥ 30) | Thiago e Fabrício | Sprint 8 (15) |
| sweep_reservas_48h, sweep_custodia_7d e sweep_exclusao_30d | Thiago | Sprint 8 (16) |
| private.reter_escrow, release_escrow e estornar_escrow (ADR-03) | Augusto | Sprint 8 (16) |
| Outbox e webhook de notificações no FastAPI (ADR-25) | Thiago e Rafael | Sprint 8 (16) |
| Demais varreduras da tabela do contexto (DaaS, logs, ESG, moedas) | Dono de cada módulo | Sprint 8–9 (16–17) |
| Modo demonstração fast-forward-timers e desligamento após a banca | Thiago | Sprint 9 (17) / Pós-banca |

## 8. Referências *(recomendada)*

- Documentação do `pg_cron` e do `pg_net` no Supabase; padrão Transactional Outbox.
- BPMN P34 e P5b; RB-03, RB-13, RB-14, STY028, STY037, RNF-09.
- ADR-03, ADR-04, ADR-05, ADR-06, ADR-07, ADR-08, ADR-10, ADR-14, ADR-15, ADR-21, ADR-22, ADR-25.

## Histórico de revisões

| Versão | Data | Autor | Alteração |
| --- | --- | --- | --- |
| 0.1 | 31/10/2026 | Thiago Lopes Martins | Rascunho inicial |
| 0.2 | 31/10/2026 | Thiago Lopes Martins | Notificações por webhook do FastAPI em vez de Edge Functions; prazos dos ADR-04, 05 e 14 incluídos |
| 0.3 | 31/10/2026 | Thiago Lopes Martins | Keep-alive, envio ao Projeto 2 do DaaS, descarte de partição de logs e expiração FIFO incluídos (2º alinhamento do Fabrício) |
| 0.4 | 31/10/2026 | Thiago Lopes Martins | Expiração de moedas e descarte de logs financeiros marcados para reconciliação; efeito do ping no Supabase marcado como não confirmado |
| 0.5 | 31/10/2026 | Thiago Lopes Martins | Keep-alive por monitor externo; logs em duas tabelas; expiração de moedas unificada; DaaS por webhook (3º alinhamento do Fabrício) |
| 0.6 | 31/10/2026 | Thiago Lopes Martins | Webhooks com compare_digest e BackgroundTasks, keep-alive redundante com alerta, /health nos dois bancos e endpoint admin fast-forward-timers para a banca |
| 0.7 | 31/10/2026 | Thiago Lopes Martins | Refresh horário do schema esg (ADR-22), limpeza de auth_login_attempts (ADR-21) e de cron.job_run_details, e varredura do leilão a cada 10 s |
| 0.8 | 01/11/2026 | Thiago Lopes Martins | Status do evento na outbox antes do reenvio e aviso de fim de leilão com o ends_at atual (ADR-25) |
| 0.9 | 01/11/2026 | Thiago Lopes Martins | Escrow confirmado, entregue_em definido no servidor, revelia do vendedor com estorno automático, sweep_exclusao_30d com anonimizar_usuario e audit_verify diário |
| 0.10 | 01/11/2026 | Thiago Lopes Martins | Prazo de 72 h do moderador em app_config, aviso de 7 dias antes do fim da carência de exclusão e desligamento do endpoint de demonstração após a banca |

---

## Anexo — Texto Integral Detalhado (Documento Original)

ADR-16 — Tarefas agendadas
Architecture Decision Record · Projeto Steely · Escola de TI · UniCesumar
Versão Data Autor Alteração
0.1 31/10/2026 Thiago Lopes
Martins
Rascunho inicial
0.2 31/10/2026 Thiago Lopes
Martins
Opção escolhida mudou de A para C (SELECT
FOR UPDATE), alinhada ao ADR-09; limites do
Realtime gratuito registrados
0.3 31/10/2026 Thiago Lopes
Martins
Parâmetros do leilão confirmados; usuário lido
de auth.uid(); limite do Realtime gratuito aceito
até 23/11
0.4 31/10/2026 Thiago Lopes
Martins
Ausência de taxa em dinheiro registrada; lance
automático segue em aberto
0.5 31/10/2026 Thiago Lopes
Martins
Ordem de lock com duas carteiras,
lançamentos BID_* do ADR-10 v1.1, regra do
líder e lance automático fora do MVP
0.6 31/10/2026 Thiago Lopes
Martins
Função em private.rpc_place_auction_bid com
checagens repetidas (status, KYC, Trust
Score); STY037-RN04 como prazo de 48 h para
retirada; lance automático fora do MVP
aprovado
Campo Valor
Status ☒  Proposto ☐  Aceito ☐  Rejeitado ☐  Substituído
pelo ADR-___ (alinhado ao ADR-08 proposto pelo
Fabrício)
Data 31/10/2026
Responsável Thiago Lopes Martins
Sprint A definir (pergunta em aberto)
Participantes Thiago (autor). Revisão sugerida: Augusto (escrow,
ADR-03), Fabrício (banco, ADR-08), Rafael
(notificações, ADR-25)
Page 16 of 29
--- Page 17 ---
1. Contexto
Hoje duas regras dependem do tempo: cancelar a reserva se o vendedor não responder
em 48 h (RB-03) e liberar a custódia 7 dias após a leitura do QR Code (STY028, RF-11, RF-
13). O BPMN e os requisitos trazem outras regras com prazo que precisam do mesmo
mecanismo, e escolher um agendador só para duas delas obrigaria a escolher outro
depois. O conteúdo de C3 da Matriz CSD não está nos documentos que recebi; peço o
texto.
Campo Valor
Vínculos STY028, C3 da Matriz CSD, RNF-09 · RB-03, RB-13,
RB-14 · RF-09, RF-11, RF-13, RF-14, RF-15 · ADR-03,
ADR-08, ADR-14, ADR-15, ADR-25
Prazo Origem Efeito Precisão
necessária
48 h sem resposta do
vendedor
RB-03 Cancela reserva; oferta volta a
Disponível
Minutos
7 dias após a entrega RF-11, RF-
13
Libera repasse, se não houver
devolução, laudo em análise ou
disputa
Minutos
24 h de proposta de lote RF-09 Cancela proposta e libera itens Minutos
3 dias de mediação e de
resposta à devolução
RF-13,
BPMN
P5b
Escala à arbitragem ou defere ao
comprador; a revelia do vendedor (3
dias sem resposta) gera estorno
automático, auditado, com direito a
escalamento em 10 dias (STY034,
ADR-06); o prazo de resposta do
moderador é de 3 dias (72 h),
guardado em app_config
Minutos
Fim do leilão (muda com
anti-sniping) e prazo de
48 h para confirmar a
retirada
RF-15,
STY037
Fecha leilão; se o vencedor não
agenda a retirada em 48 h, aplica a
penalidade, estorna o saldo e oferece
o lote ao 2º colocado (STY037-RN04)
Segundos
30 dias sem solicitação;
15 dias inativa
RB-13,
RB-14
Expira oferta; sugere Ecoponto Diária
Page 17 of 29
--- Page 18 ---
Prazo Origem Efeito Precisão
necessária
365 dias sem login (RF-
14) ou após o crédito
(ADR-10), com alertas
aos 30 e 7 dias
RF-14 Expira moedas por lote, do mais
antigo ao mais novo (FIFO, ADR-10); o
ADR-10 v1.1 unificou as regras: expira
o que ocorrer primeiro, lote vencido
(lot.expires_at) ou conta sem login
nem movimento há 365 dias
(wallet.last_activity_at); moedas em
BID_HOLD não expiram
Diária
Carência de exclusão e
expurgo em 30 dias
STY010,
RNF-03
sweep_exclusao_30d chama
private.anonimizar_usuario(user_id)
(ADR-07), que anonimiza e elimina; 7
dias antes do fim da carência de 30
dias envia e-mail de aviso, e as
avaliações recebidas por terceiros
passam a exibir o autor como
"Usuário removido"
Diária
Agendamento sem
resposta; tolerância de 1
h
STY025,
RF-10,
RB-05
Expira; aplica strike Minutos
Envio dos pacotes
anonimizados do DaaS
ao Projeto 2
ADR-04 O pg_cron aciona o webhook
/api/v1/internal/jobs/sync-daas, que
agrega no Projeto 1 (HAVING
COUNT(DISTINCT transacao_id) >=
30), remove identificadores e grava
no Projeto 2 por asyncpg
Diária
Retenção e descarte
dos logs de auditoria
ADR-05,
RNF-11
Cria a partição do mês seguinte nas
duas tabelas; descarta as de
audit.system_and_access_logs com
12 meses e as de
audit.financial_and_dispute_logs com
60 meses
Diária
Verificação da cadeia
de hash dos logs
ADR-05 Executa private.audit_verify para
validar a cadeia de hash dos logs
Diária
Page 18 of 29
--- Page 19 ---
Definido pelo Fabrício (ADR-08): PostgreSQL com pg_cron  no Supabase. A custódia é um
saldo contábil simulado no schema escrow (ADR-03), liberado por private.release_escrow
e devolvido por private.estornar_escrow.
2. Direcionadores da decisão
Idempotência e consistência com o dado (RNF-09, ADR-14).
Sem servidor sempre ligado nem custo no plano gratuito.
Efeitos externos necessários: push, e-mail, PDF (ADR-25).
Observabilidade e auditoria de cada execução (RNF-05, RNF-11).
Poder demonstrar na defesa: 48 h e 7 dias não cabem numa apresentação.
Esforço até 23/11.
Prazo Origem Efeito Precisão
necessária
Limpeza das chaves de
idempotência (72 h), do
auth_login_attempts e
do cron.job_run_details
ADR-14 Remove chaves expiradas; apaga de
auth_login_attempts (ADR-21) os
registros com bloqueado_ate há mais
de 24 h, para não acumular IPs e e-
mails sem necessidade (LGPD); e
apaga de cron.job_run_details as
linhas com mais de 7 dias, porque a
varredura de 10 s do leilão gera 8.640
linhas por dia
Horas
Refresh horário das
views materializadas do
schema esg (painel
ESG)
ADR-22 REFRESH MATERIALIZED VIEW
CONCURRENTLY em
esg.usuario_mensal e
esg.plataforma_mensal, lidas por
private.esg_resumo_usuario e
private.esg_resumo_plataforma (k ≥
30 por região)
Horas
Keep-alive externo
(UptimeRobot, com
redundância no GitHub
Actions): GET
/api/v1/health a cada 10
min, fora do pg_cron
ADR-08,
ADR-09
Evita a hibernação do Render e conta
como tráfego externo nos dois
projetos Supabase
Minutos
Atividade no Projeto 2
do DaaS
ADR-04,
ADR-08
O /health também lê o Projeto 2,
então o keep-alive externo cobre os
dois
Diária
Page 19 of 29
--- Page 20 ---
3. Opções consideradas
4. Decisão
Opção escolhida: ☒  A. Os prazos ficam guardados no próprio dado (ex. responder_ate ,
custodia_libera_em ) e o pg_cron  roda varreduras idempotentes direto no banco, como
decidido pelo Fabrício: o banco do Supabase fica ativo 24/7, enquanto a API gratuita
hiberna sem tráfego. As varreduras gravam um evento numa tabela outbox, e o pg_net
chama um webhook do FastAPI, que envia push (FCM ou Expo Push) e e-mail; o pg_cron
reenvia a cada minuto os eventos sem confirmação (o FastAPI marca o status do evento
na outbox antes de enviar, para não repetir o push quando o reenvio do pg_cron e as
tentativas do próprio FastAPI se cruzam; o aviso de leilão prestes a encerrar lê o ends_at
atual, porque o anti-sniping o prorroga, ADR-15), o que cobre o tempo de despertar do
FastAPI. A Opção B (Edge Functions) não será usada, para manter um único ambiente de
código (Python). As chamadas do pg_net chegam à internet pública com o cabeçalho X-
Internal-Token (ADR-13), e o FastAPI valida o token com secrets.compare_digest (segredo
no Supabase Vault), responde 202 Accepted de imediato e processa em
BackgroundTasks. As funções de varredura são SECURITY DEFINER (ADR-09). O keep-
alive não é job do pg_cron: chamadas internas do banco não contam contra a pausa de 7
dias do Supabase, então o UptimeRobot chama GET /api/v1/health a cada 10 minutos, com
Opção A — pg_cron
com funções SQL
Opção B — Edge
Functions (Supabase)
Opção C — Worker
dedicado com fila
(BullMQ, pg-boss)
Descrição O pg_cron  roda, a cada
minuto, funções SQL que
varrem prazos vencidos.
Funções em TypeScript
disparadas por
agendamento ou HTTP.
Processo Node sempre
ligado com jobs
atrasados por item.
Prós Sem infraestrutura.
Transacional com os
dados. Idempotente pelo
próprio estado. Atende
as regras de minutos e
dias.
Faz efeitos externos
(push, e-mail, PDF).
Escreve em TypeScript,
o mesmo do front.
Controle total,
retentativas e prazo
exato por item.
Contras Só funciona com
PostgreSQL. Efeitos
externos exigem pg_net
ou outbox.
Observabilidade
limitada.
Cota e limites de
execução do plano
gratuito. Entrega ao
menos uma vez, então
exige idempotência.
Não é transacional com
o banco.
Exige hospedagem
sempre ligada (fora do
plano gratuito ou com
sleep). Mais
infraestrutura e
monitoramento.
Page 20 of 29
--- Page 21 ---
um workflow do GitHub Actions como segunda chamada e alerta imediato por e-mail ou
Discord da equipe se o /health falhar, o que evita os 15 minutos de hibernação do Render; o
/health faz ping na API dos dois projetos Supabase (Core e DaaS) e devolve {"status": "ok",
"core_db": "up", "daas_db": "up"}, o que conta como tráfego externo. C foi descartada: não
há hospedagem gratuita confiável para um processo sempre ligado.
Regras de projeto.
1 . Varredura idempotente. O filtro pelo estado atual (ex. status = 'RESERVADO' AND
responder_ate <= now() ) torna a repetição inofensiva; lote com FOR UPDATE SKIP
LOCKED  evita execuções sobrepostas.
2. 48 h (RB-03). responder_ate = reserva_em + 48 h , renovado quando o vendedor
responde. Ao vencer: oferta volta a Disponível, propostas e agendamentos da reserva
são cancelados e o QR é invalidado, sem strike.
3. 7 dias (RF-11, RF-13). custodia_libera_em = entregue_em + 7 × 24 h . Ao vencer, se
não houver devolução, laudo em análise ou disputa, chama
release_escrow(transaction_id)  conforme o ADR-03 (função
private.release_escrow), com chave natural única (ADR-14). O entregue_em é definido
no servidor, na hora em que ele recebe a confirmação de entrega, mesmo quando o app
a sincroniza depois, e não pelo relógio do aparelho. Liberação antecipada por laudo
validado é evento, não varredura.
4. Fim de leilão (ADR-15). Varredura a cada 10 segundos (o pg_cron do Supabase,
v1.5 ou superior, aceita intervalos de 1 a 59 segundos, confirmado com o
Fabrício; a confirmar na versão do projeto ) que só fecha se ends_at <= now() .
5. Horário. Tudo em UTC e now()  do banco; "7 dias" são 168 horas.
6. Tolerância. Atraso de até 5 minutos nas regras de horas e dias é aceito.
7. Modo demonstração. Além do pg_cron real, o endpoint POST /api/v1/admin/demo/fast-
forward-timers, restrito ao perfil ADMIN, simula na defesa ao vivo o vencimento das 48
h da reserva (RB-03) e dos 7 dias da garantia (ADR-03), rodando as mesmas
varreduras, e cada uso fica na auditoria. Depois da banca, o endpoint e a massa
sintética DEMONSTRAÇÃO são desligados e removidos (registrado nos ADR-03, ADR-
04 e ADR-16). As funções aceitam um p_now  para testes.
8. Auditoria. Cada execução registra nome, run_id , quantidade processada e
Correlation ID ; o atraso acima de 5 minutos gera alerta.
5. Consequências
Positivas: sem servidor novo; efeito e dado na mesma transação; as regras do BPMN usam
um único mecanismo; a defesa mostra o prazo vencendo em minutos.
Page 21 of 29
--- Page 22 ---
Negativas ou riscos aceitos: acoplamento ao PostgreSQL; lógica de negócio em SQL, mais
difícil de depurar; atenção à hospedagem gratuita (Render), que hiberna sem tráfego; o
keep-alive é redundante (UptimeRobot e GitHub Actions) e avisa por e-mail ou Discord se
o /health falhar; o endpoint de demonstração é um caminho de código a mais, restrito a
ADMIN e que deve ser desligado depois da banca.
O que muda: colunas de prazo nas tabelas de oferta, transação, proposta, agendamento e
carteira; tabelas app_config  e outbox ; funções sweep_* ; extensões pg_cron  (e
pg_net ) habilitadas; um endpoint de webhook no FastAPI; o diagrama de arquitetura
ganha o agendador.
6. Validação
Reserva criada com p_now  48 h atrás: a varredura cancela e devolve a oferta a
Disponível.
Custódia com 7 dias vencidos: liberada uma única vez, mesmo com a varredura
rodando duas vezes; bloqueada se houver devolução aberta.
Teste ponta a ponta em modo demonstração, do QR até a liberação, em menos de 10
minutos.
O histórico de execuções ( cron.job_run_details  e a tabela de auditoria) mostra
todas as rodadas, sem atraso acima de 5 minutos em 24 h de observação.
7. Plano de implementação
8. Referências
Documentação do pg_cron  e do pg_net.
PostgreSQL: SELECT ... FOR UPDATE SKIP LOCKED .
RB-03, RB-13, RB-14; RF-09, RF-11, RF-13, RF-14, RF-15; BPMN P34, P5 e P5b; STY028.
Tarefa Responsável Sprint
Colunas de prazo e app_config Thiago com Fabrício A definir
sweep_reservas_48h  e sweep_custodia_7d Thiago A definir
release_escrow Augusto (ADR-03) A definir
Outbox e webhook de notificações no FastAPI Thiago e Rafael (ADR-25) A definir
Demais varreduras da tabela do contexto Dono de cada módulo A definir
Modo demonstração e endpoint administrativo Thiago A definir
Page 22 of 29
--- Page 23 ---
ADR-03, ADR-08, ADR-14, ADR-15, ADR-25.
Histórico de revisões
Versão Data Autor Alteração
0.1 31/10/2026 Thiago Lopes
Martins
Rascunho inicial
0.2 31/10/2026 Thiago Lopes
Martins
Notificações por webhook do FastAPI em vez
de Edge Functions; prazos dos ADR-04, 05 e 14
incluídos
0.3 31/10/2026 Thiago Lopes
Martins
Keep-alive, envio ao Projeto 2 do DaaS,
descarte de partição de logs e expiração FIFO
incluídos (2º alinhamento do Fabrício)
0.4 31/10/2026 Thiago Lopes
Martins
Expiração de moedas e descarte de logs
financeiros marcados para reconciliação;
efeito do ping no Supabase marcado como não
confirmado
0.5 31/10/2026 Thiago Lopes
Martins
Keep-alive por monitor externo; logs em duas
tabelas; expiração de moedas unificada; DaaS
por webhook (3º alinhamento do Fabrício)
0.6 31/10/2026 Thiago Lopes
Martins
Webhooks com compare_digest e
BackgroundTasks, keep-alive redundante com
alerta, /health nos dois bancos e endpoint
admin fast-forward-timers para a banca
0.7 31/10/2026 Thiago Lopes
Martins
Refresh horário do schema esg (ADR-22),
limpeza de auth_login_attempts (ADR-21) e de
cron.job_run_details, e varredura do leilão a
cada 10 s
0.8 01/11/2026 Thiago Lopes
Martins
Status do evento na outbox antes do reenvio e
aviso de fim de leilão com o ends_at atual
(ADR-25)
0.9 01/11/2026 Thiago Lopes
Martins
Escrow confirmado, entregue_em definido no
servidor, revelia do vendedor com estorno
automático, sweep_exclusao_30d com
anonimizar_usuario e audit_verify diário
Page 23 of 29
--- Page 24 ---
