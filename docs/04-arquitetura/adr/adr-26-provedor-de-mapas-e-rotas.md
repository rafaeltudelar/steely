# ADR-26 — Provedor de mapas e rotas
**Architecture Decision Record · Projeto Steely · Escola de TI · UniCesumar**

| Campo | Valor | Campo | Valor |
| --- | --- | --- | --- |
| **Status** | ☒ Proposto  ☐ Aceito  ☐ Rejeitado  ☐ Substituído pelo ADR-___ | **Data** | 01/11/2026 |
| **Responsável** | Rafael Tudela Rizental | **Sprint** | 8 |
| **Participantes** | Augusto Palma Guglielmi, Fabrício Notoya Thomas, Pietro Pasqual Silva, Rafael Tudela Rizental, Thiago Lopes Martins | | |
| **Vínculos** | STY029, RNF-07 · ADR-08 · ADR-09 · ADR-13 · ADR-17 · ADR-18 · ADR-23 | | |

## 1. Contexto *(obrigatória)*

A story STY029 (Gerar e consultar rota) permite que comprador e vendedor visualizem a rota até o ponto de encontro combinado para a entrega de peças de hardware. O fluxo inclui:

•  Geração de rota — A geração de rota requer agendamento confirmado com local definido (STY029-RN01); o app exibe o mapa com a rota do usuário até o local de encontro.

•  Cache offline da rota — A rota gerada deve ser armazenada localmente para consulta sem conexão e sincronizada quando a conexão retornar em até 10 segundos (RNF-07, BPMN P34, ADR-23).

•  Alerta de divergência — Alteração ou cancelamento do agendamento ocorrido enquanto o dispositivo estava offline gera alerta de divergência após a sincronização (STY029-RN03).

•  Expiração do armazenamento local — Armazenamento local expirado exige nova sincronização antes da exibição da rota (STY029-RN04).

•  Sigilo do endereço — Pela regra RB-06 e pelo ADR-09, o endereço exato do ponto de encontro só é liberado pelo backend depois que a oferta está 'Reservada' e com agendamento ativo.

O problema é escolher o provedor de mapas e rotas que ofereça mapa interativo, cálculo de rotas, plano gratuito suficiente para o escopo acadêmico, compatibilidade com React Native + Expo e um fallback quando o serviço estiver indisponível, sem expor no aplicativo a chave de cobrança do serviço de rotas nem o endereço antes da hora.

## 2. Direcionadores da decisão *(recomendada)*

•  RNF-07 — Disponibilidade offline — O sistema deve guardar dados críticos (incluindo rotas) e sincronizar em até 10 segundos após reconexão.

•  STY029-RN01 — Geração de rota — A rota é gerada somente com agendamento confirmado e local definido.

•  STY029-RN02 — Cache de rota — Rota deve ser armazenada offline e exibida mesmo sem conexão.

•  STY029-RN03 — Alerta de divergência — Mudança no agendamento durante o período offline gera alerta após a sincronização.

•  STY029-RN04 — Armazenamento expirado — Rota com armazenamento local expirado só é exibida após nova sincronização.

•  RB-06 / ADR-09 — Sigilo do endereço — O endereço exato só sai do backend após a reserva com agendamento ativo.

•  Proteção da chave de cobrança — A chave da API de rotas não pode ficar no aplicativo.

•  Custo no plano gratuito — O projeto é acadêmico; o provedor deve oferecer cota gratuita suficiente para desenvolvimento e testes (estimativa: ~500 cálculos de rota/mês e ~5.000 carregamentos de mapa).

•  Base nativa do app — O app já roda como Development Build (ADR-23); a preferência é por pacotes oficiais do Expo SDK, sem novos plugins nativos.

## 3. Opções consideradas *(obrigatória)*

