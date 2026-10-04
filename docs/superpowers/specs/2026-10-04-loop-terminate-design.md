# Loop 出错处理增强:新增 `terminate` 行为

- 日期:2026-10-04
- 范围:PETP 执行引擎的循环(Loop)控制流
- 类型:架构级增强(跨多个核心文件,改变 loop 语义)

## 1. 背景与意图

现有 loop 的出错处理只有 `exception_then` 两个取值:

| 取值 | 当前行为 |
|------|----------|
| `continue` | loop 内 task 抛异常 → 跳到下一次迭代 |
| `break` | loop 内 task 抛异常 → 退出 loop,**继续执行 loop 之后的 task** |

另有 `loop_condition`(每次迭代末尾求值)可返回 `(True,'break')` / `(True,'continue')` 做编程式控制。

**本次新增第三种行为 `terminate`**:退出循环并**立即终结整个 execution**,不再执行 loop 之后的 task,且支持自定义 `terminate_msg`。

关键区别:现有 `break` 退出循环后 execution **继续往下走**;`terminate` 则**直接结束整个 execution 并以失败告知调用方**。

## 2. 设计决策(已与用户对齐)

1. **终结方式 = 抛异常**。`terminate` 时 `raise` 一个自定义异常(携带 `terminate_msg`),`Execution.run()` 不捕获,直接向上抛。调用方(HTTP `/petp/exec`、MCP、`BackgroundRuntime`)按失败处理。语义最清晰:出错就是出错。
   - 不复用现有 `__end_execution` 机制 —— 后者走 `break` + 正常 `return data_chain`,调用方视为**成功**,无法区分"出错终结"。两套机制并存、互不干扰。

2. **复用 `exception_then` 字段**。在现有字段上新增取值 `terminate`(`continue`/`break` 不变),再新增一个 `terminate_msg` 字段存自定义消息。改动最小,向后兼容。

3. **两条路径都支持 terminate**:
   - 路径 A:loop 内 task 抛异常 + `exception_then == 'terminate'`
   - 路径 B:`loop_condition` 返回 `(True, 'terminate')`(主动终结,非出错)

4. **`terminate_msg` 支持表达式**(f-string against `data_chain`,与其他参数一致)。为空时自动生成默认消息:带 loop_code + task 序号 + 原始异常信息。

5. **GUI 旧 loop 自动补齐 schema**:`LoopEditDialog` 打开时用 `Loop.tpl()` 补齐缺失的 key,旧 loop 也能直接编辑出 `terminate_msg`。

6. **异常类放 `core/loop.py`**(离 Loop 最近,import 简单)。

## 3. 控制流

### 路径 A — task 抛异常(`exception_then=terminate`)
```
task 抛异常
  → exception_then == 'terminate'
  → 记录日志 + task.end + log_end_process(与现有 continue/break 一致)
  → 求值 terminate_msg(表达式),为空则拼默认消息
  → raise LoopTerminateError(msg)     ← run() 不捕获,向上抛
```

### 路径 B — loop_condition 返回 terminate
```
loop_condition 返回 (True, 'terminate')
  → _eval_loop_condition 返回 'terminate'
  → 求值 terminate_msg,为空则拼默认消息
  → raise LoopTerminateError(msg)
```

### 调用方如何感知
- `BackgroundRuntime.run_execution()`:外层已有 `try/except Exception`,会捕获 `LoopTerminateError` 并返回 `{"ok": False, "error": msg, ...}` —— 自然变成一次失败返回,无需特殊分支。
- GUI 模式:异常冒泡到 `Executor.run()` 的错误处理(触发 AI 错误分析那套),与真实出错路径一致。

## 4. 具体改动点

### 4.1 `core/loop.py`
- 新增异常类:
  ```python
  class LoopTerminateError(Exception):
      """Raised when a loop's exception_then='terminate' or loop_condition
      returns (True,'terminate'): exit the loop and terminate the whole execution."""
  ```
- `tpl()`:JSON 模板加 `"terminate_msg":""`;`exception_then` 注释补 `"terminate"` 说明。
- 新增 `get_terminate_msg()` → `self.get_attributes().get('terminate_msg', '')`(兜底空串,向后兼容)。

### 4.2 `core/execution.py`

