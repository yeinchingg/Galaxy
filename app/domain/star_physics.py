"""
app/domain/star_physics.py
核心領域層：恆星物理公式、光譜分類與演化階段判定（純 Python 規則，無外部依賴）
"""

from dataclasses import dataclass
from typing import Dict, Tuple, Optional

# 依溫度分類光譜型與近似顏色 (由高溫到低溫)
SPECTRAL_TABLE = [
    (30000, "O", "#9bb0ff", "藍色"),
    (10000, "B", "#aabfff", "藍白色"),
    (7500,  "A", "#cad7ff", "白色"),
    (6000,  "F", "#f8f7ff", "黃白色"),
    (5200,  "G", "#fff4ea", "黃色"),
    (3700,  "K", "#ffd2a1", "橙色"),
    (0,     "M", "#ffcc6f", "紅色"),
]


@dataclass(frozen=True)
class StarColor:
    spectral_type: str
    hex_code: str
    name: str


@dataclass
class InitialStarProps:
    mass: float
    metallicity: float
    rotation: float
    luminosity_solar: float
    radius_solar: float
    temperature_k: float
    oblateness: float
    lifetime_gyr: float
    color: StarColor


class StarPhysicsCalculator:
    """純天文物理計算引擎"""

    @staticmethod
    def temp_to_color(temp_k: float) -> StarColor:
        """根據表面有效溫度轉換光譜型與顏色"""
        if temp_k <= 0:
            return StarColor(spectral_type="-", hex_code="#333333", name="無法用溫度描述")

        for threshold, spectral_type, hex_color, name in SPECTRAL_TABLE:
            if temp_k >= threshold:
                return StarColor(spectral_type=spectral_type, hex_code=hex_color, name=name)
        return StarColor(spectral_type="M", hex_code="#ffcc6f", name="紅色")

    @staticmethod
    def compute_initial_properties(mass: float, metallicity: float = 1.0, rotation: float = 0.0) -> InitialStarProps:
        """計算恆星零齡主序星 (ZAMS) 初始物理參數"""
        mass = max(0.1, min(mass, 100.0))
        metallicity = max(0.0, min(metallicity, 2.0))
        rotation = max(0.0, min(rotation, 1.0))

        # 質量-光度與質量-半徑關係 (簡化模型)
        luminosity = mass ** 3.5
        radius = mass ** 0.74
        temperature = 5778 * (luminosity / (radius ** 2)) ** 0.25

        # 金屬遮蔽效應
        temperature *= (1 - 0.05 * (metallicity - 1))

        # 自轉扁率
        oblateness = 0.5 * (rotation ** 2)

        # 主序壽命 (十億年 Gyr)
        lifetime_gyr = 10 / (mass ** 2.5)

        color = StarPhysicsCalculator.temp_to_color(temperature)

        return InitialStarProps(
            mass=mass,
            metallicity=metallicity,
            rotation=rotation,
            luminosity_solar=round(luminosity, 3),
            radius_solar=round(radius, 3),
            temperature_k=round(temperature),
            oblateness=round(oblateness, 4),
            lifetime_gyr=round(lifetime_gyr, 3),
            color=color,
        )

    @staticmethod
    def calculate_evolution_state(mass: float, l0: float, r0: float, age_frac: float) -> Tuple[str, str, Optional[float], Optional[float]]:
        """依年齡比例計算演化階段與當前光度/半徑倍數"""
        if age_frac < 0.9:
            stage = "main_sequence"
            stage_name = "主序星"
            l = l0 * (1 + 0.3 * age_frac)
            r = r0 * (1 + 0.2 * age_frac)
        elif age_frac < 1.0:
            stage = "subgiant"
            stage_name = "次巨星（即將離開主序）"
            t = (age_frac - 0.9) / 0.1
            l = l0 * (1.3 + 0.7 * t)
            r = r0 * (1.2 + 1.5 * t)
        elif age_frac < 1.15:
            stage = "giant"
            stage_name = "紅巨星" if mass < 8 else "紅超巨星"
            t = (age_frac - 1.0) / 0.15
            l = l0 * (2.0 + 20 * t)
            r = r0 * (2.7 + 50 * t)
        else:
            # 演化末期殘骸判定
            if mass < 0.5:
                stage, stage_name = "white_dwarf", "白矮星（極低質量恆星最終型態，理論上需比宇宙年齡更久）"
                r, l = 0.01, 0.0005
            elif mass < 8:
                stage, stage_name = "white_dwarf", "白矮星"
                r, l = 0.01, 0.001
            elif mass < 20:
                stage, stage_name = "neutron_star", "超新星爆炸後 → 中子星"
                r, l = 0.00001, 0.0
            else:
                stage, stage_name = "black_hole", "超新星爆炸後 → 黑洞"
                r, l = 0.0, 0.0

        return stage, stage_name, l, r