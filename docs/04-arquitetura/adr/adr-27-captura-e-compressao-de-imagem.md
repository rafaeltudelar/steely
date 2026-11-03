# ADR-27 — Captura e compressão de imagem
**Architecture Decision Record · Projeto Steely · Escola de TI · UniCesumar**

| Campo | Valor | Campo | Valor |
| --- | --- | --- | --- |
| **Status** | ☒ Proposto  ☐ Aceito  ☐ Rejeitado  ☐ Substituído pelo ADR-___ | **Data** | 01/11/2026 |
| **Responsável** | Rafael Tudela Rizental | **Sprint** | 8 e 9 |
| **Participantes** | Augusto Palma Guglielmi, Fabrício Notoya Thomas, Pietro Pasqual Silva, Rafael Tudela Rizental, Thiago Lopes Martins | | |
| **Vínculos** | RNF-05, STY017 · ADR-11 · ADR-12 · ADR-13 · ADR-17 · ADR-23 | | |

## 1. Contexto *(obrigatória)*

A story STY017 (Scanner IA) permite que o vendedor fotografe peças de hardware para anúncio no marketplace Steely. O fluxo envolve:

•  Captura de imagem — O uso do scanner requer ao menos uma imagem do item (STY017-RN01), capturada pela câmera ou escolhida na galeria do dispositivo.

•  Validação de qualidade — Imagens de baixa qualidade (desfoque, enquadramento ou iluminação inadequados) são rejeitadas, com orientação para nova captura (STY017-RN02).

•  Limite de tamanho — O RNF-05 (Compatibilidade de mídia) exige que as imagens enviadas não excedam 2 MB, para garantir upload rápido mesmo em conexões móveis lentas.

•  Limites de imagem do anúncio — As imagens têm formato, tamanho e quantidade limitados, e os metadados de localização são removidos automaticamente (STY016-RN02); o ADR-11 fixa até 6 fotos por oferta.

Pelo ADR-11, o app envia a imagem pré-comprimida (≤ 2 MB, JPEG) ao FastAPI sob /api/v1 (ADR-13); o cliente não escreve direto no Supabase. No servidor, a biblioteca Pillow faz o expurgo completo de EXIF/GPS, a conversão para WebP, o salvamento no bucket público offers-media e o cálculo do imagehash anti-duplicidade, e o Scanner IA roda seus 4 estágios em ONNX Runtime (ADR-12).

O problema é definir a captura e a compressão no cliente até 2 MB e como orientar a recaptura quando a imagem não atender aos critérios mínimos.

## 2. Direcionadores da decisão *(recomendada)*

•  RNF-05 — Compatibilidade de mídia — Imagens comprimidas a ≤ 2 MB antes do upload para garantir velocidade em conexões móveis.

•  STY017-RN01 — Ao menos uma imagem — O uso do scanner requer ao menos uma imagem do item, com resolução suficiente para identificar a peça.

•  STY017-RN02 — Qualidade e orientação de recaptura — Imagens de baixa qualidade são rejeitadas, com orientação para nova captura (ex: "Imagem escura, tente com mais luz").

•  STY016-RN02 — Limites de imagem — Formato, tamanho e quantidade de imagens limitados e remoção automática dos metadados de localização.

•  Pipeline do servidor (ADR-11, ADR-12) — O FastAPI faz expurgo de EXIF/GPS, conversão para WebP, imagehash e Scanner IA; o cliente não acessa o Supabase Storage diretamente.

•  Desempenho em aparelhos simples — A validação no cliente precisa ser instantânea e não pode travar celulares Android de 2 GB de RAM.

•  Base nativa do app — O app já roda como Development Build (ADR-23); a preferência é por pacotes oficiais do Expo SDK, sem novos plugins nativos.

## 3. Opções consideradas *(obrigatória)*

| Opção A — expo-image-manipulator | Opção B — react-native-image-resizer | Opção C — sharp (server-side) |
| --- | --- | --- |
| Descrição<br>Pacote oficial do Expo SDK que redimensiona e comprime imagens no dispositivo (compress de 0,0 a 1,0; saída JPEG, PNG ou WebP), usado com expo-image-picker para a captura.<br>Prós<br>•  Pacote oficial do Expo, sem novos plugins nativos além do Development Build (ADR-23)<br>•  Envia arquivos ≤ 2 MB e economiza dados<br>•  Permite validar resolução, proporção e tamanho antes do upload<br>Contras<br>•  API antiga (manipulateAsync) obsoleta; exige usar a API contextual atual<br>•  Consome CPU e memória em aparelhos de baixo desempenho | Descrição<br>Biblioteca da comunidade para redimensionar e comprimir imagens em React Native, com suporte a JPEG, PNG e WebP.<br>Prós<br>•  Saída em WebP<br>•  Controle granular de qualidade e formato<br>•  Processamento no cliente<br>Contras<br>•  Adiciona módulo nativo de terceiros ao build<br>•  Sem vantagem de formato: a Opção A também gera WebP | Descrição<br>Biblioteca Node.js de alto desempenho que processaria as imagens no servidor após receber o arquivo original.<br>Prós<br>•  Alta performance e saída em WebP/AVIF<br>•  Sem processamento no dispositivo<br>Contras<br>•  Upload do original (~5–15 MB) aumenta consumo de dados e latência<br>•  Não permite validação antes do upload<br>•  Exigiria um serviço Node.js à parte do backend Python (FastAPI) |

