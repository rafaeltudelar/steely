# ADR-13 — Contrato e versionamento da API
**Architecture Decision Record · Projeto Steely · Escola de TI · UniCesumar**

| Campo | Valor | Campo | Valor |
| --- | --- | --- | --- |
| **Status** | ☒ Proposto  ☐ Aceito  ☐ Rejeitado  ☐ Substituído pelo ADR-___ | **Data** | 01/11/2026 |
| **Responsável** | Thiago Lopes Martins | **Sprint** | Sprint 8–9 / 15–17 (Entrega até 23/11) |
| **Participantes** | Thiago Lopes Martins, Fabrício Notoya Thomas, Augusto Palma Guglielmi, Pietro Pasqual Silva, Rafael Tudela Rizental | | |
| **Vínculos** | RNF-02 · RNF-04 · RNF-09 · RNF-11 · RNF-13 · RF-01 · ADR-08 · ADR-09 · ADR-14 · ADR-17 · ADR-18 | | |

## 1. Contexto *(obrigatória)*

O Steely tem dois clientes (web e app Android, da parte do Pietro e do Rafael) falando com o mesmo backend em REST e em tempo real (chat e leilões). A equipe tem 5 pessoas e entrega até 23/11/2026. Sem contrato único de API, front e back travam um ao outro e cada módulo inventa seu formato de resposta e de erro.

Requisitos que puxam a decisão: leitura p95 ≤ 200 ms e escrita p99 ≤ 500 ms (`RNF-04`), validação offline do QR Code com contrato fixo de payload e chave pública (`RNF-02`), cabeçalho de idempotência padronizado (`RNF-09`, `ADR-14`), Correlation ID em todas as respostas (`RNF-11`) e cabeçalhos de limite de taxa (`RNF-13`, `RF-01`).

**Definido pelo grupo (`ADR-08` e `ADR-09`):** backend em Python com **FastAPI** sobre PostgreSQL no **Supabase**; todas as escritas e leituras protegidas passam pelo FastAPI, e o cliente só se conecta direto ao Realtime, com o JWT já emitido. A Data API (PostgREST) fica desabilitada no Supabase, então a chave pública do navegador serve só ao WebSocket do Realtime (`ADR-09`).

## 2. Direcionadores da decisão *(recomendada)*

- **Consistência entre web, Android e backend:** um contrato único e um único formato de erro.
- **Esforço até 23/11:** gerar clientes e mocks automaticamente em vez de escrevê-los à mão.
- **Custo zero:** apenas ferramentas open source gratuitas.
- **Testabilidade e Defesa:** o contrato alimenta os testes do `ADR-17` e gera documentação navegável (Swagger UI / Redoc), aproveitando o que o FastAPI já gera a partir do Pydantic v2 sem escrever o contrato duas vezes.

## 3. Opções consideradas *(obrigatória)*

| Opção A — OpenAPI 3.1 design-first | Opção B — Code-first no FastAPI com snapshot versionado | Opção C — Spec gerada pelo PostgREST / Supabase |
| --- | --- | --- |
| **Descrição:** Um YAML versionado no repositório é a fonte única; clientes, mocks e testes saem dele.<br>**Prós:**<br>• Web e Android começam com mock antes do backend.<br>• Mudanças passam por PR.<br>• Independe de framework.<br>**Contras:**<br>• Exige disciplina e lint.<br>• Esforço inicial de escrita manual duplicada com os modelos do FastAPI. | **Descrição:** A spec OpenAPI 3.1 é gerada a partir dos modelos Pydantic v2 e rotas do FastAPI e exportada para openapi/openapi.snapshot.json no CI.<br>**Prós:**<br>• Menos duplicação: a spec reflete o código.<br>• PR de contrato (rotas stub 501) libera o front.<br>• oasdiff barra quebras no CI.<br>**Contras:**<br>• Exige commitar o snapshot atualizado quando mudar rota ou schema. | **Descrição:** Usa a spec que o PostgREST publica diretamente a partir do schema do banco.<br>**Prós:**<br>• Zero esforço para CRUD simples.<br>**Contras:**<br>• O contrato vira espelho das tabelas.<br>• Data API está desabilitada (ADR-09).<br>• Não controla formato de erro nem versão. |

