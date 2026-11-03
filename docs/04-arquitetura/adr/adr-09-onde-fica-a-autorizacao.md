# ADR-09 — Onde fica a autorização
*Architecture Decision Record · Projeto Steely · Escola de TI · UniCesumar*

| Campo | Valor | Campo | Valor |
| :--- | :--- | :--- | :--- |
| **Status** | ☒ Proposto ☐ Aceito ☐ Rejeitado ☐ Substituído pelo ADR-___ | **Data** | 01/11/2026 |
| **Responsável** | Fabrício Notoya Thomas | **Sprint** | Sprint 8 (15–17) |
| **Participantes** | Fabrício Notoya Thomas, Thiago Lopes Martins, Augusto Palma Guglielmi, Pietro Pasqual Silva, Rafael Tudela Rizental | | |
| **Vínculos** | `EDTS-57` · `RNF-01` · `RNF-02` · `RNF-13` · `RB-01` · `RB-06` · `RB-10` · `R-04` · `STYG-RN01` · `STY002-RN03/RN04` · `STY035-RN03` · `STY050-RN03` · `STY056-RN01/RN02` · `ADR-03` · `ADR-05` · `ADR-06` · `ADR-07` · `ADR-08` · `ADR-13` · `ADR-16` · `ADR-18` · `ADR-21` · `ADR-22` | | |

---

## 1. Contexto *(obrigatória)*
A plataforma Steely possui múltiplos perfis de usuários (`Visitante`, `Usuário Comum Comprador/Vendedor`, `ONG Verificada`, `Técnico Parceiro`, `Moderador` e `Administrador`) e exige controles de acesso baseados em papel (*RBAC*), atributos dinâmicos de negócio (*ABAC*) e titularidade do recurso (*Ownership*):
* Somente o autor/proprietário de um registro pode editá-lo ou inativá-lo (`STYG-RN01`);
* Acesso a Leilões Exclusivos, Grandes Lotes e Mural Institucional exige `KYC validado` (`RB-01`);
* Geração e uso de moedas ou participação em leilões são bloqueados automaticamente se `Trust Score < 70%` (`RB-10`);
* O endereço exato da coleta (numeração e coordenadas precisas) deve permanecer oculto na API até que a oferta mude para o status `"Reservado"` (`RB-06`);
* **Estornos de custódia por decisão de moderação (`private.estornar_escrow` — `ADR-03` e `ADR-06`) e banimentos/suspensões definitivas** exigem aprovação de um **segundo moderador distinto do primeiro** (`STY035-RN03`, `STY050-RN03`, `R-04`), enquanto a consulta aos logs (`STY056`, `ADR-05`) e à tabela fiscal segregada (`ADR-07`) é restrita ao perfil de auditoria e dentro do prazo legal.

Para que a autorização em duas camadas (FastAPI + PostgreSQL) seja inviolável, é necessário endereçar quatro vetores críticos levantados na revisão arquitetural da equipe:
1. **Bloqueio de Chamada Direta via PostgREST (`Data API`):** Como o navegador recebe a `anon_key` e o `JWT` do usuário para escutar o *Supabase Realtime*, se a Data API (PostgREST) estiver ativa e expuser funções `SECURITY DEFINER` com `GRANT EXECUTE TO authenticated`, um usuário malicioso poderia invocar `rpc_place_auction_bid` diretamente pelo navegador, pulando o FastAPI;
2. **Propagação de Contexto JWT (`SET LOCAL ROLE authenticated`) através do Pooler (`Supavisor`);**
3. **Extração do IP Real do Cliente (`CF-Connecting-IP`) atrás do Cloudflare Proxy para o Rate Limiting (`RNF-13`);**
4. **Autenticação de Webhooks Internos (`/api/v1/internal/jobs/*`) acionados pelo `pg_cron`/`pg_net` (`ADR-16`).**

## 2. Direcionadores da decisão *(recomendada)*
* **Defesa em Profundidade Real e Incontornável (`RNF-01`, `LGPD`, `RB-06`):** Impedir qualquer *bypass* do FastAPI via PostgREST e garantir que tanto o código Python quanto o PostgreSQL validem as permissões e regras críticas (`KYC`, `Trust Score >= 70%`).
* **Rate Limiting Preciso por IP Real (`RNF-13`, `STY002`, `ADR-21`):** Ler o IP verdadeiro do usuário atrás da Cloudflare (`CF-Connecting-IP`) para que o limite de 5 tentativas em 5 minutos não bloqueie todos os usuários simultaneamente.
* **Proteção de Rotas Internas e Padronização (`ADR-13`, `ADR-16`):** Proteger webhooks internos com token criptográfico (`X-Internal-Token`) e execução assíncrona (`202 Accepted`), mantendo erros no padrão **RFC 9457 (*Problem Details*)** sobre **OpenAPI 3.1**.

