# Hyperspace LLM 使用方式（通用参考）

> 一份可直接搬到任何项目的 Hyperspace LLM 调用指南。**零依赖**（只需 `requests` 或 `httpx`）。

**官方文档**：<https://ai-docs.portal.hyperspace.tools.sap/llm-proxy/configuration/api-endpoints/>

---

## 一、核心事实

只需记住 4 件事就能开始使用：

1. **Hyperspace 是本地 HTTP 代理**，默认地址 `http://localhost:6655/anthropic/v1`
2. **协议 100% 兼容 Anthropic `/messages`**，可以完全按 Anthropic 官方文档写代码
3. **认证方式**：`Authorization: Bearer <API_KEY>`
4. **模型名必须带前缀** `anthropic--`，例如 `anthropic--claude-sonnet-latest`

---

## 二、前置条件

1. 安装 **Hyperspace AI 桌面应用**并登录
2. 桌面应用后台运行（代理监听 `localhost:6655`）
3. 从 **桌面应用 → Settings → API Key** 复制 Key

---

## 三、请求格式

### 端点

```
POST http://localhost:6655/anthropic/v1/messages
```

### 请求头

```
Authorization: Bearer <YOUR_API_KEY>
Content-Type: application/json
```

### 请求 Body（Anthropic 标准格式）

```json
{
  "model": "anthropic--claude-sonnet-latest",
  "max_tokens": 1024,
  "system": "你是一个助手",
  "messages": [
    {"role": "user", "content": "你好"}
  ]
}
```

**必填字段**：`model`、`max_tokens`、`messages`
**可选字段**：`system`、`tools`、`temperature`、`stream`、`stop_sequences`、`tool_choice`

### 响应格式

```json
{
  "id": "msg_xxx",
  "type": "message",
  "role": "assistant",
  "content": [
    {"type": "text", "text": "你好！有什么可以帮你？"}
  ],
  "model": "anthropic--claude-sonnet-latest",
  "stop_reason": "end_turn",
  "usage": {"input_tokens": 12, "output_tokens": 18}
}
```

---

## 四、可用模型

| 模型名 | 场景 |
|--------|------|
| `anthropic--claude-opus-latest` | 复杂推理、长链工具调用 |
| `anthropic--claude-sonnet-latest` | 通用场景（推荐默认） |
| `anthropic--claude-haiku-latest` | 快速分类、简单摘要、便宜 |
| `anthropic--claude-4.6-sonnet` | 固定版本（生产环境推荐锁定） |

---

## 五、最小可运行示例

### Python（用 `requests`）

```python
import os
import requests

def call_hyperspace(messages, model="anthropic--claude-sonnet-latest",
                    system=None, tools=None, max_tokens=1024):
    """
    调用 Hyperspace LLM 代理，返回完整的 Anthropic 响应 dict。
    """
    url = os.environ.get("HYPERSPACE_BASE_URL",
                         "http://localhost:6655/anthropic/v1") + "/messages"
    api_key = os.environ["HYPERSPACE_API_KEY"]

    body = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": messages,
    }
    if system:
        body["system"] = system
    if tools:
        body["tools"] = tools

    resp = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=body,
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()


# 使用示例
result = call_hyperspace(
    messages=[{"role": "user", "content": "写一句问候"}],
    system="你是助手",
)
print(result["content"][0]["text"])
```

### Python（用 `httpx` 异步）

```python
import os
import httpx

async def call_hyperspace_async(messages, model="anthropic--claude-sonnet-latest",
                                 system=None, max_tokens=1024):
    url = os.environ.get("HYPERSPACE_BASE_URL",
                         "http://localhost:6655/anthropic/v1") + "/messages"
    body = {"model": model, "max_tokens": max_tokens, "messages": messages}
    if system:
        body["system"] = system

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            url,
            headers={
                "Authorization": f"Bearer {os.environ['HYPERSPACE_API_KEY']}",
                "Content-Type": "application/json",
            },
            json=body,
        )
        resp.raise_for_status()
        return resp.json()
```

### curl 验证连通性

```bash
curl -X POST http://localhost:6655/anthropic/v1/messages \
  -H "Authorization: Bearer $HYPERSPACE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "anthropic--claude-sonnet-latest",
    "max_tokens": 100,
    "messages": [{"role": "user", "content": "Hi"}]
  }'
```

### Node.js（用 `fetch`）

```javascript
async function callHyperspace({ messages, model = "anthropic--claude-sonnet-latest",
                                 system, maxTokens = 1024 }) {
  const baseUrl = process.env.HYPERSPACE_BASE_URL
                  || "http://localhost:6655/anthropic/v1";
  const body = { model, max_tokens: maxTokens, messages };
  if (system) body.system = system;

  const resp = await fetch(`${baseUrl}/messages`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${process.env.HYPERSPACE_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });
  if (!resp.ok) throw new Error(`Hyperspace error: ${resp.status}`);
  return await resp.json();
}
```

