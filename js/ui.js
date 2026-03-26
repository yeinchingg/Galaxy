// ui.js
// ─────────────────────────────────────────────────────────────────────────────
// 【Presenter / Store 層】單向數據流調度中心
//
// 職責：
//   Store        — 參數變動的唯一入口（update → recalculate → refresh）
//   updateReadout(ph) — 把 Physics.compute() 結果寫入所有右側 DOM 元素
//   setupTabs()  — 左右面板分頁切換邏輯
//   Slider 綁定  — 讀取 SCHEMA 自動綁定 range input 的 input 事件
//   setVal()     — 安全設定 DOM 值 + 同步 P 物件
//   preset 載入  — 讀取 PRESETS，用 setVal 逐一設定後觸發 simulate
//
// 單向數據流（Single Direction Data Flow）：
//   使用者操作滑桿
//     → Store.update(key, value)
//       → Physics.compute(P)  [Model 更新]
//       → Galaxy.build(P, ph) [View 更新：粒子]
//       → updateReadout(ph)   [View 更新：右側面板 + 圖表]
//
// 注意：外部只需呼叫 simulate() 即可觸發完整更新。
// ─────────────────────────────────────────────────────────────────────────────

// ── Store：參數變動的統一入口 ─────────────────────────────────────────────────
var Store = {
  /**
   * update(key, value)
   *   更新 P[key]，然後觸發完整的物理計算 + 畫面更新。
   *   所有滑桿/選單的 change 事件都應呼叫此函數，而非直接修改 P。
   */
  update: function (key, value) {
    P[key] = value;
    simulate();
  }
};

// ── 主更新函數 ────────────────────────────────────────────────────────────────
/**
 * simulate()
 *   觸發完整的「計算 → 渲染 → 讀出」循環，是整個 App 的更新入口。
 */
function simulate() {
  var ph = Physics.compute(P);   // Model：純計算
  Galaxy.build(P, ph);           // View：更新 Three.js 粒子
  updateReadout(ph);             // View：更新右側面板與圖表
}

