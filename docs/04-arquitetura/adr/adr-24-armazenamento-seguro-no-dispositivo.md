# ADR-24 — Armazenamento seguro no dispositivo
**Architecture Decision Record · Projeto Steely · Escola de TI · UniCesumar**

| Campo | Valor | Campo | Valor |
| --- | --- | --- | --- |
| **Status** | ☒ Proposto  ☐ Aceito  ☐ Rejeitado  ☐ Substituído pelo ADR-___ | **Data** | 01/11/2026 |
| **Responsável** | Rafael Tudela Rizental | **Sprint** | 8 |
| **Participantes** | Augusto Palma Guglielmi, Fabrício Notoya Thomas, Pietro Pasqual Silva, Rafael Tudela Rizental, Thiago Lopes Martins | | |
| **Vínculos** | RNF-02, RNF-01 · ADR-07 · ADR-09 · ADR-13 · ADR-14 · ADR-17 · ADR-18 · ADR-21 · ADR-23 | | |

## 1. Contexto *(obrigatória)*

O Steely utiliza QR Codes assinados digitalmente com Ed25519 para confirmação de entrega presencial entre comprador e vendedor. Conforme o fluxo BPMN P34, o vendedor escaneia o QR do comprador com validação offline em até 150 ms (RNF-02). O sistema também mantém tokens de sessão JWT emitidos pelo backend FastAPI (ADR-13) para autenticação do usuário (RNF-01).

As regras de negócio definem que o QR Code é único, assinado digitalmente e vinculado com prazo de validade (STY027-RN01). A validação verifica assinatura, vigência e vínculo da transação (STY028-RN01). Quando o dispositivo está sem conexão, a leitura é armazenada localmente e sincronizada quando o acesso for restabelecido (STY028-RN04); para que a validação aconteça offline em até 150 ms (BPMN P34, RNF-02), a chave pública precisa estar armazenada no próprio dispositivo. A leitura validada entra na fila de mutações offline do WatermelonDB com um Idempotency-Key (ADR-23, ADR-14).

A chave pública Ed25519 e os tokens JWT são informações críticas: se comprometidas, permitiriam falsificação de confirmações de entrega ou acesso não autorizado à conta. Este ADR define onde e como armazenar essas informações de forma protegida no dispositivo, garantindo acesso rápido (< 150 ms) e segurança contra extração.

## 2. Direcionadores da decisão *(recomendada)*

•  RNF-01 — confidencialidade e segurança dos dados de autenticação (tokens JWT, credenciais)

•  RNF-02 — integridade do QR Code com validação criptográfica offline em até 150 ms

•  STY028-RN04 — sem conexão, a leitura é armazenada localmente e sincronizada quando o acesso for restabelecido (exige a chave pública disponível no dispositivo)

•  STY027-RN01 — QR Code único, assinado com Ed25519 e vinculado com prazo de validade

•  Base nativa do app — o app já roda como Development Build (expo-dev-client) por causa do WatermelonDB (ADR-23); a preferência é por pacotes oficiais do Expo SDK, sem adicionar novos plugins nativos

•  Proteção contra extração — chaves e tokens não devem ser acessíveis por outros aplicativos nem em dispositivos com root

•  Latência de acesso — leitura da chave pública deve completar em tempo desprezível para não comprometer o limite de 150 ms da validação

## 3. Opções consideradas *(obrigatória)*

