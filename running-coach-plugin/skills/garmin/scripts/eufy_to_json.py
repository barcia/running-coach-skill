#!/usr/bin/env python3
"""
Conversor de datos de báscula Eufy a JSON para Garmin Connect.

Uso:
    python eufy_to_json.py eufy_export.csv
    python eufy_to_json.py eufy_export.csv --latest 5
    python eufy_to_json.py eufy_export.csv --output mediciones.json
    python eufy_to_json.py eufy_export.csv --compact

Genera JSON compatible con el MCP add_body_composition de Garmin.
"""

import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path


# Mapeo de tipos de cuerpo Eufy → Garmin physique_rating (1-9)
# Basado en el estándar Tanita usado por Garmin FIT SDK
PHYSIQUE_MAPPING = {
    # Español (con variaciones de capitalización)
    "obesidad oculta": 1,
    "obeso": 2,
    "musculatura con sobrepeso": 3,
    "poco ejercicio": 4,
    "promedio": 5,
    "músculo estándar": 6,
    "musculo estándar": 6,
    "músculo estandar": 6,
    "musculo estandar": 6,
    "delgado": 7,
    "delgado y musculoso": 8,
    "muy musculoso": 9,
    # English
    "hidden-obese": 1,
    "hidden obese": 1,
    "obese": 2,
    "muscular overweight": 3,
    "solidly built": 3,
    "under-exercised": 4,
    "under exercised": 4,
    "average": 5,
    "standard": 5,
    "standard muscular": 6,
    "thin": 7,
    "thin and muscular": 8,
    "thin & muscular": 8,
    "very muscular": 9,
}


def parse_eufy_date(date_str: str) -> str:
    """Convierte fecha Eufy a formato ISO YYYY-MM-DD."""
    if not date_str or not date_str.strip():
        raise ValueError("Fecha vacía")

    formats = [
        "%d/%m/%Y %H:%M",
        "%d/%m/%Y %H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%d-%m-%Y %H:%M",
        "%d-%m-%Y %H:%M:%S",
    ]

    date_str = date_str.strip()
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue

    raise ValueError(f"Formato de fecha no reconocido: {date_str}")


def parse_float(value: str) -> float | None:
    """Parsea un valor float desde string."""
    if not value or value.strip() == "" or value.strip() == "-":
        return None
    try:
        return float(value.replace(",", ".").strip())
    except ValueError:
        return None


def parse_int(value: str) -> int | None:
    """Parsea un valor int desde string."""
    f = parse_float(value)
    return int(f) if f is not None else None


def map_physique_rating(eufy_text: str) -> int:
    """Convierte texto de Eufy a valor numérico Garmin (1-9)."""
    if not eufy_text or not eufy_text.strip():
        return 5  # Default: Average
    text = eufy_text.lower().strip()
    return PHYSIQUE_MAPPING.get(text, 5)


def convert_eufy_row(row: dict) -> dict | None:
    """Convierte una fila del CSV de Eufy a parámetros Garmin."""
    try:
        # Intentar obtener la fecha
        date_field = row.get("Hora") or row.get("Date") or row.get("Fecha")
        if not date_field:
            return None

        date = parse_eufy_date(date_field)

        # Peso es requerido
        weight = parse_float(row.get("PESO (kg)") or row.get("Weight (kg)"))
        if weight is None:
            return None

        result = {
            "date": date,
            "weight": weight,
        }

        # Campos opcionales
        if (v := parse_float(row.get("IMC") or row.get("BMI"))) is not None:
            result["bmi"] = v

        # % grasa corporal (con header corrupto y normal)
        percent_fat_key = (
            row.get("% DE GRASA CORPORAL %") or
            row.get("%!D(MISSING)E GRASA CORPORAL %") or
            row.get("Body Fat %")
        )
        if (v := parse_float(percent_fat_key)) is not None:
            result["percent_fat"] = v

        if (v := parse_float(row.get("MASA MUSCULAR (kg)") or row.get("Muscle Mass (kg)"))) is not None:
            result["muscle_mass"] = v

        if (v := parse_float(row.get("MB") or row.get("BMR"))) is not None:
            result["basal_met"] = v

        if (v := parse_float(row.get("AGUA") or row.get("Water %"))) is not None:
            result["percent_hydration"] = v

        if (v := parse_float(row.get("MASA ÓSEA (kg)") or row.get("Bone Mass (kg)"))) is not None:
            result["bone_mass"] = v

        if (v := parse_int(row.get("GRASA VISCERAL") or row.get("Visceral Fat"))) is not None:
            result["visceral_fat_rating"] = v

        if (v := parse_float(row.get("EDAD DEL CUERPO") or row.get("Body Age"))) is not None:
            result["metabolic_age"] = v

        # Physique rating (mapeo de texto)
        physique_text = row.get("TIPO DE CUERPO") or row.get("Body Type")
        if physique_text:
            result["physique_rating"] = map_physique_rating(physique_text)

        return result

    except Exception as e:
        print(f"Error procesando fila: {e}", file=sys.stderr)
        return None


def read_eufy_csv(file_path: Path) -> list[dict]:
    """Lee el CSV de Eufy y retorna lista de mediciones convertidas."""
    results = []

    # Intentar diferentes encodings
    encodings = ["utf-8-sig", "utf-8", "latin-1", "cp1252"]

    for encoding in encodings:
        try:
            with open(file_path, "r", encoding=encoding) as f:
                content = f.read()
                delimiter = "," if content.count(",") > content.count(";") else ";"

            with open(file_path, "r", encoding=encoding) as f:
                reader = csv.DictReader(f, delimiter=delimiter)
                for row in reader:
                    converted = convert_eufy_row(row)
                    if converted:
                        results.append(converted)
                break

        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"Error leyendo archivo con encoding {encoding}: {e}", file=sys.stderr)
            continue

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Convierte CSV de báscula Eufy a JSON para Garmin",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  %(prog)s eufy_export.csv
  %(prog)s eufy_export.csv --latest 5
  %(prog)s eufy_export.csv --output mediciones.json
  %(prog)s eufy_export.csv --compact
        """
    )
    parser.add_argument(
        "csv_file",
        type=Path,
        help="Archivo CSV exportado de EufyLife"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        help="Guardar JSON en archivo (default: stdout)"
    )
    parser.add_argument(
        "--latest", "-l",
        type=int,
        metavar="N",
        help="Solo procesar las últimas N mediciones"
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Output JSON en una sola línea por medición"
    )

    args = parser.parse_args()

    if not args.csv_file.exists():
        print(f"Error: Archivo no encontrado: {args.csv_file}", file=sys.stderr)
        sys.exit(1)

    # Leer y convertir
    measurements = read_eufy_csv(args.csv_file)

    if not measurements:
        print("No se encontraron mediciones válidas", file=sys.stderr)
        sys.exit(1)

    # Ordenar por fecha (más reciente primero)
    measurements.sort(key=lambda x: x["date"], reverse=True)

    # Limitar si se especificó --latest
    if args.latest:
        measurements = measurements[:args.latest]

    print(f"Encontradas {len(measurements)} mediciones", file=sys.stderr)

    # Generar output
    if args.compact:
        output = "\n".join(json.dumps(m, ensure_ascii=False) for m in measurements)
    else:
        output = json.dumps(measurements, indent=2, ensure_ascii=False)

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
