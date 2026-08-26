from app.use_cases.star_simulation_use_case import StarSimulationUseCase


def test_simulation_use_case_main_sequence():
    use_case = StarSimulationUseCase()
    result = use_case.simulate_evolution(
        mass=1.0, metallicity=1.0, rotation=0.0, age_gyr=4.6
    )

    assert result["stage"] == "main_sequence"
    assert result["age_gyr"] == 4.6
    assert result["current_temperature_k"] is not None
    assert result["current_color"]["spectral_type"] == "G"
