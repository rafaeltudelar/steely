# ADR-11 — Armazenamento de imagens
*Architecture Decision Record · Projeto Steely · Escola de TI · UniCesumar*

| Campo | Valor | Campo | Valor |
| :--- | :--- | :--- | :--- |
| **Status** | ☒ Proposto ☐ Aceito ☐ Rejeitado ☐ Substituído pelo ADR-___ | **Data** | 01/11/2026 |
| **Responsável** | Fabrício Notoya Thomas | **Sprint** | Sprint 8–9 (15–17) |
| **Participantes** | Fabrício Notoya Thomas, Rafael Tudela Rizental, Augusto Palma Guglielmi, Thiago Lopes Martins, Pietro Pasqual Silva | | |
| **Vínculos** | `STY016` · `LGPD` · `RB-06` · `RF-13` · `RNF-01` · `RNF-05` · `RNF-07` · `RNF-09` · `STY010` · `STY016-RN02` · `STY021-RN03` · `STY031` · `STY039` · `STY047-RN03` · `ADR-05` · `ADR-07` · `ADR-08` · `ADR-27` | | |

---

## 1. Contexto *(obrigatória)*
O fluxo operacional do Steely depende do armazenamento seguro e eficiente de mídias visuais com diferentes requisitos de privacidade, tamanho e retenção:
1. **Fotos de Ofertas e Dataset de IA (`RF-05`, `STY016`, `RNF-09`):** são públicas para exibição no catálogo e no Hardware Captcha (`RF-16`), mas **não podem conter metadados `EXIF` (especialmente coordenadas GPS)**, sob risco de revelar o endereço exato do vendedor antes da reserva confirmada (violando `RB-06`, `STY016-RN02` e a `LGPD`).
2. **Anexos de Chat (`RF-08`, `STY021`):** imagens privadas trocadas durante a negociação.
3. **Evidências de Devolução, Garantia e Laudos (`RF-12`, `RF-13`, `STY031`, `BPMN P5/P5b`):** exigem foto legível do Número de Série (`S/N`) e **vídeo curto do defeito em bancada**.
4. **Documentos de Identidade (`KYC` — `RB-01`) e Documentação Societária de ONGs (`RF-17`, `STY039`):** arquivos altamente sensíveis que exigem proteção em repouso (`RNF-01`) e acesso restrito ao back-office.

É necessário definir onde guardar essas mídias no escopo atual (plano gratuito até 23/11, preparando o caminho para escalabilidade futura), como garantir a remoção automática de `EXIF` no backend Python (FastAPI) e qual política de acesso aplicar.

## 2. Direcionadores da decisão *(recomendada)*
* **Privacidade e Conformidade LGPD (`STY016-RN02`, `STY047-RN03`, `RB-06`):** Garantia técnica de que 100% das imagens armazenadas tenham seus metadados `EXIF`/`GPS` destruídos antes da persistência.
* **Controle de Acesso Estrito a Mídias Privadas (`RNF-01`, `RB-01`):** Impedir acesso não autenticado a documentos de KYC/ONGs, anexos de chat e vídeos de disputas.
* **Custo Zero no MVP com Escalabilidade Futura (`TAP`, `ADR-08`, `ADR-27`):** Operar dentro do plano gratuito do *Supabase Storage* durante a fase acadêmica, mas desacoplado por uma camada de serviço no FastAPI compatível com protocolo S3 (permitindo migrar para Cloudflare R2 ou AWS S3 em produção futura).

## 3. Opções consideradas *(obrigatória)*

