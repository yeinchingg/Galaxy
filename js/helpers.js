// helpers.js
// ─────────────────────────────────────────────────────────────────────────────
// 【通用工具層】純數學工具函數，不依賴任何全域狀態
//
// 職責：
//   randn()        — Box-Muller 法產生常態分佈亂數 N(0,1)
//   sersicR(n)     — 依 Sérsic index 取樣半徑（累積分佈反函數近似）
//   hsl2rgb(h,s,l) — HSL 轉 [0,1] RGB 三元組
//   imfF(imf)      — 根據 IMF 名稱回傳質量修正係數
//   kpcToPc(kpc)   — 單位換算：kpc → pc
//   clamp(v,lo,hi) — 數值夾取
//
// 注意：所有函數皆為純函數（pure function），不讀取/修改全域 P 物件。
//       需要 IMF 時請傳入字串，不要直接讀取 P.imf。
// ─────────────────────────────────────────────────────────────────────────────

// ── 常態分佈亂數（Box-Muller Transform） ────────────────────────────────────
function randn() {
  var u = 0, v = 0;
  while (!u) u = Math.random();
  while (!v) v = Math.random();
  return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
}

// ── Sérsic 半徑取樣 ──────────────────────────────────────────────────────────
// 以冪次方近似 Sérsic 累積分佈的反函數，供粒子位置隨機取樣
function sersicR(n) {
  return Math.pow(-Math.log(1 - Math.random() * 0.9998), n);
}

// ── HSL → RGB（回傳 [0,1] 範圍的浮點陣列） ──────────────────────────────────
function hsl2rgb(h, s, l) {
  h /= 360; s /= 100; l /= 100;
  var q = l < 0.5 ? l * (1 + s) : l + s - l * s;
  var p = 2 * l - q;
  function hue2rgb(t) {
    t = ((t % 1) + 1) % 1;
    if (t < 1/6) return p + (q - p) * 6 * t;
    if (t < 0.5) return q;
    if (t < 2/3) return p + (q - p) * (2/3 - t) * 6;
    return p;
  }
  return [hue2rgb(h + 1/3), hue2rgb(h), hue2rgb(h - 1/3)];
}

// ── IMF 質量修正係數 ─────────────────────────────────────────────────────────
// 傳入 IMF 名稱字串，回傳相對於 Kroupa 的恆星質量比例係數
// 純函數版：接受參數，不直接讀取 P.imf
function imfF(imfName) {
  if (imfName === 'salpeter') return 1.7;
  if (imfName === 'chabrier') return 0.95;
  return 1.0; // kroupa (預設)
}

// ── 單位換算 ─────────────────────────────────────────────────────────────────
function kpcToPc(kpc) { return kpc * 1e3; }
function pcToKpc(pc)  { return pc  * 1e-3; }

// ── 夾取工具 ─────────────────────────────────────────────────────────────────
function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }
