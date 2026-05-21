import pytest
from uuid import UUID
from datetime import date

from triathlon_planner.models.session_template import CardioBlock
from triathlon_planner.models.generated_session import GeneratedCardioBlock
from triathlon_planner.models.athlete_profile import (
    AthleteProfile,
    GoalProfile,
    Availability,
    DisciplineProfiles,
    RunDisciplineProfile,
    BikeDisciplineProfile,
    SwimDisciplineProfile,
    RunPerformanceMetrics,
    BikePerformanceMetrics,
    SwimPerformanceMetrics,
    Constraints,
    Injury,
    Equipment,
    TrainingState,
)
from triathlon_planner.generation.calculator import (
    pace_from_zone,
    watts_from_zone,
    heart_rate_from_zone,
    swim_pace_from_zone,
    generate_cardio_block,
)



# ── Fixture réutilisable ──────────────────────────────────────────────────────
@pytest.fixture
def valid_athlete() -> AthleteProfile:
    return AthleteProfile(
        athlete_id=UUID("12345678-1234-5678-1234-567890abcdef"),
        age=22,
        weight_kg=76.0,
        goal_profile=GoalProfile(
            primary_goal="improve_triathlon",
            target_event_type="long_distance",
            target_event_date=date(2026, 7, 12),
        ),
        availability=Availability(
            sessions_per_week_target=10,
            max_training_hours_per_week=12.0,
            available_days=[
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            ],
            long_session_day="saturday",
            double_session_days_allowed=["saturday", "sunday"],
        ),
        discipline_profiles=DisciplineProfiles(
            run=RunDisciplineProfile(
                class_label="advanced",
                experience_years=1.5,
                current_frequency_per_week=4,
                performance_metrics=RunPerformanceMetrics(
                    recent_10k_time_sec=2247,
                    easy_pace_sec_per_km=300,
                    threshold_pace_sec_per_km=228,
                    threshold_heart_rate_bpm=178,
                ),
                level_score=92.9,
                robustness_score=85.0,
            ),
            bike=BikeDisciplineProfile(
                class_label="intermediate_mid",
                experience_years=1.0,
                current_frequency_per_week=1,
                performance_metrics=BikePerformanceMetrics(ftp_watts=255, threshold_heart_rate_bpm=165),
                level_score=80.0,
                robustness_score=80.0
            ),
            swim=SwimDisciplineProfile(
                class_label="intermediate_low",
                experience_years=1.0,
                current_frequency_per_week=1,
                performance_metrics=SwimPerformanceMetrics(
                    continuous_swim_distance_m=3000, css_pace_sec_per_100m=105.0
                ),
                level_score=70.0,
                robustness_score=70.0,
            ),
        ),
        constraints=Constraints(
            injuries=[
                Injury(
                    name="cross-linked ligament (LCA) surgery",
                    status="history",
                    affected_discipline="run",
                )
            ],
            equipment=Equipment(
                has_power_meter=True,
                has_home_trainer=True,
                has_pool_access=True,
                has_pull_buoy=True,
                has_paddles=False,
                has_gym_access=True,
            ),
        ),
        training_state=TrainingState(
            current_fatigue="moderate",
            training_consistency_recent_weeks="high",
            training_consistency_score=0.8,
        ),
    )

@pytest.fixture
def valid_athlete_no_performance_metrics() -> AthleteProfile:
    return AthleteProfile(
        athlete_id=UUID("12345678-1234-5678-1234-567890abcdef"),
        age=22,
        weight_kg=76.0,
        goal_profile=GoalProfile(
            primary_goal="improve_triathlon",
            target_event_type="long_distance",
            target_event_date=date(2026, 7, 12),
        ),
        availability=Availability(
            sessions_per_week_target=10,
            max_training_hours_per_week=12.0,
            available_days=[
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            ],
            long_session_day="saturday",
            double_session_days_allowed=["saturday", "sunday"],
        ),
        discipline_profiles=DisciplineProfiles(
            run=RunDisciplineProfile(
                class_label="advanced",
                experience_years=1.5,
                current_frequency_per_week=4,
                performance_metrics=RunPerformanceMetrics(
                    recent_10k_time_sec=2247,
                    easy_pace_sec_per_km=300,
                    threshold_heart_rate_bpm=178,
                ),
                level_score=92.9,
                robustness_score=85.0,
            ),
            bike=BikeDisciplineProfile(
                class_label="intermediate_mid",
                experience_years=1.0,
                current_frequency_per_week=1,
                performance_metrics=BikePerformanceMetrics(threshold_heart_rate_bpm=165),
                level_score=80.0,
                robustness_score=80.0
            ),
            swim=SwimDisciplineProfile(
                class_label="intermediate_low",
                experience_years=1.0,
                current_frequency_per_week=1,
                performance_metrics=SwimPerformanceMetrics(
                    continuous_swim_distance_m=3000, css_pace_sec_per_100m=105.0
                ),
                level_score=70.0,
                robustness_score=70.0,
            ),
        ),
        constraints=Constraints(
            injuries=[
                Injury(
                    name="cross-linked ligament (LCA) surgery",
                    status="history",
                    affected_discipline="run",
                )
            ],
            equipment=Equipment(
                has_power_meter=True,
                has_home_trainer=True,
                has_pool_access=True,
                has_pull_buoy=True,
                has_paddles=False,
                has_gym_access=True,
            ),
        ),
        training_state=TrainingState(
            current_fatigue="moderate",
            training_consistency_recent_weeks="high",
            training_consistency_score=0.8,
        ),
    )


