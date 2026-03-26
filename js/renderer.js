// renderer.js
// ─────────────────────────────────────────────────────────────────────────────
// 【View 層】Three.js WebGL 初始化、相機、軌道控制、渲染迴圈
//
// 職責：
//   - 建立 WebGLRenderer / Scene / Camera
//   - 實作滑鼠軌道控制（旋轉 / 平移 / 縮放）
//   - 管理自動旋轉（autoSpin）
//   - 提供 resetCam() 重設視角
//
// 不觸碰：任何 P 參數、物理計算、UI DOM（HUD 除外）
// ─────────────────────────────────────────────────────────────────────────────

// ── Three.js 初始化 ──────────────────────────────────────────────────────────
var cvs      = document.getElementById('c');
var renderer = new THREE.WebGLRenderer({ canvas: cvs, antialias: true });
renderer.setClearColor(0x000003, 1);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);

var scene  = new THREE.Scene();
var camera = new THREE.PerspectiveCamera(55, innerWidth / innerHeight, 0.1, 2000);
camera.position.set(0, 12, 30);
camera.lookAt(0, 0, 0);

window.addEventListener('resize', function () {
  renderer.setSize(innerWidth, innerHeight);
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
});

// ── 軌道控制（球座標 + 平移向量） ────────────────────────────────────────────
var sph  = { theta: 0.3, phi: 1.2, r: 30 };
var panV = new THREE.Vector3();
var drag = false, rDrag = false, lx = 0, ly = 0;
var autoSpin = false;

function updCam() {
  camera.position.set(
    sph.r * Math.sin(sph.phi) * Math.sin(sph.theta) + panV.x,
    sph.r * Math.cos(sph.phi)                       + panV.y,
    sph.r * Math.sin(sph.phi) * Math.cos(sph.theta) + panV.z
  );
  camera.lookAt(panV);
}
updCam();

// 滑鼠按下：左鍵旋轉 / 右鍵平移
cvs.addEventListener('mousedown', function (e) {
  drag = true; rDrag = e.button === 2;
  lx = e.clientX; ly = e.clientY;
});
window.addEventListener('mouseup', function () { drag = false; });

window.addEventListener('mousemove', function (e) {
  if (!drag) return;
  var dx = e.clientX - lx, dy = e.clientY - ly;
  if (rDrag) {
    // 平移：沿相機右向量與世界 Y 軸
    var f  = sph.r * 0.001;
    var rv = new THREE.Vector3();
    camera.getWorldDirection(rv);
    rv.cross(new THREE.Vector3(0, 1, 0)).normalize();
    panV.addScaledVector(rv, -dx * f);
    panV.addScaledVector(new THREE.Vector3(0, 1, 0), dy * f);
  } else {
    // 旋轉：更新球座標角度
    sph.theta -= dx * 0.007;
    sph.phi    = clamp(sph.phi + dy * 0.007, 0.05, Math.PI - 0.05);
  }
  lx = e.clientX; ly = e.clientY;
  updCam();
});

// 滾輪縮放
cvs.addEventListener('wheel', function (e) {
  e.preventDefault();
  sph.r = clamp(sph.r * Math.pow(1.001, e.deltaY), 3, 200);
  updCam();
}, { passive: false });

// 禁止右鍵選單
cvs.addEventListener('contextmenu', function (e) { e.preventDefault(); });

/** 重設相機視角至預設位置 */
function resetCam() {
  sph = { theta: 0.3, phi: 1.2, r: 30 };
  panV.set(0, 0, 0);
  updCam();
}

// ── 渲染迴圈 ─────────────────────────────────────────────────────────────────
var lastT = 0;
(function loop(t) {
  requestAnimationFrame(loop);
  if (autoSpin) {
    sph.theta += (t - lastT) * 0.0004;
    updCam();
  }
  lastT = t;
  renderer.render(scene, camera);
})();