## 4. Decisão *(obrigatória)*

**Opção escolhida:** ☐ A  ☒ B  ☐ C

**Opção escolhida: B — Code-first no FastAPI, com snapshot da spec versionado no Git e verificação no CI**, mais **AsyncAPI 3.0** para os eventos de chat e leilão no Supabase Realtime (`ADR-09`). Como o grupo escolheu FastAPI, manter um YAML escrito à mão duplicaria todos os modelos Pydantic. No FastAPI o próprio código gera **OpenAPI 3.1**; para não perder as vantagens da Opção A, exportamos a spec gerada para `openapi/openapi.snapshot.json` no repositório: o CI falha se o código divergir do snapshot ou se o `oasdiff` detectar mudança incompatível, e o front pode ser destravado no dia 1 com um PR de contrato (modelos Pydantic + rotas vazias devolvendo `501 Not Implemented`).

- **Versionamento:** Prefixo `/api/v1`; versão só no caminho; sem quebras na `v1` até a defesa (campos novos entram como opcionais). Se uma rota precisar ser descontinuada, usa-se `Deprecation` e `Sunset` (RFC 8594).
- **Envelope e convenções:** Recursos unitários retornam o objeto direto; listas usam `{ "data": [...], "meta": { "nextCursor", "limit", "hasMore" } }`; paginação por cursor (offset só em relatórios admin/DaaS); campos JSON em `camelCase` (com `alias_generator = to_camel` no Pydantic), datas em ISO-8601 UTC, valores monetários em centavos inteiros (`priceCents`) e moedas do Steely como inteiro (`coins`).
- **Padrão de erro — RFC 9457 (`application/problem+json`):** Campos `type`, `title`, `status`, `detail`, `instance`, mais `code` (estável), `correlationId` (`RNF-11`) e `errors[]`. Códigos fixados: `AUCTION_ENDED`, `BID_TOO_LOW`, `BID_OUTDATED`, `ALREADY_LEADING`, `INSUFFICIENT_COINS_HOLD`, `IDEMPOTENCY_KEY_REQUIRED`, `IDEMPOTENCY_KEY_REUSED`, `IDEMPOTENCY_IN_PROGRESS`, `OFFER_NOT_AVAILABLE`, `QR_EXPIRED`, `QR_SIGNATURE_INVALID`, `RETURN_WINDOW_CLOSED`, `RATE_LIMITED`, `CAPTCHA_REQUIRED`, `PII_OR_CONTACT_DETECTED`, `ACCOUNT_IN_GRACE_PERIOD`.
- **Cabeçalhos comuns:** `Authorization: Bearer <jwt>`, `X-Correlation-Id`, `Idempotency-Key` (UUID v4 — `ADR-14`) e `RateLimit-*` + `Retry-After` (`RNF-13`).
- **Autenticação, borda e rate limit:** Login em `POST /api/v1/auth/login` com Turnstile a partir da 3ª falha (`ADR-21`) e `slowapi` lendo `CF-Connecting-IP` (com fallback para `X-Forwarded-For`). Endpoints internos de jobs (`POST /api/v1/internal/jobs/*`) validam `X-Internal-Token` com `secrets.compare_digest` e respondem `202 Accepted` (`ADR-16`). Endpoint público `GET /api/v1/health` faz `SELECT 1` nos bancos Core e DaaS (`ADR-08`, `ADR-16`).

## 5. Consequências *(obrigatória)*

