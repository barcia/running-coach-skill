# Conversión Eufy → Garmin

Guía para importar datos de básculas Eufy Smart Scale a Garmin Connect.

## Exportar Datos de Eufy

1. Abre la app **EufyLife** en tu móvil
2. Ve a **Perfil** → **Exportar datos**
3. Selecciona el rango de fechas
4. Exporta como **CSV**

## Mapeo de Campos

| Campo CSV Eufy | Parámetro Garmin | Conversión |
|----------------|------------------|------------|
| `Hora` | `date` | Formato ISO YYYY-MM-DD |
| `PESO (kg)` | `weight` | Directo |
| `IMC` | `bmi` | Directo |
| `% DE GRASA CORPORAL %` | `percent_fat` | Directo |
| `MASA MUSCULAR (kg)` | `muscle_mass` | Directo |
| `MB` | `basal_met` | Directo (metabolismo basal) |
| `AGUA` | `percent_hydration` | Directo |
| `MASA ÓSEA (kg)` | `bone_mass` | Directo |
| `GRASA VISCERAL` | `visceral_fat_rating` | Directo (entero) |
| `EDAD DEL CUERPO` | `metabolic_age` | Directo |
| `TIPO DE CUERPO` | `physique_rating` | Ver mapeo abajo |

### Campos NO Soportados en Garmin

Estos campos de Eufy no tienen equivalente en Garmin:
- `FRECUENCIA CARDÍACA` - No se puede subir con composición corporal
- `% PROTEÍNA` - No soportado
- `% GRASA SUBCUTÁNEA` - No soportado

### Campos Calculables

Eufy incluye algunos campos que Garmin puede calcular:
- `% DE MASA MUSCULAR` = `MASA MUSCULAR / PESO * 100`
- `MASA GRASA CORPORAL (kg)` = `PESO * % GRASA CORPORAL / 100`
- `% DE MASA ÓSEA` = `MASA ÓSEA / PESO * 100`

## Mapeo Physique Rating (TIPO DE CUERPO)

Eufy muestra el tipo de cuerpo como texto. Garmin usa valores 1-9 del estándar Tanita:

| Eufy (Español) | Eufy (English) | Garmin Value | Descripción |
|----------------|----------------|--------------|-------------|
| Obesidad oculta | Hidden-Obese | 1 | Alta grasa, bajo músculo |
| Obeso | Obese | 2 | Alta grasa, músculo promedio |
| Musculatura con sobrepeso | Muscular Overweight / Solidly Built | 3 | Alta grasa, alto músculo |
| Poco ejercicio | Under-Exercised | 4 | Grasa media, bajo músculo |
| Promedio | Average | 5 | Grasa y músculo promedio |
| Músculo estándar | Standard Muscular | 6 | Grasa media, alto músculo |
| Delgado | Thin | 7 | Baja grasa, bajo músculo |
| Delgado y musculoso | Thin and Muscular | 8 | Baja grasa, músculo promedio |
| Muy musculoso | Very Muscular | 9 | Baja grasa, alto músculo |

### Código de Mapeo

```python
PHYSIQUE_MAPPING = {
    # Español
    "obesidad oculta": 1,
    "obeso": 2,
    "musculatura con sobrepeso": 3,
    "poco ejercicio": 4,
    "promedio": 5,
    "músculo estándar": 6,
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

def map_physique_rating(eufy_text: str) -> int:
    """Convierte texto de Eufy a valor numérico Garmin."""
    return PHYSIQUE_MAPPING.get(eufy_text.lower().strip(), 5)  # Default: Average
```

## Conversión de Timestamps

Eufy exporta fechas en formato local. Convierte a ISO para Garmin:

```python
from datetime import datetime

# Formato Eufy típico: "26/01/2025 08:30" o "2025-01-26 08:30:00"
def parse_eufy_date(date_str: str) -> str:
    """Convierte fecha Eufy a formato ISO YYYY-MM-DD."""
    formats = [
        "%d/%m/%Y %H:%M",
        "%d/%m/%Y %H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    raise ValueError(f"Formato de fecha no reconocido: {date_str}")
```

## Ejemplo Completo de Conversión

```python
import csv

def convert_eufy_row_to_garmin(row: dict) -> dict:
    """Convierte una fila del CSV de Eufy a parámetros Garmin."""

    # Función auxiliar para parsear números
    def parse_float(value: str) -> float | None:
        if not value or value.strip() == "":
            return None
        return float(value.replace(",", "."))

    def parse_int(value: str) -> int | None:
        if not value or value.strip() == "":
            return None
        return int(float(value.replace(",", ".")))

    return {
        "date": parse_eufy_date(row.get("Hora", "")),
        "weight": parse_float(row.get("PESO (kg)", "")),
        "bmi": parse_float(row.get("IMC", "")),
        "percent_fat": parse_float(row.get("% DE GRASA CORPORAL %", "")),
        "muscle_mass": parse_float(row.get("MASA MUSCULAR (kg)", "")),
        "basal_met": parse_float(row.get("MB", "")),
        "percent_hydration": parse_float(row.get("AGUA", "")),
        "bone_mass": parse_float(row.get("MASA ÓSEA (kg)", "")),
        "visceral_fat_rating": parse_int(row.get("GRASA VISCERAL", "")),
        "metabolic_age": parse_float(row.get("EDAD DEL CUERPO", "")),
        "physique_rating": map_physique_rating(row.get("TIPO DE CUERPO", "Promedio")),
    }

# Uso
with open("eufy_export.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        garmin_data = convert_eufy_row_to_garmin(row)
        # Filtrar None values
        garmin_data = {k: v for k, v in garmin_data.items() if v is not None}

        # Llamar al MCP
        mcp__Garmin__add_body_composition(**garmin_data)
```

## Verificación en Garmin Connect

Después de subir los datos:

1. Abre [Garmin Connect](https://connect.garmin.com)
2. Ve a **Salud** → **Peso**
3. Verifica que aparecen las mediciones con fecha correcta
4. Comprueba que el **Physique Rating** se muestra correctamente en los detalles

## Troubleshooting

### Error: "Invalid date format"
- Asegúrate de usar formato ISO: `YYYY-MM-DD`
- Verifica que la fecha no sea futura

### Error: "Invalid physique_rating"
- El valor debe ser un entero entre 1 y 9
- Revisa el mapeo de texto a número

### Datos duplicados
- Garmin permite múltiples mediciones por día
- Usa `get_body_composition` para verificar antes de subir
- No hay función de eliminación vía MCP (usa la web de Garmin)

### Campos que no aparecen
- Algunos campos solo se muestran en la app móvil
- `physique_rating` puede no mostrarse si no hay suficientes datos históricos