| Aspecto | Opção A — Salvar Binários (`BYTEA` / Base64) dentro do PostgreSQL | Opção B — Supabase Storage Segregado em Buckets (Público vs. Privados com Signed URLs) + Sanitização `Pillow` no FastAPI | Opção C — Serviço Pago Dedicado de Mídia (AWS S3 + CloudFront desde o Dia 1) |
| :--- | :--- | :--- | :--- |
| **Descrição** | Gravar os arquivos de imagem e vídeo diretamente em colunas binárias dentro das tabelas do banco PostgreSQL. | Utilizar o **Supabase Storage** (integrado ao `ADR-08`) no MVP, isolado por uma classe `StorageService` no FastAPI. As imagens passam pelo FastAPI (`Pillow`) para remoção obrigatória de `EXIF` e conversão para `WebP`, sendo salvas em buckets públicos ou privados protegidos por **Signed URLs**. | Contratar infraestrutura paga na AWS S3 desde o início do projeto acadêmico. |
| **Prós** | • Sem necessidade de gerenciar buckets externos. | • **Custo zero atual** e integração nativa com o ecossistema Supabase (`ADR-08`, `ADR-09`).<br>• Remoção infalível de `EXIF` em Python (`Pillow`) + redução de 70% no peso ao converter para `WebP`.<br>• Suporte a vídeos curtos de disputa (`<= 30s` / `<= 50 MB`) e *Signed URLs* temporárias.<br>• Fácil migração futura para Cloudflare R2 / AWS S3 (já que o Supabase Storage usa protocolo compatível com S3). | • Capacidade de armazenamento virtualmente ilimitada mediante pagamento por uso. |
| **Contras** | • **Inviável:** esgota os 500 MB do banco rapidamente (apenas 10 vídeos de 50 MB lotariam o SGBD) e degrada a performance das queries (`RNF-04`). | • Limite de 1 GB no plano gratuito atual (mitigado pela compressão WebP nas fotos e limpeza/expurgo de mídias de disputas encerradas; escalável para R2/S3 no futuro). | • Exige cartão de crédito internacional e gera custo financeiro, contrariando o `TAP` (Orçamento R$ 0). |

## 4. Decisão *(obrigatória)*
**Opção escolhida:** ☐ A ☒ **B** ☐ C

Fica decidido o uso do **Supabase Storage com Segregação de Buckets e Sanitização Server-Side via `Pillow` no FastAPI**, estruturado para atender ao plano gratuito atual e preparado para escalabilidade S3 futura:

1. **Arquitetura de Buckets e Política de Acesso (`RLS` + *Signed URLs*):**
   * **Bucket `offers-media` (Público para Leitura / Escrita somente via FastAPI):**
     * Armazena as imagens já limpas (sem `EXIF`) das ofertas do catálogo (`STY016`) e do repositório do Hardware Captcha (`STY046`).
     * Regras: até 6 fotos por oferta, comprimidas na origem a `<= 2 MB` (`ADR-27`) e convertidas no FastAPI para `WebP` (foco + miniatura `400x400`).
   * **Bucket `chat-attachments` (Privado):**
     * Armazena imagens enviadas no chat (`STY021`, `<= 2 MB`, sem `EXIF`). Acesso permitido apenas aos dois participantes da conversa e à moderação por meio de **Signed URL com expiração de 15 minutos**.
   * **Bucket `disputes-laudos` (Privado — Imagens e Vídeos Curtos):**
     * Armazena fotos de Número de Série (`S/N`), fotos de testes periciais (`RF-12`) e **vídeos de evidência de defeito para devolução (`RF-13`, `BPMN P5b`)**.
     * **Regra para Vídeos:** formato `MP4` ou `WebM`, duração máxima de **30 segundos** e tamanho máximo de **50 MB**. Acesso restrito às partes da transação e aos moderadores via **Signed URL temporária**.
   * **Bucket `kyc-institutional-docs` (Estritamente Privado e Sensível):**
     * Armazena documentos de identidade (`RB-01`) e estatutos/atas de ONGs (`STY039`). Criptografado em repouso (`AES-256` — `RNF-01`) e acessível exclusivamente por administradores do back-office via **Signed URL de 5 minutos**, gerando log obrigatório em `audit.system_and_access_logs` (`ADR-05`).
   * **Expurgo Físico em Eliminação de Conta (`ADR-07`, `STY010`):** Quando a carência de 30 dias expira e `private.anonimizar_usuario(user_id)` é executada (`ADR-16`), o FastAPI remove fisicamente dos buckets do Supabase Storage a foto de perfil do titular, os anexos de chat (`chat-attachments`) e as fotos de anúncios sem transação ativa (`offers-media`).
2. **Pipeline de Remoção Automática de EXIF e Validação no FastAPI (`STY016-RN02`):**
   * Além da compressão no cliente (`ADR-27`), todo upload de imagem recebido pelo FastAPI passa por um pipeline obrigatório em memória usando a biblioteca **`Pillow` (`PIL`)**:
     1. Validação dos *Magic Bytes* do cabeçalho binário (bloqueando arquivos maliciosos renomeados como `.jpg` — `STY021-RN03`);
     2. Re-codificação limpa dos pixels para formato `WebP` sem copiar os dicionários `info['exif']`, `gps_info` ou perfis proprietários — **garantindo 0% de metadados de localização na imagem salva**;
     3. Cálculo de *hash* perceptual (`imagehash` / `SHA-256`) para detectar reutilização fraudulenta da mesma foto em anúncios distintos (`STY016` Fluxo Alternativo 4).
