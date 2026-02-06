#!/usr/bin/env python3
"""
Script para crear workouts de intervalos en Garmin Connect.

Uso con zonas:
    python interval-run.py --title "6x1min Z4" --warmup-duration 10 --reps 6 \
        --interval-duration 1 --interval-type time --interval-target hr --interval-target-value 4 \
        --recovery-duration 1 --cooldown-duration 5

Uso con ritmo personalizado (min/km):
    python interval-run.py --title "3x5min" --warmup-duration 15 --reps 3 \
        --interval-duration 5 --interval-type time \
        --interval-target pace --interval-pace-from 4.83 --interval-pace-to 5.17 \
        --recovery-target pace --recovery-pace-from 6.00 --recovery-pace-to 6.50 \
        --recovery-duration 3 --cooldown-duration 10 \
        --warmup-target pace --warmup-pace-from 6.00 --warmup-pace-to 6.50 \
        --cooldown-target pace --cooldown-pace-from 6.00 --cooldown-pace-to 6.50

Uso con frecuencia cardíaca personalizada (bpm):
    python interval-run.py --title "3x5min HR" --warmup-duration 10 --reps 3 \
        --interval-duration 5 --interval-type time \
        --interval-target hr --interval-hr-from 155 --interval-hr-to 170 \
        --recovery-duration 3 \
        --recovery-target hr --recovery-hr-from 120 --recovery-hr-to 140 \
        --cooldown-duration 10
"""

import argparse
import json
import sys


# ---------------------------------------------------------------------------
# Constantes Garmin API
# ---------------------------------------------------------------------------

TARGET_NO_TARGET = {"workoutTargetTypeId": 1, "workoutTargetTypeKey": "no.target"}
TARGET_HR_ZONE = {"workoutTargetTypeId": 4, "workoutTargetTypeKey": "heart.rate.zone"}
TARGET_PACE_ZONE = {"workoutTargetTypeId": 6, "workoutTargetTypeKey": "pace.zone"}

# Rangos de validación
PACE_MIN = 2.0    # min/km — nadie corre más rápido de 2:00/km
PACE_MAX = 12.0   # min/km — más lento que esto no es running
HR_MIN = 60       # bpm — por debajo no es esfuerzo real
HR_MAX = 220      # bpm — máximo teórico


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def pace_to_mps(pace_min_km: float) -> float:
    """Convierte ritmo (min/km decimal) a velocidad (m/s) para la API de Garmin."""
    return 1000 / (pace_min_km * 60)


def validate_pace(value: float, label: str) -> None:
    """Valida que un valor de ritmo esté en rango razonable."""
    if value < PACE_MIN or value > PACE_MAX:
        print(
            f"ERROR: {label} = {value} min/km fuera de rango válido ({PACE_MIN}-{PACE_MAX}).\n"
            f"  - Si querías frecuencia cardíaca, usa --target hr con --hr-from/--hr-to (bpm)\n"
            f"  - Si querías ritmo, el valor debe estar entre {PACE_MIN} y {PACE_MAX} min/km",
            file=sys.stderr,
        )
        sys.exit(1)


def validate_hr(value: float, label: str) -> None:
    """Valida que un valor de frecuencia cardíaca esté en rango razonable."""
    if value < HR_MIN or value > HR_MAX:
        print(
            f"ERROR: {label} = {value} bpm fuera de rango válido ({HR_MIN}-{HR_MAX}).\n"
            f"  - Si querías ritmo, usa --target pace con --pace-from/--pace-to (min/km)\n"
            f"  - Si querías frecuencia cardíaca, el valor debe estar entre {HR_MIN} y {HR_MAX} bpm",
            file=sys.stderr,
        )
        sys.exit(1)


