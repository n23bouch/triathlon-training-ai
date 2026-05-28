from uuid import uuid4
from triathlon_planner.models.session_template import (
    SessionTemplate,
    CardioTemplateParams,
    StrengthTemplateParams,
    MobilityTemplateParams,
    LevelRange,
    StrengthLevelRange,
)
from triathlon_planner.models.athlete_profile import Sport

# ── Factory functions ─────────────────────────────────────────────────────────


def make_ef_template(discipline: Sport) -> SessionTemplate:
    """EF — Endurance Fondamentale. Pas d'échauffement, bloc Z2 continu.
    Source : modèle 80/20 (Fitzgerald), polarisé (Seiler 2010).
    Volumes : 20-35min débutant → 60-90min avancé.
    """
    return SessionTemplate(
        template_id=uuid4(),
        discipline=discipline,
        session_type="EF",
        name=f"EF {discipline.capitalize()}",
        target_level_score_min=0.0,
        target_level_score_max=100.0,
        intensity_category="low",
        params=CardioTemplateParams(
            work_zone="Z2",
            rest_zone="Z1",
            rest_ratio=0.0,
            level_ranges=[
                LevelRange(
                    level_min=0,
                    level_max=30,
                    work_volume_sec_min=1200,
                    work_volume_sec_max=2100,
                    block_duration_sec_min=1200,
                    block_duration_sec_max=2100,
                ),
                LevelRange(
                    level_min=30,
                    level_max=50,
                    work_volume_sec_min=2100,
                    work_volume_sec_max=3000,
                    block_duration_sec_min=2100,
                    block_duration_sec_max=3000,
                ),
                LevelRange(
                    level_min=50,
                    level_max=70,
                    work_volume_sec_min=2700,
                    work_volume_sec_max=4200,
                    block_duration_sec_min=2700,
                    block_duration_sec_max=4200,
                ),
                LevelRange(
                    level_min=70,
                    level_max=100,
                    work_volume_sec_min=3600,
                    work_volume_sec_max=5400,
                    block_duration_sec_min=3600,
                    block_duration_sec_max=5400,
                ),
            ],
        ),
    )


def make_recovery_template(discipline: Sport) -> SessionTemplate:
    """Récupération active. Bloc Z1 continu, pas d'échauffement.
    Source : MarathonHandbook (2026) — 30-40min débutants, jusqu'à 60min avancés.
    HR : <72% HRmax. Joe Friel : la récup active stimule l'adaptation.
    CORRECTION : 3 niveaux au lieu d'1 seul.
    """
    return SessionTemplate(
        template_id=uuid4(),
        discipline=discipline,
        session_type="Récupération",
        name=f"Récupération {discipline.capitalize()}",
        target_level_score_min=0.0,
        target_level_score_max=100.0,
        intensity_category="low",
        params=CardioTemplateParams(
            work_zone="Z1",
            rest_zone="Z1",
            rest_ratio=0.0,
            level_ranges=[
                LevelRange(
                    level_min=0,
                    level_max=30,
                    work_volume_sec_min=900,
                    work_volume_sec_max=1200,  # 15-20min
                    block_duration_sec_min=900,
                    block_duration_sec_max=1200,
                ),
                LevelRange(
                    level_min=30,
                    level_max=60,
                    work_volume_sec_min=1200,
                    work_volume_sec_max=1800,  # 20-30min
                    block_duration_sec_min=1200,
                    block_duration_sec_max=1800,
                ),
                LevelRange(
                    level_min=60,
                    level_max=100,
                    work_volume_sec_min=1800,
                    work_volume_sec_max=2700,  # 30-45min
                    block_duration_sec_min=1800,
                    block_duration_sec_max=2700,
                ),
            ],
        ),
    )


