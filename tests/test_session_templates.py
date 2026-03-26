import pytest

from pydantic import ValidationError
from uuid import uuid4 
from typing import get_args

from triathlon_planner.models.session_template import SessionTemplate, SessionBlock, CardioBlock, StrengthBlock,MobilityBlock, TrainingZone, BodyPart, Laterality, CardioZone, StrengthIntensity, MobilityIntensity

# ── Fixture réutilisable ──────────────────────────────────────────────────────
@pytest.fixture
def valid_cardio_session_template():
    return SessionTemplate(
        template_id=uuid4(),
        discipline="run",
        blocks=[
            CardioBlock(duration_sec=1200, cardio_zone="Z2", repetitions=1),
            CardioBlock(distance_m=1000, cardio_zone="Z4", repetitions=3),
            CardioBlock(duration_sec=900, cardio_zone="Z2", repetitions=1),
        ],
        target_level_score_min=50.0,
        target_level_score_max=70.0
    )

def valid_streght_session_template(): 
    return SessionTemplate(
        template_id=uuid4(),
        discipline="strenght"
        blocks= [
            MobilityBlock()
        ],
        
    )

# ── Tests : cas valides ───────────────────────────────────────────────────────
def test_valid_session_template(valid_cardio_session_template):
    assert valid_cardio_session_template.discipline == "run"
    assert valid_cardio_session_template.blocks[1] == "Z4"
    assert len(valid_cardio_session_template.blocks) == 3
    assert valid_cardio_session_template.target_level_score_min == 50.0
    assert valid_cardio_session_template.target_level_score_max == 70.0

def test_valide_session_block(valid_cardio_session_template):
    for block in valid_cardio_session_template.blocks:
        assert block.cardio_zone in get_args(CardioZone)
        assert block.repetitions >= 1
        assert (block.duration_sec is not None and block.duration_sec > 0) or (block.distance_m is not None and block.distance_m > 0)
    
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
            blocks=[SessionBlock(duration_sec=900, zone="Recovery", repetitions=1)],
            target_level_score_min=30.0,
            target_level_score_max=50.0
        )
