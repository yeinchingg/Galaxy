// physics.js
// ─────────────────────────────────────────────────────────────────────────────
// 【Model 層】原子化物理公式
//
// 職責：
//   Physics 物件 — 每個方法只做「一件事」的純計算函數（原子函數）
//   Physics.compute(p) — 組合原子函數，一次回傳完整物理量快照
//
// 設計原則：
//   ✅ 所有函數為純函數（pure function）：輸入相同參數 → 輸出相同結果
//   ✅ 不觸碰任何 DOM、Three.js 物件、或全域 P（由呼叫方傳入）
//   ✅ 拆分粒度：每個原子函數對應 Python src/physics_models.py 的同名計算
//
// 對應 Python 端：src/physics_models.py
// ─────────────────────────────────────────────────────────────────────────────

var Physics = {

  // ── 暗物質暈（NFW Profile） ──────────────────────────────────────────────

  /** 維里質量 M_vir [M☉]，從 log10(M) 還原 */
  getM: function(logM) {
    return Math.pow(10, logM);
  },

  /** NFW 維里半徑 R_vir [kpc]
   *  公式：R_vir = (M / (4/3 π · 200 · ρ_crit))^(1/3)
   *  ρ_crit 以 9.47e10 M☉/kpc³ 近似 */
  getRvir: function(M) {
    return Math.cbrt(M / (4/3 * Math.PI * 200 * 9.47e10)) * 1e3;
  },

  /** NFW 特徵半徑 R_s [kpc] */
  getRs: function(Rvir, conc) {
    return Rvir / conc;
  },

  /** 維里速度 V_200 [km/s]
   *  公式：V_200 = sqrt(G·M / R_vir)，G = 4.302e-3 pc M☉⁻¹ (km/s)² */
  getVvir: function(M, Rvir) {
    return Math.sqrt(4.302e-3 * M / Rvir * 1e-3) * 1000;
  },

  /** 維里溫度 T_vir [K]
   *  公式：T_vir ∝ V_200² */
  getTvir: function(Vvir) {
    return 3.6e5 * Math.pow(Vvir / 100, 2);
  },

  // ── 恆星質量 ─────────────────────────────────────────────────────────────

  /** 恆星總質量 M★ [M☉]（含 IMF 修正與豐度匹配關係） */
  getMstar: function(M, imfName) {
    return 0.028 * Math.min(1, M / 1e12) * M * imfF(imfName);
  },

  /** 核球質量 M_bulge [M☉] */
  getMbulge: function(Mstar, bd) {
    return Mstar * bd / (1 + bd);
  },

  /** 盤質量 M_disk = M★ - M_bulge */
  getMdisk: function(Mstar, Mbulge) {
    return Mstar - Mbulge;
  },

  /** 核球與恆星質量比 B/T */
  getBT: function(Mbulge, Mstar) {
    return Mbulge / Mstar;
  },

  /** 黑洞質量 M• [M☉] */
  getMbh: function(smbh) {
    return Math.pow(10, smbh);
  },

  /** 半光半徑 R_half [kpc]（Sérsic 近似） */
  getRhalf: function(sersic, rd) {
    return rd * Math.pow(sersic, 0.5) * 0.5 + 0.5;
  },

  // ── SFR 與氣體 ────────────────────────────────────────────────────────────

  /** 有效恆星形成率 SFR_eff [M☉/yr]（扣除反饋壓制） */
  getSFReff: function(sfr, snfb, agn) {
    return Math.pow(10, sfr) * (1 - snfb * 0.6) * (1 - agn * 0.8);
  },

  /** HI + H₂ 氣體總質量 */
  getMgas: function(mhi, mh2) {
    return Math.pow(10, mhi) + Math.pow(10, mh2);
  },

  /** 氣體分率 f_gas */
  getFgas: function(Mgas, Mstar) {
    return Mgas / (Mstar + Mgas);
  },

  /** 氣體耗盡時標 t_dep [Gyr] */
  getTdep: function(Mgas, SFReff) {
    return Mgas / Math.max(0.01, SFReff) / 1e9;
  },

  // ── AGN 與外流 ────────────────────────────────────────────────────────────

  /** AGN 波耳光度 L_AGN [erg/s] */
  getLagn: function(agn, Mbh) {
    return agn > 0 ? agn * 1.26e38 * Mbh : 0;
  },

  /** 質量外流率 [M☉/yr] */
  getMout: function(SFReff, snfb, Lagn) {
    return SFReff * snfb * 10 + Lagn / 1e44 * 50;
  },

  /** 載荷因子 η = Ṁ_out / SFR */
  getEta: function(Mout, SFReff) {
    return Mout / Math.max(0.01, SFReff);
  },

  // ── 動力學 ───────────────────────────────────────────────────────────────

  /** 速度彌散 σ [km/s] */
  getSigma: function(Vvir, qprob) {
    return Vvir * 0.55 * (1 - qprob * 0.25);
  },

  /** Toomre Q 不穩定性參數（盤穩定性指標，> 1 穩定） */
  getToomreQ: function(sigma, conc, Vvir, rd) {
    return (sigma * conc * 0.08 / (Vvir * rd * 0.018)).toFixed(2);
  },

  /** Tully-Fisher 偏差 [mag]（觀測關係偏差量） */
  getTFdev: function(Vvir, Mstar) {
    var VTF = Math.pow(10,
      ((-19.5 + 2.5 * (Math.log10(Math.max(1, Mstar)) - 10.5)) + 2.07) / 0.28
    );
    return (Vvir - VTF) / VTF * 2.5;
  },

  // ── 主計算入口：組合所有原子函數 ─────────────────────────────────────────
  /**
   * Physics.compute(p)
   *   接受完整參數物件 p（通常傳入全域 P），
   *   回傳一個「物理快照」物件，包含所有計算結果。
   *
   *   呼叫範例：var ph = Physics.compute(P);
   */
  compute: function(p) {
    // 暗物質暈
    var M    = this.getM(p.logM);
    var Rv   = this.getRvir(M);
    var V2   = this.getVvir(M, Rv);
    var Tv   = this.getTvir(V2);
    var rs   = this.getRs(Rv, p.conc);

    // 恆星
    var Ms   = this.getMstar(M, p.imf);
    var Mb   = this.getMbulge(Ms, p.bd);
    var Md   = this.getMdisk(Ms, Mb);
    var BT   = this.getBT(Mb, Ms);
    var Mbh  = this.getMbh(p.smbh);
    var Rh   = this.getRhalf(p.sersic, p.rd);

    // SFR / 氣體
    var sfrE = this.getSFReff(p.sfr, p.snfb, p.agn);
    var Mhi  = Math.pow(10, p.mhi);
    var Mh2  = Math.pow(10, p.mh2);
    var Mg   = this.getMgas(p.mhi, p.mh2);
    var fg   = this.getFgas(Mg, Ms);
    var tdep = this.getTdep(Mg, sfrE);

    // AGN / 外流
    var Lagn = this.getLagn(p.agn, Mbh);
    var Mout = this.getMout(sfrE, p.snfb, Lagn);
    var eta  = this.getEta(Mout, sfrE);

    // 動力學
    var sig  = this.getSigma(V2, p.qprob);
    var Q    = this.getToomreQ(sig, p.conc, V2, p.rd);
    var TFdev= this.getTFdev(V2, Ms);

    return {
      M, Rv, V2, Tv, rs,
      Ms, Mb, Md, BT, Mbh, Rh,
      sfrE, sSFR: sfrE / Ms,
      Mhi, Mh2, Mg, fg, tdep,
      Lagn, Mout, eta,
      sig, Q, TFdev
    };
  }
};