## 3. Opções consideradas *(obrigatória)*

| Aspecto | Opção A — Somente RLS no Banco com Data API (PostgREST) Exposta | Opção B — Somente Checagem no FastAPI usando `service_role` irrestrita | Opção C — Duas Camadas Blindadas: Data API Desabilitada + Funções em Schema `private` com Checagem Dupla + `SET LOCAL ROLE` no FastAPI |
| :--- | :--- | :--- | :--- |
| **Descrição** | O cliente fala direto com o PostgREST do Supabase e toda a autorização fica apenas no banco. | O FastAPI valida permissões em Python, mas roda todas as queries SQL como superusuário/`service_role`. | **Arquitetura Blindada em Duas Camadas:**<br>1. A **Data API (PostgREST) é desabilitada** no Supabase (cliente usa apenas o WebSocket do *Realtime*);<br>2. Todo tráfego HTTP passa pelo **FastAPI** (que lê `CF-Connecting-IP` no `slowapi` e valida `X-Internal-Token` nas rotas internas);<br>3. O FastAPI injeta `SET LOCAL ROLE authenticated` + `request.jwt.claims` na transação SQL para ativar a `RLS`;<br>4. As funções `SECURITY DEFINER` ficam no **schema não exposto `private`** e **repetem internamente as checagens de `KYC` e `Trust Score >= 70%`**. |
| **Prós** | • Menos código de backend. | • Simples de configurar a conexão SQL inicial. | • **Impossibilita bypass pelo navegador:** sem PostgREST ativo e com funções em `private.*` que validam `KYC`/`Trust Score` dentro do próprio SQL, ninguém consegue pular o FastAPI.<br>• **Rate limit exato por usuário/IP (`CF-Connecting-IP`).**<br>• **Segurança em rotas de jobs (`X-Internal-Token` + `202 Accepted`).** |
| **Contras** | • **Vulnerável:** permite chamar RPCs direto pelo navegador pulando Rate Limit e Captcha (`ADR-21`). | • **Falsa sensação de duas camadas:** qualquer esquecimento de `WHERE user_id = ...` no Python vaza dados de todos os usuários. | • Exige configurar `db_schemas` vazio no PostgREST e validar o cabeçalho da Cloudflare no FastAPI (configuração única e simples). |

## 4. Decisão *(obrigatória)*
**Opção escolhida:** ☐ A ☐ B ☒ **C**

Fica decidido que a autorização residirá **nas duas camadas (FastAPI + RLS/SQL no PostgreSQL)**, com as seguintes travas obrigatórias:

1. **Desativação da Data API (PostgREST) e Isolamento em Schema `private` (Prevenção de Bypass):**
   * Nas configurações do Supabase (*API Settings*), a **Data API (PostgREST) é desabilitada** (ou o campo *Exposed Schemas* é configurado sem `public` e sem `private`). Assim, a `anon_key` presente no navegador serve **exclusivamente** para abrir o WebSocket do *Supabase Realtime* (`RNF-06`), sendo impossível fazer chamadas REST/RPC diretas ao banco a partir do navegador.
   * Todas as funções `SECURITY DEFINER` (`private.rpc_record_ledger_transaction`, `private.rpc_place_auction_bid`, `private.reter_escrow`, `private.release_escrow`, `private.estornar_escrow`, `private.audit_log`, `private.audit_verify`, `private.anonimizar_usuario`, `private.esg_resumo_usuario` e `private.esg_resumo_plataforma`) são criadas dentro do **schema não exposto `private`**, com `SET search_path = public, private, pg_temp`, `REVOKE ALL FROM PUBLIC, anon` e permissões estritas (`ADR-03`, `ADR-05`, `ADR-07`, `ADR-22`). No caso do ESG (`ADR-22`), as views materializadas ficam no schema `esg` sem permissão de leitura direta, sendo acessadas apenas pelas funções `private.esg_resumo_*` que filtram por `auth.uid()` e aplicam `k >= 30` por região. No caso do estorno por moderação (`private.estornar_escrow` — `ADR-03`, `ADR-06`), a função SQL exige a presença de duas aprovações de moderadores distintos (`R-04`), salvo estorno automático por revelia do vendedor (3 dias sem resposta).
   * **Checagem Dupla no SQL:** Além da validação no FastAPI, as funções `private.rpc_place_auction_bid` e `private.rpc_record_ledger_transaction` **repetem dentro do próprio bloco PL/pgSQL** a verificação de conta ativa (`status = 'ACTIVE'`), `kyc_verified = TRUE` (`RB-01`) e `trust_score >= 70` (`RB-10`), garantindo que nenhuma regra crítica dependa apenas da camada Python.
