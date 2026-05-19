import pytest

from pydantic import ValidationError
from uuid import uuid4
from datetime import date

from triathlon_planner.models.generated_session import (
    GeneratedSession,
    GeneratedCardioBlock,
    GeneratedStrengthBlock,
    GeneratedMobilityBlock,
)


# ── Fixture réutilisable ──────────────────────────────────────────────────────
@pytest.fixture
def valid_generated_session():
    return GeneratedSession(
        session_id=uuid4(),
        athlete_id=uuid4(),
        template_id=uuid4(),
        discipline="run",
        session_type="Seuil",
        schedule_date=date(2026, 7, 1),
        blocks=[
            GeneratedCardioBlock(
                duration_sec=1500,
                cardio_zone="Z2",
                repetitions=1,
                target_pace_sec_per_km=320.0,
                target_heart_rate_bpm=144,
            ),
            GeneratedCardioBlock(
                distance_m=2500,
                cardio_zone="Z4",
                repetitions=2,
                target_pace_sec_per_km=230.0,
                target_heart_rate_bpm=170,
                recovery_block=GeneratedCardioBlock(
                    distance_m=500,
                    cardio_zone="Z2",
                    repetitions=1,
                    target_pace_sec_per_km=320.0,
                    target_heart_rate_bpm=155,
                ),
            ),
            GeneratedCardioBlock(
                duration_sec=600,
                cardio_zone="Z2",
                repetitions=1,
                target_pace_sec_per_km=320.0,
                target_heart_rate_bpm=150,
            ),
        ],
    )


@pytest.fixture
def valid_generated_strength_session():
    return GeneratedSession(
        session_id=uuid4(),
        athlete_id=uuid4(),
        template_id=uuid4(),
        discipline="strength",
        session_type="Force",
        schedule_date=date(2026, 7, 2),
        blocks=[
            GeneratedStrengthBlock(
                intensity="moderate",
                body_part="chest",
                laterality="bilateral",
                reps_per_set=10,
                rest_sec=60,
                target_weight_kg=50.0,
                rpe_target=7.0,
            ),
            GeneratedStrengthBlock(
                intensity="heavy",
                body_part="quadriceps",
                laterality="unilateral",
                reps_per_set=5,
                rest_sec=120,
                target_weight_kg=80.0,
                rpe_target=9.0,
            ),
        ],
    )


@pytest.fixture
def valid_generated_mobility_session():
    return GeneratedSession(
        session_id=uuid4(),
        athlete_id=uuid4(),
        template_id=uuid4(),
        discipline="mobility",
        session_type="Mobilité",
        schedule_date=date(2026, 7, 3),
        blocks=[
            GeneratedMobilityBlock(
                intensity="dynamic",
                body_part="shoulders",
                laterality="bilateral",
                hold_sec=30,
            ),
            GeneratedMobilityBlock(
                intensity="passive",
                body_part="hips",
                laterality="unilateral",
                hold_sec=45,
            ),
            GeneratedMobilityBlock(
                intensity="active",
                body_part="ankles",
                laterality="bilateral",
                hold_sec=20,
            ),
        ],
    )


# ── Tests : cas valides ───────────────────────────────────────────────────────
def test_valid_generated_session(valid_generated_session):
    assert valid_generated_session.discipline == "run"
    assert valid_generated_session.blocks[1].cardio_zone == "Z4"
    assert len(valid_generated_session.blocks) == 3
    assert valid_generated_session.schedule_date == date(2026, 7, 1)


def test_valid_generated_strength_session(valid_generated_strength_session):
    assert valid_generated_strength_session.discipline == "strength"
    assert valid_generated_strength_session.blocks[0].intensity == "moderate"
    assert valid_generated_strength_session.blocks[1].body_part == "quadriceps"
    assert len(valid_generated_strength_session.blocks) == 2
    assert valid_generated_strength_session.schedule_date == date(2026, 7, 2)


def test_valid_generated_mobility_session(valid_generated_mobility_session):
    assert valid_generated_mobility_session.discipline == "mobility"
    assert valid_generated_mobility_session.blocks[0].intensity == "dynamic"
    assert valid_generated_mobility_session.blocks[1].body_part == "hips"
    assert len(valid_generated_mobility_session.blocks) == 3
    assert valid_generated_mobility_session.schedule_date == date(2026, 7, 3)


# ── Tests : cas invalides ─────────────────────────────────────────────────────
def test_invalid_generated_session_block_no_duration_no_distance():
    with pytest.raises(ValidationError):
        GeneratedCardioBlock(
            cardio_zone="Z4",
            repetitions=2,
            target_pace_sec_per_km=230.0,
            target_heart_rate_bpm=170,
        )


def test_invalid_generated_strength_block_no_reps_no_duration():
    with pytest.raises(ValidationError):
        GeneratedStrengthBlock(
            intensity="heavy",
            body_part="quadriceps",
            laterality="unilateral",
            rest_sec=120,
            target_weight_kg=80.0,
            rpe_target=9.0,
        )


def test_invalid_generated_session_block_invalid_cardio_zone():
    with pytest.raises(ValidationError):
        GeneratedCardioBlock(
            duration_sec=600,
            cardio_zone="Z6",  # Invalid cardio zone
            repetitions=1,
            target_pace_sec_per_km=320.0,
            target_heart_rate_bpm=150,
        )


def test_invalid_generated_strength_block_invalid_intensity():
    with pytest.raises(ValidationError):
        GeneratedStrengthBlock(
            intensity="extreme",  # Invalid intensity
            body_part="quadriceps",
            laterality="unilateral",
            reps_per_set=5,
            rest_sec=120,
            target_weight_kg=80.0,
            rpe_target=9.0,
        )


def test_invalid_generated_mobility_block_invalid_intensity():
    with pytest.raises(ValidationError):
        GeneratedMobilityBlock(
            intensity="super_dynamic",  # Invalid intensity
            body_part="shoulders",
            laterality="bilateral",
            hold_sec=30,
        )
