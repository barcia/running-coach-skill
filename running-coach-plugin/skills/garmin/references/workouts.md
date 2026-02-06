# Garmin Workout Schema Reference

## IMPORTANTE: Zonas HR/Pace

Para especificar zonas de frecuencia cardíaca o ritmo, usar **`zoneNumber`**, NO `targetValueOne`/`targetValueTwo`.

```json
{
  "targetType": {"workoutTargetTypeId": 4, "workoutTargetTypeKey": "heart.rate.zone"},
  "zoneNumber": 4
}
```

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

| ID | Key | Valor |
|----|-----|-------|
| 1 | no.target | Sin objetivo |
| 4 | heart.rate.zone | Zona 1-5 (usar `zoneNumber`) |
| 6 | pace.zone | Zona 1-5 (usar `zoneNumber`) |

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
    "workoutTargetTypeId": 4,
    "workoutTargetTypeKey": "heart.rate.zone"
  },
  "zoneNumber": 4
}
```

## RepeatGroupDTO (Grupo de Repeticiones)

```json
{
  "type": "RepeatGroupDTO",
  "stepOrder": 2,
  "numberOfIterations": 6,
  "workoutSteps": [
    {
      "type": "ExecutableStepDTO",
      "stepOrder": 1,
      "stepType": {"stepTypeId": 3, "stepTypeKey": "interval"},
      "endCondition": {"conditionTypeId": 2, "conditionTypeKey": "time"},
      "endConditionValue": 60,
      "targetType": {"workoutTargetTypeId": 4, "workoutTargetTypeKey": "heart.rate.zone"},
      "zoneNumber": 4
    },
    {
      "type": "ExecutableStepDTO",
      "stepOrder": 2,
      "stepType": {"stepTypeId": 4, "stepTypeKey": "recovery"},
      "endCondition": {"conditionTypeId": 2, "conditionTypeKey": "time"},
      "endConditionValue": 60,
      "targetType": {"workoutTargetTypeId": 4, "workoutTargetTypeKey": "heart.rate.zone"},
      "zoneNumber": 2
    }
  ]
}
```

## Workout Completo Ejemplo

```json
{
  "workoutName": "6x1min Z4",
  "description": "Intervalos en zona 4",
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
          "targetType": {"workoutTargetTypeId": 1, "workoutTargetTypeKey": "no.target"}
        },
        {
          "type": "RepeatGroupDTO",
          "stepOrder": 2,
          "numberOfIterations": 6,
          "workoutSteps": [
            {
              "type": "ExecutableStepDTO",
              "stepOrder": 1,
              "stepType": {"stepTypeId": 3, "stepTypeKey": "interval"},
              "endCondition": {"conditionTypeId": 2, "conditionTypeKey": "time"},
              "endConditionValue": 60,
              "targetType": {"workoutTargetTypeId": 4, "workoutTargetTypeKey": "heart.rate.zone"},
              "zoneNumber": 4
            },
            {
              "type": "ExecutableStepDTO",
              "stepOrder": 2,
              "stepType": {"stepTypeId": 4, "stepTypeKey": "recovery"},
              "endCondition": {"conditionTypeId": 2, "conditionTypeKey": "time"},
              "endConditionValue": 60,
              "targetType": {"workoutTargetTypeId": 4, "workoutTargetTypeKey": "heart.rate.zone"},
              "zoneNumber": 2
            }
          ]
        },
        {
          "type": "ExecutableStepDTO",
          "stepOrder": 3,
          "stepType": {"stepTypeId": 2, "stepTypeKey": "cooldown"},
          "endCondition": {"conditionTypeId": 2, "conditionTypeKey": "time"},
          "endConditionValue": 300,
          "targetType": {"workoutTargetTypeId": 1, "workoutTargetTypeKey": "no.target"}
        }
      ]
    }
  ]
}
```

## Notas Importantes

- `endConditionValue` para tiempo siempre en **segundos**
- `endConditionValue` para distancia siempre en **metros**
- **`zoneNumber`** para zonas HR/pace (1-5), NO usar `targetValueOne`/`targetValueTwo`
- **`numberOfIterations`** es requerido en RepeatGroupDTO
- RepeatGroupDTO NO necesita `stepType` ni `endCondition` (solo `numberOfIterations` y `workoutSteps`)
- No incluir `stepId` en workouts nuevos
- Steps dentro de RepeatGroupDTO tienen su propio `stepOrder` empezando en 1

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
