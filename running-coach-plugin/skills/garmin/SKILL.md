---
name: garmin
description: Crear y subir workouts (carreras simples, intervalos) y datos de composicion corporal a Garmin Connect. Usar para crear entrenamientos estructurados, programarlos en calendario, subir mediciones de peso/grasa desde bascula Eufy o manualmente.
allowed-tools:
  - Bash
  - Read
  - Write
  - mcp: garmin_mcp
---

# Garmin Skill

## Tabla de Decisión

| Necesidad | Recurso |
|-----------|---------|
| Carrera simple (tiempo/distancia) | `scripts/simple-run.py` → MCP upload |
| Intervalos con repeticiones | `scripts/interval-run.py` → MCP upload |
| Programar workout en fecha | MCP `schedule_workout` directo |
| Subir peso/grasa manual | `scripts/upload_body_composition.py` → MCP |
| Importar mediciones Eufy | `scripts/eufy_to_json.py` → MCP |

---

## Workouts

### Flujo
```
Script genera JSON → mcp__Garmin_MCP__upload_workout → workoutId → mcp__Garmin_MCP__schedule_workout (opcional)
```

### Carrera Simple
```bash
python ~/.claude/skills/garmin/scripts/simple-run.py \
  --title "Easy Run" \
  --duration 30 \
  --duration-type time
```
Opciones `--duration-type`: `time` (minutos) | `distance` (km)

### Intervalos
```bash
python ~/.claude/skills/garmin/scripts/interval-run.py \
  --title "6x1min" \
  --warmup-duration 10 \
  --reps 6 \
  --interval-duration 1 \
  --interval-type time \
  --recovery-duration 1 \
  --cooldown-duration 5
```

### Subir y Programar
```python
# 1. Subir workout
response = mcp__Garmin_MCP__upload_workout(workout_data=workout_json)
workout_id = response["workoutId"]

# 2. Programar (opcional)
mcp__Garmin_MCP__schedule_workout(workout_id=workout_id, calendar_date="2024-01-15")
```

---

## Composición Corporal

### Flujo
```
CSV Eufy ──→ eufy_to_json.py ──→ JSON ──┐
                                        ├──→ mcp__Garmin_MCP__add_body_composition
Datos manuales ──→ upload_body_composition.py ──┘
```

### Subir Medición Manual
```bash
python ~/.claude/skills/garmin/scripts/upload_body_composition.py \
  --date 2026-02-03 \
  --weight 75.5 \
  --percent-fat 18.5 \
  --muscle-mass 35.2
```

**Parámetros:**
- Requeridos: `--date`, `--weight`
- Opcionales: `--percent-fat`, `--percent-hydration`, `--visceral-fat-mass`, `--bone-mass`, `--muscle-mass`, `--basal-met`, `--active-met`, `--physique-rating` (1-9), `--metabolic-age`, `--visceral-fat-rating` (1-59), `--bmi`
- Output: `--compact` (JSON en una línea), `--output FILE`

### Importar desde Eufy
```bash
# Ver todas las mediciones
python ~/.claude/skills/garmin/scripts/eufy_to_json.py eufy_export.csv

# Solo las últimas 5
python ~/.claude/skills/garmin/scripts/eufy_to_json.py eufy_export.csv --latest 5
```

### Subir a Garmin
```python
mcp__Garmin_MCP__add_body_composition(
    date="2026-02-03",
    weight=75.5,
    percent_fat=18.5,
    muscle_mass=35.2
)
```

---

## Referencias

| Archivo | Contenido |
|---------|-----------|
| `references/workouts.md` | Schema workouts, steps, valores, scheduling |
| `references/fit.md` | Protocolo FIT, escalas, physique rating table |
| `references/eufy-to-garmin.md` | Guía de exportación Eufy y mapeo de campos |
