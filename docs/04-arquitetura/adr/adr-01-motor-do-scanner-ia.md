# ADR-01 — Arquitetura e motor de visão computacional do Scanner IA
*Architecture Decision Record · Projeto Steely · Escola de TI · UniCesumar*

| Campo | Valor | Campo | Valor |
| :--- | :--- | :--- | :--- |
| **Status** | ☒ Proposto ☐ Aceito ☐ Rejeitado ☐ Substituído pelo ADR-___ | **Data** | 01/11/2026 |
| **Responsável** | Fabrício Notoya Thomas | **Sprint** | Sprint 8–9 (15–17) |
| **Participantes** | Fabrício Notoya Thomas, Augusto Palma Guglielmi, Thiago Lopes Martins, Pietro Pasqual Silva, Rafael Tudela Rizental | | |
| **Vínculos** | `RF-03` · `RF-04` · `RF-05` · `RF-19` · `RF-20` · `RNF-05` · `RNF-08 (v1)` · `RNF-09` · `RB-08` · `RB-11` · `STY017 (RN01–RN04)` · `STY046` · `STY047` · `STY048` · `D1 da Matriz CSD` · `BPMN P1` · `ADR-06` · `ADR-08` · `ADR-10` · `ADR-11` · `ADR-12` · `ADR-21` · `ADR-27` | | |

---

## 1. Contexto *(obrigatória)*
O diferencial central de usabilidade e catalogação da plataforma Steely é o **Scanner IA** (`RF-03`, `RF-04`, `STY017`), que permite ao vendedor fotografar um componente de hardware usado e obter o preenchimento automático da categoria, fabricante, linha/arquitetura, modelo exato (`SKU`), especificações técnicas e estimativa de estado aparente de conservação (incluindo a distinção obrigatória entre `"PC Montado"` e `"Peça Avulsa"` do `RF-19`), em troca de incentivo em moedas virtuais (`RB-08`, `ADR-10`). Além disso, o motor de visão computacional apoia a detecção de suspeita de dano visual para proteção da garantia (`RB-11`, `ADR-06`) e alimenta o pipeline de aprendizado contínuo (`RNF-09`) junto ao **Hardware Captcha** (`RF-20`, `STY046`), à extração anonimizada de datasets (`STY047`) e à promoção governada de versões de modelo (`STY048`).

O domínio de hardware usado impõe desafios severos que inviabilizam classificadores convencionais:
1. **Ambiguidade Visual Intra-Classe (*Placas Gêmeas*):** Modelos distintos de um mesmo fabricante frequentemente compartilham exatamente a mesma carcaça, PCB e dissipador (ex.: *ASUS Dual RTX 3060* vs. *RTX 3060 Ti*, ou *AMD Ryzen 5 5600X* vs. *5800X*), diferenciando-se apenas pelo código impresso na etiqueta ou gravado a laser no *heatspreader* (`IHS`);
2. **Natureza *Open-Set* do Catálogo:** Novos modelos de GPUs, CPUs, placas-mãe e memórias são lançados ou cadastrados continuamente (`STY017-RN04`); não é viável retreinar toda a rede neural do zero a cada novo SKU adicionado ao catálogo;
3. **Restrições Estritas de Custo Zero, Latência e Memória (`TAP`, `RNF-05`, `ADR-08`):** O projeto tem orçamento de `R$ 0,00`, latência máxima de `<= 4,0 s` (meta sub-2s na inferência) e o backend principal **FastAPI** roda no **Render Free (512 MB de RAM)**, exigindo que o carregamento dos modelos pesados não provoque *Out-Of-Memory (OOM)* na API transacional.