| Opção A — Google Maps Platform | Opção B — Mapbox | Opção C — OpenStreetMap + Leaflet |
| --- | --- | --- |
| Descrição<br>react-native-maps (incluído no Expo SDK) para o mapa e Google Routes API (Compute Routes) chamada pelo FastAPI para a rota, com cache offline no WatermelonDB (ADR-23).<br>Prós<br>•  react-native-maps incluído no Expo SDK, sem novos plugins nativos<br>•  Melhor base cartográfica do Brasil, com trânsito em tempo real<br>•  Chave da Routes API fica só no servidor (FastAPI)<br>•  10 mil cálculos de rota grátis por mês e Maps SDK for Android sem limite<br>Contras<br>•  Download programático de tiles offline não permitido<br>•  Termos restringem o armazenamento de respostas de rota<br>•  Custo pode crescer se o projeto escalar | Descrição<br>SDK nativo Mapbox GL para React Native, com Directions API e mapas offline por região.<br>Prós<br>•  100 mil requisições/mês de Directions no plano gratuito<br>•  Mapas offline nativos<br>Contras<br>•  Adiciona SDK nativo de terceiros ao build<br>•  Exige conta e token próprios (config plugin) | Descrição<br>Tiles OSM com Leaflet renderizado em WebView e rotas via OSRM (self-hosted) ou GraphHopper.<br>Prós<br>•  Sem custo de API<br>•  Dados abertos<br>Contras<br>•  Renderização via WebView, menos fluida que o nativo<br>•  Qualidade de dados variável em áreas menos mapeadas<br>•  Setup alto (servidor OSRM ou API externa) |

Comparativo por critério

| Critério | A — Google Maps Platform | B — Mapbox | C — OpenStreetMap + Leaflet |
| --- | --- | --- | --- |
| Renderização de mapa | Google Maps (react-native-maps) | Mapbox GL Native | Leaflet (WebView) |
| Cálculo de rotas | Google Routes API — Compute Routes (chamada pelo FastAPI) | Mapbox Directions API | OSRM / GraphHopper |
| Plano gratuito | 10 k cálculos de rota/mês (Compute Routes Essentials); Maps SDK for Android sem limite | 100 k requisições/mês (Directions) | Gratuito (self-hosted ou APIs públicas) |
| Qualidade dos dados (Brasil) | Excelente (trânsito em tempo real) | Boa (dados OSM + Mapbox) | Variável (depende de contribuições OSM) |
| Suporte offline de mapa | Limitado (tiles em cache automático) | Mapas offline nativos | Tiles offline manuais |
| Manutenção do pacote no app | react-native-maps (incluído no Expo SDK) | SDK de terceiros | WebView (sem componente nativo de mapa) |
| Novos módulos nativos no build | Não | Sim | Não |
| Complexidade de setup | Baixa (chave do Maps SDK + react-native-maps) | Média (token + config plugin) | Alta (servidor OSRM ou API externa) |

## 4. Decisão *(obrigatória)*

Adotar Google Maps Platform (Opção A): react-native-maps para renderizar o mapa no app e Google Routes API (Compute Routes) chamada pelo FastAPI para calcular a rota, com cache offline no WatermelonDB (ADR-23) como fallback.

O cálculo da rota é feito no backend: quando a oferta está 'Reservada' e o agendamento ativo, o FastAPI (ADR-13) chama a Routes API (computeRoutes) e devolve a polyline junto com os dados do agendamento sincronizados para o app. A Routes API substitui a Directions API, que desde 01/03/2025 é legada e não pode ser ativada em projetos novos do Google Cloud. Assim, a chave de cobrança do Google Cloud fica apenas no servidor (a API REST de rotas não aceita restrição por SHA-1 de Android, como o SDK visual de mapas) e o endereço exato só chega ao dispositivo quando a RB-06 permite (ADR-09). No app fica apenas a chave do Maps SDK for Android, restrita ao pacote e ao SHA-1 do app.

A escolha se justifica por:

•  Pacote incluído no Expo SDK — react-native-maps não exige adicionar novos plugins nativos além do Development Build já configurado (ADR-23).

•  Qualidade de dados no Brasil — Google Maps possui a base cartográfica mais completa e atualizada para cidades brasileiras, incluindo trânsito em tempo real.

