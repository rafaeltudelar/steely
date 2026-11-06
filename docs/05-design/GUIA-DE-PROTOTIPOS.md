# Guia de protótipos — da tarefa do Jira até o Figma

[← Design](README.md)

Este guia ensina qualquer pessoa da equipe a fazer **uma tela de protótipo nova**, igual às que já estão aprovadas, usando **Claude**, **Gemini**, **ChatGPT** ou outra IA. A IA escreve a tela em HTML, dois scripts conferem se ela segue o Design System e o plugin **html.to.design** leva a tela para o Figma.

> **Por que HTML e não direto no Figma?** Porque o HTML pode ser conferido por máquina: cor errada, fonte errada ou texto escondido atrás do rodapé são reprovados antes de chegar ao Figma. Assim todas as telas ficam iguais, não importa quem fez nem qual IA usou.

## Sumário

0. [Visão geral (leia primeiro)](#0-visão-geral) — inclui as [regras da equipe](#regras-da-equipe-no-github) e [por que a IA não “inventa”](#por-que-a-ia-não-oscila)
1. [Preparação — só na primeira vez](#1-preparação--só-na-primeira-vez)
2. [Passo 1 — Pegar a tarefa no Jira](#passo-1--pegar-a-tarefa-no-jira)
3. [Passo 2 — Gerar o HTML com a IA](#passo-2--gerar-o-html-com-a-ia) — escolha **uma** trilha:
   - [Trilha A · Claude Code (terminal)](#trilha-a--claude-code-terminal) ⭐ mais automática
   - [Trilha B · claude.ai (navegador)](#trilha-b--claudeai-navegador)
   - [Trilha C · Gemini CLI (terminal)](#trilha-c--gemini-cli-terminal)
   - [Trilha D · Gemini no navegador](#trilha-d--gemini-no-navegador)
   - [Trilha E · ChatGPT e outras IAs](#trilha-e--chatgpt-e-outras-ias)
   - [Conferência final pela IA](#conferência-final-pela-ia)
4. [Passo 3 — Verificar a tela](#passo-3--verificar-a-tela)
5. [Passo 4 — Colocar no Figma](#passo-4--colocar-no-figma)
6. [Passo 5 — Enviar para o GitHub](#passo-5--enviar-para-o-github)
7. [Problemas comuns](#problemas-comuns)
8. [Tabela das 59 telas e posições no Figma](#tabela-das-59-telas)

---

## 0. Visão geral

```
 Jira (PROTOTIPAGEM_NNN)
   │  1. ler a tarefa e os casos de uso
   ▼
 IA (Claude, Gemini, ChatGPT…) + prompt mestre
   │  2. gera docs/05-design/prototipos/html/NNN-nome.html
   ▼
 verificar_telas.py  +  conferir_telas.py      ← repete até tudo ✅
   │  3. gera também o PNG
   ▼
 Figma (html.to.design, 1920×1200, posição da tabela)
   │  4. título em cima, nome no bloco
   ▼
 GitHub (branch + Pull Request com HTML e PNG)
      5. revisão de um colega e as mesmas verificações rodando sozinhas
```

**Tempo médio por tela:** 20–40 minutos depois da primeira vez.

**Regras que nunca mudam:**

| | Regra |
|---|---|
| 🎨 | Só as 9 cores do [Design System](README.md#design-system-em-resumo) (e transparências delas) |
| 🔤 | Só **Space Grotesk** (títulos e preços) e **DM Sans** (todo o resto), nos tamanhos 11, 13, 14, 15, 16, 18, 20 ou 24 px |
| 📱 | Página 1920×1200, celular 375×812 na posição 773,194 — igual a todas as telas |
| 📏 | Nada escondido atrás do rodapé, nada vazando pela lateral |
| 🗂️ | Arquivo `NNN-nome-em-minusculas.html`, com o número da tabela |
| ✅ | Só vai para o Figma depois que os dois verificadores aprovarem |

### Regras da equipe no GitHub

| | Regra |
|---|---|
| 🚫 | **Ninguém mexe na `main`.** Nem pelo terminal, nem pelo site, nem pela IA. A `main` é protegida: só recebe mudanças por Pull Request aprovado. |
| 🌿 | **Cada pessoa trabalha no seu próprio branch**, um branch por tarefa do Jira (`docs/EDTS-258-tela-007-meus-anuncios`). Não faça commit no branch de outra pessoa; se precisar ajustar algo dela, comente no PR. |
| ✍️ | Commits pequenos, com a sua conta do GitHub, no formato `docs(design): adiciona tela 007 meus anúncios (EDTS-258)`. Assim o histórico mostra quem fez cada tela. |
| 👀 | Todo PR precisa de **1 aprovação** de um colega e dos checks ✅ antes do merge. |
| 🌍 | **O repositório é público**: nada de senha, chave de API, `.env`, CPF, telefone ou e-mail pessoal, nem arquivos internos da faculdade. Dados de exemplo nas telas são inventados. |
| 🗂️ | Não mova nem renomeie arquivos existentes sem combinar: outros documentos apontam para eles. |

### Por que a IA não oscila

Cada IA tem seu "gosto" e, solta, cada pessoa receberia uma tela diferente. Aqui isso não acontece porque **a IA não decide o visual**, só preenche o conteúdo:

1. **CSS copiado, não reescrito** — o prompt manda copiar literalmente o cabeçalho e o CSS da tela 002. Cores, fontes, raios e espaçamentos já vêm prontos.
2. **Mesmas regras para todas as IAs** — o [`AGENTS.md`](../../AGENTS.md) é lido sozinho pelo Claude Code, Gemini CLI, Codex, Cursor e Copilot; nas versões de navegador ele vai como anexo.
3. **Verificação por máquina** — `verificar_telas.py` e `conferir_telas.py` reprovam qualquer cor, fonte, tamanho ou posição fora do padrão, não importa qual IA gerou.
4. **Os mesmos checks no PR** — o GitHub roda os verificadores de novo; um erro não passa nem se alguém pular o Passo 3.
5. **Olho humano no fim** — o PNG é comparado com 001–006 e um colega revisa o PR.

Se mesmo assim a IA desviar, a resposta é sempre a mesma: *"Use exatamente o CSS de gerar_telas.py, sem mudar nenhuma cor, fonte ou tamanho."*

---

## 1. Preparação — só na primeira vez

### 1.1 Programas

| O quê | Para quê | Como conferir |
|---|---|---|
| [Git](https://git-scm.com/downloads) | Baixar e enviar o repositório | `git --version` |
| [Python 3.9+](https://www.python.org/downloads/) | Rodar os verificadores (não precisa instalar nada além dele) | `python3 --version` (Windows: `py --version`) |
| [Google Chrome](https://www.google.com/chrome/) | O `conferir_telas.py` usa o Chrome sem abrir janela | Já instalado na maioria dos PCs |
| Plugin **html.to.design** no Figma | Importar o HTML como camadas editáveis | Figma → *Plugins* → procure "html.to.design" → *Run* |

> No **Windows**, em todos os comandos deste guia troque `python3` por `py`.

### 1.2 Baixar o repositório

```bash
git clone https://github.com/rafaeltudelar/steely.git
cd steely
```

Se você ainda não tem permissão de escrita, peça ao Rafael para te adicionar como colaborador (ou faça um *fork* e abra o PR a partir dele).

### 1.3 Testar se está tudo funcionando

```bash
python3 ferramentas/prototipos/verificar_telas.py
python3 ferramentas/prototipos/conferir_telas.py --sem-png
```

As duas linhas finais devem dizer **"6 de 6 telas aprovadas."** (ou mais, conforme a equipe adiciona telas). Se não disserem, veja [Problemas comuns](#problemas-comuns).

### 1.4 Acesso ao Figma

Arquivo: [STEELY no Figma](https://www.figma.com/design/MZxnX0uT8BGIxpxkMFwUCj/STEELY), página **Page 1**. Você precisa de permissão de edição. As telas de referência são **001 a 006** (Home, Notificações, Criar anúncio) e, à esquerda delas, as de autenticação.

---

## Passo 1 — Pegar a tarefa no Jira

1. No Jira, abra o épico **Prototipagem** (EDTS-322) e pegue uma tarefa `PROTOTIPAGEM_NNN` atribuída a você. O **NNN** é o número da tela — ele define o nome do arquivo e a posição no Figma (ver [tabela](#tabela-das-59-telas)).
2. Anote três coisas, porque vão para o prompt:
   - **Número e nome**: ex. `007 · Meus Anúncios`
   - **O que a tela precisa ter**: a descrição da tarefa no Jira
   - **Casos de uso relacionados**: abra [`especificacao-dos-casos-de-uso.xlsx`](../02-requisitos/casos-de-uso/especificacao-dos-casos-de-uso.xlsx), ache a aba `STYnnn` do assunto (ex.: STY019 Alterar Status Anúncio para a tela 009) e copie o **fluxo principal** e os **fluxos alternativos**. Confira também as [regras de negócio](../02-requisitos/).
3. Pense no **fluxo**: de qual tela o usuário vem e para qual vai ao tocar em cada botão. Isso evita telas soltas.

> Dica: se a descrição no Jira for genérica, o caso de uso é a fonte mais confiável do que precisa aparecer na tela.

---

## Passo 2 — Gerar o HTML com a IA

### O prompt mestre (vale para todas as trilhas)

Copie o bloco abaixo, troque **só** o que está entre `⟨ ⟩` e cole na IA. Ele é longo de propósito: cada linha evita um erro que já aconteceu.

```text
Você vai criar UMA tela de protótipo mobile do app Steely em HTML, idêntica em estilo às telas
já aprovadas. Responda em português do Brasil.

TELA: ⟨NNN⟩ · ⟨Nome da tela⟩   (Jira ⟨EDTS-XXX⟩)
ARQUIVO: docs/05-design/prototipos/html/⟨NNN-nome-em-minusculas-sem-acento⟩.html
O QUE A TELA PRECISA TER (Jira):
⟨cole a descrição da tarefa⟩
CASOS DE USO E REGRAS:
⟨cole o fluxo principal, os fluxos alternativos e as regras de negócio que importam⟩
DE ONDE VEM / PARA ONDE VAI:
⟨ex.: vem da Home pelo menu Perfil; "Editar" abre a tela 008⟩

REFERÊNCIAS (leia antes de escrever):
- docs/05-design/prototipos/html/002-central-de-notificacoes.html → o cabeçalho e o CSS oficiais
- docs/05-design/prototipos/html/004-criar-anuncio-etapa-2-detalhes.html → exemplo de formulário com etapas
- ferramentas/prototipos/gerar_telas.py → componentes (stepper, footer, notif, ocard, orow, navitem)
  e o dicionário I com os ícones já aprovados
- docs/05-design/README.md → Design System (cores, fontes, tamanhos)

REGRAS OBRIGATÓRIAS:
1. Copie LITERALMENTE tudo do início de 002-central-de-notificacoes.html até
   <div class="notch"></div>, trocando só o <title>. Não reescreva nenhuma regra de CSS.
   Reaproveite as classes existentes (.topbar .iconbtn .h1 .h2 .h3 .body .small .label .label-s
   .caption .field .flabel .input .hint .info .card .opt .radio .chip .chips .tagchip .toggle .notif
   .footer .btn.primary .btn.secondary .nav .navitem .fab .tile .photo .divider .summary-row ...).
   Só crie classe nova se nenhuma servir, e coloque-a no fim do <style>.
2. Estrutura fixa: <body> 1920x1200 fundo #070F18 → <div class="phone"> (375x812, left:773px,
   top:194px) → <div class="notch"> → <div class="screen"> com o conteúdo → rodapé (.footer com
   botões) OU menu inferior (.nav), nunca os dois. O .footer/.nav é IRMÃO do .screen (filho
   direto do .phone), nunca fica dentro dele. No .nav, marque .on na aba de onde o usuário veio.
   Telas com etapas usam a barra de etapas igual à de 003–006 (função stepper).
3. Cores: SOMENTE #0D1B2A #070F18 #11233A #1A3250 #1DDB6A #A8EFC4 #FFFFFF #6B7A8D #FF5A5F
   e rgba() dessas mesmas cores. #FF5A5F só para campo obrigatório (*), erro e segurança.
4. Fontes: Space Grotesk só em títulos (.h1 24 Bold, .h2 18 Bold, .h3 16 Medium) e preços;
   DM Sans no resto. Tamanhos permitidos: 11, 13, 14, 15, 16, 18, 20, 24 px. Nada fora disso.
5. Ícones: só os do dicionário I de gerar_telas.py (Lucide, viewBox 0 0 24 24, stroke-width 2,
   cores da paleta). Se faltar um ícone, NÃO invente o desenho: me peça e eu colo o SVG copiado
   de lucide.dev. Nunca use emoji como ícone.
   Proibido: <script>, imagens externas, url(https://…), Tailwind ou outro framework, hsl(),
   cores com nome (white, black…). Se precisar do logo, copie o <img class="logo"> de 001.
6. Nada vaza pela direita (só .chips e .carousel podem rolar de lado). Margem lateral 24px (já está no .screen). Espaço entre blocos 10–18px, ajustando o gap do
   .screen para TUDO caber acima do rodapé. Se não couber, encurte textos ou junte campos
   lado a lado — nunca diminua fonte abaixo da escala.
7. Textos reais e curtos, em português, coerentes com Maringá-PR e hardware usado
   (ex.: RTX 3060 Ti 8GB, Ryzen 5 5600, R$ 1.650). Nada de "Lorem ipsum".
8. <title> começa com o número: "⟨NNN⟩ · ⟨Nome da tela⟩". O nome do arquivo é o da coluna
   "Arquivo" da tabela do guia.
9. Se você pode gravar arquivos, grave direto em ARQUIVO. Se não pode, entregue o HTML
   COMPLETO, do <!DOCTYPE html> ao </html>, num único bloco, sem cortar nada.

Ao terminar, rode (se você puder executar comandos) e corrija até os dois mostrarem ✅:
  python3 ferramentas/prototipos/verificar_telas.py
  python3 ferramentas/prototipos/conferir_telas.py ⟨NNN⟩
Depois abra o PNG gerado em docs/05-design/prototipos/png/ e confira se está bonito e
alinhado com as telas 001–006 antes de dizer que terminou.
```

---

### Trilha A · Claude Code (terminal)

A mais automática: o Claude lê os arquivos, escreve a tela, roda os verificadores, olha o PNG e corrige sozinho. O repositório tem um [`CLAUDE.md`](../../CLAUDE.md) que carrega as regras de [`AGENTS.md`](../../AGENTS.md) automaticamente.

1. Instale uma vez seguindo a [documentação do Claude Code](https://docs.claude.com/en/docs/claude-code/overview). Também funciona pelo app **Claude** para desktop, na aba **Code**.
2. Na pasta do repositório, crie o branch da tela:
   ```bash
   git checkout main
   git pull
   git checkout -b docs/EDTS-⟨XXX⟩-tela-⟨NNN⟩-⟨nome⟩
   ```
   Exemplo para a tela 007: `docs/EDTS-258-tela-007-meus-anuncios`.
3. Abra o Claude Code na pasta:
   ```bash
   claude
   ```
4. Cole o **prompt mestre** preenchido.
5. Quando ele pedir permissão para criar o arquivo ou rodar `python3`, aprove.
6. No fim, peça: `mostre o PNG da tela e me diga o resultado dos dois verificadores`. Confira você mesmo o PNG em `docs/05-design/prototipos/png/`.
7. Para ajustar algo, peça em linguagem normal (`mova o botão X para…`, `deixe o título mais curto`) — ele refaz e verifica de novo.
8. Vá para o [Passo 4 — Figma](#passo-4--colocar-no-figma).

> Dica: em telas complexas (ex.: checkout), peça "faça um plano antes de escrever". Ele mostra a estrutura e você aprova antes.

---

### Trilha B · claude.ai (navegador)

Para quem prefere não usar terminal para gerar. Você ainda precisa do repositório clonado (item 1.2), do Python e do Chrome para verificar.

1. Entre em [claude.ai](https://claude.ai) e crie um **Projeto** chamado "Steely — protótipos" (assim você anexa os arquivos uma vez só).
2. Em **Project knowledge**, envie estes arquivos do repositório:
   - `AGENTS.md`
   - `ferramentas/prototipos/gerar_telas.py`
   - `docs/05-design/README.md`
   - `docs/05-design/prototipos/html/002-central-de-notificacoes.html`
   - `docs/05-design/prototipos/html/004-criar-anuncio-etapa-2-detalhes.html`
   - `docs/05-design/prototipos/png/001-home-feed.png`, `002-central-de-notificacoes.png` e `004-criar-anuncio-etapa-2-detalhes.png` (para ele ver o resultado visual)

   Não envie o `001-home-feed.html`: ele carrega o logo embutido e é pesado. Se sua tela tiver o logo, copie a linha `<img class="logo" …>` do 001 à mão depois.
3. Abra uma conversa nova dentro do projeto e cole o **prompt mestre** preenchido.
4. O Claude mostra o HTML num painel ao lado. Clique em **Copiar** (ou baixe o arquivo).
5. Salve o arquivo dentro da pasta do repositório que você clonou, em `docs/05-design/prototipos/html/`, com o nome da coluna *Arquivo* da [tabela](#tabela-das-59-telas).
   - Use um editor de código (VS Code, Notepad++ ou o Bloco de Notas do Windows com codificação **UTF-8**). No Mac, **não use o TextEdit** (ele salva em RTF).
   - Se você baixou o arquivo, mova-o da pasta Downloads e confira que termina em `.html` (e não `.html.txt`).
   - Crie também o branch: `git checkout -b docs/EDTS-⟨XXX⟩-tela-⟨NNN⟩-⟨nome⟩` (ou faça pelo site no Passo 5).
6. Rode o [Passo 3](#passo-3--verificar-a-tela). Se algo reprovar, copie a lista de erros e cole na mesma conversa:
   ```text
   O verificador reprovou com estes erros. Corrija e me devolva o HTML completo:
   ⟨cole os erros⟩
   ```
7. Repita até ✅ e vá para o [Passo 4](#passo-4--colocar-no-figma).

---

### Trilha C · Gemini CLI (terminal)

Funciona como a trilha A. O repositório tem um [`GEMINI.md`](../../GEMINI.md) que carrega as regras de [`AGENTS.md`](../../AGENTS.md).

1. Instale uma vez (precisa do [Node.js](https://nodejs.org) 18 ou mais novo):
   ```bash
   npm install -g @google/gemini-cli
   ```
   Na primeira execução, entre com sua conta Google.
2. Crie o branch, como na trilha A (passo 2).
3. Na pasta do repositório:
   ```bash
   gemini
   ```
4. Cole o **prompt mestre** preenchido. Para garantir que ele leia as referências, comece a mensagem com:
   ```text
   @ferramentas/prototipos/gerar_telas.py @docs/05-design/README.md @docs/05-design/prototipos/html/004-criar-anuncio-etapa-2-detalhes.html @docs/05-design/prototipos/html/001-home-feed.html
   ```
5. Aprove quando ele pedir para escrever o arquivo e rodar os comandos `python3`.
6. Se ele disser que terminou sem rodar os verificadores, peça: `rode os dois verificadores e corrija até ficar tudo ✅`.
7. Abra o PNG gerado e confira com seus olhos. Vá para o [Passo 4](#passo-4--colocar-no-figma).

---

### Trilha D · Gemini no navegador

1. Entre em [gemini.google.com](https://gemini.google.com). Use o modelo mais avançado disponível na sua conta.
2. Recomendado: crie um **Gem** chamado "Steely protótipos", cole o conteúdo de `AGENTS.md` nas instruções e anexe ao **Conhecimento** do Gem os mesmos arquivos da trilha B (passo 2). Assim você não repete nada a cada tela.
3. Sem Gem: numa conversa nova, clique em **+ → Enviar arquivos** e envie os arquivos da trilha B (passo 2).
4. Se aparecer a opção **Canvas**, ative — fica mais fácil ver e copiar o código.
5. Cole o **prompt mestre** preenchido.
6. Copie o HTML **inteiro** (confira se termina em `</html>`) e salve como na trilha B (passo 5).
7. Rode o [Passo 3](#passo-3--verificar-a-tela). Se reprovar, cole os erros na conversa como na trilha B (passo 6).

> Respostas longas às vezes vêm cortadas: se o código não terminar em `</html>`, peça *"continue exatamente de onde parou"* e junte as partes, ou peça o arquivo de novo.

> O Gemini às vezes "melhora" cores ou troca a fonte por conta própria. Se acontecer, responda: `Use exatamente o CSS de gerar_telas.py, sem alterar nenhuma cor nem fonte.`

---

### Trilha E · ChatGPT e outras IAs

Funciona igual à trilha B/D. Vale para **ChatGPT**, **Microsoft Copilot**, **DeepSeek**, **Grok**, **Perplexity** e qualquer outra IA de conversa.

1. **ChatGPT**: em [chatgpt.com](https://chatgpt.com), crie um **Projeto** "Steely protótipos" (ou um **GPT** personalizado). Cole o conteúdo de `AGENTS.md` em *Instruções* e envie os arquivos da trilha B (passo 2) em *Arquivos*. Use o modelo mais avançado da sua conta; se aparecer **Canvas**, ative.
2. **Outras IAs de conversa**: numa conversa nova, anexe os mesmos arquivos (ou cole o conteúdo de `AGENTS.md` e de `002-central-de-notificacoes.html` no início da mensagem).
3. Cole o **prompt mestre** preenchido.
4. Salve o HTML completo como na trilha B (passo 5) e rode o [Passo 3](#passo-3--verificar-a-tela). Se reprovar, cole os erros na conversa como na trilha B (passo 6).

**IAs que mexem nos arquivos** (Codex CLI da OpenAI, Cursor, Windsurf, GitHub Copilot no VS Code): funcionam como a trilha A. Elas leem o [`AGENTS.md`](../../AGENTS.md) da raiz sozinhas; crie o branch antes, abra a pasta do repositório e cole o prompt mestre. Aprove a execução dos comandos `python3`.

> IA que não consegue abrir anexos grandes: envie pelo menos `AGENTS.md`, `002-central-de-notificacoes.html` e o PNG da 002. Sem o HTML de referência, nenhuma IA acerta o padrão.

---

### Conferência final pela IA

Antes de levar ao Figma, peça para a própria IA revisar o que fez — funciona em qualquer trilha:

```text
Antes de eu levar ao Figma, confira a tela ⟨NNN⟩ item por item e me responda com ✅ ou ❌:
1. O trecho do início até <div class="notch"></div> é idêntico ao de 002 (só o <title> muda)?
2. Só cores da paleta e rgba() delas? #FF5A5F só em obrigatório/erro/segurança?
3. Space Grotesk só em títulos e preços, DM Sans no resto, tamanhos só 11/13/14/15/16/18/20/24?
4. Todos os ícones vêm do dicionário I de gerar_telas.py? Nenhum emoji?
5. O .footer/.nav é irmão do .screen e nada fica atrás dele nem vaza pela direita?
6. Os textos batem com a tarefa do Jira e o caso de uso? Os botões levam às telas certas?
7. Os dois verificadores deram ✅? (cole a saída)
Se algum item for ❌, corrija e mostre de novo.
```

A IA **não** coloca a tela no Figma sozinha: essa parte é sua, com o html.to.design (Passo 4). Assim só a versão aprovada vai para o arquivo da equipe.

---

## Passo 3 — Verificar a tela

Rode da raiz do repositório, trocando `007` pelo seu número:

```bash
python3 ferramentas/prototipos/verificar_telas.py
python3 ferramentas/prototipos/conferir_telas.py 007
python3 ferramentas/verificar_links.py
```

No Windows (PowerShell): `py ferramentas\prototipos\conferir_telas.py 007`. No Mac, o primeiro `python3` pode pedir para instalar as *Ferramentas de Linha de Comando*: aceite.

| Verificador | O que olha | Precisa de |
|---|---|---|
| `verificar_telas.py` | O **código**: nome do arquivo, `<title>`, estrutura, cores, fontes, tamanhos, recursos externos | Só Python |
| `conferir_telas.py` | O que **aparece no navegador**: cor e fonte de cada elemento, fontes carregadas, nada atrás do rodapé, nada vazando; e salva o **PNG** | Python, Chrome, internet |

### Como ler o resultado

```text
❌ 007-meus-anuncios.html
   - Cor fora da paleta: #22C55E                     → a IA inventou um verde; peça para usar #1DDB6A
   - Tamanho 12px fora da escala (...) em .caption   → troque para 11 ou 13
   - "Ver detalhes" fica atrás do rodapé (941 > 916)  → falta espaço; reduza gaps ou textos
   - Caixa .card fica atrás do rodapé                → idem
   - Fonte "Inter" em .body                          → a IA trocou a fonte
```

### O que os verificadores NÃO pegam (confira no olho)

- Peso de fonte errado (título em 600 em vez de Bold) ou Space Grotesk em texto comum
- Cantos, margens e espaçamentos diferentes das telas vizinhas
- Ícone inventado ou desenhado errado, emoji no lugar de ícone
- Elementos sobrepostos ou textos que não fazem sentido para a tarefa

Quando os verificadores mostrarem ✅, **abra o PNG** (`docs/05-design/prototipos/png/007-….png`) e compare lado a lado com 001–006. Os verificadores garantem as regras; o seu olho garante que ficou bonito (alinhamentos, hierarquia, textos que fazem sentido).

---

## Passo 4 — Colocar no Figma

1. Abra o arquivo [STEELY](https://www.figma.com/design/MZxnX0uT8BGIxpxkMFwUCj/STEELY), **Page 1**.
2. *Plugins* → **html.to.design** → escolha importar o **arquivo HTML** e selecione o seu `NNN-….html`.
   - Tamanho / viewport: **1920 × 1200**. É isso que deixa o celular no mesmo lugar das outras telas.
3. O plugin cria um bloco (Section) de **2120 × 1400**, fundo cinza `#444444`, com a tela 1920 × 1200 dentro — igual às telas já importadas. Com o bloco selecionado, no painel direito defina:
   - **X** = valor da [tabela](#tabela-das-59-telas) para o seu número
   - **Y** = **12682**

   Se a sua versão do plugin criar só o frame (sem a Section cinza): crie uma Section (atalho **Shift+S**) com **W 2120, H 1400**, preenchimento `#444444`, na posição X/Y acima, e arraste o frame importado para dentro, centralizado (100 px de cada lado). A versão gratuita do plugin tem limite de importações por mês: importe só a versão aprovada.
4. **Renomeie o bloco e o frame** (duplo clique no nome da camada) para `NNN · Nome da tela` — ex.: `007 · Meus Anúncios`.
5. **Título em cima**: duplique o título de uma tela vizinha (ex.: o texto "Home / Feed" acima da 001), troque o texto e posicione em **X = mesmo X do bloco**, **Y = 12064**. O padrão é Space Grotesk Bold 64, branco. Duplique também o subtítulo da 001 (logo abaixo do título, mesmo X) e escreva `PROTOTIPAGEM_NNN · EDTS-XXX · Sprint NN`.
6. Confira com zoom: o celular deve estar alinhado com os vizinhos e a fonte deve ser Space Grotesk ou DM Sans. Se aparecer outra, o Figma não tinha a fonte: instale [Space Grotesk](https://fonts.google.com/specimen/Space+Grotesk) e [DM Sans](https://fonts.google.com/specimen/DM+Sans) no computador e importe de novo.
7. **Protótipo navegável** (desejado): na aba *Prototype* do Figma, ligue os botões da sua tela às telas de destino (*On click → Navigate to*), conforme o fluxo que você anotou no Passo 1.

> A posição é calculada pelo número, então **não importa a ordem** em que as pessoas importam: a tela 030 tem o lugar dela mesmo que a 010 ainda não exista.

---

## Passo 5 — Enviar para o GitHub

### Pelo terminal (trilhas A e C, ou quem já usa Git)

```bash
git add docs/05-design/prototipos/html/007-meus-anuncios.html docs/05-design/prototipos/png/007-meus-anuncios.png docs/05-design/prototipos/README.md
git commit -m "docs(design): adiciona tela 007 meus anúncios (EDTS-258)"
git push -u origin docs/EDTS-258-tela-007-meus-anuncios
```

Abra o link que o `git push` mostrar e crie o **Pull Request**. Preencha o modelo, cole o PNG na descrição e peça revisão de um colega.

### Pelo site do GitHub (sem terminal)

1. No repositório, entre na pasta `docs/05-design/prototipos/html/`.
2. *Add file → Upload files* e arraste o HTML.
3. Embaixo, escolha **Create a new branch for this commit and start a pull request**, dê o nome `docs/EDTS-258-tela-007-meus-anuncios` e use a mensagem `docs(design): adiciona tela 007 meus anúncios (EDTS-258)`.
4. Ainda nesse branch, entre em `docs/05-design/prototipos/png/` e envie o PNG do mesmo jeito. Depois edite `docs/05-design/prototipos/README.md` (ícone de lápis) e adicione a linha da sua tela na tabela.
5. Abra o Pull Request.

Nos dois casos, a aba **Checks** do PR roda os mesmos verificadores. O PR só pode ser aprovado com tudo ✅ e **1 aprovação** de um colega. Quem abriu o PR não faz merge do próprio trabalho sem essa revisão, e ninguém envia nada direto para a `main`.

### Também atualize

- A tabela de telas em [`prototipos/README.md`](prototipos/README.md) (uma linha com número, nome, Jira, casos de uso e o PNG).
- A tarefa no Jira: mova para *Done* e cole o link do PR.

---

## Problemas comuns

| Problema | Solução |
|---|---|
| `python3: command not found` | Windows: use `py`. Mac: instale pelo [python.org](https://www.python.org/downloads/). |
| `Não achei o Chrome` | Instale o Chrome ou informe o caminho. Mac/Linux: `CHROME="/caminho/do/chrome" python3 …`. Windows (PowerShell): `$env:CHROME="C:\caminho\chrome.exe"; py …` |
| `Fonte não carregou (sem internet?)` | O conferidor baixa as fontes do Google Fonts; conecte-se à internet e rode de novo. |
| `A conferência não terminou` | O HTML tem erro de sintaxe ou está incompleto (a IA cortou o fim). Confira se termina em `</html>`. |
| Acentos estranhos (`Ã§`) | O arquivo não foi salvo em UTF-8. Salve de novo como UTF-8. |
| A IA "melhorou" as cores | Responda: *"Use exatamente o CSS de gerar_telas.py, sem mudar nenhuma cor, fonte ou tamanho."* |
| A IA respondeu só um trecho | Peça: *"Me devolva o arquivo HTML completo, do `<!DOCTYPE html>` ao `</html>`."* |
| Texto atrás do rodapé | Peça para reduzir o `gap` do `.screen`, encurtar textos ou colocar dois campos lado a lado. |
| No Figma o celular ficou em outro lugar | O viewport do plugin não estava em 1920 × 1200. Apague e importe de novo. |
| No Figma a fonte virou outra | Instale Space Grotesk e DM Sans no computador e importe de novo. |
| `push` recusado para a `main` (*protected branch*) | Correto: a `main` é protegida. Crie um branch (`git checkout -b docs/EDTS-…`), faça o commit nele e abra PR. |
| Check vermelho no PR | Abra *Details* no check, leia o erro (mesmo formato do Passo 3) e corrija no mesmo branch. |

---

## Tabela das 59 telas

**Fórmula:** `X = 34983 + (NNN − 1) × 2370`, `Y = 12682`, título em `Y = 12064`. Arquivo: `NNN-nome.html` (minúsculas, sem acento, palavras separadas por hífen).

| Nº | Tela | Jira | X no Figma | Arquivo | Situação |
|---|---|---|---|---|---|
| 001 | Home / Feed Principal | EDTS-252 | 34983 | [`001-home-feed.html`](prototipos/html/001-home-feed.html) | ✅ pronta |
| 002 | Central de Notificações | EDTS-253 | 37353 | [`002-central-de-notificacoes.html`](prototipos/html/002-central-de-notificacoes.html) | ✅ pronta |
| 003 | Criar Anúncio (Etapa 1: Fotos) | EDTS-254 | 39723 | [`003-criar-anuncio-etapa-1-fotos.html`](prototipos/html/003-criar-anuncio-etapa-1-fotos.html) | ✅ pronta |
| 004 | Criar Anúncio (Etapa 2: Detalhes) | EDTS-255 | 42093 | [`004-criar-anuncio-etapa-2-detalhes.html`](prototipos/html/004-criar-anuncio-etapa-2-detalhes.html) | ✅ pronta |
| 005 | Criar Anúncio (Etapa 3: Preço e Entrega) | EDTS-256 | 44463 | [`005-criar-anuncio-etapa-3-preco-e-entrega.html`](prototipos/html/005-criar-anuncio-etapa-3-preco-e-entrega.html) | ✅ pronta |
| 006 | Criar Anúncio (Etapa 4: Revisão e Publicação) | EDTS-257 | 46833 | [`006-criar-anuncio-etapa-4-revisao.html`](prototipos/html/006-criar-anuncio-etapa-4-revisao.html) | ✅ pronta |
| 007 | Meus Anúncios | EDTS-258 | 49203 | `007-meus-anuncios.html` | a fazer |
| 008 | Editar Anúncio | EDTS-259 | 51573 | `008-editar-anuncio.html` | a fazer |
| 009 | Pausar/Reativar Anúncio | EDTS-260 | 53943 | `009-pausar-reativar-anuncio.html` | a fazer |
| 010 | Excluir Anúncio | EDTS-261 | 56313 | `010-excluir-anuncio.html` | a fazer |
| 011 | Estatísticas do Anúncio | EDTS-262 | 58683 | `011-estatisticas-do-anuncio.html` | a fazer |
| 012 | Anúncios Favoritos | EDTS-263 | 61053 | `012-anuncios-favoritos.html` | a fazer |
| 013 | Comparar Anúncios | EDTS-264 | 63423 | `013-comparar-anuncios.html` | a fazer |
| 014 | Busca Avançada | EDTS-265 | 65793 | `014-busca-avancada.html` | a fazer |
| 015 | Resultados de Busca | EDTS-266 | 68163 | `015-resultados-de-busca.html` | a fazer |
| 016 | Detalhes do Anúncio | EDTS-267 | 70533 | `016-detalhes-do-anuncio.html` | a fazer |
| 017 | Perfil do Vendedor (Visão Comprador) | EDTS-268 | 72903 | `017-perfil-do-vendedor-visao-comprador.html` | a fazer |
| 018 | Categorias | EDTS-269 | 75273 | `018-categorias.html` | a fazer |
| 019 | Filtro por Localização (Mapa) | EDTS-270 | 77643 | `019-filtro-por-localizacao-mapa.html` | a fazer |
| 020 | Scanner de Código de Barras/QR | EDTS-271 | 80013 | `020-scanner-de-codigo-de-barras-qr.html` | a fazer |
| 021 | Histórico de Preços | EDTS-272 | 82383 | `021-historico-de-precos.html` | a fazer |
| 022 | Chat de Negociação | EDTS-273 | 84753 | `022-chat-de-negociacao.html` | a fazer |
| 023 | Enviar Proposta | EDTS-274 | 87123 | `023-enviar-proposta.html` | a fazer |
| 024 | Propostas Recebidas | EDTS-275 | 89493 | `024-propostas-recebidas.html` | a fazer |
| 025 | Agendar Entrega/Retirada | EDTS-276 | 91863 | `025-agendar-entrega-retirada.html` | a fazer |
| 026 | Confirmação de Entrega | EDTS-277 | 94233 | `026-confirmacao-de-entrega.html` | a fazer |
| 027 | Rastreamento de Envio | EDTS-278 | 96603 | `027-rastreamento-de-envio.html` | a fazer |
| 028 | Checkout / Pagamento | EDTS-279 | 98973 | `028-checkout-pagamento.html` | a fazer |
| 029 | Confirmação de Pedido | EDTS-280 | 101343 | `029-confirmacao-de-pedido.html` | a fazer |
| 030 | Meus Pedidos | EDTS-281 | 103713 | `030-meus-pedidos.html` | a fazer |
| 031 | Detalhes do Pedido | EDTS-282 | 106083 | `031-detalhes-do-pedido.html` | a fazer |
| 032 | Solicitar Garantia | EDTS-283 | 108453 | `032-solicitar-garantia.html` | a fazer |
| 033 | Acompanhar Garantia | EDTS-284 | 110823 | `033-acompanhar-garantia.html` | a fazer |
| 034 | Abrir Disputa | EDTS-285 | 113193 | `034-abrir-disputa.html` | a fazer |
| 035 | Detalhes da Disputa | EDTS-286 | 115563 | `035-detalhes-da-disputa.html` | a fazer |
| 036 | Cancelar Pedido | EDTS-287 | 117933 | `036-cancelar-pedido.html` | a fazer |
| 037 | Avaliar Transação | EDTS-288 | 120303 | `037-avaliar-transacao.html` | a fazer |
| 038 | Carteira Digital | EDTS-289 | 122673 | `038-carteira-digital.html` | a fazer |
| 039 | Depositar na Carteira | EDTS-290 | 125043 | `039-depositar-na-carteira.html` | a fazer |
| 040 | Sacar da Carteira | EDTS-291 | 127413 | `040-sacar-da-carteira.html` | a fazer |
| 041 | Verificação Captcha | EDTS-292 | 129783 | `041-verificacao-captcha.html` | a fazer |
| 042 | Criar Leilão | EDTS-293 | 132153 | `042-criar-leilao.html` | a fazer |
| 043 | Participar de Leilão | EDTS-294 | 134523 | `043-participar-de-leilao.html` | a fazer |
| 044 | Impulsionar Anúncio (Boost) | EDTS-295 | 136893 | `044-impulsionar-anuncio-boost.html` | a fazer |
| 045 | Sobre o Steely | EDTS-296 | 139263 | `045-sobre-o-steely.html` | a fazer |
| 046 | Termos de Uso | EDTS-297 | 141633 | `046-termos-de-uso.html` | a fazer |
| 047 | Política de Privacidade | EDTS-298 | 144003 | `047-politica-de-privacidade.html` | a fazer |
| 048 | Central de Ajuda / FAQ | EDTS-299 | 146373 | `048-central-de-ajuda-faq.html` | a fazer |
| 049 | Mapa de Ecopontos | EDTS-300 | 148743 | `049-mapa-de-ecopontos.html` | a fazer |
| 050 | Dashboard ESG Pessoal | EDTS-301 | 151113 | `050-dashboard-esg-pessoal.html` | a fazer |
| 051 | Doar para ONG | EDTS-302 | 153483 | `051-doar-para-ong.html` | a fazer |
| 052 | Meu Perfil | EDTS-303 | 155853 | `052-meu-perfil.html` | a fazer |
| 053 | Editar Perfil | EDTS-304 | 158223 | `053-editar-perfil.html` | a fazer |
| 054 | Configurações de Segurança | EDTS-305 | 160593 | `054-configuracoes-de-seguranca.html` | a fazer |
| 055 | Avaliar Usuário | EDTS-306 | 162963 | `055-avaliar-usuario.html` | a fazer |
| 056 | Solicitar Exclusão de Conta | EDTS-307 | 165333 | `056-solicitar-exclusao-de-conta.html` | a fazer |
| 057 | Realizar Denúncia | EDTS-308 | 167703 | `057-realizar-denuncia.html` | a fazer |
| 058 | Minhas Denúncias (Histórico) | EDTS-309 | 170073 | `058-minhas-denuncias-historico.html` | a fazer |
| 059 | Notificação de Sanção | EDTS-310 | 172443 | `059-notificacao-de-sancao.html` | a fazer |

---

*Dúvidas? Abra uma issue com o modelo "Problema" ou pergunte no grupo. Melhorias neste guia são bem-vindas via Pull Request.*
