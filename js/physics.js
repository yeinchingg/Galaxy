var Physics = {
  /** 主計算入口：將 P 的參數轉化為物理量 */
  compute: function (p) {
    // 1. 從 log 質量還原為真實太陽質量
    const M = Math.pow(10, p.logM);

    // 2. 計算維里半徑 (星系引力影響範圍)
    // 公式簡化：質量越大，半徑開立方根後越大
    const Rv = Math.cbrt(M / (4 / 3 * Math.PI * 200 * 9.47e10)) * 1e3;

    // 3. 計算旋轉速度 (決定星星跑多快)
    // V = sqrt(G * M / R)
    const V2 = Math.sqrt(4.302e-3 * M / Rv * 1e-3) * 1000;

    // 4. 計算恆星總量 (假設為總質量的 2.8%)
    const Ms = M * 0.028;

    // 5. 恆星形成強度 (影響星星的藍色程度)
    const sfrE = Math.pow(10, p.sfr);

    // 核心回傳格式
    return {
      Rv: Rv,  // 對應 r-rv
      V2: V2,  // 對應 r-vv
      Ms: Ms   // 對應 r-ms
    };
  }
};
