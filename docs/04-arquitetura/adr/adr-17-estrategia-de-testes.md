# ADR-17 — Estratégia de testes
**Architecture Decision Record · Projeto Steely · Escola de TI · UniCesumar**

| Campo | Valor | Campo | Valor |
| --- | --- | --- | --- |
| **Status** | ☒ Proposto  ☐ Aceito  ☐ Rejeitado  ☐ Substituído pelo ADR-___ | **Data** | 01/11/2026 |
| **Responsável** | Thiago Lopes Martins | **Sprint** | Sprint 8–9 / 15–17 (Entrega até 23/11) |
| **Participantes** | Thiago Lopes Martins, Fabrício Notoya Thomas, Augusto Palma Guglielmi, Pietro Pasqual Silva, Rafael Tudela Rizental | | |
| **Vínculos** | L-03 · D3 Matriz CSD · RNF-02 · RNF-04..06 · RNF-09 · RNF-10 · RNF-13 · ADR-03..05 · ADR-09 · ADR-12..16 · ADR-20 · ADR-23..27 | | |

## 1. Contexto *(obrigatória)*

A lacuna `L-03` aponta que não há estratégia de testes definida, e a `D3` da Matriz CSD pede definição da pirâmide e metas de cobertura. Os requisitos têm limites mensuráveis que precisam de prova: leitura p95 ≤ 200 ms e escrita p99 ≤ 500 ms (`RNF-04`), validação do QR em ≤ 150 ms offline (`RNF-02`), Scanner IA em ≤ 4 s com Circuit Breaker (`RNF-05`), propagação de lance ≤ 100 ms (`RNF-06`), idempotência (`RNF-09`), Lighthouse ≥ 90 e WCAG 2.1 AA (`RNF-10`) e limite de taxa (`RNF-13`).

As regras mais arriscadas (moedas, escrow, leilão, prazos, autorização, auditoria e anonimização) ficam em funções SQL e políticas RLS (`ADR-03..10`, `ADR-14..16`), então teste de unidade de código de aplicação sozinho não as protege. Stack definida: FastAPI (`ADR-13`), PostgreSQL no Supabase (`ADR-08`), Web em React + Vite (`ADR-18..22`) e Android com Expo + React Native (`ADR-23..27`).

## 2. Direcionadores da decisão *(recomendada)*

- **Cobrir primeiro o que custa mais se falhar:** dinheiro simulado (escrow), moedas, leilão, idempotência, auditoria e controle de acesso.
- **Provar os limites dos RNFs com medição automatizada** e ferramentas gratuitas no CI (GitHub Actions + `supabase start`).
- **Esforço compatível com a entrega até 23/11** e geração de evidências apresentáveis na banca.

## 3. Opções consideradas *(obrigatória)*

| Opção A — Pirâmide clássica uniforme | Opção B — Pirâmide orientada a risco (com pgTAP e contrato) | Opção C — Testes manuais com roteiros + smoke |
| --- | --- | --- |
| **Descrição:** Muitos testes de unidade, alguns de integração e poucos E2E, com a mesma meta em todos os módulos.<br>**Prós:**<br>• Simples de explicar.<br>• Rápida no CI.<br>**Contras:**<br>• Teste de unidade de código não pega falha de regra em funções SQL/RLS.<br>• Esforço igual em módulo trivial e crítico. | **Descrição:** Pirâmide com integração reforçada onde a regra está no banco (pgTAP) e metas mais altas nos módulos críticos.<br>**Prós:**<br>• Foca o esforço onde o risco é maior.<br>• Testa de verdade funções SQL, triggers e RLS.<br>• Comprova cada RNF.<br>**Contras:**<br>• Exige subir container de banco no CI (supabase start). | **Descrição:** Roteiros de teste por caso de uso executados à mão antes da entrega.<br>**Prós:**<br>• Quase sem configuração inicial.<br>**Contras:**<br>• Não escala, não prova RNF de concorrência/latência e não impede regressão em PR. |

## 4. Decisão *(obrigatória)*

**Opção escolhida:** ☐ A  ☒ B  ☐ C

**Opção escolhida: B — Pirâmide orientada a risco.** Mantém a pirâmide e reforça a camada de banco (`pgTAP`) e contrato (`Schemathesis`) para proteger a arquitetura dos `ADR-03..16`:

