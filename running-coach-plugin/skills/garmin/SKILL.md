---
name: garmin
description: Crear y subir workouts (carreras simples, intervalos) y datos de composicion corporal a Garmin Connect. Usar para crear entrenamientos estructurados, programarlos en calendario, subir mediciones de peso/grasa desde bascula Eufy o manualmente.
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

**Con zona de ritmo:**
```bash
python ~/.claude/skills/garmin/scripts/simple-run.py \
  --title "Easy Run" \
  --notes "Carrera fácil 30min en zona 2 de ritmo" \
  --duration 30 \
  --duration-type time \
  --target pace \
  --target-value 2
```

**Con ritmo personalizado (min/km):**
```bash
python ~/.claude/skills/garmin/scripts/simple-run.py \
  --title "Rodaje 7km" \
  --notes "Rodaje suave a ritmo 5:30-6:00" \
  --duration 7 \
  --duration-type distance \
  --target pace \
  --pace-from 5.50 \
  --pace-to 6.00
```

**Con FC personalizada (bpm):**
```bash
python ~/.claude/skills/garmin/scripts/simple-run.py \
  --title "Rodaje aeróbico" \
  --notes "Rodaje aeróbico manteniendo FC entre 135-150 bpm" \
  --duration 40 \
  --duration-type time \
  --target hr \
  --hr-from 135 \
  --hr-to 150
```

**Sin objetivo:**
```bash
python ~/.claude/skills/garmin/scripts/simple-run.py \
  --title "Easy Run" \
  --notes "Carrera fácil sin objetivo específico" \
  --duration 30 \
  --duration-type time
```

Opciones `--duration-type`: `time` (minutos) | `distance` (km)
Opciones `--target`: `none` | `hr` | `pace`

### Intervalos

**Con ritmo personalizado por fase:**
```bash
python ~/.claude/skills/garmin/scripts/interval-run.py \
  --title "3x5min ritmo" \
  --notes "Series de 5min a ritmo medio con recuperación activa" \
  --reps 3 \
  --warmup-duration 15 \
  --warmup-target pace --warmup-pace-from 6.00 --warmup-pace-to 6.50 \
  --interval-duration 5 --interval-type time \
  --interval-target pace --interval-pace-from 4.83 --interval-pace-to 5.17 \
  --recovery-duration 3 \
  --recovery-target pace --recovery-pace-from 6.00 --recovery-pace-to 6.50 \
  --cooldown-duration 10 \
  --cooldown-target pace --cooldown-pace-from 6.00 --cooldown-pace-to 6.50
```

**Con zona HR:**
```bash
python ~/.claude/skills/garmin/scripts/interval-run.py \
  --title "6x1min Z4" \
  --notes "Series cortas en zona 4 de FC para mejorar VO2max" \
  --warmup-duration 10 \
  --reps 6 \
  --interval-duration 1 --interval-type time \
  --interval-target hr --interval-target-value 4 \
  --recovery-duration 1 \
  --cooldown-duration 5
```

**Con FC personalizada (bpm):**
```bash
python ~/.claude/skills/garmin/scripts/interval-run.py \
  --title "3x5min HR 155-170" \
  --notes "Series de 5min a FC 155-170 con recuperación activa a 120-140" \
  --reps 3 \
  --warmup-duration 10 \
  --interval-duration 5 --interval-type time \
  --interval-target hr --interval-hr-from 155 --interval-hr-to 170 \
  --recovery-duration 3 \
  --recovery-target hr --recovery-hr-from 120 --recovery-hr-to 140 \
  --cooldown-duration 10
```

**Opciones de target por fase** (warmup, interval, recovery, cooldown):
- `--{fase}-target`: `none` | `hr` | `pace`
- `--{fase}-target-value`: zona 1-5 (para `hr` o `pace` zone)
- `--{fase}-pace-from` / `--{fase}-pace-to`: rango en min/km (para `pace` personalizado)
- `--{fase}-hr-from` / `--{fase}-hr-to`: rango en bpm (para `hr` personalizada)

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
| `references/workouts.md` | Schema workouts, steps, target types, ritmo personalizado, scheduling |
| `references/fit.md` | Protocolo FIT, escalas, physique rating table |
| `references/eufy-to-garmin.md` | Guía de exportación Eufy y mapeo de campos |
