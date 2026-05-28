import pytest

from pydantic import ValidationError
from uuid import uuid4

from triathlon_planner.models.session_template import (
    SessionTemplate,
    CardioBlock,
    StrengthBlock,
    MobilityBlock,
    CardioTemplateParams,
    StrengthTemplateParams,
    MobilityTemplateParams,
    LevelRange,
    StrengthLevelRange,
)


# ── Fixture réutilisable ──────────────────────────────────────────────────────
@pytest.fixture
def valid_cardio_session_template():
    return SessionTemplate(
        template_id=uuid4(),
        discipline="run",
        session_type="Seuil",
        name="Seuil Run 60min",
        target_level_score_min=50.0,
        target_level_score_max=70.0,
        intensity_category="high",
        params=CardioTemplateParams(
            warmup_duration_sec=1200,
            warmup_zone="Z1",
            work_zone="Z4",
            rest_zone="Z2",
            rest_ratio=0.3,
            cooldown_duration_sec=600,
            cooldown_zone="Z1",
            level_ranges=[
                LevelRange(
                    level_min=70.0,
                    level_max=100.0,
                    work_volume_sec_min=1800,
                    work_volume_sec_max=3600,
                    block_duration_sec_min=360,
                    block_duration_sec_max=600,
                )
            ],
            requires_pool=False,
            requires_power_meter=False,
        ),
    )


@pytest.fixture
def valid_strength_session_template():
    return SessionTemplate(
        template_id=uuid4(),
        discipline="strength",
        session_type="Force",
        name="Force Chest",
        target_level_score_min=40.0,
        target_level_score_max=60.0,
        intensity_category="medium",
        params=StrengthTemplateParams(
            movement_pattern="pushing",
            load_intensity="heavy",
            level_ranges=[
                StrengthLevelRange(
                    level_min=40.0,
                    level_max=60.0,
                    sets_min=3,
                    sets_max=5,
                    reps_min=8,  # explicite car optionnel maintenant
                    reps_max=12,
                )
            ],
            rest_sec=90,
            unilateral=False,
            requires_gym=True,
        ),
    )


@pytest.fixture
def valid_mobility_session_template():
    return SessionTemplate(
        template_id=uuid4(),
        discipline="mobility",
        session_type="Mobilité",
        name="Mobilité Hanches et Épaules",
        target_level_score_min=30.0,
        target_level_score_max=50.0,
        intensity_category="low",
        params=MobilityTemplateParams(
            target_zone="hip_flexor",
            mobility_type="dynamic",
            hold_sec=30,
            reps=3,
            bilateral=True,
            requires_equipment="foam_roller",
        ),
    )


# ── Tests : cas valides ───────────────────────────────────────────────────────
def test_valid_session_template(valid_cardio_session_template):
    assert valid_cardio_session_template.discipline == "run"
    assert valid_cardio_session_template.session_type == "Seuil"
    assert valid_cardio_session_template.name == "Seuil Run 60min"
    assert valid_cardio_session_template.intensity_category == "high"
    assert valid_cardio_session_template.target_level_score_min == 50.0
    assert valid_cardio_session_template.target_level_score_max == 70.0


def test_valid_cardio_template_params(valid_cardio_session_template):
    params = valid_cardio_session_template.params
    assert params.work_zone == "Z4"
    assert params.warmup_zone == "Z1"
    assert params.rest_ratio == 0.3
    assert len(params.level_ranges) == 1
    assert params.level_ranges[0].level_min == 70.0


def test_valid_strength_template_params(valid_strength_session_template):
    params = valid_strength_session_template.params
    assert params.movement_pattern == "pushing"
    assert params.load_intensity == "heavy"
    assert params.level_ranges[0].sets_min == 3
    assert params.level_ranges[0].reps_max is not None
    assert params.level_ranges[0].reps_max == 12


