# Protótipos

[← Design](../README.md)

Telas de alta fidelidade do app mobile, feitas no Figma ([arquivo STEELY](https://www.figma.com/design/MZxnX0uT8BGIxpxkMFwUCj/STEELY)).

## Autenticação (versão de 13/09/2026)

| Tela | Caso de uso | |
|---|---|---|
| Logo | — | <img src="00-logo.png" width="220"> |
| Login | STY002, STY003 | <img src="01-login.png" width="220"> |
| Criar conta | STY001, STY004 | <img src="02-criar-conta.png" width="220"> |
| Verificar e-mail | STY001 | <img src="03-verificar-email.png" width="220"> |
| Recuperar senha | STY005 | <img src="04-recuperar-senha.png" width="220"> |
| Entrar com código | STY006 | <img src="05-entrar-com-codigo.png" width="220"> |

## Sprint 13 — Home, notificações e criação de anúncio

Geradas em HTML por [`ferramentas/prototipos/gerar_telas.py`](../../../ferramentas/prototipos/), aprovadas pelas verificações automáticas (paleta, tipografia e layout) e importadas no Figma com o plugin html.to.design. Cada pasta tem um arquivo por tela:

- [`html/`](html/) — o arquivo que vai para o Figma (1920×1200, celular 375×812 na posição 773,194)
- [`png/`](png/) — a captura do celular, gerada pelo `conferir_telas.py`

| Nº | Tela | Jira | Casos de uso | |
|---|---|---|---|---|
| 001 | [Home / Feed](html/001-home-feed.html) | EDTS-252 | STY020, STY017 | <img src="png/001-home-feed.png" width="180"> |
| 002 | [Central de Notificações](html/002-central-de-notificacoes.html) | EDTS-253 | STY021, STY025 | <img src="png/002-central-de-notificacoes.png" width="180"> |
| 003 | [Criar Anúncio — Fotos](html/003-criar-anuncio-etapa-1-fotos.html) | EDTS-254 | STY016, STY017 | <img src="png/003-criar-anuncio-etapa-1-fotos.png" width="180"> |
| 004 | [Criar Anúncio — Detalhes](html/004-criar-anuncio-etapa-2-detalhes.html) | EDTS-255 | STY016, STY055, STY052 | <img src="png/004-criar-anuncio-etapa-2-detalhes.png" width="180"> |
| 005 | [Criar Anúncio — Preço e entrega](html/005-criar-anuncio-etapa-3-preco-e-entrega.html) | EDTS-256 | STY016 | <img src="png/005-criar-anuncio-etapa-3-preco-e-entrega.png" width="180"> |
| 006 | [Criar Anúncio — Revisão](html/006-criar-anuncio-etapa-4-revisao.html) | EDTS-257 | STY016 | <img src="png/006-criar-anuncio-etapa-4-revisao.png" width="180"> |

## Sprint 13 — ESG e perfil

| Nº | Tela | Jira | Casos de uso | |
|---|---|---|---|---|
| 049 | [Mapa de Ecopontos](html/049-mapa-de-ecopontos.html) | EDTS-300 | STY058, STY029 | <img src="png/049-mapa-de-ecopontos.png" width="180"> |
| 050 | [Dashboard ESG Pessoal](html/050-dashboard-esg-pessoal.html) | EDTS-301 | STY054 | <img src="png/050-dashboard-esg-pessoal.png" width="180"> |
| 051 | [Doar para ONG](html/051-doar-para-ong.html) | EDTS-302 | STY041, STY058 | <img src="png/051-doar-para-ong.png" width="180"> |
| 052 | [Meu Perfil](html/052-meu-perfil.html) | EDTS-303 | STY011 | <img src="png/052-meu-perfil.png" width="180"> |
| 053 | [Editar Perfil](html/053-editar-perfil.html) | EDTS-304 | STY011 | <img src="png/053-editar-perfil.png" width="180"> |
| 054 | [Configurações de Segurança](html/054-configuracoes-de-seguranca.html) | EDTS-305 | STY007, STY008, STY009 | <img src="png/054-configuracoes-de-seguranca.png" width="180"> |

## Sprint 13 — Pedidos, garantia, disputas, carteira e leilão

| Nº | Tela | Jira | Casos de uso | |
|---|---|---|---|---|
| 031 | [Detalhes do Pedido](html/031-detalhes-do-pedido.html) | EDTS-282 | STY028, STY031, STY032 | <img src="png/031-detalhes-do-pedido.png" width="180"> |
| 032 | [Solicitar Garantia](html/032-solicitar-garantia.html) | EDTS-283 | STY031, STY033 | <img src="png/032-solicitar-garantia.png" width="180"> |
| 033 | [Acompanhar Garantia](html/033-acompanhar-garantia.html) | EDTS-284 | STY031, STY033 | <img src="png/033-acompanhar-garantia.png" width="180"> |
| 034 | [Abrir Disputa](html/034-abrir-disputa.html) | EDTS-285 | STY033, STY034 | <img src="png/034-abrir-disputa.png" width="180"> |
| 035 | [Detalhes da Disputa](html/035-detalhes-da-disputa.html) | EDTS-286 | STY033, STY034, STY035 | <img src="png/035-detalhes-da-disputa.png" width="180"> |
| 036 | [Cancelar Pedido](html/036-cancelar-pedido.html) | EDTS-287 | STY026 | <img src="png/036-cancelar-pedido.png" width="180"> |
| 037 | [Avaliar Transação](html/037-avaliar-transacao.html) | EDTS-288 | STY012 | <img src="png/037-avaliar-transacao.png" width="180"> |
| 038 | [Carteira Digital](html/038-carteira-digital.html) | EDTS-289 | STY042, STY043, STY044 | <img src="png/038-carteira-digital.png" width="180"> |
| 039 | [Depositar na Carteira](html/039-depositar-na-carteira.html) | EDTS-290 | STY045 | <img src="png/039-depositar-na-carteira.png" width="180"> |
| 040 | [Sacar da Carteira](html/040-sacar-da-carteira.html) | EDTS-291 | STY028, STY045 | <img src="png/040-sacar-da-carteira.png" width="180"> |
| 041 | [Verificação Captcha](html/041-verificacao-captcha.html) | EDTS-292 | STY046, STY004 | <img src="png/041-verificacao-captcha.png" width="180"> |
| 042 | [Criar Leilão](html/042-criar-leilao.html) | EDTS-293 | STY036 | <img src="png/042-criar-leilao.png" width="180"> |

## Histórico — versões anteriores

Primeiras versões das telas de autenticação, anexadas nas tarefas de prototipagem do Jira. Ficam aqui para mostrar a evolução do design; a versão atual é a da seção [Autenticação](#autenticação-versão-de-13092026).

| Sprint | Tela | Jira | |
|---|---|---|---|
| 8 (30/08/2026) | Login — primeira versão | EDTS-103 | <img src="historico/sprint08-login-v1.png" width="180"> |
| 9 (06/09/2026) | Login — segunda versão | EDTS-124 | <img src="historico/sprint09-login-v2.png" width="180"> |
| 9 (06/09/2026) | Criar conta — primeira versão | EDTS-124 | <img src="historico/sprint09-criar-conta-v1.png" width="180"> |

As telas de autenticação da Sprint 10 (EDTS-173) são as da seção Autenticação acima. As tarefas EDTS-191 (Sprint 11) e EDTS-203 (Sprint 12) não têm imagens anexadas no Jira.

As demais telas (chat, propostas, agendamento, garantia e disputas — tarefas `PROTOTIPAGEM` no Jira) seguem o mesmo processo: veja o [Guia de protótipos](../GUIA-DE-PROTOTIPOS.md).
