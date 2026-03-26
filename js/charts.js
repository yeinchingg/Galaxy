// charts.js
// ─────────────────────────────────────────────────────────────────────────────
// 【View 層】Mini Canvas 圖表繪製
//
// 職責：接收「純數據」參數並繪製；不直接讀取全域 P 物件。
//       圖表函數皆為 drawXxx(data) 形式，資料由 ui.js 的 updateReadout() 傳入。
//
// 圖表清單：
//   drawRotCurve(ph)      — NFW+盤+核球旋轉曲線（含 Tully-Fisher 預測線）
//   drawGasProfile(p)     — HI / H₂ / 恆星盤 radial profile
//   drawChemPlot(p)       — [Fe/H]−[α/Fe] 相空間，含三族群散點
//   drawSFH(ph, p)        — 恆星形成歷史 SFR(t) + 金屬豐度 Z(t)
//   drawIFU(ph, p)        — 視線速度 IFU mock 色圖
//
// 設計原則：
//   ✅ 每個函數只接受需要的參數（不讀取全域 P）
//   ✅ miniCtx(id, h) 是私有輔助，負責清空畫布並回傳 context
// ─────────────────────────────────────────────────────────────────────────────

// ── 私有輔助：取得畫布 context 並清空 ─────────────────────────────────────
function miniCtx(id, h) {
  var c = document.getElementById(id);
  if (!c) return null;
  var W = c.offsetWidth || 180;
  c.width = W; c.height = h || 60;
  var cx = c.getContext('2d');
  cx.fillStyle = '#000d20';
  cx.fillRect(0, 0, W, h || 60);
  return cx;
}

// ── 折線繪製輔助 ─────────────────────────────────────────────────────────────
function _strokeLine(cx, data, W, H, maxVal, color, lineWidth) {
  cx.beginPath();
  cx.strokeStyle = color;
  cx.lineWidth   = lineWidth || 1.5;
  data.forEach(function (v, i) {
    var x = i / (data.length - 1) * W;
    var y = H - 4 - v / maxVal * (H - 8);
    i === 0 ? cx.moveTo(x, y) : cx.lineTo(x, y);
  });
  cx.stroke();
}

// ── 旋轉曲線 ─────────────────────────────────────────────────────────────────
/**
 * drawRotCurve(ph)
 *   ph: Physics.compute(P) 的回傳物件
 *   繪製 NFW 暗物質、恆星盤、核球、總計旋轉速度，以及 Tully-Fisher 預測線
 */
function drawRotCurve(ph) {
  var cx = miniCtx('rotc', 65); if (!cx) return;
  var W = document.getElementById('rotc').width, H = 65;
  var N = 50, vDM = [], vS = [], vB = [], vT = [];

  for (var i = 0; i < N; i++) {
    var r  = (i + 1) / N * ph.Rv * 0.25;
    var xn = r / ph.rs;
    var dm = Math.sqrt(Math.max(0, 4.302e-3 * ph.M  * (Math.log(1 + xn) - xn / (1 + xn)) / r * 1e-3));
    var st = Math.sqrt(Math.max(0, 4.302e-3 * ph.Md * 0.5 * Math.exp(-r / P.rd) / r * 1e-3));
    var bv = Math.sqrt(Math.max(0, 4.302e-3 * ph.Mb * r / Math.pow(r + P.br, 2) * 1e-3));
    vDM.push(dm); vS.push(st); vB.push(bv);
    vT.push(Math.sqrt(dm*dm + st*st + bv*bv));
  }

  var mx = Math.max.apply(null, vT) || 1;

  // Tully-Fisher 預測線（虛線）
  var VTF = ph.V2 * 0.9;
  cx.beginPath(); cx.setLineDash([3, 3]);
  cx.strokeStyle = '#fc6'; cx.lineWidth = 1;
  cx.moveTo(0, H - 4 - VTF / mx * (H - 6));
  cx.lineTo(W, H - 4 - VTF / mx * (H - 6));
  cx.stroke(); cx.setLineDash([]);

  // 各成分曲線
  [[vDM, '#38f'], [vS, '#f70'], [vB, '#0d6'], [vT, '#eee']].forEach(function (pair) {
    _strokeLine(cx, pair[0], W, H, mx, pair[1], 1.5);
  });
}

// ── 氣體 Radial Profile ───────────────────────────────────────────────────────
/**
 * drawGasProfile(p)
 *   p: 包含 mhi, mh2, rhi, rd, h2c 的參數物件（直接傳 P 即可）
 */
function drawGasProfile(p) {
  var cx = miniCtx('gasplot', 70); if (!cx) return;
  var W = document.getElementById('gasplot').width, H = 70;
  var N = 50, rmax = Math.max(p.rhi, p.rd) * 1.5;
  var hi = [], h2 = [], st = [];
  for (var i = 0; i < N; i++) {
    var r = (i + 0.5) / N * rmax;
    hi.push(Math.exp(-r / p.rhi));
    h2.push(Math.exp(-r / (p.rd * p.h2c * 2)));
    st.push(Math.exp(-r / p.rd));
  }
  [['#4af', hi], ['#0d6', h2], ['#f70', st]].forEach(function (pair) {
    _strokeLine(cx, pair[1], W, H, 1, pair[0], 1.5);
  });
}

// ── [Fe/H] − [α/Fe] 化學相空間 ───────────────────────────────────────────────
/**
 * drawChemPlot(p)
 *   p: 包含 feh, afe 的參數物件
 *   繪製三族群（薄盤 / 厚盤 / 暈）散點圖 + 目前參數標記
 */
