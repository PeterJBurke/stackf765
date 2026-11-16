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
groups.hardware = makeMountHardware();
scene.add(groups.frame, groups.roof, groups.fc, groups.service, groups.hardware);

// Where the service board sits: flat on the bottom plate behind the stack, long axis across the frame,
// USB socket toward the left side (-X), cable connector toward the right.
const SERVICE = { x: 0, y: -42, rotZ: Math.PI / 2 };
const CABLE_LENGTH = 100;

const penny = makePenny(() => update());
scene.add(penny);

// ---- views (theta, phi, radius, target), ported from the reference ----
const presets = {
  iso: [0.80, 1.12, 430, [8, 0, 9]],
  top: [Math.PI, 0.0001, 430, [0, 0, 6]],
  side: [Math.PI / 2, Math.PI / 2 - 0.025, 380, [0, 0, 14]],
  detail: [0.7, 1.25, 165, [4, -8, 12]],
  service: [-2.25, 1.02, 150, [0, -30, 8]],
};
let view = 'iso';
function setView(name) {
  view = name;
  const map = penny.children[0].material[1].map;
  map.rotation = name === 'top' || name === 'service' ? Math.PI / 2 : -Math.PI / 2;   // keep the coin upright for the viewer
  penny.rotation.set(Math.PI / 2, 0, 0);
  penny.position.set(104, -40, FLOOR_Z);
  if (name === 'detail') penny.position.set(38, -20, 0);
  if (name === 'service') penny.position.set(-36, -44, 0);
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
  ['serviceLabel', [SERVICE.x, SERVICE.y - 9, 3], [-275, -75], [-95, 60], [-270, 48], () => groups.service.visible],
  ['frameLabel', [70, -52, -3], [-10, 28], [-10, 28], [40, 40], () => true]];
st.onUpdate = () => {
  for (const [id, p, off, offTop, offSide, on] of labelDefs) {
    const [dx, dy] = view === 'top' ? offTop : view === 'side' ? offSide : off;
    const el = $(id);
    el.style.display = showLabels && innerWidth > 850 && view !== 'detail' && view !== 'service' && on() ? 'block' : 'none';
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
  // From the upper board's cable connector (J5, opens toward +X): the slack is folded forward and down
  // beside the stack, then the cable runs back along the right edge of the plate into the service
  // board's connector (J2).  The fold is sized so the drawn cable is the real 100 mm.
  const a = partBox(boards.upper, 'J5'), b = partBox(boards.service, 'J2');
  if (!a || !b) return null;
  const ac = a.getCenter(new THREE.Vector3()), bc = b.getCenter(new THREE.Vector3());
  const ax = a.max.x, bx = b.max.x, az = ac.z + 0.2, bz = bc.z;
  const path = (h) => [[ax - 1.5, ac.y, az], [ax + 2.5, ac.y, az], [ax + 4.2, ac.y + 0.45 * h, az - 5], [ax + 4.6, ac.y + h, 9],
    [ax + 5.6, ac.y + 0.55 * h, 4.4], [21.6, -20, 3.2], [21.7, -31, 3.2], [bx + 5.5, bc.y + 5, bz + 0.3], [bx + 2.5, bc.y, bz], [bx - 1.5, bc.y, bz]];
  let lo = 0, hi = 45, cable = null;
  for (let i = 0; i < 18; i++) {
    const h = (lo + hi) / 2;
    cable = makeCable(path(h));
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
    b.service.position.set(SERVICE.x, SERVICE.y, DIM.tape);
    b.service.rotation.z = SERVICE.rotZ;
    const tape = new THREE.Mesh(new THREE.BoxGeometry(28, 14, DIM.tape - 0.1), new THREE.MeshStandardMaterial({ color: 0xd9dbde, roughness: 0.9 }));
    tape.position.set(SERVICE.x, SERVICE.y, DIM.tape / 2);
    groups.service.add(b.service, tape);
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