def make_long_session(discipline: Sport) -> SessionTemplate:
    """Sortie longue. Échauffement Z2, blocs Z3 (allure marathon), retour au calme Z2.
    Source : Renner's Reis (2025) — blocs Z3 10-30min selon distance cible.
    MarathonHandbook : 8-15km à allure marathon en fin de longue sortie.
    rest_ratio=0.17 ≈ 5min récup Z2 pour un bloc de 30min.
    """
    return SessionTemplate(
        template_id=uuid4(),
        discipline=discipline,
        session_type="Long",
        name=f"Sortie Longue {discipline.capitalize()}",
        target_level_score_min=0.0,
        target_level_score_max=100.0,
        intensity_category="medium",
        params=CardioTemplateParams(
            warmup_duration_sec=1200,
            warmup_zone="Z2",
            work_zone="Z3",
            rest_zone="Z2",
            rest_ratio=0.17,
            cooldown_duration_sec=600,
            cooldown_zone="Z2",
            level_ranges=[
                LevelRange(
                    level_min=0,
                    level_max=30,
                    work_volume_sec_min=600,
                    work_volume_sec_max=900,  # 1×10-15min
                    block_duration_sec_min=600,
                    block_duration_sec_max=900,
                ),
                LevelRange(
                    level_min=30,
                    level_max=50,
                    work_volume_sec_min=1800,
                    work_volume_sec_max=2400,  # 2×15-20min
                    block_duration_sec_min=900,
                    block_duration_sec_max=1200,
                ),
                LevelRange(
                    level_min=50,
                    level_max=70,
                    work_volume_sec_min=2400,
                    work_volume_sec_max=3600,  # 2-3×20-25min
                    block_duration_sec_min=1200,
                    block_duration_sec_max=1500,
                ),
                LevelRange(
                    level_min=70,
                    level_max=100,
                    work_volume_sec_min=4500,
                    work_volume_sec_max=5400,  # 3×25-30min
                    block_duration_sec_min=1500,
                    block_duration_sec_max=1800,
                ),
            ],
        ),
    )


def make_tempo_template(discipline: Sport) -> SessionTemplate:
    """Tempo. Échauffement Z2, blocs Z3, récup Z2 (footing léger entre blocs).
    Source : Hal Higdon Advanced 1 — 10-15min easy Z2, 10-20min near peak pace Z3, 5-10min easy Z2.
    CORRECTION : rest_zone Z2 au lieu de Z1 (évite accumulation lactate après Z3).
    """
    return SessionTemplate(
        template_id=uuid4(),
        discipline=discipline,
        session_type="Tempo",
        name=f"Tempo {discipline.capitalize()}",
        target_level_score_min=30.0,
        target_level_score_max=70.0,
        intensity_category="medium",
        params=CardioTemplateParams(
            warmup_duration_sec=900,
            warmup_zone="Z2",
            work_zone="Z3",
            rest_zone="Z2",  # CORRIGÉ : Z2 au lieu de Z1
            rest_ratio=0.2,
            cooldown_duration_sec=600,
            cooldown_zone="Z1",
            level_ranges=[
                LevelRange(
                    level_min=30,
                    level_max=50,
                    work_volume_sec_min=1200,
                    work_volume_sec_max=1800,  # 20-30min total
                    block_duration_sec_min=600,
                    block_duration_sec_max=900,
                ),
                LevelRange(
                    level_min=50,
                    level_max=70,
                    work_volume_sec_min=1800,
                    work_volume_sec_max=2700,  # 30-45min total
                    block_duration_sec_min=900,
                    block_duration_sec_max=1500,
                ),
            ],
        ),
    )


def make_threshold_template(discipline: Sport) -> SessionTemplate:
    """Seuil. Échauffement Z2, blocs Z4, récup Z1.
    Source : Billat — 15-25min Z4/séance selon niveau. rest_ratio=0.3 ≈ 3min récup pour 10min Z4.
    TrainingPeaks : 3min rest → speeds maintenus plus élevés.
    """
    return SessionTemplate(
        template_id=uuid4(),
        discipline=discipline,
        session_type="Seuil",
        name=f"Seuil {discipline.capitalize()}",
        target_level_score_min=30.0,
        target_level_score_max=100.0,
        intensity_category="high",
        params=CardioTemplateParams(
            warmup_duration_sec=900,
            warmup_zone="Z2",
            work_zone="Z4",
            rest_zone="Z1",
            rest_ratio=0.3,
            cooldown_duration_sec=600,
            cooldown_zone="Z1",
            level_ranges=[
                LevelRange(
                    level_min=30,
                    level_max=50,
                    work_volume_sec_min=1200,
                    work_volume_sec_max=1800,
                    block_duration_sec_min=600,
                    block_duration_sec_max=900,
                ),
                LevelRange(
                    level_min=50,
                    level_max=70,
                    work_volume_sec_min=1800,
                    work_volume_sec_max=2400,
                    block_duration_sec_min=900,
                    block_duration_sec_max=1200,
                ),
                LevelRange(
                    level_min=70,
                    level_max=100,
                    work_volume_sec_min=2400,
                    work_volume_sec_max=3600,
                    block_duration_sec_min=1200,
                    block_duration_sec_max=1800,
                ),
            ],
        ),
    )


