import pytest

from pydantic import ValidationError
from uuid import uuid4 
from typing import get_args

from triathlon_planner.models.session_template import SessionTemplate, SessionBlock, CardioBlock, StrengthBlock,MobilityBlock, BodyPart, Laterality, CardioZone, StrengthIntensity, MobilityIntensity

# ── Fixture réutilisable ──────────────────────────────────────────────────────
@pytest.fixture
def valid_cardio_session_template():
    return SessionTemplate(
        template_id=uuid4(),
        discipline="run",
        session_type="Seuil",
        blocks=[
            CardioBlock(duration_sec=1200, cardio_zone="Z2", repetitions=1),
            CardioBlock(distance_m=1000, cardio_zone="Z4", repetitions=3),
            CardioBlock(duration_sec=900, cardio_zone="Z2", repetitions=1),
        ],
        target_level_score_min=50.0,
        target_level_score_max=70.0
    )

@pytest.fixture
def valid_strength_session_template(): 
    return SessionTemplate(
        template_id=uuid4(),
        discipline="strength",
        session_type="Force",
        blocks=[
            StrengthBlock(intensity="moderate", body_part="chest", laterality="bilateral", reps_per_set=10, rest_sec=60),
            StrengthBlock(intensity="moderate", body_part="chest", laterality="unilateral", reps_per_set=5, rest_sec=90),
            StrengthBlock(intensity="heavy", body_part="chest", laterality="bilateral", reps_per_set=8, rest_sec=120),
        ],
        target_level_score_min=40.0,
        target_level_score_max=60.0      
    )

@pytest.fixture
def valid_mobility_session_template():
    return SessionTemplate(
        template_id=uuid4(),
        discipline="mobility",
        session_type="Mobilité",
        blocks=[
            MobilityBlock(intensity="dynamic", body_part="shoulders", laterality="bilateral", hold_sec=30),
            MobilityBlock(intensity="passive", body_part="hips", laterality="unilateral", hold_sec=45),
            MobilityBlock(intensity="active", body_part="ankles", laterality="bilateral", hold_sec=20),
        ],      
        target_level_score_min=30.0,
        target_level_score_max=50.0
    )
    
# ── Tests : cas valides ───────────────────────────────────────────────────────
def test_valid_session_template(valid_cardio_session_template):
    assert valid_cardio_session_template.discipline == "run"
    assert valid_cardio_session_template.blocks[1].cardio_zone == "Z4"
    assert len(valid_cardio_session_template.blocks) == 3
    assert valid_cardio_session_template.target_level_score_min == 50.0
    assert valid_cardio_session_template.target_level_score_max == 70.0

def test_valid_cardio_block(valid_cardio_session_template):
    for block in valid_cardio_session_template.blocks:
        assert block.cardio_zone in get_args(CardioZone)
        assert block.repetitions >= 1
        assert (block.duration_sec is not None and block.duration_sec > 0) or (block.distance_m is not None and block.distance_m > 0)

def test_valid_strength_block(valid_strength_session_template):
    for block in valid_strength_session_template.blocks:
        assert block.intensity in get_args(StrengthIntensity)
        assert block.body_part in get_args(BodyPart)
        assert block.laterality in get_args(Laterality)
        assert block.reps_per_set is not None and block.reps_per_set > 0
        assert block.rest_sec is not None and block.rest_sec > 0

def test_valid_mobility_block(valid_mobility_session_template):
    for block in valid_mobility_session_template.blocks:
        assert block.intensity in get_args(MobilityIntensity)
        assert block.body_part in get_args(BodyPart)
        assert block.laterality in get_args(Laterality)
        assert block.hold_sec is not None and block.hold_sec > 0
    
# ── Tests : cas invalides (ValidationError attendu) ───────────────────────────
def test_invalid_session_block_no_duration_no_distance():
    with pytest.raises(ValidationError):
        CardioBlock(cardio_zone="Z4", repetitions=2)

def test_invalid_session_template_invalid_level_score_range():
    with pytest.raises(ValidationError):
        SessionTemplate(
            template_id=uuid4(),
            discipline="bike",
            session_type="Tempo",
            blocks=[CardioBlock(duration_sec=1800, cardio_zone="Tempo", repetitions=1)],
            target_level_score_min=80.0,
            target_level_score_max=60.0
        )

def test_invalid_session_template_invalid_discipline():
    with pytest.raises(ValidationError):
        SessionTemplate(
            template_id=uuid4(),
            discipline="yoga",  # Invalid discipline
            session_type="Mobilité",
            blocks=[SessionBlock(duration_sec=900, repetitions=1)],
            target_level_score_min=30.0,
            target_level_score_max=50.0
        )

def test_invalid_strength_block_no_reps_no_duration():
    with pytest.raises(ValidationError):
        StrengthBlock(intensity="moderate", body_part="quadriceps", laterality="bilateral", rest_sec=60)

def test_invalid_mobility_block_no_hold_no_duration():
    with pytest.raises(ValidationError):
        MobilityBlock(intensity="passive", body_part="back", laterality="unilateral")