// ── updateReadout：將物理快照寫入所有 DOM ──────────────────────────────────────
function updateReadout(ph) {
  // ── 物理 tab ──
  setText('r-mv',  '10^' + P.logM.toFixed(1) + ' M☉');
  setText('r-rv',  ph.Rv.toFixed(1));
  setText('r-vv',  ph.V2.toFixed(1));
  setText('r-tv',  ph.Tv.toExponential(2) + ' K');
  setText('r-rs',  ph.rs.toFixed(1));
  setText('r-mb',  '10^' + Math.log10(Math.max(1, ph.Mb)).toFixed(1) + ' M☉');
  setText('r-bt',  ph.BT.toFixed(3));
  setText('r-bh',  '10^' + P.smbh.toFixed(1) + ' M☉');
  setText('r-bhr', (ph.Mbh / Math.max(1, ph.Mb) * 100).toFixed(2) + '%');
  setText('r-ms',  '10^' + Math.log10(ph.Ms).toFixed(1) + ' M☉');
  setText('r-rh',  ph.Rh.toFixed(1));
  setText('r-imf', P.imf.charAt(0).toUpperCase() + P.imf.slice(1));
  var fb = ph.Ms / ph.M;
  setText('r-fb',  fb < 1 ? (fb < 0.001 ? fb.toExponential(2) : fb.toFixed(4)) : '—');
  setText('r-sfr', ph.sfrE.toFixed(2));
  setText('r-ss',  ph.sSFR.toExponential(2) + ' yr⁻¹');
  setText('r-pop', P.qprob > 0.5 ? 'Quenched' : P.sfr > 1 ? '星爆' : '藍序列旋渦');
  setText('r-tf',  (ph.TFdev > 0 ? '+' : '') + ph.TFdev.toFixed(2) + ' mag');

  // ── 氣體 tab ──
  setText('g-mhi',  '10^' + P.mhi.toFixed(1) + ' M☉');
  setText('g-mh2',  '10^' + P.mh2.toFixed(1) + ' M☉');
  setText('g-fg',   (ph.fg * 100).toFixed(1) + '%');
  setText('g-tdep', ph.tdep.toFixed(2));
  setText('g-mout', ph.Mout.toFixed(1));
  setText('g-eta',  ph.eta.toFixed(2));

  // ── 動態 tab ──
  setText('d-tq', ph.Q);
  var mstates = ['關閉', '靠近中（潮汐開始）', '首次穿越（潮汐尾）', '併合後（擾動盤）'];
  setText('d-merger', mstates[P.merger] || '—');
  setText('d-tidal',  P.merger >= 2 ? '顯著潮汐特徵' : P.merger === 1 ? '輕微潮汐擾動' : '無');
  setText('d-thick',  P.afe > 0.15 ? '早期快速形成' : '晚期緩慢增豐');
  setText('d-diskage',P.feh > -0.3  ? '< 8 Gyr（年輕盤）' : '8-12 Gyr（古老盤）');

  // ── 化學 tab ──
  setText('c-feh',  P.feh.toFixed(2));
  setText('c-afe',  P.afe.toFixed(2));
  setText('c-zmet', Math.pow(10, P.feh).toFixed(3));
  setText('c-aenh', P.afe > 0.2 ? '顯著增強（厚盤/暈）' : P.afe > 0 ? '輕微增強' : '太陽豐度');
  setText('c-tz',   P.tauZ.toFixed(1));
  setText('c-td',   P.afe > 0.15 ? '早期快速形成' : '晚期緩慢增豐');
  setText('c-da',   P.feh > -0.3  ? '< 8 Gyr' : '8-12 Gyr');
  setText('c-la',   P.agn > 0 ? ph.Lagn.toExponential(2) + ' erg/s' : '靜止 (Seyfert off)');
  setText('c-mo',   ph.Mout.toFixed(1));
  setText('c-et',   ph.eta.toFixed(2));

  // ── 觀測 tab ──
  var z = P.redshift, DH = 3e5 / 70;
  var DC = DH * z * (1 + z * 0.5), DL = DC * (1 + z), DA = DC / (1 + z);
  var asec = DA * 1e3 / 206265;
  var psfMap = { ideal: 0, ground: asec * 1, hst: asec * 0.1, jwst: asec * 0.06 };
  var psf = psfMap[P.telmode] || 0;
  setText('o-dl', DL.toFixed(1));  setText('ob-dl', DL.toFixed(1));
  setText('o-da', DA.toFixed(1));  setText('ob-da', DA.toFixed(1));
  setText('o-as', asec.toFixed(4));setText('ob-as', asec.toFixed(4));
  setText('o-psf',psf.toFixed(3)); setText('ob-psf',psf.toFixed(3));
  setText('o-av', P.dust.toFixed(2)); setText('ob-av', P.dust.toFixed(2));
  setText('o-ab', (P.dust * 1.32).toFixed(2));
  setText('o-ebv',(P.dust / 3.1).toFixed(3)); setText('ob-ebv',(P.dust / 3.1).toFixed(3));
  var egr = P.gr + P.dust * 0.08;
  setText('o-egr', egr.toFixed(3)); setText('ob-egr', egr.toFixed(3));
  setText('o-vmax', ph.V2.toFixed(0)); setText('ob-vm', ph.V2.toFixed(0));
  setText('ob-vg', (ph.V2 / P.rd).toFixed(1) + ' km/s/kpc');
  setText('ob-pa', (P.incl * 1.2).toFixed(0));

  // ── 圖表（只在可見時繪製） ──
  drawRotCurve(ph);
  if (document.getElementById('gasplot').offsetWidth > 0)  drawGasProfile(P);
  if (document.getElementById('chemplot').offsetWidth > 0) { drawChemPlot(P); drawSFH(ph, P); }
  if (document.getElementById('ifumap').offsetWidth > 0)   drawIFU(ph, P);
}

// 安全設定 DOM textContent
function setText(id, val) {
  var el = document.getElementById(id);
  if (el) el.textContent = val;
}

