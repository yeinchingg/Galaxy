"""
app/use_cases/star_simulation_use_case.py
應用案例層：調度物理領域模型，執行恆星演化模擬運算並回傳格式化結果
"""

from typing import Dict, Any
from app.domain.star_physics import StarPhysicsCalculator


class StarSimulationUseCase:
    def __init__(self, calculator: StarPhysicsCalculator = None):
        self.calculator = calculator or StarPhysicsCalculator()

    def get_initial_state(self, mass: float, metallicity: float = 1.0, rotation: float = 0.0) -> Dict[str, Any]:
        """取得恆星初始狀態 (API/UI 使用)"""
        props = self.calculator.compute_initial_properties(mass, metallicity, rotation)
        return {
            "mass": props.mass,
            "metallicity": props.metallicity,
            "rotation": props.rotation,
            "luminosity_solar": props.luminosity_solar,
            "radius_solar": props.radius_solar,
            "temperature_k": props.temperature_k,
            "oblateness": props.oblateness,
            "lifetime_gyr": props.lifetime_gyr,
            "color": {
                "spectral_type": props.color.spectral_type,
                "hex": props.color.hex_code,
                "name": props.color.name,
            },
        }

    def simulate_evolution(self, mass: float, metallicity: float, rotation: float, age_gyr: float) -> Dict[str, Any]:
        """執行特定年齡下的演化模擬"""
        base = self.get_initial_state(mass, metallicity, rotation)
        lifetime = base["lifetime_gyr"]
        age_frac = age_gyr / lifetime if lifetime > 0 else 0.0

        stage, stage_name, current_l, current_r = self.calculator.calculate_evolution_state(
            mass=mass,
            l0=base["luminosity_solar"],
            r0=base["radius_solar"],
            age_frac=age_frac
        )

        # 計算當前有效溫度與外觀顏色
        if current_l is not None and current_r and current_r > 0:
            current_temp = 5778 * (current_l / (current_r ** 2)) ** 0.25
        else:
            current_temp = 0.0

        current_color = self.calculator.temp_to_color(current_temp)

        return {
            **base,
            "age_gyr": age_gyr,
            "age_fraction_of_lifetime": round(age_frac, 3),
            "stage": stage,
            "stage_name": stage_name,
            "current_luminosity_solar": round(current_l, 5) if current_l is not None else None,
            "current_radius_solar": round(current_r, 5) if current_r is not None else None,
            "current_temperature_k": round(current_temp) if current_temp > 0 else None,
            "current_color": {
                "spectral_type": current_color.spectral_type,
                "hex": current_color.hex_code,
                "name": current_color.name,
            },
        }