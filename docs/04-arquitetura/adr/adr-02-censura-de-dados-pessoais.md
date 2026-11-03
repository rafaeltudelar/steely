# ADR-02 — Censura e mascaramento de dados pessoais e contatos no chat e anúncios
*Architecture Decision Record · Projeto Steely · Escola de TI · UniCesumar*

| Campo | Valor | Campo | Valor |
| :--- | :--- | :--- | :--- |
| **Status** | ☒ Proposto ☐ Aceito ☐ Rejeitado ☐ Substituído pelo ADR-___ | **Data** | 01/11/2026 |
| **Responsável** | Fabrício Notoya Thomas | **Sprint** | Sprint 8–9 (15–17) |
| **Participantes** | Fabrício Notoya Thomas, Augusto Palma Guglielmi, Thiago Lopes Martins, Pietro Pasqual Silva, Rafael Tudela Rizental | | |
| **Vínculos** | `RB-15` · `RB-06` · `RB-10` · `RF-08` · `RF-17` · `RNF-01` · `RNF-03` · `RNF-11` · `STY021 (RN01–RN05)` · `STY052 (RN01–RN05)` · `LGPD` · `ADR-05` · `ADR-07` · `ADR-08` · `ADR-09` · `ADR-11` · `ADR-13` | | |

---

## 1. Contexto *(obrigatória)*
Para evitar fraudes, evasão da custódia de 7 dias (`ADR-03`) e exposição indevida de dados pessoais (`LGPD`), a plataforma Steely impõe regras rigorosas sobre textos livres enviados no **Chat Interno (`RF-08`, `STY021`)** e nas **Descrições de Produtos (`STY016`, `STY052`)**:
1. **Regra de Negócio `RB-15` (Criptografia/Censura de Contatos) e `STY021-RN02`:** O chat deve censurar automaticamente números de telefone, e-mails, chaves/links externos e redes sociais **antes da reserva confirmada** (enquanto a oferta não atinge o status `"Reservado"` — `RB-06`), substituindo os padrões detectados por asteriscos (`***`) e alertando o remetente sobre a política de negociação segura na plataforma;
2. **Moderação de Descrições de Produtos em 2 Níveis (`STY052-RN01 a RN05`):** Na publicação ou edição de ofertas, trechos identificados com **alta confiança** (telefones, e-mails, CPF/CNPJ, endereços, links e perfis externos) devem ser ocultados automaticamente com notificação ao autor (`RN01`); casos de **confiança intermediária** (onde sequências alfanuméricas podem confundir-se com especificações legítimas de hardware, como `RTX 4070`, `13700K`, `3200 MHz` ou códigos de lote) devem ser encaminhados à **fila de revisão humana da moderação** (`RN02`), assegurando direito de contestação (`RN03`), punição por reincidência (`RN04`) e retenção preventiva caso o detector esteja indisponível (`RN05`);
3. **Integridade de Anexos e Ciclo de Vida (`STY021-RN01, RN03, RN04, RN05` e `ADR-07`):** O chat exige usuário autenticado e oferta ativa (mantendo chat ativo se houver reclamação aberta — `STY021-RN02` da planilha / modo somente leitura quando encerrada — `RN05`), bloqueia envio se houver *block* entre usuários (`RN04`), valida anexos contra *malware*/conteúdo impróprio (`RN03`, `ADR-11`) e tem seu conteúdo fisicamente excluído após os 30 dias de carência na eliminação de conta (`ADR-07`).

## 2. Direcionadores da decisão *(recomendada)*
* **Prevenção de Bypass e Segurança Server-Side (`RNF-01`, `RB-15`, `ADR-09`):** A censura não pode rodar apenas no navegador/app; como a Data API (PostgREST) está desabilitada (`ADR-09`), toda mensagem e descrição passa obrigatoriamente pelo **FastAPI** antes de ser gravada no PostgreSQL e antes de ser transmitida pelo *Supabase Realtime*.
* **Baixo Falso-Positivo em Domínio de Hardware (`STY052-RN01/RN02`):** Distinguir contatos reais (mesmo ofuscados com espaços ou palavras por extenso) de nomenclaturas técnicas de hardware (`DDR4-3600`, `Ryzen 7 5700X3D`, `LGA 1700`, `PCIe 4.0`).
* **Latência Sub-10ms e Custo Zero (`RNF-03`, `RNF-04`, `TAP`):** O filtro síncrono de mensagens em tempo real não pode depender de APIs externas pagas nem atrasar a entrega via WebSocket.
* **Privacidade nos Logs e Direito de Eliminação (`LGPD`, `ADR-05`, `ADR-07`):** O trecho censurado jamais deve vazar em texto claro nos logs de auditoria (`ADR-05`).

