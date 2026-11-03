# Back-end — API

[← Início](../README.md)

API REST que concentra as regras de negócio do Steely. Toda escrita e toda leitura protegida passam por ela; os apps só falam direto com o Supabase para o Realtime.

| | |
|---|---|
| **Tecnologia** | Python · FastAPI · Pydantic v2 |
| **Hospedagem** | Render |
| **Banco** | PostgreSQL no Supabase — ver [database/](../database/) |

## Decisões que se aplicam aqui

| ADR | Assunto |
|---|---|
| [ADR-09](../docs/04-arquitetura/adr/adr-09-onde-fica-a-autorizacao.md) | Autorização em duas camadas (FastAPI + PostgreSQL) |
| [ADR-13](../docs/04-arquitetura/adr/adr-13-contrato-e-versionamento-da-api.md) | Contrato OpenAPI, versionamento `/api/v1` e formato de erro |
| [ADR-14](../docs/04-arquitetura/adr/adr-14-idempotencia.md) | Idempotência com `Idempotency-Key` |
| [ADR-15](../docs/04-arquitetura/adr/adr-15-concorrencia-dos-lances.md) | Concorrência dos lances nos leilões |
| [ADR-16](../docs/04-arquitetura/adr/adr-16-tarefas-agendadas.md) | Tarefas agendadas (`pg_cron`) |
| [ADR-17](../docs/04-arquitetura/adr/adr-17-estrategia-de-testes.md) | Estratégia de testes |
| [ADR-02](../docs/04-arquitetura/adr/adr-02-censura-de-dados-pessoais.md) | Censura de dados pessoais no chat |
| [ADR-03](../docs/04-arquitetura/adr/adr-03-escrow-simulado.md) | Escrow e retenção de 7 dias |

## Código

*Ainda não adicionado a este repositório.*
