// Shared code for the StackF765 drone and board viewer pages.
//
// Scene convention (same as the reference pages this was modelled on,
// peterjburke.github.io/dronerenders/fc/): millimetres, X lateral, +Y toward the nose, Z up,
// Z = 0 is the top face of the frame's bottom plate, X/Y = 0 is the centre of the 20 x 20 mm FC mount.
//
// The boards are the GLB files that kicad-cli exports for the project page (../boards/*/*.glb:
// metres, Y up, board centred in X/Z, pin headers toward -Z).  They are loaded by URL, not copied.
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

window.THREE = THREE;                      // penny.js (classic script, copied from the reference) expects a global
export { THREE };

// ---- stack dimensions (mm) --------------------------------------------------------------
export const DIM = {
  pcb: 1.6,            // PCB thickness
  standoff: 8.0,       // board-to-board standoff
  gap: 9.6,            // lower top surface -> upper top surface (standoff + PCB)
  hole: 10,            // 20 x 20 mm mounting pattern: holes at +-10 mm
  grommet: 6.6,        // silicone grommet, overall height ("M3 to M2" type; nominal)
  flange: 2.5,         // grommet flange thickness below and above the PCB
  flangeDia: 6.6,      // grommet flange diameter (the board keeps 7 mm clear around each hole)
  grommetHole: 4.0,    // lower board mounting hole = grommet waist
};
// Soft mounting: the lower board rides on the lower flanges of four grommets that stand directly on
// the frame plate.  Nothing rigid touches the board; the upper board is carried by the lower one.
DIM.zLower = DIM.flange;                               // bottom face of the lower PCB: 2.5
DIM.zUpper = DIM.zLower + DIM.gap;                     // bottom face of the upper PCB: 12.1

const BOARD_URL = {
  lower: new URL('../../boards/lower/lower.glb', import.meta.url).href,
  upper: new URL('../../boards/upper/upper.glb', import.meta.url).href,
  service: new URL('../../boards/service/service.glb', import.meta.url).href,
};
// reference designators of the right-angle 0.1 inch pin headers, for the "Hide headers" control
const HEADER_REFS = { lower: ['J2'], upper: ['J1'], service: [] };

// Load one board.  Resolves to a Group in scene convention: mm, Z up, origin at the centre of the
// PCB's bottom face, pin headers toward +Y (the nose).  A rotation only, so nothing is mirrored.
export function loadBoard(id, onProgress) {
  return new Promise((resolve, reject) => {
    new GLTFLoader().load(BOARD_URL[id], (gltf) => {
      const g = new THREE.Group();
      g.name = id;
      const m = gltf.scene;
      m.scale.setScalar(1000);             // KiCad exports metres
      m.rotation.x = Math.PI / 2;          // Y up -> Z up; KiCad -Z (header edge) -> +Y
      g.add(m);
      g.userData.model = m;
      g.userData.headers = HEADER_REFS[id].map((n) => m.getObjectByName(n)).filter(Boolean);
      resolve(g);
    }, (e) => onProgress && onProgress(id, e.loaded, e.total), (err) => reject(new Error('Could not load ' + id + '.glb')));
  });
}

// Loads all three boards, reporting combined progress as text into statusEl.
export async function loadBoards(statusEl) {
  const done = {}, total = {};
  const report = (id, l, t) => {
    done[id] = l; if (t) total[id] = t;
    const mb = Object.values(done).reduce((a, b) => a + b, 0) / 1048576;
    if (statusEl) statusEl.textContent = 'Loading 3D models… ' + mb.toFixed(1) + ' MB';
  };
  if (statusEl) statusEl.textContent = 'Loading 3D models…';
  const ids = ['lower', 'upper', 'service'];
  const res = await Promise.allSettled(ids.map((id) => loadBoard(id, report)));
  const out = {}, failed = [];
  res.forEach((r, i) => { if (r.status === 'fulfilled') out[ids[i]] = r.value; else failed.push(ids[i]); });
  if (statusEl) {
    statusEl.textContent = failed.length ? 'Could not load: ' + failed.map((f) => f + '.glb').join(', ') : '';
    statusEl.classList.toggle('error', failed.length > 0);
  }
  return out;
}

