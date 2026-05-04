# MCP 与 HTTP API

PETP 内置 HTTP 服务器和 MCP 工具服务器的完整参考。

---

## 概述

PETP 内置的 HTTP 服务器运行在端口 **8866**，提供：
- 标准 **MCP 工具服务器**（Streamable-HTTP）
- REST API，用于触发 Execution 和 Pipeline

---

## 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/mcp` | GET, POST | MCP 工具服务器（Streamable-HTTP，JSON-RPC 2.0） |
| `/petp/tools` | GET | 列出暴露为 MCP 工具的 Execution |
| `/petp/exec` | POST | 触发 Execution 或 Pipeline |
| `/petp/result?request_id=<id>` | GET | 轮询异步结果 |

---

## MCP 客户端配置

**Claude Code / Cursor / 任何 MCP 客户端：**

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

**MCP Inspector：**

Transport Type = **Streamable HTTP**，URL = `http://localhost:8866/mcp`

---

## HTTP API 示例

```bash
# 列出可用工具
curl http://localhost:8866/petp/tools

# 触发 Execution（同步，等待结果）
curl -X POST http://localhost:8866/petp/exec \
  -H "Content-Type: application/json" \
  -d '{"action":"execution","params":{"execution":"MY_EXEC"},"wait_for_result":"true"}'

# 触发 Execution（异步，返回 request_id）
curl -X POST http://localhost:8866/petp/exec \
  -H "Content-Type: application/json" \
  -d '{"action":"execution","params":{"execution":"MY_EXEC"},"wait_for_result":"false"}'

# 轮询异步结果
curl http://localhost:8866/petp/result?request_id=<id>

# 触发 Pipeline
curl -X POST http://localhost:8866/petp/exec \
  -H "Content-Type: application/json" \
  -d '{"action":"pipeline","params":{"pipeline":"DAILY_REPORT"},"wait_for_result":"true"}'
```

---

## 认证

当 `petpconfig.yaml` 中配置了 `http_request_token` 时，所有 API 调用需要 Bearer 令牌：

```bash
curl -H "Authorization: Bearer <token>" http://localhost:8866/petp/tools
```

---

## MCP 工具 Schema

当 Execution 的 YAML 中设置 `astool: true` 和 `mcp_desc` JSON 字段时，该 Execution 会作为 MCP 工具暴露：

```yaml
astool: true
mcp_desc: '{"desc":"工具描述", "params":["param1","param2"], "outParams":["result"]}'
```

| 字段 | 说明 |
|------|------|
| `desc` | 工具描述，展示给 MCP 客户端 |
| `params` | 输入参数名（成为 `inputSchema` 属性） |
| `outParams` | 输出字段名（成为 `outputSchema` 属性） |

`mcp_desc.inputSchema` 定义在 **Execution 级别**。如果第一个任务是 `INITIAL_PARAMS`，其键代表 Execution 的外部输入。可在 GUI 中使用 `McpDescEditor` 可视化编辑 Schema。

---

## Docker 容器端点

在 Docker 中运行时，以上所有端点均可用。Docker 自动启用无头模式。

```bash
docker run --rm -p 8866:8866 petp-background:amd64-local

# 通过 HTTP 触发
curl -X POST http://localhost:8866/petp/exec \
  -H "Content-Type: application/json" \
  -d '{"action":"execution","params":{"execution":"MY_EXEC"},"wait_for_result":"true"}'
```