2. **Rate Limiting com IP Real atrás da Cloudflare (`RNF-13`, `STY002`, `ADR-21`):**
   * O tráfego passa pelo proxy reverso da **Cloudflare** (mitigação DDoS L7). No FastAPI, a função extratora de chave do `slowapi` lê prioritariamente o cabeçalho **`CF-Connecting-IP`** (aceito apenas de requisições originadas dos *IP Ranges* oficiais da Cloudflare / *Authenticated Origin Pulls*, com fallback para o primeiro IP confiável de `X-Forwarded-For`).
   * Isso garante que os limites de `5 tentativas / 5 min` em `/api/v1/auth/*` (junto ao contador de 3 falhas do Captcha `ADR-21` e bloqueio na 5ª falha `STY002-RN04`), `30 req/min` em moedas/captcha e `120 req/min` em consultas públicas sejam aplicados individualmente por cliente real, sem bloquear usuários legítimos em massa.
3. **Autenticação e Execução Assíncrona de Endpoints Internos (`/api/v1/internal/jobs/*` — `ADR-16`):**
   * Todas as rotas sob `/api/v1/internal/jobs/*` acionadas pelo `pg_cron`/`pg_net` exigem o cabeçalho `X-Internal-Token` (segredo de 256 bits guardado no *Supabase Vault* e validado no FastAPI com `secrets.compare_digest` em tempo constante). Requisições sem o token ou com token inválido recebem `401/403` imediato.
   * Para não estourar o timeout HTTP do `pg_net`, os endpoints internos validam o token, enfileiram a execução pesada (ex.: sincronização do DaaS ou disparo de notificações push) em **`BackgroundTasks` do FastAPI** e respondem imediatamente com **`202 Accepted`**.
4. **Sessão Transacional `RLS` no FastAPI (`asyncpg` + `Supavisor`):**
   * O `asyncpg` conecta na porta `6543` com `statement_cache_size=0`. A dependência `get_rls_db_session` abre transação explícita (`async with session.begin():`) e executa:
     ```sql
     SET LOCAL ROLE authenticated;
     SELECT set_config('request.jwt.claims', :jwt_claims_json, true);
     ```
     mantendo o `auth.uid()` e todas as políticas `RLS` ativas durante toda a transação e limpando o estado automaticamente no `COMMIT`/`ROLLBACK`.

## 5. Consequências *(obrigatória)*
* **Positivas:**
  * **Elimina 100% do risco crítico de bypass via PostgREST:** mesmo que um usuário extraia seu próprio JWT e a `anon_key` no navegador, a Data API está desligada, as funções estão no schema `private` e o próprio SQL revalida `KYC` e `Trust Score >= 70%`.
  * **Elimina o bloqueio coletivo no Rate Limiting:** o `slowapi` enxerga o IP real de cada usuário via `CF-Connecting-IP`.
  * **Blindagem das rotas internas do `pg_cron`:** protegidas por `X-Internal-Token` e resposta rápida `202 Accepted`.
* **Negativas ou riscos aceitos:**
  * Exige manter o segredo `INTERNAL_JOB_TOKEN` sincronizado entre as variáveis de ambiente do Render (FastAPI) e o *Supabase Vault* (`pg_net`).
* **O que muda no código, no banco, na arquitetura e nos diagramas:**
  * Desativação da Data API no painel do Supabase; migração das funções `SECURITY DEFINER` para o schema `private`.
  * Criação do `get_real_client_ip(request)` lendo `CF-Connecting-IP` no `app/core/rate_limit.py` e do `verify_internal_token` no `app/api/deps.py`.

