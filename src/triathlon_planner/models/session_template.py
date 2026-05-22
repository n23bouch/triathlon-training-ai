from typing import Literal, Optional
from pydantic import BaseModel, Field, model_validator
from uuid import UUID
from .athlete_profile import Sport

SessionType = Literal[
    "EF",
    "Tempo",
    "Seuil",
    "Sprint",
    "Long",
    "Force",
    "Mobilité",
    "Récupération",
    "Technique",
]
CardioZone = Literal["Z1", "Z2", "Z3", "Z4", "Z5"]
StrengthIntensity = Literal["technique", "light", "moderate", "heavy", "maximal"]
MobilityIntensity = Literal["passive", "active", "dynamic"]
BodyPart = Literal[
    "calf",
    "hamstring",
    "quadriceps",
    "chest",
    "shoulders",
    "back",
    "core",
    "arms",
    "ankles",
    "hips",
]
Laterality = Literal["unilateral", "bilateral"]


class SessionBlock(BaseModel):
    duration_sec: Optional[int] = Field(default=None, gt=0)
    distance_m: Optional[float] = Field(default=None, ge=0.0)
    repetitions: int = Field(default=1, ge=1)

    @model_validator(mode="after")
    def validate_block(self):
        if (self.duration_sec == 0 or self.duration_sec is None) and (
            self.distance_m == 0 or self.distance_m is None
        ):
            raise ValueError(
                "Either duration_sec or distance_m must be greater than zero."
            )
        return self


class CardioBlock(SessionBlock):
    cardio_zone: CardioZone
    departure_interval_sec: Optional[int] = Field(default=None, gt=0)
    recovery_block: Optional["CardioBlock"] = (
        None  # For interval sessions, the recovery block can be defined as another CardioBlock
    )


CardioBlock.model_rebuild()  # Needed to resolve the forward reference for recovery_block


class StrengthBlock(SessionBlock):
    reps_per_set: Optional[int] = Field(default=None, gt=0)
    intensity: StrengthIntensity
    rest_sec: Optional[int] = Field(default=None, gt=0)
    body_part: BodyPart
    laterality: Laterality
    exercise_name: str = Field(default="Generic Strength Exercise", min_length=1)

    @model_validator(mode="after")
    def validate_block(self):
        if (self.reps_per_set is None) and (self.duration_sec is None):
            raise ValueError(
                "For strength blocks, either reps_per_set or duration_sec must be provided."
            )
        return self


class MobilityBlock(SessionBlock):
    hold_sec: Optional[int] = Field(default=None, gt=0)
    intensity: MobilityIntensity
    body_part: BodyPart
    laterality: Laterality
    exercise_name: str = Field(default="Generic Mobility Exercise", min_length=1)

    @model_validator(mode="after")
    def validate_block(self):
        if (self.hold_sec is None) and (self.duration_sec is None):
            raise ValueError(
                "For mobility blocks, either hold_sec or duration_sec must be provided."
            )
        return self


class LevelRange(BaseModel):
    level_min: float = Field(ge=0.0, le=100.0)
    level_max: float = Field(ge=0.0, le=100.0)
    work_volume_sec_min: int = Field(gt=0)
    work_volume_sec_max: int = Field(gt=0)
    block_duration_sec_min: int = Field(gt=0)
    block_duration_sec_max: int = Field(gt=0)

    @model_validator(mode="after")
    def validate_level_range(self):
        if self.level_min > self.level_max:
            raise ValueError("level_min must be ≤ level_max.")
        return self
    
    @model_validator(mode="after")
    def validate_work_volume(self):
        if self.work_volume_sec_min > self.work_volume_sec_max:
            raise ValueError("work_volume_sec_min must be ≤ work_volume_sec_max.")
        return self

    @model_validator(mode="after")
    def validate_block_duration(self):
        if self.block_duration_sec_min > self.block_duration_sec_max:
            raise ValueError("block_duration_sec_min must be ≤ block_duration_sec_max.")
        return self

class StrengthLevelRange(BaseModel):
    level_min: float = Field(ge=0.0, le=100.0)
    level_max: float = Field(ge=0.0, le=100.0)
    sets_min: int = Field(gt=0)
    sets_max: int = Field(gt=0)
    reps_min: int = Field(gt=0)
    reps_max: int = Field(gt=0)

    @model_validator(mode="after")
    def validate_level_range(self):
        if self.level_min > self.level_max:
            raise ValueError("level_min must be ≤ level_max.")
        return self
    
    @model_validator(mode="after")
    def validate_sets(self):
        if self.sets_min > self.sets_max:
            raise ValueError("sets_min must be ≤ sets_max.")
        return self

    @model_validator(mode="after")
    def validate_reps(self):
        if self.reps_min > self.reps_max:
            raise ValueError("reps_min must be ≤ reps_max.")
        return self

class CardioTemplateParams(BaseModel):
    warmup_duration_sec: int = Field(gt=0)
    warmup_zone: CardioZone
    work_zone: CardioZone
    rest_zone: CardioZone
    rest_ratio: float = Field(gt=0.0)
    cooldown_duration_sec: int = Field(gt=0)
    cooldown_zone: CardioZone
    level_ranges: list[LevelRange]
    requires_pool: bool = False
    requires_power_meter: bool = False

    
class StrengthTemplateParams(BaseModel):
    movement_pattern: Literal["squatting", "hinging", "pushing", "pulling", "core"]
    load_intensity: Literal["endurance", "moderate", "heavy"]
    level_ranges: list[StrengthLevelRange]
    rest_sec: int = Field(gt=0)
    unilateral: bool
    requires_gym: bool


class MobilityTemplateParams(BaseModel):
    target_zone: Literal[
        "hip_flexor", "ankle", "thoracic", "shoulder", "hamstring", "hip_rotation"
    ]
    mobility_type: Literal["dynamic", "active", "passive"]
    hold_sec: int = Field(gt=0)
    reps: Optional[int] = None
    bilateral: bool
    requires_equipment: Literal["none", "foam_roller", "band"]


class SessionTemplate(BaseModel):
    template_id: UUID
    discipline: Sport
    session_type: SessionType
    name: str
    target_level_score_min: float = Field(ge=0.0, le=100.0)
    target_level_score_max: float = Field(ge=0.0, le=100.0)
    intensity_category: Literal["low", "medium", "high"]
    params: CardioTemplateParams | StrengthTemplateParams | MobilityTemplateParams

    @model_validator(mode="after")
    def validate_level_score_range(self):
        if self.target_level_score_min > self.target_level_score_max:
            raise ValueError("target_level_score_min must be ≤ target_level_score_max.")
        return self
    
    @model_validator(mode="after")
    def validate_coherence_between_discipline_and_params(self):
        cardio_sports = ["swim", "bike", "run"]
        if self.discipline in cardio_sports and not isinstance(self.params, CardioTemplateParams):
            raise ValueError("For cardio discipline, params must be of type CardioTemplateParams.")
        if self.discipline == "strength" and not isinstance(self.params, StrengthTemplateParams):
            raise ValueError("For strength discipline, params must be of type StrengthTemplateParams.")
        if self.discipline == "mobility" and not isinstance(self.params, MobilityTemplateParams):
            raise ValueError("For mobility discipline, params must be of type MobilityTemplateParams.")
        return self
    
