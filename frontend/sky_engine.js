/**
 * frontend/sky_engine.js
 * 專業擬真天文觀測儀：
 * - 修正光照平衡（告別過曝發白）
 * - 舒適特寫距離（不會再過大爆框）
 * - 首次 Zoom-in 快轉，特寫狀態下支援滑鼠手動 360 度旋轉星體
 * - 真實恆星光暈與星系動態透明盤面
 */

let scene, camera, renderer, raycaster, mouse;
let celestialTargets = [];
let userLocation = { lat: 25.033, lon: 121.5654 };

// 狀態控制
let isInspecting = false;
let inspectingTarget = null;
let targetMeshToSpin = null;
let isFirstInspection = false; // 是否初次點擊觸發快轉

// 原始視角與相機位置
const DEFAULT_CAM_POS = new THREE.Vector3(0, 0, 0.1);
let camLon = 180,
  camLat = 20;
let isDragging = false,
  prevMouseX = 0,
  prevMouseY = 0;

// 本機貼圖路徑
const LOCAL_TEX = {
  milkyway: "/static/static/textures/8k_stars_milky_way.jpg",
  sun: "/static/static/textures/8k_sun.jpg",
  moon: "/static/static/textures/8k_moon.jpg",
  mercury: "/static/static/textures/8k_mercury.jpg",
  venus: "/static/static/textures/8k_venus_surface.jpg",
  earth: "/static/static/textures/8k_earth_daymap.jpg",
  mars: "/static/static/textures/8k_mars.jpg",
  jupiter: "/static/static/textures/8k_jupiter.jpg",
  saturn: "/static/static/textures/8k_saturn.jpg",
  saturnRing: "/static/static/textures/8k_saturn_ring_alpha.png",
  uranus: "/static/static/textures/2k_uranus.jpg",
  neptune: "/static/static/textures/2k_neptune.jpg",
};