3. **Estratégia de Escalabilidade Futura:**
   * A comunicação do FastAPI com o Storage é encapsulada na interface `MediaStorageProvider`. No escopo acadêmico atual, utiliza o plano gratuito do Supabase Storage; em cenário de crescimento comercial futuro (múltiplos vídeos de 50 MB e datasets massivos de IA — `RNF-09`), basta apontar as credenciais compatíveis com `S3` para **Cloudflare R2** ou **AWS S3** sem alterar os endpoints da API.

## 5. Consequências *(obrigatória)*
* **Positivas:**
  * Conformidade total com a `LGPD`, `RB-06` e `STY016-RN02`: mesmo que o vendedor tire uma foto com o GPS do celular ligado, o arquivo publicado no bucket `offers-media` não possui nenhuma coordenada geográfica.
  * Suporte completo ao fluxo de devolução (`RF-13`) com vídeos de até 30s / 50 MB protegidos em bucket privado.
  * Isolamento arquitetural que permite escalar o armazenamento no futuro sem refatorar o código de negócio.
* **Negativas ou riscos aceitos:**
  * O upload passa pelo FastAPI para sanitização antes de ir ao bucket, consumindo ~50 ms a 120 ms de CPU para imagens (dentro do limite do `RNF-05`). Para vídeos de até 50 MB, o FastAPI valida tamanho/formato em *stream* e encaminha ao bucket privado.
* **O que muda no código, no banco, na arquitetura e nos diagramas:**
  * Adição das bibliotecas `Pillow` e `imagehash` no `requirements.txt` do FastAPI.
  * Criação dos 4 buckets no Supabase Storage e armazenamento apenas do caminho relativo (`bucket/path`) no banco PostgreSQL.

## 6. Validação *(recomendada)*
* **Teste de Remoção de EXIF (`pytest`):** Submeter uma imagem JPEG contendo coordenadas `EXIF GPSLatitude` e `GPSLongitude` ao endpoint de upload do FastAPI; baixar a imagem resultante do bucket `offers-media` e verificar via `Pillow` (`img.getexif()`) que o dicionário de metadados está completamente vazio.
* **Teste de Segurança de Bucket Privado:** Tentar acessar um documento do bucket `kyc-institutional-docs` ou um vídeo do `disputes-laudos` por URL pública direta $\rightarrow$ deve retornar `403/400 Access Denied`.

## 7. Plano de implementação *(recomendada)*
1. **Criar os 4 buckets (`offers-media`, `chat-attachments`, `disputes-laudos`, `kyc-institutional-docs`) no Supabase:** Fabrício — *Sprint 8*.
2. **Implementar o `MediaSanitizerService` com `Pillow` no FastAPI (remoção de EXIF, conversão `WebP` e limite de 50 MB/30s para vídeos):** Fabrício — *Sprint 8*.
3. **Integrar o upload com a compressão client-side do Web e Mobile (`ADR-27`):** Fabrício, Pietro e Rafael — *Sprint 9*.

## 8. Referências *(recomendada)*
* Lei Geral de Proteção de Dados (`Lei nº 13.709/2018`).
* Documento de Requisitos v2.0 (`RF-05`, `RF-08`, `RF-13`, `RF-17`, `RNF-01`, `RNF-05`, `RNF-07`, `RNF-09`).
* Especificação de Casos de Uso e Regras de Negócio (`STY016-RN02`, `STY021-RN03`, `STY031`, `STY039`, `STY047-RN03`, `RB-06`).
* ADRs relacionados: `ADR-05`, `ADR-07`, `ADR-08`, `ADR-09`, `ADR-27`.

---

### Histórico de revisões
| Versão | Data | Autor | Alteração |
| :--- | :--- | :--- | :--- |
| 1.0 | 31/10/2026 | Fabrício Notoya Thomas | Definição dos buckets segregados, remoção de EXIF via Pillow, limite de vídeo (30s/50MB) e política de Signed URLs. |
| 1.1 | 01/11/2026 | Fabrício Notoya Thomas | Alinhamento com `ADR-05` (`audit.system_and_access_logs`) e `ADR-07` (exclusão física das fotos de perfil, chats e ofertas sem transação ativa após os 30 dias de carência). |