---

## 六、环境变量约定

推荐用 4 个环境变量管理配置：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `HYPERSPACE_BASE_URL` | `http://localhost:6655/anthropic/v1` | 代理 URL |
| `HYPERSPACE_API_KEY` | *(必填)* | 从桌面应用复制 |
| `HYPERSPACE_MODEL` | `anthropic--claude-sonnet-latest` | 默认模型 |
| `HYPERSPACE_TIMEOUT` | `60` | 秒 |

`.env` 示例：

```env
HYPERSPACE_BASE_URL=http://localhost:6655/anthropic/v1
HYPERSPACE_API_KEY=你的-api-key
HYPERSPACE_MODEL=anthropic--claude-sonnet-latest
```

---

## 七、常见调用场景

### 场景 1：单轮对话

```python
messages = [{"role": "user", "content": "什么是 PR？"}]
result = call_hyperspace(messages)
```

### 场景 2：带 System Prompt 的多轮对话

```python
messages = [
    {"role": "user", "content": "PR 是什么？"},
    {"role": "assistant", "content": "PR 是采购申请..."},
    {"role": "user", "content": "如何创建？"},
]
result = call_hyperspace(messages, system="你是 SAP 专家")
```

### 场景 3：工具调用（Function Calling）

```python
tools = [{
    "name": "query_pr",
    "description": "查询采购申请状态",
    "input_schema": {
        "type": "object",
        "properties": {"pr_id": {"type": "string"}},
        "required": ["pr_id"],
    },
}]

result = call_hyperspace(
    messages=[{"role": "user", "content": "查PR12345的状态"}],
    tools=tools,
)

# 判断是否需要执行工具
if result["stop_reason"] == "tool_use":
    for block in result["content"]:
        if block["type"] == "tool_use":
            tool_name = block["name"]   # "query_pr"
            tool_input = block["input"] # {"pr_id": "PR12345"}
            tool_id = block["id"]
            # → 执行工具，把结果加回 messages 继续调用
```

### 场景 4：强制结构化输出（`tool_choice`）

```python
result = call_hyperspace(
    messages=[{"role": "user", "content": "分类：我要买笔"}],
    tools=[{
        "name": "classify",
        "input_schema": {
            "type": "object",
            "properties": {
                "category": {"type": "string",
                             "enum": ["sourcing", "procurement"]}
            },
            "required": ["category"],
        },
    }],
    # 关键：强制返回工具调用
)

# 手动加 tool_choice（上面的 call_hyperspace 没暴露这个参数时）
# body["tool_choice"] = {"type": "tool", "name": "classify"}
```

### 场景 5：完整工具调用循环（ReAct）

```python
def run_agent_loop(user_message, tools, tool_handlers, max_iter=10):
    messages = [{"role": "user", "content": user_message}]

    for _ in range(max_iter):
        result = call_hyperspace(messages, tools=tools)

        # 把 assistant 响应加入历史
        messages.append({"role": "assistant", "content": result["content"]})

        if result["stop_reason"] != "tool_use":
            # 提取文本返回
            return "".join(b["text"] for b in result["content"]
                           if b["type"] == "text")

        # 执行所有工具调用
        tool_results = []
        for block in result["content"]:
            if block["type"] == "tool_use":
                handler = tool_handlers[block["name"]]
                output = handler(block["input"])
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block["id"],
                    "content": str(output),
                })
        messages.append({"role": "user", "content": tool_results})

    return "达到最大迭代次数"
```

### 场景 6：流式响应（SSE）

```python
import json
import requests

def stream_hyperspace(messages, model="anthropic--claude-sonnet-latest"):
    url = "http://localhost:6655/anthropic/v1/messages"
    body = {
        "model": model,
        "max_tokens": 1024,
        "messages": messages,
        "stream": True,
    }
    with requests.post(url, headers={
        "Authorization": f"Bearer {os.environ['HYPERSPACE_API_KEY']}",
        "Content-Type": "application/json",
    }, json=body, stream=True, timeout=60) as resp:
        for line in resp.iter_lines():
            if line and line.startswith(b"data: "):
                event = json.loads(line[6:])
                if event.get("type") == "content_block_delta":
                    yield event["delta"].get("text", "")
```

---

## 八、关键字段速查

