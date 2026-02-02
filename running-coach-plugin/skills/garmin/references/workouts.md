# Workouts Estructurados en Garmin

Documentación para crear y programar entrenamientos en Garmin Connect.

## ⚠️ IMPORTANTE: Zonas Cardíacas

**Usa SIEMPRE zonas predefinidas (`zoneNumber`)** para aprovechar tu configuración de perfil:

```python
# ✅ CORRECTO - Usa zonas del perfil
"targetType": {"workoutTargetTypeId": 4, "workoutTargetTypeKey": "heart.rate.zone"},
"zoneNumber": 2  # Zona 2 según tu FC máx configurada

# ❌ INCORRECTO - Valores fijos (solo para casos especiales)
"targetType": {"workoutTargetTypeId": 4, "workoutTargetTypeKey": "heart.rate.zone"},
"targetValueOne": 125,
"targetValueTwo": 145
```

## Funciones MCP Disponibles

| Función | Descripción |
|---------|-------------|
| `get_workouts` | Lista todos los workouts guardados |
| `get_workout_by_id` | Detalles de un workout específico |
| `upload_workout` | Crear nuevo workout |
| `schedule_workout` | Programar workout en el calendario |
| `download_workout` | Descargar workout como FIT |
| `get_scheduled_workouts` | Ver workouts programados |

## Estructura de Workout

```python
workout_data = {
    "workoutName": "Nombre del workout",
    "description": "Descripción del workout con detalles del objetivo y estructura",
    "sportType": {
        "sportTypeId": 1,      # Ver tabla de deportes
        "sportTypeKey": "running"
    },
    "workoutSegments": [
        {
            "segmentOrder": 1,
            "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
            "workoutSteps": [
                # Steps del segmento
            ]
        }
    ]
}
```

## Tipos de Deporte

| sportTypeId | sportTypeKey        | Descripción en App       | Notas |
| ----------- | ------------------- | ------------------------ | ----- |
| 1           | running             | Carrera                  | Usar stepType "interval" (3) |
| 2           | cycling             | Ciclismo                 | |
| 3           | hiking              | Senderismo               | |
| 4           | other               | Natación en piscina      | ⚠️ No es "Otro" genérico |
| 5           | swimming            | Natación                 | |
| 6           | walking             | Cardio (Caminata)        | Usar stepType "other" (7) |
| 7           | fitness_equipment   | Yoga                     | |
| 8           | transition          | Transición               | |
| 9           | open_water_swimming | Natación aguas abiertas  | |

## Tipos de Steps

### Step Simple (ExecutableStepDTO)

```python
{
    "type": "ExecutableStepDTO",
    "stepId": None,
    "stepOrder": 1,
    "stepType": {
        "stepTypeId": 1,        # Ver tabla
        "stepTypeKey": "warmup"
    },
    "endCondition": {
        "conditionTypeId": 2,
        "conditionTypeKey": "time",
        "displayOrder": 2,
        "displayable": True
    },
    "endConditionValue": 600,  # 10 minutos en segundos
    "targetType": {
        "workoutTargetTypeId": 1,
        "workoutTargetTypeKey": "no.target"
    }
}
```

### Step Types

| stepTypeId | stepTypeKey | Descripción                                            |
| ---------- | ----------- | ------------------------------------------------------ |
| 1          | warmup      | Calentamiento                                          |
| 2          | cooldown    | Enfriamiento                                           |
| 3          | interval    | Carrera - Intervalo de trabajo (Usar este por default) |
| 4          | recovery    | Recuperación activa                                    |
| 5          | rest        | Descanso                                               |
| 6          | repeat      | Grupo de repetición                                    |
| 7          | other       | Otro                                                   |

### Grupo de Repetición (RepeatGroupDTO)

```python
{
    "type": "RepeatGroupDTO",
    "stepId": None,
    "stepOrder": 2,
    "stepType": {
        "stepTypeId": 6,
        "stepTypeKey": "repeat"
    },
    "numberOfIterations": 5,  # Número de repeticiones
    "workoutSteps": [
        # Steps que se repiten
    ]
}
```

## End Conditions (Condiciones de Fin)

| conditionTypeId | conditionTypeKey | Valor | Descripción |
|-----------------|------------------|-------|-------------|
| 1 | lap.button | - | Presionar botón LAP |
| 2 | time | segundos | Duración fija |
| 3 | distance | metros | Distancia fija |
| 4 | calories | kcal | Calorías quemadas |
| 5 | heart_rate.less_than | bpm | FC menor que |
| 6 | heart_rate.greater_than | bpm | FC mayor que |
| 7 | iterations | - | Solo para repeat |
| 8 | cadence.less_than | rpm/spm | Cadencia menor que |
| 9 | cadence.greater_than | rpm/spm | Cadencia mayor que |
| 10 | power.less_than | watts | Potencia menor que |
| 11 | power.greater_than | watts | Potencia mayor que |