| Camada | Alvo | Ferramenta | Peso |
| --- | --- | --- | --- |
| Unidade | Lógica pura e utilitários (backend, web, mobile, schemas) | `pytest`, `Vitest` (web) e `Jest` (React Native) | ~60% |
| Componente e A11y | Telas, formulários e acessibilidade | `React Testing Library` + `jest-axe` | ~15% |
| Banco e regras | Funções SQL, RLS (`authenticated`), ledger, escrow, leilão, varreduras, triggers append-only e partições de logs (`ADR-05`), GRANTs de `private` e Data API desligada (`ADR-09`) | `pgTAP` (`supabase test db`) | ~10% |
| API e contrato | Endpoints contra o OpenAPI 3.1 (`ADR-13`) com banco em container | `pytest` + `HTTPX` + `Schemathesis` | ~10% |
| Ponta a ponta (E2E) | Fluxos críticos: publicar, negociar, QR offline, leilão | `Playwright` (web) e `Maestro` (Android) | ~5% |
| Carga, UI e Resiliência | `RNF-04`, `RNF-06`, `RNF-13`; Lighthouse ≥ 90 / WCAG 2.1 AA (`ADR-20`); Circuit Breaker Scanner (`RNF-05`) e QR ≤ 150 ms (`RNF-02`) | `k6`, `Lighthouse CI` + `axe`, injeção de falha e micro-benchmark | Por PR / Sprint |

**Cobertura mínima e Regras de processo:** Global ≥ 70% das linhas; Módulos críticos (ledger, leilão, escrow, idempotência, varreduras, autorização) ≥ 85% das linhas e ≥ 75% dos ramos; Telas ≥ 60%. Toda regra Alta/Crítica (`RB-01, 02, 04, 06..11, 15`) tem ao menos um teste automatizado. Dados de teste são sintéticos (LGPD), inclusive o `seed_demo_daas.sql` da demonstração, que marca as linhas como `"DEMONSTRAÇÃO"`, respeita `k >= 30` transações e `COUNT(DISTINCT vendedor_id) >= 3` por recorte (valor em `app_config`) e é removido do Projeto 2 depois da banca (`ADR-04`).

## 5. Consequências *(obrigatória)*

- **Positivas:** O esforço foca no que custa mais se falhar; cada RNF mensurável ganha evidência automatizada; relatórios de cobertura e matriz de rastreabilidade servem diretamente à defesa (fechando a `L-03`).
- **Negativas ou riscos aceitos:** O CI sobe banco em container (`supabase start`); limites dos planos gratuitos (Render Free / Realtime) durante o teste de carga k6 são documentados junto ao resultado medido.
- **O que muda no código, banco e diagramas:** Pastas de teste por camada, `supabase/tests/` com suites pgTAP, scripts k6 e pipeline GitHub Actions.

## 6. Validação *(recomendada)*

- Pipeline de CI rodando as 7 camadas e bloqueando PR com falha ou queda de cobertura.
- 100% das regras de negócio Críticas e Altas com pelo menos um teste automatizado verde.
- Relatórios do k6, do Lighthouse CI e de cobertura anexados ao material da defesa.

## 7. Plano de implementação *(recomendada)*

| Tarefa | Responsável | Sprint |
| --- | --- | --- |
| Pipeline de CI (supabase start) e metas de cobertura | Thiago | Sprint 8 (15) |
| Ambiente de banco de teste e dados sintéticos (seed_demo_daas.sql) | Thiago e Fabrício | Sprint 8 (15–16) |
| Testes de componente, Vitest, Playwright e Lighthouse CI | Pietro | Sprint 8–9 (16–17) |
| Testes do app Android (Jest + Maestro) e QR offline ≤ 150 ms | Rafael | Sprint 8–9 (16–17) |
| pgTAP de ledger, escrow, auditoria, anonimização e RLS | Fabrício e Augusto | Sprint 8–9 (16–17) |
| Testes de idempotência, lances, varreduras e cenários k6 | Thiago | Sprint 9 (17) |

## 8. Referências *(recomendada)*

- Martin Fowler, *The Practical Test Pyramid*; pgTAP, Schemathesis, Playwright, Maestro, k6, Lighthouse CI, axe-core.
- L-03, D3 da Matriz CSD; RNF-02, RNF-04..06, RNF-09, RNF-10, RNF-13.
- ADR-03..05, ADR-09, ADR-12..16, ADR-20, ADR-23..27.

## Histórico de revisões

| Versão | Data | Autor | Alteração |
| --- | --- | --- | --- |
| 0.1 | 31/10/2026 | Thiago Lopes Martins | Rascunho inicial |
| 0.2 | 31/10/2026 | Thiago Lopes Martins | Ferramentas do backend definidas (pytest, HTTPX) conforme o ADR-13 |
| 0.3 | 31/10/2026 | Thiago Lopes Martins | Vite confirmado; testes de RLS, partições de logs e limite de taxa incluídos |
| 0.4 | 31/10/2026 | Thiago Lopes Martins | Teste do envio ao DaaS com k ≥ 30 incluído |
| 0.5 | 31/10/2026 | Thiago Lopes Martins | Teste de GRANTs das funções, CI com supabase start, carga atrás do Cloudflare e seed sintético do DaaS |
| 0.6 | 31/10/2026 | Thiago Lopes Martins | Teste de GRANTs do schema private com Data API desabilitada; host de carga passa a ser o Render Free |
| 0.7 | 01/11/2026 | Thiago Lopes Martins | Seed do DaaS rotulado DEMONSTRAÇÃO, com mínimo de 3 vendedores por recorte, removido após a banca |

