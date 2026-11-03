# ADR-08 — Banco principal
*Architecture Decision Record · Projeto Steely · Escola de TI · UniCesumar*

| Campo | Valor | Campo | Valor |
| :--- | :--- | :--- | :--- |
| **Status** | ☒ Proposto ☐ Aceito ☐ Rejeitado ☐ Substituído pelo ADR-___ | **Data** | 01/11/2026 |
| **Responsável** | Fabrício Notoya Thomas | **Sprint** | Sprint 8 (15–17) |
| **Participantes** | Fabrício Notoya Thomas, Augusto Palma Guglielmi, Thiago Lopes Martins, Pietro Pasqual Silva, Rafael Tudela Rizental | | |
| **Vínculos** | `R-08` · `EDTS-49` · `RNF-04` · `RNF-06` · `RNF-07` · `RNF-08` · `RNF-09` · `RF-06` · `ADR-03` · `ADR-04` · `ADR-05` · `ADR-06` · `ADR-07` · `ADR-09` · `ADR-10` · `ADR-15` · `ADR-16` · `ADR-18` · `ADR-21` · `ADR-22` · `ADR-23` | | |

---

## 1. Contexto *(obrigatória)*
A plataforma Steely exige um Sistema Gerenciador de Banco de Dados (SGBD) relacional com garantias estritas de atomicidade, consistência, isolamento e durabilidade (`ACID`) para sustentar operações críticas de negócio, incluindo: custódia financeira simulada de 7 dias (`escrow` — `RF-11`, `RF-13`), carteira contábil de moedas virtuais (`RF-14`, `RNF-09`), disputas de lances em leilões (`RF-15`, `RNF-06`), busca textual tolerante a erros de digitação (`STY020-RN02`) e filtragem geoespacial por raio de distância (`RF-06`, `RF-18`).

Durante a elaboração da Matriz GUT, surgiu uma inconsistência documental que cita o **SQLite**, enquanto os requisitos de concorrência (`R-08`), disponibilidade (`RNF-08` — SLA de 99,5%, `RTO <= 2h`, `RPO <= 5 min`), agendamento de tarefas (`ADR-16`) e controle de acesso em nível de linha (`ADR-09`) exigem um banco cliente-servidor robusto integrado ao backend em **Python (FastAPI)**. É necessário formalizar a escolha do **Supabase (PostgreSQL)** como banco principal e delimitar o uso do SQLite exclusivamente ao armazenamento local *Offline-First* do aplicativo Android (`RNF-07`, `ADR-23`).

## 2. Direcionadores da decisão *(recomendada)*
* **Concorrência e Consistência Transacional (`RNF-04`, `RNF-06`, `RNF-09`, `R-08`):** Suporte a controle de concorrência multiversão (`MVCC`) e travas em nível de linha (`SELECT ... FOR UPDATE`) para evitar *race conditions* em leilões e gastos duplos de moedas, mantendo latência de leitura `p95 <= 200 ms` e escrita `p99 <= 500 ms`.
* **Segurança, Privacidade e Segregação Física do DaaS (`RNF-01`, `RNF-03`, `ADR-04`, `LGPD`):** Suporte nativo a *Row Level Security* (`RLS`), criptografia em repouso (`pgcrypto`) e possibilidade de isolar fisicamente a base analítica do DaaS em um segundo projeto gratuito do Supabase.
* **Capacidades Nativas Geoespaciais, Textuais e de Agendamento (`RF-06`, `STY020`, `ADR-16`):** Disponibilidade de extensões como `PostGIS`, `pg_trgm`, `unaccent`, `pg_cron` e `pg_net`.
* **Custo Zero (Plano Gratuito) e Esforço até 23/11 (`TAP`):** Minimizar o esforço de administração de infraestrutura (*DevOps*) com um serviço gerenciado gratuito que facilite a demonstração na banca de defesa.

## 3. Opções consideradas *(obrigatória)*