•  Custo zero para o projeto — Desde 01/03/2025, o Google dá 10.000 cálculos de rota grátis por mês (Compute Routes Essentials), e o Maps SDK for Android não tem limite de uso. Isso cobre com folga o volume acadêmico esperado (~500 cálculos de rota + ~5.000 carregamentos de mapa por mês).

•  Fallback offline — A polyline recebida do FastAPI é salva no WatermelonDB (CachedRoute). Sem conexão, o app exibe a rota em cache sobre os tiles já vistos do Google Maps; ao reconectar, a sincronização ocorre em até 10 s (RNF-07).

A Opção B (Mapbox) foi descartada por acrescentar um SDK nativo de terceiros ao build e exigir conta e token próprios; seus mapas offline nativos não compensam, já que a rota fica no WatermelonDB. A Opção C (OSM + Leaflet) foi descartada pela renderização via WebView (experiência inferior) e qualidade de dados inconsistente em áreas urbanas do interior do Paraná.

## 5. Consequências *(obrigatória)*

Positivas

•  Experiência nativa de mapa — react-native-maps renderiza Google Maps nativamente no Android, com gestos de zoom, pan e rotação fluidos.

•  Chave protegida e endereço em sigilo — A Routes API só é chamada pelo FastAPI; a chave de cobrança não fica no app e o endereço respeita a RB-06 (ADR-09).

•  Cobertura completa no Brasil — Endereços, POIs e logradouros bem mapeados na região de Maringá/PR (sede da UniCesumar).

•  Fallback offline funcional — Rota em cache no WatermelonDB garante navegação mesmo sem conexão, atendendo RNF-07.

Negativas

•  Dependência de serviço externo — Se a Routes API ficar indisponível e não houver rota em cache, o usuário verá apenas o mapa com o marcador do ponto de encontro. Mitigação: exibir o endereço em texto como fallback final.

•  Limitação de tiles offline — Google Maps não permite download programático de tiles para uso offline; o cache do SDK cobre apenas tiles já visualizados. Mitigação: a polyline sobre o mapa em cache é suficiente para navegação básica.

•  Custo em escala — Se o projeto escalar além do contexto acadêmico, a cota gratuita mensal pode não ser suficiente. Mitigação: monitorar uso no Google Cloud Console e limitar as chamadas no FastAPI.

•  Termos de uso — O Google restringe o armazenamento persistente de respostas da Routes API. Mitigação: rotas no WatermelonDB têm prazo de expiração e são removidas ao concluir ou cancelar o encontro; rota expirada exige nova sincronização (STY029-RN04).

O que muda: o FastAPI ganha a integração com a Routes API e passa a incluir a polyline nos dados do agendamento; o app só renderiza o mapa e lê a rota do WatermelonDB.

## 6. Validação *(recomendada)*

| Cenário de teste | Critério de aceitação |
| --- | --- |
| Geração de rota | Com agendamento confirmado e local definido, o app recebe a polyline do FastAPI e exibe a rota em ≤ 3 segundos no Android (STY029-RN01) |
| Sigilo do endereço | Antes da reserva com agendamento ativo, a API não devolve o endereço exato nem a rota (RB-06, ADR-09) |
| Chave protegida | Inspeção do APK não encontra a chave da Routes API; só a chave restrita do Maps SDK for Android |
| Cache offline da rota | Com o dispositivo em modo avião, a rota previamente sincronizada é exibida a partir do WatermelonDB sem erro (RNF-07) |
| Sincronização após reconexão | Ao restaurar a conexão, a rota é atualizada no mapa em ≤ 10 segundos (RNF-07, BPMN P34) |
| Armazenamento expirado | Com a rota em cache expirada, o app não exibe a rota antiga e solicita nova sincronização antes da exibição (STY029-RN04) |
| Alerta de divergência | Agendamento alterado no servidor enquanto o dispositivo estava offline gera alerta de divergência após a sincronização (STY029-RN03) |
| Fallback sem API | Com a Routes API indisponível e sem cache, o app exibe o endereço do ponto de encontro em texto e o marcador no mapa |
| Consumo de cota | Em um mês de desenvolvimento com a equipe de 5 integrantes, o consumo permanece dentro da cota gratuita (10 k cálculos de rota/mês) |