### 请求 Body 字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `model` | string | ✅ | 带 `anthropic--` 前缀 |
| `max_tokens` | int | ✅ | 单次响应上限 |
| `messages` | array | ✅ | `{role, content}` 数组 |
| `system` | string | | 顶层字段，不放 messages 里 |
| `temperature` | float | | 0.0~1.0，默认 1.0 |
| `tools` | array | | 工具定义 |
| `tool_choice` | object | | `{"type": "auto"/"any"/"tool", "name": "..."}` |
| `stream` | bool | | 流式响应 |
| `stop_sequences` | array | | 停止字符串 |

### Message content 三种格式

```python
# 1. 简单文本
{"role": "user", "content": "你好"}

# 2. 多个 block（工具调用响应必用）
{"role": "assistant", "content": [
    {"type": "text", "text": "让我查一下"},
    {"type": "tool_use", "id": "toolu_xxx", "name": "query", "input": {...}}
]}

# 3. 工具结果（作为 user 消息发回）
{"role": "user", "content": [
    {"type": "tool_result", "tool_use_id": "toolu_xxx", "content": "结果字符串"}
]}
```

### `stop_reason` 取值

| 值 | 含义 |
|----|------|
| `end_turn` | 正常完成 |
| `tool_use` | 请求调用工具（需回喂结果） |
| `max_tokens` | 达到 token 上限 |
| `stop_sequence` | 命中 stop_sequences |

---

## 九、故障排查

| 症状 | 原因 | 解决 |
|------|------|------|
| Connection refused | 桌面应用未启动 | 打开 Hyperspace 桌面应用 |
| 401 Unauthorized | API Key 错误/过期 | 重新从桌面应用复制 Key |
| `model not found` | 忘加 `anthropic--` 前缀 | 用 `anthropic--claude-sonnet-latest` |
| 超时 | 大模型 + 复杂任务 | 增大 timeout（如 120s） |
| `max_tokens is required` | 忘传 max_tokens | 必填字段 |

---

## 十、迁移到官方 Anthropic API

代码结构完全一致，只需改 3 处：

| | Hyperspace | 官方 Anthropic |
|---|-----------|--------------|
| Base URL | `http://localhost:6655/anthropic/v1` | `https://api.anthropic.com/v1` |
| 认证头 | `Authorization: Bearer <key>` | `x-api-key: <key>` |
| 模型名 | `anthropic--claude-sonnet-latest` | `claude-sonnet-latest` |
| 额外头 | 无 | 需加 `anthropic-version: 2023-06-01` |

Body / Response schema 完全相同，业务代码零改动。

---

## 十一、最小可移植封装（推荐直接复制）

粘贴到任何 Python 项目即可使用，只依赖 `requests`：

```python
"""hyperspace_client.py — 单文件、零依赖（除 requests）的 Hyperspace 客户端。"""
import os
import requests
from typing import Any


class HyperspaceClient:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout: int = 60,
    ):
        self.api_key = api_key or os.environ["HYPERSPACE_API_KEY"]
        self.base_url = (base_url or os.environ.get(
            "HYPERSPACE_BASE_URL", "http://localhost:6655/anthropic/v1"
        )).rstrip("/")
        self.model = model or os.environ.get(
            "HYPERSPACE_MODEL", "anthropic--claude-sonnet-latest"
        )
        self.timeout = timeout

    def send(self, **body: Any) -> dict[str, Any]:
        """
        直接透传 Anthropic /messages body。
        自动注入默认 model 和 max_tokens。
        """
        body.setdefault("model", self.model)
        body.setdefault("max_tokens", 1024)

        resp = requests.post(
            f"{self.base_url}/messages",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json=body,
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()

    def text(self, prompt: str, system: str | None = None, **kwargs) -> str:
        """快捷方法：直接返回文本响应。"""
        body = {"messages": [{"role": "user", "content": prompt}], **kwargs}
        if system:
            body["system"] = system
        resp = self.send(**body)
        return "".join(b["text"] for b in resp["content"] if b["type"] == "text")


# 使用
if __name__ == "__main__":
    client = HyperspaceClient()
    print(client.text("用一句话介绍 SAP Ariba"))
```

---

## 附录：核对清单

复制到新项目后，检查这些点即可跑通：

- [ ] 安装依赖：`pip install requests`（或 `httpx`）
- [ ] 设置 `HYPERSPACE_API_KEY` 环境变量
- [ ] 启动 Hyperspace 桌面应用
- [ ] `curl` 验证 `localhost:6655` 可达
- [ ] 模型名带 `anthropic--` 前缀
- [ ] 请求 body 包含 `model`、`max_tokens`、`messages` 三个必填字段
- [ ] 认证头用 `Authorization: Bearer`（不是 `x-api-key`）

---

*版本：v1.0 · 通用参考 · 可自由复制到任何项目*
