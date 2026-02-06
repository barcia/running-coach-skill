# Garmin Workout Schema Reference

## Sport Types

| ID | Key |
|----|-----|
| 1 | running |
| 2 | cycling |
| 4 | strength_training |
| 5 | cardio |
| 11 | walking |

## Step Types

| ID | Key | Descripción |
|----|-----|-------------|
| 1 | warmup | Calentamiento |
| 2 | cooldown | Vuelta a la calma |
| 3 | interval | Trabajo principal |
| 4 | recovery | Recuperación entre series |
| 5 | rest | Descanso completo |

## End Conditions

| ID | Key | Unidad |
|----|-----|--------|
| 1 | lap.button | Manual |
| 2 | time | segundos |
| 3 | distance | metros |

## Target Types

| ID | Key | Descripción |
|----|-----|-------------|
| 1 | no.target | Sin objetivo |
| 4 | heart.rate.zone | Frecuencia cardíaca |
| 6 | pace.zone | Ritmo / Velocidad |

### Zona (zoneNumber)

Para usar zonas predefinidas del usuario (1-5), usar `zoneNumber`:

```json
{
  "targetType": {"workoutTargetTypeId": 4, "workoutTargetTypeKey": "heart.rate.zone"},
  "zoneNumber": 4
}
```

```json
{
  "targetType": {"workoutTargetTypeId": 6, "workoutTargetTypeKey": "pace.zone"},
  "zoneNumber": 3
}
```

### Ritmo personalizado (targetValueOne / targetValueTwo)

Para definir un rango de ritmo específico (ej: 5:30-6:00 min/km), usar `targetValueOne` y `targetValueTwo` con **velocidad en m/s**:

```json
{
  "targetType": {"workoutTargetTypeId": 6, "workoutTargetTypeKey": "pace.zone"},
  "targetValueOne": 3.0303,
  "targetValueTwo": 2.7778
}
```

**Conversión min/km → m/s:** `m/s = 1000 / (min_km × 60)`

| Ritmo (min/km) | m/s |
|-----------------|-----|
| 4:00 | 4.1667 |
| 4:30 | 3.7037 |
| 5:00 | 3.3333 |
| 5:30 | 3.0303 |
| 6:00 | 2.7778 |
| 6:30 | 2.5641 |
| 7:00 | 2.3810 |

**IMPORTANTE:**
- `targetValueOne` = velocidad MÁS RÁPIDA (m/s mayor = min/km menor)
- `targetValueTwo` = velocidad MÁS LENTA (m/s menor = min/km mayor)
- Siempre: `targetValueOne` > `targetValueTwo`
- NO mezclar: si usas `targetValueOne`/`targetValueTwo`, NO incluyas `zoneNumber`
- NO confundir targetType: ritmo es **ID 6 `pace.zone`**, frecuencia cardíaca es **ID 4 `heart.rate.zone`**

### FC personalizada (targetValueOne / targetValueTwo)

Para definir un rango de frecuencia cardíaca específico (ej: 140-160 bpm):

```json
{
  "targetType": {"workoutTargetTypeId": 4, "workoutTargetTypeKey": "heart.rate.zone"},
  "targetValueOne": 160,
  "targetValueTwo": 140
}
```

**IMPORTANTE:**
- `targetValueOne` = bpm ALTO (límite superior del rango)
- `targetValueTwo` = bpm BAJO (límite inferior del rango)
- Siempre: `targetValueOne` > `targetValueTwo`
- Mismo targetType que zona HR (ID 4), Garmin diferencia por la presencia de `targetValueOne`/`Two` vs `zoneNumber`

## ExecutableStepDTO (Step Simple)

```json
{
  "type": "ExecutableStepDTO",
  "stepOrder": 1,
  "stepType": {
    "stepTypeId": 3,
    "stepTypeKey": "interval"
  },
  "endCondition": {
    "conditionTypeId": 2,
    "conditionTypeKey": "time"
  },
  "endConditionValue": 300,
  "targetType": {
    "workoutTargetTypeId": 6,
    "workoutTargetTypeKey": "pace.zone"
  },
  "targetValueOne": 3.4483,
  "targetValueTwo": 3.2258
}
```

## RepeatGroupDTO (Grupo de Repeticiones)

