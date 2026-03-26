# Galaxy Simulator 3D — 重構版

互動式 3D 星系模擬器。使用 Three.js WebGL 渲染粒子系統，可調整 30+ 天文物理參數，即時更新旋轉曲線、氣體剖面、化學相空間等圖表。

---

## 目錄結構

```
GalaxyFrontend/
├── index.html               # 主頁面：所有 UI DOM
├── style.css                # 樣式
├── vendor/
│   └── three.min.js         # Three.js r128（本地）
└── js/
    ├── params.js            # [Model]    參數狀態 P、SCHEMA、PRESETS
    ├── helpers.js           # [工具]     純數學函數（randn、hsl2rgb…）
    ├── physics.js           # [Model]    原子化物理公式 + Physics.compute()
    ├── renderer.js          # [View]     Three.js 初始化 + 相機 + 渲染迴圈
    ├── galaxy_builder.js    # [View]     粒子 Pipeline（Galaxy.build）
    ├── charts.js            # [View]     5 個 mini Canvas 圖表
    └── ui.js                # [Presenter] Store + 單向數據流 + 滑桿綁定
```

---

## 架構說明：MVP 變體

本專案採用「**Model → Presenter/Store → View**」三層架構，確保每個檔案只負責一件事。

```
使用者操作滑桿
      │
      ▼
┌─────────────────────────────────────┐
│  Presenter / Store  (ui.js)         │
│  Store.update(key, value)           │
│    → P[key] = value                 │
│    → simulate()                     │
└──────────┬──────────────────────────┘
           │
     ┌─────┴───────┐
     ▼             ▼
┌─────────┐   ┌──────────────────────────┐
│  Model  │   │  View                    │
│         │   │                          │
│params.js│   │ Galaxy.build(P, ph)      │
│  P 物件  │   │   → BufferAttribute 更新 │
│  SCHEMA │   │   → attributes.needsUpdate│
│  PRESETS│   │                          │
│         │   │ updateReadout(ph)         │
│physics.js   │   → setText(...) DOM     │
│  Physics│   │   → drawRotCurve(ph)     │
│  .compute   │   → drawGasProfile(P)    │
│  (P)→ph │   │   → drawChemPlot(P)      │
│         │   │   → drawSFH(ph, P)       │
└─────────┘   │   → drawIFU(ph, P)       │
              │                          │
              │ renderer.js              │
              │   → WebGL render loop    │
              └──────────────────────────┘
```

---

## 各檔案職責詳解

### `js/params.js` — 單一參數來源

**職責：定義所有參數的預設值、邊界、與 UI 設定。**

| 匯出物件 | 說明 |
|----------|------|
| `P`       | 當前星系的參數狀態（唯一真相來源）。所有計算皆讀取 `P`，修改只能透過 `Store.update()` |
| `SCHEMA`  | 每個滑桿的設定表（min/max/step/label/unit/desc/folder）。`ui.js` 讀取此表自動綁定事件 |
| `PRESETS` | 10 個預設星系的完整參數快照（銀河系、M31、AGN…） |

**擴充方式**：想新增參數 `foo`，只需：
1. 在 `P` 加入 `foo: 預設值`
2. 在 `SCHEMA` 加入 `foo: { min, max, step, label, folder }`
3. 在 `index.html` 對應 pane 加入 `<input type="range" id="foo">`

`ui.js` 的滑桿綁定迴圈會自動偵測並連結，無需改動 `ui.js`。

---

### `js/helpers.js` — 通用數學工具

**職責：純函數工具，不依賴任何全域狀態。**

| 函數 | 說明 |
|------|------|
| `randn()` | Box-Muller 法產生常態分佈亂數 N(0,1) |
| `sersicR(n)` | 依 Sérsic index 取樣粒子半徑（累積分佈反函數近似） |
| `hsl2rgb(h, s, l)` | HSL → [0,1] 浮點 RGB 三元組 |
| `imfF(imfName)` | IMF 名稱 → 質量修正係數（Kroupa/Salpeter/Chabrier） |
| `clamp(v, lo, hi)` | 數值夾取 |

> **重構差異**：原版 `imfF()` 直接讀取全域 `P.imf`；重構版接受參數 `imfF(imfName)`，為純函數，方便單元測試。

---

### `js/physics.js` — 原子化物理公式

**職責：純計算，不觸碰 DOM 或 Three.js。**

#### 設計：原子函數 + 組合入口