function drawChemPlot(p) {
  var cx = miniCtx('chemplot', 90); if (!cx) return;
  var W = document.getElementById('chemplot').width, H = 90;

  // 三族群背景散點
  var pops = [
    { n:100, feh:-0.1,  afe:0.05,  df:0.2, da:0.05, col:'rgba(100,170,255,0.55)' }, // 薄盤
    { n:70,  feh:-0.55, afe:0.25,  df:0.3, da:0.08, col:'rgba(255,170,100,0.55)' }, // 厚盤
    { n:35,  feh:-1.5,  afe:0.35,  df:0.5, da:0.1,  col:'rgba(255,80,80,0.45)'  }  // 暈
  ];
  pops.forEach(function (pop) {
    for (var i = 0; i < pop.n; i++) {
      var fx = pop.feh + randn() * pop.df;
      var ay = pop.afe + randn() * pop.da;
      var px = (fx + 2.5) / 3 * W;
      var py = H - (ay + 0.2) / 0.8 * H;
      cx.beginPath();
      cx.arc(clamp(px, 2, W-2), clamp(py, 2, H-2), 1.5, 0, Math.PI * 2);
      cx.fillStyle = pop.col; cx.fill();
    }
  });

  // 目前參數標記（綠點）
  var cpx = (p.feh + 2.5) / 3 * W;
  var cpy = H - (p.afe + 0.2) / 0.8 * H;
  cx.beginPath();
  cx.arc(clamp(cpx, 5, W-5), clamp(cpy, 5, H-5), 5, 0, Math.PI * 2);
  cx.fillStyle = '#0f0'; cx.fill();

  // 座標軸標籤
  cx.fillStyle = '#2a5070'; cx.font = '8px monospace';
  cx.fillText('[Fe/H]→', W - 48, H - 2);
  cx.fillText('[α/Fe]', 2, 10);
}

// ── 恆星形成歷史 ─────────────────────────────────────────────────────────────
/**
 * drawSFH(ph, p)
 *   ph: Physics.compute(P) 的回傳物件
 *   p:  包含 sfr, tauZ 的參數物件
 */
function drawSFH(ph, p) {
  var cx = miniCtx('sfhplot', 65); if (!cx) return;
  var W = document.getElementById('sfhplot').width, H = 65;
  var N = 50, sfrt = [], zt = [];

  for (var i = 0; i < N; i++) {
    var t = i / N * 13.8;
    sfrt.push(Math.max(0,
      ph.sfrE * Math.exp(-Math.pow(t - 3 * Math.pow(10, p.sfr * 0.2), 2) / (p.tauZ * p.tauZ))
    ));
    zt.push(0.02 * (1 - Math.exp(-t / p.tauZ)));
  }

  var mx1 = Math.max.apply(null, sfrt) || 1;
  var mx2 = Math.max.apply(null, zt)   || 1;

  _strokeLine(cx, sfrt, W, H, mx1, '#0cf', 1.5);
  _strokeLine(cx, zt,   W, H, mx2, '#fc6', 1.0);

  cx.fillStyle = '#2a5070'; cx.font = '8px monospace';
  cx.fillText('t(Gyr)→', W - 46, H - 2);
}

// ── IFU 視線速度色圖 ──────────────────────────────────────────────────────────
/**
 * drawIFU(ph, p)
 *   ph: Physics.compute(P)
 *   p:  包含 ifumode, incl, rd 的參數物件
 */
function drawIFU(ph, p) {
  var c = document.getElementById('ifumap'); if (!c) return;
  var W = c.offsetWidth || 180; c.width = W; c.height = 90;
  var cx = c.getContext('2d');
  cx.fillStyle = '#000d20'; cx.fillRect(0, 0, W, 90);

  if (!p.ifumode) {
    cx.fillStyle = '#2a5070'; cx.font = '9px monospace';
    cx.fillText('IFU 關閉 — 請開啟觀測頁IFU開關', 8, 48);
    return;
  }

  var sinI = Math.sin(p.incl * Math.PI / 180);
  for (var xi = 0; xi < W; xi++) {
    for (var yi = 0; yi < 90; yi++) {
      var rx = (xi - W / 2) / (W / 2) * p.rd * 2;
      var ry = (yi - 45) / 45 * p.rd * 2;
      var r  = Math.sqrt(rx*rx + ry*ry);
      if (r > p.rd * 1.9) continue;
      var Vlos = ph.V2 * 0.85 * (rx / Math.max(0.5, r)) * sinI * Math.min(1, r / p.rd);
      var t    = clamp(Vlos / ph.V2, -1, 1);
      cx.fillStyle = 'rgba(' +
        Math.round(Math.max(0, t) * 200 + 30) + ',30,' +
        Math.round(Math.max(0, -t) * 200 + 30) + ',0.75)';
      cx.fillRect(xi, yi, 1, 1);
    }
  }

  // 橢圓外框輔助線
  cx.strokeStyle = 'rgba(255,255,255,0.15)'; cx.lineWidth = 1;
  cx.beginPath();
  cx.ellipse(W/2, 45,
    p.rd * W / 4 / p.rd,
    45 * 0.4 * Math.abs(Math.cos(p.incl * Math.PI / 180)) + 5,
    0, 0, Math.PI * 2);
  cx.stroke();

  cx.fillStyle = '#aaa'; cx.font = '8px monospace';
  cx.fillText('±' + ph.V2.toFixed(0) + ' km/s', 4, 10);
}