| Aspecto | Opção A — Supabase / PostgreSQL (Nuvem) + SQLite restrito ao Mobile Offline | Opção B — SQLite como Banco Principal no Servidor da API | Opção C — PostgreSQL Autogerenciado em VPS / Docker |
| :--- | :--- | :--- | :--- |
| **Descrição** | Adotar o **PostgreSQL 15+ gerenciado pelo Supabase** como banco de dados central consumido pelo backend Python (FastAPI via `SQLAlchemy`/`asyncpg`), reservando o **SQLite** exclusivamente para o cache local *Offline-First* no dispositivo Android (`RNF-07`, `ADR-23`). | Utilizar o **SQLite** em arquivo local no servidor Python (FastAPI) como banco de dados principal para todas as operações da plataforma. | Instalar e manter manualmente uma instância **PostgreSQL** em container Docker em uma máquina virtual, sem a plataforma do Supabase. |
| **Prós** | • Controle de concorrência `MVCC` e *row-level locks* (`FOR UPDATE`), eliminando o risco `R-08`.<br>• Extensões nativas prontas: `PostGIS` (raio geográfico), `pg_trgm` (busca textual), `pg_cron` + `pg_net` (rotinas agendadas) e `RLS`.<br>• Permite provisionar os 2 projetos gratuitos do Supabase para segregar fisicamente o banco Transacional (`ADR-08`) e o banco DaaS (`ADR-04`). | • Configuração local imediata sem dependência de rede.<br>• Baixa latência para leituras simples de um único usuário. | • Controle irrestrito do sistema operacional e configurações do banco.<br>• Ausência dos limites de tamanho do plano gratuito do Supabase. |
| **Contras** | • Cota do *Free Tier* limitada a 500 MB, 200 conexões simultâneas de Realtime e ausência de *PITR* gratuito (documentado como desvio conhecido do ambiente acadêmico gratuito). | • **Inviável para o escopo do servidor:** aplica *lock* no arquivo inteiro durante escritas simultâneas, quebrando leilões concorrentes (`RNF-06`, `R-08`) e o SLA de 1.000 usuários (`RNF-04`).<br>• Não possui `RLS`, `pg_cron` nem `PostGIS` nativo. | • Custo financeiro de VPS (violando o orçamento zero do `TAP`) e alto esforço operacional de backup, TLS e *pooling* até 23/11. |

## 4. Decisão *(obrigatória)*
**Opção escolhida:** ☒ **A** ☐ B ☐ C

Fica decidido o uso do **Supabase (PostgreSQL)** como **Banco de Dados Principal** do servidor da plataforma Steely, integrado ao backend em **Python (FastAPI)**:
1. **Resolução definitiva da inconsistência da Matriz GUT:** A citação ao SQLite na Matriz GUT refere-se unicamente à camada de persistência local no aplicativo móvel Android (**`SQLite` via `WatermelonDB` — `ADR-23`, protegido pela criptografia nativa do sistema operacional e TTL de expiração, com tokens JWT e chave pública `Ed25519` isolados no `expo-secure-store` / Android Keystore — `ADR-24`**), exigida pelo requisito *Offline-First* (`RNF-07`) para guardar rotas (`STY029`) e leituras de QR Code sem internet (`STY028`). No servidor central, o SQLite é descartado por não suportar concorrência de escrita distribuída (`R-08`).
2. **Alocação dos 2 Projetos Gratuitos na Nuvem + Homologação Local (`ADR-03`, `ADR-04`, `ADR-05`, `ADR-07` e `ADR-17`):**
   * **Projeto Supabase 1 — Core Transacional (`ADR-08`):**
     * Schema `public`: tabelas transacionais do domínio (`users`, `ofertas`, `propostas`, `agendamentos`, `chats`, `mensagens`, `leiloes`, `lances`, `wallets`, `wallet_ledger`, `laudos`, `devolucoes`, `esg_fatores`, `app_config`, `idempotency_keys` e `auth_login_attempts` para o Captcha Cloudflare Turnstile do `ADR-21`);
     * Schema `escrow` (`ADR-03`): tabelas de custódia financeira simulada em centavos (`escrow.escrow` e `escrow.escrow_evento`, isoladas do ledger de moedas da `RB-09`), não expostas na API e manipuladas apenas por funções `private.*`;
     * Schema `esg` (`ADR-22`): views materializadas (`esg.usuario_mensal` e `esg.plataforma_mensal`, atualizadas a cada 1h via `REFRESH MATERIALIZED VIEW CONCURRENTLY` no `pg_cron` e lidas apenas por funções `private.esg_resumo_*`);
     * Schema `private` (`ADR-03`, `ADR-05`, `ADR-07`, `ADR-09`, `ADR-22`): tabelas ultrassensíveis isoladas (`oferta_enderecos_exatos` para sigilo `RB-06`, `user_kyc_docs` cifrados com `pgcrypto`, e `dados_fiscais_transacoes` segregada por 5 anos conforme `PRM-63`/`ADR-07`) e **todas as funções `SECURITY DEFINER`** (`rpc_place_auction_bid`, `rpc_record_ledger_transaction`, `reter_escrow`, `release_escrow`, `estornar_escrow`, `audit_log`, `audit_verify`, `anonimizar_usuario`, `esg_resumo_usuario`, `esg_resumo_plataforma`);
     * Schema `audit` (`ADR-05`): dividido em **duas tabelas particionadas por mês (`PARTITION BY RANGE (created_at)`)**, *append-only* em 3 camadas (`REVOKE UPDATE, DELETE, TRUNCATE`, gatilho de bloqueio e hash encadeado `SHA-256` verificado diariamente por `private.audit_verify`), além da limpeza de `cron.job_run_details > 7d` e `auth_login_attempts > 24h`:
       1. `audit.system_and_access_logs` (retenção de **12 meses** — atende com folga ao mínimo legal de 6 meses do Marco Civil Art. 15 / `PRM-62` e ao `BPMN P6b`): partições descartadas (`DROP TABLE`) após 12 meses;
       2. `audit.financial_and_dispute_logs` (retenção de **5 anos / 60 meses** — `PRM-63` / Código Civil): guarda trilha de escrow, arbitragem, eliminação de conta e *ledger*, descartando partições apenas após 60 meses.
   * **Projeto Supabase 2 — Base DaaS Fisicamente Segregada (`ADR-04`):**
     * Segundo banco PostgreSQL fisicamente separado na nuvem. Os pacotes chegam através de rotina agendada (`ADR-16`): o `pg_cron` aciona via `pg_net` o webhook interno do FastAPI (`POST /api/v1/internal/jobs/sync-daas`), que valida o `X-Internal-Token`, retorna `202 Accepted` e em segundo plano (`BackgroundTasks`) executa a agregação no Projeto 1 com `HAVING COUNT(DISTINCT transacao_id) >= 30`, remove identificadores pessoais e realiza `UPSERT` via `asyncpg` no Projeto 2 (`DATABASE_URL_DAAS`).
   * **Ambiente de Homologação e CI (`ADR-17`):** O desenvolvimento local e a esteira de CI utilizam **`supabase start` (Supabase CLI em containers Docker locais)** sem custo.