def make_short_interval_template(discipline: Sport) -> SessionTemplate:
    """Fractionné court. Échauffement Z2, blocs Z5 courts, récup Z1.
    Source : tlimVO2max ~8min (Billat). Ne jamais dépasser 15min total Z5/séance.
    CORRECTION : rest_ratio=1.0 (récup = durée du bloc, minimum pour Z5).
    Distances : 150-600m selon niveau.
    """
    return SessionTemplate(
        template_id=uuid4(),
        discipline=discipline,
        session_type="Sprint",
        name=f"Fractionné Court {discipline.capitalize()}",
        target_level_score_min=50.0,
        target_level_score_max=100.0,
        intensity_category="high",
        params=CardioTemplateParams(
            warmup_duration_sec=900,
            warmup_zone="Z2",
            work_zone="Z5",
            rest_zone="Z1",
            rest_ratio=1.0,  # CORRIGÉ : 1.0 minimum pour Z5
            cooldown_duration_sec=600,
            cooldown_zone="Z1",
            interval_type="distance",
            level_ranges=[
                LevelRange(
                    level_min=50,
                    level_max=70,
                    work_volume_sec_min=360,
                    work_volume_sec_max=600,  # 6-10min total
                    block_duration_sec_min=30,
                    block_duration_sec_max=60,
                    block_distance_m_min=150,
                    block_distance_m_max=300,
                ),
                LevelRange(
                    level_min=70,
                    level_max=85,
                    work_volume_sec_min=480,
                    work_volume_sec_max=720,  # 8-12min total
                    block_duration_sec_min=60,
                    block_duration_sec_max=90,
                    block_distance_m_min=300,
                    block_distance_m_max=400,
                ),
                LevelRange(
                    level_min=85,
                    level_max=100,
                    work_volume_sec_min=600,
                    work_volume_sec_max=900,  # 10-15min total
                    block_duration_sec_min=60,
                    block_duration_sec_max=120,
                    block_distance_m_min=400,
                    block_distance_m_max=600,
                ),
            ],
        ),
    )


def make_long_interval_template(discipline: Sport) -> SessionTemplate:
    """Fractionné long. Échauffement Z2, blocs Z4 longs, récup active Z2.
    Source : Billat — 50-100% récup, volumes 12-40min Z4 selon niveau.
    Distances : 600-2000m.
    """
    return SessionTemplate(
        template_id=uuid4(),
        discipline=discipline,
        session_type="Sprint",
        name=f"Fractionné Long {discipline.capitalize()}",
        target_level_score_min=40.0,
        target_level_score_max=100.0,
        intensity_category="high",
        params=CardioTemplateParams(
            warmup_duration_sec=900,
            warmup_zone="Z2",
            work_zone="Z4",
            rest_zone="Z2",
            rest_ratio=0.5,
            cooldown_duration_sec=600,
            cooldown_zone="Z1",
            interval_type="distance",
            level_ranges=[
                LevelRange(
                    level_min=40,
                    level_max=60,
                    work_volume_sec_min=720,
                    work_volume_sec_max=1200,
                    block_duration_sec_min=180,
                    block_duration_sec_max=300,
                    block_distance_m_min=600,
                    block_distance_m_max=1000,
                ),
                LevelRange(
                    level_min=60,
                    level_max=80,
                    work_volume_sec_min=1200,
                    work_volume_sec_max=1800,
                    block_duration_sec_min=240,
                    block_duration_sec_max=360,
                    block_distance_m_min=1000,
                    block_distance_m_max=1500,
                ),
                LevelRange(
                    level_min=80,
                    level_max=100,
                    work_volume_sec_min=1500,
                    work_volume_sec_max=2400,
                    block_duration_sec_min=300,
                    block_duration_sec_max=480,
                    block_distance_m_min=1200,
                    block_distance_m_max=2000,
                ),
            ],
        ),
    )


def make_swim_technique_template() -> SessionTemplate:
    """Technique natation. Drills Z1-Z2, blocs courts, pas d'échauffement.
    Technique prioritaire même pour les avancés — spécificité natation.
    """
    return SessionTemplate(
        template_id=uuid4(),
        discipline="swim",
        session_type="Technique",
        name="Technique Natation",
        target_level_score_min=0.0,
        target_level_score_max=100.0,
        intensity_category="low",
        params=CardioTemplateParams(
            work_zone="Z2",
            rest_zone="Z1",
            rest_ratio=0.3,
            level_ranges=[
                LevelRange(
                    level_min=0,
                    level_max=50,
                    work_volume_sec_min=600,
                    work_volume_sec_max=900,
                    block_duration_sec_min=60,
                    block_duration_sec_max=120,
                ),
                LevelRange(
                    level_min=50,
                    level_max=100,
                    work_volume_sec_min=900,
                    work_volume_sec_max=1500,
                    block_duration_sec_min=120,
                    block_duration_sec_max=300,
                ),
            ],
        ),
    )