## 3. Opções consideradas *(obrigatória)*

| Aspecto | Opção A — Filtro Regex Apenas no Cliente (Front-end Web/Mobile) ou Revisão 100% Manual | Opção B — Chamada a LLM / API Comercial Externa de Moderação a Cada Mensagem | Opção C — Pipeline Server-Side no FastAPI (Normalizador Anti-Ofuscação + Motor Regex Compilado em 2 Níveis + Allowlist de Hardware + Fila de Moderação) |
| :--- | :--- | :--- | :--- |
| **Descrição** | Executar o filtro `regex` apenas no React/React Native antes do envio, ou depender exclusivamente de moderadores humanos lendo mensagens. | Enviar toda mensagem de chat e descrição de anúncio para uma API externa de IA (ex.: OpenAI Moderation / Perspective API) antes de salvar. | Executar no **FastAPI** um motor determinístico em **3 etapas**: (1) Normalizador anti-ofuscação (*leetspeak*/extenso); (2) *Allowlist* de tokens técnicos de hardware do catálogo; e (3) Motor `re` compilado em **2 faixas de confiança** (`Alta` $\rightarrow$ máscara imediata `***`; `Intermediária` $\rightarrow$ fila `STY052`), persistindo já mascarado no banco e disparando no *Supabase Realtime*. |
| **Prós** | • Simples de prototipar na interface. | • Boa compreensão semântica de contexto livre. | • **Impossível de burlar pelo cliente (`ADR-09`).**<br>• **Latência `< 2 ms` e custo R$ 0.**<br>• **Cumpre 100% da `RB-15`, `STY021` e `STY052` (2 níveis + contestação + reincidência).** |
| **Contras** | • **Inseguro (`RNF-01`):** facilmente burlado via requisições HTTP diretas à API; revisão 100% manual inviabiliza o chat em tempo real (`RNF-03`). | • **Inviável:** custo financeiro, latência alta (`300–1500 ms` por mensagem) e envio de dados pessoais brutos de usuários a terceiros (`LGPD`). | • Exige manter o dicionário de termos técnicos de hardware (*allowlist*) sincronizado com o catálogo para minimizar falsos positivos. |

## 4. Decisão *(obrigatória)*
**Opção escolhida:** ☐ A ☐ B ☒ **C**

Fica decidido o uso do **Pipeline Server-Side de Censura e Moderação em 2 Níveis no FastAPI (`ContentModerationService`)**, integrado ao PostgreSQL (`ADR-08`) e ao *Supabase Realtime*:

1. **Interceptação Obrigatória no FastAPI e Fluxo em Tempo Real (`ADR-09`, `RNF-03`, `STY021`):**
   * Como a Data API (PostgREST) está desligada (`ADR-09`), clientes Web e Android enviam mensagens exclusivamente via `POST /api/v1/chats/{chat_id}/messages` e publicam/editam ofertas via `POST/PATCH /api/v1/offers`.
   * O FastAPI verifica as pré-condições da `STY021`: usuário autenticado (`RN01`), inexistência de bloqueio entre remetente e destinatário (`RN04`), e se a oferta está ativa ou com reclamação aberta (`RN02`), recusando escritas com erro **RFC 9457** (`ADR-13`) se a oferta estiver encerrada (`RN05` — modo somente leitura).
