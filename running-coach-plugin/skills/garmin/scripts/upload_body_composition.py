#!/usr/bin/env python3
"""
Generador de JSON para subir composición corporal a Garmin Connect.

Uso:
    python upload_body_composition.py --date 2026-02-03 --weight 75.5 --percent-fat 18.5

Genera un JSON listo para usar con el MCP add_body_composition.
"""

import argparse
import json
import sys
from datetime import datetime


def validate_date(date_str: str) -> str:
    """Valida que la fecha esté en formato ISO YYYY-MM-DD."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError:
        raise argparse.ArgumentTypeError(f"Fecha inválida: {date_str}. Usa formato YYYY-MM-DD")


def validate_physique_rating(value: str) -> int:
    """Valida physique_rating (1-9)."""
    v = int(value)
    if not 1 <= v <= 9:
        raise argparse.ArgumentTypeError(f"physique_rating debe estar entre 1 y 9, recibido: {v}")
    return v


def validate_visceral_fat_rating(value: str) -> int:
    """Valida visceral_fat_rating (1-59)."""
    v = int(value)
    if not 1 <= v <= 59:
        raise argparse.ArgumentTypeError(f"visceral_fat_rating debe estar entre 1 y 59, recibido: {v}")
    return v


def positive_float(value: str) -> float:
    """Valida que sea un float positivo."""
    v = float(value)
    if v <= 0:
        raise argparse.ArgumentTypeError(f"El valor debe ser positivo, recibido: {v}")
    return v


def main():
    parser = argparse.ArgumentParser(
        description="Genera JSON de composición corporal para Garmin MCP",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  %(prog)s --date 2026-02-03 --weight 75.5
  %(prog)s --date 2026-02-03 --weight 75.5 --percent-fat 18.5 --muscle-mass 35.2
  %(prog)s --date 2026-02-03 --weight 75 --bmi 24.5 --physique-rating 6
        """
    )

    # Parámetros requeridos
    parser.add_argument(
        "--date",
        type=validate_date,
        required=True,
        help="Fecha de la medición (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--weight",
        type=positive_float,
        required=True,
        help="Peso en kg"
    )

    # Parámetros opcionales
    parser.add_argument(
        "--percent-fat",
        type=float,
        metavar="PCT",
        help="Porcentaje de grasa corporal (0-100)"
    )
    parser.add_argument(
        "--percent-hydration",
        type=float,
        metavar="PCT",
        help="Porcentaje de hidratación (0-100)"
    )
    parser.add_argument(
        "--visceral-fat-mass",
        type=positive_float,
        metavar="KG",
        help="Masa de grasa visceral en kg"
    )
    parser.add_argument(
        "--bone-mass",
        type=positive_float,
        metavar="KG",
        help="Masa ósea en kg"
    )
    parser.add_argument(
        "--muscle-mass",
        type=positive_float,
        metavar="KG",
        help="Masa muscular en kg"
    )
    parser.add_argument(
        "--basal-met",
        type=positive_float,
        metavar="KCAL",
        help="Metabolismo basal en kcal/día"
    )
    parser.add_argument(
        "--active-met",
        type=positive_float,
        metavar="KCAL",
        help="Metabolismo activo en kcal/día"
    )
    parser.add_argument(
        "--physique-rating",
        type=validate_physique_rating,
        metavar="1-9",
        help="Rating físico Tanita (1=obesidad oculta, 9=muy musculoso)"
    )
    parser.add_argument(
        "--metabolic-age",
        type=positive_float,
        metavar="YEARS",
        help="Edad metabólica en años"
    )
    parser.add_argument(
        "--visceral-fat-rating",
        type=validate_visceral_fat_rating,
        metavar="1-59",
        help="Rating de grasa visceral (1-12=saludable, 13-59=exceso)"
    )
    parser.add_argument(
        "--bmi",
        type=positive_float,
        help="Índice de masa corporal"
    )

    # Opciones de output
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Output JSON en una sola línea"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        metavar="FILE",
        help="Guardar en archivo (default: stdout)"
    )

    args = parser.parse_args()

    # Construir el diccionario con solo los parámetros proporcionados
    result = {
        "date": args.date,
        "weight": args.weight,
    }

    # Mapeo de argumentos CLI a nombres de parámetros MCP
    optional_mappings = {
        "percent_fat": args.percent_fat,
        "percent_hydration": args.percent_hydration,
        "visceral_fat_mass": args.visceral_fat_mass,
        "bone_mass": args.bone_mass,
        "muscle_mass": args.muscle_mass,
        "basal_met": args.basal_met,
        "active_met": args.active_met,
        "physique_rating": args.physique_rating,
        "metabolic_age": args.metabolic_age,
        "visceral_fat_rating": args.visceral_fat_rating,
        "bmi": args.bmi,
    }

    for key, value in optional_mappings.items():
        if value is not None:
            result[key] = value

    # Generar JSON
    if args.compact:
        output = json.dumps(result, ensure_ascii=False)
    else:
        output = json.dumps(result, indent=2, ensure_ascii=False)

    # Escribir output
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
            f.write("\n")
        print(f"Guardado en: {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
