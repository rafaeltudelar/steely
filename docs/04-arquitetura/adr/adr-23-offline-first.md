# ADR-23 — Offline-first
**Architecture Decision Record · Projeto Steely · Escola de TI · UniCesumar**

| Campo | Valor | Campo | Valor |
| --- | --- | --- | --- |
| **Status** | ☒ Proposto  ☐ Aceito  ☐ Rejeitado  ☐ Substituído pelo ADR-___ | **Data** | 01/11/2026 |
| **Responsável** | Rafael Tudela Rizental | **Sprint** | 8 |
| **Participantes** | Augusto Palma Guglielmi, Fabrício Notoya Thomas, Pietro Pasqual Silva, Rafael Tudela Rizental, Thiago Lopes Martins | | |
| **Vínculos** | RNF-07, STY029 · ADR-03 · ADR-07 · ADR-08 · ADR-13 · ADR-14 · ADR-16 · ADR-17 · ADR-18 · ADR-24 · ADR-26 | | |

## 1. Contexto *(obrigatória)*

O aplicativo Steely permite que compradores e vendedores agendem encontros presenciais para troca de componentes de hardware de TI. O requisito não funcional RNF-07 exige que o sistema armazene dados localmente e sincronize em segundo plano em até 10 segundos após o restabelecimento da conexão. A user story STY029 (“Como Usuário preciso gerar a rota até o local do encontro e consultá-la mesmo sem conexão para chegar ao ponto combinado no horário previsto”) define que rotas e dados de agendamento devem permanecer acessíveis offline.

O fluxo BPMN P34 especifica o comportamento esperado: “Sem conexão: guardar leitura e sincronizar em 10 s (RNF-07)”. As regras de negócio de STY029 reforçam que a rota deve estar disponível offline (RN02), que alteração ou cancelamento do agendamento ocorrido enquanto o dispositivo estava offline gera alerta de divergência após a sincronização (RN03) e que armazenamento local expirado exige nova sincronização antes da exibição da rota (RN04).

Além da rota, a confirmação de entrega também acontece no ponto de encontro, muitas vezes sem sinal: sem conexão, a leitura do QR Code é armazenada localmente e sincronizada quando o acesso for restabelecido (STY028-RN04). O backend do projeto é Python (FastAPI) com endpoints sob o prefixo /api/v1 (ADR-13), sobre PostgreSQL no Supabase (ADR-08), e as escritas repetidas após reconexão precisam ser idempotentes (Idempotency-Key, ADR-14).

Este ADR define onde armazenar no dispositivo o cache de rotas e dados do encontro e a fila de mutações offline, e como sincronizar essas informações em segundo plano quando a conectividade for restabelecida.

## 2. Direcionadores da decisão *(recomendada)*

•  RNF-07 — armazenamento local obrigatório com sincronização em segundo plano completada em até 10 segundos após reconexão

•  STY029-RN02 — rota até o ponto de encontro deve estar disponível mesmo sem conexão

•  STY029-RN03 — alteração ou cancelamento do agendamento ocorrido enquanto o dispositivo estava offline gera alerta de divergência após a sincronização

•  STY029-RN04 — armazenamento local expirado exige nova sincronização antes da exibição da rota

•  STY028-RN04 — sem conexão, a leitura do QR Code é armazenada localmente e sincronizada quando o acesso for restabelecido

•  Idempotência (ADR-14) — cada mutação enviada após reconexão deve levar um Idempotency-Key para não duplicar confirmações

•  Backend FastAPI + Supabase (ADR-08, ADR-13) — a sincronização conversa apenas com a API REST do FastAPI; o cliente não escreve direto no Supabase

•  Development Build do Expo — módulos nativos são aceitos via expo-dev-client (Development Build), desde que bem mantidos

•  Modelo relacional — dados de agendamento, rotas e pontos de encontro possuem relacionamentos que exigem queries estruturadas

•  Consumo de recursos — sincronização em segundo plano deve minimizar uso de bateria e dados móveis

## 3. Opções consideradas *(obrigatória)*