// 天體資料庫
const CELESTIAL_CATALOG = [
  {
    id: "Sun",
    name: "太陽 (Sun)",
    type: "G2V 主序恆星",
    isPlanet: true,
    mass: "1.00 M☉",
    radius: "1.00 R☉",
    dist: "1.00 AU",
    hab: "太陽系母星，表面有效溫度 5,778 K，由核心強烈氫融合反應維繫熱核平衡。",
    size: 20,
    isDisc: false,
    isStar: true,
    tex: LOCAL_TEX.sun,
    photo:
      "https://images-assets.nasa.gov/image/GSFC_20171208_Archive_e001435/GSFC_20171208_Archive_e001435~orig.jpg",
  },
  {
    id: "Mercury",
    name: "水星 (Mercury)",
    type: "類地行星",
    isPlanet: true,
    mass: "0.055 M⊕",
    radius: "0.383 R⊕",
    dist: "0.39 AU",
    hab: "極端晝夜溫差 (-180°C ~ 430°C)，表面布滿撞擊坑，無實質大氣層保護。",
    size: 7,
    isDisc: false,
    isStar: false,
    tex: LOCAL_TEX.mercury,
    photo: "https://images-assets.nasa.gov/image/PIA15160/PIA15160~orig.jpg",
  },
  {
    id: "Venus",
    name: "金星 (Venus)",
    type: "類地行星",
    isPlanet: true,
    mass: "0.815 M⊕",
    radius: "0.949 R⊕",
    dist: "0.72 AU",
    hab: "失控溫室效應，表面高達 465°C，濃密硫酸雲層伴隨 92 大氣壓高壓環境。",
    size: 10,
    isDisc: false,
    isStar: false,
    tex: LOCAL_TEX.venus,
    photo: "https://images-assets.nasa.gov/image/PIA00104/PIA00104~orig.jpg",
  },
  {
    id: "Moon",
    name: "月球 (Moon)",
    type: "天然衛星 (潮汐鎖定)",
    isPlanet: true,
    mass: "0.012 M⊕",
    radius: "0.272 R⊕",
    dist: "384,400 km",
    hab: "表面無大氣層保護，極端溫差達 250°C，極區永久陰影坑蘊含大量水冰沉積物。",
    size: 8,
    isDisc: false,
    isStar: false,
    tex: LOCAL_TEX.moon,
    photo:
      "https://images-assets.nasa.gov/image/as11-40-5903/as11-40-5903~orig.jpg",
  },
  {
    id: "Mars",
    name: "火星 (Mars)",
    type: "類地行星",
    isPlanet: true,
    mass: "0.107 M⊕",
    radius: "0.532 R⊕",
    dist: "1.52 AU",
    hab: "大氣壓約 6 hPa，地表富含氧化鐵與極冠乾冰，已證實遠古曾具備豐富湖泊水系。",
    size: 9,
    isDisc: false,
    isStar: false,
    tex: LOCAL_TEX.mars,
    photo: "https://images-assets.nasa.gov/image/PIA04591/PIA04591~orig.jpg",
  },
  {
    id: "Jupiter",
    name: "木星 (Jupiter)",
    type: "氣體巨行星",
    isPlanet: true,
    mass: "317.8 M⊕",
    radius: "11.21 R⊕",
    dist: "5.20 AU",
    hab: "無固態表面，強烈磁層與大紅斑風暴，衛星歐羅巴內部蘊含龐大次表層全球海洋。",
    size: 18,
    isDisc: false,
    isStar: false,
    tex: LOCAL_TEX.jupiter,
    photo: "https://images-assets.nasa.gov/image/PIA22946/PIA22946~orig.jpg",
  },
  {
    id: "Saturn",
    name: "土星 (Saturn)",
    type: "環狀氣體巨行星",
    isPlanet: true,
    mass: "95.2 M⊕",
    radius: "9.45 R⊕",
    dist: "9.58 AU",
    hab: "由水冰微粒構成的宏偉環系，衛星泰坦擁有濃密氮氣大氣與液態甲烷湖泊循環。",
    size: 15,
    isDisc: false,
    isStar: false,
    hasRing: true,
    tex: LOCAL_TEX.saturn,
    ringTex: LOCAL_TEX.saturnRing,
    photo: "https://images-assets.nasa.gov/image/PIA18273/PIA18273~orig.jpg",
  },
  {
    id: "Uranus",
    name: "天王星 (Uranus)",
    type: "冰巨行星",
    isPlanet: true,
    mass: "14.5 M⊕",
    radius: "4.01 R⊕",
    dist: "19.2 AU",
    hab: "自轉軸橫躺傾斜 97.8 度，富含水、氨與甲烷冰，大氣極端寒冷最低達 49 K。",
    size: 12,
    isDisc: false,
    isStar: false,
    tex: LOCAL_TEX.uranus,
    photo: "https://images-assets.nasa.gov/image/PIA18182/PIA18182~orig.jpg",
  },
  {
    id: "Neptune",
    name: "海王星 (Neptune)",
    type: "冰巨行星",
    isPlanet: true,
    mass: "17.1 M⊕",
    radius: "3.88 R⊕",
    dist: "30.1 AU",
    hab: "大氣擁有高達時速 2,100 公里的超音速狂風與神秘大黑斑風暴。",
    size: 12,
    isDisc: false,
    isStar: false,
    tex: LOCAL_TEX.neptune,
    photo: "https://images-assets.nasa.gov/image/PIA01492/PIA01492~orig.jpg",
  },
  // ✨ 深空星系與星雲（以自生成高品質螺旋紋理確保絕不黑球、絕不破圖）
  {
    id: "M31",
    name: "仙女座大星系 (M31)",
    type: "螺旋星系 (Spiral Galaxy)",
    ra: 0.712,
    dec: 41.27,
    mag: 3.44,
    mass: "1.5×10¹² M☉",
    radius: "110,000 ly",
    dist: "2.54 百萬光年",
    hab: "本星系群最大螺旋星系，直徑逾 22 萬光年，上兆顆恆星正圍繞超大質量黑洞公轉。",
    size: 24,
    isDisc: true,
    isStar: false,
    photo: "https://images-assets.nasa.gov/image/PIA15416/PIA15416~orig.jpg",
  },
  {
    id: "M42",
    name: "獵戶座大星雲 (M42)",
    type: "發射星雲 (Diffuse Nebula)",
    ra: 5.588,
    dec: -5.39,
    mag: 4.0,
    mass: "2,000 M☉",
    radius: "12 ly",
    dist: "1,344 ly",
    hab: "活躍的恆星育嬰室，強烈紫外線激發周圍氫氣發出粉紅色光芒。",
    size: 20,
    isDisc: true,
    isStar: false,
    photo: "https://images-assets.nasa.gov/image/PIA08653/PIA08653~orig.jpg",
  },
  // ✨ 知名恆星（專屬高溫發光體）
  {
    id: "Sirius",
    name: "天狼星 (Sirius)",
    type: "A1V 藍白主序星",
    ra: 6.752,
    dec: -16.716,
    mag: -1.46,
    mass: "2.06 M☉",
    radius: "1.71 R☉",
    dist: "8.6 ly",
    hab: "全天最亮恆星，伴有一顆超高密度白矮星伴星 (天狼星 B)。",
    size: 10,
    isDisc: false,
    isStar: true,
    starColor: 0x99ccff,
    photo:
      "https://images-assets.nasa.gov/image/GSFC_20171208_Archive_e001830/GSFC_20171208_Archive_e001830~orig.jpg",
  },
  {
    id: "Betelgeuse",
    name: "參宿四 (Betelgeuse)",
    type: "M1-2Ia 紅超巨星",
    ra: 5.919,
    dec: 7.407,
    mag: 0.5,
    mass: "16.5 M☉",
    radius: "764 R☉",
    dist: "642 ly",
    hab: "已至演化末期，體積可吞沒木星軌道，數萬年內將發生超新星爆發。",
    size: 14,
    isDisc: false,
    isStar: true,
    starColor: 0xff5533,
    photo: "https://images-assets.nasa.gov/image/PIA23687/PIA23687~orig.jpg",
  },
];