3. **Hospedagem Oficial, Monitoramento Redundante e Keep-Alive dos 2 Bancos (`RNF-04`, `RNF-08`):**
   * **Hosts Escolhidos:** O backend **FastAPI** é hospedado oficialmente no **Render (Free Web Service)** e o front-end **Vite SPA** no **Cloudflare Pages**, ambos atrás do proxy reverso gratuito da **Cloudflare** (proteção DDoS L7 para o `RNF-13`).
   * **Keep-Alive e Alerta de Falha Tocando os 2 Projetos:** Para evitar ponto único de falha no *keep-alive*, o **UptimeRobot** (primário, a cada 10 min) e um workflow agendado no **GitHub Actions** (secundário, com alerta automático por e-mail/Discord da equipe em caso de status `!= 200`) chamam `GET /api/v1/health` no FastAPI. Essa rota `/health` executa uma chamada leve na API de **ambos os projetos Supabase (Projeto 1 Core e Projeto 2 DaaS)**, impedindo tanto a hibernação de 15 min do Render quanto a pausa por inatividade de 7 dias nos dois bancos do Supabase.

## 5. Consequências *(obrigatória)*
* **Positivas:**
  * Elimina o risco `R-08` usando transações `ACID` e *locks* de linha (`SELECT ... FOR UPDATE`).
  * Resolve todos os conflitos com os ADRs `04` (ETL assíncrono para o 2º banco Supabase), `05` (duas tabelas particionadas separando 12 meses e 5 anos), `09` (funções `SECURITY DEFINER` em schema privado `private` não exposto) e `16` (keep-alive redundante tocando ambos os bancos).
* **Negativas, desvios do plano gratuito e riscos aceitos:**
  1. **Desvio de Capacidade no Plano Gratuito (`RNF-04` e `RNF-06`):** No ambiente acadêmico gratuito até 23/11, a instância *Render Free* (0,1 vCPU / 512 MB RAM) e o *Supabase Free* (200 conexões Realtime) destinam-se à validação funcional e demonstração na banca, não sustentando os 1.000 usuários simultâneos nominais. Para produção comercial real, exige-se upgrade para *Render Standard* (múltiplos workers) e **Supabase Pro com Spend Cap desabilitado (até 10.000 conexões Realtime)**, o qual introduz **custo financeiro variável por consumo excedente**.
  2. **Desvio de RPO e Retenção de 30 Dias nos Backups (`RNF-08`, `ADR-07`):** O `RPO <= 5 min` nominal exige o add-on pago **Point-in-Time Recovery (PITR / WAL contínuo)** do Supabase. No plano gratuito até 23/11, o backup automatizado via `pg_dump` no GitHub Actions roda a cada **6 horas** (**RPO real de até 6 horas**) e os artefatos são retidos por **no máximo 30 dias (`retention-days: 30`)**, garantindo que dados de contas eliminadas (`ADR-07`) desapareçam dos backups em até 30 dias (informado na política de privacidade).
  3. **Configuração do Pooler:** A conexão do `asyncpg` na porta `6543` (*Supavisor* modo transacional) exige `statement_cache_size=0`.
