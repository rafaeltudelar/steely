# ADR-12 — Limiar de confiança do Scanner
*Architecture Decision Record · Projeto Steely · Escola de TI · UniCesumar*

| Campo | Valor | Campo | Valor |
| :--- | :--- | :--- | :--- |
| **Status** | ☒ Proposto ☐ Aceito ☐ Rejeitado ☐ Substituído pelo ADR-___ | **Data** | 01/11/2026 |
| **Responsável** | Fabrício Notoya Thomas | **Sprint** | Sprint 8–9 (15–17) |
| **Participantes** | Fabrício Notoya Thomas, Augusto Palma Guglielmi, Thiago Lopes Martins, Pietro Pasqual Silva, Rafael Tudela Rizental | | |
| **Vínculos** | `RNF-05` · `RNF-08 (v1)` · `RNF-09` · `D1 da Matriz CSD` · `RF-05` · `RF-19` · `RB-08` · `STY017-RN01/RN02/RN03/RN04` · `BPMN P1` · `ADR-01` · `ADR-04` · `ADR-06` · `ADR-10` · `ADR-27` | | |

---

## 1. Contexto *(obrigatória)*
Em complemento ao `ADR-01`, o **Scanner IA** do Steely utiliza uma arquitetura proprietária **Multimodal Híbrida em Múltiplos Estágios** servida via **ONNX Runtime / TensorRT dentro do ecossistema Python (FastAPI)**, composta por:
1. **Detecção e Recorte de Região de Interesse (`YOLOv11s` / `RT-DETR`):** isola o corpo físico do componente, a etiqueta de identificação/código de barras e sub-regiões sensíveis (soquetes de CPU, pinos PGA, conectores PCIe), eliminando a bagunça de fundo;
2. **Classificação Multi-Tarefa Hierárquica (`ConvNeXt-Small` / `SigLIP-Base` via `timm`):** prediz simultaneamente da camada `L0` à `L4` (`Head 0`: PC Montado vs. Peça Avulsa conforme `RF-19`; `Head L1`: Categoria; `Head L2`: Marca/Fabricante; `Head L3`: Arquitetura/Soquete/Série; `Head L4`: Linha/Tier), aplicando restrições de consistência hierárquica (impedindo combinações contraditórias como `Marca: Intel + Soquete: AM5`);
3. **Verificação *Open-Set* via *Deep Metric Learning* (`ArcFace` 512-D + `FAISS`):** projeta os atributos visuais em um espaço de embeddings normalizado de 512 dimensões e busca por similaridade de cosseno (`k-NN` no `FAISS`) contra os centroides de SKUs exatos (`L5`) do catálogo, evitando retreinar a rede inteira a cada lançamento de hardware;
4. **Reconhecimento Óptico de Caracteres (`PaddleOCR PP-OCRv4`) + *Fuzzy Token Matching*:** lê códigos gravados na etiqueta ou no *heatspreader* (IHS) para desempatar placas visualmente gêmeas que compartilham a mesma carcaça/PCB (ex.: *ASUS Dual RTX 3060* vs. *RTX 3060 Ti*, ou *Ryzen 5 5600X* vs. *5800X*).

Para resolver a dúvida `D1 da Matriz CSD` e cumprir `STY017-RN02/RN03/RN04`, `RNF-05` e o fluxo `BPMN P1`, é necessário definir: (a) o limiar numérico mínimo de confiança para preenchimento automático; (b) quando degradar graciosamente para as **até 3 hipóteses (`Top-3`)** de escolha manual; (c) a regra de concessão de moedas em cada caminho; e (d) o mecanismo de *fallback* quando a imagem ou a inferência falham.

## 2. Direcionadores da decisão *(recomendada)*
* **Precisão de Catálogo e Prevenção de Disputas (`RF-05`, `RF-13`, `D1 da Matriz CSD`):** Garantir que SKUs visualmente gêmeos (`L5`) só sejam preenchidos de forma 100% automática quando a similaridade vetorial (`ArcFace`/`FAISS`) e o OCR/hierarquia tiverem alta certeza.
* **Degradação Graciosa e Aproveitamento da Inferência (`STY017-RN03`, `BPMN P1`):** Quando a etiqueta estiver parcialmente ilegível mas o modelo souber a linha/série (`L3`/`L4`), apresentar os **Top-3 candidatos do `FAISS`** para escolha manual com 1 clique em vez de obrigar o usuário a digitar tudo do zero.
* **Latência Estrita e Resiliência (`RNF-05`):** Garantir execução total da esteira em `<= 4,0 segundos` (com inferência local/ONNX sub-2 segundos), desviando imediatamente via *Circuit Breaker* para preenchimento manual em caso de falha ou sobrecarga.

