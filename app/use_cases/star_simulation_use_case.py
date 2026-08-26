"""
app/use_cases/star_simulation_use_case.py
應用案例層：調度物理領域模型，執行恆星演化模擬運算並回傳強型態 DTO (Pydantic Model)
"""

from typing import Optional
from pydantic import BaseModel, Field
from app.domain.star_physics import StarPhysicsCalculator


# --- 定義強型態 DTO (Pydantic Models) ---
class StarColorDTO(BaseModel):
    spectral_type: str = Field(..., description="光譜型 (如 O, B, A, F, G, K, M)")
    hex_code: str = Field(..., description="對應的 HEX 色碼")
    name: str = Field(..., description="顏色名稱描述")


class StarInitialResponseDTO(BaseModel):
    mass: float = Field(..., description="恆星質量 (太陽質量倍數)")
    metallicity: float = Field(..., description="金屬量")
    rotation: float = Field(..., description="自轉速率")
    luminosity_solar: float = Field(..., description="初始光度 (太陽光度倍數)")
    radius_solar: float = Field(..., description="初始半徑 (太陽半徑倍數)")
    temperature_k: float = Field(..., description="表面有效溫度 (K)")
    oblateness: float = Field(..., description="自轉扁率")
    lifetime_gyr: float = Field(..., description="主序星壽命 (十億年)")
    color: StarColorDTO


class StarEvolutionResponseDTO(StarInitialResponseDTO):
    age_gyr: float = Field(..., description="當前模擬年齡 (十億年)")
    age_fraction_of_lifetime: float = Field(..., description="年齡佔總壽命比例")
    stage: str = Field(..., description="演化階段英文代號")
    stage_name: str = Field(..., description="演化階段中文名稱")
    current_luminosity_solar: Optional[float] = Field(None, description="當前光度")
    current_radius_solar: Optional[float] = Field(None, description="當前半徑")
    current_temperature_k: Optional[int] = Field(None, description="當前溫度")
    current_color: StarColorDTO


class StarSimulationUseCase:
    def __init__(self, calculator: StarPhysicsCalculator = None):
        self.calculator = calculator or StarPhysicsCalculator()

    def get_initial_state(
        self, mass: float, metallicity: float = 1.0, rotation: float = 0.0
    ) -> StarInitialResponseDTO:
        """取得恆星初始狀態，並直接回傳強型態 DTO"""
        props = self.calculator.compute_initial_properties(mass, metallicity, rotation)

        return StarInitialResponseDTO(
            mass=props.mass,
            metallicity=props.metallicity,
            rotation=props.rotation,
            luminosity_solar=props.luminosity_solar,
            radius_solar=props.radius_solar,
            temperature_k=props.temperature_k,
            oblateness=props.oblateness,
            lifetime_gyr=props.lifetime_gyr,
            color=StarColorDTO(
                spectral_type=props.color.spectral_type,
                hex_code=props.color.hex_code,
                name=props.color.name,
            ),
        )

    def simulate_evolution(
        self, mass: float, metallicity: float, rotation: float, age_gyr: float
    ) -> StarEvolutionResponseDTO:
        """執行特定年齡下的演化模擬，並回傳完整的演化 DTO"""
        base_dto = self.get_initial_state(mass, metallicity, rotation)
        lifetime = base_dto.lifetime_gyr
        age_frac = age_gyr / lifetime if lifetime > 0 else 0.0

        stage, stage_name, current_l, current_r = (
            self.calculator.calculate_evolution_state(
                mass=mass,
                l0=base_dto.luminosity_solar,
                r0=base_dto.radius_solar,
                age_frac=age_frac,
            )
        )

        # 計算當前有效溫度與外觀顏色
        if current_l is not None and current_r and current_r > 0:
            current_temp = 5778 * (current_l / (current_r**2)) ** 0.25
        else:
            current_temp = 0.0

        current_color_props = self.calculator.temp_to_color(current_temp)

        # 透過 DTO 封裝回傳，享有 Pydantic 的型態保護與自動序列化
        return StarEvolutionResponseDTO(
            **base_dto.model_dump(),
            age_gyr=age_gyr,
            age_fraction_of_lifetime=round(age_frac, 3),
            stage=stage,
            stage_name=stage_name,
            current_luminosity_solar=(
                round(current_l, 5) if current_l is not None else None
            ),
            current_radius_solar=round(current_r, 5) if current_r is not None else None,
            current_temperature_k=round(current_temp) if current_temp > 0 else None,
            current_color=StarColorDTO(
                spectral_type=current_color_props.spectral_type,
                hex_code=current_color_props.hex_code,
                name=current_color_props.name,
            )
        )
