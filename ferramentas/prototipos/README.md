# Ferramentas de protótipos

[← Guia de protótipos](../../docs/05-design/GUIA-DE-PROTOTIPOS.md)

Scripts em Python puro (sem instalar nada além do Python 3.9+ e do Google Chrome) para gerar, verificar e capturar as telas HTML que vão para o Figma.

| Arquivo | O que faz | Precisa de |
|---|---|---|
| [`gerar_telas.py`](gerar_telas.py) | Gera as telas 001–006 em `docs/05-design/prototipos/html/`. Serve de **modelo**: o CSS e os componentes (botão, campo, cartão, chip, rodapé, barra de etapas, notificação, menu inferior) estão todos nele | Python |
| [`verificar_telas.py`](verificar_telas.py) | Lê o código de cada tela e reprova cor fora da paleta, fonte errada, tamanho fora da escala, nome de arquivo fora do padrão ou estrutura diferente | Python |
| [`conferir_telas.py`](conferir_telas.py) | Abre cada tela no Chrome sem janela, confere o que **aparece de verdade** (cores, fontes carregadas, nada atrás do rodapé, nada vazando) e salva a captura em `docs/05-design/prototipos/png/` | Python, Chrome, internet |
| [`conferir.html`](conferir.html) | Página de apoio usada pelo `conferir_telas.py` (não precisa abrir) | — |
| [`assets/logo-steely.png`](assets/logo-steely.png) | Logo com fundo transparente, embutido nas telas | — |

## Comandos

Rode sempre da **raiz do repositório**:

```bash
python3 ferramentas/prototipos/gerar_telas.py        # (re)gera 001–006
python3 ferramentas/prototipos/verificar_telas.py    # verificação rápida do código
python3 ferramentas/prototipos/conferir_telas.py     # verificação no navegador + PNGs
python3 ferramentas/prototipos/conferir_telas.py 007 # só a tela 007
python3 ferramentas/verificar_links.py               # links do repositório
```

No Windows, troque `python3` por `py`. Se o Chrome estiver num lugar fora do padrão, informe o caminho:

```bash
CHROME="/caminho/do/chrome" python3 ferramentas/prototipos/conferir_telas.py
```

A tela só está **aprovada** quando os dois verificadores mostram ✅. O mesmo teste roda sozinho no GitHub a cada Pull Request.
