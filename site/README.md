# Site do projeto

[← Steely](../README.md)

Página pública do Steely, publicada pelo GitHub Pages em <https://rafaeltudelar.github.io/steely/>.

| Arquivo | O que é |
|---|---|
| `index.html` | A página (topo com a cena 3D, como funciona, protótipos, equipe) |
| `estilo.css` | Estilos — só cores e fontes do Design System |
| `cena.js` | Cena 3D do Scanner IA ([Three.js](https://threejs.org) r160). Pausa fora da tela e fica parada para quem prefere menos movimento |
| `prototipos.js` | Visualizador navegável: carrega as telas de `docs/05-design/prototipos/html/` e liga os botões entre elas |

## Ver no computador

Da raiz do repositório:

```bash
python3 -m http.server 8000
```

E abra <http://localhost:8000/site/>.

## Publicar

O workflow [`site.yml`](../.github/workflows/site.yml) monta o site com as telas e publica. Ele roda à mão (aba **Actions → Site → Run workflow**) e, depois que a variável `PAGES_ATIVO` for criada com o valor `true`, a cada mudança na `main`.

Para incluir uma tela nova no visualizador, adicione um item na lista `TELAS` de `prototipos.js` dizendo quais botões levam a quais telas.
