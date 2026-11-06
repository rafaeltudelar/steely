# Passo a passo simples — fazer uma tela do Steely

[← Design](README.md) · [Guia completo](GUIA-DE-PROTOTIPOS.md)

O caminho mais fácil, **sem decorar comando**: GitHub Desktop (tudo com botões) e qualquer IA no navegador (ChatGPT, Gemini ou Claude). Siga na ordem, sem pular nada. Os exemplos usam a tela **007 · Meus Anúncios (EDTS-258)**: troque pelos dados da sua tarefa.

---

## Parte 0 — Preparar o computador (só uma vez na vida)

1. Instale estes programas (clique em *Download* e depois *Próximo, Próximo, Concluir*):
   - **GitHub Desktop**: <https://desktop.github.com>
   - **Python**: <https://www.python.org/downloads> — no Windows, na primeira tela do instalador, marque ✅ **Add Python to PATH** antes de clicar em *Install*
   - **Google Chrome**, se ainda não tiver
   - **Mac**: instale também o **VS Code** (<https://code.visualstudio.com>) para salvar os arquivos
2. Aceite o convite do repositório: no seu e-mail, procure *"rafaeltudelar invited you"* e clique em **Accept invitation**.
3. Abra o **GitHub Desktop**, entre com a sua conta do GitHub e vá em **File → Clone repository** → aba **GitHub.com** → escolha **rafaeltudelar/steely** → **Clone**. Pronto: agora existe uma pasta **steely** no seu computador (normalmente em *Documentos/GitHub/steely*).
4. No Figma, abra o arquivo [STEELY](https://www.figma.com/design/MZxnX0uT8BGIxpxkMFwUCj/STEELY) → menu **Plugins** → procure **html.to.design** → clique em **Run** uma vez para instalar.

---

## Parte 1 — Pegar a tarefa

1. Abra a sua tarefa **PROTOTIPAGEM** no Jira.
2. Anote num bloco de notas:
   - o **número da tela** (ex.: `007`)
   - o **nome da tela** (ex.: `Meus Anúncios`)
   - o **código da tarefa** (ex.: `EDTS-258`)
3. Copie a **descrição** da tarefa inteira e guarde.

---

## Parte 2 — Criar o seu branch (a sua cópia para trabalhar)

1. Abra o **GitHub Desktop**.
2. Lá em cima, clique em **Current branch** e confira que está em **main**. Clique em **Fetch origin** para pegar a versão mais nova.
3. Clique em **Current branch → New branch**.
4. Escreva o nome assim, tudo minúsculo, sem acento e sem espaço: `docs/EDTS-258-tela-007-meus-anuncios`
5. Clique em **Create branch** e depois em **Publish branch**.

> ⚠️ **Nunca trabalhe na `main`.** Lá em cima precisa aparecer o nome do **seu** branch.

---

## Parte 3 — Mandar para a IA

1. Abra a IA que preferir — **ChatGPT**, **Gemini** ou **Claude** — numa **conversa nova**.
2. Clique no **clipe 📎 / + / Anexar** e envie estes arquivos da pasta **steely**:

| Arquivo | Onde está |
|---|---|
| `AGENTS.md` | dentro de `steely` |
| `gerar_telas.py` | `steely/ferramentas/prototipos/` |
| `README.md` | `steely/docs/05-design/` |
| `002-central-de-notificacoes.html` | `steely/docs/05-design/prototipos/html/` |
| `004-criar-anuncio-etapa-2-detalhes.html` | `steely/docs/05-design/prototipos/html/` |
| `002-central-de-notificacoes.png` | `steely/docs/05-design/prototipos/png/` |

3. Abra o [Guia de protótipos no GitHub](https://github.com/rafaeltudelar/steely/blob/main/docs/05-design/GUIA-DE-PROTOTIPOS.md#o-prompt-mestre-vale-para-todas-as-trilhas), desça até **"O prompt mestre"** e clique no ícone de **copiar** (📋) no canto do quadro cinza.
4. Cole na IA e, **antes de enviar**, troque só o que está entre `⟨ ⟩`:
   - `⟨NNN⟩` → `007`
   - `⟨Nome da tela⟩` → `Meus Anúncios`
   - `⟨EDTS-XXX⟩` → `EDTS-258`
   - `⟨NNN-nome-em-minusculas-sem-acento⟩` → `007-meus-anuncios`
   - `⟨cole a descrição da tarefa⟩` → a descrição do Jira
   - o resto que tiver `⟨ ⟩`, escreva com as suas palavras (ex.: "vem da Home pelo menu Perfil")
5. Envie e espere a IA terminar.
6. Confira se o código **termina em `</html>`**. Se não terminar, escreva: *"Me mande o HTML completo, do começo ao fim, num bloco só."*

---

## Parte 4 — Salvar o arquivo

1. Clique em **Copiar** no código que a IA mandou.
2. Abra o **Bloco de Notas** (Windows) ou o **VS Code** (Mac — **não use o TextEdit**).
3. Cole o código.
4. **Arquivo → Salvar como** e vá até a pasta `steely/docs/05-design/prototipos/html/`.
5. No nome, escreva `007-meus-anuncios.html`. No Windows, em *Tipo* escolha **Todos os arquivos** e em *Codificação* escolha **UTF-8**.
6. Salve.

---

## Parte 5 — Verificar se a tela está certa

1. No **GitHub Desktop**: menu **Repository → Open in Terminal** (Mac) ou **Open in Command Prompt** (Windows). Abre uma janela preta.
2. Copie e cole a linha abaixo e aperte **Enter**:
   - Mac: `python3 ferramentas/prototipos/verificar_telas.py`
   - Windows: `py ferramentas/prototipos/verificar_telas.py`
3. Agora esta (troque `007` pelo seu número) e aperte **Enter**:
   - Mac: `python3 ferramentas/prototipos/conferir_telas.py 007`
   - Windows: `py ferramentas/prototipos/conferir_telas.py 007`
4. Olhe o resultado:
   - **Tudo ✅ e "telas aprovadas"** → vá para a Parte 6.
   - **Apareceu ❌** → copie todas as linhas com `-` que aparecem embaixo do ❌, volte na IA e escreva *"O verificador reprovou com estes erros. Corrija e me mande o HTML completo:"* e cole os erros. Salve de novo por cima do mesmo arquivo (Parte 4) e rode a Parte 5 de novo. Repita até ficar tudo ✅.
5. Abra a pasta `steely/docs/05-design/prototipos/png/`. Apareceu a imagem `007-meus-anuncios.png`: abra e veja se ficou bonita e parecida com as outras telas.

---

## Parte 6 — Colocar no Figma

1. Abra o Figma → arquivo **STEELY** → **Page 1**.
2. Menu **Plugins → html.to.design**.
3. Escolha importar **arquivo HTML** e selecione o seu `007-meus-anuncios.html`.
4. Em tamanho/viewport, coloque **1920 × 1200** e importe.
5. Vai aparecer um bloco cinza. Clique nele uma vez e, no painel da **direita**, mude:
   - **X** = o valor da sua tela na [tabela do guia](GUIA-DE-PROTOTIPOS.md#tabela-das-59-telas) (a tela 007 é **49203**)
   - **Y** = **12682**
6. Na lista de camadas (esquerda), dê **dois cliques no nome do bloco** e renomeie para `007 · Meus Anúncios`.
7. Copie o **título grande** de outra tela (ex.: "Home / Feed", em cima da tela 001) com **Ctrl+C / Ctrl+V** (Mac: **Cmd+C / Cmd+V**), arraste para cima da sua tela e troque o texto pelo nome da sua.

---

## Parte 7 — Fazer o commit e enviar

1. Volte ao **GitHub Desktop**. Na esquerda aparecem os arquivos novos:
   - ✅ `docs/05-design/prototipos/html/007-meus-anuncios.html`
   - ✅ `docs/05-design/prototipos/png/007-meus-anuncios.png`

   Se aparecer **algum outro arquivo** que você não mexeu, **desmarque**.
2. Embaixo, no campo **Summary**, escreva (com os seus dados): `docs(design): adiciona tela 007 meus anúncios (EDTS-258)`
3. Clique no botão azul **Commit to docs/EDTS-258-…**

   > ⚠️ Se o botão disser **"Commit to main"**, **pare**: você está na main. Volte à Parte 2.
4. Clique em **Push origin** (lá em cima).
5. Clique em **Create Pull Request**. Abre o site do GitHub.
6. Na descrição, arraste o PNG da sua tela, escreva o código do Jira e clique em **Create pull request**.
7. Avise no grupo: *"Abri o PR da tela 007, alguém revisa?"*
8. Espere aparecer ✅ verde em **Checks** e um colega aprovar. Pronto, a tela está entregue! 🎉
9. No Jira, mova a tarefa para **Done** e cole o link do PR.

---

## Deu problema?

| Problema | O que fazer |
|---|---|
| `python3` não encontrado | No Windows use `py`. Se nem `py` funcionar, reinstale o Python marcando **Add Python to PATH**. |
| `Não achei o Chrome` | Instale o Google Chrome. |
| Letras estranhas (`Ã§`) | Salve o arquivo de novo escolhendo **UTF-8**. |
| A IA mudou cores ou fontes | Escreva: *"Use exatamente o CSS do gerar_telas.py, sem mudar nenhuma cor, fonte ou tamanho."* |
| ❌ vermelho no PR | Clique em **Details**, copie o erro, mande para a IA, salve o arquivo de novo e faça **Commit + Push** de novo (Parte 7, itens 1 a 4). |
| Travou em qualquer coisa | Mande print no grupo. |

Quer o caminho mais automático (a IA cria o branch, verifica e corrige sozinha)? Veja a Trilha A do [Guia completo](GUIA-DE-PROTOTIPOS.md).