Comparativo por critério

| Critério | A — expo-image-manipulator | B — react-native-image-resizer | C — sharp (server-side) |
| --- | --- | --- | --- |
| Onde comprime | Cliente (dispositivo) | Cliente (dispositivo) | Servidor (serviço Node.js) |
| Manutenção do pacote | Oficial do Expo SDK | Biblioteca de terceiros | Biblioteca Node.js |
| Novos módulos nativos no build | Não | Sim | Não se aplica (servidor) |
| Compressão JPEG | compress (0.0–1.0) | quality (0–100) | quality + pipeline |
| Redimensionamento | resize (width/height) | width/height | resize (width/height) |
| Formato de saída | JPEG, PNG, WebP | JPEG, PNG, WebP | JPEG, PNG, WebP, AVIF |
| Consumo de dados no upload | Reduzido (envia ≤ 2 MB) | Reduzido (envia ≤ 2 MB) | Alto (envia original ~5–15 MB) |
| Validação antes do upload | Sim | Sim | Não |

## 4. Decisão *(obrigatória)*

Adotar expo-image-manipulator (Opção A) para redimensionar e comprimir as imagens no cliente, combinado com expo-image-picker para captura via câmera ou galeria. Ambos são pacotes oficiais do Expo SDK e não exigem adicionar novos plugins nativos além do Development Build já configurado (ADR-23).

A estratégia no cliente será:

1.  Captura — expo-image-picker com mediaTypes: ['images'] e quality: 0.8, até 6 fotos por oferta (ADR-11).

2.  Validação instantânea — Conferir resolução mínima, proporção entre 3:4 e 4:3, tamanho e os metadados de exposição/luminosidade da captura; se falhar, exibir o RecaptureGuidance antes de qualquer upload.

3.  Redimensionamento — Se a imagem exceder 1920 px no maior lado, redimensionar para 1920 px mantendo a proporção.

4.  Compressão JPEG — Usar a API atual do pacote (ImageManipulator.manipulate(uri).resize(...), depois renderAsync() e saveAsync({ compress: 0.7, format: SaveFormat.JPEG })), já que o manipulateAsync está obsoleto; se ainda passar de 2 MB, usar compress: 0.5; se ainda passar, redimensionar para 1280 px e comprimir de novo.

5.  Envio ao FastAPI — Enviar o JPEG ≤ 2 MB ao endpoint de mídia sob /api/v1 (ADR-11, ADR-13). O pacote também gera WebP, mas o app envia JPEG porque a Pillow recodifica toda imagem para WebP no servidor ao remover o EXIF (ADR-11).

No servidor (ADR-11, ADR-12), a Pillow faz o expurgo completo de EXIF/GPS (STY016-RN02, LGPD), converte para WebP e salva no bucket offers-media, calcula o imagehash anti-duplicidade e executa os 4 estágios do Scanner IA. A validação fina de foco e enquadramento da peça (STY017-RN02) é feita pelo Estágio 0 — Gate de Qualidade e ROI do ADR-12, que usa o detector YOLOv11s/RT-DETR, mede a nitidez e a exposição, exige que a peça ocupe ao menos 15% da imagem e responde em < 150 ms. O app trata a faixa devolvida em decision_band: LOW_QUALITY_RECAPTURE exibe o RecaptureGuidance; CIRCUIT_OPEN_FALLBACK (timeout de 3,5 s ou Circuit Breaker aberto) leva ao preenchimento manual. A confiança define o restante do fluxo: ≥ 80% preenchimento automático + moedas; 50%–79% Top-3 hipóteses; < 50% preenchimento manual.

Para vídeos de evidência de disputa (RF-13, bucket disputes-laudos), o limite do ADR-11 é de 30 segundos e 50 MB. O expo-image-picker limita a duração com videoMaxDuration: 30, mas no Android isso depende do app de câmera instalado, e o pacote não tem opção de tamanho máximo. Por isso o app confere o fileSize e a duração do vídeo antes do envio, e o FastAPI barra no servidor o que passar do limite (ADR-11).

