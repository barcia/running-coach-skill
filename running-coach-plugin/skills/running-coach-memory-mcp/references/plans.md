# Plans (Entrenamientos)

Planes de entrenamiento diarios que definen qué debe hacer el atleta cada día.

## Campos Clave

| Campo | Significado | Notas de Uso |
| :--- | :--- | :--- |
| `planned_at` | Fecha de ejecución prevista | Formato estricto `YYYY-MM-DD` |
| `description` | El qué: el entrenamiento | Claro, conciso y directo. Ej: "Rodaje 45' Z2" |
| `notes` | El porqué: explicación/contexto | Justificación, objetivo fisiológico, contexto. Opcional. |
| `status` | Estado del plan | `pending`, `completed`, `skipped`, `modified` |
| `activity_id` | ID de la actividad realizada | Vincula con la actividad grabada (ej: ID externo de plataforma) |
| `workout_id` | ID del entrenamiento estructurado | Vincula con la sesión de intervalos enviada al reloj (ej: ID externo de plataforma) |

## Estados del Plan

- **`pending`**: Por hacer, aún no ejecutado
- **`completed`**: Realizado - cambiar solo cuando haya evidencia de ejecución
- **`skipped`**: Saltado intencionalmente
- **`modified`**: Cambiado sobre la marcha respecto al plan original

## Herramientas Disponibles

- `add_plan(planned_at, description, notes)`: Crear nuevo plan
- `get_plan(plan_id)`: Obtener plan específico
- `list_plans(start_date, end_date, status, limit)`: Listar planes con filtros
- `get_today_plan()`: Obtener plan de hoy
- `get_upcoming_plans()`: Obtener próximos planes
- `update_plan(plan_id, ...)`: Actualizar plan existente
- `delete_plan(plan_id)`: Eliminar plan

## Mejores Prácticas

1. **Cierre de bucle**: Cuando un atleta termine un entrenamiento, usa `update_plan` para cambiar el estado a `completed` y, si es posible, guarda el `activity_id`
2. **Vinculación**: Conecta planes con actividades reales usando `activity_id` y con entrenamientos estructurados usando `workout_id`
3. **Estados precisos**: Solo marca como `completed` cuando haya evidencia real de ejecución
