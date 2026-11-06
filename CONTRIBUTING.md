# Como contribuir com o Steely

Obrigado por ajudar! Este guia vale para a equipe e para quem chegar de fora. Ele é curto de propósito: siga os passos e o resto as verificações automáticas conferem por você.

## Regra de ouro

**Ninguém envia direto para a `main`.** Toda mudança entra por um *Pull Request* (PR) revisado por pelo menos uma pessoa. A `main` fica protegida e as verificações precisam passar antes do merge.

## O fluxo (GitHub Flow)

```bash
# 1. Atualize sua main
git checkout main
git pull

# 2. Crie um branch para a tarefa do Jira
git checkout -b docs/EDTS-258-tela-007-meus-anuncios

# 3. Trabalhe, rode as verificações e faça commits pequenos
python3 ferramentas/verificar_links.py
git add .
git commit -m "docs(design): adiciona tela 007 meus anúncios (EDTS-258)"

# 4. Envie e abra o PR
git push -u origin docs/EDTS-258-tela-007-meus-anuncios
```

Depois abra o PR no GitHub (o modelo de descrição aparece sozinho), peça revisão e aguarde o ✅ das verificações.

### Nome do branch

`tipo/EDTS-123-descricao-curta`, tudo em minúsculas e sem acento.

| Tipo | Quando usar |
|---|---|
| `feat` | Funcionalidade nova no código |
| `fix` | Correção de bug |
| `docs` | Documentação, protótipos e telas |
| `chore` | Configuração, scripts, organização |
| `refactor` | Melhoria de código sem mudar o comportamento |
| `test` | Testes |

### Mensagem de commit ([Conventional Commits](https://www.conventionalcommits.org/pt-br/), em português)

```
tipo(área): o que mudou, no imperativo (EDTS-123)
```

Exemplos:

- `docs(design): adiciona tela 007 meus anúncios (EDTS-258)`
- `feat(backend): cria rota de publicação de oferta (EDTS-301)`
- `fix(mobile): corrige preço sem centavos no card (EDTS-322)`

Áreas comuns: `design`, `requisitos`, `arquitetura`, `gestao`, `backend`, `web`, `mobile`, `database`, `scanner`, `ferramentas`, `site`.

## Telas e protótipos

Siga o [Guia de protótipos](docs/05-design/GUIA-DE-PROTOTIPOS.md). Em resumo:

1. Gere o HTML da tela (com Claude ou Gemini) em `docs/05-design/prototipos/html/NNN-nome-da-tela.html`.
2. Rode `python3 ferramentas/prototipos/verificar_telas.py` e `python3 ferramentas/prototipos/conferir_telas.py NNN` até ficar tudo ✅.
3. Importe no Figma com o html.to.design na posição da tabela do guia.
4. Abra o PR com o HTML **e** o PNG gerado.

Só use as cores, fontes e tamanhos do [Design System](docs/05-design/README.md#design-system-em-resumo).

## Documentos

- Escreva em português, frases curtas, sem jargão desnecessário.
- Use links relativos (`../02-requisitos/`) para outros arquivos do repositório; o verificador de links reprova links quebrados.
- Nomes de arquivo em minúsculas, com hífen e sem acento (`matriz-de-rastreabilidade.xlsx`).
- Não mova nem renomeie arquivos existentes sem combinar com a equipe — outros documentos apontam para eles.
- Nunca suba senhas, chaves de API, `.env` ou dados pessoais reais.

## Revisão

Quem revisa confere:

- [ ] A mudança faz o que a tarefa do Jira pede, e só isso
- [ ] As verificações automáticas passaram
- [ ] Telas: cores, fontes e espaçamentos batem com o Design System e com as telas vizinhas
- [ ] Textos claros e sem erro de português

Comentários de revisão são sobre o trabalho, nunca sobre a pessoa. Na dúvida, pergunte no PR.

## Licença

Ao contribuir, você concorda que o código fica sob a [licença MIT](LICENSE) e a documentação e os protótipos sob a [CC BY 4.0](LICENSE-DOCS.md).
