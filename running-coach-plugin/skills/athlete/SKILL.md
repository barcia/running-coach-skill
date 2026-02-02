---
name: athlete
description: Manage the Athlete Profile (ATHLETE.md), the Single Source of Truth for personal data, sports history, and objectives. Use when accessing athlete context, reading/writing profile data, performing onboarding, or checking availability and preferences.
---

# Athlete Documentation Standard

Este documento define la estructura estándar para el archivo `ATHLETE.md`, que actúa como la **Single Source of Truth (SSOT)** del atleta.

El archivo debe existir siempre (por defecto en `~/.local/share/running-coach/ATHLETE.md`) y debe mantenerse actualizado. Si no existe, créalo tras entrevistar al usuario.

## Estructura Canónica

El archivo debe seguir estrictamente esta jerarquía para facilitar la lectura tanto por humanos como por el LLM.

### Reglas Generales
1.  **Jerarquía Clara:** Usa H2 (`##`) para bloques principales y H3 (`###`) para sub-secciones específicas.
2.  **Meta-descripciones:** Al inicio de cada bloque H2 o H3, incluye una breve frase en *cursiva* describiendo qué tipo de información contiene esa sección. Esto da contexto semántico al agente.
3.  **Listas:** Usa bullet points para la información.

---

### Esquema de Contenido

#### Encabezado
`# Atleta: [Nombre]`

#### 1. Información Personal
`## 1. Información Personal`
*Descripción: Datos biométricos, médicos y logísticos que definen el contexto vital del atleta.*
- Edad/Año nacimiento
- Peso/Altura
- Ubicación/Idioma/Clima
- Salud/Lesiones

`### Disponibilidad y Horario`
*Descripción: Restricciones de calendario fijas y preferencias de conciliación.*
- Días fijos ocupados (Gimnasio, trabajo, etc.)
- Días preferidos para rodajes largos
- Preferencias de conciliación (vida-deporte)

#### 2. Información Deportiva
`## 2. Información Deportiva`
*Descripción: Perfil atlético, historial, capacidades fisiológicas y herramientas disponibles.*
- Historial deportivo y experiencia
- Ritmos de referencia actuales

`### Zonas y Umbrales`
*Descripción: Referencias de intensidad. La fuente de verdad principal suele ser la configuración del dispositivo.*
- Frecuencia Cardíaca (o referencia a Garmin)
- Ritmos por zona

`### Equipamiento`
*Descripción: Hardware y material disponible para el entrenamiento.*
- Modelo de reloj/GPS
- Ecosistemas de gestión de rendimiento deportivo (Garmin, etc)
- Zapatillas y material relevante

#### 3. Objetivos
`## 3. Objetivos`
*Descripción: Metas temporales jerarquizadas que guían la periodización del plan.*
- Definir fecha de actualización (ej: "Enero 2026")
- Corto Plazo
- Medio Plazo
- Largo Plazo (Visión general)

#### 4. Preferencias de Entrenamiento
`## 4. Preferencias de Entrenamiento`
*Descripción: Pautas explícitas sobre la metodología, estilo de coaching y comunicación.*
- Filosofía (ej: Consistencia vs Intensidad)
- Estilo del coach (Duro, Empático, Técnico...)
- Feedback preferido

#### 5. Status / Momentum
`## 5. Status / Momentum`
*Descripción: Contexto vivo del estado físico/mental actual y foco del microciclo presente. Actualizar frecuentemente.*
- Fase del macrociclo actual (Base, Específico...)
- Foco de la semana/bloque actual
- Sensaciones recientes relevantes

---

## Mantenimiento

- **Lectura:** El agente debe leer este archivo al inicio de cada sesión para cargar el contexto.
- **Escritura:** Si el usuario aporta nuevos datos relevantes (cambio de peso, nuevo objetivo, lesión, cambio de horario), el agente debe actualizar directamente, o proponer actualizar si tiene dudas, este archivo para mantener la SSOT al día.