A Opção B (react-native-image-resizer) foi descartada por acrescentar um módulo nativo de terceiros ao build sem vantagem sobre a Opção A, que também gera WebP. A Opção C (sharp server-side) foi descartada por transferir imagens originais de 5–15 MB pela rede, impedir a validação antes do upload e exigir um serviço Node.js à parte do backend Python (FastAPI).

## 5. Consequências *(obrigatória)*

Positivas

•  Economia de dados do usuário — Comprimir no cliente reduz o upload de ~8 MB (foto original de câmera 12 MP) para ≤ 2 MB, economia de ~75%.

•  Upload mais rápido — Arquivos menores melhoram a experiência especialmente em redes 3G/4G.

•  Pacotes oficiais do Expo — expo-image-manipulator e expo-image-picker não adicionam novos plugins nativos ao Development Build.

•  Feedback imediato — Problemas de resolução, proporção, tamanho e exposição são apontados na hora, antes do upload.

•  Privacidade e formato garantidos no servidor — O expurgo de EXIF/GPS e a conversão para WebP ficam centralizados na Pillow (ADR-11), sem depender do aparelho.

Negativas

•  Processamento no dispositivo — Redimensionar e comprimir consome CPU/memória; em aparelhos simples pode haver atraso de ~1–2 s por imagem. Mitigação: processar sequencialmente com indicador de progresso.

•  Perda de qualidade — compress: 0.7 gera artefatos em zoom máximo. Mitigação: o nível é suficiente para identificar a peça; números de série podem ir em foto separada com zoom.

•  Validação em duas etapas — Foco e enquadramento só são confirmados pelo Estágio 0 do ADR-12 no servidor, exigindo conexão. Mitigação: o Estágio 0 responde em < 150 ms e o RecaptureGuidance orienta a nova captura.

•  Limite do vídeo não garantido pelo picker — No Android, a duração máxima depende do app de câmera, e o tamanho não é limitado na captura. Mitigação: conferência de fileSize e duração no app e bloqueio no FastAPI (ADR-11).

## 6. Validação *(recomendada)*

| Cenário de teste | Resultado esperado | Critério de aceite |
| --- | --- | --- |
| Captura de foto com câmera 12 MP (≥ 8 MB original) | Arquivo enviado ≤ 2 MB após o pipeline de compressão | fileSize <= 2 * 1024 * 1024 bytes |
| Foto com resolução abaixo do mínimo | RecaptureGuidance exibido antes do upload | Nenhuma requisição enviada ao FastAPI |
| Proporção fora da faixa 3:4 a 4:3 | Alerta de recaptura: "Enquadramento inadequado — use proporção padrão" | Razão largura/altura entre 0,75 e 1,33 |
| Foto em ambiente escuro | Alerta de recaptura: "Iluminação insuficiente — tente em um local mais claro" | Exposição/luminosidade abaixo do limiar configurado |
| Foto desfocada ou sem a peça no quadro | Imagem rejeitada pelo Estágio 0 do ADR-12 no FastAPI e RecaptureGuidance exibido (STY017-RN02) | Resposta com decision_band: LOW_QUALITY_RECAPTURE em < 150 ms |
| Scanner indisponível ou lento | Circuit Breaker do ADR-12 abre e o app segue para o preenchimento manual | Resposta com decision_band: CIRCUIT_OPEN_FALLBACK, sem travar o anúncio |
| Upload de várias fotos (até 6 por oferta, ADR-11; STY016-RN02) | Todas as imagens processadas com sucesso | Arquivos em WebP no bucket offers-media, sem EXIF/GPS |
| Foto original > 10 MB | Pipeline completo: resize 1920 px → compress 0.7 → 0.5 → resize 1280 px se necessário | Arquivo enviado ≤ 2 MB |
| Dispositivo Android de 2 GB de RAM | Processamento completo em ≤ 3 s por imagem, sem travar | Tempo medido com performance.now() |
| Vídeo de disputa | Vídeo acima de 30 s ou 50 MB é barrado pelo app (fileSize e duração) e pelo FastAPI (ADR-11) | Vídeo acima do limite não é aceito |

## 7. Plano de implementação *(recomendada)*

