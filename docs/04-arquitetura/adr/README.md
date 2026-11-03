# ADRs — Registros de Decisão de Arquitetura

[← Arquitetura](../README.md)

Um **ADR** (*Architecture Decision Record*) registra uma decisão técnica importante: o problema, as opções consideradas, a opção escolhida e as consequências. Todos seguem o mesmo modelo:

1. Contexto · 2. Direcionadores da decisão · 3. Opções consideradas · 4. Decisão · 5. Consequências · Histórico de versões

Status de todos: **Proposto**.

## Índice

| ADR | Decisão | Área | Autor |
|---|---|---|---|
| [01](adr-01-motor-do-scanner-ia.md) | Arquitetura e motor de visão computacional do Scanner IA | Scanner IA | Fabricio |
| [02](adr-02-censura-de-dados-pessoais.md) | Censura e mascaramento de dados pessoais no chat e nos anúncios | Segurança | Fabricio |
| [03](adr-03-escrow-simulado.md) | Escrow simulado e retenção de 7 dias | Negócio | Augusto |
| [04](adr-04-k-anonimato-no-daas.md) | k-anonimato no DaaS (k ≥ 30) | Dados / LGPD | Augusto |
| [05](adr-05-retencao-e-imutabilidade-dos-logs.pdf) | Retenção e imutabilidade dos logs | Auditoria | Augusto |
| [06](adr-06-criterios-de-arbitragem.pdf) | Critérios de arbitragem | Negócio | Augusto |
| [07](adr-07-eliminacao-de-conta.pdf) | Eliminação de conta | LGPD | Augusto |
| [08](adr-08-banco-principal.md) | Banco principal | Dados | Fabricio |
| [09](adr-09-onde-fica-a-autorizacao.md) | Onde fica a autorização | Segurança | Fabricio |
| [10](adr-10-ledger-de-moedas.md) | Ledger de moedas | Dados | Fabricio |
| [11](adr-11-armazenamento-de-imagens.md) | Armazenamento de imagens | Dados | Fabricio |
| [12](adr-12-limiar-de-confianca-do-scanner.md) | Limiar de confiança do Scanner | Scanner IA | Fabricio |
| [13](adr-13-contrato-e-versionamento-da-api.md) | Contrato e versionamento da API | Back-end | Thiago |
| [14](adr-14-idempotencia.md) | Idempotência | Back-end | Thiago |
| [15](adr-15-concorrencia-dos-lances.md) | Concorrência dos lances | Back-end | Thiago |
| [16](adr-16-tarefas-agendadas.md) | Tarefas agendadas | Back-end | Thiago |
| [17](adr-17-estrategia-de-testes.md) | Estratégia de testes | Qualidade | Thiago |
| [18](adr-18-estado-e-cache-de-dados-no-web.pdf) | Estado e cache de dados no web | Web | Pietro |
| [19](adr-19-design-system-compartilhado.pdf) | Design system compartilhado | Web / Mobile | Pietro |
| [20](adr-20-acessibilidade-e-responsividade.pdf) | Acessibilidade e responsividade | Web | Pietro |
| [21](adr-21-provedor-de-captcha.pdf) | Provedor de captcha | Web | Pietro |
| [22](adr-22-dashboard-e-esg.pdf) | Dashboard e ESG | Web | Pietro |
| [23](adr-23-offline-first.md) | Offline-first | Mobile | Rafael |
| [24](adr-24-armazenamento-seguro-no-dispositivo.md) | Armazenamento seguro no dispositivo | Mobile | Rafael |
| [25](adr-25-notificacoes-push.md) | Notificações push | Mobile | Rafael |
| [26](adr-26-provedor-de-mapas-e-rotas.md) | Provedor de mapas e rotas | Mobile | Rafael |
| [27](adr-27-captura-e-compressao-de-imagem.md) | Captura e compressão de imagem | Mobile | Rafael |

## Por que alguns estão em PDF

Os ADRs 05 a 07 e 18 a 22 estão em PDF porque, nesses, a versão em Markdown exportada do Jira perdeu a seção "Opção escolhida". O PDF é a versão completa.
