let scene, camera, renderer, raycaster, mouse;
let celestialTargets = [];
let eclipticLineMesh = null;
let userLocation = { lat: 25.033, lon: 121.5654 };

// 狀態控制
let isInspecting = false;
let inspectingTarget = null;
let targetMeshToSpin = null;

// 原始視角與相機位置
const DEFAULT_CAM_POS = new THREE.Vector3(0, 0, 0.1);
let camLon = 180,
  camLat = 20;
let isDragging = false,
  prevMouseX = 0,
  prevMouseY = 0;

// 本機貼圖路徑
const LOCAL_TEX = {
  milkyway: "/textures/8k_stars_milky_way.jpg",
  sun: "/textures/8k_sun.jpg",
  moon: "/textures/8k_moon.jpg",
  mercury: "/textures/8k_mercury.jpg",
  venus: "/textures/8k_venus_surface.jpg",
  earth: "/textures/8k_earth_daymap.jpg",
  mars: "/textures/8k_mars.jpg",
  jupiter: "/textures/8k_jupiter.jpg",
  saturn: "/textures/8k_saturn.jpg",
  saturnRing: "/textures/8k_saturn_ring_alpha.png",
  uranus: "/textures/2k_uranus.jpg",
  neptune: "/textures/2k_neptune.jpg",
};

let CELESTIAL_CATALOG = [];

// ==========================================
// 1. 初始化 Three.js 與核心邏輯
// ==========================================
function initSkyEngine() {
  const canvas = document.getElementById("skyCanvas");
  scene = new THREE.Scene();

  camera = new THREE.PerspectiveCamera(
    55,
    window.innerWidth / window.innerHeight,
    0.1,
    7000,
  );
  camera.position.copy(DEFAULT_CAM_POS);

  renderer = new THREE.WebGLRenderer({
    canvas: canvas,
    antialias: true,
    powerPreference: "high-performance",
  });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

  raycaster = new THREE.Raycaster();
  mouse = new THREE.Vector2();

  createMilkyWayDome();
  setupGeolocationAndCalculateEphemeris();
  setupControls();

  animate();
}

// 建立 360° 本機真實銀河天球
function createMilkyWayDome() {
  const loader = new THREE.TextureLoader();
  loader.load(LOCAL_TEX.milkyway, (texture) => {
    texture.mapping = THREE.EquirectangularReflectionMapping;
    const domeGeo = new THREE.SphereGeometry(3500, 64, 64);
    domeGeo.scale(-1, 1, 1);
    const domeMat = new THREE.MeshBasicMaterial({ map: texture });
    scene.add(new THREE.Mesh(domeGeo, domeMat));
  });

  scene.add(new THREE.AmbientLight(0xffffff, 0.8));
  scene.add(camera);
}

// 2. 計算地平座標與黃道軌跡
function setupGeolocationAndCalculateEphemeris() {
  if ("geolocation" in navigator) {
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        userLocation.lat = pos.coords.latitude;
        userLocation.lon = pos.coords.longitude;
        updateLocationHud();
        recomputeEphemeris();
      },
      () => {
        updateLocationHud();
        recomputeEphemeris();
      },
    );
  } else {
    updateLocationHud();
    recomputeEphemeris();
  }
}

function updateLocationHud() {
  document.getElementById("hudLocation").textContent =
    `${Math.abs(userLocation.lat).toFixed(2)}°${userLocation.lat >= 0 ? "N" : "S"}, ${Math.abs(userLocation.lon).toFixed(2)}°${userLocation.lon >= 0 ? "E" : "W"}`;
}

// 輔助函式：將黃經轉換為赤經赤緯
function eclipticToEquatorial(lambdaDeg) {
  const EPSILON = 23.439291 * (Math.PI / 180); // 黃赤交角
  const l = lambdaDeg * (Math.PI / 180);
  const sinL = Math.sin(l);
  const cosL = Math.cos(l);

  let ra = Math.atan2(sinL * Math.cos(EPSILON), cosL) * (180 / Math.PI);
  if (ra < 0) ra += 360;
  ra = ra / 15; // 轉為小時 (0-24)

  const dec = Math.asin(Math.sin(EPSILON) * sinL) * (180 / Math.PI);
  return { ra, dec };
}