## Target Types (Objetivos)

| workoutTargetTypeId | workoutTargetTypeKey | Descripción |
|---------------------|----------------------|-------------|
| 1 | no.target | Sin objetivo |
| 2 | power.zone | Zona de potencia |
| 3 | cadence.zone | Zona de cadencia |
| 4 | heart.rate.zone | Zona de FC |
| 5 | speed.zone | Zona de velocidad |
| 6 | pace.zone | Zona de ritmo |

### Zona de Frecuencia Cardíaca PREDEFINIDA

Usa las zonas configuradas en tu perfil de Garmin (Zona 1, Zona 2, etc.):

```python
{
    "targetType": {
        "workoutTargetTypeId": 4,
        "workoutTargetTypeKey": "heart.rate.zone"
    },
    "zoneNumber": 2  # Zona 2 de tu perfil (valores dependen de tu FC máx)
}
```

**Zonas típicas (% FC máx):**
- Zona 1: 50-60% (Recuperación)
- Zona 2: 60-70% (Base aeróbica)
- Zona 3: 70-80% (Tempo)
- Zona 4: 80-90% (Umbral)
- Zona 5: 90-100% (VO2 Max)

### Frecuencia Cardíaca PERSONALIZADA

Define valores específicos de BPM:

```python
{
    "targetType": {
        "workoutTargetTypeId": 4,
        "workoutTargetTypeKey": "heart.rate.zone"
    },
    "targetValueOne": 125,  # FC mínima en BPM
    "targetValueTwo": 145   # FC máxima en BPM
}
```

### Target con Rango (Ritmo/Velocidad)

```python
{
    "targetType": {
        "workoutTargetTypeId": 6,
        "workoutTargetTypeKey": "pace.zone"
    },
    "targetValueOne": 240,  # Ritmo más rápido (4:00/km = 240 seg/km)
    "targetValueTwo": 270   # Ritmo más lento (4:30/km = 270 seg/km)
}
```

## Ejemplos Completos

### Running: Intervalos 5x1000m (Zona 4)

```python
workout = {
    "workoutName": "5x1000m Intervalos Z4",
    "description": "Sesión de intervalos de velocidad: 5 repeticiones de 1000m en zona 4 con 400m de recuperación. Incluye calentamiento y enfriamiento.",
    "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
    "workoutSegments": [{
        "segmentOrder": 1,
        "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
        "workoutSteps": [
            # Calentamiento 10 min en Z2
            {
                "type": "ExecutableStepDTO",
                "stepOrder": 1,
                "stepType": {"stepTypeId": 1, "stepTypeKey": "warmup"},
                "endCondition": {"conditionTypeId": 2, "conditionTypeKey": "time"},
                "endConditionValue": 600,
                "targetType": {"workoutTargetTypeId": 4, "workoutTargetTypeKey": "heart.rate.zone"},
                "zoneNumber": 2
            },
            # 5 repeticiones de 1000m (Z4) + 400m recuperación
            {
                "type": "RepeatGroupDTO",
                "stepOrder": 2,
                "stepType": {"stepTypeId": 6, "stepTypeKey": "repeat"},
                "numberOfIterations": 5,
                "workoutSteps": [
                    # Intervalo 1000m en Zona 4
                    {
                        "type": "ExecutableStepDTO",
                        "stepOrder": 1,
                        "stepType": {"stepTypeId": 3, "stepTypeKey": "interval"},
                        "endCondition": {"conditionTypeId": 3, "conditionTypeKey": "distance"},
                        "endConditionValue": 1000,
                        "targetType": {"workoutTargetTypeId": 4, "workoutTargetTypeKey": "heart.rate.zone"},
                        "zoneNumber": 4
                    },
                    # Recuperación 400m en Z1
                    {
                        "type": "ExecutableStepDTO",
                        "stepOrder": 2,
                        "stepType": {"stepTypeId": 4, "stepTypeKey": "recovery"},
                        "endCondition": {"conditionTypeId": 3, "conditionTypeKey": "distance"},
                        "endConditionValue": 400,
                        "targetType": {"workoutTargetTypeId": 4, "workoutTargetTypeKey": "heart.rate.zone"},
                        "zoneNumber": 1
                    }
                ]
            },
            # Enfriamiento 10 min en Z1
            {
                "type": "ExecutableStepDTO",
                "stepOrder": 3,
                "stepType": {"stepTypeId": 2, "stepTypeKey": "cooldown"},
                "endCondition": {"conditionTypeId": 2, "conditionTypeKey": "time"},
                "endConditionValue": 600,
                "targetType": {"workoutTargetTypeId": 4, "workoutTargetTypeKey": "heart.rate.zone"},
                "zoneNumber": 1
            }
        ]
    }]
}

# Subir workout
mcp__Garmin__upload_workout(workout_data=workout)

# Agendar para mañana
mcp__Garmin__schedule_workout(
    workout_id=resultado["workout_id"],
    calendar_date="2026-01-27"
)
```

