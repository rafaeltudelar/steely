# Matrizes de gestão

[← Gestão](../README.md)

| Arquivo | Matriz | Para que serve |
|---|---|---|
| [matriz-csd-equipe.xlsx](matriz-csd-equipe.xlsx) | **CSD** — Certezas, Suposições e Dúvidas | Versão oficial da equipe (v1.0, 06/09/2026). Cruza o TAP, a GUT, as regras de negócio e a SWOT |
| [matriz-csd-scanner-ia-e-censura.xlsx](matriz-csd-scanner-ia-e-censura.xlsx) | **CSD** complementar | Aprofunda as certezas, suposições e dúvidas do Scanner IA e da censura de dados (ADR-01 e ADR-02), com a fonte de cada item |
| [matriz-gut-riscos.xlsx](matriz-gut-riscos.xlsx) | **GUT** — Gravidade, Urgência e Tendência | 15 riscos do projeto (`R-01` a `R-15`), 10 deles priorizados, com os critérios de pontuação |
| [matriz-raci.xlsx](matriz-raci.xlsx) | **RACI** — Responsável, Aprovador, Consultado, Informado | 19 entregáveis × 13 papéis, a partir dos 58 casos de uso |
| [analise-swot.png](analise-swot.png) | **SWOT** — Forças, Fraquezas, Oportunidades e Ameaças | Posicionamento do produto (Scanner IA, Captcha, escrow, DaaS) |

> **Atenção na GUT:** o risco `R-08` fala em SQLite como banco do servidor. Essa opção foi descartada no [ADR-08](../../04-arquitetura/adr/adr-08-banco-principal.md): o banco principal é PostgreSQL (Supabase), e o SQLite ficou só para o cache offline do celular.
