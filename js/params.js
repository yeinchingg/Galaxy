// params.js
// ─────────────────────────────────────────────────────────────────────────────
// 【Model 層】所有可調參數的「單一來源」
//
// 職責：
//   1. P          — 目前星系的參數狀態物件（唯一真相來源）
//   2. SCHEMA     — 每個滑桿的 config（min/max/step/label/folder）
//                   ui.js 會讀取此表，自動生成 DOM，不需要在 HTML 手動填 min/max
//   3. PRESETS    — 10 個預設星系，使用 SCHEMA 中的 key 對應
//
// 擴充方式：只需在 SCHEMA 新增一筆 + 在 P 設定預設值，UI 會自動跟上。
// ─────────────────────────────────────────────────────────────────────────────

// ── 1. 當前參數狀態 ──────────────────────────────────────────────────────────
var P = {
  // 暗物質暈
  logM:12.5, conc:8, spin:0.04, ell:0.2,
  // 核球
  bd:0.2, br:0.8, smbh:7.5,
  // 恆星盤
  sersic:1.5, rd:3.5, incl:25, thick:0.08,
  // 星族
  gr:0.45, sfr:0.5, qprob:0.2, imf:'kroupa',
  // 氣體
  mhi:9.5, rhi:6.0, mh2:8.8, h2c:0.6,
  // 反饋
  agn:0.1, vout:200, snfb:0.1,
  // 併合
  merger:0, mratio:0.3, morb:45, msep:30,
  // 化學
  feh:-0.2, afe:0.1, tauZ:5,
  // 觀測
  telmode:'ideal', redshift:0.05, dust:0.3, band:'optical', ifumode:0
};

// ── 2. 滑桿 Schema（驅動 UI 自動生成）───────────────────────────────────────
//   folder: 對應左側面板分頁 's'=結構 'g'=氣體 'd'=動態 'o'=觀測
//   select: true 表示此項目由 HTML <select> 控制，不在 SCHEMA 生成 range
var SCHEMA = {
  // —— 結構 ——
  logM:     { min:10,    max:15,   step:0.1,   label:'log M_halo',    unit:'',        desc:'暗物質暈總質量',        folder:'s' },
  conc:     { min:2,     max:20,   step:0.5,   label:'集中度 c',      unit:'',        desc:'NFW 輪廓集中度',        folder:'s' },
  spin:     { min:0.01,  max:0.15, step:0.005, label:'自旋 λ',        unit:'',        desc:'角動量自旋參數',        folder:'s' },
  ell:      { min:0,     max:0.6,  step:0.02,  label:'橢圓率 ε',      unit:'',        desc:'',                      folder:'s' },
  bd:       { min:0,     max:2,    step:0.05,  label:'B/D 比',        unit:'',        desc:'核球/盤質量比',         folder:'s' },
  br:       { min:0.1,   max:5,    step:0.1,   label:'核球半徑',      unit:'kpc',     desc:'',                      folder:'s' },
  smbh:     { min:6,     max:10,   step:0.1,   label:'SMBH log M•',   unit:'',        desc:'超大質量黑洞質量',      folder:'s' },
  sersic:   { min:0.5,   max:6,    step:0.1,   label:'Sérsic n',      unit:'',        desc:'1=指數盤 4=橢圓',       folder:'s' },
  rd:       { min:0.5,   max:12,   step:0.5,   label:'盤半徑 Rd',     unit:'kpc',     desc:'',                      folder:'s' },
  incl:     { min:0,     max:90,   step:1,     label:'傾斜角',        unit:'°',       desc:'',                      folder:'s' },
  thick:    { min:0.01,  max:0.5,  step:0.01,  label:'盤厚度',        unit:'',        desc:'',                      folder:'s' },
  gr:       { min:-0.1,  max:0.9,  step:0.01,  label:'g-r 色指數',    unit:'',        desc:'',                      folder:'s' },
  sfr:      { min:-2,    max:3,    step:0.1,   label:'log SFR',       unit:'',        desc:'',                      folder:'s' },
  qprob:    { min:0,     max:1,    step:0.05,  label:'Quenching',     unit:'',        desc:'',                      folder:'s' },
  // —— 氣體 ——
  mhi:      { min:7,     max:11,   step:0.1,   label:'log M_HI',      unit:'M☉',     desc:'中性氫氣體質量',        folder:'g' },
  rhi:      { min:1,     max:25,   step:0.5,   label:'HI 盤半徑',     unit:'kpc',     desc:'HI 盤通常比恆星盤大',   folder:'g' },
  mh2:      { min:6,     max:11,   step:0.1,   label:'log M_H2',      unit:'M☉',     desc:'分子氣體質量',          folder:'g' },
  h2c:      { min:0.1,   max:1,    step:0.05,  label:'H₂ 集中度',     unit:'',        desc:'越高越集中於中央',      folder:'g' },
  agn:      { min:0,     max:1,    step:0.05,  label:'AGN 強度',      unit:'',        desc:'0=靜止 1=類星體',       folder:'g' },
  vout:     { min:0,     max:1500, step:50,    label:'外流速度',      unit:'km/s',    desc:'AGN+SN 驅動星系風',     folder:'g' },
  snfb:     { min:0,     max:1,    step:0.05,  label:'SN 反饋效率',   unit:'',        desc:'影響有效 SFR',          folder:'g' },
  // —— 動態 ——
  mratio:   { min:0.05,  max:1,    step:0.05,  label:'質量比 μ',      unit:'',        desc:'M2/M1',                 folder:'d' },
  morb:     { min:0,     max:180,  step:5,     label:'軌道傾角',      unit:'°',       desc:'',                      folder:'d' },
  msep:     { min:5,     max:100,  step:5,     label:'分離距離',      unit:'kpc',     desc:'',                      folder:'d' },
  feh:      { min:-2.5,  max:0.5,  step:0.05,  label:'[Fe/H]',        unit:'',        desc:'鐵豐度，0=太陽',        folder:'d' },
  afe:      { min:-0.2,  max:0.6,  step:0.05,  label:'[α/Fe]',        unit:'',        desc:'α元素比，厚盤指標',     folder:'d' },
  tauZ:     { min:0.5,   max:13,   step:0.5,   label:'化學時標 τ_Z',  unit:'Gyr',     desc:'',                      folder:'d' },
  // —— 觀測 ——
  redshift: { min:0.001, max:2,    step:0.01,  label:'紅移 z',        unit:'',        desc:'影響角直徑與PSF',       folder:'o' },
  dust:     { min:0,     max:5,    step:0.1,   label:'A_V 消光',      unit:'mag',     desc:'V-band 總消光量',       folder:'o' }
};

