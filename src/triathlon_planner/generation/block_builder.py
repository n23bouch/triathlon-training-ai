from typing import Optional
from triathlon_planner.models.session_template import CardioBlock
from triathlon_planner.models.generated_session import GeneratedCardioBlock
from triathlon_planner.models.athlete_profile import AthleteProfile, Sport
from .calculator import (
    pace_from_zone,
    watts_from_zone,
    heart_rate_from_zone,
    swim_pace_from_zone,
)


def generate_cardio_block(
    block: CardioBlock,
    discipline: Sport,
    athlete: AthleteProfile,
) -> GeneratedCardioBlock:
    zone = block.cardio_zone
    target_pace_km: Optional[float] = None
    target_pace_100m: Optional[float] = None
    target_watts: Optional[int] = None
    target_hr: Optional[int] = None

    if discipline == "run":
        metrics = athlete.discipline_profiles.run.performance_metrics
        if metrics and metrics.threshold_pace_sec_per_km:
            target_pace_km = round(
                pace_from_zone(zone, metrics.threshold_pace_sec_per_km)
            )
        if metrics and metrics.threshold_heart_rate_bpm:
            target_hr = round(
                heart_rate_from_zone(zone, metrics.threshold_heart_rate_bpm)
            )

    elif discipline == "bike":
        metrics = athlete.discipline_profiles.bike.performance_metrics
        if metrics and metrics.ftp_watts:
            target_watts = round(watts_from_zone(zone, metrics.ftp_watts))
        if metrics and metrics.threshold_heart_rate_bpm:
            target_hr = round(
                heart_rate_from_zone(zone, metrics.threshold_heart_rate_bpm)
            )

    elif discipline == "swim":
        metrics = athlete.discipline_profiles.swim.performance_metrics
        if metrics and metrics.css_pace_sec_per_100m:
            target_pace_100m = round(
                swim_pace_from_zone(zone, metrics.css_pace_sec_per_100m)
            )
        # FC en fallback si pas de CSS
        run_metrics = athlete.discipline_profiles.run.performance_metrics
        if run_metrics and run_metrics.threshold_heart_rate_bpm:
            target_hr = round(
                heart_rate_from_zone(zone, run_metrics.threshold_heart_rate_bpm)
            )

    generated_recovery = None
    if block.recovery_block:
        generated_recovery = generate_cardio_block(
            block=block.recovery_block,
            discipline=discipline,
            athlete=athlete,
        )

    return GeneratedCardioBlock(
        **block.model_dump(exclude={"recovery_block"}),
        target_pace_sec_per_km=target_pace_km,
        target_pace_sec_per_100m=target_pace_100m,
        target_power_watts=target_watts,
        target_heart_rate_bpm=target_hr,
        recovery_block=generated_recovery,
    )
