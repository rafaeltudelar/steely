# Casos de uso

[← Requisitos](../README.md)

| Arquivo | O que é |
|---|---|
| [especificacao-dos-casos-de-uso.xlsx](especificacao-dos-casos-de-uso.xlsx) | Índice geral, user stories e **uma aba por caso de uso** (`STYG` e `STY001`–`STY058`), com atores, pré-condições, fluxo principal e fluxos alternativos |
| [diagramas-de-casos-de-uso.docx](diagramas-de-casos-de-uso.docx) | 7 diagramas UML, um por pacote: Conta, Ofertas, Negociação, Pós-venda, Economia, Comunidade e Governança |

`STYG — Manter Geral` é o fluxo padrão de cadastro e edição, reaproveitado por casos como "Editar perfil" e "Editar oferta".

## Índice

| STY | Caso de uso | Ator principal |
|---|---|---|
| 001 | Realizar cadastro | Visitante |
| 002 | Realizar login | Visitante |
| 003 | Login por serviços (OAuth / redes sociais) | Visitante |
| 004 | Autenticação por captcha | Visitante / Usuário |
| 005 | Recuperação de conta | Visitante |
| 006 | Requisitar código de login | Visitante |
| 007 | Setup de 2FA | Usuário autenticado |
| 008 | Alterar senha | Usuário autenticado |
| 009 | Deslogar | Usuário autenticado |
| 010 | Requisitar deleção de conta | Usuário autenticado |
| 011 | Ver perfil | Usuário |
| 012 | Avaliar usuário | Comprador / Vendedor |
| 013 | Montador de setup | Usuário |
| 014 | Cálculo de setup | Usuário |
| 015 | Tendências de setup | Usuário |
| 016 | Publicar oferta | Vendedor |
| 017 | Scanner IA | Vendedor |
| 018 | Impulsionar oferta (pago / ONG) | Vendedor / ONG |
| 019 | Alterar status do anúncio (pausar / reabrir) | Vendedor |
| 020 | Buscar e filtrar ofertas | Usuário |
| 021 | Enviar mensagem | Usuário |
| 022 | Configurar mensagem automática | Vendedor |
| 023 | Deletar mensagem | Usuário |
| 024 | Encerrar chat | Usuário |
| 025 | Agendar horário | Comprador |
| 026 | Cancelar agendamento | Comprador / Vendedor |
| 027 | Gerar QR Code | Comprador / Vendedor |
| 028 | Escanear QR Code | Comprador / Vendedor |
| 029 | Gerar e consultar rota | Usuário |
| 030 | Laudo técnico | Comprador / Técnico parceiro |
| 031 | Solicitar devolução | Comprador |
| 032 | Gerar comprovante em PDF | Usuário |
| 033 | Abrir reclamação | Usuário |
| 034 | Escalar reclamação | Usuário |
| 035 | Encerrar reclamação | Moderador |
| 036 | Criar leilão | Back-office |
| 037 | Participar de leilão | Comprador |
| 038 | Proposta por lote | Comprador |
| 039 | Requisitar cadastro de ONG | Representante de ONG |
| 040 | Verificar ONG | Back-office |
| 041 | Publicar pedido de doação | ONG verificada |
| 042 | Verificar moedas (cashback) | Usuário autenticado |
| 043 | Resgatar moedas | Usuário autenticado |
| 044 | Gastar moedas | Usuário autenticado |
| 045 | Manter método de pagamento | Usuário autenticado |
| 046 | Hardware Captcha | Usuário |
| 047 | Recolher dados para treino da IA | Back-office |
| 048 | Atualizar a IA | Back-office |
| 049 | Realizar denúncia | Usuário |
| 050 | Analisar e finalizar denúncia | Moderador |
| 051 | Remover post | Moderador / Back-office |
| 052 | Censurar dados pessoais em descrições | Moderador |
| 053 | Gerar relatório DaaS | Back-office |
| 054 | Gerar métricas ESG | Usuário / Back-office |
| 055 | Descrição de item (falhas e defeitos crônicos) | Usuário |
| 056 | Checar logs | Back-office |
| 057 | Consultar guia informativo | Usuário |
| 058 | Sugerir ecoponto oficial (reciclagem) | Vendedor |

Os fluxos de cada caso de uso estão desenhados nos [diagramas de sequência](../../03-modelagem/).