// World-space bounding box of a named part (reference designator) of a loaded board, or null.
export function partBox(board, ref) {
  const o = board && board.userData.model.getObjectByName(ref);
  if (!o) return null;
  board.updateWorldMatrix(true, true);
  const b = new THREE.Box3().setFromObject(o);
  return b.isEmpty() ? null : b;
}

// ---- mounting hardware (illustrative, generated here; not part of the KiCad export) -----------
function cyl(r, z0, z1, mat, seg = 28) {
  const m = new THREE.Mesh(new THREE.CylinderGeometry(r, r, z1 - z0, seg), mat);
  m.rotation.x = Math.PI / 2; m.position.z = (z0 + z1) / 2;
  return m;
}
// Soft mounting, Matek style: a silicone grommet pressed into each of the lower board's four 4 mm
// holes (20 x 20 mm pattern), an M2 screw with a washer through each grommet into the frame.  The
// grommet is a revolved profile: lower flange standing on the frame plate, 4 mm waist in the PCB,
// upper flange under the washer, M2 bore.  The upper board has no holes here; it is not fastened to
// the frame and sits on the lower board's three standoffs.
//   tip  Z of the screw tip: below the bottom plate on the drone page, 0 where there is no frame.
// Returned group: origin at mount centre on the frame plate; children tagged userData.part
// ('grommet' stays in the board, 'screw' = washer, head and shank).
export const GROMMET_COLOUR = 0xe4472b;                                // orange-red silicone
export function grommetProfile() {
  const R = DIM.flangeDia / 2, w = DIM.grommetHole / 2 - 0.06, bore = 1.05, f = 0.7, clear = 0.12;
  const z0 = DIM.zLower - DIM.flange, z1 = z0 + DIM.grommet, zb = DIM.zLower - clear, zt = DIM.zLower + DIM.pcb + clear;
  const pts = [], arc = (cr, cz, a0, a1) => { for (let i = 0; i <= 6; i++) { const a = (a0 + (a1 - a0) * i / 6) * Math.PI / 180; pts.push(new THREE.Vector2(cr + f * Math.cos(a), cz + f * Math.sin(a))); } };
  pts.push(new THREE.Vector2(bore, z0));
  arc(R - f, z0 + f, -90, 0); arc(R - f, zb - f, 0, 90);              // lower flange, rounded rim
  pts.push(new THREE.Vector2(w, zb), new THREE.Vector2(w, zt));       // waist through the PCB
  arc(R - f, zt + f, -90, 0); arc(R - f, z1 - f, 0, 90);              // upper flange
  pts.push(new THREE.Vector2(bore, z1));
  return pts;
}
export function makeMountHardware({ tip = 0 } = {}) {
  const steel = new THREE.MeshStandardMaterial({ color: 0xb4b9c0, metalness: 0.85, roughness: 0.34 });
  const dark = new THREE.MeshStandardMaterial({ color: 0x1b1d20, metalness: 0.5, roughness: 0.6 });
  const rubber = new THREE.MeshStandardMaterial({ color: GROMMET_COLOUR, metalness: 0, roughness: 0.92, envMapIntensity: 0.25 });
  const g = new THREE.Group(); g.name = 'mount-hardware';
  const z1 = DIM.zLower - DIM.flange + DIM.grommet, prof = grommetProfile();
  for (const sx of [-1, 1]) for (const sy of [-1, 1]) {
    const c = new THREE.Group(); c.position.set(sx * DIM.hole, sy * DIM.hole, 0);
    const gr = new THREE.Mesh(new THREE.LatheGeometry(prof, 40), rubber);
    gr.rotation.x = Math.PI / 2; gr.userData.part = 'grommet';      // lathe axis Y -> Z
    const screw = [cyl(2.4, z1, z1 + 0.3, steel), cyl(1.9, z1 + 0.3, z1 + 2.3, steel),      // washer, socket-head cap,
      cyl(0.95, z1 + 2.26, z1 + 2.32, dark, 6), cyl(1.0, tip, z1 + 0.3, steel, 16)];         // hex socket, shank
    for (const m of screw) m.userData.part = 'screw';
    c.add(gr, ...screw);
    g.add(c);
  }
  return g;
}

// Round cable along a smooth path through `pts` ([x,y,z] mm).
export function makeCable(pts, radius = 1.25) {
  const curve = new THREE.CatmullRomCurve3(pts.map((p) => new THREE.Vector3(...p)), false, 'centripetal');
  const mesh = new THREE.Mesh(new THREE.TubeGeometry(curve, 96, radius, 10, false),
    new THREE.MeshStandardMaterial({ color: 0x2b2d31, metalness: 0, roughness: 0.6 }));
  mesh.name = 'service-cable';
  mesh.userData.length = curve.getLength();
  return mesh;
}

// ---- stage: renderer, Z-up camera, the reference's orbit controls, theme, grid ---------------
export function createStage({ floorZ = 0, gridSize = 300, minRadius = 60, maxRadius = 1000, fov = 32 } = {}) {
  const scene = new THREE.Scene();
  const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.setSize(innerWidth, innerHeight);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.0;
  document.body.insertBefore(renderer.domElement, document.body.firstChild);

  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
  scene.environmentIntensity = 0.55;       // the KiCad models have metal pads and pins that need something to reflect
  scene.add(new THREE.HemisphereLight(0xffffff, 0xa0a8b2, 0.9));
  for (const p of [[120, -180, 250], [-180, 100, 160], [0, 200, 200]]) {
    const l = new THREE.DirectionalLight(0xffffff, 1.0); l.position.set(...p); scene.add(l);
  }

  const camera = new THREE.PerspectiveCamera(fov, innerWidth / innerHeight, 2, 3000);
  camera.up.set(0, 0, 1);
  const st = { theta: 0.8, phi: 1.12, radius: 400, target: new THREE.Vector3(), dark: false, onUpdate: null };

  let queued = false;
  function render() {
    queued = false;
    const { theta, phi, radius, target } = st;
    camera.position.set(target.x + radius * Math.sin(phi) * Math.sin(theta),
      target.y + radius * Math.sin(phi) * Math.cos(theta), target.z + radius * Math.cos(phi));
    camera.lookAt(target);
    camera.updateMatrixWorld();
    renderer.render(scene, camera);
    if (st.onUpdate) st.onUpdate();
  }
  function update() { if (!queued) { queued = true; requestAnimationFrame(render); } }

  let grid = null;
  function setTheme(dark) {
    st.dark = dark;
    document.documentElement.dataset.theme = dark ? 'dark' : 'light';
    scene.background = new THREE.Color(dark ? 0x1d2024 : 0xf7f8f9);
    if (grid) scene.remove(grid);
    grid = new THREE.Group();
    const n = gridSize / 10;
    const minor = new THREE.GridHelper(gridSize, n, dark ? 0x363d46 : 0xe0e3e6, dark ? 0x363d46 : 0xe0e3e6);
    const major = new THREE.GridHelper(gridSize, n / 5, dark ? 0x555d68 : 0xb4bbc4, dark ? 0x555d68 : 0xb4bbc4);
    minor.rotateX(Math.PI / 2); major.rotateX(Math.PI / 2);
    grid.add(minor, major);
    grid.position.z = floorZ;
    scene.add(grid);
    update();
  }
  setTheme(matchMedia('(prefers-color-scheme: dark)').matches);

  // pointer controls: left-drag / one finger rotates, right-drag / two fingers pans, wheel / pinch zooms
  const el = renderer.domElement, ptr = new Map();
  let pinch = 0;
  const clampR = (r) => THREE.MathUtils.clamp(r, minRadius, maxRadius);
  function pan(dx, dy) {
    const right = new THREE.Vector3().setFromMatrixColumn(camera.matrixWorld, 0), up = new THREE.Vector3().setFromMatrixColumn(camera.matrixWorld, 1);
    st.target.addScaledVector(right, -dx * st.radius / innerHeight * 0.6).addScaledVector(up, dy * st.radius / innerHeight * 0.6);
  }
  el.oncontextmenu = (e) => e.preventDefault();
  el.onpointerdown = (e) => { ptr.set(e.pointerId, { x: e.clientX, y: e.clientY, pan: e.button === 2 }); el.setPointerCapture(e.pointerId); pinch = 0; };
  el.onpointerup = el.onpointercancel = (e) => { ptr.delete(e.pointerId); pinch = 0; };
  el.onpointermove = (e) => {
    const p = ptr.get(e.pointerId); if (!p) return;
    const dx = e.clientX - p.x, dy = e.clientY - p.y; p.x = e.clientX; p.y = e.clientY;
    if (ptr.size >= 2) {
      const [a, b] = [...ptr.values()], d = Math.hypot(a.x - b.x, a.y - b.y);
      if (pinch) st.radius = clampR(st.radius * pinch / d);
      pinch = d; pan(dx / 2, dy / 2);
    } else if (p.pan) pan(dx, dy);
    else { st.theta += dx * 0.006; st.phi = THREE.MathUtils.clamp(st.phi - dy * 0.006, 0.001, Math.PI - 0.05); }
    update();
  };
  el.addEventListener('wheel', (e) => { e.preventDefault(); st.radius = clampR(st.radius * Math.exp(e.deltaY * 0.001)); update(); }, { passive: false });
  addEventListener('resize', () => {
    renderer.setSize(innerWidth, innerHeight);
    const old = camera.aspect; camera.aspect = innerWidth / innerHeight;
    st.radius *= Math.max(1, 1 / camera.aspect) / Math.max(1, 1 / old);   // keep the subject in frame on narrow screens
    camera.updateProjectionMatrix(); update();
  });

  // world point -> CSS pixel position
  function project(p) { const v = new THREE.Vector3(...p).project(camera); return [(v.x + 1) * innerWidth / 2, (-v.y + 1) * innerHeight / 2]; }
  return { scene, camera, renderer, st, update, render, setTheme, project };
}

