#!/usr/bin/env python3
"""
Script para crear workouts de carrera simple en Garmin Connect.

Uso con zona:
    python simple-run.py --title "Easy Run" --duration 30 --duration-type time
    python simple-run.py --title "10K Z3" --duration 10 --duration-type distance --target pace --target-value 3

Uso con ritmo personalizado (min/km):
    python simple-run.py --title "Rodaje 7km" --duration 7 --duration-type distance \
        --target pace --pace-from 5.50 --pace-to 6.00

Uso con FC personalizada (bpm):
    python simple-run.py --title "Rodaje aeróbico" --duration 40 --duration-type time \
        --target hr --hr-from 135 --hr-to 150
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


# ---------------------------------------------------------------------------
# Generador
# ---------------------------------------------------------------------------

def create_simple_run_workout(
    title: str,
    duration: float,
    duration_type: str,
    target: str = "none",
    target_value: int | None = None,
    pace_from: float | None = None,
    pace_to: float | None = None,
    hr_from: float | None = None,
    hr_to: float | None = None,
    notes: str | None = None,
) -> dict:
    """Genera el JSON del workout de carrera simple."""

    # Condición de fin
    if duration_type == "time":
        end_condition = {"conditionTypeId": 2, "conditionTypeKey": "time"}
        condition_value = int(duration * 60)  # minutos a segundos
    else:  # distance
        end_condition = {"conditionTypeId": 3, "conditionTypeKey": "distance"}
        condition_value = int(duration * 1000)  # km a metros

    # Target
    if target == "hr":
        target_obj = dict(TARGET_HR_ZONE)
    elif target == "pace":
        target_obj = dict(TARGET_PACE_ZONE)
    else:
        target_obj = dict(TARGET_NO_TARGET)

    step = {
        "type": "ExecutableStepDTO",
        "stepOrder": 1,
        "stepType": {"stepTypeId": 3, "stepTypeKey": "interval"},
        "endCondition": end_condition,
        "endConditionValue": condition_value,
        "targetType": target_obj,
    }

    # Zona (1-5)
    if target in ("hr", "pace") and target_value is not None:
        step["zoneNumber"] = target_value

    # Ritmo personalizado (min/km → m/s)
    if target == "pace" and pace_from is not None and pace_to is not None:
        fast_pace = min(pace_from, pace_to)
        slow_pace = max(pace_from, pace_to)
        step["targetValueOne"] = pace_to_mps(fast_pace)   # m/s mayor (rápido)
        step["targetValueTwo"] = pace_to_mps(slow_pace)   # m/s menor (lento)

    # FC personalizada (bpm)
    if target == "hr" and hr_from is not None and hr_to is not None:
        step["targetValueOne"] = max(hr_from, hr_to)   # bpm alto
        step["targetValueTwo"] = min(hr_from, hr_to)    # bpm bajo

    workout = {
        "workoutName": title,
        "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
        "workoutSegments": [
            {
                "segmentOrder": 1,
                "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
                "workoutSteps": [step],
            }
        ],
    }

    if notes:
        workout["description"] = notes

    return workout


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Crear workout de carrera simple para Garmin Connect"
    )
    parser.add_argument("--title", required=True, help="Nombre del workout")
    parser.add_argument("--notes", required=True, help="Descripción del workout")
    parser.add_argument(
        "--duration", type=float, required=True,
        help="Duración (minutos si time, km si distance)",
    )
    parser.add_argument(
        "--duration-type", choices=["time", "distance"], default="time",
        help="Tipo de duración: time (minutos) o distance (km)",
    )
    parser.add_argument(
        "--target", choices=["none", "hr", "pace"], default="none",
        help="Tipo de objetivo",
    )
    parser.add_argument(
        "--target-value", type=int, choices=[1, 2, 3, 4, 5],
        help="Zona objetivo (1-5, para hr zone o pace zone)",
    )
    parser.add_argument("--pace-from", type=float, help="Ritmo rango inicio (min/km)")
    parser.add_argument("--pace-to", type=float, help="Ritmo rango fin (min/km)")
    parser.add_argument("--hr-from", type=float, help="FC rango inicio (bpm)")
    parser.add_argument("--hr-to", type=float, help="FC rango fin (bpm)")

    args = parser.parse_args()

    # Validaciones para HR
    if args.target == "hr":
        has_zone = args.target_value is not None
        has_hr_range = args.hr_from is not None and args.hr_to is not None
        has_partial_hr = (args.hr_from is not None) != (args.hr_to is not None)

        if has_partial_hr:
            parser.error("--hr-from y --hr-to deben usarse juntos")
        if not has_zone and not has_hr_range:
            parser.error(
                "Con --target hr necesitas:\n"
                "  Zona:  --target-value <1-5>\n"
                "  Rango: --hr-from <bpm> --hr-to <bpm>"
            )
        if has_zone and has_hr_range:
            parser.error("No combines --target-value con --hr-from/to. Usa uno u otro.")
        if has_hr_range:
            validate_hr(args.hr_from, "--hr-from")
            validate_hr(args.hr_to, "--hr-to")

    # Validaciones para Pace
    if args.target == "pace":
        has_zone = args.target_value is not None
        has_pace_range = args.pace_from is not None and args.pace_to is not None
        has_partial_pace = (args.pace_from is not None) != (args.pace_to is not None)

        if has_partial_pace:
            parser.error("--pace-from y --pace-to deben usarse juntos")
        if not has_zone and not has_pace_range:
            parser.error(
                "Con --target pace necesitas:\n"
                "  Zona:  --target-value <1-5>\n"
                "  Rango: --pace-from <min/km> --pace-to <min/km>"
            )
        if has_zone and has_pace_range:
            parser.error("No combines --target-value con --pace-from/to. Usa uno u otro.")
        if has_pace_range:
            validate_pace(args.pace_from, "--pace-from")
            validate_pace(args.pace_to, "--pace-to")

    workout = create_simple_run_workout(
        title=args.title,
        duration=args.duration,
        duration_type=args.duration_type,
        target=args.target,
        target_value=args.target_value,
        pace_from=args.pace_from,
        pace_to=args.pace_to,
        hr_from=args.hr_from,
        hr_to=args.hr_to,
        notes=args.notes,
    )

    print(json.dumps(workout, indent=2))


if __name__ == "__main__":
    main()