```javascript
// 每個原子函數只做一件事
Physics.getM(logM)          // M_vir 維里質量
Physics.getRvir(M)          // R_vir 維里半徑
Physics.getVvir(M, Rvir)    // V_200 維里速度
Physics.getTvir(Vvir)       // T_vir 維里溫度
Physics.getMstar(M, imf)    // M★ 恆星質量
Physics.getSFReff(sfr, snfb, agn)  // 有效 SFR
// ... 共 14 個原子函數

// 組合入口：一次計算所有物理量
var ph = Physics.compute(P);
// ph → { M, Rv, V2, Tv, rs, Ms, Mb, Md, BT, Mbh, Rh,
//         sfrE, sSFR, Mhi, Mh2, Mg, fg, tdep,
//         Lagn, Mout, eta, sig, Q, TFdev }
```

**修東西時只需看這個檔案**：
- 旋轉速度不對 → 修 `getVvir()`
- SFR 計算有誤 → 修 `getSFReff()`
- 氣體耗盡時標錯 → 修 `getTdep()`

> **重構差異**：原版是一個 `phys()` 函數算完所有東西；重構版拆成 14 個原子函數，再由 `Physics.compute(p)` 組合，便於單獨測試與修改。

---

### `js/renderer.js` — Three.js 渲染引擎

**職責：WebGL 環境、相機、軌道控制、渲染迴圈。**

- 初始化 `WebGLRenderer`, `Scene`, `PerspectiveCamera`
- 球座標軌道控制（左鍵旋轉 / 右鍵平移 / 滾輪縮放）
- `autoSpin` 自動旋轉
- `resetCam()` 重設視角
- **不讀取 `P` 物件，不呼叫物理或 UI 函數**

---

### `js/galaxy_builder.js` — 粒子 Pipeline

**職責：依參數生成/更新 Three.js 粒子系統。**

#### Pipeline 流程

```
Galaxy.build(P, ph)
  │
  ├─ fillAttributes(p, ph)      ← 填入 position/color/size TypedArray
  │    ├─ 薄盤   70,000 粒子
  │    ├─ 厚盤    9,000 粒子
  │    ├─ 暗物質暈 6,000 粒子
  │    ├─ 核球   最多 14,000 粒子（依 bd 參數）
  │    ├─ HII 發射區（依 sfr）
  │    ├─ HI 氣體盤（依 mhi）
  │    ├─ AGN 噴流（依 agn）
  │    └─ 併合伴星系（依 merger）
  │
  ├─ 首次呼叫：new THREE.BufferGeometry + THREE.Points
  └─ 後續呼叫：attributes.needsUpdate = true（不重建物件）
               setDrawRange(0, idx)
```

#### 效能關鍵：屬性更新而非重建

```javascript
// ❌ 原版：每次滑桿變動都 new 新物件（FPS 下降）
scene.remove(gG);
gG = new THREE.Group();
// ... 重新建立所有 Points

// ✅ 重構版：只更新 TypedArray，標記 needsUpdate
_geo.attributes.position.array.set(_pos.subarray(0, idx * 3));
_geo.attributes.position.needsUpdate = true;
_geo.setDrawRange(0, idx);
```

**修東西時只需看這個檔案**：
- 星星太亮/太暗 → 修 `createShaderMaterial()` 的 fragmentShader
- 旋臂形狀不對 → 修薄盤迴圈的 `arm` 計算
- 併合粒子位置錯 → 修「併合伴星系」區塊

---

### `js/charts.js` — 圖表繪製

**職責：接收數據並繪製 Canvas 圖表；不讀取全域 `P`（改為接受參數）。**

| 函數 | 輸入 | 說明 |
|------|------|------|
| `drawRotCurve(ph)` | 物理快照 | NFW+盤+核球旋轉曲線 |
| `drawGasProfile(p)` | 參數物件 | HI/H₂/恆星盤 radial profile |
| `drawChemPlot(p)` | 參數物件 | [Fe/H]−[α/Fe] 相空間散點圖 |
| `drawSFH(ph, p)` | 快照+參數 | 恆星形成歷史 SFR(t) + Z(t) |
| `drawIFU(ph, p)` | 快照+參數 | 視線速度 IFU mock 色圖 |

> **重構差異**：原版函數內部直接讀取全域 `P`；重構版改為接受 `p` 參數，資料由 `ui.js` 的 `updateReadout()` 傳入，符合「由外部注入資料」原則。

