# Site do projeto

[← Steely](../README.md)

Página pública do Steely, publicada pelo GitHub Pages em <https://rafaeltudelar.github.io/steely/>.

| Arquivo | O que é |
|---|---|
| `index.html` | A página (topo com a cena 3D, como funciona, jornada, protótipos, equipe) |
| `estilo.css` | Estilos — só cores e fontes do Design System |
| `cena.js` | Cena 3D do Scanner IA ([Three.js](https://threejs.org) r160): entrada da câmera, base holográfica e placa que gira com a rolagem. Pausa fora da tela e fica parada para quem prefere menos movimento |
| `movimento.js` | Animações com [Motion](https://motion.dev) 12 (versão fixa no importmap): entrada do topo, contadores, revelação das seções, barra de leitura, linha do tempo da jornada, celular em 3D e cartões que inclinam. Sem o Motion ou com "reduzir movimento", tudo aparece parado |
| `prototipos.js` | Visualizador navegável: carrega as telas de `docs/05-design/prototipos/html/` e liga os botões entre elas |

## Ver no computador

Da raiz do repositório:

```bash
python3 -m http.server 8000
```

E abra <http://localhost:8000/site/>.

## Publicar

O workflow [`site.yml`](../.github/workflows/site.yml) monta o site com as telas e publica. Ele roda à mão (aba **Actions → Site → Run workflow**) e, a cada mudança em `site/` ou nas telas que chegar à `main` (a variável `PAGES_ATIVO` já está `true`).

Para incluir uma tela nova no visualizador, adicione um item na lista `TELAS` de `prototipos.js` dizendo quais botões levam a quais telas.