**改动点 1 — task 异常块(约第 131–150 行)**
- `exception_policy in ('continue', 'break')` → 改为 `in ('continue', 'break', 'terminate')`
- except 内 `log_end_process` 之后、分支判断处加:
  ```python
  if exception_policy == 'terminate':
      raise LoopTerminateError(self._build_terminate_msg(current_loop, processor, state, data_chain, e))
  ```

**改动点 2 — `_eval_loop_condition` 消费处(约第 159–169 行)**
- 加:
  ```python
  elif cond_action == 'terminate':
      raise LoopTerminateError(self._build_terminate_msg(current_loop, processor, state, data_chain, None))
  ```

**改动点 3 — `_eval_loop_condition` 放宽(约第 209 行)**
- `return action if action in ('break', 'continue') else 'break'`
- → `return action if action in ('break', 'continue', 'terminate') else 'break'`

**改动点 4 — 新增私有方法 `_build_terminate_msg`**
- 用 `processor.expression2str(terminate_msg)` 求值(支持 f-string);为空时拼默认消息
  `f"Loop [{loop_code}] terminated at task {seq}"` +(若有原始异常)`": {exc}"`。

### 4.3 `core/runtime/BackgroundRuntime.py`
- 镜像 4.2 的改动点 1、2、3(循环逻辑是 execution.py 的逐行复制)。
- 外层 `try/except Exception`(约第 203 行)已能捕获 `LoopTerminateError` → 返回 `ok=False`,无需额外分支。
- `_build_terminate_msg` 复用 `Execution` 上的静态/实例方法,避免重复实现。

### 4.4 `mvp/view/common/LoopEditDialog.py`
- `__init__` 解析 `loop_attributes_json` 后,用 `Loop.tpl()` 的模板 dict 补齐 `self._data` 缺失的 key(模板有、data 无 → 补默认值)。
- `_KEY_TIPS` 加 `'terminate_msg': 'loop_tip_terminate_msg'`。
- **副作用(可接受)**:旧 loop 被打开编辑并保存后,JSON 会补全所有 tpl 字段(schema 向前对齐)。

### 4.5 `i18n/translations.py`
- `loop_tip_exception_then` 补 `terminate` 说明。
- 新增 `loop_tip_terminate_msg`(en + zh)。

### 4.6 portable 同步
- 改完主仓后跑 `python portable/sync_portable.py` 同步到 `portable/`(不手改 portable 文件)。

## 5. 表达式求值上下文

`_build_terminate_msg` 对 `terminate_msg` 做 f-string 求值,复用**当前 `processor` 实例**的 `expression2str()`:
- task 异常路径:`processor` 是刚抛异常的 task 的 processor,data_chain 已挂上 → 可用。
- loop_condition 路径:`processor` 指向刚跑完的 task 的 processor,data_chain 已更新 → 可用。
- 两份实现(main + BG)均在循环内持有 `processor`,传入即可。

## 6. 测试与验证策略

纯引擎控制流,不依赖 GUI/浏览器,用 headless 真实验证。

### 测试脚本:`testcoverage/loop_terminate_smoke.py`
内存构造测试专用 `Execution`(构造 `Loop`/`Task` 对象,**不写磁盘业务 YAML**,不违反 GUI-only 约束),覆盖四条路径:

1. **task 异常 + terminate** → `Execution.run()` 抛 `LoopTerminateError`,消息含 terminate_msg。
2. **loop_condition 返回 terminate** → 同样抛异常。
3. **terminate_msg 表达式求值** → `"失败 {loop_item}"` 正确插值。
4. **向后兼容** → 旧 loop(`exception_then=break`,无 `terminate_msg`)行为不变。

### 双实现一致性
同一脚本**同时**跑 `Execution.run()` 与 `BackgroundRuntime.run_execution()`,断言两者行为一致(本次最大回归风险点:后者返回 `ok=False` 且 `error` 含消息)。

脚本保留进 `testcoverage/`(与 `nogui_smoke.py` 同级),可长期回归。

## 7. 向后兼容

- 旧 YAML loop 没有 `terminate_msg` key → `get_terminate_msg()` 兜底空串。
- 旧 `exception_then=continue/break` 行为完全不变。
- `_eval_loop_condition` 对未知 action 仍归为 `break`(原行为),只额外放行 `terminate`。
- 不触碰 `__end_execution` / `__goto_task` 等现有早停/跳转机制。

## 8. 不在本次范围

- 不给 `exception_then` 以外的 task 级(非 loop)异常处理加 terminate —— 仅限 loop 作用域。
- 不改 pipeline 层的跨 execution 终结语义。
