# star_engine.py
"""
簡化版恆星演化物理模擬。
注意：這是教學用簡化模型，公式經過簡化以利即時互動展示，非精確天文模擬。

輸入：質量 (太陽質量倍數)、金屬量指數 (0~2，1=太陽)、自轉比例 (0~1，1=接近臨界自轉速度)
輸出：光度、半徑、溫度、顏色、扁率(形狀)、主序壽命，以及依「年齡」推算的目前演化階段
"""

import math

# 依溫度分類光譜型與近似顏色 (由高溫到低溫)
_SPECTRAL_TABLE = [
    (30000, "O", "#9bb0ff", "藍色"),
    (10000, "B", "#aabfff", "藍白色"),
    (7500,  "A", "#cad7ff", "白色"),
    (6000,  "F", "#f8f7ff", "黃白色"),
    (5200,  "G", "#fff4ea", "黃色"),
    (3700,  "K", "#ffd2a1", "橙色"),
    (0,     "M", "#ffcc6f", "紅色"),
]


def _temp_to_color(temp_k: float) -> dict:
    for threshold, spectral_type, hex_color, name in _SPECTRAL_TABLE:
        if temp_k >= threshold:
            return {"spectral_type": spectral_type, "hex": hex_color, "name": name}
    return {"spectral_type": "M", "hex": "#ffcc6f", "name": "紅色"}


class StarSimulator:

    def compute_initial(self, mass: float, metallicity: float = 1.0, rotation: float = 0.0) -> dict:
        """
        mass: 太陽質量倍數 (0.1 ~ 50 建議範圍)
        metallicity: 0~2，1 為太陽金屬量
        rotation: 0~1，自轉速度占臨界(瓦解)自轉速度的比例
        """
        mass = max(0.1, min(mass, 100))
        metallicity = max(0.0, min(metallicity, 2.0))
        rotation = max(0.0, min(rotation, 1.0))

        luminosity = mass ** 3.5  # 太陽光度倍數
        radius = mass ** 0.74     # 太陽半徑倍數
        temperature = 5778 * (luminosity / radius ** 2) ** 0.25

        # 金屬量越高，因線遮蔽效應，同質量下溫度略低（外觀偏紅）
        temperature *= (1 - 0.05 * (metallicity - 1))

        # 自轉造成扁率（形狀被拉扁），簡化為 0.5 * (自轉比例)^2
        oblateness = 0.5 * rotation ** 2

        lifetime_gyr = 10 / (mass ** 2.5)  # 主序壽命 (十億年)

        color = _temp_to_color(temperature)

        return {
            "mass": mass,
            "metallicity": metallicity,
            "rotation": rotation,
            "luminosity_solar": round(luminosity, 3),
            "radius_solar": round(radius, 3),
            "temperature_k": round(temperature),
            "oblateness": round(oblateness, 4),
            "lifetime_gyr": round(lifetime_gyr, 3),
            "color": color,
        }

    def evolve(self, mass: float, metallicity: float, rotation: float, age_gyr: float) -> dict:
        """依輸入年齡計算恆星目前狀態與所處的演化階段"""
        base = self.compute_initial(mass, metallicity, rotation)
        lifetime = base["lifetime_gyr"]
        age_frac = age_gyr / lifetime if lifetime > 0 else 0

        L0, R0 = base["luminosity_solar"], base["radius_solar"]

        if age_frac < 0.9:
            stage = "main_sequence"
            stage_name = "主序星"
            L = L0 * (1 + 0.3 * age_frac)
            R = R0 * (1 + 0.2 * age_frac)
        elif age_frac < 1.0:
            stage = "subgiant"
            stage_name = "次巨星（即將離開主序）"
            t = (age_frac - 0.9) / 0.1
            L = L0 * (1.3 + 0.7 * t)
            R = R0 * (1.2 + 1.5 * t)
        elif age_frac < 1.15:
            stage = "giant"
            stage_name = "紅巨星" if mass < 8 else "紅超巨星"
            t = (age_frac - 1.0) / 0.15
            L = L0 * (2.0 + 20 * t)
            R = R0 * (2.7 + 50 * t)
        else:
            # 主序後終點，依質量分岔
            L = None
            if mass < 0.5:
                stage, stage_name = "white_dwarf", "白矮星（極低質量恆星最終型態，理論上需比宇宙年齡更久）"
                R, L = 0.01, 0.0005
            elif mass < 8:
                stage, stage_name = "white_dwarf", "白矮星"
                R, L = 0.01, 0.001
            elif mass < 20:
                stage, stage_name = "neutron_star", "超新星爆炸後 → 中子星"
                R, L = 0.00001, 0.0
            else:
                stage, stage_name = "black_hole", "超新星爆炸後 → 黑洞"
                R, L = 0.0, 0.0

        temperature = 5778 * (L / R ** 2) ** 0.25 if (L and R) else 0
        color = _temp_to_color(temperature) if temperature else {
            "spectral_type": "-", "hex": "#333333", "name": "無法用溫度描述"}

        return {
            **base,
            "age_gyr": age_gyr,
            "age_fraction_of_lifetime": round(age_frac, 3),
            "stage": stage,
            "stage_name": stage_name,
            "current_luminosity_solar": round(L, 5) if L is not None else None,
            "current_radius_solar": round(R, 5) if R is not None else None,
            "current_temperature_k": round(temperature) if temperature else None,
            "current_color": color,
        }
