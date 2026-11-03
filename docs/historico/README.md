# Histórico — 1º semestre (mar–jun/2026)

[← Documentação](../README.md)

> ⚠️ **Estes documentos descrevem a primeira versão do produto e não estão mais vigentes.** Ficam aqui para mostrar a evolução do projeto.

## O que mudou

No 1º semestre, o Steely era uma **plataforma de doação e coleta de sucata eletrônica**, com os perfis Doador, Coletor e Instituição. No 2º semestre, virou um **marketplace de hardware reaproveitável**, com Scanner IA, leilões, moedas virtuais, escrow e DaaS.

Por isso a numeração dos documentos mudou, e **o mesmo código pode significar coisas diferentes**:

| Código | 1º semestre (este histórico) | 2º semestre (vigente) |
|---|---|---|
| Casos de uso | `UC-01` a `UC-18` | `STY001` a `STY058` |
| `RF-10` | Mural Institucional | Agendamento, rotas e pontos de coleta |
| `RNF-07` | Otimização de imagem | Offline-first |

Ao ler um ADR ou documento atual, use sempre a [numeração vigente](../02-requisitos/).

## Conteúdo

| Arquivo | O que é | Substituído por |
|---|---|---|
| [casos-de-uso/diagrama-de-casos-de-uso-mar-2026.pdf](casos-de-uso/diagrama-de-casos-de-uso-mar-2026.pdf) | Primeiro diagrama de casos de uso ("Plataforma de Sucata"), 18 casos | [Casos de uso](../02-requisitos/casos-de-uso/) |
| [casos-de-uso/documento-de-casos-de-uso-mai-2026.pdf](casos-de-uso/documento-de-casos-de-uso-mai-2026.pdf) | 16 casos de uso narrativos (UC-01 a UC-16) | [Casos de uso](../02-requisitos/casos-de-uso/) |
| [casos-de-uso/diagrama-de-casos-de-uso-mai-2026.pdf](casos-de-uso/diagrama-de-casos-de-uso-mai-2026.pdf) | Diagrama dos 16 casos de uso | [Casos de uso](../02-requisitos/casos-de-uso/) |
| [requisitos/documento-de-requisitos-v1-mai-2026.pdf](requisitos/documento-de-requisitos-v1-mai-2026.pdf) | RF-01 a RF-21 e RNF-01 a RNF-09 | [Requisitos v2](../02-requisitos/) |
| [diagramas/diagrama-de-classe-jun-2026.png](diagramas/diagrama-de-classe-jun-2026.png) | Diagrama de classe com 10 classes (Usuário, Oferta, Proposta, Transação, Agenda...) | Em elaboração (Sprint 13) |
| [diagramas/der-jun-2026.png](diagramas/der-jun-2026.png) | DER com 10 tabelas | Em elaboração (Sprint 13) |
| [diagramas/sequencia-detalhado/](diagramas/sequencia-detalhado/) | 18 diagramas de sequência (UC-01 a UC-18) com App, Sistema, BD e serviços externos | [Diagramas de sequência](../03-modelagem/) |
| [diagramas/sequencia-simplificado/](diagramas/sequencia-simplificado/) | Os mesmos 18 casos de uso, em versão simplificada (ator × sistema) | [Diagramas de sequência](../03-modelagem/) |
