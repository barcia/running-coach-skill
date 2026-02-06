#!/usr/bin/env python3
"""
Script para crear workouts de carrera simple en Garmin Connect.

Uso:
    python simple-run.py --title "Easy Run" --duration 30 --duration-type time
    python simple-run.py --title "10K Run" --duration 10 --duration-type distance --target hr --target-value 3
"""

import argparse
import json


def create_simple_run_workout(
    title: str,
    duration: float,
    duration_type: str,
    target: str = "none",
    target_value: int | None = None,
    notes: str | None = None
) -> dict:
    """Genera el JSON del workout de carrera simple."""

    # Condición de fin
    if duration_type == "time":
        end_condition = {
            "conditionTypeId": 2,
            "conditionTypeKey": "time"
        }
        condition_value = int(duration * 60)  # minutos a segundos
    else:  # distance
        end_condition = {
            "conditionTypeId": 3,
            "conditionTypeKey": "distance"
        }
        condition_value = int(duration * 1000)  # km a metros

    # Target
    if target == "none" or target_value is None:
        target_obj = {
            "workoutTargetTypeId": 1,
            "workoutTargetTypeKey": "no.target"
        }
    elif target == "hr":
        target_obj = {
            "workoutTargetTypeId": 4,
            "workoutTargetTypeKey": "heart.rate.zone"
        }
    elif target == "pace":
        target_obj = {
            "workoutTargetTypeId": 6,
            "workoutTargetTypeKey": "pace.zone"
        }
    else:
        raise ValueError(f"Target type no válido: {target}")

    step = {
        "type": "ExecutableStepDTO",
        "stepOrder": 1,
        "stepType": {
            "stepTypeId": 3,
            "stepTypeKey": "interval"
        },
        "endCondition": end_condition,
        "endConditionValue": condition_value,
        "targetType": target_obj
    }

    # IMPORTANTE: usar zoneNumber para HR/pace zones, NO targetValueOne/targetValueTwo
    if target in ("hr", "pace") and target_value is not None:
        step["zoneNumber"] = target_value

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
                "workoutSteps": [step]
            }
        ]
    }

    if notes:
        workout["description"] = notes

    return workout


def main():
    parser = argparse.ArgumentParser(
        description="Crear workout de carrera simple para Garmin Connect"
    )
    parser.add_argument(
        "--title",
        required=True,
        help="Nombre del workout"
    )
    parser.add_argument(
        "--notes",
        help="Descripción del workout"
    )
    parser.add_argument(
        "--duration",
        type=float,
        required=True,
        help="Duración (minutos si time, km si distance)"
    )
    parser.add_argument(
        "--duration-type",
        choices=["time", "distance"],
        default="time",
        help="Tipo de duración: time (minutos) o distance (km)"
    )
    parser.add_argument(
        "--target",
        choices=["none", "hr", "pace"],
        default="none",
        help="Tipo de objetivo"
    )
    parser.add_argument(
        "--target-value",
        type=int,
        choices=[1, 2, 3, 4, 5],
        help="Zona objetivo (1-5)"
    )

    args = parser.parse_args()

    # Validar que si hay target, también hay target-value
    if args.target != "none" and args.target_value is None:
        parser.error("--target-value es requerido cuando --target no es 'none'")

    workout = create_simple_run_workout(
        title=args.title,
        duration=args.duration,
        duration_type=args.duration_type,
        target=args.target,
        target_value=args.target_value,
        notes=args.notes
    )

    print(json.dumps(workout, indent=2))


if __name__ == "__main__":
    main()
