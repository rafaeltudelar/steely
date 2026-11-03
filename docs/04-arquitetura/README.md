# 04 · Arquitetura

[← Documentação](../README.md)

Como o Steely é construído e **por que** cada escolha foi feita.

| Documento | O que é |
|---|---|
| [diagrama-de-implantacao.pdf](diagrama-de-implantacao.pdf) | Onde cada parte roda: apps clientes, API, Supabase (Auth, PostgREST, Realtime, Edge Functions, pg_cron, Storage) e o serviço de IA |
| [adr/](adr/) | Os **27 ADRs** — registros de decisão de arquitetura |

## Visão geral

| Camada | Tecnologia | Decidido em |
|---|---|---|
| Mobile (Android) | Expo (React Native), WatermelonDB para o modo offline | [ADR-23](adr/adr-23-offline-first.md) a [ADR-27](adr/adr-27-captura-e-compressao-de-imagem.md) |
| Web | SPA em React + Vite, publicada no Cloudflare Pages · TanStack Query + Zustand | [ADR-18](adr/adr-18-estado-e-cache-de-dados-no-web.pdf) a [ADR-22](adr/adr-22-dashboard-e-esg.pdf) |
| API | FastAPI (Python), no Render | [ADR-13](adr/adr-13-contrato-e-versionamento-da-api.md), [ADR-09](adr/adr-09-onde-fica-a-autorizacao.md) |
| Banco de dados | PostgreSQL no Supabase, em 2 projetos: Core e DaaS | [ADR-08](adr/adr-08-banco-principal.md) |
| Tempo real | Supabase Realtime (chat e leilões) | [ADR-08](adr/adr-08-banco-principal.md), [ADR-15](adr/adr-15-concorrencia-dos-lances.md) |
| Captcha | Cloudflare Turnstile | [ADR-21](adr/adr-21-provedor-de-captcha.pdf) |
| Mapas e rotas | Google Routes API | [ADR-26](adr/adr-26-provedor-de-mapas-e-rotas.md) |
| Scanner IA | Pipeline próprio em ONNX: classificação hierárquica + busca vetorial (FAISS) + OCR | [ADR-01](adr/adr-01-motor-do-scanner-ia.md), [ADR-12](adr/adr-12-limiar-de-confianca-do-scanner.md) |

Restrição que guiou quase todas as decisões: **custo zero** (planos gratuitos) e entrega até a banca.

## Diagrama de classe e DER

O diagrama de classe e o DER do modelo atual estavam em elaboração na Sprint 13 (tarefas EDTS-318 e EDTS-319) e ainda não foram entregues. As versões de junho/2026, do produto anterior, estão em [historico/diagramas](../historico/diagramas/).

> **Ponto em aberto:** o diagrama de implantação cita os schemas `public`, `ledger` e `audit`, e a tarefa do DER prevê `public`, `private`, `escrow`, `audit`, `esg` e `daas`. A referência para alinhar é o [ADR-08](adr/adr-08-banco-principal.md).