- **Positivas:** Front e mobile geram tipos e cliente HTTP direto do snapshot (`openapi-typescript` + `openapi-fetch` — `ADR-18`); sem contrato duplicado; erros padronizados em RFC 9457; quebra de contrato barra o PR antes do merge; o próprio FastAPI publica Swagger UI e Redoc.
- **Negativas ou riscos aceitos:** O snapshot precisa ser comitado a cada mudança de rota; o limite de taxa do `slowapi` fica na memória do processo (complementado pelo Cloudflare WAF na borda — `RNF-13`); endpoints internos dependem do segredo `X-Internal-Token`.
- **O que muda no código, banco e diagramas:** Handlers globais RFC 9457, prefixo `/api/v1`, pasta `openapi/openapi.snapshot.json` e `asyncapi/` no repositório, e FastAPI como único ponto de escrita nos diagramas.

## 6. Validação *(recomendada)*

- Lint (Spectral) e verificação de compatibilidade (`oasdiff`) verdes no CI.
- Teste de contrato (Schemathesis, `ADR-17`) sem divergências entre spec e backend.
- Pietro e Rafael compilam o cliente gerado sem tipar nenhuma resposta à mão.
- Todo erro retornado nos testes segue o formato RFC 9457 (incluindo um erro de regra de negócio e um `409` de concorrência demonstrados via Swagger UI).

## 7. Plano de implementação *(recomendada)*

| Tarefa | Responsável | Sprint |
| --- | --- | --- |
| Esqueleto da spec: segurança, erros RFC 9457, parâmetros comuns, paginação | Thiago | Sprint 8 (15) |
| Spectral + oasdiff + verificação de openapi.snapshot.json no CI | Thiago | Sprint 8 (15) |
| Scripts de mock (Prism) e geração de cliente (openapi-typescript) | Thiago, Pietro e Rafael | Sprint 8 (15) |
| Modelos Pydantic e rotas por módulo | Dono de cada módulo (revisão Thiago) | Sprint 8–9 (15–16) |
| AsyncAPI de lances e chat | Thiago | Sprint 8 (16) |
| Endpoints de autenticação, slowapi e /api/v1/health | Thiago e Fabrício | Sprint 8 (15) |

## 8. Referências *(recomendada)*

- OpenAPI Specification 3.1; AsyncAPI 3.0; documentação do FastAPI e do Pydantic v2.
- RFC 9457 (Problem Details for HTTP APIs); RFC 8594 (Sunset).
- Spectral, oasdiff, Prism, openapi-typescript.
- RNF-02, RNF-04, RNF-09, RNF-11, RNF-13; ADR-08, ADR-09, ADR-14, ADR-17, ADR-18.

## Histórico de revisões

| Versão | Data | Autor | Alteração |
| --- | --- | --- | --- |
| 0.1 | 31/10/2026 | Thiago Lopes Martins | Rascunho inicial |
| 0.2 | 31/10/2026 | Thiago Lopes Martins | Decisão alterada de OpenAPI design-first para code-first no FastAPI, alinhada ao ADR-09 (Fabrício) |
| 0.3 | 31/10/2026 | Thiago Lopes Martins | Autenticação pelo FastAPI, limite de taxa, health check; OpenAPI 3.1 e RFC 9457 padronizados (2º alinhamento do Fabrício) |
| 0.4 | 31/10/2026 | Thiago Lopes Martins | Nome do snapshot igual ao da equipe (openapi.snapshot.json); limites do slowapi registrados |
| 0.5 | 31/10/2026 | Thiago Lopes Martins | Cloudflare na borda (IP real, CORS), endpoints internos com segredo e keep-alive por monitor externo (3º alinhamento do Fabrício) |
| 0.6 | 31/10/2026 | Thiago Lopes Martins | Data API desabilitada, IP real com CF-Connecting-IP e fallback, token interno com compare_digest e 202, Render como host e health nos dois projetos com monitor redundante |

---

## Anexo — Texto Integral Detalhado (Documento Original)