```json
{
  "type": "RepeatGroupDTO",
  "stepOrder": 2,
  "numberOfIterations": 3,
  "workoutSteps": [
    {
      "type": "ExecutableStepDTO",
      "stepOrder": 1,
      "stepType": {"stepTypeId": 3, "stepTypeKey": "interval"},
      "endCondition": {"conditionTypeId": 2, "conditionTypeKey": "time"},
      "endConditionValue": 300,
      "targetType": {"workoutTargetTypeId": 6, "workoutTargetTypeKey": "pace.zone"},
      "targetValueOne": 3.4483,
      "targetValueTwo": 3.2258
    },
    {
      "type": "ExecutableStepDTO",
      "stepOrder": 2,
      "stepType": {"stepTypeId": 4, "stepTypeKey": "recovery"},
      "endCondition": {"conditionTypeId": 2, "conditionTypeKey": "time"},
      "endConditionValue": 180,
      "targetType": {"workoutTargetTypeId": 6, "workoutTargetTypeKey": "pace.zone"},
      "targetValueOne": 2.7778,
      "targetValueTwo": 2.5641
    }
  ]
}
```

## Workout Completo Ejemplo

```json
{
  "workoutName": "3x5min ritmo 4:50-5:10",
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
      "workoutSteps": [
        {
          "type": "ExecutableStepDTO",
          "stepOrder": 1,
          "stepType": {"stepTypeId": 1, "stepTypeKey": "warmup"},
          "endCondition": {"conditionTypeId": 2, "conditionTypeKey": "time"},
          "endConditionValue": 600,
          "targetType": {"workoutTargetTypeId": 6, "workoutTargetTypeKey": "pace.zone"},
          "targetValueOne": 2.7778,
          "targetValueTwo": 2.5641
        },
        {
          "type": "RepeatGroupDTO",
          "stepOrder": 2,
          "numberOfIterations": 3,
          "workoutSteps": [
            {
              "type": "ExecutableStepDTO",
              "stepOrder": 1,
              "stepType": {"stepTypeId": 3, "stepTypeKey": "interval"},
              "endCondition": {"conditionTypeId": 2, "conditionTypeKey": "time"},
              "endConditionValue": 300,
              "targetType": {"workoutTargetTypeId": 6, "workoutTargetTypeKey": "pace.zone"},
              "targetValueOne": 3.4483,
              "targetValueTwo": 3.2258
            },
            {
              "type": "ExecutableStepDTO",
              "stepOrder": 2,
              "stepType": {"stepTypeId": 4, "stepTypeKey": "recovery"},
              "endCondition": {"conditionTypeId": 2, "conditionTypeKey": "time"},
              "endConditionValue": 180,
              "targetType": {"workoutTargetTypeId": 6, "workoutTargetTypeKey": "pace.zone"},
              "targetValueOne": 2.7778,
              "targetValueTwo": 2.5641
            }
          ]
        },
        {
          "type": "ExecutableStepDTO",
          "stepOrder": 3,
          "stepType": {"stepTypeId": 2, "stepTypeKey": "cooldown"},
          "endCondition": {"conditionTypeId": 2, "conditionTypeKey": "time"},
          "endConditionValue": 300,
          "targetType": {"workoutTargetTypeId": 6, "workoutTargetTypeKey": "pace.zone"},
          "targetValueOne": 2.7778,
          "targetValueTwo": 2.5641
        }
      ]
    }
  ]
}
```

## Notas Importantes

- `endConditionValue` para tiempo siempre en **segundos**
- `endConditionValue` para distancia siempre en **metros**
- `zoneNumber` para zonas predefinidas (1-5), NO usar junto con `targetValueOne`/`targetValueTwo`
- `targetValueOne`/`targetValueTwo` para rangos personalizados, valores de ritmo en **m/s**
- `numberOfIterations` es requerido en RepeatGroupDTO
- RepeatGroupDTO NO necesita `stepType` ni `endCondition` (solo `numberOfIterations` y `workoutSteps`)
- No incluir `stepId` en workouts nuevos
- Steps dentro de RepeatGroupDTO tienen su propio `stepOrder` empezando en 1
- **CADA step DEBE tener `stepType`** — si falta, Garmin muestra "workout.stepType.null"

## Scheduling

### Programar Workout en Calendario
```python
mcp__Garmin_MCP__schedule_workout(
    workout_id=1462596263,      # ID devuelto por upload_workout
    calendar_date="2024-01-15"  # Fecha YYYY-MM-DD
)
```

### Consultar Workouts Programados
```python
mcp__Garmin_MCP__get_scheduled_workouts(
    start_date="2024-01-01",
    end_date="2024-01-31"
)
```

**Notas:**
- `workout_id` es un entero devuelto por `upload_workout`
- Un workout puede programarse múltiples veces en diferentes fechas