// ── 3. 預設星系 ──────────────────────────────────────────────────────────────
var PRESETS = {
  mw:       {logM:12.0,conc:10,spin:0.035,ell:0.15,bd:0.25,br:0.8, smbh:6.6,sersic:1.2,rd:3.5, incl:25,thick:0.07,gr:0.53,sfr:0.5, qprob:0.15,mhi:9.4, rhi:15,mh2:8.9,h2c:0.65,agn:0.02,vout:150, snfb:0.08,merger:0,mratio:0.3,morb:45, msep:30,feh:-0.1, afe:0.1, tauZ:5,  telmode:'ideal',redshift:0.001,dust:0.3, band:'optical',ifumode:0},
  m31:      {logM:12.2,conc:9, spin:0.04, ell:0.2, bd:0.4, br:1.0, smbh:8.1,sersic:2.0,rd:5.0, incl:77,thick:0.08,gr:0.6, sfr:0.8, qprob:0.2, mhi:9.6, rhi:20,mh2:9.0,h2c:0.6, agn:0.05,vout:200, snfb:0.1, merger:1,mratio:0.1,morb:30, msep:45,feh:-0.05,afe:0.08,tauZ:6,  telmode:'ideal',redshift:0.001,dust:0.25,band:'optical',ifumode:1},
  m33:      {logM:11.5,conc:8, spin:0.06, ell:0.2, bd:0.05,br:0.3, smbh:5.5,sersic:1.0,rd:2.8, incl:55,thick:0.06,gr:0.35,sfr:0.6, qprob:0.08,mhi:9.2, rhi:10,mh2:8.4,h2c:0.5, agn:0.0, vout:100, snfb:0.07,merger:0,mratio:0.3,morb:45, msep:30,feh:-0.35,afe:0.15,tauZ:4,  telmode:'ideal',redshift:0.001,dust:0.15,band:'optical',ifumode:0},
  lmc:      {logM:10.8,conc:6, spin:0.09, ell:0.35,bd:0.08,br:0.3, smbh:5.2,sersic:0.9,rd:1.8, incl:35,thick:0.1, gr:0.25,sfr:0.5, qprob:0.05,mhi:9.0, rhi:7, mh2:8.0,h2c:0.4, agn:0.0, vout:90,  snfb:0.08,merger:0,mratio:0.3,morb:45, msep:30,feh:-0.5, afe:0.2, tauZ:3.5,telmode:'ideal',redshift:0.001,dust:0.2, band:'optical',ifumode:0},
  smc:      {logM:10.0,conc:5, spin:0.08, ell:0.4, bd:0.05,br:0.2, smbh:5.0,sersic:0.8,rd:1.0, incl:40,thick:0.12,gr:0.2, sfr:0.3, qprob:0.05,mhi:8.8, rhi:5, mh2:7.5,h2c:0.3, agn:0.0, vout:80,  snfb:0.06,merger:0,mratio:0.3,morb:45, msep:30,feh:-0.6, afe:0.22,tauZ:3,  telmode:'ideal',redshift:0.001,dust:0.1, band:'optical',ifumode:0},
  blackeye: {logM:12.1,conc:8, spin:0.07, ell:0.25,bd:0.3, br:0.9, smbh:7.8,sersic:2.5,rd:5.5, incl:65,thick:0.09,gr:0.48,sfr:1.2, qprob:0.2, mhi:9.8, rhi:18,mh2:9.3,h2c:0.7, agn:0.15,vout:350, snfb:0.15,merger:2,mratio:0.2,morb:160,msep:12,feh:-0.2, afe:0.12,tauZ:4.5,telmode:'ideal',redshift:0.002,dust:0.5, band:'optical',ifumode:1},
  ell:      {logM:13.5,conc:5, spin:0.01, ell:0.5, bd:2.0, br:4.0, smbh:9.2,sersic:4.5,rd:8.0, incl:30,thick:0.4, gr:0.82,sfr:-1.5,qprob:0.95,mhi:8.0, rhi:8, mh2:7.0,h2c:0.2, agn:0.1, vout:500, snfb:0.05,merger:0,mratio:0.3,morb:45, msep:30,feh:0.1,  afe:-0.05,tauZ:10, telmode:'ideal',redshift:0.02, dust:0.1, band:'nir',   ifumode:0},
  sb:       {logM:11.5,conc:7, spin:0.09, ell:0.3, bd:0.1, br:0.4, smbh:7.0,sersic:1.0,rd:2.0, incl:50,thick:0.06,gr:0.1, sfr:2.8, qprob:0.02,mhi:10.0,rhi:8, mh2:9.8,h2c:0.8, agn:0.2, vout:600, snfb:0.2, merger:0,mratio:0.3,morb:45, msep:30,feh:-0.3, afe:0.25,tauZ:2,  telmode:'ideal',redshift:0.005,dust:0.8, band:'halpha', ifumode:0},
  q:        {logM:13.0,conc:6, spin:0.02, ell:0.35,bd:0.8, br:2.5, smbh:8.8,sersic:3.5,rd:6.0, incl:20,thick:0.3, gr:0.78,sfr:-2.0,qprob:0.9, mhi:8.2, rhi:10,mh2:7.2,h2c:0.15,agn:0.05,vout:300, snfb:0.05,merger:0,mratio:0.3,morb:45, msep:30,feh:0.05, afe:0.0, tauZ:10, telmode:'ideal',redshift:0.05, dust:0.05,band:'nir',   ifumode:0},
  agn:      {logM:12.8,conc:7, spin:0.03, ell:0.25,bd:0.6, br:1.5, smbh:9.5,sersic:2.5,rd:5.0, incl:35,thick:0.1, gr:0.6, sfr:1.5, qprob:0.3, mhi:9.0, rhi:12,mh2:8.5,h2c:0.6, agn:0.85,vout:1200,snfb:0.1, merger:0,mratio:0.3,morb:45, msep:30,feh:0.0,  afe:0.05,tauZ:5,  telmode:'ideal',redshift:0.05, dust:0.4, band:'optical', ifumode:0}
};