// The reference's US-cent scale object (assets/penny.js), obverse up.
export function makePenny(onLoad) { return window.PennyModel.make({ obvRot: Math.PI / 2, onLoad }); }

// ---- frame: MOD-L 4" HD Cargo meshes, as packed by the reference (assets/frame-mod-l-hd-cargo.js) ----
// The frame's two middle standoffs (x = +-16.7, y = -28 mm) stand right behind the tail corners of the
// flight controller, over its battery / ESC solder pads. They are not needed and are left out; the four
// standoffs at the nose and tail ends stay. The packed mesh file itself is unchanged.
export const OMITTED_FRAME_MESHES = ['Frame/Standoff-3', 'Frame/Standoff-4'];
export function addFrame(groups) {
  const decode = (s, T) => { const b = atob(s), u = new Uint8Array(b.length); for (let i = 0; i < b.length; i++) u[i] = b.charCodeAt(i); return new T(u.buffer); };
  const linear = (x) => (x <= 0.04045 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4));
  for (const d of window.CURRENT_FRAME_MESHES) {
    if (OMITTED_FRAME_MESHES.includes(d.name)) continue;
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(decode(d.p, Float32Array), 3));
    g.setAttribute('normal', new THREE.BufferAttribute(decode(d.n, Float32Array), 3));
    const c = decode(d.c, Float32Array); for (let i = 0; i < c.length; i++) c[i] = linear(c[i]);
    g.setAttribute('color', new THREE.BufferAttribute(c, 3));
    g.setIndex(new THREE.BufferAttribute(decode(d.i, Uint32Array), 1));
    const m = new THREE.Mesh(g, new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.77, metalness: 0.16, side: THREE.DoubleSide }));
    m.name = d.name;
    groups[d.group].add(m);                // 'frame' (arms, plates, standoffs) or 'roof' (top plate)
  }
}