## 2. Direcionadores da decisão *(recomendada)*
* **Reconhecimento *Coarse-to-Fine* e *Open-Set* sem Retreino Completo (`RF-04`, `RF-19`, `STY017-RN04`):** Combinar classificação hierárquica consistente (`L0` a `L4`) com busca métrica vetorial (`L5`) e leitura óptica de etiquetas (`OCR`), permitindo adicionar novos SKUs apenas inserindo seu vetor no índice.
* **Custo Zero e Isolamento de Memória frente ao Render Free (`TAP`, `ADR-08`):** Operar com modelos próprios exportados para **ONNX (`INT8`/`FP16`)** sem pagar APIs comerciais por chamada, isolando o worker pesado em infraestrutura gratuita de maior RAM (**Hugging Face Spaces Free — 2 vCPU / 16 GB RAM** ou host local na defesa).
* **Latência Otimizada (`<= 4,0 s`) e Privacidade (`RNF-05`, `LGPD`, `STY047`):** Garantir inferência rápida com *Circuit Breaker* (`ADR-12`) e treinar apenas sobre imagens sem `EXIF`/`GPS` (`ADR-11`) e com consentimento válido (`STY047-RN01/RN02`).
* **Governança e Evolução Contínua (`RNF-09`, `STY046`, `STY048`):** Aproveitar a rotulagem colaborativa do Hardware Captcha e promover novas versões gradualmente com *rollback* automático em caso de degradação ou viés.

## 3. Opções consideradas *(obrigatória)*

| Aspecto | Opção A — API Comercial Externa de Visão / LLM Multimodal (GPT-4o Vision / Gemini Pro Vision / Rekognition) | Opção B — Classificador CNN Monolítico Fechado Embutido no Processo do Render Free (ResNet/MobileNet Softmax) | Opção C — Pipeline Proprietário Multimodal Híbrido em 4 Estágios (ONNX Runtime INT8 + FAISS) com Worker Isolado em Hugging Face Spaces Free + Ciclo MLOps |
| :--- | :--- | :--- | :--- |
| **Descrição** | Enviar cada foto do vendedor para uma API paga de nuvem para identificar o hardware via prompt multimodal. | Treinar uma única rede convolucional com saída *Softmax* fixa sobre `N` classes e carregá-la diretamente dentro do container de 512 MB do FastAPI no Render Free. | Arquitetura proprietária em **4 estágios ONNX (`INT8`)**: (1) Detecção de ROI (`YOLOv11s`); (2) Classificação Hierárquica `L0–L4` (`ConvNeXt-Small`/`SigLIP`); (3) Busca *Open-Set* `L5` (`ArcFace` 512-D + `FAISS`); e (4) OCR de etiqueta (`PaddleOCR PP-OCRv4`), servida por um **Inference Worker em Hugging Face Spaces Free (16 GB RAM)** chamado pelo FastAPI. |
| **Prós** | • Sem necessidade de treinar modelos próprios inicialmente. | • Pipeline único simples para poucas classes fixas. | • **Resolve placas gêmeas e *Open-Set*:** une visão global, métrica `FAISS` e `OCR` da etiqueta.<br>• **Custo R$ 0 e zero OOM no Render:** usa os 16 GB de RAM gratuitos do HF Spaces.<br>• **Atende 100% a `STY017`, `STY046`, `STY047` e `STY048`.** |
| **Contras** | • **Inviável:** custo financeiro por imagem (viola o `TAP`), latência de rede instável (`> 4s`), envio de fotos a terceiros (`LGPD`) e alucinação de SKUs técnicos. | • **Inviável:** estoura os 512 MB de RAM do Render Free (`OOM`), confunde placas gêmeas sem ler a etiqueta e exige retreinar a rede inteira a cada novo SKU (`STY017-RN04`). | • Exige sincronizar o índice `FAISS` e os artefatos `.onnx` versionados entre o repositório de modelos e o worker de inferência. |

## 4. Decisão *(obrigatória)*
**Opção escolhida:** ☐ A ☐ B ☒ **C**

Fica decidida a adoção do **Pipeline Proprietário Multimodal Híbrido em 4 Estágios sobre ONNX Runtime (`INT8`/`FP16`) e `FAISS`, com Worker Isolado e Ciclo Completo de Active Learning (`STY017`, `STY046–STY048`)**:

