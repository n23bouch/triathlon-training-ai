import pytest
from pydantic import ValidationError

from triathlon_planner.generation.classifier import (
    compute_weakest_discipline,
    compute_overall_level,
    compute_fatigue_factor,
    compute_load_factor,
    AthleteContext
)
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


# ── Fixture réutilisable ──────────────────────────────────────────────────────
@pytest.fixture
def valid_athlete() -> AthleteProfile:
    return AthleteProfile(
        athlete_id="12345678-1234-5678-1234-567890abcdef",
        age=22,
        weight_kg=76.0,
        goal_profile=GoalProfile(
            primary_goal="improve_triathlon",
            target_event_type="long_distance",
            target_event_date="2026-07-12",
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
                performance_metrics=BikePerformanceMetrics(ftp_watts=255),
                level_score=80.0,
                robustness_score=80.0,
            ),
            swim=SwimDisciplineProfile(
                class_label="intermediate_low",
                experience_years=1.0,
                current_frequency_per_week=1,
                performance_metrics=SwimPerformanceMetrics(
                    continuous_swim_distance_m=3000
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


# ── Tests unitaires pour les fonctions de classification ────────────────────
def test_compute_weakest_discipline(valid_athlete):
    weakest = compute_weakest_discipline(valid_athlete)
    assert weakest == "swim"

def test_compute_fatigue_factor(valid_athlete):
    fatigue_factor = compute_fatigue_factor(valid_athlete)
    expected_fatigue = 0.3  # "moderate" fatigue
    assert fatigue_factor == expected_fatigue

def test_compute_load_factor(valid_athlete):
    fatigue_factor = compute_fatigue_factor(valid_athlete)
    load_factor = compute_load_factor(fatigue_factor)
    expected_load = 1.0 - (0.3 * 0.5)  # 1.0 - (fatigue_level * 0.5)
    assert load_factor == expected_load

def test_available_sessions_per_week(valid_athlete):
    available_sessions = valid_athlete.availability.sessions_per_week_target
    assert available_sessions == 10

def test_compute_overall_level(valid_athlete):
    overall_level = compute_overall_level(valid_athlete)
    expected_overall = (70.0 * 1.5 + 92.9 + 80.0) / 3.5
    assert overall_level == pytest.approx(expected_overall)