// ── 分頁切換 ─────────────────────────────────────────────────────────────────
function setupTabs(groupId, panePrefix, ids) {
  var tabs = document.querySelectorAll('#' + groupId + ' .tab');
  tabs.forEach(function (tab, i) {
    tab.addEventListener('click', function () {
      tabs.forEach(function (t) { t.classList.remove('on'); });
      tab.classList.add('on');
      ids.forEach(function (id) {
        var el = document.getElementById(panePrefix + id);
        if (el) el.classList.toggle('on', id === ids[i]);
      });
      // 分頁切換後重繪圖表（因 canvas offsetWidth 在隱藏時為 0）
      setTimeout(function () {
        var ph = Physics.compute(P);
        drawRotCurve(ph);
        if (document.getElementById('gasplot').offsetWidth > 0)  drawGasProfile(P);
        if (document.getElementById('chemplot').offsetWidth > 0) { drawChemPlot(P); drawSFH(ph, P); }
        if (document.getElementById('ifumap').offsetWidth > 0)   drawIFU(ph, P);
      }, 20);
    });
  });
}
setupTabs('ltabs', 'l', ['s', 'g', 'd', 'o']);
setupTabs('rtabs', 'r', ['ph', 'ch', 'ob']);

// ── 滑桿綁定（由 SCHEMA 自動驅動）────────────────────────────────────────────
// 讀取 SCHEMA 中所有 range 類型的 key，統一綁定 input 事件
// 這樣新增參數只需修改 params.js 的 SCHEMA，此處無需改動
Object.keys(SCHEMA).forEach(function (key) {
  var el = document.getElementById(key);
  if (!el || el.tagName !== 'INPUT') return;
  el.addEventListener('input', function () {
    var val = parseFloat(el.value);
    // 更新顯示值
    var dec = el.step && el.step.indexOf('.') >= 0 ? el.step.split('.')[1].length : 0;
    var vEl = document.getElementById('v-' + key);
    if (vEl) vEl.textContent = val.toFixed(dec);
    // 觸發單向數據流
    Store.update(key, val);
  });
});

// SELECT 類型的單獨綁定（不在 SCHEMA range 中）
['imf', 'merger', 'telmode', 'band', 'ifumode'].forEach(function (id) {
  var el = document.getElementById(id); if (!el) return;
  el.addEventListener('change', function () {
    var val = (isNaN(el.value) || el.value === '') ? el.value : parseFloat(el.value);
    Store.update(id, val);
  });
});

// ── setVal：安全設定 DOM 值並同步 P ───────────────────────────────────────────
function setVal(id, v) {
  var el = document.getElementById(id); if (!el) return;
  if (el.tagName === 'SELECT') {
    el.value = v;
    P[id] = (isNaN(v) || v === '') ? v : parseFloat(v);
  } else {
    el.value = v;
    P[id] = parseFloat(v);
    var dec = el.step && el.step.indexOf('.') >= 0 ? el.step.split('.')[1].length : 0;
    var vEl = document.getElementById('v-' + id);
    if (vEl) vEl.textContent = parseFloat(v).toFixed(dec);
  }
}

// ── Preset 載入 ───────────────────────────────────────────────────────────────
document.getElementById('preset').addEventListener('change', function (e) {
  if (!e.target.value) return;
  var pr = PRESETS[e.target.value];
  if (!pr) return;
  for (var k in pr) setVal(k, pr[k]);
  e.target.value = '';
  simulate();
});

// ── 隨機星系 ─────────────────────────────────────────────────────────────────
function doRand() {
  // 隨機化主要視覺參數（從 SCHEMA 讀取 min/max）
  var randKeys = ['logM','conc','spin','ell','bd','sersic','rd','incl','thick','gr','sfr','qprob'];
  randKeys.forEach(function (key) {
    var s = SCHEMA[key]; if (!s) return;
    var el = document.getElementById(key); if (!el) return;
    var val = s.min + Math.random() * (s.max - s.min);
    setVal(key, val);
  });
  simulate();
}

// ── 自動旋轉切換 ──────────────────────────────────────────────────────────────
function toggleSpin() {
  autoSpin = !autoSpin;
  document.getElementById('btnA').textContent = autoSpin ? '■ 停止旋轉' : '◎ 自動旋轉';
}

// ── 啟動 ─────────────────────────────────────────────────────────────────────
simulate();
