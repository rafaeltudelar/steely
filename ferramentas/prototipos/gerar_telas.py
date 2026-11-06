#!/usr/bin/env python3
"""Gera as telas 001-006 (Sprint 13) do Steely em HTML.

Cada arquivo tem 1920x1200 com o celular de 375x812 em (773, 194), igual as telas
ja importadas no Figma, para importar com o plugin html.to.design.

Uso:  python3 ferramentas/prototipos/gerar_telas.py [pasta-de-saida]
Padrao: docs/05-design/prototipos/html/
Depois: python3 ferramentas/prototipos/verificar_telas.py  (cores, fontes, estrutura)
        python3 ferramentas/prototipos/conferir_telas.py   (layout + capturas PNG)
"""
import sys, pathlib, base64

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / 'docs/05-design/prototipos/html'
OUT.mkdir(parents=True, exist_ok=True)
LOGO = 'data:image/png;base64,' + base64.b64encode((AQUI / 'assets/logo-steely.png').read_bytes()).decode()

I = {
 'x':'<path d="M18 6 6 18M6 6l12 12"/>',
 'left':'<path d="m15 18-6-6 6-6"/>',
 'right':'<path d="m9 18 6-6-6-6"/>',
 'down':'<path d="m6 9 6 6 6-6"/>',
 'camera':'<path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/><circle cx="12" cy="13" r="3"/>',
 'image':'<rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.09-3.09a2 2 0 0 0-2.82 0L6 21"/>',
 'info':'<circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/>',
 'check':'<path d="M20 6 9 17l-5-5"/>',
 'checkc':'<circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/>',
 'tag':'<path d="M12.586 2.586A2 2 0 0 0 11.172 2H4a2 2 0 0 0-2 2v7.172a2 2 0 0 0 .586 1.414l8.704 8.704a2.426 2.426 0 0 0 3.42 0l6.58-6.58a2.426 2.426 0 0 0 0-3.42z"/><circle cx="7.5" cy="7.5" r=".5"/>',
 'msg':'<path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/>',
 'cal':'<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
 'shield':'<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/>',
 'coins':'<circle cx="8" cy="8" r="6"/><path d="M18.09 10.37A6 6 0 1 1 10.34 18M7 6h1v4M16.71 13.88l.7.71-2.82 2.82"/>',
 'trash':'<path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>',
 'pencil':'<path d="M21.174 6.812a1 1 0 0 0-3.986-3.987L3.842 16.174a2 2 0 0 0-.5.83l-1.321 4.352a.5.5 0 0 0 .623.622l4.353-1.32a2 2 0 0 0 .83-.497z"/>',
 'alert':'<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4M12 17h.01"/>',
 'sparkles':'<path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"/>',
 'chart':'<path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/>',
 'users':'<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>',
 'qr':'<rect x="3" y="3" width="5" height="5" rx="1"/><rect x="16" y="3" width="5" height="5" rx="1"/><rect x="3" y="16" width="5" height="5" rx="1"/><path d="M21 16h-3a2 2 0 0 0-2 2v3M21 21v.01M12 7v3a2 2 0 0 1-2 2H7M3 12h.01M12 3h.01M12 16v.01M16 12h1M21 12v.01M12 21v-1"/>',
 'eye':'<path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0"/><circle cx="12" cy="12" r="3"/>',
 'bell':'<path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/>',
 'pin':'<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
 'scan':'<path d="M3 7V5a2 2 0 0 1 2-2h2M17 3h2a2 2 0 0 1 2 2v2M21 17v2a2 2 0 0 1-2 2h-2M7 21H5a2 2 0 0 1-2-2v-2"/><path d="M7 12h10"/>',
 'gpu':'<rect x="2" y="6" width="20" height="12" rx="2"/><circle cx="9" cy="12" r="3"/><circle cx="16.5" cy="12" r="2"/><path d="M6 18v2M10 18v2M14 18v2"/>',
 'leaf':'<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/>',
 'zap':'<path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z"/>',
 'lock':'<rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
 'plus':'<path d="M5 12h14M12 5v14"/>',
 'search':'<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
 'sliders':'<path d="M21 4h-7M10 4H3M21 12h-9M8 12H3M21 20h-5M12 20H3M14 2v4M8 10v4M16 18v4"/>',
 'heart':'<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>',
 'home':'<path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"/><path d="M3 10a2 2 0 0 1 .709-1.528l7-5.999a2 2 0 0 1 2.582 0l7 5.999A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>',
 'user':'<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
 'cpu':'<rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6" rx="1"/><path d="M15 2v2M15 20v2M2 15h2M2 9h2M20 15h2M20 9h2M9 2v2M9 20v2"/>',
 'memory':'<path d="M6 19v-3M10 19v-3M14 19v-3M18 19v-3M8 11V9M16 11V9M12 11V9M2 15h20M2 7a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v1.1a2 2 0 0 0 0 3.837V17a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2v-5.1a2 2 0 0 0 0-3.837Z"/>',
}
C = {'w':'#FFFFFF','m':'#6B7A8D','g':'#1DDB6A','e':'#A8EFC4','r':'#FF5A5F','d':'#0D1B2A'}

