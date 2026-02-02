---
name: garmin-expert
description: Interact with Garmin Connect to manage biometric data and structured workouts. Use when uploading body composition, creating or scheduling workouts, syncing Eufy scale data, or analyzing activity adherence and feedback.
---

# Garmin Connect and MCP expert

Esta skill te permite interactuar con Garmin Connect a través del MCP de Garmin.

## Pautas de Análisis de Actividades

Al analizar actividades completadas por el atleta:

1. **Verificación de Cumplimiento**: Si la actividad tiene un `workout_id` asignado, obtén el workout original y compáralo con la ejecución real para evaluar la adherencia al plan.
2. **Análisis de Feedback**: Presta especial atención a los campos subjetivos para ajustar la carga futura:
   - `description`: Notas manuales del usuario.
   - `directWorkoutFeel`: Sensación general.
   - `directWorkoutRpe`: Esfuerzo percibido.
   
   Usa estos datos para determinar si el entrenamiento está siendo demasiado duro o suave.

## Referencias

- `fit.md`: **Referencia de Datos Biométricos**. Consulta este archivo cuando necesites subir datos de salud. Contiene la definición exacta de todos los parámetros de `add_body_composition`, sus unidades, rangos válidos y tablas de interpretación (como el Physique Rating).
- `workouts.md`: **Ingeniería de Workouts**. Consulta este archivo OBLIGATORIAMENTE antes de generar cualquier JSON de entrenamiento. Contiene los IDs numéricos para deportes, tipos de pasos (intervalo, recuperación, etc.), objetivos (zonas de FC, potencia) y ejemplos probados de estructuras complejas.
- `eufy-to-garmin.md`: **Guía de Conversión**. Consulta este archivo solo para tareas de migración de datos desde CSVs de EufyLife.