def make_core_strength_template() -> SessionTemplate:
    """Core & gainage isométrique. Tous niveaux.
    Source : HITP protocol (Arévalo-Chico 2024) — gainage central prioritaire.
    CORRECTION : 3 niveaux dont vrais débutants (15-20sec).
    """
    return SessionTemplate(
        template_id=uuid4(),
        discipline="strength",
        session_type="Force",
        name="Core & Gainage",
        target_level_score_min=0.0,
        target_level_score_max=100.0,
        intensity_category="medium",
        params=StrengthTemplateParams(
            movement_pattern="core",
            load_intensity="endurance",
            level_ranges=[
                StrengthLevelRange(
                    level_min=0,
                    level_max=30,
                    sets_min=2,
                    sets_max=2,
                    hold_duration_sec_min=15,
                    hold_duration_sec_max=20,  # vrais débutants
                ),
                StrengthLevelRange(
                    level_min=30,
                    level_max=60,
                    sets_min=2,
                    sets_max=3,
                    hold_duration_sec_min=20,
                    hold_duration_sec_max=35,
                ),
                StrengthLevelRange(
                    level_min=60,
                    level_max=100,
                    sets_min=3,
                    sets_max=4,
                    hold_duration_sec_min=40,
                    hold_duration_sec_max=60,
                ),
            ],
            rest_sec=30,
            unilateral=False,
            requires_gym=False,
        ),
    )


def make_legs_endurance_templates() -> list[SessionTemplate]:
    """Endurance jambes. Squats et deadlifts légers, tous niveaux.
    Source : Schoenfeld (2021) — 40-60% 1RM = 12-25 reps pour endurance musculaire.
    rest_sec=60 : repos court = endurance musculaire.
    """
    templates = []
    for pattern in ["squatting", "hinging"]:
        templates.append(
            SessionTemplate(
                template_id=uuid4(),
                discipline="strength",
                session_type="Force",
                name=f"Endurance Jambes - {pattern.capitalize()}",
                target_level_score_min=0.0,
                target_level_score_max=100.0,
                intensity_category="medium",
                params=StrengthTemplateParams(
                    movement_pattern=pattern,  # type: ignore
                    load_intensity="endurance",
                    level_ranges=[
                        StrengthLevelRange(
                            level_min=0,
                            level_max=50,
                            sets_min=2,
                            sets_max=3,
                            reps_min=12,
                            reps_max=15,
                        ),
                        StrengthLevelRange(
                            level_min=50,
                            level_max=100,
                            sets_min=3,
                            sets_max=4,
                            reps_min=15,
                            reps_max=20,
                        ),
                    ],
                    rest_sec=60,
                    unilateral=False if pattern == "squatting" else True,
                    requires_gym=False,
                ),
            )
        )
    return templates


def make_legs_strength_template() -> list[SessionTemplate]:
    """Force jambes. Squats et deadlifts chargés, intermédiaires et avancés.
    Source : Cripps (Scientific Triathlon) — 70-85% 1RM, 4-8 reps, 4 sets.
    rest_sec=150 : 2.5min minimum pour force lourde.
    """
    templates = []
    for pattern in ["squatting", "hinging"]:
        templates.append(
            SessionTemplate(
                template_id=uuid4(),
                discipline="strength",
                session_type="Force",
                name=f"Force Jambes - {pattern.capitalize()}",
                target_level_score_min=40.0,
                target_level_score_max=100.0,
                intensity_category="high",
                params=StrengthTemplateParams(
                    movement_pattern=pattern,  # type: ignore
                    load_intensity="heavy",
                    level_ranges=[
                        StrengthLevelRange(
                            level_min=40,
                            level_max=70,
                            sets_min=3,
                            sets_max=4,
                            reps_min=6,
                            reps_max=8,
                        ),
                        StrengthLevelRange(
                            level_min=70,
                            level_max=100,
                            sets_min=4,
                            sets_max=5,
                            reps_min=4,
                            reps_max=6,
                        ),
                    ],
                    rest_sec=150,
                    unilateral=False if pattern == "squatting" else True,
                    requires_gym=True,
                ),
            )
        )
    return templates