def ic(name, size=18, color='m', sw=2):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{C[color]}" '
            f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">{I[name]}</svg>')

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{width:1920px;height:1200px;background:#070F18;font-family:'DM Sans',sans-serif;color:#FFFFFF;position:relative;overflow:hidden;-webkit-font-smoothing:antialiased}
.phone{position:absolute;left:773px;top:194px;width:375px;height:812px;background:#0D1B2A;border:2px solid #1A3250;border-radius:44px;overflow:hidden}
.notch{position:absolute;top:0;left:122px;width:126px;height:30px;background:#070F18;border-radius:0 0 16px 16px;z-index:5}
.screen{position:absolute;left:0;top:0;width:371px;padding:42px 24px 0 24px;display:flex;flex-direction:column;gap:18px}
.row{display:flex;align-items:center}
.col{display:flex;flex-direction:column}
.between{justify-content:space-between}
.grow{flex:1;min-width:0}
.h1{font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:24px;line-height:30px;color:#FFFFFF}
.h2{font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:18px;line-height:24px;color:#FFFFFF}
.h3{font-family:'Space Grotesk',sans-serif;font-weight:500;font-size:16px;line-height:22px;color:#FFFFFF}
.price{font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:16px;line-height:20px;color:#1DDB6A}
.big-price{font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:24px;line-height:30px;color:#FFFFFF}
.body{font-size:14px;line-height:20px;font-weight:400;color:#FFFFFF}
.small{font-size:13px;line-height:18px;font-weight:400;color:#6B7A8D}
.label{font-size:15px;line-height:20px;font-weight:600}
.label-s{font-size:13px;line-height:16px;font-weight:600;color:#FFFFFF}
.caption{font-size:11px;line-height:14px;font-weight:500;color:#6B7A8D}
.muted{color:#6B7A8D}.green{color:#1DDB6A}.white{color:#FFFFFF}.esg{color:#A8EFC4}.red{color:#FF5A5F}
.iconbtn{width:32px;height:32px;border:1px solid #1A3250;border-radius:8px;display:flex;align-items:center;justify-content:center;flex:none}
.topbar{display:flex;align-items:center;gap:12px;height:32px}
.topbar .title{flex:1;text-align:center}
.spacer32{width:32px;flex:none}
.steps{display:flex;gap:6px}
.steps div{flex:1;height:4px;border-radius:999px;background:#1A3250}
.steps div.on{background:#1DDB6A}
.steplabels{display:flex;justify-content:space-between;margin-top:8px}
.steplabels span{font-size:11px;line-height:14px;font-weight:500;color:#6B7A8D}
.steplabels span.on{color:#1DDB6A}
.steplabels span.done{color:#FFFFFF}
.field{display:flex;flex-direction:column;gap:8px}
.flabel{font-size:13px;line-height:17px;color:#6B7A8D;font-weight:400}
.flabel b{color:#FF5A5F;font-weight:400}
.input{min-height:49px;border:1px solid #1A3250;border-radius:12px;background:rgba(255,255,255,0.03);display:flex;align-items:center;gap:10px;padding:0 16px;font-size:14px;line-height:18px;color:#FFFFFF}
.input.ph{color:rgba(107,122,141,0.5)}
.input.focus{border-color:#1DDB6A}
.textarea{align-items:flex-start;padding:14px 16px;min-height:96px}
.hint{font-size:11px;line-height:14px;font-weight:500;color:#6B7A8D;display:flex;gap:6px;align-items:flex-start}
.info{display:flex;gap:10px;align-items:flex-start;padding:12px 14px;border-radius:12px;background:rgba(29,219,106,0.05);border:1px solid rgba(29,219,106,0.14)}
.info .small{flex:1}
.esgbox{background:rgba(168,239,196,0.08);border:1px solid rgba(168,239,196,0.2)}
.card{border:1px solid #1A3250;border-radius:12px;background:#11233A}
.opt{display:flex;gap:12px;align-items:flex-start;padding:12px 14px;border:1px solid #1A3250;border-radius:12px;background:rgba(255,255,255,0.03)}
.opt.sel{border-color:#1DDB6A;background:rgba(29,219,106,0.07)}
.radio{width:18px;height:18px;border-radius:999px;border:2px solid #1A3250;flex:none;margin-top:1px;display:flex;align-items:center;justify-content:center}
.opt.sel .radio{border-color:#1DDB6A}
.opt.sel .radio i{width:8px;height:8px;border-radius:999px;background:#1DDB6A;display:block}
.chip{height:32px;padding:0 14px;border-radius:999px;border:1px solid #1A3250;background:rgba(255,255,255,0.03);display:flex;align-items:center;gap:6px;font-size:13px;line-height:16px;font-weight:600;color:#6B7A8D;flex:none}
.chip.on{background:#1DDB6A;border-color:#1DDB6A;color:#0D1B2A}
.chip .count{min-width:18px;height:18px;border-radius:999px;background:#0D1B2A;color:#1DDB6A;font-size:11px;line-height:14px;font-weight:600;display:flex;align-items:center;justify-content:center;padding:0 5px}
.tagchip{height:28px;padding:0 10px;border-radius:999px;background:rgba(29,219,106,0.12);display:flex;align-items:center;gap:6px;font-size:11px;line-height:14px;font-weight:500;color:#1DDB6A}
.toggle{width:44px;height:26px;border-radius:999px;background:#1DDB6A;position:relative;flex:none}
.toggle i{position:absolute;right:3px;top:3px;width:20px;height:20px;border-radius:999px;background:#0D1B2A;display:block}
.footer{position:absolute;left:0;bottom:0;width:371px;padding:14px 24px 26px 24px;background:#0D1B2A;border-top:1px solid #1A3250;display:flex;gap:12px;z-index:4}
.btn{height:48px;border-radius:12px;font-size:15px;line-height:20px;font-weight:600;display:flex;align-items:center;justify-content:center;gap:8px}
.btn.primary{background:#1DDB6A;color:#0D1B2A;flex:1}
.btn.secondary{background:rgba(255,255,255,0.03);border:1px solid #1A3250;color:#FFFFFF;padding:0 18px}
.btn.small{height:34px;border-radius:8px;font-size:13px;line-height:16px;padding:0 12px}
.tile{border-radius:12px;display:flex;align-items:center;justify-content:center;position:relative;flex:none}
.photo{background:linear-gradient(160deg,#1A3250 0%,#11233A 100%);border:1px solid #1A3250}
.addtile{border:1.5px dashed #1DDB6A;background:rgba(29,219,106,0.05);flex-direction:column;gap:6px}
.emptytile{border:1.5px dashed #1A3250}
.badge-cover{position:absolute;left:8px;bottom:8px;height:22px;padding:0 8px;border-radius:999px;background:rgba(13,27,42,0.85);display:flex;align-items:center;gap:4px;font-size:11px;line-height:14px;font-weight:500;color:#1DDB6A}
.rm{position:absolute;right:6px;top:6px;width:22px;height:22px;border-radius:999px;background:rgba(13,27,42,0.85);display:flex;align-items:center;justify-content:center}
.ord{position:absolute;left:6px;top:6px;width:20px;height:20px;border-radius:999px;background:rgba(13,27,42,0.85);font-size:11px;line-height:14px;font-weight:600;color:#FFFFFF;display:flex;align-items:center;justify-content:center}
.notif{display:flex;gap:12px;padding:12px 14px;border-radius:12px;border:1px solid #1A3250;background:rgba(255,255,255,0.03);position:relative}
.notif.unread{background:rgba(29,219,106,0.05);border-color:rgba(29,219,106,0.14)}
.nicon{width:40px;height:40px;border-radius:12px;display:flex;align-items:center;justify-content:center;flex:none}
.ng{background:rgba(29,219,106,0.12)}.ne{background:rgba(168,239,196,0.12)}.nr{background:rgba(255,90,95,0.12)}.nm{background:rgba(107,122,141,0.16)}
.dot{width:8px;height:8px;border-radius:999px;background:#1DDB6A;flex:none}
.group{font-size:11px;line-height:14px;font-weight:600;color:#6B7A8D;letter-spacing:0.6px;text-transform:uppercase}
.divider{height:1px;background:#1A3250}
.summary-row{display:flex;justify-content:space-between;align-items:center;padding:9px 0}
.logo{height:34px;width:auto;display:block;margin-left:-6px}
.avatar{width:40px;height:40px;border-radius:999px;background:#1A3250;border:1.5px solid rgba(29,219,106,0.6);display:flex;align-items:center;justify-content:center;flex:none}
.bell{width:40px;height:40px;border-radius:12px;border:1px solid #1A3250;background:rgba(255,255,255,0.03);display:flex;align-items:center;justify-content:center;position:relative;flex:none}
.bell i{position:absolute;right:9px;top:8px;width:9px;height:9px;border-radius:999px;background:#FF5A5F;border:2px solid #0D1B2A;display:block}
.search{height:48px;border:1px solid #1A3250;border-radius:12px;background:rgba(255,255,255,0.03);display:flex;align-items:center;gap:8px;padding:0 6px 0 14px}
.search .ph{flex:1;font-size:14px;line-height:18px;color:rgba(107,122,141,0.7)}
.filter{width:36px;height:36px;border-radius:8px;background:rgba(29,219,106,0.12);display:flex;align-items:center;justify-content:center}
.chips{display:flex;gap:8px;overflow:hidden;margin-right:-24px}
.banner{display:flex;gap:12px;align-items:center;padding:14px 16px;border-radius:18px;background:rgba(29,219,106,0.07);border:1px solid rgba(29,219,106,0.22)}
.carousel{display:flex;gap:12px;overflow:hidden;margin-right:-24px}
.ocard{width:156px;flex:none;border:1px solid #1A3250;border-radius:12px;background:#11233A;overflow:hidden}
.ocard .media{height:104px;background:#1A3250;position:relative;display:flex;align-items:center;justify-content:center}
.imp{position:absolute;left:8px;top:8px;height:22px;padding:0 8px;border-radius:999px;background:rgba(13,27,42,0.85);display:flex;align-items:center;gap:4px;font-size:11px;line-height:14px;font-weight:500;color:#1DDB6A}
.fav{position:absolute;right:8px;top:8px;width:28px;height:28px;border-radius:999px;background:rgba(13,27,42,0.85);display:flex;align-items:center;justify-content:center}
.ocard .info2{padding:10px 10px 12px;display:flex;flex-direction:column;gap:4px}
.nav{position:absolute;left:0;bottom:0;width:371px;height:84px;padding:10px 20px 0;background:rgba(13,27,42,0.96);border-top:1px solid #1A3250;display:flex;justify-content:space-between;align-items:flex-start;z-index:4}
.navitem{width:56px;display:flex;flex-direction:column;align-items:center;gap:4px;padding-top:6px;font-size:11px;line-height:14px;font-weight:500;color:#6B7A8D}
.navitem.on{color:#1DDB6A}
.navitem.add{padding-top:0;gap:2px}
.fab{width:48px;height:48px;border-radius:999px;background:#1DDB6A;display:flex;align-items:center;justify-content:center}
"""

HEAD = ('<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8"><title>{title}</title>'
        '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;700&display=swap" rel="stylesheet">'
        '<style>{css}</style></head><body><div class="phone"><div class="notch"></div>')
TAIL = '</div></body></html>'

def page(fname, title, inner):
    (OUT / fname).write_text(HEAD.format(title=title, css=CSS) + inner + TAIL, encoding='utf-8')

def stepper(n, name):
    labels = ['Fotos', 'Detalhes', 'Preço e entrega', 'Revisão']
    bars = ''.join(f'<div class="{"on" if i < n else ""}"></div>' for i in range(4))
    lab = ''.join(f'<span class="{"on" if i == n-1 else ("done" if i < n-1 else "")}">{l}</span>' for i, l in enumerate(labels))
    return (f'<div class="topbar"><div class="iconbtn">{ic("left" if n>1 else "x",16,"w")}</div>'
            f'<div class="title label white">Criar anúncio</div><div class="spacer32"></div></div>'
            f'<div class="col" style="gap:4px"><span class="caption green">ETAPA {n} DE 4</span><span class="h1">{name}</span></div>'
            f'<div><div class="steps">{bars}</div><div class="steplabels">{lab}</div></div>')

def footer(primary, back=True, icon=None):
    b = f'<div class="btn secondary">Voltar</div>' if back else ''
    i = ic(icon, 18, 'd', 2.2) if icon else ''
    return f'<div class="footer">{b}<div class="btn primary">{i}{primary}</div></div>'

# ---------------- 001 Home / Feed ----------------
def ocard(icon, title, price, boosted=False):
    b = f'<div class="imp">{ic("zap",11,"g",2.2)}Impulsionado</div>' if boosted else ''
    return (f'<div class="ocard"><div class="media">{ic(icon,40,"m",1.5)}{b}<div class="fav">{ic("heart",14,"w")}</div></div>'
            f'<div class="info2"><span class="label-s" style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{title}</span>'
            f'<span class="price">{price}</span></div></div>')
def orow(icon, title, meta, price, esg=False):
    e = f'<span class="tagchip" style="height:20px;background:rgba(168,239,196,0.14);color:#A8EFC4">{ic("leaf",11,"e")}Reuso</span>' if esg else ''
    return (f'<div class="card row" style="gap:12px;padding:10px"><div class="tile photo" style="width:56px;height:56px">{ic(icon,26,"m",1.5)}</div>'
            f'<div class="col grow" style="gap:4px"><span class="label-s">{title}</span><span class="row caption" style="gap:6px">{ic("pin",11,"m")}{meta}{e}</span></div>'
            f'<span class="price">{price}</span></div>')
def navitem(icon, label, on=False):
    return f'<div class="navitem{" on" if on else ""}">{ic(icon,22,"g" if on else "m")}<span>{label}</span></div>'
n001 = f'''<div class="screen" style="gap:14px">
<div class="row between"><img class="logo" src="{LOGO}" alt="Steely"><div class="row" style="gap:10px"><div class="bell">{ic("bell",18,"w")}<i></i></div><div class="avatar">{ic("user",18,"w")}</div></div></div>
<div class="col" style="gap:4px"><span class="h1">Olá, Rafael</span><span class="row small" style="gap:6px">{ic("pin",13,"g")}Maringá, PR · raio de 25 km</span></div>
<div class="search">{ic("search",18,"m")}<span class="ph">Buscar peças e componentes</span><div class="filter">{ic("sliders",16,"g")}</div></div>
<div class="chips"><div class="chip on">Todos</div><div class="chip">GPU</div><div class="chip">Processador</div><div class="chip">Memória</div><div class="chip">Placa-mãe</div></div>
<div class="banner"><div class="tile" style="width:44px;height:44px;background:rgba(29,219,106,0.12)">{ic("scan",22,"g",1.75)}</div>
<div class="col grow" style="gap:2px"><span class="h3">Scanner IA</span><span class="small">Anuncie em segundos com IA.</span></div>{ic("right",18,"g")}</div>
<div class="row between"><span class="h2">Em destaque</span><span class="label-s green">Ver tudo</span></div>
<div class="carousel">{ocard("gpu","RTX 3060 Ti 8GB","R$ 1.650",True)}{ocard("cpu","Ryzen 7 5700X","R$ 980")}{ocard("memory","Kit 16GB DDR4","R$ 260")}</div>
<div class="row between"><span class="h2">Perto de você</span><span class="label-s green">Ver mapa</span></div>
{orow("gpu","GTX 1660 Super 6GB","2,1 km","R$ 890",True)}
</div>
<div class="nav">{navitem("home","Início",True)}{navitem("search","Buscar")}<div class="navitem add"><div class="fab">{ic("plus",22,"d",2.4)}</div><span>Anunciar</span></div>{navitem("msg","Chat")}{navitem("user","Perfil")}</div>'''
page('001-home-feed.html', '001 · Home / Feed', n001)

# ---------------- 002 Central de Notificações ----------------
def notif(icon, tone, color, title, text, time, unread=False, actions=''):
    d = '<div class="dot" style="margin-top:6px"></div>' if unread else ''
    return (f'<div class="notif{" unread" if unread else ""}"><div class="nicon {tone}">{ic(icon,20,color)}</div>'
            f'<div class="col grow" style="gap:4px"><div class="row between" style="gap:8px"><span class="label-s grow">{title}</span>'
            f'<span class="caption">{time}</span>{d}</div><span class="small">{text}</span>{actions}</div></div>')

n002 = f'''<div class="screen" style="gap:14px">
<div class="topbar"><div class="iconbtn">{ic("left",16,"w")}</div><div class="title h2">Notificações</div><div class="iconbtn" style="border:none">{ic("checkc",20,"g")}</div></div>
<div class="chips"><div class="chip on">Todas <span class="count">3</span></div><div class="chip">Negociações</div><div class="chip">Anúncios</div><div class="chip">Conta</div></div>
<div class="row between"><span class="group">Hoje</span><span class="label-s green">Marcar todas como lidas</span></div>
{notif("tag","ng","g","Nova proposta recebida","Lucas M. ofereceu <span class='white'>R$ 1.500</span> pela RTX 3060 Ti 8GB. Válida por 24 h.","10 min",True,
 '<div class="row" style="gap:8px;margin-top:6px"><div class="btn primary small" style="flex:none">Ver proposta</div><div class="btn secondary small">Recusar</div></div>')}
{notif("cal","ng","g","Confirme o encontro","Ana P. propôs amanhã, 18h, no Shopping Catuaí. Responda em até 24 h.","1 h",True)}
{notif("msg","ng","g","Nova mensagem","Ana P.: “Ainda está disponível? Consigo buscar hoje.”","2 h",True)}
<span class="group">Ontem</span>
{notif("checkc","ne","e","Anúncio publicado","“Ryzen 5 5600 + cooler box” passou na moderação e já aparece nas buscas.","ontem")}
<span class="group">Esta semana</span>
{notif("shield","nr","r","Novo acesso à sua conta","iPhone · Maringá, PR. Se não foi você, altere sua senha agora.","seg")}
</div>'''
page('002-central-de-notificacoes.html', '002 · Central de Notificações', n002)

# ---------------- 003 Etapa 1: Fotos ----------------
photo = lambda w, h, n, cover=False, isz=40: (
    f'<div class="tile photo" style="width:{w}px;height:{h}px">{ic("gpu",isz,"m",1.5)}'
    f'<div class="ord">{n}</div><div class="rm">{ic("x",12,"w",2.5)}</div>'
    + (f'<div class="badge-cover">{ic("image",12,"g")}Capa</div>' if cover else '') + '</div>')
n003 = f'''<div class="screen" style="gap:14px">
{stepper(1,"Fotos do item")}
<div class="info" style="padding:14px;border-radius:18px;background:rgba(29,219,106,0.07);border-color:rgba(29,219,106,0.2)">
<div class="tile" style="width:44px;height:44px;background:rgba(29,219,106,0.12);border:1px solid rgba(29,219,106,0.22)">{ic("scan",22,"g",1.75)}</div>
<div class="col grow" style="gap:4px"><span class="h3">Use o Scanner IA</span><span class="small">Fotografe a etiqueta e a IA preenche os detalhes. <span class="esg">+20 moedas</span></span></div></div>
<div class="row between"><span class="label-s">Suas fotos</span><span class="caption"><span class="white">3</span> de 10</span></div>
<div class="col" style="gap:10px">
<div class="row" style="gap:10px">{photo(212,212,1,True,64)}<div class="col" style="gap:10px">{photo(101,101,2)}{photo(101,101,3)}</div></div>
<div class="row" style="gap:10px"><div class="tile addtile" style="width:101px;height:101px">{ic("camera",22,"g")}<span class="caption green">Adicionar</span></div>
<div class="tile emptytile" style="width:101px;height:101px">{ic("image",20,"m",1.5)}</div><div class="tile emptytile" style="width:101px;height:101px">{ic("image",20,"m",1.5)}</div></div>
</div>
<div class="hint">{ic("info",13,"m")}<span>Arraste para reordenar. JPG, PNG ou HEIC até 5 MB; a localização das fotos é removida.</span></div>
</div>
{footer("Continuar", back=False)}'''
page('003-criar-anuncio-etapa-1-fotos.html', '003 · Criar Anúncio — Fotos', n003)

# ---------------- 004 Etapa 2: Detalhes ----------------
n004 = f'''<div class="screen" style="gap:10px">
{stepper(2,"Detalhes do item")}
<div class="info"><div style="margin-top:1px">{ic("sparkles",18,"g")}</div><div class="col grow" style="gap:2px"><span class="label-s">Identificado pelo Scanner IA</span><span class="small">RTX 3060 Ti 8GB · <span class="green">94% de confiança</span></span></div></div>
<div class="field"><span class="flabel">Título <b>*</b></span><div class="input">RTX 3060 Ti 8GB Gigabyte Gaming OC</div></div>
<div class="row" style="gap:10px"><div class="field grow"><span class="flabel">Categoria <b>*</b></span><div class="input between">Placa de vídeo {ic("down",16,"m")}</div></div>
<div class="field grow"><span class="flabel">Tempo de uso <b>*</b></span><div class="input between">1 a 2 anos {ic("down",16,"m")}</div></div></div>
<div class="field"><span class="flabel">Estado de conservação <b>*</b></span>
<div class="row" style="gap:10px"><div class="opt sel grow" style="align-items:center"><div class="radio" style="margin:0"><i></i></div><span class="label-s">Funciona</span></div>
<div class="opt grow" style="align-items:center"><div class="radio" style="margin:0"></div><span class="label-s">Com defeito</span></div></div>
<div class="hint">{ic("info",13,"m")}<span>Com defeito exige fotos detalhadas do problema.</span></div></div>
<div class="field"><span class="flabel">Especificações técnicas</span><div class="row" style="gap:6px;flex-wrap:wrap">
<span class="tagchip">8 GB GDDR6</span><span class="tagchip">PCIe 4.0</span><span class="tagchip">200 W</span><span class="tagchip">{ic("plus",12,"g",2.5)}Adicionar</span></div></div>
<div class="field"><span class="flabel">Descrição</span><div class="input textarea" style="min-height:60px;padding:12px 16px">Usada em PC gamer, nunca minerou. Acompanha caixa original.</div>
<div class="hint">{ic("shield",13,"m")}<span>Não informe telefone, e-mail ou endereço — dados pessoais são ocultados.</span></div></div>
</div>
{footer("Continuar")}'''
page('004-criar-anuncio-etapa-2-detalhes.html', '004 · Criar Anúncio — Detalhes', n004)

# ---------------- 005 Etapa 3: Preço e entrega ----------------
n005 = f'''<div class="screen" style="gap:11px">
{stepper(3,"Preço e entrega")}
<div class="field"><span class="flabel">Preço <b>*</b></span><div class="input focus" style="height:52px"><span class="big-price muted" style="font-size:18px">R$</span><span class="big-price">1.650</span></div></div>
<div class="info" style="flex-direction:column;gap:10px;align-items:stretch"><div class="row" style="gap:8px">{ic("chart",16,"g")}<span class="label-s grow">Referência do modelo</span><span class="price" style="font-size:14px">R$ 1.550 – 1.800</span></div>
<div style="position:relative;width:100%;height:6px;border-radius:999px;background:#1A3250"><div style="position:absolute;left:30%;width:45%;height:6px;border-radius:999px;background:#1DDB6A"></div><div style="position:absolute;left:47%;top:-4px;width:14px;height:14px;border-radius:999px;background:#FFFFFF;border:3px solid #1DDB6A"></div></div>
<span class="caption">Seu preço está dentro da faixa das últimas negociações.</span></div>
<div class="opt" style="align-items:center"><div class="col grow" style="gap:2px"><span class="label-s">Aceitar propostas</span><span class="caption">Mínimo aceito: <span class="white">R$ 1.450</span></span></div><div class="toggle"><i></i></div></div>
<div class="field"><span class="flabel">Forma de entrega <b>*</b></span>
<div class="opt sel"><div class="radio"><i></i></div><div class="col grow" style="gap:2px"><span class="label-s">Encontro em ponto seguro</span><span class="caption">Combine pelo chat; confirmação por QR Code.</span></div>{ic("qr",18,"g")}</div>
<div class="opt"><div class="radio"></div><div class="col grow" style="gap:2px"><span class="label-s">Retirada com o vendedor</span><span class="caption">O comprador busca com você.</span></div>{ic("users",18,"m")}</div></div>
<div class="field"><span class="flabel">Localização aproximada <b>*</b></span><div class="input between"><span class="row" style="gap:8px">{ic("pin",16,"g")}Zona 7, Maringá – PR</span>{ic("down",16,"m")}</div>
<div class="hint">{ic("eye",13,"m")}<span>Os compradores veem só o bairro, nunca o seu endereço.</span></div></div>
</div>
{footer("Continuar")}'''
page('005-criar-anuncio-etapa-3-preco-e-entrega.html', '005 · Criar Anúncio — Preço e entrega', n005)

# ---------------- 006 Etapa 4: Revisão e publicação ----------------
def srow(icon, title, value):
    return (f'<div class="summary-row"><div class="row" style="gap:10px">{ic(icon,16,"m")}<div class="col" style="gap:2px">'
            f'<span class="caption">{title}</span><span class="label-s">{value}</span></div></div>'
            f'<span class="row label-s green" style="gap:4px">{ic("pencil",13,"g")}Editar</span></div>')
n006 = f'''<div class="screen" style="gap:13px">
{stepper(4,"Revise e publique")}
<div class="card" style="overflow:hidden"><div class="tile photo" style="width:321px;height:112px;border-radius:0;border:none">{ic("gpu",52,"m",1.5)}<div class="badge-cover">{ic("image",12,"g")}3 fotos</div></div>
<div class="col" style="gap:4px;padding:12px 14px 14px"><span class="label-s" style="font-size:15px;line-height:20px">RTX 3060 Ti 8GB Gigabyte Gaming OC</span>
<div class="row" style="gap:8px"><span class="caption">Usado · Funciona perfeitamente</span><span class="tagchip" style="height:20px;background:rgba(168,239,196,0.14);color:#A8EFC4">{ic("leaf",11,"e")}Reuso</span></div>
<div class="row between" style="margin-top:2px"><span class="price" style="font-size:20px;line-height:26px">R$ 1.650</span><span class="row caption" style="gap:4px">{ic("pin",12,"m")}Zona 7, Maringá</span></div></div></div>
<div class="col" style="padding:0 2px">{srow("tag","Categoria e estado","Placa de vídeo · 1 a 2 anos de uso")}<div class="divider"></div>{srow("users","Propostas","Aceita a partir de R$ 1.450")}<div class="divider"></div>{srow("qr","Entrega","Encontro em ponto seguro")}</div>
<div class="info esgbox"><div style="margin-top:1px">{ic("coins",18,"e")}</div><span class="small">Você ganha <span class="esg">+20 moedas</span> pelo Scanner IA.</span></div>
<div class="row" style="gap:10px;align-items:flex-start"><div class="tile" style="width:20px;height:20px;border-radius:6px;background:#1DDB6A">{ic("check",14,"d",3)}</div><span class="small">Declaro que o item é meu e as informações são verdadeiras. Haverá moderação automática.</span></div>
</div>
{footer("Publicar anúncio", icon="zap")}'''
page('006-criar-anuncio-etapa-4-revisao.html', '006 · Criar Anúncio — Revisão e publicação', n006)
print('ok', sorted(p.name for p in OUT.glob('*.html')))
