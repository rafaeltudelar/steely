#!/usr/bin/env python3
"""Verificação rápida (sem navegador) das telas HTML em docs/05-design/prototipos/html/.

Confere o código-fonte de cada tela:
  - nome do arquivo no formato NNN-nome-da-tela.html e <title> começando com o mesmo NNN;
  - estrutura padrão: página 1920x1200, .phone de 375x812 em 773,194, .notch;
  - Google Fonts com Space Grotesk e DM Sans; nenhuma outra fonte;
  - cores (hex e rgb/rgba) só da paleta da marca;
  - tamanhos de fonte só da escala 11, 13, 14, 15, 16, 18, 20, 24;
  - nada carregado de fora além do Google Fonts (imagens só embutidas em data:).

Para o layout de verdade (nada atrás do rodapé) e as capturas PNG, rode depois o conferir_telas.py.

Uso:  python3 ferramentas/prototipos/verificar_telas.py [arquivos...]
Sai com código 1 se alguma tela reprovar.
"""
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parents[2]
TELAS = RAIZ / 'docs/05-design/prototipos/html'

PALETA = {
    '0d1b2a': 'Charcoal', '070f18': 'Fundo', '11233a': 'Superfície', '1a3250': 'Borda',
    '1ddb6a': 'Verde', 'a8efc4': 'ESG', 'ffffff': 'Branco', '6b7a8d': 'Secundário', 'ff5a5f': 'Alerta',
}
PALETA_RGB = {'13,27,42', '7,15,24', '17,35,58', '26,50,80', '29,219,106', '168,239,196',
              '255,255,255', '107,122,141', '255,90,95'}
FONTES = {'space grotesk', 'dm sans', 'sans-serif'}
TAMANHOS = {11, 13, 14, 15, 16, 18, 20, 24}
NOME = re.compile(r'^(\d{3})-[a-z0-9]+(?:-[a-z0-9]+)*\.html$')


CORES_COM_NOME = r'\b(?:white|black|red|green|blue|gray|grey|silver|lime|teal|navy|orange|yellow|purple)\b'


def expandir(h):
    h = h.lower()
    return ''.join(c * 2 for c in h[:3]) if len(h) in (3, 4) else h[:6]


def verificar(arq: pathlib.Path):
    erros = []
    txt = arq.read_text(encoding='utf-8')
    m = NOME.match(arq.name)
    if not m:
        erros.append('Nome fora do padrão NNN-nome-em-minusculas.html (ex.: 007-meus-anuncios.html)')
    t = re.search(r'<title>(.*?)</title>', txt, re.S)
    if not t:
        erros.append('Falta <title>')
    elif m and not t.group(1).strip().startswith(m.group(1)):
        erros.append(f'<title> deve começar com {m.group(1)} (está "{t.group(1).strip()}")')

    sem_dados = re.sub(r'data:[^"\')\s]+', 'data:', txt)  # ignora imagens embutidas
    estilo = ' '.join(re.findall(r'<style>(.*?)</style>', txt, re.S)) + ' ' + ' '.join(re.findall(r'style="([^"]*)"', txt))

    for trecho, desc in [(r'width:\s*1920px', 'body com 1920px de largura'),
                         (r'height:\s*1200px', 'body com 1200px de altura'),
                         (r'class="phone"', 'div .phone'), (r'class="notch"', 'div .notch'),
                         (r'left:\s*773px', '.phone em left:773px'), (r'top:\s*194px', '.phone em top:194px'),
                         (r'width:\s*375px', '.phone com 375px'), (r'height:\s*812px', '.phone com 812px'),
                         (r'fonts\.googleapis\.com/css2\?[^"]*Space\+Grotesk', 'Google Fonts com Space Grotesk'),
                         (r'fonts\.googleapis\.com/css2\?[^"]*DM\+Sans', 'Google Fonts com DM Sans')]:
        if not re.search(trecho, txt):
            erros.append(f'Falta: {desc}')

    for h in sorted(set(re.findall(r'#([0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3,4})\b', sem_dados))):
        if expandir(h) not in PALETA:
            erros.append(f'Cor fora da paleta: #{h}')
    for rgb in sorted(set(re.findall(r'rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)', estilo))):
        if ','.join(rgb) not in PALETA_RGB and ','.join(rgb) != '0,0,0':
            erros.append(f'Cor fora da paleta: rgb({",".join(rgb)})')

    if re.search(r'\bhsla?\(', estilo):
        erros.append('Use hex ou rgba() da paleta, não hsl()')
    for nome in sorted(set(re.findall(r'(?:color|background|fill|stroke|border)[\w-]*\s*[:=]\s*["\']?(' + CORES_COM_NOME[2:-2] + r')\b', txt, re.I))):
        erros.append(f'Cor com nome não permitida: {nome} (use o hex da paleta)')
    if re.search(r'url\(\s*["\']?https?:', estilo):
        erros.append('Não use url(https://…) no CSS: nada de imagem externa')
    for fam in set(re.findall(r'font-family\s*:\s*([^;}"]+)', estilo)):
        for f in fam.split(','):
            nome = f.strip().strip('\'"').lower()
            if nome and nome not in FONTES:
                erros.append(f'Fonte não permitida: {f.strip()}')
    for tam in sorted(set(float(x) for x in re.findall(r'font-size\s*:\s*([\d.]+)px', estilo))):
        if tam not in TAMANHOS:
            erros.append(f'Tamanho de fonte fora da escala: {tam:g}px')

    for url in re.findall(r'(?:src|href)="(https?://[^"]+)"', txt):
        if not re.match(r'https://fonts\.(googleapis|gstatic)\.com', url):
            erros.append(f'Recurso externo não permitido: {url[:60]}')
    if '<script' in txt.lower():
        erros.append('Não use <script> nas telas (o html.to.design importa só o visual)')
    return erros


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    arquivos = [pathlib.Path(a) for a in sys.argv[1:]] or sorted(TELAS.glob('*.html'))
    if not arquivos:
        sys.exit(f'Nenhuma tela em {TELAS.relative_to(RAIZ)}')
    reprovadas = 0
    for arq in arquivos:
        erros = verificar(arq)
        print(('❌ ' if erros else '✅ ') + arq.name)
        for e in erros:
            print(f'   - {e}')
        reprovadas += bool(erros)
    print(f'\n{len(arquivos) - reprovadas} de {len(arquivos)} telas aprovadas.')
    sys.exit(1 if reprovadas else 0)


if __name__ == '__main__':
    main()