### Cycling: Tempo 2x20min

```python
workout = {
    "workoutName": "2x20min Tempo",
    "description": "Sesión de tempo en bici: 2 bloques de 20 minutos en zona 3 con recuperación entre bloques.",
    "sportType": {"sportTypeId": 2, "sportTypeKey": "cycling"},
    "workoutSegments": [{
        "segmentOrder": 1,
        "sportType": {"sportTypeId": 2, "sportTypeKey": "cycling"},
        "workoutSteps": [
            # Calentamiento 15 min
            {
                "type": "ExecutableStepDTO",
                "stepOrder": 1,
                "stepType": {"stepTypeId": 1, "stepTypeKey": "warmup"},
                "endCondition": {"conditionTypeId": 2, "conditionTypeKey": "time"},
                "endConditionValue": 900,
                "targetType": {"workoutTargetTypeId": 1, "workoutTargetTypeKey": "no.target"}
            },
            # 2x20min con 5min recuperación
            {
                "type": "RepeatGroupDTO",
                "stepOrder": 2,
                "stepType": {"stepTypeId": 6, "stepTypeKey": "repeat"},
                "numberOfIterations": 2,
                "workoutSteps": [
                    # Tempo 20min a zona de potencia
                    {
                        "type": "ExecutableStepDTO",
                        "stepOrder": 1,
                        "stepType": {"stepTypeId": 3, "stepTypeKey": "interval"},
                        "endCondition": {"conditionTypeId": 2, "conditionTypeKey": "time"},
                        "endConditionValue": 1200,
                        "targetType": {"workoutTargetTypeId": 2, "workoutTargetTypeKey": "power.zone"},
                        "targetValueOne": 200,
                        "targetValueTwo": 240
                    },
                    # Recuperación 5min
                    {
                        "type": "ExecutableStepDTO",
                        "stepOrder": 2,
                        "stepType": {"stepTypeId": 4, "stepTypeKey": "recovery"},
                        "endCondition": {"conditionTypeId": 2, "conditionTypeKey": "time"},
                        "endConditionValue": 300,
                        "targetType": {"workoutTargetTypeId": 1, "workoutTargetTypeKey": "no.target"}
                    }
                ]
            },
            # Enfriamiento 10 min
            {
                "type": "ExecutableStepDTO",
                "stepOrder": 3,
                "stepType": {"stepTypeId": 2, "stepTypeKey": "cooldown"},
                "endCondition": {"conditionTypeId": 2, "conditionTypeKey": "time"},
                "endConditionValue": 600,
                "targetType": {"workoutTargetTypeId": 1, "workoutTargetTypeKey": "no.target"}
            }
        ]
    }]
}
```

### Running Simple: Rodaje Zona 2

```python
workout = {
    "workoutName": "Rodaje Zona 2 - 45min",
    "description": "Rodaje base aeróbico de 45 minutos en zona 2. Enfoque en volumen a baja intensidad.",
    "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
    "workoutSegments": [{
        "segmentOrder": 1,
        "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
        "workoutSteps": [
            {
                "type": "ExecutableStepDTO",
                "stepOrder": 1,
                "stepType": {"stepTypeId": 3, "stepTypeKey": "interval"},
                "endCondition": {"conditionTypeId": 2, "conditionTypeKey": "time"},
                "endConditionValue": 2700,
                "targetType": {"workoutTargetTypeId": 4, "workoutTargetTypeKey": "heart.rate.zone"},
                "zoneNumber": 2  # Usa Zona 2 del perfil
            }
        ]
    }]
}
```

### Walking: Caminata de recuperación activa (Cardio)

