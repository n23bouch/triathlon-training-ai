import pytest
from pydantic import ValidationError
from datetime import date

from triathlon_planner.models.athlete_profile import (
    AthleteProfile,
    GoalProfile,
    Availability,
    DisciplineProfiles,
    Constraints,
    TrainingState,
    SwimDisciplineProfile,
    RunDisciplineProfile,
    BikeDisciplineProfile,
    RunPerformanceMetrics,
    BikePerformanceMetrics,
    SwimPerformanceMetrics,
    Injury,
    Equipment,
)

# ── Fixture réutilisable ──────────────────────────────────────────────────────


@pytest.fixture
def valid_athlete() -> AthleteProfile:
    return AthleteProfile(
        athlete_id="12345678-1234-5678-1234-567890abcdef",
        age=22,
        weight_kg=78.0,
        goal_profile=GoalProfile(
            primary_goal="finish_event",
            target_event_type="middle_distance",
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
            swim=SwimDisciplineProfile(
                class_label="intermediate_low",
                experience_years=1.0,
                current_frequency_per_week=1,
                performance_metrics=SwimPerformanceMetrics(
                    continuous_swim_distance_m=3000
                ),
                level_score=55.0,
                robustness_score=50.0,
            ),
            bike=BikeDisciplineProfile(
                class_label="intermediate_mid",
                experience_years=1.0,
                current_frequency_per_week=0,
                performance_metrics=BikePerformanceMetrics(ftp_watts=250),
                level_score=65.0,
                robustness_score=70.0,
            ),
            run=RunDisciplineProfile(
                class_label="advanced",
                experience_years=2.0,
                current_frequency_per_week=4,
                performance_metrics=RunPerformanceMetrics(
                    recent_10k_time_sec=2240,
                    threshold_pace_sec_per_km=228,
                ),
                level_score=92.9,
                robustness_score=75.0,
            ),
        ),
        constraints=Constraints(
            injuries=[
                Injury(
                    name="LCA surgery",
                    status="sensitive",
                    affected_discipline="run",
                    severity="moderate",
                    notes="Operations done in 2019 and 2021",
                )
            ],
            equipment=Equipment(
                has_power_meter=False,
                has_home_trainer=False,
                has_pool_access=True,
                has_pull_buoy=True,
                has_paddles=False,
                has_gym_access=True,
            ),
        ),
        training_state=TrainingState(
            current_fatigue="moderate",
            training_consistency_recent_weeks="moderate",
            training_consistency_score=0.6,
        ),
    )


# ── Tests : cas valides ───────────────────────────────────────────────────────


def test_create_valid_athlete_profile(valid_athlete):
    assert str(valid_athlete.athlete_id) == "12345678-1234-5678-1234-567890abcdef"
    assert valid_athlete.age == 22
    assert valid_athlete.weight_kg == 78.0
    assert valid_athlete.goal_profile.primary_goal == "finish_event"
    assert valid_athlete.constraints.equipment.has_home_trainer is False


def test_discipline_profiles_scores(valid_athlete):
    assert valid_athlete.discipline_profiles.run.level_score == 92.9
    assert valid_athlete.discipline_profiles.swim.robustness_score == 50.0
    assert valid_athlete.discipline_profiles.bike.level_score == 65.0


def test_injury_details(valid_athlete):
    injury = valid_athlete.constraints.injuries[0]
    assert injury.name == "LCA surgery"
    assert injury.status == "sensitive"
    assert injury.affected_discipline == "run"


def test_optional_performance_metrics_can_be_none():
    profile = RunDisciplineProfile(
        class_label="beginner",
        experience_years=0.5,
        current_frequency_per_week=2,
        performance_metrics=None,
    )
    assert profile.performance_metrics is None


def test_no_injuries_is_valid():
    constraints = Constraints(
        injuries=[],
        equipment=Equipment(
            has_power_meter=False,
            has_home_trainer=False,
            has_pool_access=False,
            has_pull_buoy=False,
            has_paddles=False,
            has_gym_access=False,
        ),
    )
    assert constraints.injuries == []


# ── Tests : cas invalides (ValidationError attendu) ───────────────────────────


def test_invalid_age_too_high():
    with pytest.raises(ValidationError):
        AthleteProfile(
            athlete_id="12345678-1234-5678-1234-567890abcdef",
            age=150,  # > 100 → doit échouer
            weight_kg=70.0,
            goal_profile=GoalProfile(primary_goal="general_fitness"),
            availability=Availability(
                sessions_per_week_target=3,
                max_training_hours_per_week=6.0,
                available_days=["monday", "wednesday", "friday"],
            ),
            discipline_profiles=DisciplineProfiles(
                swim=SwimDisciplineProfile(
                    class_label="beginner",
                    experience_years=0,
                    current_frequency_per_week=0,
                ),
                bike=BikeDisciplineProfile(
                    class_label="beginner",
                    experience_years=0,
                    current_frequency_per_week=0,
                ),
                run=RunDisciplineProfile(
                    class_label="beginner",
                    experience_years=0,
                    current_frequency_per_week=0,
                ),
            ),
            constraints=Constraints(
                equipment=Equipment(
                    has_power_meter=False,
                    has_home_trainer=False,
                    has_pool_access=False,
                    has_pull_buoy=False,
                    has_paddles=False,
                    has_gym_access=False,
                )
            ),
            training_state=TrainingState(
                current_fatigue="low",
                training_consistency_recent_weeks="low",
                training_consistency_score=0.2,
            ),
        )


def test_invalid_sessions_per_week_too_high():
    with pytest.raises(ValidationError):
        Availability(
            sessions_per_week_target=25,  # > 20 → doit échouer
            max_training_hours_per_week=8.0,
            available_days=["monday"],
        )


def test_invalid_training_hours_zero():
    with pytest.raises(ValidationError):
        Availability(
            sessions_per_week_target=5,
            max_training_hours_per_week=0.0,  # doit être > 0
            available_days=["monday"],
        )


def test_invalid_level_score_out_of_range():
    with pytest.raises(ValidationError):
        RunDisciplineProfile(
            class_label="beginner",
            experience_years=1.0,
            current_frequency_per_week=2,
            level_score=150.0,  # > 100 → doit échouer
        )


def test_invalid_primary_goal():
    with pytest.raises(ValidationError):
        GoalProfile(primary_goal="become_ironman")  # pas dans le Literal
