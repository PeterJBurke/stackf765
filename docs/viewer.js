// 3D viewer for the StackF765 boards.  Loads the GLB files exported by KiCad
// (kicad-cli pcb export glb) and shows them as the assembled stack.
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";

export function createViewer(el, boards, opts = {}) {
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 0.85;
  el.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
  scene.environmentIntensity = 0.75;
  const key = new THREE.DirectionalLight(0xffffff, 1.4);
  key.position.set(60, 120, 80);
  scene.add(key);
  scene.add(new THREE.AmbientLight(0xffffff, 0.35));

  const camera = new THREE.PerspectiveCamera(32, 1, 1, 2000);
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;

  const root = new THREE.Group();     // millimetres, Y up
  scene.add(root);
  const groups = {};
  let explode = opts.explode ?? 0;
  const status = opts.status;

  function layout() {
    for (const b of boards) {
      const g = groups[b.id];
      if (!g) continue;
      g.position.set(b.pos[0] + (b.explodeDir?.[0] ?? 0) * explode,
                     b.pos[1] + (b.explodeDir?.[1] ?? 0) * explode,
                     b.pos[2] + (b.explodeDir?.[2] ?? 0) * explode);
    }
  }

  function frame(dir = [0.9, 0.8, 1.1]) {
    const box = new THREE.Box3().setFromObject(root);
    if (box.isEmpty()) return;
    const c = box.getCenter(new THREE.Vector3());
    const r = box.getSize(new THREE.Vector3()).length() / 2;
    const d = r / Math.sin((camera.fov * Math.PI) / 360) * 1.05;
    const v = new THREE.Vector3(...dir).normalize().multiplyScalar(d);
    camera.position.copy(c).add(v);
    camera.near = d / 50; camera.far = d * 10; camera.updateProjectionMatrix();
    controls.target.copy(c);
    controls.update();
  }

  const loader = new GLTFLoader();
  let pending = boards.length;
  for (const b of boards) {
    loader.load(b.url, (gltf) => {
      const g = new THREE.Group();
      const m = gltf.scene;
      m.scale.setScalar(1000);        // KiCad exports metres
      g.add(m);
      g.name = b.id;
      groups[b.id] = g;
      root.add(g);
      layout();
      if (--pending === 0) { frame(); if (status) status.textContent = ""; }
    }, undefined, (e) => { if (status) status.textContent = "Could not load " + b.url; console.error(e); pending--; });
  }

  function resize() {
    const w = el.clientWidth, h = el.clientHeight;
    renderer.setSize(w, h, false);
    camera.aspect = w / h; camera.updateProjectionMatrix();
  }
  new ResizeObserver(resize).observe(el);
  resize();
  renderer.setAnimationLoop(() => { controls.update(); renderer.render(scene, camera); });

  return {
    setExplode(v) { explode = v; layout(); },
    setVisible(id, on) { if (groups[id]) groups[id].visible = on; },
    view(name) {
      frame({ top: [0, 1, 0.001], bottom: [0, -1, 0.001], front: [0, 0.25, 1], side: [1, 0.25, 0], iso: [0.9, 0.8, 1.1] }[name]);
    },
    frame,
  };
}
