# Pipeline 与 Cron

Pipeline 串联多个 Execution，支持通过 cron 定时调度执行。

---

## 概述

**Pipeline** 按顺序运行一系列 Execution，`data_chain` 在所有 Execution 间传递。Pipeline 可以手动触发、通过 HTTP API 触发或按 cron 定时执行。

---

## Cron 设置（GUI）

1. 切换到 GUI 的 **Pipelines** 标签页
2. 选择或创建一个 Pipeline
3. 勾选 **as cron** → 输入 cron 表达式（如 `0 9 * * 1-5`）
4. 点击 **Execute** — 按计划运行，直到通过 **Stop** / **Stop All** 停止

cron 输入框的悬浮提示显示人类可读的描述（如 "At 09:00 AM, Monday through Friday"）。

---

## Pipeline YAML 格式

```yaml
!!python/object:core.pipeline.Pipeline
pipeline: DAILY_REPORT
cronEnabled: true
cronExp: 0 9 * * 1-5
cronDesc: At 09:00 AM, Monday through Friday
list:
- execution: fetch_data
  input: ''
- execution: generate_report
  input: ''
- execution: send_email
  input: '{"to":"team@example.com"}'
```

| 字段 | 说明 |
|------|------|
| `pipeline` | Pipeline 名称（唯一标识符） |
| `cronEnabled` | `true` 激活 cron 调度 |
| `cronExp` | 标准 5 字段 cron 表达式 |
| `cronDesc` | 自动生成的人类可读描述 |
| `list` | 按顺序排列的 Execution 列表，可带可选的 `input` JSON |

---

## 运行 Pipeline

```bash
# GUI — 通过复选框 + cron 表达式输入管理，持久化到 YAML

# 后台 — 运行一次 Pipeline
python PETP_background.py --run-pipeline DAILY_REPORT --no-http

# 后台 — 带初始数据运行
python PETP_background.py --run-pipeline DAILY_REPORT --init-data '{"to":"ops@example.com"}' --no-http

# 后台 — 持久 HTTP 服务（通过 POST /petp/exec 触发 Pipeline）
python PETP_background.py

# Docker
docker run --rm -p 8866:8866 petp-background:amd64-local
# 然后：POST http://localhost:8866/petp/exec  {"action":"pipeline","params":{"pipeline":"DAILY_REPORT"},"wait_for_result":"true"}
```

---

## Cron 架构

`Cron` 类（`core/cron/cron.py`）管理 Pipeline 的定时执行：

- **Worker 线程**：从待处理队列弹出任务，按 Pipeline 键去重
- **每 Pipeline 线程**：等待下一个 cron 触发时刻，然后执行
- **线程安全**：所有共享状态由 `threading.Lock` 保护；`threading.Event` 替代 sleep 轮询
- **去重**：如果键已在运行中或待处理队列中则拒绝
- **停止**：`stop_one()` / `stop_all()` 清除状态并 join 所有线程确保干净关闭
- **自动重试**：捕获异常以在单次失败后继续运行
