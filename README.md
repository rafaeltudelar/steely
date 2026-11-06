<a href="https://rafaeltudelar.github.io/steely/"><img src=".github/assets/banner.svg" alt="Steely — hardware usado, com laudo de IA" width="100%"></a>

<p align="center">
  <a href=".github/workflows/verificacoes.yml"><img alt="Verificações" src="https://github.com/rafaeltudelar/steely/actions/workflows/verificacoes.yml/badge.svg"></a>
  <img alt="Status: em desenvolvimento" src="https://img.shields.io/badge/status-em%20desenvolvimento-1DDB6A?labelColor=0D1B2A">
  <img alt="Sprints 7 a 16" src="https://img.shields.io/badge/sprints-7%E2%80%9316-A8EFC4?labelColor=0D1B2A">
  <a href="LICENSE"><img alt="Código: MIT" src="https://img.shields.io/badge/c%C3%B3digo-MIT-6B7A8D?labelColor=0D1B2A"></a>
  <a href="LICENSE-DOCS.md"><img alt="Docs: CC BY 4.0" src="https://img.shields.io/badge/docs-CC%20BY%204.0-6B7A8D?labelColor=0D1B2A"></a>
</p>

# Steely

**Marketplace de hardware de TI reaproveitável, com laudo técnico por Inteligência Artificial.**