def test_valid_mobility_template_params(valid_mobility_session_template):
    params = valid_mobility_session_template.params
    assert params.target_zone == "hip_flexor"
    assert params.mobility_type == "dynamic"
    assert params.hold_sec == 30
    assert params.bilateral is True


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
            name="Tempo Bike 45min",
            params=CardioTemplateParams(
                warmup_duration_sec=900,
                warmup_zone="Z1",
                work_zone="Z3",
                rest_zone="Z2",
                rest_ratio=0.2,
                cooldown_duration_sec=300,
                cooldown_zone="Z1",
                level_ranges=[
                    LevelRange(
                        level_min=70.0,
                        level_max=100.0,
                        work_volume_sec_min=1200,
                        work_volume_sec_max=2400,
                        block_duration_sec_min=300,
                        block_duration_sec_max=600,
                    )
                ],
            ),
            target_level_score_min=80.0,
            target_level_score_max=60.0,
            intensity_category="medium",
        )


def test_invalid_session_template_invalid_discipline():
    with pytest.raises(ValidationError):
        SessionTemplate(
            template_id=uuid4(),
            discipline="yoga",  # Invalid discipline
            session_type="Mobilité",
            name="Yoga Session",
            params=MobilityTemplateParams(
                target_zone="shoulder",
                mobility_type="passive",
                hold_sec=60,
                reps=2,
                bilateral=True,
                requires_equipment="none",
            ),
            target_level_score_min=30.0,
            target_level_score_max=50.0,
            intensity_category="low",
        )


def test_invalid_strength_block_no_reps_no_duration():
    with pytest.raises(ValidationError):
        StrengthBlock(
            intensity="moderate",
            body_part="quadriceps",
            laterality="bilateral",
            rest_sec=60,
        )


def test_invalid_mobility_block_no_hold_no_duration():
    with pytest.raises(ValidationError):
        MobilityBlock(intensity="passive", body_part="back", laterality="unilateral")


def test_invalid_level_range_min_greater_than_max():
    with pytest.raises(ValidationError):
        LevelRange(
            level_min=80.0,
            level_max=50.0,  # level_min > level_max
            work_volume_sec_min=900,
            work_volume_sec_max=1800,
            block_duration_sec_min=300,
            block_duration_sec_max=600,
        )


def test_invalid_level_range_volume_min_greater_than_max():
    with pytest.raises(ValidationError):
        LevelRange(
            level_min=50.0,
            level_max=80.0,
            work_volume_sec_min=1800,
            work_volume_sec_max=900,  # min > max
            block_duration_sec_min=300,
            block_duration_sec_max=600,
        )


def test_invalid_strength_level_range_sets():
    with pytest.raises(ValidationError):
        StrengthLevelRange(
            level_min=40.0,
            level_max=60.0,
            sets_min=5,
            sets_max=3,  # sets_min > sets_max
            reps_min=8,
            reps_max=12,
        )


def test_invalid_discipline_params_mismatch():
    with pytest.raises(ValidationError):
        SessionTemplate(
            template_id=uuid4(),
            discipline="run",  # cardio
            session_type="Seuil",
            name="Test",
            target_level_score_min=50.0,
            target_level_score_max=70.0,
            intensity_category="high",
            params=StrengthTemplateParams(  # ❌ mauvais type
                movement_pattern="squatting",
                load_intensity="moderate",
                level_ranges=[
                    StrengthLevelRange(
                        level_min=50.0,
                        level_max=70.0,
                        sets_min=3,
                        sets_max=4,
                        reps_min=10,
                        reps_max=12,
                    )
                ],
                rest_sec=60,
                unilateral=False,
                requires_gym=False,
            ),
        )


def test_invalid_strength_level_range_hold_duration():
    with pytest.raises(ValidationError):
        StrengthLevelRange(
            level_min=0,
            level_max=50,
            sets_min=2,
            sets_max=4,
            reps_min=1,
            reps_max=1,
            hold_duration_sec_min=60,
            hold_duration_sec_max=30,  # min > max ❌
        )


def test_invalid_strength_level_range_no_reps_no_hold():
    with pytest.raises(ValidationError):
        StrengthLevelRange(
            level_min=0,
            level_max=50,
            sets_min=2,
            sets_max=3,
            # ni reps ni hold → doit échouer
        )


def test_invalid_strength_level_range_both_reps_and_hold():
    with pytest.raises(ValidationError):
        StrengthLevelRange(
            level_min=0,
            level_max=50,
            sets_min=2,
            sets_max=3,
            reps_min=10,
            reps_max=15,
            hold_duration_sec_min=30,
            hold_duration_sec_max=60,
            # les deux à la fois → doit échouer
        )
