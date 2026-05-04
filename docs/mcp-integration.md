# MCP & HTTP API

Full reference for PETP's built-in HTTP server and MCP Tool Server.

---

## Overview

PETP includes a built-in HTTP server on port **8866** that exposes:
- A standard **MCP Tool Server** via Streamable-HTTP
- A REST API for triggering executions and pipelines

---

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/mcp` | GET, POST | MCP Tool Server (Streamable-HTTP, JSON-RPC 2.0) |
| `/petp/tools` | GET | List executions exposed as MCP tools |
| `/petp/exec` | POST | Trigger an execution or pipeline |
| `/petp/result?request_id=<id>` | GET | Poll async result |

---

## MCP Client Configuration

**Claude Code / Cursor / any MCP client:**

```json
{
  "mcpServers": {
    "petp": {
      "type": "http",
      "url": "http://localhost:8866/mcp"
    }
  }
}
```

**MCP Inspector:**

Transport Type = **Streamable HTTP**, URL = `http://localhost:8866/mcp`

---

## HTTP API Examples

```bash
# List available tools
curl http://localhost:8866/petp/tools

# Trigger execution (synchronous, wait for result)
curl -X POST http://localhost:8866/petp/exec \
  -H "Content-Type: application/json" \
  -d '{"action":"execution","params":{"execution":"MY_EXEC"},"wait_for_result":"true"}'

# Trigger execution (async, returns request_id)
curl -X POST http://localhost:8866/petp/exec \
  -H "Content-Type: application/json" \
  -d '{"action":"execution","params":{"execution":"MY_EXEC"},"wait_for_result":"false"}'

# Poll async result
curl http://localhost:8866/petp/result?request_id=<id>

# Trigger pipeline
curl -X POST http://localhost:8866/petp/exec \
  -H "Content-Type: application/json" \
  -d '{"action":"pipeline","params":{"pipeline":"DAILY_REPORT"},"wait_for_result":"true"}'
```

---

## Authentication

When `http_request_token` is configured in `petpconfig.yaml`, all API calls require a Bearer token:

```bash
curl -H "Authorization: Bearer <token>" http://localhost:8866/petp/tools
```

---

## MCP Tool Schema

An Execution is exposed as an MCP tool when its YAML has `astool: true` and a `mcp_desc` JSON field:

```yaml
astool: true
mcp_desc: '{"desc":"Tool description", "params":["param1","param2"], "outParams":["result"]}'
```

| Field | Description |
|-------|-------------|
| `desc` | Tool description shown to MCP clients |
| `params` | Input parameter names (become `inputSchema` properties) |
| `outParams` | Output field names (become `outputSchema` properties) |

The `mcp_desc.inputSchema` is defined at the **Execution level**. If the first task is `INITIAL_PARAMS`, its keys represent the Execution's external inputs. Use `McpDescEditor` in the GUI to edit the schema visually.

---

## Docker Container Endpoints

When running in Docker, all endpoints above are available. Docker auto-enables headless mode.

```bash
docker run --rm -p 8866:8866 petp-background:amd64-local

# Trigger via HTTP
curl -X POST http://localhost:8866/petp/exec \
  -H "Content-Type: application/json" \
  -d '{"action":"execution","params":{"execution":"MY_EXEC"},"wait_for_result":"true"}'
```