def validate_phase_args(args, phase: str, parser) -> None:
    """Valida la combinación de argumentos de target para una fase."""
    target = getattr(args, f"{phase}_target")
    zone = getattr(args, f"{phase}_target_value")
    pace_from = getattr(args, f"{phase}_pace_from")
    pace_to = getattr(args, f"{phase}_pace_to")
    hr_from = getattr(args, f"{phase}_hr_from")
    hr_to = getattr(args, f"{phase}_hr_to")

    if target == "none":
        return

    if target == "hr":
        has_zone = zone is not None
        has_hr_range = hr_from is not None and hr_to is not None
        has_partial_hr = (hr_from is not None) != (hr_to is not None)

        if has_partial_hr:
            parser.error(f"--{phase}-hr-from y --{phase}-hr-to deben usarse juntos")
        if not has_zone and not has_hr_range:
            parser.error(
                f"Con --{phase}-target hr necesitas:\n"
                f"  Zona:  --{phase}-target-value <1-5>\n"
                f"  Rango: --{phase}-hr-from <bpm> --{phase}-hr-to <bpm>"
            )
        if has_zone and has_hr_range:
            parser.error(
                f"No combines --{phase}-target-value con --{phase}-hr-from/to. Usa uno u otro."
            )
        if has_hr_range:
            validate_hr(hr_from, f"--{phase}-hr-from")
            validate_hr(hr_to, f"--{phase}-hr-to")
        return

    # target == "pace"
    has_zone = zone is not None
    has_pace_range = pace_from is not None and pace_to is not None
    has_partial_pace = (pace_from is not None) != (pace_to is not None)

    if has_partial_pace:
        parser.error(f"--{phase}-pace-from y --{phase}-pace-to deben usarse juntos")

    if not has_zone and not has_pace_range:
        parser.error(
            f"Con --{phase}-target pace necesitas:\n"
            f"  Zona:  --{phase}-target-value <1-5>\n"
            f"  Rango: --{phase}-pace-from <min/km> --{phase}-pace-to <min/km>"
        )

    if has_zone and has_pace_range:
        parser.error(
            f"No combines --{phase}-target-value con --{phase}-pace-from/to. Usa uno u otro."
        )

    if has_pace_range:
        validate_pace(pace_from, f"--{phase}-pace-from")
        validate_pace(pace_to, f"--{phase}-pace-to")


# ---------------------------------------------------------------------------
# Generador de steps
# ---------------------------------------------------------------------------

def create_step(
    step_order: int,
    step_type_id: int,
    step_type_key: str,
    duration_minutes: float,
    target_type: str = "none",
    target_value: int | None = None,
    duration_type: str = "time",
    duration_value: float | None = None,
    pace_from: float | None = None,
    pace_to: float | None = None,
    hr_from: float | None = None,
    hr_to: float | None = None,
) -> dict:
    """Crea un step ejecutable."""

    # Condición de fin
    if duration_type == "time":
        end_condition = {"conditionTypeId": 2, "conditionTypeKey": "time"}
        condition_value = int(duration_minutes * 60)
    else:  # distance
        end_condition = {"conditionTypeId": 3, "conditionTypeKey": "distance"}
        condition_value = int((duration_value or duration_minutes) * 1000)

    # Target
    if target_type == "hr":
        target_obj = dict(TARGET_HR_ZONE)
    elif target_type == "pace":
        target_obj = dict(TARGET_PACE_ZONE)
    else:
        target_obj = dict(TARGET_NO_TARGET)

    step = {
        "type": "ExecutableStepDTO",
        "stepOrder": step_order,
        "stepType": {
            "stepTypeId": step_type_id,
            "stepTypeKey": step_type_key,
        },
        "endCondition": end_condition,
        "endConditionValue": condition_value,
        "targetType": target_obj,
    }

    # Zona (1-5) — para HR zone o pace zone
    if target_type in ("hr", "pace") and target_value is not None:
        step["zoneNumber"] = target_value

    # Ritmo personalizado (min/km → m/s)
    if target_type == "pace" and pace_from is not None and pace_to is not None:
        fast_pace = min(pace_from, pace_to)
        slow_pace = max(pace_from, pace_to)
        step["targetValueOne"] = pace_to_mps(fast_pace)   # m/s mayor (rápido)
        step["targetValueTwo"] = pace_to_mps(slow_pace)   # m/s menor (lento)

    # FC personalizada (bpm)
    if target_type == "hr" and hr_from is not None and hr_to is not None:
        step["targetValueOne"] = max(hr_from, hr_to)   # bpm alto
        step["targetValueTwo"] = min(hr_from, hr_to)    # bpm bajo

    return step