function recomputeEphemeris() {
  const { dateStr, timeStr, nowObj } = getFormattedTimeString();
  document.getElementById("hudUtcTime").textContent = `${dateStr} ${timeStr}`;

  celestialTargets.forEach((t) => scene.remove(t.mesh));
  celestialTargets = [];
  if (eclipticLineMesh) {
    scene.remove(eclipticLineMesh);
    eclipticLineMesh = null;
  }
  document.getElementById("catalogListContainer").innerHTML = "";

  const observer = new Astronomy.Observer(
    userLocation.lat,
    userLocation.lon,
    0,
  );

  const astroTime = Astronomy.MakeTime(nowObj);
  const lstFormatted = calculateLST(userLocation.lon, astroTime);
  document.getElementById("hudLstTime").textContent = lstFormatted;

  let visibleCount = 0;
  const distanceToSky = 1200;

  // 🌟 1. 計算並繪製真實的「黃道軌跡線 (Ecliptic Path)」
  const eclipticPoints = [];
  for (let lon = 0; lon <= 360; lon += 3) {
    const eq = eclipticToEquatorial(lon);
    const horiz = Astronomy.Horizon(
      astroTime,
      observer,
      eq.ra,
      eq.dec,
      "normal",
    );
    if (horiz.altitude > -10) {
      // 涵蓋在地平線附近的軌跡
      const altRad = THREE.MathUtils.degToRad(horiz.altitude);
      const azRad = THREE.MathUtils.degToRad(horiz.azimuth);
      const x = distanceToSky * Math.cos(altRad) * Math.sin(azRad);
      const y = distanceToSky * Math.sin(altRad);
      const z = distanceToSky * Math.cos(altRad) * Math.cos(azRad);
      eclipticPoints.push(new THREE.Vector3(x, y, z));
    }
  }

  if (eclipticPoints.length > 1) {
    const eclipticGeo = new THREE.BufferGeometry().setFromPoints(
      eclipticPoints,
    );
    const eclipticMat = new THREE.LineDashedMaterial({
      color: 0x38bdf8,
      dashSize: 12,
      gapSize: 8,
      transparent: true,
      opacity: 0.45,
    });
    eclipticLineMesh = new THREE.Line(eclipticGeo, eclipticMat);
    eclipticLineMesh.computeLineDistances();
    scene.add(eclipticLineMesh);
  }

  // 🌟 2. 放置各大天體
  CELESTIAL_CATALOG.forEach((item) => {
    let alt = 0,
      az = 0,
      raStr = "--",
      decStr = "--";
    let isVisible = false;

    if (item.isPlanet) {
      const body = Astronomy.Body[item.id];
      const eq = Astronomy.Equator(body, astroTime, observer, true, true);
      const horiz = Astronomy.Horizon(
        astroTime,
        observer,
        eq.ra,
        eq.dec,
        "normal",
      );
      alt = horiz.altitude;
      az = horiz.azimuth;
      isVisible = alt > -5;
      raStr = eq.ra.toFixed(2);
      decStr = eq.dec.toFixed(2);
    } else {
      const horiz = Astronomy.Horizon(
        astroTime,
        observer,
        item.ra,
        item.dec,
        "normal",
      );
      alt = horiz.altitude;
      az = horiz.azimuth;
      isVisible = alt > -5;
      raStr = item.ra.toFixed(2);
      decStr = item.dec.toFixed(2);
    }

    const altRad = THREE.MathUtils.degToRad(alt);
    const azRad = THREE.MathUtils.degToRad(az);

    const x = distanceToSky * Math.cos(altRad) * Math.sin(azRad);
    const y = distanceToSky * Math.sin(altRad);
    const z = distanceToSky * Math.cos(altRad) * Math.cos(azRad);

    const worldPos = new THREE.Vector3(x, y, z);
    const mesh = createCelestialEntity(item, isVisible);
    mesh.position.copy(worldPos);
    scene.add(mesh);

    const targetData = {
      ...item,
      alt: alt.toFixed(1),
      az: az.toFixed(1),
      ra: raStr,
      dec: decStr,
      isVisible,
      worldPos,
      mesh,
    };

    celestialTargets.push(targetData);
    if (isVisible) visibleCount++;
    addCatalogItemUI(targetData);
  });

  const currentMonthDay = getFormattedCurrentDate();
  document.getElementById("visibleCount").innerHTML =
    `可見星體數：${visibleCount} / ${CELESTIAL_CATALOG.length} <br> 日期：${currentMonthDay}`;
}