// 1. 初始化 Three.js
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

// 建立 360° 本機真實銀河天球 + 擬真太空光照
function createMilkyWayDome() {
  const loader = new THREE.TextureLoader();
  loader.load(LOCAL_TEX.milkyway, (texture) => {
    texture.mapping = THREE.EquirectangularReflectionMapping;
    const domeGeo = new THREE.SphereGeometry(3500, 64, 64);
    domeGeo.scale(-1, 1, 1);
    const domeMat = new THREE.MeshBasicMaterial({ map: texture });
    scene.add(new THREE.Mesh(domeGeo, domeMat));
  });

  // 🌟 光照修正：深邃太空環境光（0.35 不過曝）+ 相機補光（0.6）
  scene.add(new THREE.AmbientLight(0xffffff, 0.35));

  const camLight = new THREE.DirectionalLight(0xffffff, 0.7);
  camLight.position.set(0, 0, 1);
  camera.add(camLight);
  scene.add(camera);
}

// 2. Astronomy Engine 計算地平座標
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

function recomputeEphemeris() {
  const now = new Date();
  document.getElementById("hudUtcTime").textContent = now
    .toISOString()
    .slice(11, 19);

  celestialTargets.forEach((t) => scene.remove(t.mesh));
  celestialTargets = [];
  document.getElementById("catalogListContainer").innerHTML = "";

  const observer = new Astronomy.Observer(
    userLocation.lat,
    userLocation.lon,
    0,
  );
  const astroTime = Astronomy.MakeTime(now);

  const gast = Astronomy.SiderealTime(astroTime);
  const lst = (gast + userLocation.lon / 15.0 + 24.0) % 24.0;
  document.getElementById("hudLstTime").textContent =
    `${Math.floor(lst).toString().padStart(2, "0")}:${Math.floor((lst % 1) * 60)
      .toString()
      .padStart(2, "0")}:${Math.floor((((lst % 1) * 60) % 1) * 60)
      .toString()
      .padStart(2, "0")}`;

  let visibleCount = 0;

  CELESTIAL_CATALOG.forEach((item) => {
    let alt = 0,
      az = 0,
      ra = 0,
      dec = 0,
      mag = item.mag || 0;

    if (item.isPlanet && window.Astronomy) {
      try {
        const equ = Astronomy.Equator(item.id, astroTime, observer, true, true);
        const hor = Astronomy.Horizon(
          astroTime,
          observer,
          equ.ra,
          equ.dec,
          "normal",
        );
        alt = hor.altitude;
        az = hor.azimuth;
        ra = equ.ra;
        dec = equ.dec;
        mag = Astronomy.Illumination(item.id, astroTime).mag;
      } catch (e) {
        alt = 30;
        az = 140;
      }
    } else {
      ra = item.ra;
      dec = item.dec;
      if (window.Astronomy) {
        const hor = Astronomy.Horizon(astroTime, observer, ra, dec, "normal");
        alt = hor.altitude;
        az = hor.azimuth;
      }
    }

    const isVisible = alt > 0;
    if (isVisible) visibleCount++;

    const distR = 900;
    const phi = (90 - alt) * (Math.PI / 180);
    const theta = (az + 180) * (Math.PI / 180);

    const x = distR * Math.sin(phi) * Math.sin(theta);
    const y = distR * Math.cos(phi);
    const z = distR * Math.sin(phi) * Math.cos(theta);

    const mesh = createCelestialEntity(item, isVisible);
    mesh.position.set(x, y, z);
    scene.add(mesh);

    const targetData = {
      ...item,
      alt: alt.toFixed(2),
      az: az.toFixed(2),
      ra: typeof ra === "number" ? `${ra.toFixed(2)}h` : ra,
      dec: typeof dec === "number" ? `${dec.toFixed(2)}°` : dec,
      mag: typeof mag === "number" ? mag.toFixed(1) : mag,
      mesh: mesh,
      worldPos: new THREE.Vector3(x, y, z),
      isVisible: isVisible,
    };
    mesh.userData = targetData;
    celestialTargets.push(targetData);

    addCatalogItemUI(targetData);
  });

  document.getElementById("visibleCount").textContent =
    `${visibleCount} / ${CELESTIAL_CATALOG.length} 今日可見`;
}

