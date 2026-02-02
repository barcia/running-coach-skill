---
name: running-coach-memory
description: Manage training plans and semantic memory via Running Coach Memory MCP. Use when creating, updating, or retrieving workout plans (CRUD), and when storing or searching conversational insights (memories) for the athlete context.
---

# Running Coach Memory MCP Guide

Esta Skill define cómo interactuar con el sistema de persistencia del entrenador. Running Coach Memory MCP es la **Single Source of Truth (SSOT)** para los *datos dinámicos* del atleta: qué hace (Planes) y qué dice (Memorias).

## Arquitectura de Datos

### 1. Planes (`plans`)
Es el registro maestro de la planificación deportiva. Actúa como calendario centralizado donde se definen los entrenamientos futuros (prescripción) y se registran los pasados (historial), permitiendo análisis de cumplimiento y carga a lo largo del tiempo.
- **Detalles:** Ver [references/plans.md](references/plans.md).

### 2. Memorias (`memories`)
El cerebro semántico. Almacena insights desestructurados para evitar amnesia entre sesiones.
- **Acceso Dual:**
    - **Lineal (Cronológico):** Útil para recordar el contexto inmediato de las últimas conversaciones.
    - **Semántico (Vectorial):** Útil para conectar puntos distantes en el tiempo (e.g., relacionar un dolor actual con una lesión de hace 6 meses).
- **Qué guardar:** Preferencias sutiles, sensaciones recurrentes, feedback cualitativo.
- **Qué NO guardar:** Datos biométricos crudos (van a la plataforma de datos) o cambios estructurales permanentes (van a `ATHLETE.md`).
- **Detalles:** Ver [references/memories.md](references/memories.md).

## Flujo de Trabajo Técnico

### 1. Inicialización (Context Loading)
Antes de decidir nada, carga el estado actual del sistema.
```python
# Obtiene de una vez:
# - 5 últimos planes (contexto de fatiga reciente)
# - 5 próximos planes (contexto de planificación futura)
# - 20 memorias recientes (contexto conversacional inmediato)
get_athlete_status()
```

### 2. Gestión de Planes (Training Logic)
Operaciones estándar para el ciclo de vida del entrenamiento.
```python
# Crear (SSOT first)
add_plan(planned_at="2026-01-30", description="5km Z2")

# Conciliar (Cierre de bucle)
# Vincula el plan con la realidad (activity_id externa)
update_plan(plan_id=123, status="completed", activity_id="garmin_987654")
```

### 3. Gestión de Memoria (Semantic Retrieval)
No confíes solo en la memoria reciente (`get_athlete_status`). Busca proactivamente.
```python
# Antes de prescribir series, verifica historial de lesiones o molestias
search_memories(query="dolor rodilla series", limit=3)

# Al recibir un insight valioso, cristalízalo
add_memory(author="agent", content="El atleta prefiere rodajes largos los domingos por logística familiar")
```