// 建立天體 3D 實體
function createCelestialEntity(item, isVisible) {
  const group = new THREE.Group();
  const loader = new THREE.TextureLoader();
  let visualMesh;

  if (item.id === "Sun") {
    const geom = new THREE.SphereGeometry(item.size, 32, 32);
    const mat = new THREE.MeshBasicMaterial({ map: loader.load(item.tex) });
    visualMesh = new THREE.Mesh(geom, mat);
    group.add(visualMesh);

    const haloCanvas = document.createElement("canvas");
    haloCanvas.width = 128;
    haloCanvas.height = 128;
    const hCtx = haloCanvas.getContext("2d");
    const hGrad = hCtx.createRadialGradient(64, 64, 0, 64, 64, 64);
    hGrad.addColorStop(0, "rgba(255, 255, 200, 0.9)");
    hGrad.addColorStop(0.3, "rgba(255, 150, 50, 0.4)");
    hGrad.addColorStop(0.6, "rgba(255, 100, 0, 0.1)");
    hGrad.addColorStop(1, "rgba(0, 0, 0, 0)");
    hCtx.fillStyle = hGrad;
    hCtx.fillRect(0, 0, 128, 128);
    const haloSprite = new THREE.Sprite(
      new THREE.SpriteMaterial({
        map: new THREE.CanvasTexture(haloCanvas),
        transparent: true,
        blending: THREE.AdditiveBlending,
      }),
    );
    haloSprite.scale.set(item.size * 6, item.size * 6, 1);
    group.add(haloSprite);
  } else if (item.isDisc) {
    const canvas = document.createElement("canvas");
    canvas.width = 256;
    canvas.height = 256;
    const ctx = canvas.getContext("2d");
    const grad = ctx.createRadialGradient(128, 128, 5, 128, 128, 128);
    grad.addColorStop(0, "rgba(255, 255, 255, 1.0)");
    grad.addColorStop(
      0.2,
      item.id === "M31"
        ? "rgba(165, 180, 252, 0.8)"
        : "rgba(244, 114, 182, 0.8)",
    );
    grad.addColorStop(
      0.6,
      item.id === "M31" ? "rgba(99, 102, 241, 0.3)" : "rgba(217, 70, 239, 0.3)",
    );
    grad.addColorStop(1, "rgba(0, 0, 0, 0)");
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, 256, 256);

    const discTex = new THREE.CanvasTexture(canvas);
    const discGeo = new THREE.PlaneGeometry(item.size * 2, item.size * 2);
    const discMat = new THREE.MeshBasicMaterial({
      map: discTex,
      transparent: true,
      opacity: 0.95,
      side: THREE.DoubleSide,
      blending: THREE.AdditiveBlending,
    });
    visualMesh = new THREE.Mesh(discGeo, discMat);
    visualMesh.lookAt(0, 0, 0);
    group.add(visualMesh);
  } else if (item.isStar) {
    const geom = new THREE.SphereGeometry(item.size, 32, 32);
    let mat = item.tex
      ? new THREE.MeshBasicMaterial({ map: loader.load(item.tex) })
      : new THREE.MeshBasicMaterial({ color: item.starColor || 0xffffff });
    visualMesh = new THREE.Mesh(geom, mat);
    group.add(visualMesh);

    const haloCanvas = document.createElement("canvas");
    haloCanvas.width = 64;
    haloCanvas.height = 64;
    const hCtx = haloCanvas.getContext("2d");
    const hGrad = hCtx.createRadialGradient(32, 32, 0, 32, 32, 32);
    hGrad.addColorStop(0, "rgba(255, 255, 255, 1.0)");
    hGrad.addColorStop(
      0.4,
      item.id === "Sirius"
        ? "rgba(153, 204, 255, 0.5)"
        : "rgba(255, 100, 50, 0.5)",
    );
    hGrad.addColorStop(1, "rgba(0, 0, 0, 0)");
    hCtx.fillStyle = hGrad;
    hCtx.fillRect(0, 0, 64, 64);

    const haloSprite = new THREE.Sprite(
      new THREE.SpriteMaterial({
        map: new THREE.CanvasTexture(haloCanvas),
        transparent: true,
        blending: THREE.AdditiveBlending,
      }),
    );
    haloSprite.scale.set(item.size * 3.5, item.size * 3.5, 1);
    group.add(haloSprite);
  } else {
    const geom = new THREE.SphereGeometry(item.size, 32, 32);
    const matOpts = {};
    if (item.tex) {
      matOpts.map = loader.load(item.tex);
    } else {
      matOpts.color = 0xaaaaaa;
    }
    const mat = new THREE.MeshBasicMaterial(matOpts);
    visualMesh = new THREE.Mesh(geom, mat);
    group.add(visualMesh);

    if (item.hasRing && item.ringTex) {
      const ringGeo = new THREE.RingGeometry(
        item.size * 1.35,
        item.size * 2.3,
        64,
      );
      const ringMat = new THREE.MeshBasicMaterial({
        map: loader.load(item.ringTex),
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.9,
      });
      const ring = new THREE.Mesh(ringGeo, ringMat);
      ring.rotation.x = Math.PI / 2.2;
      group.add(ring);
    }
  }

  group.userData = {
    visualRef: visualMesh,
    name: item.name,
    targetData: item,
  };
  return group;
}

