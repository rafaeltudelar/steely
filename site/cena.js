// Cena 3D do topo: uma placa de vídeo low-poly sendo varrida pelo feixe do Scanner IA.
// Three.js r160 (versão fixa no importmap). Respeita prefers-reduced-motion e pausa fora da tela.
let THREE;

const COR = {
  charcoal: 0x0D1B2A, superficie: 0x11233A, borda: 0x1A3250,
  verde: 0x1DDB6A, esg: 0xA8EFC4, cinza: 0x6B7A8D, branco: 0xFFFFFF,
};

const canvas = document.getElementById('cena');
const palco = canvas.parentElement;
const etiquetas = [...document.querySelectorAll('#etiquetas span')];
const reduzido = matchMedia('(prefers-reduced-motion: reduce)').matches;

function suportaWebGL() {
  try { return !!document.createElement('canvas').getContext('webgl2'); } catch { return false; }
}

function semTresD() {
  // Sem WebGL ou sem acesso ao CDN: mostra só as etiquetas sobre o fundo.
  palco.classList.add('sem-3d');
  etiquetas.forEach((el, i) => {
    el.style.left = `${28 + (i % 2) * 44}%`;
    el.style.top = `${30 + Math.floor(i / 2) * 36}%`;
    el.classList.add('visivel');
  });
}

if (!suportaWebGL()) semTresD();
else import('three').then((m) => { THREE = m; iniciar(); }).catch(semTresD);

