// StackF765 drone view: the KiCad-exported boards mounted in the MOD-L 4" HD Cargo frame.
// Page structure, camera presets, controls and labels follow peterjburke.github.io/dronerenders/fc/.
import { THREE, DIM, createStage, addFrame, loadBoards, makeMountHardware, makeCable, makePenny, partBox } from './stackf765.js';

const $ = (id) => document.getElementById(id);
const FLOOR_Z = -7.4;                                   // just under the cross plate, as in the reference
const stage = createStage({ floorZ: FLOOR_Z });
const { scene, st, update } = stage;

const groups = { frame: new THREE.Group(), roof: new THREE.Group(), fc: new THREE.Group(), service: new THREE.Group(), hardware: null };
addFrame(groups);
groups.roof.visible = false;
groups.hardware = makeMountHardware({ tip: -6.8 });      // screws end inside the frame's cross plate
scene.add(groups.frame, groups.roof, groups.fc, groups.service, groups.hardware);

// Where the service board is shown: a loose accessory, not fixed to the frame.  It lies flat on the
// ground grid to the right of the frame, between the two right-hand arms, component side up, with its
// cable connector (J2) toward the stack.  The user mounts it wherever suits the airframe.
const SERVICE = { x: 80, y: 0, z: FLOOR_Z + 0.1, rotZ: -Math.PI / 2 };
const CABLE_LENGTH = 100;

const penny = makePenny(() => update());
scene.add(penny);

// ---- views (theta, phi, radius, target), ported from the reference ----
const presets = {
  iso: [0.80, 1.12, 430, [8, 0, 9]],
  top: [Math.PI, 0.0001, 430, [0, 0, 6]],
  side: [Math.PI / 2, Math.PI / 2 - 0.025, 380, [0, 0, 14]],
  detail: [0.7, 1.25, 165, [4, -8, 12]],
  service: [0.95, 1.0, 170, [58, 2, -2]],
  mount: [-Math.PI / 2, 1.5, 84, [0, 2, 6.5]],          // side-on at board level: the grommets in profile
};
let view = 'iso';
function setView(name) {
  view = name;
  const map = penny.children[0].material[1].map;
  map.rotation = name === 'top' || name === 'service' ? Math.PI / 2 : -Math.PI / 2;   // keep the coin upright for the viewer
  penny.rotation.set(Math.PI / 2, 0, 0);
  penny.position.set(104, -40, FLOOR_Z);
  if (name === 'detail') penny.position.set(38, -20, 0);
  if (name === 'service') penny.position.set(84, -26, FLOOR_Z);
  if (name === 'side') { penny.rotation.set(0, 0, -Math.PI / 2); penny.position.set(0, -88, 14); }
  [st.theta, st.phi, st.radius] = presets[name];
  st.radius *= Math.max(1, 1 / stage.camera.aspect);
  st.target.fromArray(presets[name][3]);
  $('droneView').value = name;
  update();
}

// ---- labels ----
let showLabels = true;
const labelDefs = [   // element, anchor (mm), pixel offset, pixel offset in top and side views, visible?
  ['fcLabel', [12, 0, 25], [130, -110], [130, -110], [130, -110], () => groups.fc.visible],
  ['serviceLabel', [SERVICE.x, SERVICE.y, -5], [-250, 40], [-70, 45], [40, 30], () => groups.service.visible],
  ['frameLabel', [70, -52, -3], [-150, -45], [-10, 28], [40, 40], () => true]];
st.onUpdate = () => {
  const gl = $('grommetLabel'), [gx, gy] = stage.project([-10, -10, 1.2]);     // under the near rear grommet
  gl.style.display = showLabels && innerWidth > 850 && view === 'mount' && groups.hardware.visible ? 'block' : 'none';
  gl.style.left = (gx - gl.offsetWidth / 2) + 'px'; gl.style.top = (gy + 26) + 'px';
  for (const [id, p, off, offTop, offSide, on] of labelDefs) {
    const [dx, dy] = view === 'top' ? offTop : view === 'side' ? offSide : off;
    const el = $(id);
    el.style.display = showLabels && innerWidth > 850 && view !== 'detail' && view !== 'service' && view !== 'mount' && on() ? 'block' : 'none';
    const [x, y] = stage.project(p);
    el.style.left = (x + dx) + 'px'; el.style.top = (y + dy) + 'px';
  }
};

