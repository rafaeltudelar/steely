// Movimento do site com Motion (motion.dev), versão fixa no importmap.
// Cada animação mostra uma mudança de estado: entrada do conteúdo, progresso da leitura,
// etapas da jornada e profundidade do celular. Com "reduzir movimento" nada se mexe.
import { animate, inView, scroll, stagger } from 'motion';

const raiz = document.documentElement;
const reduzido = matchMedia('(prefers-reduced-motion: reduce)').matches;
window.__movimento = true;

const mola = { type: 'spring', visualDuration: 0.6, bounce: 0.15 };

if (reduzido) {
  raiz.classList.remove('anim');
} else {
  iniciar();
}

function iniciar() {
  // Topo: entra em cascata
  animate('[data-hero]', { opacity: [0, 1], y: [28, 0] }, { ...mola, delay: stagger(0.08, { startDelay: 0.05 }) });

  // Números contam até o valor final
  inView('.numeros', () => {
    document.querySelectorAll('[data-contar]').forEach((el, i) => {
      const alvo = Number(el.dataset.contar);
      animate(0, alvo, { duration: 1.2, delay: 0.4 + i * 0.1, ease: 'easeOut', onUpdate: (v) => { el.textContent = Math.round(v); } });
    });
  }, { amount: 0.6 });

  // Títulos e textos aparecem ao entrar na tela
  inView('[data-revelar]', (el) => {
    animate(el, { opacity: 1, y: [24, 0] }, mola);
  }, { amount: 0.4 });

  // Grupos (cartões, equipe): filhos em cascata
  inView('[data-grupo]', (grupo) => {
    animate([...grupo.children], { opacity: 1, y: [32, 0] }, { ...mola, delay: stagger(0.07) });
  }, { amount: 0.2 });

  // Barra de progresso da leitura
  scroll(animate('.progresso', { scaleX: [0, 1] }, { ease: 'linear' }));

  // A cena 3D recua um pouco enquanto a página sobe
  const hero = document.querySelector('.hero');
  scroll(animate('.palco', { y: [0, 60], scale: [1, 0.94], opacity: [1, 0.55] }, { ease: 'linear' }),
    { target: hero, offset: ['start start', 'end start'] });

  jornada();
  celular3d();
  cartoes3d();
}

// Linha do tempo: a linha cresce com a rolagem e cada etapa acende quando é alcançada
function jornada() {
  const trilha = document.getElementById('trilha');
  const linha = trilha.querySelector('.trilha-linha span');
  const etapas = [...trilha.querySelectorAll('.etapa')];
  const anel = document.querySelector('.progresso-anel');
  const num = document.getElementById('painel-num');
  const nome = document.getElementById('painel-nome');
  const de = document.getElementById('painel-de');
  const nomes = etapas.map((e) => e.querySelector('b').textContent.replace(/^\d+ · /, ''));
  const texto = num.parentElement;
  let ativa = 0;
  etapas.forEach((e) => e.classList.add('apagada'));
  scroll((p) => {
    linha.style.transform = `scaleY(${p})`;
    anel.style.strokeDashoffset = 1 - p;
    let alcancadas = 0;
    for (let i = 0; i < etapas.length; i++) {
      const acesa = p >= (i + 0.35) / etapas.length;
      etapas[i].classList.toggle('apagada', !acesa);
      if (acesa) alcancadas = i + 1;
    }
    const nova = Math.max(alcancadas, 1);
    if (nova !== ativa) {
      ativa = nova;
      num.textContent = String(nova).padStart(2, '0');
      nome.textContent = nomes[nova - 1];
      de.textContent = nova;
      animate(texto, { opacity: [0, 1], y: [14, 0], scale: [0.96, 1] }, { type: 'spring', visualDuration: 0.4, bounce: 0.2 });
    }
  }, { target: trilha, offset: ['start 75%', 'end 55%'] });
}

// O celular dos protótipos gira de leve até ficar de frente quando a seção chega
function celular3d() {
  const moldura = document.querySelector('.celular-moldura');
  scroll(animate(moldura, { rotateY: [-24, 0], rotateX: [12, 0], transformPerspective: [1400, 1400] }, { ease: 'linear' }),
    { target: document.getElementById('prototipos'), offset: ['start end', 'start 25%'] });
}

// Cartões inclinam na direção do ponteiro e mostram um brilho que o segue
function cartoes3d() {
  if (!matchMedia('(hover: hover)').matches) return;
  document.querySelectorAll('.cartao').forEach((c) => {
    c.addEventListener('pointermove', (e) => {
      const r = c.getBoundingClientRect();
      const x = (e.clientX - r.left) / r.width;
      const y = (e.clientY - r.top) / r.height;
      c.style.setProperty('--mx', `${x * 100}%`);
      c.style.setProperty('--my', `${y * 100}%`);
      animate(c, { rotateX: (0.5 - y) * 8, rotateY: (x - 0.5) * 10, transformPerspective: 900 }, { type: 'spring', stiffness: 220, damping: 22 });
    });
    c.addEventListener('pointerleave', () => {
      animate(c, { rotateX: 0, rotateY: 0 }, { type: 'spring', stiffness: 180, damping: 18 });
    });
  });
}
