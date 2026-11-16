// StackF765 board view: the stack on its mounting hardware, or one board at a time.
// Controls follow peterjburke.github.io/dronerenders/fc/board.html.
import { THREE, DIM, createStage, loadBoards, makeMountHardware, makePenny } from './stackf765.js';

const $ = (id) => document.getElementById(id);
const stage = createStage({ floorZ: 0, gridSize: 200, minRadius: 25, maxRadius: 500, fov: 36 });
const { scene, st, update } = stage;

const hardware = makeMountHardware();
scene.add(hardware);
const penny = makePenny(() => update());
penny.rotation.x = Math.PI / 2;
scene.add(penny);

// 70 mm rule, as in the reference
const rc = document.createElement('canvas'); rc.width = 2220; rc.height = 240;
const cx = rc.getContext('2d'); cx.fillStyle = '#bfc7cc'; cx.fillRect(0, 0, 2220, 240); cx.fillStyle = '#24322d'; cx.font = '42px sans-serif'; cx.textAlign = 'center';
for (let i = 0; i <= 70; i++) { const x = 60 + i * 30; cx.fillRect(x, 0, 2, i % 10 === 0 ? 110 : i % 5 === 0 ? 75 : 40); if (i % 10 === 0) cx.fillText(String(i), x, 190); }
const rt = new THREE.CanvasTexture(rc); rt.colorSpace = THREE.SRGBColorSpace;
const steel = () => new THREE.MeshStandardMaterial({ color: 0x98a4ac, metalness: 0.7, roughness: 0.3 });
const ruler = new THREE.Mesh(new THREE.BoxGeometry(74, 8, 0.6), [steel(), steel(), steel(), steel(), new THREE.MeshStandardMaterial({ map: rt, metalness: 0.45, roughness: 0.4 }), steel()]);
scene.add(ruler);

const boards = {};
let choice = 'stack', exploded = false, headersVisible = true, viewName = 'iso';
const LABEL = { stack: 'Stack', upper: 'Upper board (flight controller)', lower: 'Lower board (power)', service: 'Service board' };

function layout() {
  const stack = choice === 'stack';
  const { lower, upper, service } = boards;
  if (lower) { lower.visible = stack || choice === 'lower'; lower.position.set(0, 0, stack ? DIM.zLower : 2); }
  if (upper) { upper.visible = stack || choice === 'upper'; upper.position.set(0, 0, stack ? DIM.zUpper + (exploded ? 18 : 0) : 6); }
  if (service) { service.visible = stack || choice === 'service'; service.position.set(stack ? -36 : 0, stack ? 4 : 0, stack ? 0.1 : 2); }
  hardware.visible = stack;
  hardware.traverse((o) => { if (o.userData.part === 'screw') o.position.z = o.userData.z0 + (exploded ? 7 : 0); });
  for (const b of Object.values(boards)) for (const h of b.userData.headers) h.visible = headersVisible;
  const w = choice === 'service' ? 9 : 15.75;
  penny.position.set((stack ? 40 : w + 16), 0, 0);
  ruler.position.set(0, stack ? 42 : choice === 'service' ? 24 : 40, 0.3);
  $('viewLabel').textContent = LABEL[choice] + (exploded && stack ? ' · exploded' : '');
  $('explode').textContent = exploded ? 'Assemble stack' : 'Explode stack';
  update();
}
hardware.traverse((o) => { if (o.userData.part === 'screw') o.userData.z0 = o.position.z; });

function setView(name) {
  viewName = name;
  const stack = choice === 'stack';
  st.theta = name === 'side' ? Math.PI / 2 : name === 'top' || name === 'bottom' ? Math.PI : 0.4;
  st.phi = name === 'top' ? 0.001 : name === 'bottom' ? Math.PI - 0.051 : name === 'side' ? Math.PI / 2 - 0.02 : 0.9;
  st.radius = (stack ? 190 : 150) * Math.max(1, 1.25 / stage.camera.aspect);
  st.target.set(stack ? 0 : 6, stack ? 6 : 3, stack ? (exploded ? 20 : 13) : 4);
  penny.children[0].material[1].map.rotation = name === 'top' ? Math.PI / 2 : -Math.PI / 2;   // keep the coin upright for the viewer
  $('viewChoice').value = name;
  update();
}

$('boardChoice').onchange = (e) => { choice = e.target.value; if (choice !== 'stack') exploded = false; layout(); setView(viewName); };
$('viewChoice').onchange = (e) => setView(e.target.value);
$('explode').onclick = () => { choice = 'stack'; $('boardChoice').value = 'stack'; exploded = !exploded; layout(); setView(viewName); };
$('headers').onclick = () => {
  headersVisible = !headersVisible;
  $('headers').textContent = headersVisible ? 'Hide headers' : 'Show headers';
  $('headers').title = (headersVisible ? 'Hide' : 'Show') + ' the 0.1 inch pin headers';
  layout();
};
$('theme').onclick = () => stage.setTheme(!st.dark);
$('legendButton').onclick = () => { const l = $('legend'); l.hidden = !l.hidden; $('legendButton').setAttribute('aria-expanded', String(!l.hidden)); };

layout(); setView('iso');
loadBoards($('status')).then((b) => {
  Object.assign(boards, b);
  for (const g of Object.values(b)) scene.add(g);
  const q = new URLSearchParams(location.search);
  if (q.get('board') in LABEL) { choice = q.get('board'); $('boardChoice').value = choice; }
  layout(); setView(['iso', 'top', 'bottom', 'side'].includes(q.get('view')) ? q.get('view') : 'iso');
  window.STACKF765_READY = true;
});
window.boardViewer = { stage, boards, hardware, setView };