## 3. Opções consideradas *(obrigatória)*

| Aspecto | Opção A — Corte Binário Único (Aceita ou Descarta tudo em 75%) | Opção B — Pipeline em 3 Faixas de Confiança (`>= 80%` Auto L5, `50%–79%` Top-3 Hipóteses via FAISS/Hierarquia, `< 50%` Fallback Manual + Curadoria) com Gate de Qualidade e Circuit Breaker | Opção C — Softmax Fixo sem Verificação Open-Set e sem Limite de Tempo |
| :--- | :--- | :--- | :--- |
| **Descrição** | Aplicar um único limiar de `0.75`: se atingir, autopreenche; se ficar abaixo, descarta toda a inferência das cabeças `L0–L4` e dos vizinhos do `FAISS`, forçando digitação manual completa. | Operar em **4 estágios alinhados ao `BPMN P1` e à arquitetura híbrida do modelo:**<br>1. *Pré-validação de Qualidade (`STY017-RN02`);*<br>2. *Faixa Alta (`score >= 0.80`):* autopreenchimento completo até o SKU `L5`;<br>3. *Faixa Intermediária (`0.50 <= score < 0.80`):* recuo gracioso usando os `Top-3` centroides do `FAISS` compatíveis com `L1–L4` para escolha manual;<br>4. *Faixa Baixa (`score < 0.50` / Open-Set desconhecido / Timeout `> 3,5 s`):* fallback para preenchimento manual e envio para curadoria (`STY017-RN04`). | Usar classificador fechado tradicional sem busca métrica e sem *Circuit Breaker*, aguardando processamento por tempo indeterminado. |
| **Prós** | • Implementação simples na interface. | • **Atende integralmente ao `STY017-RN01..04`, `RNF-05` e `BPMN P1`.**<br>• Explora a natureza *Coarse-to-Fine* (`L0–L4` + `ArcFace L5` + `PaddleOCR`) do modelo proprietário.<br>• Alimenta o retreino contínuo (`RNF-09`) sempre que o vendedor escolhe uma das 3 hipóteses. | • Nenhuma lógica de seleção de hipóteses na interface. |
| **Contras** | • **Viola `STY017-RN03` e `BPMN P1`** (que exigem exibir até 3 hipóteses para escolha manual).<br>• Desperdiça a classificação correta de `L1–L4` quando apenas o SKU final `L5` tem dúvida entre 2 ou 3 modelos gêmeos. | • Exige que o FastAPI retorne a lista ordenada de até 3 candidatos (`candidates: Top-3`) junto às especificações do catálogo. | • **Viola `RNF-05` e `STY017-RN04`:** alucina classes erradas para hardwares novos fora do catálogo e trava o cadastro em caso de lentidão. |

## 4. Decisão *(obrigatória)*
**Opção escolhida:** ☐ A ☒ **B** ☐ C

Fica definida a regra de decisão do **Scanner IA** em **4 estágios determinísticos**, integrados ao serviço de inferência **ONNX Runtime no FastAPI**:

### 1. Estágio 0 — Gate de Qualidade da Imagem e Detecção de ROI (`STY017-RN01/RN02`, `ADR-27`)
* Exige ao menos 1 fotografia (`<= 2 MB`). Antes de rodar o backbone completo, valida nitidez (variância do Laplaciano para detectar *motion blur*), exposição/iluminação (evitando estouro de reflexo especular em dissipadores metálicos) e se o detector **`YOLOv11s` / `RT-DETR`** localizou uma *bounding box* válida de hardware com área mínima (`>= 15%` do quadro).
* **Ação se reprovada:** Retorna imediatamente (`< 150 ms`) o status `LOW_QUALITY_RECAPTURE`, orientando o vendedor a recapturar a foto com melhor enquadramento/iluminação ou seguir para o preenchimento manual (`BPMN P1`).

