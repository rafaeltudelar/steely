# Banco de dados

[← Início](../README.md)

Scripts SQL do banco do Steely.

| | |
|---|---|
| **Tecnologia** | PostgreSQL 15+ gerenciado pelo Supabase |
| **Projetos** | 2 projetos separados: **Core** (operação) e **DaaS** (dados analíticos anonimizados) |
| **Extensões** | PostGIS (raio geográfico), pg_trgm (busca textual), pg_cron + pg_net (rotinas agendadas), RLS (segurança por linha) |

No celular, o cache offline usa SQLite (WatermelonDB) — ver [mobile/](../mobile/).

## Decisões que se aplicam aqui

| ADR | Assunto |
|---|---|
| [ADR-08](../docs/04-arquitetura/adr/adr-08-banco-principal.md) | Banco principal |
| [ADR-09](../docs/04-arquitetura/adr/adr-09-onde-fica-a-autorizacao.md) | Autorização no banco (RLS e funções) |
| [ADR-10](../docs/04-arquitetura/adr/adr-10-ledger-de-moedas.md) | Ledger de moedas |
| [ADR-11](../docs/04-arquitetura/adr/adr-11-armazenamento-de-imagens.md) | Armazenamento de imagens (Supabase Storage) |
| [ADR-04](../docs/04-arquitetura/adr/adr-04-k-anonimato-no-daas.md) | k-anonimato no DaaS |
| [ADR-05](../docs/04-arquitetura/adr/adr-05-retencao-e-imutabilidade-dos-logs.pdf) | Retenção e imutabilidade dos logs |

## Modelo de dados

O DER do modelo atual estava em elaboração na Sprint 13 — ver [docs/04-arquitetura](../docs/04-arquitetura/). A versão de junho/2026, do produto anterior, está em [docs/historico/diagramas](../docs/historico/diagramas/).

## Código

*Ainda não adicionado a este repositório.*