# ── Tests unitaires pour les fonctions de calcul ────────────────────


def test_pace_from_zone(valid_athlete):
    run_metrics = valid_athlete.discipline_profiles.run.performance_metrics
    assert run_metrics is not None
    threshold_pace = run_metrics.threshold_pace_sec_per_km
    assert threshold_pace is not None

    pace_z2 = pace_from_zone("Z2", threshold_pace)
    expected_z2 = (threshold_pace * 1.14 + threshold_pace * 1.28) / 2
    assert pace_z2 == pytest.approx(expected_z2)


def test_watts_from_zone(valid_athlete):
    bike_metrics = valid_athlete.discipline_profiles.bike.performance_metrics
    assert bike_metrics is not None
    ftp_watts = bike_metrics.ftp_watts
    assert ftp_watts is not None

    watts_z3 = watts_from_zone("Z3", ftp_watts)
    expected_z3 = (ftp_watts * 0.76 + ftp_watts * 0.90) / 2
    assert watts_z3 == pytest.approx(expected_z3)


def test_watts_from_zone1(valid_athlete):
    bike_metrics = valid_athlete.discipline_profiles.bike.performance_metrics
    assert bike_metrics is not None
    ftp_watts = bike_metrics.ftp_watts
    assert ftp_watts is not None

    watts_z1 = watts_from_zone("Z1", ftp_watts)
    expected_z1 = ftp_watts * 0.50  # Z1 watts : < 55% FTP → valeur cible ~50% FTP
    assert watts_z1 == pytest.approx(expected_z1)


def test_heart_rate_from_zone(valid_athlete):
    run_metrics = valid_athlete.discipline_profiles.run.performance_metrics
    assert run_metrics is not None
    threshold_hr = run_metrics.threshold_heart_rate_bpm
    assert threshold_hr is not None

    hr_z4 = heart_rate_from_zone("Z4", threshold_hr)
    expected_z4 = (threshold_hr * 0.95 + threshold_hr * 1.02) / 2
    assert hr_z4 == pytest.approx(expected_z4)


def test_heart_rate_from_zone5(valid_athlete):
    run_metrics = valid_athlete.discipline_profiles.run.performance_metrics
    assert run_metrics is not None
    threshold_hr = run_metrics.threshold_heart_rate_bpm
    assert threshold_hr is not None

    hr_z5 = heart_rate_from_zone("Z5", threshold_hr)
    expected_z5 = threshold_hr * 1.07  # Z5 FC : > 102% → valeur cible ~107%
    assert hr_z5 == pytest.approx(expected_z5)


def test_swim_pace_from_zone(valid_athlete):
    swim_metrics = valid_athlete.discipline_profiles.swim.performance_metrics
    assert swim_metrics is not None
    css_pace = swim_metrics.css_pace_sec_per_100m
    assert css_pace is not None

    pace_z5 = swim_pace_from_zone("Z5", css_pace)
    expected_z5 = (css_pace * 0.94 + css_pace * 0.87) / 2
    assert pace_z5 == pytest.approx(expected_z5)


