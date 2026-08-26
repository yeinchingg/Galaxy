from dataclasses import dataclass


@dataclass
class StarPhysicalState:
    mass: float  # 太陽質量 M☉
    luminosity: float  # 太陽光度 L☉
    temperature: float  # 表面溫度 (K)
    stage: str  # 演化階段
