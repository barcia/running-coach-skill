# Conversión Eufy → Garmin

Guía para importar datos de básculas Eufy Smart Scale a Garmin Connect utilizando los scripts del repositorio.

Para ver cómo ejecutar la carga, consulta [@SKILL.md](Projects/RunningCoach/skills/garmin/SKILL.md).

## Exportar Datos de Eufy

1. Abre la app **EufyLife** en tu móvil.
2. Ve a **Perfil** → **Exportar datos**.
3. Selecciona el rango de fechas.
4. Exporta como **CSV** y guarda el archivo en tu ordenador.

## Mapeo de Campos

| Campo CSV Eufy | Parámetro Garmin | Conversión |
|----------------|------------------|------------|
| `Hora` / `Date` | `date` | Formato ISO `YYYY-MM-DD` |
| `PESO (kg)` | `weight` | Directo |
| `IMC` | `bmi` | Directo |
| `% DE GRASA CORPORAL %` | `percent_fat` | Directo |
| `MASA MUSCULAR (kg)` | `muscle_mass` | Directo |
| `MB` / `BMR` | `basal_met` | Directo (metabolismo basal) |
| `AGUA` | `percent_hydration` | Directo |
| `MASA ÓSEA (kg)` | `bone_mass` | Directo |
| `GRASA VISCERAL` | `visceral_fat_rating` | Directo (entero 1-59) |
| `EDAD DEL CUERPO` | `metabolic_age` | Directo |
| `TIPO DE CUERPO` | `physique_rating` | Mapeo Tanita (1-9) |

### Campos NO Soportados en Garmin
- `FRECUENCIA CARDÍACA` - No se puede subir junto con la composición corporal.
- `% PROTEÍNA` y `% GRASA SUBCUTÁNEA` - No soportados por el API de Garmin.

### Campos Calculables
Si necesitas calcular valores manualmente:
- `% DE MASA MUSCULAR` = `MASA MUSCULAR / PESO * 100`
- `MASA GRASA CORPORAL (kg)` = `PESO * % GRASA CORPORAL / 100`
- `% DE MASA ÓSEA` = `MASA ÓSEA / PESO * 100`

## Mapeo Physique Rating (TIPO DE CUERPO)

Garmin utiliza el estándar Tanita (valores 1-9). Los scripts realizan este mapeo automáticamente.
Para la tabla completa de valores y descripciones, ver `fit.md` → sección "Physique Rating (1-9)".

| Eufy (Español) | Eufy (English) | Valor Garmin |
|----------------|----------------|--------------|
| Obesidad oculta | Hidden-Obese | 1 |
| Obeso | Obese | 2 |
| Musculatura con sobrepeso | Muscular Overweight | 3 |
| Poco ejercicio | Under-Exercised | 4 |
| Promedio | Average | 5 |
| Músculo estándar | Standard Muscular | 6 |
| Delgado | Thin | 7 |
| Delgado y musculoso | Thin and Muscular | 8 |
| Muy musculoso | Very Muscular | 9 |

## Herramientas de Conversión

La lógica de conversión y limpieza de datos reside en los siguientes scripts:

- `scripts/eufy_to_json.py`: Procesa el CSV de Eufy, normaliza headers corruptos, mapea el `physique_rating` y genera JSON.
- `scripts/upload_body_composition.py`: Utilidad para generar JSON de mediciones manuales.

## Verificación y Troubleshooting

### Verificación
1. Accede a [Garmin Connect](https://connect.garmin.com).
2. Ve a **Salud** → **Peso**.
3. Comprueba que el **Physique Rating** se muestra en los detalles de la medición.

### Troubleshooting
- **Fecha Inválida**: Asegúrate de que el CSV no tenga fechas futuras. El script detecta varios formatos comunes de fecha.
- **Datos Duplicados**: Garmin permite varias mediciones por día. Si subes el mismo archivo dos veces, se duplicarán las entradas.
- **Campos Faltantes**: Algunos valores como el `physique_rating` pueden requerir visualización en la app móvil de Garmin Connect para aparecer.
