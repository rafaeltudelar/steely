# ADR-25 — Notificações push
**Architecture Decision Record · Projeto Steely · Escola de TI · UniCesumar**

| Campo | Valor | Campo | Valor |
| --- | --- | --- | --- |
| **Status** | ☒ Proposto  ☐ Aceito  ☐ Rejeitado  ☐ Substituído pelo ADR-___ | **Data** | 01/11/2026 |
| **Responsável** | Rafael Tudela Rizental | **Sprint** | 8 |
| **Participantes** | Augusto Palma Guglielmi, Fabrício Notoya Thomas, Pietro Pasqual Silva, Rafael Tudela Rizental, Thiago Lopes Martins | | |
| **Vínculos** | STY025, RB-03, C3 da Matriz CSD, RNF-06 · ADR-06 · ADR-08 · ADR-09 · ADR-13 · ADR-15 · ADR-16 · ADR-18 · ADR-23 | | |

## 1. Contexto *(obrigatória)*

O Steely possui fluxos que dependem de notificações com hora marcada para garantir a experiência do usuário e o cumprimento de regras de negócio:

•  Agendamento de encontro (STY025) — Ao agendar a entrega de uma peça, o comprador e o vendedor precisam ser lembrados do horário e local combinados. O agendamento fica 'pendente de confirmação' até o aceite do vendedor (STY025-RN02) e expira automaticamente se o vendedor não responder dentro do prazo (STY025-RN04), configurado no banco e varrido pelo pg_cron (ADR-16).

•  Avisos de lance em leilão — Enquanto a tela do leilão está aberta, os lances chegam em tempo real (≤ 100 ms, RNF-06) pelo WebSocket do Supabase Realtime (ADR-09, ADR-15, ADR-18). Usuários com o app em segundo plano ou fechado precisam ser avisados por push quando o seu lance é superado ou quando o leilão está prestes a encerrar.

•  Prazo de resposta de 48 h (RB-03) — Na negociação, o vendedor tem até 48 horas para responder; sem resposta, a reserva é cancelada e a oferta volta a Disponível (BPMN P34, ADR-16). O vendedor precisa de lembretes antes do vencimento para evitar a perda automática.

•  Arbitragem de disputas (ADR-06) — Comprador e vendedor precisam ser avisados dos prazos da arbitragem (3, 5 e 10 dias) e da decisão final, mesmo com o app fechado.

•  Escopo delimitado (C3 Matriz CSD) — Estão fora do escopo a conversão de moeda virtual em dinheiro real e transações financeiras externas; as notificações se restringem a eventos internos do app.

O backend do projeto é Python (FastAPI) sobre PostgreSQL no Supabase (ADR-08, ADR-13), e o agendamento de tarefas por prazo é feito com pg_cron no próprio banco (ADR-16). O problema é definir a infraestrutura de push que garanta entrega confiável no Android, se integre a esse mecanismo de agendamento e use a base Expo do app.

## 2. Direcionadores da decisão *(recomendada)*

•  RNF-06 — Tempo real e notificações — Comunicação em tempo real para chat e leilões, e notificações push de eventos críticos para quem não está com o app aberto.

•  STY025-RN02 — Pendente de confirmação — O agendamento é registrado como 'pendente de confirmação' até o aceite do vendedor; o vendedor precisa ser avisado da solicitação.

•  STY025-RN04 — Expiração por falta de resposta — A solicitação de agendamento expira automaticamente se o vendedor não responder dentro do prazo configurado (ADR-16); o sistema deve avisar as partes.

•  RB-03 — Resposta do vendedor em até 48 h — Sem resposta em 48 horas, a reserva é cancelada (BPMN P34); o sistema deve disparar lembretes antes do vencimento.

•  ADR-06 — Prazos e decisão da arbitragem — Avisos dos prazos de 3, 5 e 10 dias e da decisão final para as partes da disputa.

•  C3 da Matriz CSD — Escopo restrito a eventos internos do app; sem integração com sistemas de pagamento externo.

•  Agendamento no banco (ADR-16) — Lembretes e prazos são varridos pelo pg_cron no PostgreSQL do Supabase, e não por um scheduler no servidor de aplicação.

•  Base nativa do app — O app já roda como Development Build (ADR-23); a preferência é por pacotes oficiais do Expo SDK, sem novos plugins nativos.

•  Entrega no Android — Escopo mobile do projeto é Android, com entrega via Firebase Cloud Messaging (FCM).

## 3. Opções consideradas *(obrigatória)*