1. **Arquitetura dos 4 Estágios do Motor de Visão Computacional (Complementada pelo `ADR-12`):**
   * **Estágio 1 — Detecção de ROI e Sub-Regiões (`YOLOv11s` / `RT-DETR` em ONNX):** Localiza e recorta o corpo físico do hardware (`>= 15%` da área da foto), a **etiqueta de identificação/S/N** e sub-regiões críticas (soquetes LGA/PGA, conectores PCIe, trilhas e capacitores), eliminando o ruído de fundo e gerando os recortes para inspeção de estado aparente e suporte à `RB-11` (`ADR-06`).
   * **Estágio 2 — Classificação Multi-Tarefa Hierárquica `L0–L4` (`ConvNeXt-Small` / `SigLIP-Base` via `timm`):** Prediz simultaneamente:
     * `Head 0`: Filtro binário obrigatório **`"PC Montado"` vs. `"Peça Avulsa"`** (`RF-19`);
     * `Head L1` (Categoria: GPU, CPU, Placa-Mãe, RAM, Armazenamento, Fonte) $\rightarrow$ `Head L2` (Fabricante) $\rightarrow$ `Head L3` (Soquete/Arquitetura/Geração) $\rightarrow$ `Head L4` (Série/Tier), aplicando máscara de consistência hierárquica (impedindo combinações inválidas como `Intel + AM5`).
   * **Estágio 3 — Verificação *Open-Set* em Nível de SKU `L5` (`ArcFace` 512-D + `FAISS`):** Uma cabeça de *Deep Metric Learning* projeta o recorte visual em um vetor normalizado de **512 dimensões** e consulta via similaridade de cosseno (`k-NN` no índice **`FAISS`** em memória, filtrado pelo subespaço `L1–L4`) os centroides dos SKUs cadastrados. Quando um hardware inédito passa pela curadoria (`STY017-RN04`), basta adicionar seu vetor 512-D ao `FAISS` sem retreinar a rede.
   * **Estágio 4 — Leitura de Etiqueta e IHS (`PaddleOCR PP-OCRv4` + *Fuzzy Token Matching*):** Executa OCR leve sobre o recorte da etiqueta/IHS e aplica correspondência difusa (*Levenshtein/Jaro-Winkler*) contra os *Part Numbers* candidatos, desempatando placas visualmente gêmeas e entregando o escore composto `S_final` para as 3 faixas de decisão do **`ADR-12`** (`>= 80%` Auto L5, `50%–79%` Top-3 Hipóteses, `< 50%` Fallback Manual).
2. **Topologia de Execução Híbrida para Respeitar os 512 MB do Render Free (`ADR-08`, `RNF-05`):**
   * **No FastAPI Principal (Render Free — 512 MB RAM):** Executa a sanitização de `EXIF`/`WebP` (`Pillow` — `ADR-11`), a validação rápida de foco/nitidez (variância do Laplaciano — `< 50 ms`) e o **Circuit Breaker** (`timeout` de `3,5 s` — `ADR-12`).
   * **No Inference Worker Isolado (Hugging Face Spaces Free — 2 vCPU / 16 GB RAM com Docker FastAPI/ONNX, ou container local na máquina da banca):** Mantém carregados em RAM os modelos quantizados em **`ONNX INT8`** e o índice **`FAISS`**, respondendo às chamadas internas do FastAPI (autenticadas via `X-Internal-Token`) em **`< 1,5 s`** (cumprindo com folga o teto de `<= 4,0 s` do `RNF-05` sem risco de *OOM* no Render).
3. **Ciclo de Retroalimentação, Hardware Captcha e Governança de Modelos (`RNF-09`, `STY046`, `STY047`, `STY048`):**
   * **Hardware Captcha (`RF-20`, `STY046`):** Combina imagens de controle (já validadas) com recortes pendentes de rotulagem de estado aparente/conectores. A aprovação nos itens de controle valida o humano, registra o voto nos itens pendentes e credita moedas (`ADR-10`); após **3 falhas consecutivas**, faz fallback para o **Cloudflare Turnstile** (`STY046-RN03`, `ADR-21`). Divergências entre usuários vão para curadoria (`STY046-RN04`).
   * **Recolhimento Anonimizado (`STY047`):** A exportação de datasets para retreino exige base legal e consentimento ativo (`STY047-RN01/RN02`), exclui imediatamente titulares que revogaram consentimento (`STY047-RN04`), consome apenas imagens já sem `EXIF`/`GPS` (`ADR-11`/`STY047-RN03`) e grava hash do dataset em `audit.system_and_access_logs` (`ADR-05`).
   * **Promoção Gradual e Rollback Automático (`STY048`):** Novas versões `.onnx` são avaliadas contra o conjunto de teste padrão (`STY048-RN01`), retidas se houver viés por categoria (`STY048-RN04`), implantadas por percentual gradual de tráfego (*canary* — `STY048-RN02`) e revertidas automaticamente para o `.onnx` anterior se a latência ou acurácia degradarem em produção (`STY048-RN03`).