| Opção A — WatermelonDB | Opção B — expo-sqlite + sync customizado | Opção C — Redux Persist + AsyncStorage |
| --- | --- | --- |
| Descrição<br>Banco offline-first sobre SQLite com adaptador de sincronização pull/push pronto para uso, lazy loading, queries observáveis e resolução de conflitos configurável.<br>Prós<br>•  Adaptador de sincronização pull/push integrado, ligado aos endpoints do FastAPI (ADR-13)<br>•  Fila de mutações offline (PendingMutations) com Idempotency-Key (ADR-14)<br>•  Resolução de conflitos integrada e queries observáveis com lazy loading<br>Contras<br>•  Exige Development Build (expo-dev-client); o app deixa de rodar no Expo Go<br>•  Configuração inicial do sync adapter<br>•  Overhead de ~150 KB + JSI bridge | Descrição<br>Módulo expo-sqlite nativo do Expo SDK, com acesso direto ao SQLite e toda a camada de sincronização escrita pela equipe.<br>Prós<br>•  Pacote oficial do Expo SDK, sem dependências extras<br>•  SQL direto com alta performance<br>•  Controle total sobre as queries<br>Contras<br>•  Sincronização, fila offline, ORM e resolução de conflitos totalmente manuais<br>•  Esforço de implementação alto para o prazo acadêmico | Descrição<br>Persiste automaticamente o estado Redux em AsyncStorage (chave-valor), com integração simples à camada de estado do app.<br>Prós<br>•  Não exige módulos nativos<br>•  Integração simples com o estado da aplicação<br>•  Dependência leve (~30 KB)<br>Contras<br>•  Sem queries relacionais (serialização JSON completa)<br>•  Performance baixa com datasets estruturados grandes<br>•  Sincronização totalmente manual |

Comparativo por critério

| Critério | A · WatermelonDB | B · expo-sqlite + sync custom | C · Redux Persist + AsyncStorage |
| --- | --- | --- | --- |
| Base de armazenamento | SQLite (via JSI) | SQLite (Expo SDK nativo) | AsyncStorage (key-value) |
| Adaptador de sincronização | Integrado (pull/push) | Implementação manual | Implementação manual |
| Resolução de conflitos | Integrada (last-write-wins configurável) | Manual | Manual |
| Compatibilidade Expo | Via expo-dev-client (Development Build) | Nativa (Expo SDK) | Nativa (Expo SDK) |
| Queries relacionais | Sim — queries observáveis e lazy loading | Sim — SQL direto | Não — serialização JSON |
| Performance com datasets grandes | Alta (lazy loading, carregamento sob demanda) | Alta (SQL nativo) | Baixa (deserialização completa) |
| Fila de mutações offline | Tabela própria sincronizada no push | Implementação manual | Implementação manual |
| Esforço de implementação | Médio (configuração inicial do sync adapter) | Alto (sync + ORM + conflitos manuais) | Alto (sync + modelagem manual sem SQL) |

## 4. Decisão *(obrigatória)*

Adotar WatermelonDB (Opção A) como banco de dados offline-first do app para o cache de rotas e dados de agendamento e para a fila de mutações offline.

O sync adapter do WatermelonDB implementa o protocolo pull/push e conversará com endpoints REST de sincronização do FastAPI sob o prefixo /api/v1 (ADR-13), que persistem os dados no PostgreSQL do Supabase (ADR-08). A detecção de reconexão será feita via @react-native-community/netinfo: ao restabelecer conectividade, o listener dispara database.sync(), que executa pull (baixa alterações do servidor) e push (envia modificações locais) dentro da janela de 10 s (RNF-07). A resolução de conflitos integrada cobre o cenário de divergência pós-sync exigido por STY029-RN03.

Para a confirmação de entrega offline (STY028-RN04), o WatermelonDB terá a tabela PendingMutations (confirmações de entrega e demais escritas feitas sem rede). Quando o vendedor lê o QR Code offline, o app valida a assinatura Ed25519 localmente em ≤ 150 ms (ADR-24), gera imediatamente um Idempotency-Key (UUID v4) (ADR-14) e grava a mutação na fila com o jti do QR Code (RB-07). Ao reconectar, cada item é enviado ao FastAPI com o cabeçalho Idempotency-Key, que o servidor retém por 72 h (ADR-14), evitando confirmações duplicadas.

O horário da leitura registrado pelo celular segue na mutação apenas como dado informativo, para auditoria. Quem define entregue_em é o servidor, com o próprio relógio, ao processar a confirmação, e é esse valor que conta oficialmente os 7 dias da custódia (custodia_libera_em = entregue_em + 7 × 24 h, ADR-03, ADR-16). Assim, um relógio errado no aparelho ou uma sincronização atrasada não encurtam nem alongam a garantia.

O tempo máximo previsto para uma mutação ficar offline é de 72 h, igual à retenção do Idempotency-Key no servidor (ADR-14). Se a sincronização acontecer depois disso, o jti do QR Code, de uso único (RB-07), continua impedindo a confirmação duplicada. Na sincronização, o app trata as respostas do ADR-14 assim: 409 IDEMPOTENCY_IN_PROGRESS espera o tempo do Retry-After e reenvia com a mesma chave; Idempotent-Replayed: true conta como sucesso e remove o item da fila; 422 IDEMPOTENCY_KEY_REUSED descarta o item e registra o erro.

