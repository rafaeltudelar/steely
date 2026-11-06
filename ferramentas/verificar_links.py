#!/usr/bin/env python3
"""Confere se todos os links relativos do repositório apontam para arquivos que existem.

Olha os arquivos .md e .html (menos node_modules e .git) e verifica:
  - links Markdown  [texto](caminho)  e  ![imagem](caminho)
  - atributos HTML  src="caminho"  e  href="caminho"
Ignora links externos (http, https, mailto), âncoras (#secao) e imagens embutidas (data:).

Uso:  python3 ferramentas/verificar_links.py
Sai com código 1 se achar algum link quebrado.
"""
import pathlib
import re
import sys
import urllib.parse

RAIZ = pathlib.Path(__file__).resolve().parents[1]
IGNORAR = {'.git', 'node_modules', '_site', '.venv', 'venv'}
MD_LINK = re.compile(r'!?\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+"[^"]*")?\s*\)')
HTML_ATTR = re.compile(r'\b(?:src|href)\s*=\s*["\']([^"\']+)["\']')
EXTERNO = re.compile(r'^(?:[a-z][a-z0-9+.-]*:|//|#)', re.I)


def arquivos():
    for p in RAIZ.rglob('*'):
        if p.suffix.lower() in {'.md', '.html'} and not IGNORAR & set(p.relative_to(RAIZ).parts):
            yield p


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    quebrados, total = [], 0
    for arq in sorted(arquivos()):
        texto = arq.read_text(encoding='utf-8', errors='replace')
        texto = re.sub(r'```.*?```', '', texto, flags=re.S)  # exemplos em blocos de código não contam
        texto = re.sub(r'`[^`\n]+`', '', texto)                # nem os de código em linha
        for alvo in MD_LINK.findall(texto) + HTML_ATTR.findall(texto):
            if EXTERNO.match(alvo) or '{' in alvo:
                continue
            caminho = urllib.parse.unquote(alvo.split('#')[0].split('?')[0])
            if not caminho:
                continue
            total += 1
            base = RAIZ if caminho.startswith('/') else arq.parent
            if not (base / caminho.lstrip('/')).exists():
                quebrados.append(f'{arq.relative_to(RAIZ)} → {alvo}')
    for q in quebrados:
        print(f'❌ {q}')
    print(f'{total - len(quebrados)} de {total} links relativos OK.')
    sys.exit(1 if quebrados else 0)


if __name__ == '__main__':
    main()