# ---------------------------------------------------------------------------
# Generador de workout
# ---------------------------------------------------------------------------

def create_interval_workout(
    title: str,
    warmup_duration: float,
    reps: int,
    interval_duration: float,
    interval_type: str,
    recovery_duration: float,
    cooldown_duration: float,
    notes: str | None = None,
    warmup_target: str = "none",
    warmup_target_value: int | None = None,
    warmup_pace_from: float | None = None,
    warmup_pace_to: float | None = None,
    warmup_hr_from: float | None = None,
    warmup_hr_to: float | None = None,
    interval_target: str = "none",
    interval_target_value: int | None = None,
    interval_pace_from: float | None = None,
    interval_pace_to: float | None = None,
    interval_hr_from: float | None = None,
    interval_hr_to: float | None = None,
    recovery_target: str = "none",
    recovery_target_value: int | None = None,
    recovery_pace_from: float | None = None,
    recovery_pace_to: float | None = None,
    recovery_hr_from: float | None = None,
    recovery_hr_to: float | None = None,
    cooldown_target: str = "none",
    cooldown_target_value: int | None = None,
    cooldown_pace_from: float | None = None,
    cooldown_pace_to: float | None = None,
    cooldown_hr_from: float | None = None,
    cooldown_hr_to: float | None = None,
) -> dict:
    """Genera el JSON del workout de intervalos."""

    steps = []
    step_order = 1

    # Warmup
    steps.append(create_step(
        step_order=step_order,
        step_type_id=1, step_type_key="warmup",
        duration_minutes=warmup_duration,
        target_type=warmup_target,
        target_value=warmup_target_value,
        pace_from=warmup_pace_from, pace_to=warmup_pace_to,
        hr_from=warmup_hr_from, hr_to=warmup_hr_to,
    ))
    step_order += 1

    # Repeat group
    interval_step = create_step(
        step_order=1,
        step_type_id=3, step_type_key="interval",
        duration_minutes=interval_duration,
        duration_type=interval_type,
        duration_value=interval_duration,
        target_type=interval_target,
        target_value=interval_target_value,
        pace_from=interval_pace_from, pace_to=interval_pace_to,
        hr_from=interval_hr_from, hr_to=interval_hr_to,
    )

    recovery_step = create_step(
        step_order=2,
        step_type_id=4, step_type_key="recovery",
        duration_minutes=recovery_duration,
        target_type=recovery_target,
        target_value=recovery_target_value,
        pace_from=recovery_pace_from, pace_to=recovery_pace_to,
        hr_from=recovery_hr_from, hr_to=recovery_hr_to,
    )

    steps.append({
        "type": "RepeatGroupDTO",
        "stepOrder": step_order,
        "numberOfIterations": reps,
        "workoutSteps": [interval_step, recovery_step],
    })
    step_order += 1

    # Cooldown
    steps.append(create_step(
        step_order=step_order,
        step_type_id=2, step_type_key="cooldown",
        duration_minutes=cooldown_duration,
        target_type=cooldown_target,
        target_value=cooldown_target_value,
        pace_from=cooldown_pace_from, pace_to=cooldown_pace_to,
        hr_from=cooldown_hr_from, hr_to=cooldown_hr_to,
    ))

    workout = {
        "workoutName": title,
        "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
        "workoutSegments": [
            {
                "segmentOrder": 1,
                "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
                "workoutSteps": steps,
            }
        ],
    }

    if notes:
        workout["description"] = notes

    return workout


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def add_phase_args(parser, phase: str, required_duration: bool = True):
    """Añade argumentos de target para una fase del workout."""
    parser.add_argument(
        f"--{phase}-duration", type=float, required=required_duration,
        help=f"Duración {phase} (minutos)",
    )
    parser.add_argument(
        f"--{phase}-target", choices=["none", "hr", "pace"], default="none",
        help=f"Tipo de objetivo para {phase}",
    )
    parser.add_argument(
        f"--{phase}-target-value", type=int, choices=[1, 2, 3, 4, 5],
        help=f"Zona objetivo {phase} (1-5, para hr zone o pace zone)",
    )
    parser.add_argument(
        f"--{phase}-pace-from", type=float,
        help=f"Ritmo rango inicio {phase} (min/km, ej: 6.00)",
    )
    parser.add_argument(
        f"--{phase}-pace-to", type=float,
        help=f"Ritmo rango fin {phase} (min/km, ej: 6.50)",
    )
    parser.add_argument(
        f"--{phase}-hr-from", type=float,
        help=f"FC rango inicio {phase} (bpm, ej: 140)",
    )
    parser.add_argument(
        f"--{phase}-hr-to", type=float,
        help=f"FC rango fin {phase} (bpm, ej: 160)",
    )