---

### `js/ui.js` — Presenter / Store

**職責：橋接使用者操作與 Model/View；實現單向數據流。**

#### Store 物件（唯一參數修改入口）

```javascript
// 所有 UI 事件最終都呼叫此函數
Store.update('logM', 12.5);
// 內部：P['logM'] = 12.5 → simulate()
```

#### SCHEMA 驅動的自動滑桿綁定

```javascript
// 不需要為每個滑桿手動寫 addEventListener
// 只需讀取 SCHEMA，用迴圈一次綁定
Object.keys(SCHEMA).forEach(function(key) {
  var el = document.getElementById(key);
  el.addEventListener('input', function() {
    Store.update(key, parseFloat(el.value));
  });
});
```

**擴充時只需改 `params.js` 的 SCHEMA，`ui.js` 不需要動。**

---

## 數據流總覽

```
使用者拖動滑桿（id="logM"）
  ↓
ui.js: input event → Store.update('logM', 12.5)
  ↓
ui.js: P['logM'] = 12.5
  ↓
ui.js: simulate()
  ↓
  ├──→ Physics.compute(P)
  │      → 呼叫 14 個原子函數
  │      → 回傳 ph（物理快照）
  │
  ├──→ Galaxy.build(P, ph)
  │      → fillAttributes() 填充 TypedArray
  │      → attributes.needsUpdate = true
  │      → setDrawRange(0, idx)
  │      → 更新 HUD 文字
  │
  └──→ updateReadout(ph)
         → setText() × N（右側面板）
         → drawRotCurve(ph)
         → drawGasProfile(P)
         → drawChemPlot(P)
         → drawSFH(ph, P)
         → drawIFU(ph, P)
```

---

## 常見修改指引

| 想修改什麼 | 去哪個檔案 |
|-----------|-----------|
| 物理公式（Rvir、SFR…） | `physics.js` → 對應原子函數 |
| 粒子顏色 / 發光效果 | `galaxy_builder.js` → `createShaderMaterial()` |
| 旋臂、盤結構 | `galaxy_builder.js` → `fillAttributes()` 薄盤區塊 |
| 新增/修改滑桿 | `params.js` SCHEMA + `index.html` 加 `<input>` |
| 右側數值顯示錯誤 | `ui.js` → `updateReadout()` 對應欄位 |
| 圖表樣式 | `charts.js` → 對應 `drawXxx()` 函數 |
| 相機 / 旋轉控制 | `renderer.js` |
| 預設星系數值 | `params.js` → `PRESETS` |

---

## 載入順序（index.html）

```html
<script src="vendor/three.min.js"></script>  <!-- 1. 三方庫 -->
<script src="js/params.js"></script>          <!-- 2. 狀態定義（P, SCHEMA, PRESETS） -->
<script src="js/helpers.js"></script>         <!-- 3. 純工具函數 -->
<script src="js/physics.js"></script>         <!-- 4. 物理計算（依賴 helpers） -->
<script src="js/renderer.js"></script>        <!-- 5. Three.js 環境（建立 scene, camera） -->
<script src="js/galaxy_builder.js"></script>  <!-- 6. 粒子系統（依賴 scene） -->
<script src="js/charts.js"></script>          <!-- 7. 圖表（依賴 helpers） -->
<script src="js/ui.js"></script>              <!-- 8. 事件綁定（依賴全部，最後載入，末尾呼叫 simulate()） -->
```

`simulate()` 在 `ui.js` 末尾呼叫，確保所有模組都已初始化後才啟動。

---

## 重構前後對比

| 面向 | 重構前 | 重構後 |
|------|--------|--------|
| 物理計算 | 一個 `phys()` 函數算完所有量 | 14 個原子函數 + `Physics.compute()` 組合 |
| 粒子更新 | 每次 `new THREE.Group()` 重建 | `attributes.needsUpdate = true`，不重建 |
| 滑桿綁定 | 手動為每個 id 寫 `addEventListener` | SCHEMA 迴圈自動綁定 |
| 圖表資料來源 | 直接讀取全域 `P` | 接受 `p` 參數注入 |
| `imfF()` | 直接讀取 `P.imf`（有副作用） | 接受 `imfName` 參數（純函數） |
| 數據流 | 散落各處的 `P.xxx = ...` | 統一透過 `Store.update()` |
| 擴充參數 | 需改 ui.js + params.js + HTML | 只需改 params.js SCHEMA + HTML |