2. **Estágio 1 — Normalização Anti-Evasão e *Allowlist* de Catálogo de Hardware:**
   * Antes de avaliar os padrões, o serviço gera uma visão normalizada do texto que remove caracteres invisíveis/*zero-width*, colapsa dígitos separados por espaços/pontos/hífens (`"4 4 9 9 1..."` $\rightarrow$ `"44991..."`) e converte termos de evasão comuns (`"arroba"` $\rightarrow$ `@`, `"ponto com"` $\rightarrow$ `.com`, `"zero/um/dois..."` sequenciais para dígitos).
   * Em seguida, aplica uma **Allowlist de Especificações de Hardware** (alimentada pelo catálogo de SKUs e pelas liberações de falsos positivos da moderação — `STY052` passo 7), protegendo tokens técnicos legítimos (`RTX 3060`, `i5-12400F`, `DDR5-6000`, `1920x1080`, `500W`, `Socket 1151`).
3. **Estágio 2 — Motor de Regex em Dois Níveis de Confiança (`RB-15`, `STY021-RN02`, `STY052-RN01/RN02`):**
   * **Faixa de Alta Confiança (Ocultação Automática Imediata por `***`):**
     * *Padrões:* E-mails (`[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+`), URLs e encurtadores (`https?://`, `www\.`, `wa\.me`, `t\.me`, `bit\.ly`), menções a mensageiros/redes (`whats`, `zap`, `insta`, `telegram` acompanhados de números ou `@handle`), CPF/CNPJ, chaves PIX aleatórias, CEP (`\b\d{5}-?\d{3}\b`) e telefones brasileiros (`(?:\+?55\s?)?(?:\(?\d{2}\)?\s?)?9?\d{4}[-.\s]?\d{4}`).
     * *Comportamento no Chat (`RB-15`, `STY021-RN02`):* Aplicado sempre que o status da oferta for **anterior a `"Reservado"`** (`RB-06`). O trecho é substituído por `***` antes do `INSERT` em `public.mensagens`, a mensagem já mascarada é emitida via *Supabase Realtime* e o JSON de resposta devolve `censored: true` com alerta educativo ao remetente. Após a reserva confirmada (`status = 'RESERVED'`), a restrição de contato no chat daquela reserva é suspensa conforme `RB-15` e `RB-06`.
     * *Comportamento em Descrições de Anúncios (`STY052-RN01`):* Aplicado permanentemente na publicação e edição; oculta o trecho com `***` e notifica o vendedor. Se mais de 40% da descrição for ocultada ou comprometer a compreensão (`STY052` FA-01), solicita reescrita imediata.
   * **Faixa de Confiança Intermediária (Fila de Revisão Humana — `STY052-RN02`):**
     * Sequências numéricas ou alfanuméricas de 8 a 11 caracteres em descrições de produtos que não casaram com a *allowlist* nem com contexto explícito de telefone/CPF são gravadas com `moderation_status = 'PENDING_REVIEW'` e enviadas à **Fila de Revisão da Moderação** (`STY052` passos 3–6).
     * O moderador pode: (a) confirmar a censura; (b) liberar como falso positivo (adicionando o padrão à *allowlist* técnica — passo 7); ou (c) analisar contestações abertas pelo autor (`STY052-RN03`). Caso o serviço de detecção falhe, publicações com texto livre ficam retidas preventivamente para revisão manual (`STY052-RN05`).
4. **Anexos de Chat (`STY021-RN03`), Reincidência (`STY052-RN04`), Auditoria (`ADR-05`) e Expurgo (`ADR-07`):**
   * **Anexos (`STY021-RN03`):** Limitados a até 3 imagens por mensagem (`<= 2 MB` cada), inspecionadas pelo `MediaSanitizerService` (`ADR-11`: validação de *Magic Bytes* contra executáveis/scripts maliciosos, remoção total de `EXIF`/`GPS` e conversão `WebP`) e salvas no bucket privado `chat-attachments` com *Signed URL* de 15 min.
   * **Reincidência (`STY052-RN04`, `RB-10`):** Cada tentativa de envio de contato proibido incrementa um contador por usuário; ao atingir o limite parametrizado em `app_config` (padrão: **5 ocorrências em 7 dias**), o sistema aplica penalidade no *Trust Score* e encaminha o usuário para sanção da moderação.
   * **Auditoria sem PII (`ADR-05`) e Eliminação (`ADR-07`):** Toda censura ou decisão de moderador gera registro em `audit.system_and_access_logs` contendo apenas o `rule_triggered` (ex.: `PHONE_MASKED`, `EMAIL_MASKED`) e o `correlation_id`, **jamais gravando o telefone/CPF bruto no log**. Na eliminação de conta após 30 dias (`private.anonimizar_usuario` — `ADR-07`), todas as mensagens, rascunhos e anexos de chat do titular são fisicamente apagados.

## 5. Consequências *(obrigatória)*
* **Positivas:**
  * Cumpre integralmente a `RB-15`, `STY021 (RN01–RN05)` e `STY052 (RN01–RN05)` com execução determinística em `< 2 ms`, custo zero e impossibilidade de *bypass* pelo cliente.
  * Evita falsos positivos em números de modelos de hardware graças à combinação de *allowlist* do catálogo + fila de confiança intermediária (`STY052-RN02`).
* **Negativas ou riscos aceitos:**
  * Usuários mal-intencionados podem tentar enviar foto de um papel com número de telefone escrito à mão no anexo do chat; a mitigação é o alerta de política, a denúncia em 1 clique (`STY049`) e a possibilidade de acionar o estágio de `PaddleOCR` (`ADR-01`) sobre anexos denunciados.
* **O que muda no código, no banco, na arquitetura e nos diagramas:**
  * Criação do módulo `app/services/content_moderation.py` no FastAPI e da tabela `public.moderation_curation_queue` (`STY052`) no PostgreSQL Core.

## 6. Validação *(recomendada)*
* **Teste de Censura Pré-Reserva vs. Pós-Reserva (`pytest` — `RB-15`, `STY021-RN02`):** Enviar `"Me chama no 44 99988-7766 ou teste@email.com"` em oferta `"Disponível"` $\rightarrow$ comprovar persistência como `"Me chama no *** ou ***"` e flag `censored: true`; repetir após mudança da oferta para `"Reservado"` $\rightarrow$ comprovar liberação.
* **Teste de Falsos Positivos de Hardware e Fila de Moderação (`STY052`):** Publicar anúncio contendo `"Processador i7-13700K DDR5 5600MHz"` $\rightarrow$ aprovado sem censura; publicar sequência numérica ambígua $\rightarrow$ encaminhado para `PENDING_REVIEW` na fila do moderador.

## 7. Plano de implementação *(recomendada)*
1. **Implementar `ContentModerationService` (normalizador anti-ofuscação, regex de alta/média confiança e allowlist de SKUs) no FastAPI:** Fabrício e Thiago — *Sprint 8 (16)*.
2. **Integrar o filtro às rotas de Chat (`STY021`) e Ofertas (`STY016`/`STY052`) e criar tabela de fila/contestação de censura:** Fabrício, Augusto e Thiago — *Sprint 8–9 (16)*.
3. **Implementar avisos de censura no chat e tela de revisão/contestação da moderação (`STY052`):** Pietro e Rafael — *Sprint 9 (17)*.

## 8. Referências *(recomendada)*
* Documento de Regras de Negócio (`RB-06`, `RB-10`, `RB-15`) e Documento de Requisitos v2.0 (`RF-08`, `RF-17`, `RNF-01`, `RNF-03`, `RNF-11`).
* Especificação de Casos de Uso (`STY021 — Enviar Mensagem`, `STY052 — Censura de Dados Pessoais em Descrições de Produtos`).
* Lei Geral de Proteção de Dados (`Lei nº 13.709/2018`).
* ADRs relacionados: `ADR-01`, `ADR-03`, `ADR-05`, `ADR-07`, `ADR-08`, `ADR-09`, `ADR-11`, `ADR-13`.

---

### Histórico de revisões
| Versão | Data | Autor | Alteração |
| :--- | :--- | :--- | :--- |
| 1.0 | 01/11/2026 | Fabrício Notoya Thomas | Definição do pipeline server-side de censura e moderação em 2 níveis (`RB-15`, `STY021`, `STY052`), allowlist de hardware, sanitização de anexos e alinhamento com `ADR-05` e `ADR-07`. |
