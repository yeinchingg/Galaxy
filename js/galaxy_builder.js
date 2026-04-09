// ── 整合 AI 邏輯與進階渲染的 Galaxy 模組 ──
var Galaxy = (function () {
  var _group = null, _points = null, _geo = null;
  var _totalMax = 150000; // 預留最大粒子空間

  // 1. 預分配 TypedArray
  var _pos = new Float32Array(_totalMax * 3);
  var _col = new Float32Array(_totalMax * 3);
  var _sz = new Float32Array(_totalMax);

  /**
   * 內部函式：建立發光星雲 Shader
   */
  function createAdvancedShader(glow) {
    return new THREE.ShaderMaterial({
      uniforms: { uGlow: { value: glow } },
      transparent: true,
      blending: THREE.AdditiveBlending, // 讓點重疊時產生發光感
      depthWrite: false,
      vertexShader: `
        attribute float aSize;
        attribute vec3 aColor;
        varying vec3 vCol;
        void main() {
          vCol = aColor;
          vec4 mv = modelViewMatrix * vec4(position, 1.0);
          gl_PointSize = aSize * (800.0 / -mv.z); 
          gl_Position = projectionMatrix * mv;
        }
      `,
      fragmentShader: `
        varying vec3 vCol;
        uniform float uGlow;
        void main() {
          float d = length(gl_PointCoord - vec2(0.5));
          if (d > 0.5) discard;
          float strength = pow(1.0 - d * 2.0, 3.0) * uGlow;
          gl_FragColor = vec4(vCol, strength);
        }
      `
    });
  }

  return {
    build: function (p, ph) {
      // --- A. AI 數據清洗 (防止 NaN) ---
      const Ms = parseFloat(ph.Ms) || 1e10;
      const rd = parseFloat(p.rd) || 5.0;
      const distort = parseFloat(ph.ai_distort) || 0;
      const glow = parseFloat(ph.glow_size) || 1.0;
      const base_rgb = ph.base_color || { r: 0.5, g: 0.7, b: 1.0 };

      // 決定要畫多少點 (根據質量 Log 值調整，避免太多)
      let renderCount = Math.floor(Math.log10(Ms) * 1500);
      renderCount = Math.min(_totalMax, Math.max(500, renderCount));

      let idx = 0;
      for (let i = 0; i < renderCount; i++) {
        let sR = (typeof sersicR === 'function') ? sersicR(p.sersic || 1.5) : 1.0;
        if (isNaN(sR)) sR = 1.0;

        let r = sR * rd * (0.4 + Math.random() * 0.8);
        let phi = Math.random() * Math.PI * 2;

        // --- 方向 A：AI 歪斜感公式 ---
        let distortFactor = 1 + distort * Math.sin(phi * 2);
        let x = r * Math.cos(phi) * distortFactor;
        let z = r * Math.sin(phi) * (2 - distortFactor);
        let y = (typeof randn === 'function' ? randn() : (Math.random() - 0.5)) * rd * (p.thick || 0.1);

        if (isNaN(x) || isNaN(y) || isNaN(z)) continue;

        _pos[idx * 3] = x; _pos[idx * 3 + 1] = y; _pos[idx * 3 + 2] = z;
        _col[idx * 3] = base_rgb.r; _col[idx * 3 + 1] = base_rgb.g; _col[idx * 3 + 2] = base_rgb.b;
        _sz[idx] = 0.6 + Math.random() * 1.2;
        idx++;
      }

      // --- B. GPU 渲染更新邏輯 ---
      if (!_geo) {
        // [第一次建立]
        _geo = new THREE.BufferGeometry();
        _geo.setAttribute('position', new THREE.BufferAttribute(_pos, 3));
        _geo.setAttribute('aColor', new THREE.BufferAttribute(_col, 3));
        _geo.setAttribute('aSize', new THREE.BufferAttribute(_sz, 1));

        const material = createAdvancedShader(glow);
        _points = new THREE.Points(_geo, material);
        _group = new THREE.Group();
        _group.add(_points);

        if (typeof scene !== 'undefined') {
          scene.add(_group);
        }
      } else {
        // [更新數據]
        _geo.attributes.position.needsUpdate = true;
        _geo.attributes.aColor.needsUpdate = true;
        _geo.attributes.aSize.needsUpdate = true;

        // 更新 AI 給的光暈值
        _points.material.uniforms.uGlow.value = glow;

        // 核心修正：手動計算邊界，解決 NaN Error
        _geo.computeBoundingSphere();
      }

      _geo.setDrawRange(0, idx);

      // 更新傾斜角 (來自使用者參數)
      if (_group) _group.rotation.z = (p.incl || 0) * Math.PI / 180 * 0.35;
    }
  };
})();