| Opção A — expo-secure-store | Opção B — react-native-keychain | Opção C — AsyncStorage + expo-crypto |
| --- | --- | --- |
| Descrição<br>Pacote oficial do Expo SDK que guarda pares chave-valor criptografados; no Android, os valores ficam no SharedPreferences, cifrados com chave do Android Keystore gerenciada pelo sistema operacional.<br>Prós<br>•  Proteção por hardware em dispositivos compatíveis<br>•  Pacote oficial do Expo, sem novos plugins nativos além do Development Build (ADR-23)<br>•  Leitura < 5 ms, compatível com a validação em 150 ms (RNF-02)<br>•  API simples (get/set) e biometria configurável por item<br>Contras<br>•  Indicado só para valores pequenos (segredos curtos)<br>•  Apenas chave-valor, sem consultas<br>•  Dados apagados ao desinstalar o app | Descrição<br>Biblioteca de terceiros sobre o Android Keystore, com suporte avançado a biometria e controle granular de acessibilidade.<br>Prós<br>•  Proteção por hardware<br>•  Biometria avançada<br>•  Sem limite prático de tamanho por item<br>Contras<br>•  Adiciona módulo nativo de terceiros ao build<br>•  Configuração de serviços nativos mais complexa<br>•  Benefício extra não proporcional ao escopo do projeto | Descrição<br>AsyncStorage (não criptografado) combinado com criptografia AES-256 feita manualmente via expo-crypto.<br>Prós<br>•  Não exige módulos nativos adicionais<br>•  Sem limite de tamanho por item<br>Contras<br>•  Criptografia apenas em software, sem proteção por hardware<br>•  Chave AES precisa ser guardada à parte (problema circular de segurança)<br>•  Latência de 10–50 ms e esforço de implementação alto |

Comparativo por critério

| Critério | A · expo-secure-store | B · react-native-keychain | C · AsyncStorage + expo-crypto |
| --- | --- | --- | --- |
| Mecanismo de armazenamento (Android) | SharedPreferences cifradas com chave do Android Keystore | Android Keystore | AsyncStorage + criptografia AES-256 manual |
| Proteção por hardware | Sim — hardware-backed em dispositivos compatíveis | Sim — hardware-backed | Não — criptografia em software |
| Manutenção do pacote | Oficial do Expo SDK | Biblioteca de terceiros | Expo SDK + AsyncStorage |
| Novos módulos nativos no build | Não | Sim (plugin nativo adicional) | Não |
| Suporte a biometria | Sim (configurável por item) | Sim (avançado) | Não nativo |
| Latência de leitura | < 5 ms | < 5 ms | 10–50 ms (decrypt + deserialização) |
| Limite de tamanho por item | Sem limite próprio do Expo no Android (indicado para valores pequenos) | Sem limite prático | Sem limite |
| Gestão de chaves | Automática (SO gerencia) | Automática (SO gerencia) | Manual (chave AES deve ser armazenada separadamente) |
| Esforço de integração | Baixo (API simples get/set) | Médio (configuração de serviços nativos) | Alto (implementar encrypt/decrypt + gestão de chave AES) |

## 4. Decisão *(obrigatória)*

Adotar expo-secure-store (Opção A) para armazenamento protegido dos tokens de sessão JWT e da chave pública Ed25519 no dispositivo.

No Android, o expo-secure-store grava os valores no SharedPreferences, cifrados com uma chave mantida no Android Keystore, protegida por hardware quando o aparelho oferece esse recurso. A latência de leitura inferior a 5 ms garante ampla margem para a validação do QR Code dentro do limite de 150 ms (RNF-02). O Expo não fixa limite de tamanho no Android, e os valores guardados são pequenos: um token JWT ocupa ~1 KB e uma chave pública Ed25519 ocupa 32 bytes (44 bytes em Base64).

Por ser um pacote oficial mantido pelo próprio Expo SDK, não exige adicionar novos plugins nativos além do Development Build já configurado (ADR-23). A gestão automática de chaves pelo sistema operacional elimina o risco de exposição da chave de criptografia, problema intrínseco à Opção C.

Quando o usuário pede a exclusão da conta ou tem a sessão revogada porque a conta entrou em EM_CARENCIA (ADR-07), o app chama deleteItemAsync para STEELY_JWT_ACCESS, STEELY_JWT_REFRESH e STEELY_ED25519_PUB, junto com a limpeza do banco local do WatermelonDB e do cache (ADR-23), e volta para a tela de login.

