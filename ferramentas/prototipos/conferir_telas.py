#!/usr/bin/env python3
"""Confere as telas no navegador de verdade (Chrome sem janela) e tira as capturas PNG.

O que ele confere em cada tela (o mesmo que o grupo combinou para aprovar uma tela):
  - celular de 375x812 na posição 773,194 da página 1920x1200;
  - só cores da paleta da marca (qualquer opacidade);
  - só Space Grotesk ou DM Sans, nos tamanhos 11, 13, 14, 15, 16, 18, 20 e 24;
  - nada escondido atrás do rodapé e nada vazando pela direita;
  - as fontes carregaram de verdade.

Uso:
  python3 ferramentas/prototipos/conferir_telas.py                 # todas as telas
  python3 ferramentas/prototipos/conferir_telas.py 007 008         # só essas
  python3 ferramentas/prototipos/conferir_telas.py --sem-png       # só confere

Precisa do Google Chrome (ou Chromium) instalado e de internet (Google Fonts).
Se o Chrome estiver num lugar diferente, defina a variável CHROME com o caminho.
Sai com código 1 se alguma tela reprovar.
"""
import functools
import html
import http.server
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import urllib.parse

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
TELAS = RAIZ / 'docs/05-design/prototipos/html'
PNGS = RAIZ / 'docs/05-design/prototipos/png'

CANDIDATOS = [
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
    r'C:\Program Files\Google\Chrome\Application\chrome.exe',
    r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
]


def achar_chrome():
    if os.environ.get('CHROME'):
        return os.environ['CHROME']
    for nome in ('google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser', 'chrome'):
        if shutil.which(nome):
            return shutil.which(nome)
    for c in CANDIDATOS:
        if pathlib.Path(c).exists():
            return c
    sys.exit('Não achei o Chrome. Instale o Google Chrome ou defina CHROME=/caminho/do/chrome.')


def servidor():
    """Servidor http local na raiz do repo (o iframe precisa da mesma origem)."""
    class Silencioso(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass
    handler = functools.partial(Silencioso, directory=str(RAIZ))
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def chrome(binario, perfil, *args):
    base = [binario, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--no-first-run',
            '--no-default-browser-check', f'--user-data-dir={perfil}']
    if sys.platform.startswith('linux'):
        base.append('--no-sandbox')
    try:
        return subprocess.run(base + list(args), capture_output=True, encoding='utf-8', errors='replace', timeout=120).stdout
    except subprocess.TimeoutExpired:
        return ''


def conferir(binario, perfil, url):
    """Roda a conferência; tenta de novo com mais tempo se as fontes demorarem a chegar."""
    for orcamento in (6000, 15000):
        saida = chrome(binario, perfil, '--window-size=1920,1200', f'--virtual-time-budget={orcamento}', '--dump-dom', url)
        achado = re.search(r'RESULTADO:(\{.*?\})\s*</pre>', saida, re.S)
        if achado:
            return json.loads(html.unescape(achado.group(1)))
    return {'ok': False, 'problemas': ['A conferência não terminou (HTML incompleto ou sem internet?)']}


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    sem_png = '--sem-png' in sys.argv
    telas = sorted(TELAS.glob('[0-9][0-9][0-9]-*.html'))
    if args:
        telas = [t for t in telas if t.name[:3] in args]
    if not telas:
        sys.exit(f'Nenhuma tela encontrada em {TELAS.relative_to(RAIZ)}')

    binario = achar_chrome()
    srv = servidor()
    porta = srv.server_address[1]
    PNGS.mkdir(parents=True, exist_ok=True)
    reprovadas = 0
    with tempfile.TemporaryDirectory() as perfil:
        for tela in telas:
            rel = tela.relative_to(RAIZ).as_posix()
            url = f'http://127.0.0.1:{porta}/ferramentas/prototipos/conferir.html?tela={urllib.parse.quote(rel)}'
            resultado = conferir(binario, perfil, url)
            if resultado['ok']:
                print(f'✅ {tela.name}')
            else:
                reprovadas += 1
                print(f'❌ {tela.name}')
                for p in resultado['problemas']:
                    print(f'   - {p}')
            if not sem_png:
                png = PNGS / tela.with_suffix('.png').name
                chrome(binario, perfil, '--window-size=375,812', '--force-device-scale-factor=2', '--virtual-time-budget=6000',
                       f'--screenshot={png}', url + '&modo=captura')
                print(f'   📸 {png.relative_to(RAIZ).as_posix()}' if png.exists() else '   ⚠️ captura falhou')
    srv.shutdown()
    print(f'\n{len(telas) - reprovadas} de {len(telas)} telas aprovadas.')
    sys.exit(1 if reprovadas else 0)


if __name__ == '__main__':
    main()