O WatermelonDB usa JSI e exige expo-dev-client: o app passa a rodar como Development Build do Expo (builds via EAS), configurado com o config plugin do WatermelonDB para Expo (@morrowdigital/watermelondb-expo-plugin, mantido pela comunidade). Essa base nativa é compartilhada pelas demais decisões mobile (ADR-24 a ADR-27).

O WatermelonDB vale só para o app Android. No web, a persistência offline das queries de rota e encontro fica com o TanStack Query, que as guarda em IndexedDB (ADR-18).

Limpeza local. Quando o usuário pede a exclusão da conta ou tem a sessão revogada porque a conta entrou em EM_CARENCIA (ADR-07), o app executa uma rotina de limpeza: apaga o banco local do WatermelonDB (database.unsafeResetDatabase()), incluindo o cache de rotas e encontros e a fila PendingMutations, remove as chaves do expo-secure-store (tokens e chave pública Ed25519, ADR-24) e volta para a tela de login. Nenhum dado pessoal ou endereço exato (RB-06) fica no aparelho depois disso.

O banco local é o SQLite do WatermelonDB, conforme o ADR-08 v1.5: tokens e chaves ficam no expo-secure-store (ADR-24), e os dados de rota e encontro, que incluem o endereço exato (RB-06), ficam protegidos pela criptografia nativa do Android e por TTL curto.

A Opção B (expo-sqlite) foi descartada porque a implementação manual de sincronização, fila offline, ORM e resolução de conflitos aumentaria significativamente o esforço de desenvolvimento além do escopo acadêmico. A Opção C (Redux Persist + AsyncStorage) foi descartada pela ausência de queries relacionais e degradação de performance com os datasets estruturados de rotas e agendamentos.

## 5. Consequências *(obrigatória)*

Positivas:

•  Dados de rota e agendamento disponíveis offline, permitindo consulta mesmo sem conexão (STY029-RN02)

•  Sincronização automática em segundo plano completada em até 10 s após reconexão (RNF-07)

•  Confirmações de entrega feitas sem rede ficam na fila local e são reenviadas com Idempotency-Key, sem risco de duplicidade (STY028-RN04, ADR-14)

•  Resolução de conflitos integrada, habilitando alertas de divergência quando o agendamento muda durante o período offline (STY029-RN03)

•  Revalidação de registros com armazenamento expirado antes da exibição da rota (STY029-RN04)

•  Queries observáveis que atualizam a UI automaticamente após sync, sem recarregamento manual

Negativas:

•  O app deixa de rodar no Expo Go e passa a usar Development Build (expo-dev-client), com builds via EAS

•  O config plugin do WatermelonDB para Expo é mantido pela comunidade, não pelo Expo; uma atualização do Expo SDK pode exigir esperar a versão compatível do plugin

•  O SQLite local não usa SQLCipher; o endereço exato guardado na rota fica protegido pela criptografia nativa do Android e pelo TTL curto, e é apagado ao concluir ou cancelar o encontro (ADR-08 v1.5, ADR-26)

•  Mutações ainda não sincronizadas são descartadas pela limpeza local na exclusão da conta ou na revogação por EM_CARENCIA (ADR-07); no pedido de exclusão, o app tenta sincronizar a fila antes de limpar quando há conexão

•  Complexidade adicional na configuração do sync adapter com os endpoints de pull/push do FastAPI

•  Dependência adicional de ~150 KB no bundle da aplicação

•  Necessidade de definir políticas de expiração (TTL) e limite de tamanho de cache por tipo de dado

O que muda: o FastAPI ganha endpoints de pull/push sob /api/v1; o banco ganha colunas de controle de sincronização nas tabelas sincronizadas; o diagrama de componentes do app passa a mostrar o WatermelonDB entre a UI e a API.

## 6. Validação *(recomendada)*

| Cenário de teste | Procedimento | Resultado esperado |
| --- | --- | --- |
| Consulta offline | Desativar rede no dispositivo Android e acessar rota armazenada | Rota exibida com todos os dados do encontro |
| Sincronização ≤ 10 s | Alterar agendamento no servidor enquanto dispositivo está offline; reconectar | Dados atualizados no dispositivo em até 10 segundos |
| Alerta de divergência | Alterar ou cancelar o agendamento no servidor durante o período offline; reconectar | Alerta de divergência exibido ao usuário (STY029-RN03) |
| Armazenamento expirado | Deixar o TTL do cache expirar | Rota só é exibida após nova sincronização (STY029-RN04) |
| Confirmação de entrega offline | Ler o QR Code em modo avião e depois reconectar | Mutação enviada ao FastAPI com Idempotency-Key; entrega confirmada uma única vez (STY028-RN04, ADR-14) |
| Reenvio duplicado | Forçar o reenvio da mesma mutação após reconexão | Servidor reconhece o mesmo Idempotency-Key, responde com Idempotent-Replayed: true e o app trata como sucesso, sem duplicar a confirmação |
| Chave ainda em processamento | Reenviar a mutação enquanto o servidor ainda processa a primeira | App recebe 409 IDEMPOTENCY_IN_PROGRESS, espera o Retry-After e reenvia com a mesma chave |
| Horário oficial da entrega | Ler o QR Code offline com o relógio do aparelho adiantado e sincronizar horas depois | O horário do celular fica só na auditoria; entregue_em é o horário do servidor e a custódia libera 7 dias depois dele (ADR-03, ADR-16) |
| Limpeza local | Pedir a exclusão da conta e, em outro teste, ter a sessão revogada por EM_CARENCIA (ADR-07) | Banco do WatermelonDB, cache e chaves do expo-secure-store apagados; o app volta ao login sem dados locais |