| Opção A — expo-notifications + FCM | Opção B — OneSignal | Opção C — react-native-push-notification |
| --- | --- | --- |
| Descrição<br>Pacote oficial do Expo SDK para push tokens, recebimento e exibição; o FastAPI dispara para a Expo Push API, que entrega pelo FCM, e os prazos são varridos pelo pg_cron (ADR-16).<br>Prós<br>•  Pacote oficial do Expo, sem novos plugins nativos além do Development Build (ADR-23)<br>•  Expo Push Service gratuito<br>•  Integra com pg_cron + outbox + webhook do FastAPI (ADR-16)<br>•  Setup de baixa complexidade<br>Contras<br>•  Métricas de entrega limitadas<br>•  Dependência da disponibilidade do Expo Push Service | Descrição<br>Plataforma de notificações como serviço, com SDK próprio, dashboard de métricas e segmentação de usuários.<br>Prós<br>•  Dashboard completo de entrega e abertura<br>•  Gratuito até 10 mil assinantes<br>•  Abstrai FCM e APNs<br>Contras<br>•  Adiciona dependência de plataforma externa e SDK nativo de terceiros<br>•  Exige conta OneSignal e config plugin<br>•  Complexidade não justificada no escopo acadêmico | Descrição<br>Biblioteca da comunidade com configuração direta do FCM, sem intermediários.<br>Prós<br>•  Controle total do payload<br>•  Uso direto do FCM, sem custo<br>Contras<br>•  Configuração nativa manual e módulo nativo da comunidade no build<br>•  Sem dashboard de métricas<br>•  Alta complexidade de configuração e manutenção |

Comparativo por critério

| Critério | A — expo-notifications + FCM | B — OneSignal | C — react-native-push-notification |
| --- | --- | --- | --- |
| Manutenção do pacote | Oficial do Expo SDK | SDK de terceiros + config plugin | Biblioteca da comunidade |
| Novos módulos nativos no build | Não | Sim | Sim (configuração nativa manual) |
| Entrega Android | FCM via Expo Push Service | Abstrai o FCM | FCM configurado manualmente |
| Disparo pelo backend | FastAPI → Expo Push API | FastAPI → OneSignal REST API | FastAPI → FCM HTTP v1 |
| Agendamento dos prazos | pg_cron (ADR-16) | pg_cron (ADR-16) ou segmentos do OneSignal | pg_cron (ADR-16) |
| Custo | Gratuito (Expo Push Service) | Gratuito até 10 k assinantes | Gratuito (FCM direto) |
| Dashboard de métricas | Limitado (recibos do Expo) | Completo (dashboard OneSignal) | Nenhum nativo |
| Complexidade de setup | Baixa (EAS + push token) | Média (conta OneSignal + config plugin) | Alta (configuração nativa manual) |

## 4. Decisão *(obrigatória)*

Adotar expo-notifications + FCM via Expo Push Service (Opção A) para as notificações push do Steely, com o agendamento dos prazos feito pelo pg_cron do Supabase conforme o ADR-16.

O expo-notifications é um pacote oficial do Expo SDK e não exige adicionar novos plugins nativos além do Development Build já configurado (ADR-23). O Expo Push Service é gratuito e repassa as mensagens ao FCM, sem que o backend precise lidar diretamente com as credenciais do FCM.

O fluxo de disparo segue o mecanismo oficial do ADR-16:

1.  pg_cron agenda e varre os prazos no PostgreSQL do Supabase: lembrete 24 h antes do encontro, lembrete 1 h antes, alerta quando restam 6 h para vencer as 48 h de resposta do vendedor (RB-03), aviso de expiração do agendamento sem resposta (STY025-RN04) e avisos dos prazos de 3, 5 e 10 dias da arbitragem (ADR-06). O aviso da decisão da arbitragem é gravado na outbox no momento em que a decisão é registrada.

2.  pg_cron grava o evento na tabela outbox e aciona via pg_net o webhook interno do FastAPI POST /api/v1/internal/jobs/notifications, autenticado com X-Internal-Token, que responde 202 Accepted e processa em BackgroundTasks (ADR-09, ADR-13, ADR-16).

