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
    "calf", "hamstring", "quadriceps", "chest", "shoulders", "back", "core", "arms"
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


class StrengthBlock(SessionBlock):
    reps_per_set: Optional[int] = Field(default=None, gt=0)
    intensity: StrengthIntensity
    rest_sec: Optional[int] = Field(default=None, gt=0)
    body_part: BodyPart
    laterality: Laterality


class MobilityBlock(SessionBlock):
    hold_sec: Optional[int] = Field(default=None, gt=0)
    intensity: MobilityIntensity
    body_part: BodyPart
    laterality: Laterality


class SessionTemplate(BaseModel):
    template_id: UUID
    discipline: Sport
    session_type: SessionType
    blocks: list[CardioBlock | StrengthBlock | MobilityBlock | SessionBlock]
    target_level_score_min: float = Field(ge=0.0, le=100.0)
    target_level_score_max: float = Field(ge=0.0, le=100.0)

    @model_validator(mode="after")
    def validate_level_score_range(self):
        if self.target_level_score_min > self.target_level_score_max:
            raise ValueError(
                "target_level_score_min must be less than or equal to target_level_score_max."
            )
        return self
