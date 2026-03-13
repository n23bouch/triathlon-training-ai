import pydantic
import datetime

from typing import Literal, Optional
from pydantic import BaseModel, Field
from datetime import date

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
TrainingConsistencyLevel = Literal["low", "moderate", "high"]


class GoalProfile(BaseModel):
    primary_goal: PrimaryGoal
    priority_discipline: Optional[Sport] = None
    target_event_type: Optional[TargetEventType] = None
    target_event_date: Optional[date] = None


class Availability(BaseModel):
    sessions_per_week_target: int = Field(ge=1, le=20)
    max_training_hours_per_week: float = Field(gt=0.0, le=40.0)
    available_days: list[DayOfWeek]
    long_session_day: Optional[DayOfWeek] = None
    double_session_days_allowed: Optional[list[DayOfWeek]] = None


class Injury(BaseModel):
    area: str
    status: InjuryStatus
    notes: Optional[str] = None


class Equipment(BaseModel):
    has_power_meter: bool
    has_home_trainer: bool
    has_pool_access: bool
    has_pull_buoy: bool
    has_paddles: bool
    has_gym_access: bool


class TrainingState(BaseModel):
    current_fatigue: FatigueState
    training_consistency_recent_weeks: TrainingConsistencyLevel
    training_consistency_score: float = Field(ge=0.0, le=1.0)


class RunPerformanceMetrics(BaseModel):
    recent_5k_time_sec: Optional[int] = Field(default=None, gt=0)  # in seconds
    recent_10k_time_sec: Optional[int] = Field(default=None, gt=0)  # in seconds
    easy_pace_sec_per_km: Optional[float] = Field(
        default=None, gt=0.0
    )  # in seconds per km
    threshold_pace_sec_per_km: Optional[float] = Field(
        default=None, gt=0.0
    )  # in seconds per km
    threshold_heart_rate_bpm: Optional[int] = Field(default=None, gt=0)  # in bpm


class BikePerformanceMetrics(BaseModel):
    recent_20k_time_sec: Optional[int] = Field(default=None, gt=0)  # in seconds
    recent_40k_time_sec: Optional[int] = Field(default=None, gt=0)  # in seconds
    ftp_watts: Optional[int] = Field(default=None, gt=0)  # Functional Threshold Power
    threshold_heart_rate_bpm: Optional[int] = Field(default=None, gt=0)  # in bpm


class SwimPerformanceMetrics(BaseModel):
    css_pace_sec_per_100m: Optional[float] = Field(default=None, gt=0.0)
    recent_400m_time_sec: Optional[int] = Field(default=None, gt=0)  # in seconds
    continuous_swim_distance_m: Optional[int] = Field(default=None, gt=0)  # in meters


class RunDisciplineProfile(BaseModel):
    class_label: AthleteClass
    experience_years: float = Field(ge=0.0)
    current_frequency_per_week: int = Field(ge=0, le=14)
    performance_metrics: Optional[RunPerformanceMetrics] = None
    level_score: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    robustness_score: Optional[float] = Field(default=None, ge=0.0, le=100.0)


class BikeDisciplineProfile(BaseModel):
    class_label: AthleteClass
    experience_years: float = Field(ge=0.0)
    current_frequency_per_week: int = Field(ge=0, le=14)
    performance_metrics: Optional[BikePerformanceMetrics] = None
    level_score: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    robustness_score: Optional[float] = Field(default=None, ge=0.0, le=100.0)


class SwimDisciplineProfile(BaseModel):
    class_label: AthleteClass
    experience_years: float = Field(ge=0.0)
    current_frequency_per_week: int = Field(ge=0, le=14)
    performance_metrics: Optional[SwimPerformanceMetrics] = None
    level_score: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    robustness_score: Optional[float] = Field(default=None, ge=0.0, le=100.0)


class Constraints(BaseModel):
    injuries: list[Injury] = Field(default_factory=list)
    equipment: Equipment


class DisciplineProfiles(BaseModel):
    run: RunDisciplineProfile
    bike: BikeDisciplineProfile
    swim: SwimDisciplineProfile


class AthleteProfile(BaseModel):
    athlete_id: str
    age: int = Field(gt=0, le=100)
    weight_kg: float = Field(gt=0.0, le=300.0)
    goal_profile: GoalProfile
    availability: Availability
    discipline_profiles: DisciplineProfiles
    constraints: Constraints
    training_state: TrainingState