// 介面清單與點擊聚焦
function addCatalogItemUI(data) {
  const list = document.getElementById("catalogListContainer");
  const div = document.createElement("div");
  div.className = "catalog-item";
  div.style.opacity = data.isVisible ? "1.0" : "0.55";
  div.innerHTML = `
        <div style="display:flex; align-items:center; gap:6px;">
            <span style="display:inline-block; width:6px; height:6px; border-radius:50%; background:${data.isVisible ? "#38bdf8" : "#64748b"};"></span>
            <span style="font-weight:600; color:#fff;">${data.name}</span>
        </div>
        <span style="font-size:0.7rem; color:${data.isVisible ? "#38bdf8" : "#94a3b8"};">
            ${data.isVisible ? `+${data.alt}°` : "地平線下"}
        </span>
    `;
  div.addEventListener("click", () => zoomInToCelestial(data));
  list.appendChild(div);
}

function zoomInToCelestial(data) {
  isInspecting = true;
  inspectingTarget = data;
  targetMeshToSpin =
    data.mesh.userData.visualRef || data.mesh.children[0] || data.mesh;

  document.getElementById("resetViewBtn").style.display = "inline-flex";

  const targetPos = data.worldPos;
  const direction = targetPos.clone().normalize();
  const approachDistance = data.size * 6.0;
  const endCameraPos = targetPos
    .clone()
    .sub(direction.clone().multiplyScalar(approachDistance));

  new TWEEN.Tween(camera.position)
    .to(endCameraPos, 1100)
    .easing(TWEEN.Easing.Cubic.Out)
    .onUpdate(() => camera.lookAt(targetPos))
    .start();

  openTelemetryCard(data);
  logObservation(data);
}

function resetCameraToSky() {
  isInspecting = false;
  inspectingTarget = null;
  targetMeshToSpin = null;

  document.getElementById("resetViewBtn").style.display = "none";
  document.getElementById("telemetryCard").classList.remove("open");

  new TWEEN.Tween(camera.position)
    .to(DEFAULT_CAM_POS, 900)
    .easing(TWEEN.Easing.Cubic.InOut)
    .onUpdate(() => updateCameraOrientation())
    .start();
}

function openTelemetryCard(data) {
  const card = document.getElementById("telemetryCard");
  document.getElementById("targetName").textContent = data.name;
  document.getElementById("targetType").textContent = data.type;
  document.getElementById("realPhotoImg").src =
    data.photo ||
    "https://images-assets.nasa.gov/image/PIA04591/PIA04591~orig.jpg";

  document.getElementById("valAlt").textContent =
    `${data.alt > 0 ? "+" : ""}${data.alt}° ${data.isVisible ? "(可見)" : "(地平線下)"}`;
  document.getElementById("valAz").textContent = `${data.az}°`;
  document.getElementById("valRA").textContent = data.ra;
  document.getElementById("valDec").textContent = data.dec;
  document.getElementById("valMag").textContent = `${data.mag} mag`;
  document.getElementById("valDist").textContent = data.dist;
  document.getElementById("valMass").textContent = data.mass;
  document.getElementById("valRadius").textContent = data.radius;
  document.getElementById("valDigest").textContent = data.hab;

  card.classList.add("open");
}

async function logObservation(data) {
  const currentUser =
    typeof getCurrentUser === "function" ? getCurrentUser() : null;
  const uid =
    currentUser && currentUser.user_id ? String(currentUser.user_id) : "1";
  try {
    await fetch("/api/sky/observe", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: data.name,
        body_type: data.type,
        alt: parseFloat(data.alt),
        az: parseFloat(data.az),
        mag: parseFloat(data.mag),
        user_id: uid,
      }),
    });
  } catch (e) {}
}

// ==========================================
// 3. 互動控制與全螢幕切換邏輯
// ==========================================
function toggleFullscreen() {
  const fsIcon = document.getElementById("fsIcon");
  const fsText = document.getElementById("fsText");

  if (!document.fullscreenElement) {
    document.documentElement
      .requestFullscreen()
      .then(() => {
        fsIcon.textContent = "close_fullscreen";
        fsText.textContent = "返回視窗大小";
      })
      .catch(() => {});
  } else {
    document
      .exitFullscreen()
      .then(() => {
        fsIcon.textContent = "fullscreen";
        fsText.textContent = "全螢幕投影模式";
      })
      .catch(() => {});
  }
}