A Opção B (react-native-keychain) foi descartada porque acrescentaria um módulo nativo de terceiros ao build sem oferecer benefícios proporcionais para o escopo do projeto. A Opção C (AsyncStorage + expo-crypto) foi descartada pela ausência de proteção por hardware e pelo problema circular de armazenamento seguro da chave AES.

## 5. Consequências *(obrigatória)*

Positivas

•  Proteção por hardware — A chave que protege os dados fica no Android Keystore, hardware-backed quando disponível, dificultando a extração mesmo em dispositivos com root.

•  Pacote oficial do Expo — Mantido pelo Expo SDK; não adiciona novos plugins nativos ao Development Build (ADR-23).

•  Latência inferior a 5 ms — Garante que a validação do QR Code (leitura da chave Ed25519 + verificação de assinatura) permaneça dentro dos 150 ms exigidos pelo RNF-02.

•  Suporte a desbloqueio biométrico — Permite exigir biometria do Android para ler itens sensíveis em operações críticas.

•  Isolamento por aplicação — Cada app acessa apenas seus próprios itens, sem risco de leitura cruzada entre aplicativos.

Negativas

•  Indicado só para valores pequenos — O Expo não fixa limite no Android, mas valores grandes podem ser recusados pela camada nativa. Tokens JWT (~1 KB) e chaves Ed25519 (32 bytes) cabem com folga; dados maiores ficam no WatermelonDB (ADR-23).

•  Sem suporte a consultas — Armazenamento exclusivamente chave-valor; não é possível buscar ou filtrar itens por conteúdo.

•  Perda de dados na desinstalação — No Android, os dados são apagados ao desinstalar o app. O usuário precisará autenticar-se novamente e receber uma nova chave pública do servidor.

•  Sem sincronização entre dispositivos — O armazenamento é local; trocar de dispositivo exige novo login e redistribuição da chave pública Ed25519 pelo backend.

## 6. Validação *(recomendada)*

| Cenário de teste | Critério de aceitação |
| --- | --- |
| Validação completa do QR Code | Leitura da chave Ed25519 do secure store + verificação da assinatura digital concluída em ≤ 150 ms (RNF-02), medida em dispositivo Android intermediário |
| Resistência a extração | Em dispositivo Android com root, tentativa de acessar os dados via ferramentas de forense (Frida, objection) não retorna texto legível dos tokens ou da chave |
| Validação offline | Com dispositivo em modo avião, a leitura e verificação do QR Code funciona usando a chave armazenada localmente e a leitura entra na fila offline com Idempotency-Key (STY028-RN04, ADR-23, ADR-14) |
| Rotação de token | Ao receber novo JWT do FastAPI, o token anterior é substituído no secure store sem janela de indisponibilidade |
| Recuperação pós-reinstalação | Após desinstalar e reinstalar o app, o sistema solicita novo login e obtém nova chave pública Ed25519 do servidor sem erros |
| Proteção biométrica | Ao configurar requireAuthentication: true, a leitura do token exige confirmação biométrica antes de retornar o valor |
| Limpeza na exclusão ou revogação | Após pedir a exclusão da conta ou ter a sessão revogada por EM_CARENCIA (ADR-07), getItemAsync retorna vazio para as três chaves e o banco do WatermelonDB está zerado (ADR-23) |

## 7. Plano de implementação *(recomendada)*

1.  Instalar dependência — npx expo install expo-secure-store e validar no Development Build do app (ADR-23). Sprint 8.

2.  Criar módulo secureStorage.ts — Encapsular getItemAsync, setItemAsync e deleteItemAsync em funções tipadas com tratamento de erro. Definir constantes para as chaves: STEELY_JWT_ACCESS, STEELY_JWT_REFRESH, STEELY_ED25519_PUB. Sprint 8.

