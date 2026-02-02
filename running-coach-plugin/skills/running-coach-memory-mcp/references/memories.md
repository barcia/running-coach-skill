# Memories (Contexto Humano)

Sistema de memoria semántica para recordar preferencias, historial y contexto del atleta.

## Campos Clave

| Campo | Significado | Notas de Uso |
| :--- | :--- | :--- |
| `author` | Origen de la memoria | `user`, `agent`, `system` |
| `content` | Contenido de la memoria | Texto libre con información relevante |
| `distance` | Similitud semántica | Menor distancia = mayor relevancia en búsqueda vectorial |

## Tipos de Autor

- **`user`**: Citas directas o información proporcionada explícitamente por el atleta
- **`agent`**: Deducciones o inferencias hechas por el entrenador IA
- **`system`**: Información automática del sistema

## Herramientas Disponibles

- `add_memory(author, content)`: Añadir nueva memoria (genera embedding automáticamente)
- `get_memory(memory_id)`: Obtener memoria específica
- `list_memories(author, limit)`: Listar memorias con filtro opcional de autor
- `search_memories(query, limit)`: Búsqueda semántica por similitud
- `delete_memory(memory_id)`: Eliminar memoria

## Mejores Prácticas

1. **No preguntes lo ya contado**: Antes de pedir información, busca con `search_memories` si el atleta ya lo mencionó
2. **Búsqueda semántica efectiva**: Usa queries específicas como "molestias físicas", "preferencias de horario", "historial de lesiones"
3. **Usa el autor correcto**:
   - `user` para cosas que el atleta dijo directamente
   - `agent` para tus propias observaciones y deducciones
4. **Contexto relevante**: Guarda información que afecte decisiones futuras (preferencias, limitaciones, historial)
5. **Percepción del tiempo**: Cuando leas un registro en la memoria, ten en cuenta cuando se ha creado y si sigue vigente hoy en día. Cuanto más antiguo, seguramente menos relevancia tenga.
## Ejemplos de Uso

```
# Antes de sugerir una sesión intensa
search_memories(query="molestias físicas", limit=5)
search_memories(query="lesiones previas", limit=5)

# Antes de planificar horarios
search_memories(query="preferencias horario", limit=3)

# Para entender contexto personal
search_memories(query="motivación objetivos", limit=5)
```