def main():
    parser = argparse.ArgumentParser(
        description="Crear workout de intervalos para Garmin Connect"
    )

    # General
    parser.add_argument("--title", required=True, help="Nombre del workout")
    parser.add_argument("--notes", required=True, help="Descripción del workout")

    # Series
    parser.add_argument("--reps", type=int, required=True, help="Número de repeticiones")
    parser.add_argument(
        "--interval-type", choices=["time", "distance"], default="time",
        help="Tipo duración intervalo",
    )

    # Fases
    add_phase_args(parser, "warmup")
    add_phase_args(parser, "interval")
    add_phase_args(parser, "recovery")
    add_phase_args(parser, "cooldown")

    args = parser.parse_args()

    # Validaciones
    for phase in ["warmup", "interval", "recovery", "cooldown"]:
        validate_phase_args(args, phase, parser)

    workout = create_interval_workout(
        title=args.title,
        warmup_duration=args.warmup_duration,
        reps=args.reps,
        interval_duration=args.interval_duration,
        interval_type=args.interval_type,
        recovery_duration=args.recovery_duration,
        cooldown_duration=args.cooldown_duration,
        notes=args.notes,
        warmup_target=args.warmup_target,
        warmup_target_value=args.warmup_target_value,
        warmup_pace_from=args.warmup_pace_from,
        warmup_pace_to=args.warmup_pace_to,
        warmup_hr_from=args.warmup_hr_from,
        warmup_hr_to=args.warmup_hr_to,
        interval_target=args.interval_target,
        interval_target_value=args.interval_target_value,
        interval_pace_from=args.interval_pace_from,
        interval_pace_to=args.interval_pace_to,
        interval_hr_from=args.interval_hr_from,
        interval_hr_to=args.interval_hr_to,
        recovery_target=args.recovery_target,
        recovery_target_value=args.recovery_target_value,
        recovery_pace_from=args.recovery_pace_from,
        recovery_pace_to=args.recovery_pace_to,
        recovery_hr_from=args.recovery_hr_from,
        recovery_hr_to=args.recovery_hr_to,
        cooldown_target=args.cooldown_target,
        cooldown_target_value=args.cooldown_target_value,
        cooldown_pace_from=args.cooldown_pace_from,
        cooldown_pace_to=args.cooldown_pace_to,
        cooldown_hr_from=args.cooldown_hr_from,
        cooldown_hr_to=args.cooldown_hr_to,
    )

    print(json.dumps(workout, indent=2))


if __name__ == "__main__":
    main()