// 3. 建立 3D 模型實體（徹底告別黑球與假圖）
function createCelestialEntity(item, isVisible) {
  const group = new THREE.Group();
  const loader = new THREE.TextureLoader();
  let visualMesh;

  if (item.isDisc) {
    // ✨ 星系 / 星雲：程序化動態星雲透明螺旋盤（絕不再黑球破圖）
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
    // ✨ 恆星（天狼星、參宿四、太陽）：專屬高溫發光材質
    const geom = new THREE.SphereGeometry(item.size, 32, 32);
    let mat;
    if (item.tex) {
      const tex = loader.load(item.tex);
      mat = new THREE.MeshBasicMaterial({ map: tex });
    } else {
      mat = new THREE.MeshBasicMaterial({ color: item.starColor || 0xffffff });
    }
    visualMesh = new THREE.Mesh(geom, mat);
    group.add(visualMesh);

    // 恆星外層光暈 Sprite
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
    // ✨ 行星：真實 NASA 貼圖 + Standard 立體陰影材質（粗糙度提升，不反光泛白）
    const geom = new THREE.SphereGeometry(item.size, 32, 32);
    const tex = loader.load(item.tex);
    const mat = new THREE.MeshStandardMaterial({
      map: tex,
      roughness: 0.85,
      metalness: 0.05,
    });
    visualMesh = new THREE.Mesh(geom, mat);
    group.add(visualMesh);

    // 土星光環
    if (item.hasRing) {
      const ringGeo = new THREE.RingGeometry(
        item.size * 1.35,
        item.size * 2.3,
        64,
      );
      const ringTex = loader.load(item.ringTex);
      const ringMat = new THREE.MeshBasicMaterial({
        map: ringTex,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.85,
      });
      const ring = new THREE.Mesh(ringGeo, ringMat);
      ring.rotation.x = Math.PI / 2.2;
      group.add(ring);
    }
  }

  // 瞄準指示光環
  const ringGeo = new THREE.RingGeometry(item.size * 1.3, item.size * 1.45, 32);
  const ringMat = new THREE.MeshBasicMaterial({
    color: isVisible ? 0x38bdf8 : 0xf43f5e,
    side: THREE.DoubleSide,
    transparent: true,
    opacity: isVisible ? 0.5 : 0.2,
  });
  const targetRing = new THREE.Mesh(ringGeo, ringMat);
  targetRing.lookAt(0, 0, 0);
  group.add(targetRing);

  group.userData = { visualRef: visualMesh };
  return group;
}