Projeto acadêmico da **Escola de TI — UniCesumar** (2026). Veja o [site do projeto](https://rafaeltudelar.github.io/steely/) com o Scanner IA em 3D e os protótipos navegáveis.

> **Status: em desenvolvimento — 2º semestre de 2026 (Sprints 7–16).** A documentação está completa e os protótipos de tela estão sendo produzidos sprint a sprint. Quer ajudar? Veja [como contribuir](CONTRIBUTING.md).

---

## O problema

Todos os dias, empresas e pessoas descartam computadores e peças que ainda funcionam — só não servem mais para quem os tinha. Um PC com pouca memória RAM é "lixo" para uma empresa, mas é perfeito para virar um totem de sinalização digital ou o computador de uma sala de aula. Não existe hoje um lugar **confiável** que conecte quem quer se desfazer desse equipamento com quem precisa dele. E quem compra hardware usado em canais informais não tem garantia nenhuma sobre o estado real do produto.

## A solução

O Steely é uma plataforma (app Android + web + painel administrativo) que conecta três perfis:

| Perfil | O que faz |
|---|---|
| **Vendedor** | Anuncia o equipamento para vender, leiloar ou doar |
| **Comprador** | Procura exatamente a peça "imperfeita" que serve para o seu uso |
| **Instituição** (ONG, escola) | Solicita e recebe doações pelo Mural Institucional |

A confiança vem de duas camadas: um **laudo técnico gerado por IA** (o Scanner IA analisa as fotos e identifica o componente e seus defeitos) e a **validação da comunidade** (o Hardware Captcha).

### Principais funcionalidades

- **Scanner IA** — identifica o hardware pelas fotos e preenche o anúncio automaticamente
- **Hardware Captcha** — a comunidade valida se o anúncio corresponde ao produto
- **Chat interno** com bloqueio automático de telefones e e-mails
- **Leilões exclusivos** com moeda social e proteção anti-sniping
- **Agendamento e rotas** até o ponto de encontro, funcionando offline
- **QR Code de entrega** assinado digitalmente, validado mesmo sem internet
- **Garantia de 7 dias** com valor retido em custódia (escrow) e arbitragem de disputas
- **Carteira de moedas virtuais** (cashback)
- **Métricas ESG** (CO₂ evitado, material reaproveitado) e **relatórios DaaS** anonimizados sobre falhas recorrentes
- **Painel de moderação**

---

## O app

Protótipos de alta fidelidade da Sprint 13 — [todas as telas](docs/05-design/prototipos/) · [como fazer uma tela nova](docs/05-design/PASSO-A-PASSO-SIMPLES.md) ([guia completo](docs/05-design/GUIA-DE-PROTOTIPOS.md)).

<p align="center">
  <img src="docs/05-design/prototipos/png/001-home-feed.png" width="15%" alt="Home">
  <img src="docs/05-design/prototipos/png/002-central-de-notificacoes.png" width="15%" alt="Notificações">
  <img src="docs/05-design/prototipos/png/003-criar-anuncio-etapa-1-fotos.png" width="15%" alt="Criar anúncio: fotos">
  <img src="docs/05-design/prototipos/png/004-criar-anuncio-etapa-2-detalhes.png" width="15%" alt="Criar anúncio: detalhes">
  <img src="docs/05-design/prototipos/png/005-criar-anuncio-etapa-3-preco-e-entrega.png" width="15%" alt="Criar anúncio: preço e entrega">
  <img src="docs/05-design/prototipos/png/006-criar-anuncio-etapa-4-revisao.png" width="15%" alt="Criar anúncio: revisão">
</p>

---

## Arquitetura em uma frase

App **Expo** (Android) e SPA **React + Vite** (web) consomem uma API **FastAPI** (Python), que usa **Supabase** (PostgreSQL, Auth, Realtime, Storage) como banco e infraestrutura; o Scanner IA roda como um serviço separado com modelos **ONNX**.

Detalhes, diagrama de implantação e as 27 decisões de arquitetura (ADRs): [docs/04-arquitetura](docs/04-arquitetura/).

---

## Mapa do repositório

| Pasta | O que tem |
|---|---|
| [`docs/`](docs/) | **Toda a documentação do projeto** — comece por aqui |
| [`docs/01-gestao/`](docs/01-gestao/) | Termo de Abertura (TAP), matrizes (CSD, GUT, RACI, SWOT) e histórico das sprints |
| [`docs/02-requisitos/`](docs/02-requisitos/) | Requisitos, 58 casos de uso, regras de negócio e matriz de rastreabilidade |
| [`docs/03-modelagem/`](docs/03-modelagem/) | Diagramas de sequência, BPMN e de estados |
| [`docs/04-arquitetura/`](docs/04-arquitetura/) | Diagrama de implantação e os 27 ADRs |
| [`docs/05-design/`](docs/05-design/) | Manual da marca e protótipos de tela |
| [`docs/historico/`](docs/historico/) | Documentos do 1º semestre (versão anterior do produto) |
| [`backend/`](backend/) | API — FastAPI |
| [`web/`](web/) | Aplicação web — React + Vite |
| [`mobile/`](mobile/) | Aplicativo Android — Expo |
| [`database/`](database/) | Banco de dados — scripts SQL do Supabase |
| [`scanner/`](scanner/) | Scanner IA — visão computacional |
| [`ferramentas/`](ferramentas/) | Scripts que geram e verificam as telas e os links |
| [`site/`](site/) | Site do projeto (GitHub Pages) com a cena 3D e os protótipos navegáveis |

## Por onde começar a ler

1. **Este README** — o que é o Steely
2. [**TAP — Termo de Abertura**](docs/01-gestao/tap-termo-de-abertura-do-projeto.pdf) — objetivo, escopo e não escopo
3. [**Requisitos**](docs/02-requisitos/) — o que o sistema precisa fazer
4. [**Casos de uso**](docs/02-requisitos/casos-de-uso/) — como cada funcionalidade acontece
5. [**Arquitetura e ADRs**](docs/04-arquitetura/) — como e por que o sistema foi desenhado assim

---

## Linha do tempo

O projeto teve **duas gerações**. Saber disso evita confusão ao ler os documentos:

| Período | Produto | Numeração dos documentos |
|---|---|---|
| **1º semestre** (mar–jun/2026, Sprints 1–6) | Plataforma de doação e coleta de sucata eletrônica (Doador, Coletor, Instituição) | UC-01 a UC-18, RF-01 a RF-21 |
| **2º semestre** (ago–nov/2026, Sprints 7–16) | Marketplace de hardware com Scanner IA, leilões, moedas e escrow | STY001 a STY058, RF-01 a RF-22 (v2.0) |

Os documentos vigentes são os do 2º semestre. Os do 1º semestre ficam em [`docs/historico/`](docs/historico/) — **atenção: os mesmos números (ex.: RF-10) significam coisas diferentes nas duas gerações.**

---

## Equipe

| Nome | Papel / área principal | ADRs |
|---|---|---|
| Thiago Lopes Martins | Product Owner · back-end e contrato da API | 13–17 |
| Augusto Palma Guglielmi | Regras de negócio, conformidade (LGPD) e modelagem de dados | 03–07 |
| Fabricio Notoya Thomas | Scanner IA, banco de dados e segurança | 01–02, 08–12 |
| Pietro Pasqual Silva | Front-end web | 18–22 |
| Rafael Tudela Rizental | Mobile, prototipação e identidade visual | 23–27 |

Participaram do 1º semestre: Guilherme Pitão Garcia e Victor Hugo Silva Garcia.

A gestão foi compartilhada entre os colaboradores, com cerimônias Scrum semanais — veja [docs/01-gestao/scrum](docs/01-gestao/scrum/).

## Como contribuir

Toda mudança entra por Pull Request, com revisão e verificações automáticas. O passo a passo está em [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Licença

Código sob a [licença MIT](LICENSE). Documentação, protótipos e manual da marca sob a [CC BY 4.0](LICENSE-DOCS.md) — use à vontade, citando a equipe.