## 7. Plano de implementação *(recomendada)*

1.  Instalar WatermelonDB com o config plugin para Expo e configurar o Development Build (expo-dev-client) do app via EAS — Sprint 8

2.  Definir schemas WatermelonDB para Route, Appointment, MeetingPoint e PendingMutations, com campos de controle de sincronização (updated_at, is_deleted) — Sprint 8

3.  Implementar o sync adapter contra os endpoints de pull/push do FastAPI sob /api/v1 (ADR-13), usando o cliente HTTP tipado do app (ADR-18) — Sprint 8

4.  Configurar listener de conectividade via @react-native-community/netinfo para disparar database.sync() ao restabelecer conexão — Sprint 8

5.  Implementar a fila de mutações offline: gerar Idempotency-Key (UUID v4) no momento da ação, gravar com o jti do QR Code e o horário do aparelho (só para auditoria), enviar com o cabeçalho Idempotency-Key ao reconectar e tratar 409 IDEMPOTENCY_IN_PROGRESS, Idempotent-Replayed e 422 IDEMPOTENCY_KEY_REUSED (ADR-14, ADR-24) — Sprint 8

6.  Implementar política de expiração de cache (TTL) por tipo de dado: rotas — 24 h; agendamentos — 1 h; pontos de encontro — 7 dias — Sprint 8

7.  Implementar alerta de divergência após sync (STY029-RN03) e orientação para sincronizar quando não houver dados offline — Sprint 8

8.  Implementar a rotina de limpeza local (WatermelonDB, cache e chaves do expo-secure-store) acionada na exclusão da conta e na revogação da sessão por EM_CARENCIA (ADR-07, ADR-24) — Sprint 8

9.  Executar testes de integração e testes E2E com Maestro (ADR-17) cobrindo os 9 cenários da Seção 6 em dispositivo Android — Sprint 8

## 8. Referências *(recomendada)*

•  WatermelonDB — Documentação oficial

•  WatermelonDB Sync — Protocolo de sincronização

•  Expo Development Builds

•  NetInfo — React Native Community

•  Config plugin do WatermelonDB para Expo

•  Steely — Diagrama de Fluxo BPMN, Fluxo P34 (sincronização offline)

•  Steely — Regras de Negócio STY029 RN01–RN04 e STY028-RN04

•  Steely — Matriz de Rastreabilidade v2 (RNF-07 → STY029)

•  ADRs relacionados do grupo: ADR-03, ADR-07, ADR-08, ADR-13, ADR-14, ADR-16, ADR-17, ADR-18, ADR-24, ADR-26

## Histórico de revisões

| Versão | Data | Autor | Alteração |
| --- | --- | --- | --- |
| 1.0 | 01/11/2026 | Rafael Tudela Rizental | Criação do documento |
| 1.1 | 01/11/2026 | Rafael Tudela Rizental | Alinhamento com as ADRs do grupo: sync com FastAPI (ADR-13) sobre Supabase (ADR-08), fila PendingMutations com Idempotency-Key (ADR-14), Development Build, validação em Android, Sprint 8 e participantes atualizados |
| 1.2 | 01/11/2026 | Rafael Tudela Rizental | Tempo máximo offline de 72 h e tratamento das respostas de idempotência (ADR-14); escopo web com IndexedDB pelo TanStack Query (ADR-18); config plugin do WatermelonDB; SQLite sem SQLCipher, protegido por criptografia nativa do Android e TTL curto (ADR-08 v1.5); testes E2E com Maestro (ADR-17) |
| 1.3 | 01/11/2026 | Rafael Tudela Rizental | Horário do celular apenas informativo e entregue_em definido pelo servidor para os 7 dias (ADR-03, ADR-16); rotina de limpeza local na exclusão da conta e na revogação por EM_CARENCIA (ADR-07) |