// ---- controls ----
let headersVisible = true;
const boards = {};
function applyVisibility() {
  for (const id of ['upper', 'lower']) if (boards[id]) boards[id].visible = $('t-' + id).checked;
  groups.service.visible = $('t-service').checked;
  groups.hardware.visible = $('t-hardware').checked && $('t-lower').checked;
  for (const b of Object.values(boards)) for (const h of b.userData.headers) h.visible = headersVisible;
  groups.fc.visible = $('t-upper').checked || $('t-lower').checked;
  update();
}
for (const id of ['upper', 'lower', 'service', 'hardware']) $('t-' + id).onchange = applyVisibility;
$('droneDetails').onclick = () => { const l = $('legend'); l.hidden = !l.hidden; $('droneDetails').setAttribute('aria-expanded', String(!l.hidden)); };
$('droneView').onchange = (e) => setView(e.target.value);
$('headers').onclick = () => {
  headersVisible = !headersVisible;
  $('headers').textContent = headersVisible ? 'Hide headers' : 'Show headers';
  $('headers').title = (headersVisible ? 'Hide' : 'Show') + ' the 0.1 inch pin headers';
  applyVisibility();
};
$('roof').onclick = () => {
  groups.roof.visible = !groups.roof.visible;
  $('roof').textContent = groups.roof.visible ? 'Hide roof' : 'Show roof';
  $('roofNote').textContent = groups.roof.visible ? 'Roof fitted.' : 'Roof hidden to show the flight controller.';
  update();
};
$('theme').onclick = () => stage.setTheme(!st.dark);
$('labels').onclick = () => { showLabels = !showLabels; update(); };
if (innerWidth <= 850) $('showPanel').open = false;
setView(new URLSearchParams(location.search).get('view') in presets ? new URLSearchParams(location.search).get('view') : 'iso');

// ---- boards ----
function routeCable() {
  // From the upper board's cable connector (J5, on the right-hand edge, opening toward +X) the cable
  // leaves horizontally, drapes over the edge of the bottom plate down to the ground, and lies there in
  // one slack bow into the loose service board's connector (J2).  The bow is sized so the drawn cable
  // is the real 100 mm.
  const a = partBox(boards.upper, 'J5'), b = partBox(boards.service, 'J2');
  if (!a || !b) return null;
  const R = 1.25, ac = a.getCenter(new THREE.Vector3()), bc = b.getCenter(new THREE.Vector3());
  const ax = a.max.x, ay = ac.y, az = ac.z + 0.2, bx = b.min.x, by = bc.y, bz = bc.z, g = FLOOR_Z + R + 0.05;
  const x0 = ax + 21, run = bx - 7 - x0;                 // where it reaches the ground; length of the ground run
  const lie = (t, h) => [x0 + t * run, ay + (by - ay) * t + h * Math.sin(Math.PI * t) ** 1.5, g];
  const path = (h) => [[ax - 1.5, ay, az], [ax + 3, ay, az], [ax + 9, ay, az - 3.5], [ax + 14, ay, az - 12],
    [ax + 17.5, ay, g + 6], lie(0, h), lie(0.14, h), lie(0.28, h), lie(0.5, h), lie(0.72, h), lie(0.86, h), lie(1, h),
    [bx - 2.5, by, bz], [bx + 1.5, by, bz]];
  const build = (h) => {                                 // smooth path, kept from dipping below the ground
    const c = new THREE.CatmullRomCurve3(path(h).map((q) => new THREE.Vector3(...q)), false, 'centripetal');
    return makeCable(c.getPoints(160).map((q) => [q.x, q.y, Math.max(q.z, g)]), R);
  };
  let lo = 0, hi = 34, cable = null;
  for (let i = 0; i < 18; i++) {
    const h = (lo + hi) / 2;
    cable = build(h);
    if (cable.userData.length < CABLE_LENGTH) lo = h; else hi = h;
    if (i < 17) cable.geometry.dispose();
  }
  return cable;
}

loadBoards($('status')).then((b) => {
  Object.assign(boards, b);
  if (b.lower) { b.lower.position.z = DIM.zLower; groups.fc.add(b.lower); }
  if (b.upper) { b.upper.position.z = DIM.zUpper; groups.fc.add(b.upper); }
  if (b.service) {
    b.service.position.set(SERVICE.x, SERVICE.y, SERVICE.z);
    b.service.rotation.z = SERVICE.rotZ;
    groups.service.add(b.service);
    const cable = routeCable();
    if (cable) { groups.service.add(cable); window.STACKF765_CABLE_MM = cable.userData.length; }
  }
  applyVisibility();
  // facts for automated checks
  scene.updateMatrixWorld(true);
  const box = (o) => { const x = new THREE.Box3().setFromObject(o); return [x.min.toArray().map((v) => +v.toFixed(2)), x.max.toArray().map((v) => +v.toFixed(2))]; };
  window.STACKF765_BOXES = Object.fromEntries(Object.entries(boards).map(([k, v]) => [k, box(v)]));
  window.STACKF765_READY = true;
});

window.stackViewer = { stage, groups, boards, setView, penny };