3.  Integrar com autenticação — Fazer login via FastAPI (POST /api/v1/auth/login), exibindo o Captcha Cloudflare Turnstile em react-native-webview a partir da 3ª falha (ADR-21). Persistir access token e refresh token no secure store e injetá-los nas requisições pelo cliente HTTP tipado openapi-fetch, gerado do openapi.snapshot.json (ADR-13, ADR-18). Sprint 8.

4.  Armazenar chave pública Ed25519 — Ao receber a chave pública do servidor (no primeiro login ou após rotação), salvar no secure store com a chave STEELY_ED25519_PUB (32 bytes em Base64 = 44 caracteres). Sprint 8.

5.  Implementar verificação offline do QR Code — No fluxo de leitura do QR (STY027/STY028), ler a chave pública do secure store e verificar a assinatura Ed25519 do payload em ≤ 150 ms; gerar o Idempotency-Key (UUID v4) e gravar a leitura na fila offline do WatermelonDB com o jti do QR Code (ADR-23, ADR-14). Sprint 8.

6.  Configurar proteção biométrica (opcional) — Para operações críticas, configurar requireAuthentication: true nas opções de leitura do secure store. Sprint 8.

7.  Tratar reinstalação — No splash/bootstrap do app, verificar se as chaves existem. Se ausentes, redirecionar para fluxo de login e solicitar nova chave pública ao backend. Sprint 8.

8.  Limpeza local — Implementar a função que remove as três chaves do secure store e aciona a limpeza do WatermelonDB e do cache (ADR-23) na exclusão da conta e na revogação da sessão por EM_CARENCIA (ADR-07). Sprint 8.

9.  Testes automatizados — Testes unitários com Jest e mock do expo-secure-store e testes E2E com Maestro em Android (ADR-17) validando armazenamento, leitura, verificação e limpeza. Sprint 8.

## 8. Referências *(recomendada)*

•  Expo SecureStore — Documentação oficial: https://docs.expo.dev/versions/latest/sdk/securestore/

•  Android Keystore — https://developer.android.com/privacy-and-security/keystore

•  Ed25519 (RFC 8032) — https://datatracker.ietf.org/doc/html/rfc8032

•  OWASP Mobile Security — Secure Storage: https://mas.owasp.org/MASTG/General/0x05d-Testing-Data-Storage/

•  Diagrama de Fluxo BPMN — P34: validação offline em 150 ms (RNF-02)

•  Matriz de Rastreabilidade v2 — RF-11 → STY027, STY028 → RNF-02, RNF-09

•  Regras de Negócio — STY027-RN01 a RN03, STY028-RN01 a RN04

•  ADRs relacionados do grupo: ADR-07, ADR-09, ADR-13, ADR-14, ADR-17, ADR-18, ADR-21, ADR-23

## Histórico de revisões

| Versão | Data | Autor | Alteração |
| --- | --- | --- | --- |
| 1.0 | 01/11/2026 | Rafael Tudela Rizental | Criação do documento. Decisão por expo-secure-store para armazenamento protegido de tokens JWT e chave pública Ed25519. |
| 1.1 | 01/11/2026 | Rafael Tudela Rizental | Alinhamento com as ADRs do grupo: login via FastAPI com Turnstile (ADR-21) e cliente openapi-fetch (ADR-13, ADR-18), fila offline com Idempotency-Key (ADR-14, ADR-23), Development Build, validação em Android, Sprint 8 e participantes atualizados. |
| 1.2 | 01/11/2026 | Rafael Tudela Rizental | Mecanismo do Android corrigido (SharedPreferences cifradas com chave do Android Keystore); limite de 2 KB substituído pela orientação de valores pequenos, já que o Expo não fixa limite no Android; testes com Jest e Maestro (ADR-17). |
| 1.3 | 01/11/2026 | Rafael Tudela Rizental | Remoção das chaves do expo-secure-store, junto com a limpeza do WatermelonDB (ADR-23), na exclusão da conta e na revogação da sessão por EM_CARENCIA (ADR-07). |
