from typing import Optional
from datetime import date
from pydantic import BaseModel, Field
from uuid import UUID
from .athlete_profile import Sport
from .session_template import CardioBlock, StrengthBlock, MobilityBlock, SessionType


class GeneratedCardioBlock(CardioBlock):
    target_pace_sec_per_km: Optional[float] = Field(default=None, gt=0.0)
    target_heart_rate_bpm: Optional[int] = Field(default=None, gt=0)
    target_power_watts: Optional[int] = Field(default=None, gt=0)
    target_pace_sec_per_100m: Optional[float] = Field(default=None, gt=0.0)


class GeneratedStrengthBlock(StrengthBlock):
    target_weight_kg: Optional[float] = Field(default=None, gt=0.0)
    rpe_target: Optional[float] = Field(default=None, ge=0.0, le=10.0)


class GeneratedMobilityBlock(MobilityBlock):
    pass


class GeneratedSession(BaseModel):
    session_id: UUID
    athlete_id: UUID
    template_id: UUID
    discipline: Sport
    session_type: SessionType
    schedule_date: date
    blocks: list[GeneratedCardioBlock | GeneratedStrengthBlock | GeneratedMobilityBlock]