### 2. Cálculo do Escore de Confiança Composto (`S_final`)
* Para cada candidato retornado pela busca de vizinhos mais próximos no **`FAISS`** (espaço `ArcFace` 512-D), o escore de confiança combina:
  * A probabilidade hierárquica consistente das cabeças **`L0–L4`** (`ConvNeXt-Small` / `SigLIP-Base`);
  * A similaridade de cosseno no espaço **`ArcFace` (`L5`)**;
  * O bônus/confirmação de *token matching* do **`PaddleOCR`** sobre o *Part Number* lido na etiqueta ou IHS.

### 3. Limiares de Decisão e Regras de Moedas (`STY017-RN03/RN04`, `BPMN P1`, `ADR-10`)
* **Faixa Verde — Alta Confiança (`S_final >= 0.80`):**
  * **Comportamento:** O sistema preenche automaticamente todos os campos técnicos do SKU `L5` vencedor (incluindo a classificação inicial `Head 0`: *PC Montado* vs. *Peça Avulsa* — `RF-19`) e aplica o selo `"Identificado por IA"` (`RF-05`).
  * **Moedas (`RB-08`):** Concede **100% do crédito de moedas do Scanner IA** após a validação e publicação da oferta (`BPMN P1`).
* **Faixa Amarela — Confiança Intermediária / Desambiguação (`0.50 <= S_final < 0.80`):**
  * **Comportamento (`STY017-RN03`):** Ocorre tipicamente quando o componente é identificado até a linha/arquitetura (`L3`/`L4`), mas há dúvida entre SKUs visualmente gêmeos (`L5`). O sistema apresenta **até 3 hipóteses mais prováveis (`Top-3` do `FAISS` que possuam `score >= 0.25` cada)** para escolha manual do vendedor com 1 clique.
  * **Moedas e *Active Learning* (`BPMN P1` — seta `"escolha"`):** Se o vendedor selecionar uma das 3 hipóteses apresentadas pela IA, os dados técnicos do catálogo são preenchidos automaticamente, o par `(imagem, sku_escolhido)` é salvo como *feedback* supervisionado de alta qualidade (`STY017` passo 7) e **o vendedor recebe normalmente as moedas de incentivo do Scanner IA** (`RB-08`). Caso clique em *"Nenhuma das opções — preencher manualmente"*, segue para a Faixa Vermelha.
* **Faixa Vermelha — Baixa Confiança ou *Open-Set Rejection* (`S_final < 0.50` — `STY017-RN04`):**
  * **Comportamento:** Quando a distância de cosseno no `FAISS` indica um componente inédito ainda não cadastrado no catálogo (*open-set*) ou foto inconclusiva, o sistema redireciona para o **Preenchimento Manual** (pré-preenchendo apenas a categoria `L1` se `L1 >= 0.70`), atribui o selo `"Preenchimento Manual"` e envia o registro para a **Fila de Curadoria Administrativa de IA** (`STY017-RN04`, `RF-22`) para futura inclusão do novo centroide no `FAISS`.
  * **Moedas (`BPMN P1`):** No preenchimento manual após falha/baixa confiança da IA, **não há concessão de moedas do Scanner** (evitando que usuários enviem fotos aleatórias apenas para ganhar moedas digitando manualmente).

### 4. Fallback de Indisponibilidade e *Circuit Breaker* (`RNF-05`, `STY017` Fluxo Alternativo 4)
* **Timeout de Inferência:** A execução do pipeline ONNX Runtime no FastAPI possui *timeout* estrito de **3,5 segundos** (respeitando o teto total de `<= 4,0 s` do `RNF-05` e a meta sub-2s do `RNF-08`).
* **Circuit Breaker:** Após **3 timeouts ou erros consecutivos de inferência** em uma janela de 60 segundos, o *Circuit Breaker* abre por **60 segundos**, retornando instantaneamente (`< 50 ms`) o fallback de preenchimento manual sem travar a tela do vendedor.

## 5. Consequências *(obrigatória)*
* **Positivas:**
  * Responde integralmente à `D1 da Matriz CSD`, alinhando a arquitetura real de Machine Learning (`YOLOv11s` + `ConvNeXt/SigLIP L0–L4` + `ArcFace/FAISS L5` + `PaddleOCR`) às regras de negócio do `BPMN P1`.
  * Graças ao *Deep Metric Learning* (`ArcFace` + `FAISS`), quando um novo componente aprovado na curadoria (`STY017-RN04`) entra no catálogo, basta inserir seu vetor de 512 dimensões no índice `FAISS` sem precisar retreinar os pesos da rede neural inteira.
  * Impede fraudes de ganho de moedas no modo manual, mas recompensa justamente o usuário que ajuda a desempatar as 3 hipóteses da IA.
