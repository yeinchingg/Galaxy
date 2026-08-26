from app.domain.star_physics import StarPhysicsCalculator


def test_sun_initial_properties():
    # 測試以太陽 (1.0 M☉) 為基準的計算
    props = StarPhysicsCalculator.compute_initial_properties(
        mass=1.0, metallicity=1.0, rotation=0.0
    )
    assert props.mass == 1.0
    assert props.luminosity_solar == 1.0
    assert props.radius_solar == 1.0
    assert props.lifetime_gyr == 10.0
    assert props.color.spectral_type == "G"


def test_massive_star_evolution_stage():
    # 質量 20 太陽質量，演化末期應成為中子星/黑洞
    stage, stage_name, l, r = StarPhysicsCalculator.calculate_evolution_state(
        mass=20.0, l0=1000, r0=10, age_frac=1.2
    )
    assert stage == "black_hole"
    assert "黑洞" in stage_name
