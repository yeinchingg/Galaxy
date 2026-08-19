import pytest
from app.domain.physics_engine import StellarPhysics

def test_schwarzschild_radius_calculation():
    sun_mass = 1.989e30
    rs = StellarPhysics.calculate_schwarzschild_radius(sun_mass)
    # 太陽史瓦西半徑約為 2954 公尺 (~3 km)
    assert pytest.approx(rs, rel=1e-2) == 2954.0

def test_stellar_stage_determination():
    assert StellarPhysics.determine_stellar_stage(1.0, 0.5) == "主序星平衡 (Main Sequence)"
    assert StellarPhysics.determine_stellar_stage(1.0, 0.95) == "白矮星殘骸 (White Dwarf)"
    assert StellarPhysics.determine_stellar_stage(20.0, 0.95) == "中子星/黑洞"