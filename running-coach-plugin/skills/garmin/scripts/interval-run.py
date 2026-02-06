#!/usr/bin/env python3
"""
Script para crear workouts de intervalos en Garmin Connect.

Uso:
    python interval-run.py --title "6x1min" --warmup-duration 10 --reps 6 \
        --interval-duration 1 --interval-type time --recovery-duration 1 --cooldown-duration 5

    python interval-run.py --title "4x1km" --warmup-duration 10 --reps 4 \
        --interval-duration 1 --interval-type distance --interval-target hr --interval-target-value 4 \
        --recovery-duration 2 --cooldown-duration 5
"""

import argparse
import json


def create_step(
    step_order: int,
    step_type_id: int,
    step_type_key: str,
    duration_minutes: float,
    target_type: str = "none",
    target_value: int | None = None,
    duration_type: str = "time",
    duration_value: float | None = None
) -> dict:
    """Crea un step ejecutable."""

    # Determinar condición de fin
    if duration_type == "time":
        end_condition = {
            "conditionTypeId": 2,
            "conditionTypeKey": "time"
        }
        condition_value = int(duration_minutes * 60)
    else:  # distance
        end_condition = {
            "conditionTypeId": 3,
            "conditionTypeKey": "distance"
        }
        condition_value = int((duration_value or duration_minutes) * 1000)

    # Crear target
    if target_type == "none" or target_value is None:
        target_obj = {
            "workoutTargetTypeId": 1,
            "workoutTargetTypeKey": "no.target"
        }
    elif target_type == "hr":
        target_obj = {
            "workoutTargetTypeId": 4,
            "workoutTargetTypeKey": "heart.rate.zone"
        }
    elif target_type == "pace":
        target_obj = {
            "workoutTargetTypeId": 6,
            "workoutTargetTypeKey": "pace.zone"
        }
    else:
        raise ValueError(f"Target type no válido: {target_type}")

    step = {
        "type": "ExecutableStepDTO",
        "stepOrder": step_order,
        "stepType": {
            "stepTypeId": step_type_id,
            "stepTypeKey": step_type_key
        },
        "endCondition": end_condition,
        "endConditionValue": condition_value,
        "targetType": target_obj
    }

    # IMPORTANTE: usar zoneNumber para HR/pace zones, NO targetValueOne/targetValueTwo
    if target_type in ("hr", "pace") and target_value is not None:
        step["zoneNumber"] = target_value

    return step


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
    interval_target: str = "none",
    interval_target_value: int | None = None,
    recovery_target: str = "none",
    recovery_target_value: int | None = None,
    cooldown_target: str = "none",
    cooldown_target_value: int | None = None
) -> dict:
    """Genera el JSON del workout de intervalos."""

    steps = []
    step_order = 1

    # Warmup
    warmup = create_step(
        step_order=step_order,
        step_type_id=1,
        step_type_key="warmup",
        duration_minutes=warmup_duration,
        target_type=warmup_target,
        target_value=warmup_target_value
    )
    steps.append(warmup)
    step_order += 1

    # Repeat group con intervalos
    interval_step = create_step(
        step_order=1,
        step_type_id=3,
        step_type_key="interval",
        duration_minutes=interval_duration,
        duration_type=interval_type,
        duration_value=interval_duration,
        target_type=interval_target,
        target_value=interval_target_value
    )

    recovery_step = create_step(
        step_order=2,
        step_type_id=4,
        step_type_key="recovery",
        duration_minutes=recovery_duration,
        target_type=recovery_target,
        target_value=recovery_target_value
    )

    repeat_group = {
        "type": "RepeatGroupDTO",
        "stepOrder": step_order,
        "numberOfIterations": reps,
        "workoutSteps": [interval_step, recovery_step]
    }
    steps.append(repeat_group)
    step_order += 1

    # Cooldown
    cooldown = create_step(
        step_order=step_order,
        step_type_id=2,
        step_type_key="cooldown",
        duration_minutes=cooldown_duration,
        target_type=cooldown_target,
        target_value=cooldown_target_value
    )
    steps.append(cooldown)

    workout = {
        "workoutName": title,
        "sportType": {
            "sportTypeId": 1,
            "sportTypeKey": "running"
        },
        "workoutSegments": [
            {
                "segmentOrder": 1,
                "sportType": {
                    "sportTypeId": 1,
                    "sportTypeKey": "running"
                },
                "workoutSteps": steps
            }
        ]
    }

    if notes:
        workout["description"] = notes

    return workout


def main():
    parser = argparse.ArgumentParser(
        description="Crear workout de intervalos para Garmin Connect"
    )

    # General
    parser.add_argument("--title", required=True, help="Nombre del workout")
    parser.add_argument("--notes", help="Descripción del workout")

    # Warmup
    parser.add_argument("--warmup-duration", type=float, required=True,
                        help="Duración calentamiento (minutos)")
    parser.add_argument("--warmup-target", choices=["none", "hr", "pace"], default="none")
    parser.add_argument("--warmup-target-value", type=int, choices=[1, 2, 3, 4, 5])

    # Series
    parser.add_argument("--reps", type=int, required=True, help="Número de repeticiones")
    parser.add_argument("--interval-duration", type=float, required=True,
                        help="Duración intervalo (minutos si time, km si distance)")
    parser.add_argument("--interval-type", choices=["time", "distance"], default="time",
                        help="Tipo duración intervalo")
    parser.add_argument("--interval-target", choices=["none", "hr", "pace"], default="none")
    parser.add_argument("--interval-target-value", type=int, choices=[1, 2, 3, 4, 5])

    # Recovery
    parser.add_argument("--recovery-duration", type=float, required=True,
                        help="Duración recuperación (minutos)")
    parser.add_argument("--recovery-target", choices=["none", "hr", "pace"], default="none")
    parser.add_argument("--recovery-target-value", type=int, choices=[1, 2, 3, 4, 5])

    # Cooldown
    parser.add_argument("--cooldown-duration", type=float, required=True,
                        help="Duración vuelta a la calma (minutos)")
    parser.add_argument("--cooldown-target", choices=["none", "hr", "pace"], default="none")
    parser.add_argument("--cooldown-target-value", type=int, choices=[1, 2, 3, 4, 5])

    args = parser.parse_args()

    # Validaciones
    for phase in ["warmup", "interval", "recovery", "cooldown"]:
        target = getattr(args, f"{phase}_target")
        value = getattr(args, f"{phase}_target_value")
        if target != "none" and value is None:
            parser.error(f"--{phase}-target-value es requerido cuando --{phase}-target no es 'none'")

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
        interval_target=args.interval_target,
        interval_target_value=args.interval_target_value,
        recovery_target=args.recovery_target,
        recovery_target_value=args.recovery_target_value,
        cooldown_target=args.cooldown_target,
        cooldown_target_value=args.cooldown_target_value
    )

    print(json.dumps(workout, indent=2))


if __name__ == "__main__":
    main()
