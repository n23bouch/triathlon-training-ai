from typing import Optional
from triathlon_planner.models.session_template import CardioZone, CardioBlock
from triathlon_planner.models.generated_session import GeneratedCardioBlock
from triathlon_planner.models.athlete_profile import AthleteProfile, Sport


def pace_from_zone(zone: CardioZone, threshold_pace_sec_per_km: float) -> float: 
    if zone == "Z1":
        return (threshold_pace_sec_per_km * 1.29 + threshold_pace_sec_per_km * 1.4)/2  
    elif zone == "Z2":
        return (threshold_pace_sec_per_km * 1.14 + threshold_pace_sec_per_km * 1.28)/2  
    elif zone == "Z3":
        return (threshold_pace_sec_per_km * 1.06 + threshold_pace_sec_per_km * 1.14)/2 
    elif zone == "Z4":
        return (threshold_pace_sec_per_km * 0.99 + threshold_pace_sec_per_km * 1.05)/2  
    elif zone == "Z5":
        return (threshold_pace_sec_per_km * 0.90 + threshold_pace_sec_per_km * 0.98)/2  
    else:
        raise ValueError(f"Unknown zone: {zone}")
    

def watts_from_zone(zone: CardioZone, ftp_watts: int) -> float:
    if zone == "Z1":
        return ftp_watts*0.50   # Z1 watts : < 55% FTP → valeur cible ~50% FTP
    elif zone == "Z2":
        return (ftp_watts * 0.56 + ftp_watts * 0.75)/2  
    elif zone == "Z3":
        return (ftp_watts * 0.76 + ftp_watts * 0.90)/2 
    elif zone == "Z4":
        return (ftp_watts * 0.91 + ftp_watts * 1.05)/2  
    elif zone == "Z5":
        return ftp_watts*1.10   # Z5 watts : > 106% FTP → valeur cible ~110% FTP
    else:
        raise ValueError(f"Unknown zone: {zone}")

def heart_rate_from_zone(zone: CardioZone, threshold_heart_rate_bpm: int) -> float:
    if zone == "Z1":
        return threshold_heart_rate_bpm*0.70   # Z1 FC : < 75% → valeur cible ~70%
    elif zone == "Z2":
        return (threshold_heart_rate_bpm * 0.75 + threshold_heart_rate_bpm * 0.85)/2  
    elif zone == "Z3":
        return (threshold_heart_rate_bpm * 0.85 + threshold_heart_rate_bpm * 0.95)/2 
    elif zone == "Z4":
        return (threshold_heart_rate_bpm * 0.95 + threshold_heart_rate_bpm * 1.02)/2  
    elif zone == "Z5":
        return threshold_heart_rate_bpm*1.07  # Z5 FC : > 102% → valeur cible ~107%
    else:
        raise ValueError(f"Unknown zone: {zone}")
    
def swim_pace_from_zone(zone: CardioZone, css_pace_sec_per_100m: float) -> float:
    if zone == "Z1":
        return (css_pace_sec_per_100m * 1.30 + css_pace_sec_per_100m * 1.45)/2  
    elif zone == "Z2":
        return (css_pace_sec_per_100m * 1.15 + css_pace_sec_per_100m * 1.29)/2  
    elif zone == "Z3":
        return (css_pace_sec_per_100m * 1.05 + css_pace_sec_per_100m * 1.14)/2 
    elif zone == "Z4":
        return (css_pace_sec_per_100m * 0.95 + css_pace_sec_per_100m * 1.04)/2  
    elif zone == "Z5":
        return (css_pace_sec_per_100m*0.94 + css_pace_sec_per_100m*0.87)/2
    else:
        raise ValueError(f"Unknown zone: {zone}")

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
            target_pace_km = round(pace_from_zone(zone, metrics.threshold_pace_sec_per_km))
        if metrics and metrics.threshold_heart_rate_bpm:
            target_hr = round(heart_rate_from_zone(zone, metrics.threshold_heart_rate_bpm))

    elif discipline == "bike":
        metrics = athlete.discipline_profiles.bike.performance_metrics
        if metrics and metrics.ftp_watts:
            target_watts = round(watts_from_zone(zone, metrics.ftp_watts))
        if metrics and metrics.threshold_heart_rate_bpm:
            target_hr = round(heart_rate_from_zone(zone, metrics.threshold_heart_rate_bpm))

    elif discipline == "swim":
        metrics = athlete.discipline_profiles.swim.performance_metrics
        if metrics and metrics.css_pace_sec_per_100m:
            target_pace_100m = round(swim_pace_from_zone(zone, metrics.css_pace_sec_per_100m))
        # FC en fallback si pas de CSS
        run_metrics = athlete.discipline_profiles.run.performance_metrics
        if run_metrics and run_metrics.threshold_heart_rate_bpm:
            target_hr = round(heart_rate_from_zone(zone, run_metrics.threshold_heart_rate_bpm))

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