document.addEventListener("fullscreenchange", () => {
  const fsIcon = document.getElementById("fsIcon");
  const fsText = document.getElementById("fsText");
  if (!document.fullscreenElement) {
    fsIcon.textContent = "fullscreen";
    fsText.textContent = "全螢幕投影模式";
  } else {
    fsIcon.textContent = "close_fullscreen";
    fsText.textContent = "返回視窗大小";
  }
});

function setupControls() {
  const canvas = document.getElementById("skyCanvas");
  canvas.addEventListener("mousedown", (e) => {
    isDragging = true;
    prevMouseX = e.clientX;
    prevMouseY = e.clientY;
  });
  window.addEventListener("mouseup", () => (isDragging = false));

  canvas.addEventListener("mousemove", (e) => {
    if (!isDragging) return;
    const deltaX = e.clientX - prevMouseX;
    const deltaY = e.clientY - prevMouseY;

    if (isInspecting && targetMeshToSpin) {
      targetMeshToSpin.rotation.y += deltaX * 0.008;
      targetMeshToSpin.rotation.x += deltaY * 0.008;
    } else {
      camLon -= deltaX * 0.16;
      camLat = Math.max(-89, Math.min(89, camLat + deltaY * 0.16));
      updateCameraOrientation();
    }
    prevMouseX = e.clientX;
    prevMouseY = e.clientY;
  });

  canvas.addEventListener("click", onCanvasClick);

  window.addEventListener("resize", () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });

  updateCameraOrientation();
}

function onCanvasClick(e) {
  if (isDragging) return;
  mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
  mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;

  raycaster.setFromCamera(mouse, camera);
  const meshes = celestialTargets.map((t) => t.mesh);
  const intersects = raycaster.intersectObjects(meshes, true);

  if (intersects.length > 0) {
    let hit = intersects[0].object;
    while (hit.parent && !hit.parent.userData.name) {
      hit = hit.parent;
    }
    if (hit.parent && hit.parent.userData.targetData) {
      const clickedData = hit.parent.userData.targetData;
      const targetObj = celestialTargets.find((t) => t.id === clickedData.id);
      if (targetObj) {
        zoomInToCelestial(targetObj);
      }
    }
  }
}

function updateCameraOrientation() {
  if (isInspecting && inspectingTarget) {
    camera.lookAt(inspectingTarget.worldPos);
    return;
  }
  const phi = THREE.MathUtils.degToRad(90 - camLat);
  const theta = THREE.MathUtils.degToRad(camLon);
  const target = new THREE.Vector3(
    Math.sin(phi) * Math.sin(theta),
    Math.cos(phi),
    Math.sin(phi) * Math.cos(theta),
  );
  camera.lookAt(target);

  const normAz = ((camLon % 360) + 360) % 360;
  document.getElementById("hudOrientation").textContent =
    `Alt: ${camLat >= 0 ? "+" : ""}${camLat.toFixed(1)}° | Az: ${normAz.toFixed(1)}°`;

  const needle = document.getElementById("compassNeedle");
  const compassText = document.getElementById("compassText");
  if (needle) needle.style.transform = `rotate(${-camLon}deg)`;
  if (compassText) {
    let dirName = "北";
    if (normAz >= 22.5 && normAz < 67.5) dirName = "東北";
    else if (normAz >= 67.5 && normAz < 112.5) dirName = "東";
    else if (normAz >= 112.5 && normAz < 157.5) dirName = "東南";
    else if (normAz >= 157.5 && normAz < 202.5) dirName = "南";
    else if (normAz >= 202.5 && normAz < 247.5) dirName = "西南";
    else if (normAz >= 247.5 && normAz < 292.5) dirName = "西";
    else if (normAz >= 292.5 && normAz < 337.5) dirName = "西北";
    compassText.textContent = `${dirName} ${normAz.toFixed(0)}°`;
  }
}

function animate() {
  requestAnimationFrame(animate);
  TWEEN.update();
  if (targetMeshToSpin && !isDragging) {
    targetMeshToSpin.rotation.y += 0.0015;
  }
  renderer.render(scene, camera);
}

// ==========================================
// 初始化載入
// ==========================================
async function loadCatalogAndInit() {
  try {
    const response = await fetch("/api/sky/catalog");
    const data = await response.json();
    CELESTIAL_CATALOG = data.catalog;
    initSkyEngine();
  } catch (error) {
    console.error("無法取得天體目錄資料：", error);
    initSkyEngine();
  }
}

window.addEventListener("DOMContentLoaded", () => {
  loadCatalogAndInit();
});
