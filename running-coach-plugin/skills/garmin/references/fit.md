# Formato FIT - Composición Corporal

Documentación para subir datos de composición corporal a Garmin Connect usando el MCP.

## Field IDs del Protocolo FIT

El protocolo FIT (Flexible and Interoperable Data Transfer) es el formato binario nativo de Garmin. Estos son los Field IDs exactos para el mensaje `weight_scale` (Message ID 30):

| Field ID | Campo | Tipo | Escala | Descripción |
|----------|-------|------|--------|-------------|
| 253 | timestamp | uint32 | 1 | Segundos desde 1989-12-31 UTC |
| 0 | weight | uint16 | 100 | Peso en kg |
| 1 | percent_fat | uint16 | 100 | % grasa corporal |
| 2 | percent_hydration | uint16 | 100 | % hidratación |
| 3 | visceral_fat_mass | uint16 | 100 | Masa grasa visceral kg |
| 4 | bone_mass | uint16 | 100 | Masa ósea kg |
| 5 | muscle_mass | uint16 | 100 | Masa muscular kg |
| 7 | basal_met | uint16 | 4 | Metabolismo basal kcal |
| 8 | physique_rating | uint8 | 1 | Rating físico 1-9 |
| 9 | active_met | uint16 | 4 | Metabolismo activo kcal |
| 10 | metabolic_age | uint8 | 1 | Edad metabólica |
| 11 | visceral_fat_rating | uint8 | 1 | Rating grasa visceral 1-59 |
| 13 | bmi | uint16 | 10 | IMC |

> **Nota:** El MCP maneja las conversiones de escala automáticamente. Pasa los valores en unidades normales.

## Función MCP

```python
mcp__Garmin_MCP__add_body_composition(
    date: str,           # Fecha en formato YYYY-MM-DD (requerido)
    weight: float,       # Peso en kg (requerido)
    percent_fat: float,          # % grasa corporal
    percent_hydration: float,    # % hidratación
    visceral_fat_mass: float,    # Masa grasa visceral (kg)
    bone_mass: float,            # Masa ósea (kg)
    muscle_mass: float,          # Masa muscular (kg)
    basal_met: float,            # Metabolismo basal (kcal)
    active_met: float,           # Metabolismo activo (kcal)
    physique_rating: int,        # Rating físico (1-9)
    metabolic_age: float,        # Edad metabólica
    visceral_fat_rating: int,    # Rating grasa visceral
    bmi: float                   # Índice de masa corporal
)
```

## Parámetros Detallados

### `date` (requerido)
Fecha de la medición en formato ISO: `YYYY-MM-DD`

### `weight` (requerido)
Peso corporal en kilogramos.

### `percent_fat`
Porcentaje de grasa corporal total. Rango típico: 5-50%.

### `percent_hydration`
Porcentaje de agua corporal. Rango típico: 45-75%.

### `visceral_fat_mass`
Masa de grasa visceral en kilogramos. Diferente de `visceral_fat_rating`.

### `bone_mass`
Masa ósea en kilogramos. Rango típico: 1.5-4.0 kg.

### `muscle_mass`
Masa muscular total en kilogramos.

### `basal_met`
Tasa metabólica basal en kcal/día. Calorías que el cuerpo quema en reposo.

### `active_met`
Tasa metabólica activa en kcal/día. Incluye actividad física.

### `metabolic_age`
Edad metabólica estimada en años.

### `visceral_fat_rating`
Rating de grasa visceral. Escala: 1-59 (típicamente 1-20 es saludable).

### `bmi`
Índice de masa corporal. Fórmula: `peso / altura²`

## Physique Rating (1-9)

El physique rating clasifica el tipo de cuerpo basándose en la relación entre grasa corporal y masa muscular. Garmin usa el estándar Tanita:

```
              Masa Muscular
              Baja   Media   Alta
           ┌──────┬──────┬──────┐
Grasa Alta │  1   │  2   │  3   │
           ├──────┼──────┼──────┤
Grasa Media│  4   │  5   │  6   │
           ├──────┼──────┼──────┤
Grasa Baja │  7   │  8   │  9   │
           └──────┴──────┴──────┘
```

| Valor | Descripción EN | Descripción ES |
|-------|----------------|----------------|
| 1 | Hidden Obese | Obesidad oculta (alta grasa, poco músculo) |
| 2 | Obese | Obeso (alta grasa, músculo promedio) |
| 3 | Solidly Built | Corpulento (alta grasa, alto músculo) |
| 4 | Under-exercised | Poco ejercicio (grasa media, poco músculo) |
| 5 | Standard/Average | Promedio (grasa y músculo medios) |
| 6 | Standard Muscular | Muscular estándar (grasa media, alto músculo) |
| 7 | Thin | Delgado (baja grasa, poco músculo) |
| 8 | Thin & Muscular | Delgado y musculoso (baja grasa, músculo medio) |
| 9 | Very Muscular | Muy musculoso (baja grasa, alto músculo) |

## Escalas FIT Protocol

El protocolo FIT almacena valores con multiplicadores para precisión:

| Campo | Escala FIT | Ejemplo |
|-------|------------|---------|
| weight | × 100 | 75.5 kg → 7550 |
| percent_fat | × 100 | 18.5% → 1850 |
| percent_hydration | × 100 | 55.2% → 5520 |
| muscle_mass | × 100 | 35.2 kg → 3520 |
| bone_mass | × 100 | 2.8 kg → 280 |
| basal_met | × 4 | 1650 kcal → 6600 |
| active_met | × 4 | 2100 kcal → 8400 |
| bmi | × 10 | 24.5 → 245 |

> **Nota:** El MCP maneja estas conversiones automáticamente. Pasa los valores en unidades normales.

## Ejemplo de Uso

```python
mcp__Garmin_MCP__add_body_composition(
    date="2025-01-26",
    weight=75.5,
    percent_fat=18.5,
    percent_hydration=55.2,
    muscle_mass=35.2,
    bone_mass=2.8,
    visceral_fat_rating=8,
    basal_met=1650,
    metabolic_age=32,
    physique_rating=6,
    bmi=24.5
)
```

## Campos Derivados

Si tu fuente solo proporciona algunos campos, puedes calcular otros:

```python
# % masa muscular (si solo tienes kg)
percent_muscle = (muscle_mass_kg / weight_kg) * 100

# Masa grasa en kg (si solo tienes %)
fat_mass_kg = weight_kg * (percent_fat / 100)

# % masa ósea (si solo tienes kg)
percent_bone = (bone_mass_kg / weight_kg) * 100

# BMI (si tienes altura en metros)
bmi = weight_kg / (height_m ** 2)
```

## Funciones MCP Relacionadas

| Función | Descripción |
|---------|-------------|
| `get_body_composition` | Obtener datos de composición corporal |
| `add_weigh_in` | Subir solo peso (sin composición) |
| `get_weigh_ins` | Obtener historial de pesajes |
| `get_stats_and_body` | Obtener stats diarios + composición |

## Fuentes

- [Garmin FIT SDK](https://developer.garmin.com/fit/protocol/)
- [Tanita Physique Rating](https://tanita.eu/understanding-your-measurements/physique-rating)