* **O que muda no código, no banco, na arquitetura e nos diagramas:**
  * Configuração de `DATABASE_URL_CORE` e `DATABASE_URL_DAAS` no FastAPI, checadas simultaneamente no `/api/v1/health`.
  * Separação das tabelas `audit.system_and_access_logs` (12m) e `audit.financial_and_dispute_logs` (5a).

## 6. Validação *(recomendada)*
* **Critério de Aceite e Performance (`RNF-04`):** Consultas de listagem e busca por raio geográfico via FastAPI + PostgreSQL respondendo com latência `p95 <= 200 ms` e mutações transacionais com `p99 <= 500 ms` sob carga compatível com o ambiente.
* **Teste do Health-Check Dual:** Invocar `GET /api/v1/health` e comprovar retorno JSON `{"status": "ok", "core_db": "up", "daas_db": "up"}`.

## 7. Plano de implementação *(recomendada)*
1. **Provisionar os 2 projetos gratuitos no Supabase (Core e DaaS) e ativar extensões (`PostGIS`, `pg_trgm`, `unaccent`, `pg_cron`, `pg_net`, `pgcrypto`):** Fabrício e Augusto — *Sprint 8*.
2. **Criar os schemas (`public`, `private`, `audit` com 2 tabelas particionadas) e migrações (`EDTS-49`):** Fabrício — *Sprint 8*.
3. **Configurar o deploy no Render + Cloudflare, o `/api/v1/health` dual, o UptimeRobot com alerta e o workflow de `pg_dump` (6h):** Fabrício e Thiago — *Sprint 8*.

## 8. Referências *(recomendada)*
* Documento de Requisitos v2.0 (`RF-06`, `RNF-04`, `RNF-06`, `RNF-07`, `RNF-08`, `RNF-09`).
* Termo de Abertura do Projeto (`TAP escola de ti.pdf`).
* ADRs relacionados: `ADR-03`, `ADR-04`, `ADR-05`, `ADR-06`, `ADR-07`, `ADR-09`, `ADR-10`, `ADR-15`, `ADR-16`, `ADR-21`, `ADR-22`, `ADR-23`.

---

### Histórico de revisões
| Versão | Data | Autor | Alteração |
| :--- | :--- | :--- | :--- |
| 1.0 | 31/10/2026 | Fabrício Notoya Thomas | Elaboração inicial da decisão e resolução da inconsistência com a Matriz GUT. |
| 1.1 | 31/10/2026 | Fabrício Notoya Thomas | Inclusão de estratégia anti-hibernação, particionamento de logs, 2ª instância para DaaS e nota sobre cota gratuita do Realtime. |
| 1.2 | 31/10/2026 | Fabrício Notoya Thomas | Separação física das tabelas de log (12m vs 5a), definição do ETL do DaaS via FastAPI, host nomeado com Cloudflare L7, Keep-Alive externo, cota Pro sem Spend Cap (10k conexões) e nota sobre PITR/RPO. |
| 1.3 | 31/10/2026 | Fabrício Notoya Thomas | Escolha oficial do Render, `/health` tocando ambos os projetos Supabase com alerta no UptimeRobot, registro explícito dos desvios do plano gratuito (RPO de 6h via `pg_dump`, limite de CPU do Render Free e custo variável do Pro sem Spend Cap). |
| 1.4 | 31/10/2026 | Fabrício Notoya Thomas | Inclusão do schema `esg` (views materializadas atualizadas a cada 1h via `pg_cron` — `ADR-22`), da tabela `auth_login_attempts` (`ADR-21`) e limpeza de `cron.job_run_details` para proteger a cota de 500 MB. |
| 1.5 | 01/11/2026 | Fabrício Notoya Thomas | Alinhamento com `ADR-23` e `ADR-24`: especificação do SQLite no Android via `WatermelonDB` (`ADR-23`) com segredos isolados no `expo-secure-store` (`ADR-24`), sem dependência de fork `SQLCipher`. |
| 1.6 | 01/11/2026 | Fabrício Notoya Thomas | Alinhamento com `ADR-03` a `ADR-07`: inclusão do schema `escrow`, tabela fiscal segregada em `private`, hash encadeado no schema `audit` (12m cumprindo `PRM-62`) e retenção máxima de 30 dias nos dumps de 6h (`ADR-07`). |