function iniciar() {
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;

  const cena = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(32, 1, 0.1, 100);
  camera.position.set(0, 0.6, 9.5);
  camera.lookAt(0, 0, 0);

  cena.add(new THREE.AmbientLight(COR.branco, 0.55));
  const sol = new THREE.DirectionalLight(COR.branco, 1.6);
  sol.position.set(3, 5, 6);
  cena.add(sol);
  const luzScan = new THREE.PointLight(COR.verde, 0, 5, 1.6);
  cena.add(luzScan);

  // ---------- Placa de vídeo ----------
  const gpu = new THREE.Group();
  cena.add(gpu);
  const plano = (cor, extra = {}) => new THREE.MeshStandardMaterial({ color: cor, roughness: 0.55, metalness: 0.35, flatShading: true, ...extra });
  const arestas = new THREE.LineBasicMaterial({ color: COR.verde, transparent: true, opacity: 0.18 });

  function bloco(w, h, d, mat, x = 0, y = 0, z = 0) {
    const geo = new THREE.BoxGeometry(w, h, d);
    const m = new THREE.Mesh(geo, mat);
    m.position.set(x, y, z);
    m.add(new THREE.LineSegments(new THREE.EdgesGeometry(geo), arestas));
    gpu.add(m);
    return m;
  }

  bloco(4.4, 1.7, 0.18, plano(COR.charcoal), 0, 0, -0.18);          // placa (PCB)
  bloco(4.2, 1.6, 0.32, plano(COR.superficie), 0, 0.02, 0.07);       // carcaça
  bloco(0.08, 2.0, 0.55, plano(COR.cinza, { metalness: 0.8 }), -2.26, 0.08, -0.05); // espelho
  bloco(2.3, 0.14, 0.06, plano(COR.verde, { emissive: COR.verde, emissiveIntensity: 0.25 }), 0.35, -0.93, -0.18); // conector PCIe
  bloco(3.9, 0.06, 0.02, plano(COR.verde, { emissive: COR.verde, emissiveIntensity: 0.6 }), 0, 0.76, 0.24);      // filete de luz

  const helices = [];
  for (const x of [-1.0, 1.0]) {
    const aro = new THREE.Mesh(new THREE.TorusGeometry(0.66, 0.05, 6, 24), plano(COR.borda));
    aro.position.set(x, 0.02, 0.25);
    gpu.add(aro);
    const miolo = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.18, 0.08, 8), plano(COR.charcoal));
    miolo.rotation.x = Math.PI / 2;
    miolo.position.set(x, 0.02, 0.27);
    gpu.add(miolo);
    const helice = new THREE.Group();
    helice.position.set(x, 0.02, 0.24);
    for (let i = 0; i < 7; i++) {
      const pa = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.13, 0.02), plano(COR.cinza));
      pa.position.x = 0.38;
      const braco = new THREE.Group();
      braco.rotation.z = (i / 7) * Math.PI * 2;
      pa.rotation.x = 0.5;
      braco.add(pa);
      helice.add(braco);
    }
    gpu.add(helice);
    helices.push(helice);
  }
  gpu.rotation.set(-0.18, -0.38, 0.04);

  // ---------- Feixe do scanner ----------
  const grad = document.createElement('canvas');
  grad.width = 64; grad.height = 4;
  const g = grad.getContext('2d');
  const lg = g.createLinearGradient(0, 0, 64, 0);
  lg.addColorStop(0, 'rgba(29,219,106,0)');
  lg.addColorStop(0.75, 'rgba(29,219,106,0.35)');
  lg.addColorStop(1, 'rgba(29,219,106,1)');
  g.fillStyle = lg; g.fillRect(0, 0, 64, 4);
  const texFeixe = new THREE.CanvasTexture(grad);
  texFeixe.colorSpace = THREE.SRGBColorSpace;

  const feixe = new THREE.Mesh(
    new THREE.PlaneGeometry(0.9, 2.6),
    new THREE.MeshBasicMaterial({ map: texFeixe, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide }),
  );
  feixe.position.z = 0.45;
  gpu.add(feixe);
  const linha = new THREE.Mesh(new THREE.PlaneGeometry(0.025, 2.6), new THREE.MeshBasicMaterial({ color: COR.verde }));
  linha.position.z = 0.46;
  gpu.add(linha);

  // Partículas leves em volta (poeira digital)
  const pts = new Float32Array(180 * 3);
  for (let i = 0; i < 180; i++) {
    pts[i * 3] = (Math.random() - 0.5) * 9;
    pts[i * 3 + 1] = (Math.random() - 0.5) * 5;
    pts[i * 3 + 2] = (Math.random() - 0.5) * 4 - 1;
  }
  const geoPts = new THREE.BufferGeometry();
  geoPts.setAttribute('position', new THREE.BufferAttribute(pts, 3));
  const poeira = new THREE.Points(geoPts, new THREE.PointsMaterial({ color: COR.esg, size: 0.025, transparent: true, opacity: 0.5 }));
  cena.add(poeira);

  // Base holográfica: anel que pulsa sob a placa e uma grade que some nas bordas
  const base = new THREE.Group();
  base.position.y = -1.55;
  cena.add(base);
  const anel = new THREE.Mesh(new THREE.RingGeometry(2.3, 2.36, 96),
    new THREE.MeshBasicMaterial({ color: COR.verde, transparent: true, opacity: 0.55, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide }));
  anel.rotation.x = -Math.PI / 2;
  base.add(anel);
  const onda = anel.clone();
  onda.material = anel.material.clone();
  base.add(onda);
  const grade = new THREE.GridHelper(12, 30, COR.verde, COR.borda);
  grade.material.transparent = true;
  grade.material.opacity = 0.16;
  grade.material.depthWrite = false;
  base.add(grade);

  // ---------- Etiquetas (HTML) presas a pontos da placa ----------
  const ancoras = etiquetas.map((el) => new THREE.Vector3(+el.dataset.x, +el.dataset.y, 0.3));
  const tmp = new THREE.Vector3();
  function posicionarEtiquetas(xFeixe) {
    const w = canvas.clientWidth, h = canvas.clientHeight;
    etiquetas.forEach((el, i) => {
      tmp.copy(ancoras[i]);
      gpu.localToWorld(tmp).project(camera);
      el.style.left = `${(tmp.x * 0.5 + 0.5) * w}px`;
      el.style.top = `${(-tmp.y * 0.5 + 0.5) * h}px`;
      el.classList.toggle('visivel', xFeixe >= ancoras[i].x);
    });
  }

  // ---------- Tamanho, mouse, visibilidade ----------
  let zBase = 8.4;
  function ajustar() {
    const w = palco.clientWidth, h = palco.clientHeight;
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    zBase = w / h < 1.1 ? 11 : 8.4; // telas estreitas: afasta a câmera
    camera.position.z = zBase;
    camera.updateProjectionMatrix();
  }
  new ResizeObserver(ajustar).observe(palco);
  ajustar();

  const mouse = { x: 0, y: 0 };
  palco.addEventListener('pointermove', (e) => {
    const r = palco.getBoundingClientRect();
    mouse.x = ((e.clientX - r.left) / r.width) * 2 - 1;
    mouse.y = ((e.clientY - r.top) / r.height) * 2 - 1;
  });
  palco.addEventListener('pointerleave', () => { mouse.x = 0; mouse.y = 0; });

  if (reduzido) {
    // Sem movimento: um quadro só, com a varredura concluída.
    feixe.position.x = linha.position.x = 2.3;
    feixe.visible = false;
    gpu.updateMatrixWorld(true);
    renderer.render(cena, camera);
    posicionarEtiquetas(9);
    new ResizeObserver(() => { renderer.render(cena, camera); posicionarEtiquetas(9); }).observe(palco);
    return;
  }

  let rodando = false, ultimo = 0, t = 0;
  const CICLO = 6.5; // segundos por varredura
  function quadro(agora) {
    if (!rodando) return;
    const dt = Math.min((agora - ultimo) / 1000 || 0, 0.05);
    ultimo = agora;
    t += dt;

    const fase = (t % CICLO) / CICLO;                  // 0..1
    const ida = Math.min(fase / 0.62, 1);               // varre em 62% do ciclo, depois descansa
    const suave = ida < 1 ? 0.5 - Math.cos(ida * Math.PI) / 2 : 1;
    const x = -2.4 + suave * 4.8;
    feixe.position.x = x - 0.45;
    linha.position.x = x;
    const fim = fase > 0.9 ? 1 - (fase - 0.9) / 0.1 : 1;
    feixe.material.opacity = (ida < 1 ? 1 : 0.35) * fim;
    linha.material.opacity = fim;
    linha.material.transparent = true;
    luzScan.intensity = ida < 1 ? 6 : 1.5;
    tmp.set(x, 0, 1.2); gpu.localToWorld(tmp); luzScan.position.copy(tmp);

    helices.forEach((h, i) => { h.rotation.z -= dt * (i ? 7 : 6); });

    // Entrada: a câmera se aproxima e a placa gira para a posição (1,8 s)
    const e = Math.min(t / 1.8, 1);
    const entrada = 1 - Math.pow(1 - e, 3);
    camera.position.z = zBase + (1 - entrada) * 4;
    // Rolagem: a placa vira um pouco enquanto o topo sai da tela
    const r = palco.getBoundingClientRect();
    const rolagem = Math.min(Math.max(-r.top / r.height, 0), 1);
    const alvoY = -0.38 + mouse.x * 0.35 - (1 - entrada) * 1.2 + rolagem * 0.9;
    const alvoX = -0.18 + mouse.y * 0.18 + rolagem * 0.35;
    gpu.rotation.y += (alvoY - gpu.rotation.y) * 0.06;
    gpu.rotation.x += (alvoX - gpu.rotation.x) * 0.06;

    // Anel: pulsa com a varredura; a onda se expande e some
    const pulso = (t % 2.2) / 2.2;
    onda.scale.setScalar(1 + pulso * 0.6);
    onda.material.opacity = 0.45 * (1 - pulso);
    anel.material.opacity = ida < 1 ? 0.75 : 0.4;
    base.rotation.y = t * 0.05;
    gpu.position.y = Math.sin(t * 1.1) * 0.06;
    poeira.rotation.y = t * 0.02;

    renderer.render(cena, camera);
    posicionarEtiquetas(fase > 0.92 ? -9 : x);
    requestAnimationFrame(quadro);
  }

  new IntersectionObserver(([entrada]) => {
    const visivel = entrada.isIntersecting && !document.hidden;
    if (visivel && !rodando) { rodando = true; ultimo = performance.now(); requestAnimationFrame(quadro); }
    if (!visivel) rodando = false;
  }).observe(palco);
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) rodando = false;
    else if (!rodando) { rodando = true; ultimo = performance.now(); requestAnimationFrame(quadro); }
  });
}