---

## Anexo — Texto Integral Detalhado (Documento Original)

ADR-17 — Estratégia de testes
Architecture Decision Record · Projeto Steely · Escola de TI · UniCesumar
1. Contexto
A lacuna L-03 aponta que não há estratégia de testes definida, e a D3 da Matriz CSD pede
uma resposta; o texto de L-03 e D3 não está nos documentos que recebi, então assumo
que perguntam como e quanto vamos testar. Os requisitos têm limites mensuráveis que
precisam de prova: leitura p95 ≤ 200 ms e escrita p99 ≤ 500 ms com 1.000 usuários (RNF-
04), validação do QR em ≤ 150 ms offline (RNF-02), Scanner IA em ≤ 4 s com Circuit
Breaker (RNF-05), propagação de lance ≤ 100 ms (RNF-06), idempotência (RNF-09),
Lighthouse ≥ 90 e WCAG 2.1 AA (RNF-10) e limite de taxa (RNF-13).
São 5 pessoas e 23 dias até 23/11/2026. As regras mais arriscadas (moedas, escrow, leilão,
prazos, autorização) ficam em funções SQL e políticas RLS (ADR-09, 14, 15 e 16), então
teste de unidade de código de aplicação sozinho não as protege. Definido: backend
Versão Data Autor Alteração
0.10 01/11/2026 Thiago Lopes
Martins
Prazo de 72 h do moderador em app_config,
aviso de 7 dias antes do fim da carência de
exclusão e desligamento do endpoint de
demonstração após a banca
Campo Valor
Status ☒  Proposto ☐  Aceito ☐  Rejeitado ☐  Substituído
pelo ADR-___
Data 31/10/2026
Responsável Thiago Lopes Martins
Sprint A definir (pergunta em aberto)
Participantes Thiago (autor). Revisão sugerida: toda a equipe, por
afetar a Definição de Pronto
Vínculos L-03, D3 da Matriz CSD · RNF-02, RNF-04, RNF-05,
RNF-06, RNF-09, RNF-10, RNF-13 · ADR-09, ADR-12,
ADR-13, ADR-14, ADR-15, ADR-16, ADR-20
Page 24 of 29
--- Page 25 ---
Python com FastAPI (ADR-13), PostgreSQL no Supabase e Android com Expo e React
Native (inferido dos ADR-24 e 25, a confirmar). Web em React com Vite (confirmado por
Fabrício e Pietro).
2. Direcionadores da decisão
Cobrir primeiro o que custa mais se falhar: dinheiro, moedas, leilão, escrow e acesso.
Provar os limites dos RNFs com medição, não com opinião.
Ferramentas gratuitas, rodando no CI sem manutenção.
Esforço compatível com 3 semanas e 5 pessoas.
Evidência apresentável na defesa (relatórios, cobertura, rastreabilidade).
3. Opções consideradas
4. Decisão
Opção escolhida: ☒  B. Mantém a pirâmide pedida e a torna útil para a arquitetura
escolhida nos ADR-14, 15 e 16. A foi descartada por não alcançar as regras no banco; C, por
não provar nenhum RNF.
Camadas e ferramentas (propostas; as dependentes de stack a confirmar):
Opção A — Pirâmide
clássica uniforme
Opção B — Pirâmide
orientada a risco
Opção C — Manual com
roteiros
Descrição Muitos testes de
unidade, alguns de
integração, poucos
E2E, igual em todos os
módulos.
A pirâmide, com
integração reforçada
onde a regra está no
banco e metas mais
altas nos módulos
críticos.
Roteiros de teste por
caso de uso, executados
à mão, mais um smoke
automatizado.
Prós Simples de explicar.
Rápida no CI.
Foca o esforço onde o
risco é maior. Testa de
verdade as funções
SQL e a RLS.
Quase sem configuração.
Contras Unidade de código não
pega falha de regra no
banco. Esforço igual em
módulo trivial e crítico.
Exige ambiente de
banco no CI. Metas
diferentes confundem
a equipe no início.
Não escala, não prova
RNF e depende de
lembrar de rodar.
Page 25 of 29
--- Page 26 ---
Camada Alvo Ferramenta Peso
aproximado
Unidade Lógica pura e utilitários
(backend, web, mobile,
compartilhado)
pytest (backend), Vitest
(web) e Jest (React
Native)
~60%
Componente e
acessibilidade
Telas e formulários React Testing Library +
axe
~15%
Banco e regras Funções SQL, RLS, ledger,
leilão, varreduras, trigger
append-only e partições
dos logs (ADR-05), RLS
com o papel
authenticated como o
FastAPI faz (ADR-09),
GRANTs do schema
private e Data API
desabilitada (um usuário
não executa as funções
pelo PostgREST; elas
repetem status ACTIVE,
KYC e Trust Score)
pgTAP ( supabase test
db )
~10%
API e contrato Endpoints contra o
OpenAPI (ADR-13)
pytest + HTTPX
(TestClient do FastAPI),
Schemathesis e testes
de integração com
banco real em contêiner
~10%
Ponta a ponta Fluxos críticos: publicar,
negociar, QR, leilão
Playwright (web) e
Maestro (Android)
~5%
Carga RNF-04, RNF-06, RNF-13 k6 cenários
nomeados
Qualidade de
interface
Lighthouse ≥ 90 e WCAG
2.1 AA (ADR-20)
Lighthouse CI + axe todo PR
Page 26 of 29
--- Page 27 ---
Cobertura mínima (proposta, a ratificar pela equipe).
Global: ≥ 70% das linhas (pytest-cov no backend; cobertura do Vitest e do Jest no
front).
Módulos críticos (ledger e moedas, leilão, escrow, idempotência, varreduras,
autorização): ≥ 85% das linhas e ≥ 75% dos ramos.
Telas: ≥ 60%.
Rastreabilidade: toda regra de importância Alta ou Crítica (RB-01, 02, 04, 06, 07, 08, 09,
10, 11, 15) tem ao menos um teste automatizado ligado a ela.
O CI reprova PR que fique abaixo da meta ou reduza a cobertura.
Regras de processo. Um STY só entra na Definição de Pronto com testes ligados às suas
regras. Dados de teste são sintéticos (LGPD), inclusive o seed_demo_daas.sql da
demonstração, que marca as linhas como DEMONSTRAÇÃO, respeita k ≥ 30 transações e
COUNT(DISTINCT vendedor_id) ≥ 3 por recorte (valor em app_config) e sai do Projeto 2
depois da banca; imagens do Scanner vêm de um conjunto de referência próprio. O CI
roda unidade, componente, banco, contrato e Lighthouse em todo PR; E2E na main  e
antes de cada revisão de sprint; carga uma vez por sprint e antes da defesa.
5. Consequências
Positivas: o esforço vai para o que custa mais se falhar; cada RNF mensurável ganha
evidência; o relatório de cobertura e a matriz de rastreabilidade servem à defesa; a L-03
fecha.
Negativas ou riscos aceitos: o CI fica mais lento e exige banco em contêiner (supabase
start), pois os dois projetos gratuitos da nuvem são o Core e o DaaS de produção; seis
ferramentas para aprender em poucas semanas; o teste de 1.000 usuários e 1.000
conexões pode não ser viável nos planos gratuitos (Render Free, Realtime), e o Cloudflare
pode bloquear o k6 se o IP do CI não for liberado no WAF, e nesse caso se registra o limite
medido e o desvio em relação ao RNF.
Camada Alvo Ferramenta Peso
aproximado
Resiliência Circuit Breaker do
Scanner (RNF-05), QR
offline ≤ 150 ms (RNF-
02), limite de taxa e
contador de login após
reiniciar o FastAPI (RNF-
13)
Injeção de falha e micro-
benchmark no
dispositivo
casos
nomeados
Page 27 of 29
--- Page 28 ---
O que muda: pipeline de CI com etapas de teste e metas de cobertura; pasta de testes de
banco; conjunto de dados sintéticos; matriz RF/RB para teste; Definição de Pronto
atualizada.
6. Validação
CI verde em todo PR, com as metas de cobertura aplicadas.
Matriz de rastreabilidade cobre 100% das regras Alta e Crítica.
Relatório dos RNFs: valor medido contra a meta, para RNF-02, 04, 05, 06, 10 e 13.
Cenários de idempotência, concorrência de lances e varreduras (ADR-14, 15 e 16)
automatizados e verdes; envio ao DaaS só com k ≥ 30 (um pacote de 29 registros não
sai).
Demonstração: relatório de cobertura, execução do k6 e do Lighthouse.
7. Plano de implementação
8. Referências
Test Pyramid (Martin Fowler) e Testing Trophy (Kent C. Dodds).
pgTAP, Playwright, Maestro, k6, Lighthouse CI, axe-core, Schemathesis.
RNF-02, 04, 05, 06, 09, 10, 13; ADR-09, 12, 13, 14, 15, 16, 20.
Histórico de revisões
Tarefa Responsável Sprint
Pipeline de CI e metas de cobertura Thiago A definir
Ambiente de banco de teste e dados sintéticos Thiago com Fabrício A definir
Testes de componente e Lighthouse CI Pietro A definir