| Etapa | Descrição | Responsável | Prazo |
| --- | --- | --- | --- |
| 1. Instalar dependências | npx expo install expo-image-manipulator expo-image-picker no Development Build do app | Fabrício Notoya Thomas | Sprint 8 — Semana 1 |
| 2. Criar módulo de compressão | Implementar src/services/imageCompressor.ts: resize (1920 px) → compress JPEG (0.7) → verificação ≤ 2 MB → fallback (0.5) → fallback resize (1280 px) | Fabrício Notoya Thomas | Sprint 8 — Semana 1 |
| 3. Criar validação no cliente | Implementar src/services/imageQualityValidator.ts com resolução mínima, proporção 3:4 a 4:3, tamanho e exposição/luminosidade | Rafael Tudela Rizental | Sprint 8 — Semana 1 |
| 4. Implementar UI de recaptura | Criar o componente RecaptureGuidance com mensagens por tipo de problema (resolução, enquadramento, luz e rejeição do Estágio 0) e botão de nova tentativa | Pietro Pasqual Silva | Sprint 8 — Semana 2 |
| 5. Integrar com fluxo de anúncio | Conectar captura, validação e compressão ao formulário de anúncio (STY017 Scanner IA), respeitando os limites da STY016-RN02 (até 6 fotos, ADR-11) | Rafael Tudela Rizental | Sprint 9 |
| 6. Integrar com o endpoint de mídia | Enviar as imagens ao FastAPI sob /api/v1 pelo cliente HTTP tipado (ADR-11, ADR-13) e tratar a resposta do Scanner IA (decision_band, confiança e motivo de rejeição — ADR-12) | Thiago Lopes Martins | Sprint 9 |
| 7. Indicador de progresso | Barra de progresso durante compressão e upload, com feedback por imagem | Pietro Pasqual Silva | Sprint 8 — Semana 3 |
| 8. Testes unitários e de integração | Testar o pipeline com imagens de diferentes tamanhos e condições e validar os cenários da Seção 6 (Jest e Maestro, ADR-17) | Augusto Palma Guglielmi | Sprint 8 — Semana 3 |
| 9. Teste em dispositivos reais | Validar desempenho em celulares Android de baixo custo (2 GB de RAM) | Fabrício Notoya Thomas | Sprint 8 — Semana 3 |

## 8. Referências *(recomendada)*

•  expo-image-manipulator — Documentação oficial: https://docs.expo.dev/versions/latest/sdk/imagemanipulator/

•  expo-image-picker — Documentação oficial: https://docs.expo.dev/versions/latest/sdk/imagepicker/

•  Pillow — Documentação oficial: https://pillow.readthedocs.io/

•  RNF-05 — Compatibilidade de mídia/upload: arquivos de imagem ≤ 2 MB (Matriz de Rastreabilidade v2)

•  STY017 — Scanner IA (Matriz de Rastreabilidade Steely v1)

–  STY017-RN01: O uso do scanner requer ao menos uma imagem do item

–  STY017-RN02: Imagens de baixa qualidade são rejeitadas, com orientação para nova captura

•  STY016-RN02 — Imagens com formato, tamanho e quantidade limitados e remoção automática de metadados de localização (Regras de Negócio Steely v1)

•  Diagrama de Fluxo BPMN — P1 Publicar: capturar ao menos uma fotografia (STY017-RN01), verificar qualidade (enquadramento, foco e iluminação) e orientar nova captura

•  Termo de Abertura do Projeto (TAP) — Restrições: sigilo da localização exata do item e arquitetura REST entre app e backend; Riscos: falha no reconhecimento do Scanner IA (UC-03)

•  ADRs relacionados do grupo — ADR-11, ADR-12, ADR-13, ADR-17, ADR-23

## Histórico de revisões

| Versão | Data | Autor | Alteração |
| --- | --- | --- | --- |
| 1.0 | 01/11/2026 | Rafael Tudela Rizental | Criação do documento. Definição da estratégia de captura e compressão de imagem com expo-image-manipulator e expo-image-picker, incluindo pipeline de compressão progressiva e orientação de recaptura. |
| 1.1 | 01/11/2026 | Rafael Tudela Rizental | Alinhamento com as ADRs do grupo: upload via FastAPI com Pillow (EXIF/GPS, WebP, offers-media, imagehash — ADR-11) e Scanner IA em 4 estágios (ADR-12); validação fina de foco no Estágio 1; limite de vídeos de disputa; Development Build; validação em Android; Sprint 8 e participantes atualizados. |
| 1.2 | 01/11/2026 | Rafael Tudela Rizental | Validação fina no Estágio 0 do ADR-12 (< 150 ms, ROI ≥ 15%) e tratamento de LOW_QUALITY_RECAPTURE e CIRCUIT_OPEN_FALLBACK; API atual do expo-image-manipulator (manipulateAsync obsoleto) e saída WebP; mediaTypes: ['images']; limite de vídeo conferido por fileSize e no servidor; até 6 fotos (ADR-11); etapas 5 e 6 na Sprint 9 (ADR-11, ADR-12); vínculo ADR-23. |
