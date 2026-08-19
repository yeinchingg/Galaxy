import math

class StellarPhysics:
    @staticmethod
    def calculate_schwarzschild_radius(mass_kg: float) -> float:
        """計算史瓦西半徑 (m)"""
        G = 6.67430e-11
        c = 299792458
        return (2 * G * mass_kg) / (c ** 2)

    @staticmethod
    def determine_stellar_stage(mass: float, progress: float) -> str:
        """依質量與演化進度判定階段 (progress 0.0 ~ 1.0)"""
        if progress < 0.15:
            return "星雲塌縮 / 原恆星"
        elif progress < 0.65:
            return "主序星平衡 (Main Sequence)"
        elif progress < 0.85:
            return "紅巨星膨脹 (Red Giant)"
        else:
            return "中子星/黑洞" if mass > 8.0 else "白矮星殘骸 (White Dwarf)"