// 4. 左側清單
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

// 5. ✨ Zoom-In 與手動/自動自轉控制核心
function zoomInToCelestial(data) {
  // 檢查是否已在觀測同一個目標（若是，則不重複加速）
  const isSameTarget =
    isInspecting && inspectingTarget && inspectingTarget.id === data.id;

  isInspecting = true;
  inspectingTarget = data;
  targetMeshToSpin = data.mesh.userData.visualRef || data.mesh;

  document.getElementById("resetViewBtn").style.display = "inline-flex";

  // 🌟 距離修正：改為 5.0 倍半徑，絕不再滿版爆框！
  const targetPos = data.worldPos;
  const direction = targetPos.clone().normalize();
  const approachDistance = data.size * 5.0;
  const endCameraPos = targetPos
    .clone()
    .sub(direction.clone().multiplyScalar(approachDistance));

  // 相機平滑推入
  new TWEEN.Tween(camera.position)
    .to(endCameraPos, 1100)
    .easing(TWEEN.Easing.Cubic.Out)
    .onUpdate(() => camera.lookAt(targetPos))
    .start();

  // 🌟 只有「首次放大」才快轉展示 720 度，之後點擊絕不重複加速！
  if (!isSameTarget && targetMeshToSpin) {
    new TWEEN.Tween(targetMeshToSpin.rotation)
      .to({ y: targetMeshToSpin.rotation.y + Math.PI * 4 }, 2000)
      .easing(TWEEN.Easing.Quadratic.Out)
      .start();
  }

  openTelemetryCard(data);
  logObservation(data);
}

// 退回全天視角
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

  const photoEl = document.getElementById("realPhotoImg");
  photoEl.src =
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

// 6. ✨ 雙軌滑鼠互動：全景時轉全天球；特寫時滑鼠直接旋轉星球
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
      // 🌟 核心修正：已在特寫模式時，滑鼠拖曳直接控制星球 360 度旋轉！
      targetMeshToSpin.rotation.y += deltaX * 0.008;
      targetMeshToSpin.rotation.x += deltaY * 0.008;
    } else {
      // 全天漫遊模式：拖曳全景視角
      camLon -= deltaX * 0.16;
      camLat = Math.max(-89, Math.min(89, camLat + deltaY * 0.16));
      updateCameraOrientation();
    }

    prevMouseX = e.clientX;
    prevMouseY = e.clientY;
  });

  canvas.addEventListener("click", onCanvasClick);

  document.getElementById("fullscreenBtn").addEventListener("click", () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch(() => {});
    } else {
      document.exitFullscreen();
    }
  });

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
    while (hit.parent && !hit.userData.name) {
      hit = hit.parent;
    }
    if (hit.userData && hit.userData.name) {
      zoomInToCelestial(hit.userData);
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
}

// 7. 動畫渲染迴圈
function animate() {
  requestAnimationFrame(animate);
  TWEEN.update();

  // 恆常極緩自轉（未手動拖曳時維持生動動態）
  if (targetMeshToSpin && !isDragging) {
    targetMeshToSpin.rotation.y += 0.0015;
  }

  renderer.render(scene, camera);
}

window.addEventListener("DOMContentLoaded", () => {
  initSkyEngine();
});