## 5. Consequências *(obrigatória)*
* **Positivas:**
  * Une precisão fina em SKUs gêmeos (`YOLO + ConvNeXt/SigLIP + ArcFace/FAISS + PaddleOCR`) com capacidade *Open-Set* instantânea (inclusão de novos SKUs no `FAISS` sem retreino).
  * Protege o Render Free (512 MB) contra estouro de memória ao isolar os pesos ONNX nos 16 GB de RAM gratuitos do Hugging Face Spaces (com *Circuit Breaker* no FastAPI caso o worker oscile).
  * Fecha ponta a ponta os casos de uso `STY017`, `STY046`, `STY047` e `STY048` com auditoria (`ADR-05`) e privacidade (`LGPD`).
* **Negativas ou riscos aceitos:**
  * A execução em CPU (`ONNX INT8`) no plano gratuito tem latência entre `800 ms` e `1,8 s` por imagem (dentro dos `<= 4,0 s` do `RNF-05`, mas superior a uma GPU dedicada TensorRT).
* **O que muda no código, no banco, na arquitetura e nos diagramas:**
  * Tabelas `ml_model_versions` (controle canário e rollback do `STY048`), `ml_curation_queue` (`STY017-RN04`, `STY046-RN04`) e `ml_training_datasets` (`STY047`) no PostgreSQL Core (`ADR-08`); serviço `ScannerInferenceClient` no FastAPI conectando ao worker ONNX.

## 6. Validação *(recomendada)*
* **Teste de Latência e Precisão Multi-Estágio (`RNF-05`, `STY017`):** Submeter foto de placa de vídeo com etiqueta visível $\rightarrow$ validar detecção de ROI, classificação `L0–L4`, busca `FAISS L5` + `OCR` e retorno completo em `< 2,0 s` (limite máximo `<= 4,0 s`).
* **Teste de *Open-Set* (`FAISS`) e Rollback (`STY048`):** Inserir novo vetor 512-D no índice `FAISS` sem reiniciar o treino e comprovar reconhecimento imediato; simular degradação na versão candidata e comprovar reversão automática para a versão anterior registrada em `audit.system_and_access_logs`.

## 7. Plano de implementação *(recomendada)*
1. **Exportar pipeline (`YOLOv11s` + `ConvNeXt/SigLIP L0–L4` + `ArcFace` + `PaddleOCR`) para `ONNX INT8` e montar índice `FAISS`:** Fabrício — *Sprint 8 (15–16)*.
2. **Publicar o Inference Worker no Hugging Face Spaces (Docker) e integrar `POST /api/v1/scanner/analyze` no FastAPI (`ADR-12`):** Fabrício e Thiago — *Sprint 8–9 (16)*.
3. **Implementar endpoints e tabelas do Hardware Captcha (`STY046`), extração anonimizada (`STY047`) e promoção/rollback (`STY048`):** Fabrício, Augusto e Pietro — *Sprint 9 (16–17)*.

## 8. Referências *(recomendada)*
* Documento de Requisitos v2.0 (`RF-03`, `RF-04`, `RF-05`, `RF-19`, `RF-20`, `RNF-05`, `RNF-09`) e v1 (`RNF-08`).
* Especificação de Casos de Uso e Regras de Negócio (`STY017`, `STY046`, `STY047`, `STY048`, `RB-08`, `RB-11`, `BPMN P1`).
* Artigos base: Deng et al. (*ArcFace: Additive Angular Margin Loss*), Johnson et al. (*FAISS*), ONNX Runtime Quantization Docs.
* ADRs relacionados: `ADR-05`, `ADR-06`, `ADR-08`, `ADR-10`, `ADR-11`, `ADR-12`, `ADR-21`, `ADR-27`.

---

### Histórico de revisões
| Versão | Data | Autor | Alteração |
| :--- | :--- | :--- | :--- |
| 1.0 | 01/11/2026 | Fabrício Notoya Thomas | Definição da arquitetura híbrida em 4 estágios (YOLO + ConvNeXt/SigLIP + ArcFace/FAISS + PaddleOCR em ONNX INT8), worker isolado em HF Spaces Free e governança MLOps (`STY046–048`). |
