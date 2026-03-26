// galaxy_builder.js
// ─────────────────────────────────────────────────────────────────────────────
// 【View 層】Galaxy 粒子系統 — Pipeline 架構
//
// 職責：
//   依據 P 物件的當前參數，管理 Three.js 粒子群的建立與更新。
//
// Pipeline 流程：
//   1. initGeometry(count)        — 配置 BufferGeometry 容量（只做一次）
//   2. fillAttributes(geo, p, ph) — 根據參數填入 position / color / size
//                                   （每次滑桿變動時呼叫，不重建物件）
//   3. createShaderMaterial(psf)  — 獨立 GLSL Shader，方便視覺微調
//   4. buildGalaxy()              — 主入口：首次呼叫建立結構；
//                                   後續呼叫只更新 attributes，提升 FPS
//
// 效能設計：
//   ✅ 避免每次 new THREE.Points → 改為 attributes.needsUpdate = true
//   ✅ 粒子數量以上限 MAX_* 常數定義，方便一次調整
// ─────────────────────────────────────────────────────────────────────────────

// ── 粒子數量常數 ─────────────────────────────────────────────────────────────
var GALAXY_MAX = {
  THIN_DISK : 70000,
  THICK_DISK: 9000,
  HALO      : 6000,
  BULGE_MAX : 14000,
  HII_MAX   : 900,
  GAS_MAX   : 2500,
  AGN_MAX   : 180,
  MERGER    : 7000,
  BACKGROUND: 3000
};

// ── GLSL Shader（獨立抽出，方便視覺微調） ────────────────────────────────────
/**
 * createShaderMaterial(psf)
 *   psf: 點擴散函數模糊半徑（kpc），0 = 理想無模糊
 *   回傳 THREE.ShaderMaterial（發光粒子效果）
 */
function createShaderMaterial(psf) {
  return new THREE.ShaderMaterial({
    uniforms: { uPSF: { value: psf } },
    vertexShader: [
      'attribute float aSize; attribute vec3 aColor; varying vec3 vCol; uniform float uPSF;',
      'void main() {',
      '  vCol = aColor;',
      '  vec4 mv = modelViewMatrix * vec4(position, 1.0);',
      '  gl_PointSize = (aSize + uPSF) * (520.0 / -mv.z);',
      '  gl_Position  = projectionMatrix * mv;',
      '}'
    ].join('\n'),
    fragmentShader: [
      'varying vec3 vCol;',
      'void main() {',
      '  float d    = length(gl_PointCoord - vec2(0.5));',
      '  if (d > 0.5) discard;',
      '  float core = 1.0 - smoothstep(0.0, 0.15, d);',  // 銳利核心
      '  float glow = pow(1.0 - smoothstep(0.0, 0.5, d), 1.4);', // 暈散光暈
      '  float a    = core * 0.9 + glow * 0.55;',
      '  gl_FragColor = vec4(vCol + core * 0.5, a);',
      '}'
    ].join('\n'),
    transparent: true,
    depthWrite : false,
    blending   : THREE.AdditiveBlending
  });
}