def test_generate_cardio_block_run(valid_athlete):
    generated_block = generate_cardio_block(
        block=CardioBlock(cardio_zone="Z2", duration_sec=1200, repetitions=1),
        discipline="run",
        athlete=valid_athlete,
    )

    assert generated_block.target_pace_sec_per_km is not None
    expected_pace = round(
        (
            valid_athlete.discipline_profiles.run.performance_metrics.threshold_pace_sec_per_km
            * 1.14
            + valid_athlete.discipline_profiles.run.performance_metrics.threshold_pace_sec_per_km
            * 1.28
        )
        / 2
    )
    assert generated_block.target_pace_sec_per_km == pytest.approx(expected_pace)

    assert generated_block.target_heart_rate_bpm is not None
    expected_hr = round(
        (
            valid_athlete.discipline_profiles.run.performance_metrics.threshold_heart_rate_bpm
            * 0.75
            + valid_athlete.discipline_profiles.run.performance_metrics.threshold_heart_rate_bpm
            * 0.85
        )
        / 2
    )
    assert generated_block.target_heart_rate_bpm == pytest.approx(expected_hr)


def test_generate_cardio_block_bike(valid_athlete):
    # On passe un CardioBlock simple avec recovery_block — pas un GeneratedCardioBlock
    generated_block = generate_cardio_block(
        block=CardioBlock(
            cardio_zone="Z5",
            duration_sec=60,
            repetitions=5,
            recovery_block=CardioBlock(
                cardio_zone="Z1",
                duration_sec=120,
                repetitions=1,
            ),
        ),
        discipline="bike",
        athlete=valid_athlete,
    )

    # Vérification du bloc principal (Z5 bike)
    assert generated_block.target_power_watts is not None
    expected_watts = round(
        valid_athlete.discipline_profiles.bike.performance_metrics.ftp_watts * 1.10
    )
    assert generated_block.target_power_watts == pytest.approx(expected_watts)

    assert generated_block.target_heart_rate_bpm is not None
    expected_hr = round(
        valid_athlete.discipline_profiles.bike.performance_metrics.threshold_heart_rate_bpm * 1.07
    )
    assert generated_block.target_heart_rate_bpm == pytest.approx(expected_hr)

    # Vérification que le recovery_block a été généré récursivement
    assert generated_block.recovery_block is not None
    assert isinstance(generated_block.recovery_block, GeneratedCardioBlock)

    # Vérification des valeurs calculées du recovery_block (Z1 bike)
    expected_recovery_watts = round(
        valid_athlete.discipline_profiles.bike.performance_metrics.ftp_watts * 0.50
    )
    assert generated_block.recovery_block.target_power_watts == pytest.approx(expected_recovery_watts)

    expected_recovery_hr = round(
        valid_athlete.discipline_profiles.bike.performance_metrics.threshold_heart_rate_bpm * 0.70
    )
    assert generated_block.recovery_block.target_heart_rate_bpm == pytest.approx(expected_recovery_hr)

def test_generate_cardio_block_swim(valid_athlete):
    generated_block = generate_cardio_block(
        block=CardioBlock(cardio_zone="Z3", duration_sec=900, repetitions=1),
        discipline="swim",
        athlete=valid_athlete,
    )

    assert generated_block.target_pace_sec_per_100m is not None
    expected_pace = round(
        (
            valid_athlete.discipline_profiles.swim.performance_metrics.css_pace_sec_per_100m
            * 1.05
            + valid_athlete.discipline_profiles.swim.performance_metrics.css_pace_sec_per_100m
            * 1.14
        )
        / 2
    )
    assert generated_block.target_pace_sec_per_100m == pytest.approx(expected_pace)

    # Vérification du fallback sur la FC de course à pied
    assert generated_block.target_heart_rate_bpm is not None
    expected_hr = round(
        (
            valid_athlete.discipline_profiles.run.performance_metrics.threshold_heart_rate_bpm
            * 0.85
            + valid_athlete.discipline_profiles.run.performance_metrics.threshold_heart_rate_bpm
            * 0.95
        )
        / 2
    )
    assert generated_block.target_heart_rate_bpm == pytest.approx(expected_hr)

def test_generate_cardio_block_fallback_no_performance_metrics(valid_athlete_no_performance_metrics):
    generated_block = generate_cardio_block(
        block=CardioBlock(cardio_zone="Z2", duration_sec=1200, repetitions=1),
        discipline="run",
        athlete=valid_athlete_no_performance_metrics,
    )

    # Sans threshold_pace, l'allure doit être None
    assert generated_block.target_pace_sec_per_km is None
    # Mais la FC est calculée depuis threshold_heart_rate_bpm disponible
    assert generated_block.target_heart_rate_bpm is not None
    expected_hr = round(
        (178 * 0.75 + 178 * 0.85) / 2
    )
    assert generated_block.target_heart_rate_bpm == pytest.approx(expected_hr)