## 6. Validação *(recomendada)*
* **Teste Anti-Bypass PostgREST (`ADR-17`):** Tentar chamar `POST https://<project>.supabase.co/rest/v1/rpc/rpc_place_auction_bid` diretamente com `anon_key` + `JWT` válido de usuário $\rightarrow$ deve falhar (`404 Not Found / Data API Disabled`).
* **Teste de `CF-Connecting-IP` no Rate Limit (`pytest`):** Enviar 6 requisições de login de dois IPs simulados distintos no header `CF-Connecting-IP` (`203.0.113.10` e `203.0.113.20`) $\rightarrow$ comprovar que o primeiro IP recebe `429 Too Many Requests` na 6ª tentativa enquanto o segundo IP consegue logar normalmente.
* **Teste de Rota Interna:** Chamar `POST /api/v1/internal/jobs/sync-daas` sem `X-Internal-Token` $\rightarrow$ `403 Forbidden`; com token válido $\rightarrow$ retorno `202 Accepted` em `< 50 ms`.

## 7. Plano de implementação *(recomendada)*
1. **Desabilitar Data API no Supabase, criar schema `private` para as funções `SECURITY DEFINER` (com checagem interna de KYC/Trust Score) e políticas `RLS` (`EDTS-57`):** Fabrício — *Sprint 8*.
2. **Implementar `get_rls_db_session`, leitura de `CF-Connecting-IP` no `slowapi` e guard `X-Internal-Token` (`202 Accepted`) no FastAPI:** Fabrício e Thiago — *Sprint 8*.
3. **Implementar o proxy `/api/v1/auth/login` integrado ao Captcha após 3 falhas (`ADR-21`):** Fabrício e Pietro — *Sprint 8/9*.

## 8. Referências *(recomendada)*
* Documento de Requisitos v2.0 (`RF-01`, `RF-20`, `RNF-01`, `RNF-02`, `RNF-13`).
* Regras de Negócio (`STYG-RN01`, `RB-01`, `RB-06`, `RB-10`, `STY002-RN03/RN04`, `STY035-RN03`, `STY049-RN03`, `STY050-RN03`, `STY056-RN01/RN02`).
* PostgreSQL Documentation — *Writing `SECURITY DEFINER` Functions Safely* & *Transaction-Local `SET LOCAL`*.
* IETF **RFC 9457** — *Problem Details for HTTP APIs*.
* ADRs relacionados: `ADR-03`, `ADR-05`, `ADR-06`, `ADR-07`, `ADR-08`, `ADR-10`, `ADR-13`, `ADR-16`, `ADR-18`, `ADR-21`, `ADR-22`.

---

### Histórico de revisões
| Versão | Data | Autor | Alteração |
| :--- | :--- | :--- | :--- |
| 1.0 | 31/10/2026 | Fabrício Notoya Thomas | Definição da autorização em duas camadas (FastAPI Depends + PostgreSQL RLS). |
| 1.1 | 31/10/2026 | Fabrício Notoya Thomas | Solução do conflito `service_role` × `RLS` via `SET LOCAL ROLE authenticated`, login via FastAPI (`ADR-21`), Rate Limiting (`RNF-13`) e RFC 9457 / OpenAPI 3.1. |
| 1.2 | 31/10/2026 | Fabrício Notoya Thomas | Detalhamento de escopo transacional do `SET LOCAL` com `asyncpg` (`statement_cache_size=0`), hardening de funções `SECURITY DEFINER` e proteção DDoS L7 via Cloudflare. |
| 1.3 | 31/10/2026 | Fabrício Notoya Thomas | Desativação da Data API (PostgREST), mudança das funções `SECURITY DEFINER` para o schema `private` com revalidação SQL de KYC/Trust Score, leitura de `CF-Connecting-IP` no `slowapi` e proteção de `/api/v1/internal/jobs/*` com `X-Internal-Token` e `202 Accepted`. |
| 1.4 | 31/10/2026 | Fabrício Notoya Thomas | Alinhamento com `ADR-21` (Cloudflare Turnstile + `auth_login_attempts`) e `ADR-22` (funções `private.esg_resumo_usuario` e `private.esg_resumo_plataforma` isolando o schema `esg`). |
| 1.5 | 01/11/2026 | Fabrício Notoya Thomas | Alinhamento com `ADR-03`, `ADR-05`, `ADR-06` e `ADR-07`: funções de escrow, auditoria e anonimização em `private`, e dupla aprovação de moderadores distintos para estorno (`R-04`). |
