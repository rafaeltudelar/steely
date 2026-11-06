// Visualizador navegável das telas da Sprint 13.
// Carrega o HTML real de cada tela num iframe (mesma origem) e liga os botões da tela à próxima.
const BASE = location.pathname.includes('/site/') ? '../docs/05-design/prototipos/html/' : 'prototipos/html/';

const TELAS = [
  { n: '001', nome: 'Home / Feed', arq: '001-home-feed.html',
    links: { '.bell': '002', '.fab': '003', '.navitem.add': '003' } },
  { n: '002', nome: 'Central de Notificações', arq: '002-central-de-notificacoes.html',
    links: { '.topbar .iconbtn:first-child': '001' } },
  { n: '003', nome: 'Criar anúncio · Fotos', arq: '003-criar-anuncio-etapa-1-fotos.html',
    links: { '.footer .btn.primary': '004', '.topbar .iconbtn:first-child': '001' } },
  { n: '004', nome: 'Criar anúncio · Detalhes', arq: '004-criar-anuncio-etapa-2-detalhes.html',
    links: { '.footer .btn.primary': '005', '.footer .btn.secondary': '003', '.topbar .iconbtn:first-child': '003' } },
  { n: '005', nome: 'Criar anúncio · Preço e entrega', arq: '005-criar-anuncio-etapa-3-preco-e-entrega.html',
    links: { '.footer .btn.primary': '006', '.footer .btn.secondary': '004', '.topbar .iconbtn:first-child': '004' } },
  { n: '006', nome: 'Criar anúncio · Revisão', arq: '006-criar-anuncio-etapa-4-revisao.html',
    links: { '.footer .btn.primary': '001!', '.footer .btn.secondary': '005', '.topbar .iconbtn:first-child': '005' } },
];

const frame = document.getElementById('tela');
const lista = document.getElementById('lista-telas');
const moldura = document.querySelector('.celular-moldura');
const aviso = document.getElementById('aviso');
const reduzido = matchMedia('(prefers-reduced-motion: reduce)').matches;
let atual = null;

lista.innerHTML = TELAS.map((t) =>
  `<li><button type="button" data-n="${t.n}"><span class="num">${t.n}</span>${t.nome}</button></li>`).join('');
lista.addEventListener('click', (e) => {
  const b = e.target.closest('button');
  if (b) abrir(b.dataset.n);
});

function avisar(texto) {
  aviso.textContent = texto;
  aviso.classList.add('visivel');
  setTimeout(() => aviso.classList.remove('visivel'), 2200);
}

function abrir(destino) {
  const publicou = destino.endsWith('!');
  const n = destino.replace('!', '');
  const tela = TELAS.find((t) => t.n === n);
  if (!tela || tela === atual) return;
  atual = tela;
  lista.querySelectorAll('button').forEach((b) => b.setAttribute('aria-current', String(b.dataset.n === n)));
  const trocar = () => { frame.src = BASE + tela.arq; };
  if (reduzido) trocar();
  else { frame.classList.add('saindo'); setTimeout(trocar, 160); }
  if (publicou) setTimeout(() => avisar('Anúncio publicado! +20 moedas'), 350);
}

frame.addEventListener('load', () => {
  frame.classList.remove('saindo');
  const doc = frame.contentDocument;
  if (!doc || !atual) return;
  const estilo = doc.createElement('style');
  estilo.textContent = '[data-link]{cursor:pointer;transition:filter .15s}[data-link]:hover{filter:brightness(1.15)}';
  doc.head.appendChild(estilo);
  for (const [seletor, destino] of Object.entries(atual.links)) {
    doc.querySelectorAll(seletor).forEach((el) => {
      el.dataset.link = destino;
      el.addEventListener('click', (e) => { e.stopPropagation(); abrir(destino); });
    });
  }
});

// Ajusta a escala do celular ao espaço disponível
function escalar() {
  const largura = Math.min(moldura.parentElement.clientWidth, window.innerWidth - 32);
  const e = Math.min(1, largura / 375, (window.innerHeight - 120) / 812);
  moldura.style.setProperty('--e', Math.max(e, 0.6).toFixed(3));
}
addEventListener('resize', escalar);
escalar();
abrir('001');
