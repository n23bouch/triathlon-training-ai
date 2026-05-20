from pydantic import BaseModel, Field
from ..models.athlete_profile import AthleteProfile, Sport, PrimaryGoal

# 1. Le modèle output du classifier
class AthleteContext(BaseModel):
    overall_level: float = Field(ge=0.0, le=100.0)
    weakest_discipline: Sport
    fatigue_level: float = Field(ge=0.0, le=1.0)
    load_factor: float = Field(ge=0.5, le=1.0)
    available_sessions_per_week: int
    primary_goal: PrimaryGoal
    

# 2. Les fonctions de calcul
def compute_weakest_discipline(athlete: AthleteProfile) -> Sport:
    run_score = athlete.discipline_profiles.run.level_score or 0.0
    bike_score = athlete.discipline_profiles.bike.level_score or 0.0
    swim_score = athlete.discipline_profiles.swim.level_score or 0.0
    scores = {"run": run_score, "bike": bike_score, "swim": swim_score}
    weakest = min(scores, key=scores.get)
    return weakest

def compute_overall_level(athlete: AthleteProfile) -> float:
    overall_level = 0.0
    run_score = athlete.discipline_profiles.run.level_score or 0.0
    bike_score = athlete.discipline_profiles.bike.level_score or 0.0
    swim_score = athlete.discipline_profiles.swim.level_score or 0.0
    min_score = min(run_score, bike_score, swim_score)
    if athlete.goal_profile.primary_goal in ("finish_event", "general_fitness", "return_from_injury"):
        overall_level = (run_score + bike_score + swim_score)/3
    elif athlete.goal_profile.primary_goal == "improve_triathlon":
        overall_level = (min_score * 0.5 + run_score + bike_score + swim_score)/3.5
    elif athlete.goal_profile.primary_goal == "improve_discipline":
        priority = athlete.goal_profile.priority_discipline  # "run", "bike", ou "swim"
        if priority == "run":
            overall_level = (run_score * 0.70 + bike_score * 0.15 + swim_score * 0.15)
        elif priority == "bike":
            overall_level = (run_score * 0.15 + bike_score * 0.70 + swim_score * 0.15)
        elif priority == "swim":
            overall_level = (run_score * 0.15 + bike_score * 0.15 + swim_score * 0.70)
    return overall_level


def compute_fatigue_factor(athlete: AthleteProfile) -> float:
    """Retourne le niveau de fatigue — 0.0 = pas fatigué, 1.0 = épuisé"""
    fatigue_map = {
        "low": 0.0,
        "moderate": 0.3,
        "high": 0.6,
        "very_high": 1.0,
    }
    return fatigue_map[athlete.training_state.current_fatigue]

def compute_load_factor(fatigue_level: float) -> float:
    """Retourne la charge admissible — 1.0 = 100%, 0.5 = 50%"""
    return 1.0 - (fatigue_level * 0.5)


# 3. La fonction principale
def classify(athlete: AthleteProfile) -> AthleteContext:
    return AthleteContext(
        overall_level=compute_overall_level(athlete),
        fatigue_level=compute_fatigue_factor(athlete),
        load_factor=compute_load_factor(compute_fatigue_factor(athlete)),
        weakest_discipline=compute_weakest_discipline(athlete),
        available_sessions_per_week=athlete.availability.sessions_per_week_target,
        primary_goal=athlete.goal_profile.primary_goal
    )