```python
workout = {
    "workoutName": "Caminata 30min - Recuperación",
    "description": "Caminata ligera de 30 minutos para recuperación activa. Ayuda a la circulación sin añadir carga de entrenamiento.",
    "sportType": {"sportTypeId": 6, "sportTypeKey": "walking"},
    "workoutSegments": [{
        "segmentOrder": 1,
        "sportType": {"sportTypeId": 6, "sportTypeKey": "walking"},
        "workoutSteps": [
            {
                "type": "ExecutableStepDTO",
                "stepOrder": 1,
                "stepType": {"stepTypeId": 7, "stepTypeKey": "other"},
                "endCondition": {"conditionTypeId": 2, "conditionTypeKey": "time"},
                "endConditionValue": 1800,  # 30 minutos
                "targetType": {"workoutTargetTypeId": 1, "workoutTargetTypeKey": "no.target"}
            }
        ]
    }]
}
```

### Running: Tempo Run (Zona 3)

```python
workout = {
    "workoutName": "Tempo Run 30min Z3",
    "description": "Carrera a ritmo controlado: 30 minutos en zona 3 con calentamiento y enfriamiento. Mejora el umbral aeróbico.",
    "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
    "workoutSegments": [{
        "segmentOrder": 1,
        "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
        "workoutSteps": [
            # Calentamiento 15 min
            {
                "type": "ExecutableStepDTO",
                "stepOrder": 1,
                "stepType": {"stepTypeId": 1, "stepTypeKey": "warmup"},
                "endCondition": {"conditionTypeId": 2, "conditionTypeKey": "time"},
                "endConditionValue": 900,
                "targetType": {"workoutTargetTypeId": 4, "workoutTargetTypeKey": "heart.rate.zone"},
                "zoneNumber": 2
            },
            # Tempo 30min en Zona 3
            {
                "type": "ExecutableStepDTO",
                "stepOrder": 2,
                "stepType": {"stepTypeId": 3, "stepTypeKey": "interval"},
                "endCondition": {"conditionTypeId": 2, "conditionTypeKey": "time"},
                "endConditionValue": 1800,
                "targetType": {"workoutTargetTypeId": 4, "workoutTargetTypeKey": "heart.rate.zone"},
                "zoneNumber": 3
            },
            # Enfriamiento 10 min
            {
                "type": "ExecutableStepDTO",
                "stepOrder": 3,
                "stepType": {"stepTypeId": 2, "stepTypeKey": "cooldown"},
                "endCondition": {"conditionTypeId": 2, "conditionTypeKey": "time"},
                "endConditionValue": 600,
                "targetType": {"workoutTargetTypeId": 4, "workoutTargetTypeKey": "heart.rate.zone"},
                "zoneNumber": 1
            }
        ]
    }]
}
```

## Programar Workout

```python
# 1. Subir el workout
result = mcp__Garmin__upload_workout(workout_data=workout)
workout_id = result["workout_id"]

# 2. Programar para una fecha específica
mcp__Garmin__schedule_workout(
    workout_id=workout_id,
    calendar_date="2026-01-28"
)

# 3. Verificar workouts programados
scheduled = mcp__Garmin__get_scheduled_workouts(
    start_date="2026-01-28",
    end_date="2026-01-28"
)
```

## Conversión de Unidades

| Unidad | Valor en workout |
|--------|------------------|
| Tiempo | Segundos |
| Distancia | Metros |
| Ritmo | Segundos/km |
| Velocidad | m/s × 1000 |
| Potencia | Watts |
| FC | BPM |
| Cadencia | RPM o SPM |

### Conversiones Útiles

```python
# Ritmo mm:ss/km → segundos/km
def pace_to_seconds(pace_str: str) -> int:
    """Convierte '4:30' a 270 segundos."""
    parts = pace_str.split(":")
    return int(parts[0]) * 60 + int(parts[1])

# Velocidad km/h → m/s para workout
def kmh_to_workout_speed(kmh: float) -> float:
    """Convierte km/h a valor de workout."""
    return (kmh / 3.6) * 1000

# Tiempo hh:mm:ss → segundos
def time_to_seconds(time_str: str) -> int:
    """Convierte '1:30:00' a 5400 segundos."""
    parts = time_str.split(":")
    if len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    elif len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    return int(parts[0])
```

## Troubleshooting

### Error: "Invalid workout structure"
- Verifica que todos los steps tengan `type` ("ExecutableStepDTO" o "RepeatGroupDTO")
- Asegúrate de que `stepOrder` sea secuencial dentro de cada nivel

### Error: "Invalid sport type"
- Usa los IDs y keys de la tabla de deportes
- El `sportType` del workout debe coincidir con el del segmento

### Workout no aparece en el reloj
- Sincroniza el reloj con Garmin Connect
- Verifica que el tipo de deporte sea compatible con tu dispositivo

### Target de ritmo/velocidad invertido
- `targetValueOne` debe ser el valor más rápido (menor tiempo)
- `targetValueTwo` debe ser el valor más lento (mayor tiempo)