// ── 內部 Galaxy 狀態 ─────────────────────────────────────────────────────────
var Galaxy = (function () {
  var _group    = null;  // THREE.Group 容器
  var _points   = null;  // THREE.Points 主粒子系統
  var _geo      = null;  // THREE.BufferGeometry（可重複使用）
  var _totalMax = (
    GALAXY_MAX.THIN_DISK + GALAXY_MAX.THICK_DISK + GALAXY_MAX.HALO +
    GALAXY_MAX.BULGE_MAX + GALAXY_MAX.HII_MAX    + GALAXY_MAX.GAS_MAX +
    GALAXY_MAX.AGN_MAX   + GALAXY_MAX.MERGER
  );

  // 預先分配 TypedArray（只做一次）
  var _pos = new Float32Array(_totalMax * 3);
  var _col = new Float32Array(_totalMax * 3);
  var _sz  = new Float32Array(_totalMax);

  /** 寫入單一粒子至 TypedArray，回傳下一個 idx */
  function _write(idx, x, y, z, h, s, l, size, bandShift, dustRed) {
    var rgb = hsl2rgb(
      Math.max(0,   h + bandShift - dustRed * 30),
      Math.max(20,  s),
      Math.max(8,   l - dustRed * 8)
    );
    _pos[idx*3]   = x; _pos[idx*3+1] = y; _pos[idx*3+2] = z;
    _col[idx*3]   = rgb[0]; _col[idx*3+1] = rgb[1]; _col[idx*3+2] = rgb[2];
    _sz[idx]      = size;
    return idx + 1;
  }

  /**
   * fillAttributes(p, ph)
   *   根據參數 p 與物理快照 ph，填入全部粒子資料。
   *   回傳實際寫入粒子數 idx。
   */
  function fillAttributes(p, ph) {
    var idx = 0;
    var n = p.sersic, rd = p.rd, thick = p.thick, ell = p.ell;

    // 色彩輔助量
    var yF      = Math.max(0, Math.min(1, (3 - p.gr * 5) * 0.25 + Math.tanh(p.sfr - 0.5) * 0.4));
    var aS      = Math.max(0, 1.3 - n * 0.22);  // 旋臂強度
    var bShift  = p.band === 'nir' ? 40 : p.band === 'uv' ? -80 : 0;
    var dR      = p.dust * 0.4;                  // 塵埃紅化

    // 計算各子系統粒子數
    var ND   = GALAXY_MAX.THIN_DISK;
    var NT   = GALAXY_MAX.THICK_DISK;
    var NH   = GALAXY_MAX.HALO;
    var NB   = Math.min(GALAXY_MAX.BULGE_MAX, Math.floor(p.bd * 16000));
    var sfr10= Math.pow(10, p.sfr);
    var nHII = (sfr10 > 0.3 && p.qprob < 0.5) ? Math.min(GALAXY_MAX.HII_MAX, Math.floor(sfr10 * 200)) : 0;
    var nGas = (p.mhi > 8) ? Math.min(GALAXY_MAX.GAS_MAX, Math.floor(Math.pow(10, p.mhi - 8) * 180)) : 0;
    var nAGN = (p.agn > 0.3) ? Math.min(GALAXY_MAX.AGN_MAX, Math.floor(p.agn * 250)) : 0;
    var nM   = p.merger > 0 ? GALAXY_MAX.MERGER : 0;

    // ── 薄盤 ──
    for (var i = 0; i < ND; i++) {
      var r   = sersicR(n) * rd * (0.5 + Math.random() * 0.8);
      var phi = Math.random() * Math.PI * 2;
      var arm = aS * ((Math.cos(2 * (phi + Math.log(Math.max(0.01, r / rd)) * 1.5)) + 1) * 0.5);
      var xf  = (r + arm * rd * 0.35) * Math.cos(phi) * (1 + ell * 0.2 * Math.cos(2 * phi));
      var zf  = (r + arm * rd * 0.35) * Math.sin(phi) * (1 - ell * 0.15 * Math.cos(2 * phi));
      var yf  = randn() * rd * thick * (0.3 + Math.random() * 0.7);
      var young = Math.random() < yF * (1 - p.qprob) * (1 + arm * 0.4);
      var hue   = young ? 190 + Math.random() * 70 : 15 + p.gr * 50 + Math.random() * 20;
      idx = _write(idx, xf, yf, zf, hue, 80, 42 + Math.random() * 42, 0.55 + Math.random() * 0.85, bShift, dR);
    }

    // ── 厚盤 ──
    for (var i = 0; i < NT; i++) {
      var r2 = Math.random() * rd * 3, phi2 = Math.random() * Math.PI * 2;
      idx = _write(idx, r2 * Math.cos(phi2), randn() * rd * thick * 3, r2 * Math.sin(phi2),
                   25 + p.gr * 40, 50, 26 + Math.random() * 18, 0.4 + Math.random() * 0.5, bShift, dR);
    }

    // ── 暗物質暈 ──
    for (var i = 0; i < NH; i++) {
      var rh = Math.pow(Math.random(), 0.35) * rd * 8;
      var th = Math.acos(2 * Math.random() - 1), ph2 = Math.random() * Math.PI * 2;
      idx = _write(idx,
        rh * Math.sin(th) * Math.cos(ph2) * (1 + ell * 0.3),
        rh * Math.cos(th) * 0.55,
        rh * Math.sin(th) * Math.sin(ph2) * (1 - ell * 0.2),
        30 + Math.random() * 20, 35, 18 + Math.random() * 16, 0.35 + Math.random() * 0.4, bShift, dR);
    }

    // ── 核球（Hernquist Profile） ──
    for (var i = 0; i < NB; i++) {
      var rb = p.br * Math.abs(randn()) * 0.6;
      var tb = Math.acos(2 * Math.random() - 1), pb = Math.random() * Math.PI * 2;
      idx = _write(idx,
        rb * Math.sin(tb) * Math.cos(pb), rb * Math.cos(tb) * 0.8, rb * Math.sin(tb) * Math.sin(pb),
        30 + p.gr * 30, 60, 52 + Math.random() * 30, 0.65 + Math.random() * 0.9, bShift, dR);
    }

    // ── HII 發射區 ──
    for (var i = 0; i < nHII; i++) {
      var rh2 = Math.random() * rd * 2.5, phi3 = Math.random() * Math.PI * 2;
      var arm3 = aS * ((Math.cos(2 * (phi3 + Math.log(Math.max(0.01, rh2 / rd)) * 1.5)) + 1) * 0.5);
      var hiiH = p.band === 'halpha' ? 0 : 285 + Math.random() * 80;
      idx = _write(idx,
        (rh2 + arm3 * rd * 0.4) * Math.cos(phi3), randn() * rd * 0.04,
        (rh2 + arm3 * rd * 0.4) * Math.sin(phi3),
        hiiH, 100, 65 + Math.random() * 28, 2.2 + Math.random() * 3.0, bShift, dR);
    }

    // ── HI 氣體盤 ──
    for (var i = 0; i < nGas; i++) {
      var rg = Math.random() * p.rhi * (0.5 + Math.random()), phig = Math.random() * Math.PI * 2;
      idx = _write(idx,
        rg * Math.cos(phig), randn() * rd * thick * 0.4, rg * Math.sin(phig),
        210 + Math.random() * 30, 55, 16 + Math.random() * 14, 0.28 + Math.random() * 0.45, bShift, dR);
    }

    // ── AGN 噴流 ──
    for (var i = 0; i < nAGN; i++) {
      var ht = randn() * 0.25, hr = Math.random() * 0.25 * p.agn, hp = Math.random() * Math.PI * 2;
      idx = _write(idx,
        hr * Math.cos(hp), ht * (Math.random() < 0.5 ? 1 : -1) * rd * 2, hr * Math.sin(hp),
        50 + Math.random() * 30, 90, 72 + Math.random() * 26, 1.5 + Math.random() * 2, bShift, dR);
    }

    // ── 併合伴星系 ──
    if (p.merger > 0) {
      var ma  = p.morb * Math.PI / 180;
      var mx0 = p.msep * Math.cos(ma), my0 = p.msep * 0.25, mz0 = p.msep * Math.sin(ma);
      var ms  = Math.sqrt(p.mratio);
      for (var i = 0; i < nM; i++) {
        var mr = sersicR(1.5) * rd * ms * (0.4 + Math.random() * 0.7);
        var mp = Math.random() * Math.PI * 2;
        var mxf = mx0 + mr * Math.cos(mp) * ms;
        var myf = my0 + randn() * rd * 0.1 * ms;
        var mzf = mz0 + mr * Math.sin(mp) * ms;
        // 併合後（stage 2+）：部分粒子向中心聚攏
        if (p.merger >= 2 && Math.random() < 0.3) {
          var t2 = Math.random();
          mxf = mx0 * (1 - t2) + mr * Math.cos(mp) * 0.3;
          myf = my0 * (1 - t2);
          mzf = mz0 * (1 - t2) + mr * Math.sin(mp) * 0.3;
        }
        idx = _write(idx, mxf, myf, mzf, 200 + Math.random() * 60, 70, 38 + Math.random() * 30,
                     0.4 + Math.random() * 0.5, bShift, dR);
      }
    }

    return idx; // 實際粒子數
  }

  // ── 公開介面 ─────────────────────────────────────────────────────────────

  return {
    /**
     * build(p, ph)
     *   首次呼叫：建立完整 Three.js 物件樹
     *   後續呼叫：只更新 BufferAttribute 陣列（不重建物件，維持高 FPS）
     */
    build: function (p, ph) {
      var idx = fillAttributes(p, ph);

      if (!_geo) {
        // ── 初次建立 ──────────────────────────────────────────────────────
        _geo = new THREE.BufferGeometry();
        // 以 _totalMax 預先分配，避免後續 resize
        _geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(_totalMax * 3), 3));
        _geo.setAttribute('aColor',   new THREE.BufferAttribute(new Float32Array(_totalMax * 3), 3));
        _geo.setAttribute('aSize',    new THREE.BufferAttribute(new Float32Array(_totalMax),     1));
      }

      // 複製資料到 geometry attribute（高效路徑）
      _geo.attributes.position.array.set(_pos.subarray(0, idx * 3));
      _geo.attributes.aColor.array.set(  _col.subarray(0, idx * 3));
      _geo.attributes.aSize.array.set(   _sz.subarray(0, idx));

      // 標記更新（不重建 DrawCall）
      _geo.attributes.position.needsUpdate = true;
      _geo.attributes.aColor.needsUpdate   = true;
      _geo.attributes.aSize.needsUpdate    = true;
      _geo.setDrawRange(0, idx);  // 只渲染實際粒子數

      // PSF 模糊值
      var psfVal = p.telmode === 'ground' ? 2.5
                 : p.telmode === 'hst'    ? 0.8
                 : p.telmode === 'jwst'   ? 0.5
                 : 0.0;

      if (!_group) {
        // ── 初次建立 Group ──────────────────────────────────────────────
        _group = new THREE.Group();
        _points = new THREE.Points(_geo, createShaderMaterial(psfVal));
        _group.add(_points);
        scene.add(_group);

        // 背景星場（只建立一次）
        _buildBackground();
      } else {
        // ── 更新 Shader PSF uniform（避免重建 Material） ─────────────
        _points.material.uniforms.uPSF.value = psfVal;
      }

      // 更新核球輔助 Mesh（亮核）
      _refreshBulgeMesh(p, ph);

      // 更新 AGN 光點
      _refreshAGNMesh(p);

      // 星系傾斜角
      _group.rotation.z = p.incl * Math.PI / 180 * 0.35;

      // 更新 HUD
      var type = p.sersic > 3.5 ? '橢圓'
               : p.sersic > 2.5 ? '透鏡'
               : p.sfr    > 1.5 ? '星爆'
               : p.qprob  > 0.7 ? '紅序列'
               : '旋渦';
      var el = document.getElementById('hud-info');
      if (el) el.textContent =
        '粒子 ' + idx.toLocaleString() + ' · ' + type +
        (p.merger > 0 ? ' [+併合]' : '') +
        (p.agn    > 0.3 ? ' [AGN]' : '');
    }
  };

  // ── 私有輔助 Mesh 管理 ───────────────────────────────────────────────────

  var _bulgeMesh = null;
  var _agnMesh   = null;

  function _refreshBulgeMesh(p, ph) {
    if (_bulgeMesh) { _group.remove(_bulgeMesh); _bulgeMesh = null; }
    if (p.bd > 0.05) {
      _bulgeMesh = new THREE.Mesh(
        new THREE.SphereGeometry(p.br * 0.8, 16, 16),
        new THREE.MeshBasicMaterial({
          color      : new THREE.Color().setHSL((30 + p.gr * 35) / 360, 0.55, 0.70),
          transparent: true,
          opacity    : 0.18
        })
      );
      _group.add(_bulgeMesh);
    }
  }

  function _refreshAGNMesh(p) {
    if (_agnMesh) { _group.remove(_agnMesh); _agnMesh = null; }
    if (p.agn > 0.2) {
      _agnMesh = new THREE.Mesh(
        new THREE.SphereGeometry(0.15, 8, 8),
        new THREE.MeshBasicMaterial({
          color      : new THREE.Color().setHSL(0.12, 0.9, 0.95),
          transparent: true,
          opacity    : Math.min(0.9, p.agn)
        })
      );
      _group.add(_agnMesh);
    }
  }

  function _buildBackground() {
    var N = GALAXY_MAX.BACKGROUND;
    var bp = new Float32Array(N * 3), bc = new Float32Array(N * 3), bs = new Float32Array(N);
    for (var i = 0; i < N; i++) {
      var r = 300 + Math.random() * 700;
      var t = Math.acos(2 * Math.random() - 1), p2 = Math.random() * Math.PI * 2;
      bp[i*3]   = r * Math.sin(t) * Math.cos(p2);
      bp[i*3+1] = r * Math.cos(t);
      bp[i*3+2] = r * Math.sin(t) * Math.sin(p2);
      var bri = 0.3 + Math.random() * 0.7;
      var hue = Math.random() < 0.3 ? 200 : Math.random() < 0.5 ? 30 : 0;
      var rgb = hsl2rgb(hue, 20, bri * 75);
      bc[i*3] = rgb[0]; bc[i*3+1] = rgb[1]; bc[i*3+2] = rgb[2];
      bs[i] = Math.random() < 0.02 ? 1.8 : 0.4 + Math.random() * 0.6;
    }
    var bgGeo = new THREE.BufferGeometry();
    bgGeo.setAttribute('position', new THREE.BufferAttribute(bp, 3));
    bgGeo.setAttribute('aColor',   new THREE.BufferAttribute(bc, 3));
    bgGeo.setAttribute('aSize',    new THREE.BufferAttribute(bs, 1));
    scene.add(new THREE.Points(bgGeo, new THREE.ShaderMaterial({
      uniforms: {},
      vertexShader  : 'attribute float aSize; attribute vec3 aColor; varying vec3 vCol; void main() { vCol=aColor; vec4 mv=modelViewMatrix*vec4(position,1.0); gl_PointSize=aSize*(380.0/-mv.z); gl_Position=projectionMatrix*mv; }',
      fragmentShader: 'varying vec3 vCol; void main() { float d=length(gl_PointCoord-vec2(0.5)); if(d>0.5)discard; float g=pow(1.0-d*2.0,1.8); gl_FragColor=vec4(vCol+g*0.3,g*0.7); }',
      transparent: true, depthWrite: false, blending: THREE.AdditiveBlending
    })));
  }

})(); // end Galaxy IIFE