## 7. Plano de implementação *(recomendada)*

1.  Configurar o Google Cloud — Ativar Maps SDK for Android e Routes API. Gerar duas chaves: uma para o app, restrita ao pacote + SHA-1; outra só para o FastAPI, guardada como variável de ambiente do servidor. Sprint 8.

2.  Configurar react-native-maps — Adicionar a chave do Maps SDK em app.json (android.config.googleMaps.apiKey) e testar a renderização no Development Build. Sprint 8.

3.  Integrar a Routes API no FastAPI — Calcular a rota no backend somente para agendamentos ativos de ofertas 'Reservadas' (RB-06, ADR-09) e incluir a polyline nos dados do agendamento expostos sob /api/v1 (ADR-13). Sprint 8.

4.  Renderizar rota no mapa — Decodificar a polyline e desenhá-la com <Polyline> do react-native-maps, com <Marker> nos pontos de partida e destino. Sprint 8.

5.  Cache no WatermelonDB — Criar o model CachedRoute (meetingId, polyline, destination, createdAt, expiresAt) sincronizado pelo ADR-23. Sprint 8.

6.  Fallback offline — Ao detectar ausência de conexão (NetInfo, ADR-23), exibir a rota em cache; sem cache, exibir marcador do ponto de encontro + endereço em texto. Sprint 8.

7.  Expirar rotas — Remover o CachedRoute ao concluir ou cancelar o encontro e ao fim do prazo de expiração. Sprint 8.

8.  Testes — Teste de integração do endpoint de rota no FastAPI, teste do cache/sync e teste E2E com Maestro em Android (ADR-17) do fluxo de geração, exibição e expiração da rota. Sprint 8.

## 8. Referências *(recomendada)*

•  Google Maps Platform — Preços: https://mapsplatform.google.com/pricing/

•  Google Routes API — https://developers.google.com/maps/documentation/routes

•  Google Maps Platform — Mudanças de março de 2025 (Directions API legada e cotas gratuitas por SKU): https://developers.google.com/maps/billing-and-pricing/march-2025

•  Restrição de chaves de API do Google Maps — https://developers.google.com/maps/api-security-best-practices

•  react-native-maps — https://docs.expo.dev/versions/latest/sdk/map-view/

•  WatermelonDB — https://watermelondb.dev/ (cache offline, ADR-23)

•  Diagrama de Fluxo BPMN — P34: guardar leitura e sincronizar em 10 s (RNF-07)

•  Matriz de Rastreabilidade v2 — RF-10 → STY029 → RNF-07

•  Regras de Negócio — STY029-RN01 a RN04

•  ADRs relacionados do grupo: ADR-08, ADR-09, ADR-13, ADR-17, ADR-18, ADR-23

## Histórico de revisões

| Versão | Data | Autor | Alteração |
| --- | --- | --- | --- |
| 1.0 | 01/11/2026 | Rafael Tudela Rizental | Criação do documento. Decisão por Google Maps Platform (react-native-maps + Directions API) com fallback offline via WatermelonDB. |
| 1.1 | 01/11/2026 | Rafael Tudela Rizental | Alinhamento com as ADRs do grupo: Directions API chamada pelo FastAPI (chave no servidor) respeitando a RB-06 (ADR-09), polyline sincronizada pelo ADR-23, Development Build, validação em Android, Sprint 8 e participantes atualizados. Alerta de desvio removido por não constar nas regras de negócio. |
| 1.2 | 01/11/2026 | Rafael Tudela Rizental | Directions API (legada desde 01/03/2025, indisponível em projetos novos) substituída pela Routes API; crédito de US$ 200 substituído pela cota gratuita atual (10 k cálculos de rota/mês; Maps SDK for Android sem limite); teste E2E com Maestro (ADR-17). |
