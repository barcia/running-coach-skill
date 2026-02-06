# Running Coach

AI running coach agent with persistent memory.

## Overview

Monorepo con dos componentes:

- **`running-coach-plugin/`** — Plugin de Running Coach para Claude Desktop. Incluye agents, skills y configuración de MCPs.
- **`running-coach-memory-mcp/`** — MCP server que gestiona memoria semántica y planes de entrenamiento. Es la pieza clave para que el agente mantenga contexto entre sesiones.

## Installation

### Plugin

Descarga el `.zip` desde [Releases](https://github.com/ivanbarcia/running-coach-skill/releases) e instálalo en Claude Desktop.

### Manual

Si prefieres configurar todo manualmente:

#### 1. Garmin MCP

Instala y autentica el [Garmin MCP](https://github.com/Taxuspt/garmin_mcp):

```bash
uvx --python 3.12 --from git+https://github.com/Taxuspt/garmin_mcp garmin-mcp-auth
```

Sigue los prompts para email, password y MFA. Los tokens se guardan en `~/.garminconnect`.

#### 2. Running Coach Memory MCP

```bash
cd running-coach-memory-mcp
uv sync
```

Crea un `.env` a partir de `.env.example` con tu `OPENROUTER_API_KEY`.

Añade el server a tu configuración MCP (Cursor, Claude Desktop, etc.):

```json
{
  "mcpServers": {
    "Running Coach Memory": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/running-coach-memory-mcp", "python", "-m", "memory_mcp.server"],
      "env": {
        "OPENROUTER_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

#### 3. Agents y Skills

Copia los agents y skills del repositorio a las rutas correspondientes de tu entorno (`~/.claude/agents/`, `~/.claude/skills/`, etc.).

## License

MIT
