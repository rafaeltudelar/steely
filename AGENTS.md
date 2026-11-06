# Instruções para assistentes de IA (Claude, Gemini e outros)

Este arquivo é lido automaticamente pelo Claude Code (via `CLAUDE.md`) e pelo Gemini CLI (via `GEMINI.md`). Pessoas também podem colá-lo no início de uma conversa no claude.ai ou no Gemini.

## Projeto

Steely: marketplace de hardware de TI reaproveitável com laudo por IA. Projeto acadêmico da Escola de TI — UniCesumar (2026). Tudo em **português do Brasil**.

## Regras do repositório

- Nunca faça commit direto na `main`. Crie um branch `tipo/EDTS-123-descricao` e abra Pull Request.
- Commits no formato `tipo(área): mensagem no imperativo (EDTS-123)` — ver [CONTRIBUTING.md](CONTRIBUTING.md).
- Não mova, renomeie nem apague arquivos existentes sem a pessoa pedir.
- Nunca grave senhas, chaves, `.env` ou dados pessoais reais.
- Antes de terminar, rode `python3 ferramentas/verificar_links.py`.

## Telas de protótipo (o trabalho mais comum)

Siga [docs/05-design/GUIA-DE-PROTOTIPOS.md](docs/05-design/GUIA-DE-PROTOTIPOS.md). Resumo do que é obrigatório:

1. Arquivo `docs/05-design/prototipos/html/NNN-nome-em-minusculas.html`; `<title>NNN · Nome da tela</title>`.
2. Copie **literalmente** o início de [002-central-de-notificacoes.html](docs/05-design/prototipos/html/002-central-de-notificacoes.html) até `<div class="notch"></div>` (o mesmo `HEAD` e `CSS` de [gerar_telas.py](ferramentas/prototipos/gerar_telas.py)), trocando só o `<title>`: página 1920×1200 fundo `#070F18`, `.phone` 375×812 em `left:773px; top:194px`, `.notch`, `.screen`. Reaproveite as classes que já existem (`.topbar`, `.field`, `.input`, `.card`, `.chip`, `.opt`, `.info`, `.footer`, `.btn`, `.nav`…) antes de criar novas.
3. Só as cores da paleta (`#0D1B2A #070F18 #11233A #1A3250 #1DDB6A #A8EFC4 #FFFFFF #6B7A8D #FF5A5F`) e transparências delas em `rgba()`. `#FF5A5F` só para campo obrigatório, erro e segurança.
4. Só Space Grotesk (títulos, preços) e DM Sans (resto), nos tamanhos 11, 13, 14, 15, 16, 18, 20 ou 24 px.
5. Ícones: só os do dicionário `I` de `gerar_telas.py` (Lucide, traço 2); se faltar, peça o SVG à pessoa em vez de inventar. Nada de emoji, `<script>`, imagem externa, `url(https://…)`, `hsl()` ou cores com nome.
   O `.footer`/`.nav` é filho direto do `.phone`, irmão do `.screen`.
6. O conteúdo cabe acima do rodapé (`.footer` ou `.nav`); nada vaza pela direita (exceto `.chips` e `.carousel`, que rolam).
7. Textos realistas em português, coerentes com o Jira, os casos de uso (`docs/02-requisitos/casos-de-uso/`) e as regras de negócio.
8. Rode e só entregue com tudo ✅:
   - `python3 ferramentas/prototipos/verificar_telas.py`
   - `python3 ferramentas/prototipos/conferir_telas.py NNN` (gera também o PNG em `docs/05-design/prototipos/png/`)
9. Depois de aprovada, olhe o PNG gerado e compare com as telas vizinhas antes de dizer que terminou.
