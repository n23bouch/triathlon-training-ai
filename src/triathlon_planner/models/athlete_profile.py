from typing import Literal

import pydantic
import datetime
from pydantic import BaseModel
from datetime import date
from typing import Optional, Literal

Sport = Literal["swim", "bike", "run", "strength", "mobility"]
PrimaryGoal = Literal[
    "finish_event",
    "improve_triathlon",
    "improve_discipline",
    "return_from_injury",
    "general_fitness",
]
DayOfWeek = Literal[
    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"
]
AthleteClass = Literal[
    "beginner", "intermediate_low", "intermediate_mid", "intermediate_high", "advanced"
]
InjuryStatus = Literal["active", "recovering", "sensitive", "history"]
TargetEventType = Literal["sprint", "olympic", "middle_distance", "long_distance"]
FatigueState = Literal["low", "moderate", "high", "very_high"]


class GoalProfile(BaseModel):
    primary_goal: PrimaryGoal
    priority_discipline: Optional[Sport] = None
    target_event_type: Optional[TargetEventType] = None
    target_event_date: Optional[date] = None