def make_upper_body_swim_template() -> SessionTemplate:
    """Force haut du corps — traction et gainage dorsal pour natation.
    Source : HITP protocol — 60-70% 1RM phase spécifique.
    CORRECTION : 3 niveaux dont avancés en heavy (70-85% 1RM, 4-6 reps).
    """
    return SessionTemplate(
        template_id=uuid4(),
        discipline="strength",
        session_type="Force",
        name="Force Haut du Corps Natation",
        target_level_score_min=0.0,
        target_level_score_max=100.0,
        intensity_category="medium",
        params=StrengthTemplateParams(
            movement_pattern="pulling",
            load_intensity="moderate",
            level_ranges=[
                StrengthLevelRange(
                    level_min=0,
                    level_max=40,
                    sets_min=2,
                    sets_max=3,
                    reps_min=10,
                    reps_max=15,
                ),
                StrengthLevelRange(
                    level_min=40,
                    level_max=70,
                    sets_min=3,
                    sets_max=4,
                    reps_min=8,
                    reps_max=12,
                ),
                StrengthLevelRange(  # AJOUTÉ : niveau avancé
                    level_min=70,
                    level_max=100,
                    sets_min=4,
                    sets_max=5,
                    reps_min=4,
                    reps_max=6,
                ),
            ],
            rest_sec=90,
            unilateral=False,
            requires_gym=True,
        ),
    )


def make_hip_mobility_template() -> SessionTemplate:
    """Mobilité hanches — fléchisseurs et rotation. Critique run + bike.
    Source : hip flexors = zone #1 critique en triathlon.
    CORRECTION : type active (hold court en fin d'amplitude) plutôt que dynamic pur.
    """
    return SessionTemplate(
        template_id=uuid4(),
        discipline="mobility",
        session_type="Mobilité",
        name="Mobilité Hanches",
        target_level_score_min=0.0,
        target_level_score_max=100.0,
        intensity_category="low",
        params=MobilityTemplateParams(
            target_zone="hip_flexor",
            mobility_type="active",  # CORRIGÉ : active (hold court 2-3s) au lieu de dynamic
            hold_sec=3,
            reps=10,
            bilateral=False,
            requires_equipment="none",
        ),
    )


def make_ankle_mobility_template() -> SessionTemplate:
    """Mobilité cheville — dorsiflexion. Prévention achille + genou."""
    return SessionTemplate(
        template_id=uuid4(),
        discipline="mobility",
        session_type="Mobilité",
        name="Mobilité Cheville",
        target_level_score_min=0.0,
        target_level_score_max=100.0,
        intensity_category="low",
        params=MobilityTemplateParams(
            target_zone="ankle",
            mobility_type="active",
            hold_sec=3,
            reps=12,
            bilateral=False,
            requires_equipment="none",
        ),
    )


def make_shoulder_mobility_template() -> SessionTemplate:
    """Mobilité épaule + thoracique. Prévention coiffe + posture natation.
    Source : étirements passifs 60-120s recommandés pour la coiffe des rotateurs.
    """
    return SessionTemplate(
        template_id=uuid4(),
        discipline="mobility",
        session_type="Mobilité",
        name="Mobilité Épaule & Thoracique",
        target_level_score_min=0.0,
        target_level_score_max=100.0,
        intensity_category="low",
        params=MobilityTemplateParams(
            target_zone="shoulder",
            mobility_type="passive",
            hold_sec=60,
            reps=None,
            bilateral=True,
            requires_equipment="band",
        ),
    )


# ── Catalogue complet ─────────────────────────────────────────────────────────

TEMPLATES: list[SessionTemplate] = [
    # ── Cardio Run ────────────────────────────────────────────────
    make_ef_template("run"),
    make_recovery_template("run"),
    make_long_session("run"),
    make_tempo_template("run"),
    make_threshold_template("run"),
    make_short_interval_template("run"),
    make_long_interval_template("run"),
    # ── Cardio Bike ───────────────────────────────────────────────
    make_ef_template("bike"),
    make_recovery_template("bike"),
    make_long_session("bike"),
    make_tempo_template("bike"),
    make_threshold_template("bike"),
    make_short_interval_template("bike"),
    make_long_interval_template("bike"),
    # ── Cardio Swim ───────────────────────────────────────────────
    make_ef_template("swim"),
    make_recovery_template("swim"),
    make_threshold_template("swim"),
    make_short_interval_template("swim"),
    make_swim_technique_template(),
    # ── Strength ──────────────────────────────────────────────────
    make_core_strength_template(),
    *make_legs_endurance_templates(),
    *make_legs_strength_template(),
    make_upper_body_swim_template(),
    # ── Mobility ──────────────────────────────────────────────────
    make_hip_mobility_template(),
    make_ankle_mobility_template(),
    make_shoulder_mobility_template(),
]
