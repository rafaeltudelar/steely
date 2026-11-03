# Documentação do Steely

[← Voltar ao início](../README.md)

A documentação está organizada do **"porquê"** para o **"como"**. As pastas são numeradas na ordem recomendada de leitura.

| # | Pasta | Pergunta que responde | Principais documentos |
|---|---|---|---|
| 01 | [Gestão](01-gestao/) | Por que o projeto existe e como foi conduzido? | TAP, Matrizes CSD/GUT/RACI/SWOT, sprints |
| 02 | [Requisitos](02-requisitos/) | O que o sistema precisa fazer? | RF/RNF v2.0, 58 casos de uso, regras de negócio, rastreabilidade |
| 03 | [Modelagem](03-modelagem/) | Como o sistema se comporta? | Diagramas de sequência, BPMN, estados |
| 04 | [Arquitetura](04-arquitetura/) | Como o sistema é construído e por quê? | Diagrama de implantação, 27 ADRs |
| 05 | [Design](05-design/) | Como o sistema se apresenta? | Manual da marca, protótipos |
| — | [Histórico](historico/) | Como era a primeira versão do produto? | Documentos do 1º semestre |

## Glossário de identificadores

Os documentos se referenciam por códigos. Esta tabela explica cada um:

| Código | Significa | Onde é definido |
|---|---|---|
| `RF-01` … `RF-22` | Requisito funcional | [Documento de requisitos v2](02-requisitos/documento-de-requisitos-v2.docx) |
| `RNF-01` … `RNF-13` | Requisito não funcional | [Documento de requisitos v2](02-requisitos/documento-de-requisitos-v2.docx) |
| `STY001` … `STY058` | Caso de uso (user story) | [Especificação dos casos de uso](02-requisitos/casos-de-uso/) |
| `STYG` | Caso de uso genérico "Manter Geral" (fluxo padrão de cadastro/edição) | [Especificação dos casos de uso](02-requisitos/casos-de-uso/) |
| `STY017-RN03` | Regra de negócio nº 03 do caso de uso STY017 | [Regras de negócio v2](02-requisitos/regras-de-negocio/) |
| `RB-01` … `RB-15` | Regra de negócio transversal (vale para o sistema todo) | [Regras transversais](02-requisitos/regras-de-negocio/) |
| `PRM-xx` | Parâmetro configurável (prazos, limites, valores) | [Regras de negócio v2](02-requisitos/regras-de-negocio/) |
| `ADR-01` … `ADR-27` | Registro de decisão de arquitetura | [ADRs](04-arquitetura/adr/) |
| `R-xx` | Risco | [Matriz GUT](01-gestao/matrizes/) |
| `UC-01` … `UC-18` | Caso de uso **do 1º semestre** (obsoleto) | [Histórico](historico/) |

## Como os documentos se conectam

```
TAP (objetivo e escopo)
 └─► RF / RNF (o que fazer)
      └─► STY (casos de uso: como acontece)
           └─► STYxxx-RNyy + PRM (regras e parâmetros)
                └─► ADR (decisão técnica que atende)
                     └─► Código (backend, web, mobile, database, scanner)
```

A [matriz de rastreabilidade](02-requisitos/rastreabilidade/) registra essas ligações item a item.

## Formatos

- **`.md`** abre formatado direto no GitHub.
- **`.pdf`** abre no visualizador do GitHub.
- **`.xlsx` e `.docx`** precisam ser baixados (botão *Download raw file*). Por isso, o README de cada pasta resume o conteúdo dessas planilhas e documentos.