ADR-13 — Contrato e versionamento da API
Architecture Decision Record · Projeto Steely · Escola de TI · UniCesumar
1. Contexto
A plataforma terá um backend REST stateless (RNF-02, restrição do TAP) consumido por
dois clientes React, web e Android (RNF-07), desenvolvidos por pessoas diferentes. Sem
um contrato único, cada cliente tipa as respostas à mão e os erros divergem entre
módulos. Há ainda regras que o contrato precisa expor: JWT (RF-01), Idempotency-Key
(RNF-09), Correlation ID  (RNF-11), limites de taxa (RNF-13) e latência p95 de leitura ≤
200 ms (RNF-04).
Decidir agora desbloqueia web e mobile antes de o backend existir, e o prazo final é
23/11/2026. Lances e chat usam WebSocket (RNF-03, RNF-06), que o OpenAPI não
descreve. Definido no ADR-08 e no ADR-09 (Fabrício): backend em Python com FastAPI e
banco PostgreSQL no Supabase; o Supabase Realtime entrega os eventos de chat e leilão.
O cliente não chama o Supabase Auth nem o PostgREST: login, cadastro e recuperação
Campo Valor
Status ☒  Proposto ☐  Aceito ☐  Rejeitado ☐  Substituído
pelo ADR-___
Data 31/10/2026
Responsável Thiago Lopes Martins
Sprint A definir (pergunta em aberto)
Participantes Thiago (autor). Revisão sugerida: Pietro (cliente
web), Rafael (cliente Android), Fabrício (ADR-
08/09)
Vínculos RNF-02, RNF-04 · também RNF-09, RNF-11, RNF-13,
RF-01 · ADR-08, ADR-09, ADR-14, ADR-17, ADR-18
Page 1 of 29
--- Page 2 ---
passam pelo FastAPI, e o cliente só se conecta direto ao Realtime, com o JWT já emitido. A
Data API (PostgREST) fica desabilitada no Supabase, então a chave pública do navegador
serve só ao WebSocket do Realtime (ADR-09 v1.3).
2. Direcionadores da decisão
Consistência entre web, Android e backend (um contrato, um formato de erro).
Esforço até 23/11: gerar clientes e mocks em vez de escrevê-los.
Custo zero: só ferramentas open source.
Testabilidade: o contrato alimenta os testes do ADR-17.
Demonstrável na defesa: documentação navegável (Swagger UI ou Redoc).
Aproveitar o que o FastAPI já gera, sem escrever o contrato duas vezes.
3. Opções consideradas
Opção A — OpenAPI
3.1 design-first
Opção B — Code-first Opção C — Spec gerada pelo
PostgREST/Supabase
Descrição Um YAML versionado
no repositório é a
fonte única; clientes,
mocks e testes saem
dele.
A spec é gerada a
partir de anotações
do código do
backend.
Usa a spec que o PostgREST
publica a partir do schema
do banco.
Prós Web e Android
começam com mock
antes do backend.
Mudanças passam
por PR. Independe de
framework.
Menos duplicação. A
spec reflete o código.
Zero esforço para CRUD
simples.
Contras Exige disciplina e lint.
Esforço inicial de
escrita.
O contrato nasce
depois do código e
bloqueia o front.
Depende do
framework (agora
definido: FastAPI).
Muda sem revisão.
O contrato vira espelho das
tabelas. Não cobre bem
funções e Edge Functions.
Não controla o formato de
erro nem a versão (conferir
na versão usada).
Page 2 of 29
--- Page 3 ---
4. Decisão
Opção escolhida: ☒  B, com guarda-corpos da A. O FastAPI (Pydantic v2) é a fonte única
do contrato e publica o OpenAPI em /api/v1/openapi.json , como decidido pelo Fabrício
no ADR-09. Esta ADR chegou a propor a Opção A porque o framework não existia; com o
FastAPI definido, B elimina a duplicação e a spec nunca diverge do código. O risco que
sobra, o front esperar o backend, é tratado pelo fluxo abaixo. A foi descartada por duplicar
o que o FastAPI já gera. C foi descartada porque a escrita passa pelo FastAPI (ADR-09).
Regras adotadas:
1 . Fonte e rota. Modelos Pydantic v2 e rotas FastAPI; contrato em
/api/v1/openapi.json , em OpenAPI 3.1, padrão da equipe confirmado pelo Fabrício
(conferir na versão instalada).
2. Contrato antes da lógica. Cada endpoint começa num PR só com modelos e rota
respondendo 501; um consumidor (Pietro ou Rafael) aprova; só depois entra a
implementação.
3. Snapshot e CI. O CI exporta openapi/openapi.snapshot.json  e falha se o arquivo
versionado divergir do código; oasdiff bloqueia mudança incompatível dentro de
/api/v1 ; Spectral faz o lint. Mocks com Prism e tipos TypeScript com openapi-
typescript saem do snapshot.
4. Erros em Problem Details. Formato application/problem+json  pela RFC 9457,
padrão da equipe, que substitui a RFC 7807. Campos type , title , status , detail ,
instance , mais code  (estável, em inglês, ex. BID_OUTDATED ), correlationId  e
errors[] . Um handler global do FastAPI converte RequestValidationError  e
HTTPException  para esse formato.
5. Status HTTP. 400 requisição malformada ou cabeçalho obrigatório ausente; 401 sem
autenticação; 403 bloqueio de acesso ( KYC_REQUIRED ,
TRUST_SCORE_BELOW_THRESHOLD ); 404; 409 conflito de estado, concorrência ou
idempotência; 422 validação de campo (padrão do FastAPI) e regra de negócio violada,
distintas pelo code ; 429 com Retry-After  (RNF-13); 5xx falha do servidor.
6. Versão no prefixo. /api/v1 . Mudança incompatível cria /api/v2  convivendo com a
anterior; mudança aditiva fica em /api/v1 . Descontinuação anunciada pelos
cabeçalhos Deprecation  e Sunset , com suporte às versões N e N-1.
7. Convenções. JSON em camelCase ( alias_generator  do Pydantic); datas ISO 8601
em UTC; IDs UUID; moedas virtuais como inteiro; valores em reais em centavos inteiros;
paginação por cursor; X-Correlation-Id  em toda requisição e resposta;
Idempotency-Key  como parâmetro reutilizável (ADR-14); Bearer JWT, emitido pelo
FastAPI a partir do Supabase Auth, como esquema de segurança.
Page 3 of 29
--- Page 4 ---
8. Fora do contrato REST. Chat e leilão chegam pelo Supabase Realtime, não pelo FastAPI.
Os payloads desses eventos são descritos em AsyncAPI 3.0
( asyncapi/steely.v1.yaml ), se a equipe confirmar o escopo. O único acesso direto
do cliente ao Supabase é o Realtime, com o JWT do FastAPI; arquivos privados saem
por URL assinada devolvida pelo FastAPI.
9. Autenticação pelo FastAPI. /api/v1/auth/  com login, cadastro, recuperação,
renovação do token e logout. A renovação também passa pelo FastAPI, porque o
Realtime exige token válido e o cliente não fala com o Supabase Auth.
1 0. Limite de taxa (RNF-13). Middleware slowapi: 5 requisições em 5 minutos em
autenticação e 2FA, 30 por minuto em moedas e captcha, 120 por minuto em rotas
públicas; resposta 429 com Retry-After . O contador de falhas de login (STY002:
captcha na 3ª falha, bloqueio na 5ª) fica no PostgreSQL, não na memória, porque o
FastAPI gratuito reinicia. Atrás do Cloudflare, a key_func do slowapi lê primeiro o CF-
Connecting-IP, aceito só quando a conexão vem de IPs do Cloudflare, e cai para o X-
Forwarded-For se faltar; o uvicorn confia só nos proxies do Cloudflare; sem isso todas
as requisições parecem vir do mesmo IP e o limite de 5 em 5 minutos bloquearia todos
os usuários.
1 1 . Health check. GET /api/v1/health  sem autenticação e fora do limite de taxa,
chamado a cada 10 minutos por um monitor externo (UptimeRobot, com um workflow
do GitHub Actions como redundância e alerta por e-mail ou Discord da equipe se
falhar; ADR-08), que faz ping nos dois projetos Supabase e devolve {"status": "ok",
"core_db": "up", "daas_db": "up"}, não pelo pg_cron  (ADR-16).
1 2. Endpoints internos. As rotas /api/v1/internal/jobs/...  (ex. sync-daas  e as
notificações) recebem chamadas do pg_net  pela internet pública. Exigem o
cabeçalho X-Internal-Token , guardado no Supabase Vault e nas variáveis do host,
não aceitam JWT de usuário, validam o token com secrets.compare_digest, respondem
202 Accepted de imediato e processam em BackgroundTasks, e ficam fora da
documentação pública. O WAF do Cloudflare precisa liberar o pg_net  e o monitor
externo.
1 3. Borda e CORS. O FastAPI roda no Render (Free Web Service, escolhido na ADR-08
v1.3), atrás do proxy e do WAF gratuitos do Cloudflare (ADR-08 e ADR-09). O
Cloudflare não faz cache de /api/* , e o CORS libera só o domínio do Cloudflare Pages.
5. Consequências
Positivas: web e Android trabalham em paralelo com o backend; erros iguais em todos os
módulos; tipos gerados eliminam divergência de payload; a documentação da defesa sai
pronta.
Page 4 of 29
--- Page 5 ---
Negativas ou riscos aceitos: o front depende dos PRs de contrato (501) para começar; o
snapshot precisa ser comitado a cada mudança de rota, e quem esquecer quebra o CI; o
AsyncAPI é um segundo arquivo, se aprovado; o limite de taxa do slowapi fica na memória
do processo e zera quando o FastAPI reinicia; o ataque volumétrico L7 (RNF-13) é contido
pelo Cloudflare na borda, e o slowapi complementa; os endpoints internos são públicos e
dependem de um segredo compartilhado.
O que muda: o backend ganha handlers globais de erro, o prefixo /api/v1  e o CI de
exportação, lint e compatibilidade; o repositório ganha openapi/  e, se aprovado,
asyncapi/ ; Pietro e Rafael geram os tipos a partir do snapshot; os diagramas de
arquitetura mostram o FastAPI como único ponto de escrita.
6. Validação
Lint e verificação de compatibilidade verdes no CI.
Teste de contrato (Schemathesis, ADR-17) sem divergências entre spec e backend.
Pietro e Rafael compilam o cliente gerado sem tipar nenhuma resposta à mão.
Todo erro retornado nos testes segue o formato RFC 9457.
Demonstração: Swagger UI no ar, um erro de regra de negócio e um 409 de
concorrência.
7. Plano de implementação
Tarefa Responsável Sprint
Esqueleto da spec: segurança, erros,
parâmetros comuns, paginação
Thiago A
definir
Spectral + oasdiff no CI Thiago A
definir
Scripts de mock (Prism) e geração de cliente Thiago, com Pietro e Rafael A
definir
Modelos Pydantic e rotas por módulo Dono de cada módulo; Thiago
revisa
A
definir
AsyncAPI de lances e chat Thiago A
definir
Endpoints de autenticação, slowapi e
/api/v1/health
Thiago com Fabrício A
definir
Page 5 of 29
--- Page 6 ---
8. Referências
OpenAPI Specification 3.1; AsyncAPI 3.0; documentação do FastAPI e do Pydantic v2.
RFC 9457 (Problem Details for HTTP APIs); RFC 8594 (Sunset).
Spectral, oasdiff, Prism, openapi-typescript.
RNF-02, RNF-04, RNF-09, RNF-11, RNF-13; ADR-08, ADR-09, ADR-14, ADR-17, ADR-18.
Histórico de revisões