* **Negativas ou riscos aceitos:**
  * Caso o vendedor altere manualmente o Fabricante ou Modelo principal após uma identificação automática, o anúncio perde o selo `"Identificado por IA"` e passa a exibir `"Preenchimento Manual"`.
* **O que muda no código, no banco, na arquitetura e nos diagramas:**
  * Padronização do contrato `POST /api/v1/scanner/analyze` no FastAPI retornando `decision_band` (`AUTO_L5`, `TOP3_HYPOTHESES`, `MANUAL_CURATION`, `LOW_QUALITY_RECAPTURE` ou `CIRCUIT_OPEN_FALLBACK`), a árvore predita `L0–L4` e a lista `candidates` (até 3 SKUs do `FAISS`).

## 6. Validação *(recomendada)*
* **Critérios de Aceite e Demonstração na Defesa:**
  1. **Caso `>= 80%` (Auto L5):** Foto nítida com etiqueta legível $\rightarrow$ autopreenchimento em `< 2,0 s`, selo `"Identificado por IA"` e crédito de moedas elegível;
  2. **Caso `50%–79%` (Top-3 Hipóteses):** Foto de placa gêmea sem etiqueta nítida $\rightarrow$ exibição das até 3 hipóteses do `FAISS`, preenchimento ao clicar em uma delas e concessão das moedas;
  3. **Caso `< 50%` (Fallback + Curadoria):** Componente fora do catálogo $\rightarrow$ redirecionamento para preenchimento manual (sem moedas do Scanner) e criação de item na fila de curadoria administrativa (`RF-22`);
  4. **Caso Qualidade Ruim / Timeout:** Foto borrada ou simulação de falha do worker ONNX $\rightarrow$ orientação de recaptura ou abertura do *Circuit Breaker* em `<= 3,5 s`.

## 7. Plano de implementação *(recomendada)*
1. **Exportar os pesos do pipeline (`YOLOv11s` + Backbone Hierárquico `L0–L4` + `ArcFace` + índice `FAISS`) para execução via ONNX Runtime no FastAPI:** Fabrício — *Sprint 8*.
2. **Implementar a lógica dos limiares (`0.80` e `0.50`), o *Fuzzy Matching* com `PaddleOCR` e o *Circuit Breaker* (`3,5 s`):** Fabrício — *Sprint 8/9*.
3. **Integrar os estados de retorno (Auto, Modal de 3 Hipóteses, Recaptura e Fallback Manual) no Web e Mobile:** Pietro e Rafael — *Sprint 9*.

## 8. Referências *(recomendada)*
* Documento de Requisitos v2.0 (`RF-05`, `RF-19`, `RF-22`, `RNF-05`, `RNF-09`) e v1 (`RNF-08`).
* Especificação de Casos de Uso e Regras de Negócio (`STY017-RN01` a `RN04`, `RB-08`).
* Diagrama de Fluxo BPMN (`Diagrama de Fluxo BPMN.pdf` — Página 2: `P1 - Publicação e triagem técnica do hardware`).
* ADRs relacionados: `ADR-01`, `ADR-04`, `ADR-06`, `ADR-10`, `ADR-11`, `ADR-27`.

---

### Histórico de revisões
| Versão | Data | Autor | Alteração |
| :--- | :--- | :--- | :--- |
| 1.0 | 31/10/2026 | Fabrício Notoya Thomas | Definição dos limiares (80%/50%), integração com a arquitetura multimodal híbrida (YOLO + L0-L4 + ArcFace/FAISS + OCR) e regras de fallback/moedas. |
| 1.1 | 01/11/2026 | Fabrício Notoya Thomas | Alinhamento com `ADR-04` (hierarquia `L1–L5` usada no escalonamento de agregação do DaaS), `ADR-06` (laudo do Scanner como insumo objetivo na rubrica de arbitragem) e `ADR-27` (`Estágio 0` e bandas de retorno). |