3.  O FastAPI dispara o POST para a Expo Push API (https://exp.host/--/api/v2/push/send) com o push token do usuário.

4.  O FastAPI marca o status do evento na outbox — em envio antes do POST e enviado ao concluir. Como o pg_cron reenvia a cada minuto os eventos sem confirmação (ADR-16), um evento já marcado não é disparado de novo, o que evita push duplicado.

Nos leilões, os lances em tempo real (≤ 100 ms, RNF-06) chegam pelo WebSocket do Supabase Realtime enquanto a tela está aberta (ADR-09, ADR-15, ADR-18). O push entra apenas para quem está com o app em segundo plano ou fechado: lance superado e leilão prestes a encerrar. O aviso de leilão prestes a encerrar usa o ends_at vigente, já com as prorrogações do anti-sniping (ADR-15); quando o leilão é prorrogado, o aviso é reagendado.

A Opção B (OneSignal) foi descartada por adicionar dependência de plataforma externa e um SDK nativo de terceiros sem benefício proporcional para o escopo acadêmico; o dashboard de métricas é desejável, mas não justifica a complexidade adicional. A Opção C (react-native-push-notification) foi descartada por exigir configuração nativa manual e adicionar um módulo nativo da comunidade ao build.

## 5. Consequências *(obrigatória)*

Positivas

•  Zero custo de infraestrutura — O Expo Push Service é gratuito, adequado ao contexto acadêmico.

•  Pacote oficial do Expo — Não adiciona novos plugins nativos ao Development Build (ADR-23).

•  Agendamento confiável — Os prazos ficam no pg_cron do banco (ADR-16) e o envio passa pela outbox, então lembretes chegam mesmo com o app fechado.

•  Divisão clara de canais — Supabase Realtime para quem está com o leilão aberto (≤ 100 ms) e push apenas para quem está fora do app.

•  Integração simples com o FastAPI — Um POST HTTP para a Expo Push API, sem SDK server-side obrigatório.

Negativas

•  Dependência do Expo Push Service — Se o serviço ficar indisponível, os pushes não são entregues. Mitigação: o FastAPI reenvia com backoff exponencial e mantém o status do evento na outbox.

•  Métricas limitadas — Sem dashboard nativo de taxa de entrega ou abertura. Mitigação: consultar os recibos de entrega do Expo e registrar o resultado no backend.

•  Permissão do usuário — No Android 13 ou superior, o usuário pode negar a permissão de notificações. Mitigação: exibir tela explicativa antes de solicitar a permissão.

•  Token pode mudar — O push token pode mudar após reinstalação ou atualização do app. O app deve enviar o token atualizado ao backend em cada inicialização.

## 6. Validação *(recomendada)*

| Cenário de teste | Critério de aceitação |
| --- | --- |
| Registro de push token | Ao abrir o app pela primeira vez no Android, o token é obtido via getExpoPushTokenAsync e enviado ao FastAPI com sucesso |
| Lembrete 24 h antes do encontro | O pg_cron grava o evento na outbox, o FastAPI dispara o push e o usuário recebe a notificação com os dados do agendamento |
| Lembrete 1 h antes do encontro | Segundo lembrete entregue no Android com o app em segundo plano ou fechado |
| Alerta de prazo de resposta | Com reserva sem resposta, o vendedor recebe alerta quando restam 6 h das 48 h (RB-03); agendamento não confirmado no prazo expira e as partes são avisadas (STY025-RN04) |
| Lance em tempo real | Com a tela do leilão aberta, o novo lance aparece via Supabase Realtime em ≤ 100 ms (RNF-06), sem push |
| Lance superado com app fechado | Usuário com o app em segundo plano recebe push informando que o seu lance foi superado |
| Permissão negada (Android 13+) | Se o usuário nega a permissão, o app exibe aviso in-app para eventos críticos e não gera erro de runtime |
| Retry após falha | Se a Expo Push API retorna erro, o FastAPI reenvia com backoff exponencial (3 tentativas) e registra o status final na outbox |
| Evento repetido pelo pg_cron | Evento já marcado como enviado na outbox não gera um segundo push |
| Leilão prorrogado | Após prorrogação pelo anti-sniping, o aviso de encerramento é reagendado para o novo ends_at (ADR-15) |
| Prazos da arbitragem | Com uma disputa aberta, as partes recebem push nos marcos de 3, 5 e 10 dias (ADR-06) |
| Decisão da arbitragem | Ao registrar a decisão, comprador e vendedor recebem push com o resultado (ADR-06) |

## 7. Plano de implementação *(recomendada)*

1.  Instalar dependências — npx expo install expo-notifications expo-device expo-constants. Configurar android.googleServicesFile no app.json para o FCM. Sprint 8.

2.  Solicitar permissão — Implementar tela explicativa e chamar requestPermissionsAsync() após o aceite do usuário; tratar a negação no Android 13+. Sprint 8.

3.  Registrar push token — Chamar getExpoPushTokenAsync({ projectId }) no bootstrap do app e enviar o token ao FastAPI pelo cliente HTTP tipado (ADR-13, ADR-18); reenviar a cada inicialização. Sprint 8.

4.  Implementar handler de notificações — Configurar setNotificationHandler para exibição em foreground e addNotificationResponseReceivedListener para deep linking ao agendamento ou leilão. Sprint 8.

5.  Configurar os jobs no pg_cron — Criar os jobs de lembrete 24 h, lembrete 1 h, alerta de 6 h restantes das 48 h de resposta (RB-03), expiração do agendamento sem resposta (STY025-RN04) e prazos de 3, 5 e 10 dias da arbitragem (ADR-06), gravando os eventos na outbox e acionando via pg_net o POST /api/v1/internal/jobs/notifications com X-Internal-Token (ADR-16). O aviso da decisão da arbitragem entra na outbox quando a decisão é registrada (ADR-06). Sprint 8.

6.  Implementar o webhook no FastAPI — Responder 202 Accepted, processar em BackgroundTasks, marcar o status do evento na outbox e enviar o push para a Expo Push API (ADR-09, ADR-13, ADR-16). Sprint 8.

7.  Avisos de leilão — Disparar push de lance superado e de leilão prestes a encerrar apenas para usuários fora da tela do leilão, usando o ends_at vigente e reagendando após prorrogação; manter os lances em tempo real no Supabase Realtime (ADR-15). Sprint 8.

8.  Retry e testes — Reenvio com backoff exponencial (1 s, 4 s, 16 s) e status na outbox; testes unitários com mock do expo-notifications, teste de integração do webhook e teste E2E com Maestro em dispositivo Android (ADR-17). Sprint 8.

## 8. Referências *(recomendada)*

•  Expo Notifications — Documentação oficial: https://docs.expo.dev/versions/latest/sdk/notifications/

•  Expo Push Notifications — Guia completo: https://docs.expo.dev/push-notifications/overview/

•  Firebase Cloud Messaging (FCM) — https://firebase.google.com/docs/cloud-messaging

•  Supabase pg_cron — https://supabase.com/docs/guides/database/extensions/pg_cron

•  Supabase pg_net — https://supabase.com/docs/guides/database/extensions/pg_net

•  Supabase Realtime — https://supabase.com/docs/guides/realtime

•  FastAPI Background Tasks — https://fastapi.tiangolo.com/tutorial/background-tasks/

•  Matriz de Rastreabilidade v2 — RF-10 → STY025, STY026, STY029 → RNF-07; RF-15 (Leilões) → STY036, STY037 → RNF-06, RNF-09

•  Regras de Negócio — STY025-RN01 a RN05

•  Diagrama de Fluxo BPMN — P34: vendedor responde em até 48 horas (RB-03)

•  Matriz CSD — C3: fora do escopo a conversão de moeda virtual em dinheiro real e transações financeiras externas

•  ADRs relacionados do grupo: ADR-06, ADR-08, ADR-09, ADR-13, ADR-15, ADR-16, ADR-17, ADR-18, ADR-23

## Histórico de revisões

| Versão | Data | Autor | Alteração |
| --- | --- | --- | --- |
| 1.0 | 01/11/2026 | Rafael Tudela Rizental | Criação do documento. Decisão por expo-notifications + FCM via Expo Push Service para lembretes de agendamento, avisos de lance e prazo de resposta de 48 h. |
| 1.1 | 01/11/2026 | Rafael Tudela Rizental | Alinhamento com as ADRs do grupo: agendamento por pg_cron + outbox + pg_net e webhook do FastAPI (ADR-16), lances em tempo real via Supabase Realtime (ADR-15), Development Build, validação em Android, Sprint 8 e participantes atualizados. |
| 1.2 | 01/11/2026 | Rafael Tudela Rizental | Prazo de 48 h atribuído à RB-03 (BPMN P34) e prazo do agendamento configurável (STY025-RN04, ADR-16); status na outbox contra push duplicado; aviso de encerramento pelo ends_at vigente (ADR-15); teste E2E com Maestro (ADR-17); vínculos ADR-09, ADR-23 e RB-03. |
| 1.3 | 01/11/2026 | Rafael Tudela Rizental | Avisos dos prazos de 3, 5 e 10 dias e da decisão da arbitragem (ADR-06) incluídos nos eventos de push. |
