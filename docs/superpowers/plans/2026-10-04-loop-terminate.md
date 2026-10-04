# Loop `terminate` 行为增强 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 给 PETP loop 新增第三种出错/控制行为 `terminate`——退出循环并抛异常终结整个 execution,支持自定义 `terminate_msg`。

**Architecture:** 复用 `exception_then` 字段新增取值 `terminate`,新增 `terminate_msg` 字段。两条触发路径(task 抛异常 / loop_condition 返回 terminate)都 `raise LoopTerminateError`。`Execution.run()` 不捕获直接向上抛;`BackgroundRuntime` 外层已有的 `try/except` 会把它变成 `ok=False` 返回。循环逻辑在 `core/execution.py` 和 `core/runtime/BackgroundRuntime.py` 有两份镜像实现,必须同步改。

**Tech Stack:** Python 3.12+、pytest 9.x、wxPython(GUI)、PyYAML。

**Spec:** `docs/superpowers/specs/2026-10-04-loop-terminate-design.md`

## Global Constraints

- **Execution YAML 文件只能通过 PETP GUI 编辑**,实现与测试中**不得直接新建/修改 `core/executions/*.yaml` 或 `portable/core/executions/*.yaml`** 业务文件。测试用内存构造的 `Execution`/`Loop`/`Task` 对象。
- **portable/ 目录不手改**——主仓改完后用 `python portable/sync_portable.py` 同步。
- **不自动 git commit**——每个 Task 末尾的 commit 步骤由执行者按需执行;最终是否推送由用户决定(项目规则 #5)。本计划的 commit 步骤默认执行(本地提交),但**不 push**。
- 参数命名:`snake_case`;新字段名 `terminate_msg`(非 `terminateMsg`/`terminate_message`)。
- 向后兼容:旧 loop 无 `terminate_msg` key 时 `get_terminate_msg()` 兜底返回空串;旧 `exception_then=continue/break` 行为完全不变。
- 新异常类 `LoopTerminateError` 放 `core/loop.py`。
- `terminate_msg` 支持 f-string 表达式(走 `Processor.expression2str`),为空时拼默认消息。
- i18n:所有新增用户可见字符串进 `i18n/translations.py`(en + zh)。

## Review Focus

- **`exception_then` 为未知值(拼写错误如 `terminat`)**:应回退到现有默认(不进入 continue/break/terminate 分支,异常照常抛出到外层),不得静默吞掉。→ Task 2 测试覆盖。
- **`loop_condition` 返回 `(True, 'terminate')` 但 loop 未配 `terminate_msg`**:应抛 `LoopTerminateError` 且消息为默认消息(含 loop_code + task 序号),不得抛 KeyError。→ Task 2 测试覆盖。
- **`terminate_msg` 表达式引用了 data_chain 不存在的变量**:f-string 求值失败时应兜底返回原始模板串(复用 `expression2str` 既有兜底),不得让 terminate 本身崩成另一种异常。→ Task 4 测试覆盖。
- **两份实现(main `Execution.run()` vs `BackgroundRuntime`)行为分叉**:同一 loop 配置在两边必须一致(main 抛异常、BG 返回 `ok=False` 且 error 含同样消息)。→ Task 5 测试并行断言两边。
- **旧 loop 在 GUI 打开后字段补齐的副作用**:`LoopEditDialog` 补齐 schema 不得丢失旧 loop 已有的值,也不得改变 `exception_then` 等现有字段的值。→ Task 6 测试覆盖。

---

## File Structure

| 文件 | 职责 | 操作 |
|------|------|------|
| `core/loop.py` | Loop 数据类 + 新异常类 + tpl/getter | Modify |
| `core/execution.py` | main 执行循环:terminate 两条路径 + `_build_terminate_msg` | Modify |
| `core/runtime/BackgroundRuntime.py` | 镜像执行循环:terminate 两条路径 | Modify |
| `mvp/view/common/LoopEditDialog.py` | GUI loop 编辑器:补齐 schema + tip 映射 | Modify |
| `i18n/translations.py` | `loop_tip_exception_then` 更新 + 新增 `loop_tip_terminate_msg` | Modify |
| `testcoverage/test_loop_terminate.py` | 本功能全部 pytest 用例 | Create |
| `portable/*` | 主仓镜像 | 由 sync 脚本生成,不手改 |

---

## Task 1: Loop 新字段、异常类与 getter

**Files:**
- Modify: `core/loop.py`
- Test: `testcoverage/test_loop_terminate.py`

**Interfaces:**
- Produces:
  - `class LoopTerminateError(Exception)` — 在 `core/loop.py`
  - `Loop.get_terminate_msg() -> str` — 兜底空串
  - `Loop.tpl()` 返回的 JSON 含 `"terminate_msg":""`

- [ ] **Step 1: 写失败测试**

创建 `testcoverage/test_loop_terminate.py`:

```python
"""Tests for loop terminate behavior (exception_then=terminate / loop_condition terminate)."""

import json

import pytest

from core.loop import Loop, LoopTerminateError


class TestLoopTerminateSchema:

    def test_terminate_error_is_exception(self):
        assert issubclass(LoopTerminateError, Exception)

    def test_tpl_contains_terminate_msg(self):
        tpl = json.loads(Loop.tpl())
        assert "terminate_msg" in tpl
        assert tpl["terminate_msg"] == ""

    def test_get_terminate_msg_present(self, make_loop):
        loop = make_loop(terminate_msg="boom {loop_item}")
        assert loop.get_terminate_msg() == "boom {loop_item}"

    def test_get_terminate_msg_missing_defaults_empty(self):
        # 旧 loop:JSON 里没有 terminate_msg key
        loop = Loop("legacy", json.dumps({"task_start": 2, "task_end": 5}))
        assert loop.get_terminate_msg() == ""

    def test_get_exception_then_terminate(self, make_loop):
        assert make_loop(exception_then="terminate").get_exception_then() == "terminate"
```

- [ ] **Step 2: 运行测试,确认失败**

Run: `python -m pytest testcoverage/test_loop_terminate.py -v`
Expected: FAIL — `ImportError: cannot import name 'LoopTerminateError'` 以及 tpl 断言失败。

- [ ] **Step 3: 实现**

在 `core/loop.py` 顶部(`class Loop` 之前)加异常类:

```python
class LoopTerminateError(Exception):
    """Raised when a loop's exception_then='terminate' or loop_condition
    returns (True,'terminate'): exit the loop and terminate the whole execution."""
```

修改 `Loop.tpl()`——在返回的 JSON 串末尾(`loop_condition` 之后)加 `terminate_msg`,并更新 `exception_then` 注释:

```python
        # exception_then  - behaviour when a task inside the loop raises an exception:
        #                   "break" stops the loop (execution continues after the loop),
        #                   "continue" skips to the next iteration,
        #                   "terminate" exits the loop AND terminates the whole execution
        #                   (raises LoopTerminateError; caller treats it as a failure)
        # terminate_msg   - optional message (supports f-string against data_chain) raised
        #                   with LoopTerminateError when exception_then="terminate" or
        #                   loop_condition returns (True,'terminate'); empty → default message
        ...
        return '{"task_start":2, "task_end":5, "loop_key":"loop_list", "loop_times":"0", "loop_index_key":"loop_idx", "item_key":"loop_item", "exception_then":"break", "loop_condition":"", "terminate_msg":""}'
```

在 `get_loop_condition()` 之后加 getter:

```python
    def get_terminate_msg(self):
        return self.get_attributes().get('terminate_msg', '')
```

- [ ] **Step 4: 运行测试,确认通过**

Run: `python -m pytest testcoverage/test_loop_terminate.py -v`
Expected: PASS(5 passed)。

- [ ] **Step 5: 回归已有 loop 测试**

Run: `python -m pytest testcoverage/test_loop_state.py -v`
Expected: 全部 PASS(未破坏现有 schema)。

- [ ] **Step 6: Commit**

```bash
git add core/loop.py testcoverage/test_loop_terminate.py
git commit -m "feat(loop): add LoopTerminateError, terminate_msg field and getter"
```

---

## Task 2: `Execution.run()` — task 异常路径 terminate

**Files:**
- Modify: `core/execution.py`(task 异常块 ~131–150;新增 `_build_terminate_msg`)
- Test: `testcoverage/test_loop_terminate.py`

**Interfaces:**
- Consumes: `Loop.get_exception_then()`, `Loop.get_terminate_msg()`, `LoopTerminateError`(Task 1)
- Produces:
  - `Execution._build_terminate_msg(current_loop, processor, state, data_chain, exc) -> str`
  - `Execution.run()` 在 `exception_then=='terminate'` 时 `raise LoopTerminateError`

- [ ] **Step 1: 写失败测试**

在 `testcoverage/test_loop_terminate.py` 追加。用内存构造 `Execution`——一个 2-task loop,循环体内第 2 个 task 用 `READ_JSON` 读不存在的文件可靠抛异常:

```python
from threading import Condition

from core.execution import Execution
from core.task import Task
from core.loop import Loop


def _build_execution(loop_attrs, body_tasks):
    """内存构造一个 Execution:task1=INITIAL_PARAMS(建立 items),
    task2..=循环体。loop 覆盖 task 2..N。不写磁盘 YAML。"""
    tasks = [Task(type="INITIAL_PARAMS", input='{"items":["a","b","c"]}')]
    tasks.extend(body_tasks)
    loop = Loop("tloop", json.dumps(loop_attrs))
    ex = Execution(execution="__mem_terminate_test", list=tasks, mcp_desc="", astool=False, loops=[loop])
    return ex


class TestExecutionTerminateOnException:

    def test_task_exception_terminate_raises(self):
        # loop 覆盖 task 2(READ_JSON 读不存在文件 → 抛异常)
        loop_attrs = {
            "task_start": 2, "task_end": 2,
            "loop_key": "items", "loop_times": "0",
            "loop_index_key": "loop_idx", "item_key": "loop_item",
            "exception_then": "terminate",
            "loop_condition": "",
            "terminate_msg": "stopped at {loop_item}",
        }
        body = [Task(type="READ_JSON", input='{"file_path":"/no/such/file_xyz.json","data_key":"j"}')]
        ex = _build_execution(loop_attrs, body)
        with pytest.raises(LoopTerminateError) as ei:
            ex.run({}, Condition(), None)
        assert "stopped at a" in str(ei.value)  # 第一次迭代 loop_item='a'

    def test_task_exception_unknown_policy_propagates_original(self):
        # exception_then 拼错 → 不进入 terminate 分支,原始异常照常抛出(非 LoopTerminateError)
        loop_attrs = {
            "task_start": 2, "task_end": 2,
            "loop_key": "items", "loop_times": "0",
            "loop_index_key": "loop_idx", "item_key": "loop_item",
            "exception_then": "terminat",  # typo
            "loop_condition": "", "terminate_msg": "",
        }
        body = [Task(type="READ_JSON", input='{"file_path":"/no/such/file_xyz.json","data_key":"j"}')]
        ex = _build_execution(loop_attrs, body)
        with pytest.raises(Exception) as ei:
            ex.run({}, Condition(), None)
        assert not isinstance(ei.value, LoopTerminateError)

    def test_task_exception_terminate_empty_msg_uses_default(self):
        loop_attrs = {
            "task_start": 2, "task_end": 2,
            "loop_key": "items", "loop_times": "0",
            "loop_index_key": "loop_idx", "item_key": "loop_item",
            "exception_then": "terminate",
            "loop_condition": "", "terminate_msg": "",
        }
        body = [Task(type="READ_JSON", input='{"file_path":"/no/such/file_xyz.json","data_key":"j"}')]
        ex = _build_execution(loop_attrs, body)
        with pytest.raises(LoopTerminateError) as ei:
            ex.run({}, Condition(), None)
        msg = str(ei.value)
        assert "tloop" in msg          # 默认消息含 loop_code
        assert "task 2" in msg         # 含 task 序号
```

- [ ] **Step 2: 运行测试,确认失败**

Run: `python -m pytest testcoverage/test_loop_terminate.py::TestExecutionTerminateOnException -v`
Expected: FAIL — 现在 `exception_then='terminate'` 不在 `('continue','break')` 内,会走 `else` 分支直接 `do_process()` 抛原始异常(非 `LoopTerminateError`)。

- [ ] **Step 3: 实现**

在 `core/execution.py` 顶部 import 加入 `LoopTerminateError`:

```python
from core.loop import Loop, LoopTerminateError
```

task 异常块(当前 `if exception_policy in ('continue', 'break'):`)改为包含 `terminate`,并在 except 内 `log_end_process` 之后、`continue`/`break` 分支判断之前加 terminate 分支:

```python
                exception_policy = current_loop.get_exception_then() if current_loop else ''
                if exception_policy in ('continue', 'break', 'terminate'):
                    try:
                        processor.do_process()
                    except Exception as e:
                        logging.exception(
                            'Loop %s exception at task %s (policy=%s): %s',
                            current_loop.get_loop_code(), state.get_sequence(), exception_policy, e
                        )
                        task.end = DateUtil.get_now_in_str("%Y-%m-%d %H:%M:%S")
                        self.log_end_process(current_loop, state, processor, task, view, loop_cursor, proc_name)
                        if exception_policy == 'terminate':
                            raise LoopTerminateError(
                                self._build_terminate_msg(current_loop, processor, state, data_chain, e))
                        if exception_policy == 'continue':
                            if state.advance_loop_on_exception(data_chain):
                                continue
                            state.move_to_next()
                            continue
                        else:  # break
                            state.force_exit_loop(data_chain)
                            state.move_to_next()
                            continue
                else:
                    processor.do_process()
```

在 `_eval_loop_condition` 静态方法附近新增实例方法 `_build_terminate_msg`:

```python
    def _build_terminate_msg(self, current_loop, processor, state, data_chain, exc) -> str:
        raw = current_loop.get_terminate_msg() if current_loop else ''
        if raw:
            try:
                return processor.expression2str(raw)
            except Exception:
                return raw
        loop_code = current_loop.get_loop_code() if current_loop else ''
        base = f"Loop [{loop_code}] terminated at task {state.get_sequence()}"
        return f"{base}: {exc}" if exc is not None else base
```

- [ ] **Step 4: 运行测试,确认通过**

Run: `python -m pytest testcoverage/test_loop_terminate.py::TestExecutionTerminateOnException -v`
Expected: PASS(3 passed)。

- [ ] **Step 5: Commit**

```bash
git add core/execution.py testcoverage/test_loop_terminate.py
git commit -m "feat(loop): terminate execution when exception_then=terminate (main runtime)"
```

---

## Task 3: `Execution.run()` — loop_condition 路径 terminate

**Files:**
- Modify: `core/execution.py`(`_eval_loop_condition` ~209 放宽;消费处 ~159–169 加 terminate 分支)
- Test: `testcoverage/test_loop_terminate.py`

**Interfaces:**
- Consumes: `_build_terminate_msg`(Task 2)、`_eval_loop_condition`
- Produces: loop_condition 返回 `(True,'terminate')` 时 `Execution.run()` raise `LoopTerminateError`

- [ ] **Step 1: 写失败测试**

追加到 `testcoverage/test_loop_terminate.py`。循环体用 `INITIAL_PARAMS`(不抛异常),靠 loop_condition 在第一次迭代主动 terminate:

```python
class TestExecutionTerminateOnCondition:

    def test_loop_condition_terminate_raises(self):
        loop_attrs = {
            "task_start": 2, "task_end": 2,
            "loop_key": "items", "loop_times": "0",
            "loop_index_key": "loop_idx", "item_key": "loop_item",
            "exception_then": "",
            "loop_condition": "return True, 'terminate'",
            "terminate_msg": "cond stop {loop_item}",
        }
        body = [Task(type="INITIAL_PARAMS", input='{"noop":"1"}')]
        ex = _build_execution(loop_attrs, body)
        with pytest.raises(LoopTerminateError) as ei:
            ex.run({}, Condition(), None)
        assert "cond stop a" in str(ei.value)

    def test_loop_condition_terminate_empty_msg_default(self):
        loop_attrs = {
            "task_start": 2, "task_end": 2,
            "loop_key": "items", "loop_times": "0",
            "loop_index_key": "loop_idx", "item_key": "loop_item",
            "exception_then": "",
            "loop_condition": "return True, 'terminate'",
            "terminate_msg": "",
        }
        body = [Task(type="INITIAL_PARAMS", input='{"noop":"1"}')]
        ex = _build_execution(loop_attrs, body)
        with pytest.raises(LoopTerminateError) as ei:
            ex.run({}, Condition(), None)
        assert "tloop" in str(ei.value)
```

- [ ] **Step 2: 运行测试,确认失败**

Run: `python -m pytest testcoverage/test_loop_terminate.py::TestExecutionTerminateOnCondition -v`
Expected: FAIL — 当前 `_eval_loop_condition` 把 `terminate` 归为 `break`(第 209 行),loop 只是 break 退出,`run()` 正常返回,不抛异常。

- [ ] **Step 3: 实现**

放宽 `_eval_loop_condition` 的末行(当前 `return action if action in ('break', 'continue') else 'break'`):

```python
        return action if action in ('break', 'continue', 'terminate') else 'break'
```

在消费处(`if state.is_loop_execution and current_loop:` 块,当前有 `if cond_action == 'break'` / `elif cond_action == 'continue'`)加 terminate 分支,放在最前:

```python
            if state.is_loop_execution and current_loop:
                cond_action = self._eval_loop_condition(current_loop, data_chain)
                if cond_action == 'terminate':
                    raise LoopTerminateError(
                        self._build_terminate_msg(current_loop, processor, state, data_chain, None))
                if cond_action == 'break':
                    state.force_exit_loop(data_chain)
                    state.move_to_next()
                    continue
                elif cond_action == 'continue':
                    if state.advance_loop_on_exception(data_chain):
                        continue
                    state.move_to_next()
                    continue
```

- [ ] **Step 4: 运行测试,确认通过**

Run: `python -m pytest testcoverage/test_loop_terminate.py::TestExecutionTerminateOnCondition -v`
Expected: PASS(2 passed)。

- [ ] **Step 5: 回归全部 loop 相关测试**

Run: `python -m pytest testcoverage/test_loop_state.py testcoverage/test_loop_terminate.py testcoverage/test_if_else.py -v`
Expected: 全部 PASS。

- [ ] **Step 6: Commit**

```bash
git add core/execution.py testcoverage/test_loop_terminate.py
git commit -m "feat(loop): terminate execution when loop_condition returns terminate (main runtime)"
```

---

## Task 4: `terminate_msg` 表达式求值兜底

**Files:**
- Test: `testcoverage/test_loop_terminate.py`(仅加测试;实现已由 Task 2 的 `_build_terminate_msg` try/except 覆盖)

**Interfaces:**
- Consumes: `_build_terminate_msg`(Task 2)

- [ ] **Step 1: 写测试**

追加。`terminate_msg` 引用不存在的变量 `{nope}`,应兜底返回原始模板串(不崩):

```python
class TestTerminateMsgExpression:

    def test_terminate_msg_unresolved_var_falls_back(self):
        loop_attrs = {
            "task_start": 2, "task_end": 2,
            "loop_key": "items", "loop_times": "0",
            "loop_index_key": "loop_idx", "item_key": "loop_item",
            "exception_then": "",
            "loop_condition": "return True, 'terminate'",
            "terminate_msg": "ref {nonexistent_var_xyz}",
        }
        body = [Task(type="INITIAL_PARAMS", input='{"noop":"1"}')]
        ex = _build_execution(loop_attrs, body)
        with pytest.raises(LoopTerminateError) as ei:
            ex.run({}, Condition(), None)
        # expression2str 对未解析变量兜底返回原串;不得崩成其它异常
        assert "nonexistent_var_xyz" in str(ei.value)
```

> 注:`expression2str` 对缺失变量返回字面串 `"{nonexistent_var_xyz}"`(项目已知行为),`_build_terminate_msg` 的 try/except 是对 f-string 真正抛错(如语法)的二次兜底。两层都确保 terminate 消息构造不会二次崩溃。

- [ ] **Step 2: 运行测试,确认通过**

Run: `python -m pytest testcoverage/test_loop_terminate.py::TestTerminateMsgExpression -v`
Expected: PASS(Task 2 实现已覆盖此行为)。若 FAIL,说明 `_build_terminate_msg` 的兜底不完整,回 Task 2 修。

- [ ] **Step 3: Commit**

```bash
git add testcoverage/test_loop_terminate.py
git commit -m "test(loop): terminate_msg expression fallback on unresolved var"
```

---

## Task 5: `BackgroundRuntime` 镜像实现 + 双实现一致性

**Files:**
- Modify: `core/runtime/BackgroundRuntime.py`(task 异常块 ~135–156;loop_condition 块 ~172–183)
- Test: `testcoverage/test_loop_terminate.py`

**Interfaces:**
- Consumes: `Execution._build_terminate_msg`、`Execution._eval_loop_condition`、`LoopTerminateError`
- Produces: BG 循环在 terminate 时 raise `LoopTerminateError` → 被外层 `try/except` 捕获 → 返回 `{"ok": False, "error": <msg>}`

- [ ] **Step 1: 写失败测试**

BG 测试需要磁盘 YAML(`run_execution("name")`),但**不能新建业务 YAML**。改用直接调用 `BackgroundRuntime` 的内部执行入口 + 内存 Execution。确认 BG 的执行方法签名后选其一:

方案(确定性,推荐):把内存 `Execution` 通过 `Execution` 的内存对象喂给 BG 的核心循环方法。先确认入口:

```python
class TestBackgroundRuntimeTerminate:

    def _run_mem_execution_in_bg(self, ex, init_data=None):
        """用 BackgroundRuntime 跑内存构造的 Execution(不写磁盘 YAML)。
        通过 monkeypatch Execution.get_execution 让 BG 拿到内存对象。"""
        import core.runtime.BackgroundRuntime as bg_mod
        from mvp.model.PETPModel import PETPModel
        from utils.SystemConfig import SystemConfig
        from core.execution import Execution as ExecClass

        model = PETPModel(SystemConfig("petpconfig.yaml"))
        runtime = bg_mod.BackgroundRuntime(model, ui_policy="skip")

        orig = ExecClass.get_execution
        ExecClass.get_execution = staticmethod(lambda name: ex if name == ex.execution else orig(name))
        try:
            return runtime.run_execution(ex.execution, init_data or {})
        finally:
            ExecClass.get_execution = staticmethod(orig)

    def test_bg_task_exception_terminate_returns_not_ok(self):
        loop_attrs = {
            "task_start": 2, "task_end": 2,
            "loop_key": "items", "loop_times": "0",
            "loop_index_key": "loop_idx", "item_key": "loop_item",
            "exception_then": "terminate",
            "loop_condition": "", "terminate_msg": "bg stop {loop_item}",
        }
        body = [Task(type="READ_JSON", input='{"file_path":"/no/such/file_xyz.json","data_key":"j"}')]
        ex = _build_execution(loop_attrs, body)
        ex.execution = "__mem_bg_terminate_test"
        r = self._run_mem_execution_in_bg(ex)
        assert r["ok"] is False
        assert "bg stop a" in str(r["error"])

    def test_bg_loop_condition_terminate_returns_not_ok(self):
        loop_attrs = {
            "task_start": 2, "task_end": 2,
            "loop_key": "items", "loop_times": "0",
            "loop_index_key": "loop_idx", "item_key": "loop_item",
            "exception_then": "",
            "loop_condition": "return True, 'terminate'",
            "terminate_msg": "bg cond stop",
        }
        body = [Task(type="INITIAL_PARAMS", input='{"noop":"1"}')]
        ex = _build_execution(loop_attrs, body)
        ex.execution = "__mem_bg_cond_terminate_test"
        r = self._run_mem_execution_in_bg(ex)
        assert r["ok"] is False
        assert "bg cond stop" in str(r["error"])
```

> 执行者注:Step 1 开始前,先 `grep -n "def run_execution\|get_execution(" core/runtime/BackgroundRuntime.py` 确认 BG 是通过 `Execution.get_execution(name)` 加载 execution 的。若加载方式不同(例如直接 `YamlRO`),改用对应的 monkeypatch 目标;核心要求不变:**用内存 Execution,不落盘业务 YAML**。

- [ ] **Step 2: 运行测试,确认失败**

Run: `python -m pytest testcoverage/test_loop_terminate.py::TestBackgroundRuntimeTerminate -v`
Expected: FAIL — BG 循环尚未处理 terminate,`exception_then='terminate'` 走 `else` 直接抛原始异常被外层捕获(error 不含 terminate_msg),或 loop_condition terminate 被当 break(ok=True)。

- [ ] **Step 3: 实现**

在 `core/runtime/BackgroundRuntime.py` import 加 `LoopTerminateError`(若未间接可用):

```python
from core.loop import LoopTerminateError
```

task 异常块(当前 `if exception_policy in ('continue', 'break'):`)镜像 Task 2 改法:

```python
                    exception_policy = current_loop.get_exception_then() if current_loop else ''
                    if exception_policy in ('continue', 'break', 'terminate'):
                        try:
                            processor.do_process()
                        except Exception as e:
                            logging.exception(
                                'Loop %s exception at task %s (policy=%s): %s',
                                current_loop.get_loop_code(), state.get_sequence(), exception_policy, e
                            )
                            task.end = DateUtil.get_now_in_str("%Y-%m-%d %H:%M:%S")
                            self._log_end_process(seq, proc_name, loop_cursor, task)
                            if exception_policy == 'terminate':
                                raise LoopTerminateError(
                                    execution._build_terminate_msg(current_loop, processor, state, data_chain, e))
                            if exception_policy == 'continue':
                                if state.advance_loop_on_exception(data_chain):
                                    continue
                                state.move_to_next()
                                continue
                            else:  # break
                                state.force_exit_loop(data_chain)
                                state.move_to_next()
                                continue
                    else:
                        processor.do_process()
```

loop_condition 块(当前 `if cond_action == 'break'` / `elif ...'continue'`)镜像 Task 3:

```python
                if state.is_loop_execution and current_loop:
                    cond_action = Execution._eval_loop_condition(current_loop, data_chain)
                    if cond_action == 'terminate':
                        raise LoopTerminateError(
                            execution._build_terminate_msg(current_loop, processor, state, data_chain, None))
                    if cond_action == 'break':
                        state.force_exit_loop(data_chain)
                        state.move_to_next()
                        continue
                    elif cond_action == 'continue':
                        if state.advance_loop_on_exception(data_chain):
                            continue
                        state.move_to_next()
                        continue
```

> 注:`_build_terminate_msg` 是 `Execution` 的实例方法。BG 循环里持有 `execution`(传入的 Execution 对象)和 `processor`,直接 `execution._build_terminate_msg(...)` 调用。外层 `try/except Exception`(~第 203 行)无需改——它会捕获 `LoopTerminateError` 并返回 `ok=False`,`error` 为异常字符串(含 terminate_msg)。

- [ ] **Step 4: 运行测试,确认通过**

Run: `python -m pytest testcoverage/test_loop_terminate.py::TestBackgroundRuntimeTerminate -v`
Expected: PASS(2 passed)。

- [ ] **Step 5: 双实现一致性测试**

追加——同一 loop 配置,断言 main 抛异常、BG 返回 ok=False 且消息一致:

```python
class TestDualRuntimeConsistency:

    def test_main_raises_bg_returns_not_ok_same_msg(self):
        loop_attrs = {
            "task_start": 2, "task_end": 2,
            "loop_key": "items", "loop_times": "0",
            "loop_index_key": "loop_idx", "item_key": "loop_item",
            "exception_then": "terminate",
            "loop_condition": "", "terminate_msg": "unified {loop_item}",
        }
        body_main = [Task(type="READ_JSON", input='{"file_path":"/no/such/file_xyz.json","data_key":"j"}')]
        ex_main = _build_execution(loop_attrs, body_main)
        with pytest.raises(LoopTerminateError) as ei:
            ex_main.run({}, Condition(), None)
        main_msg = str(ei.value)

        body_bg = [Task(type="READ_JSON", input='{"file_path":"/no/such/file_xyz.json","data_key":"j"}')]
        ex_bg = _build_execution(loop_attrs, body_bg)
        ex_bg.execution = "__mem_dual_test"
        r = TestBackgroundRuntimeTerminate()._run_mem_execution_in_bg(ex_bg)
        assert r["ok"] is False
        assert "unified a" in main_msg
        assert "unified a" in str(r["error"])
```

Run: `python -m pytest testcoverage/test_loop_terminate.py::TestDualRuntimeConsistency -v`
Expected: PASS。

- [ ] **Step 6: 全量回归**

Run: `python -m pytest testcoverage/test_loop_terminate.py testcoverage/test_loop_state.py testcoverage/test_bg_runtime.py testcoverage/test_execution_integration.py -v`
Expected: 全部 PASS。

- [ ] **Step 7: Commit**

```bash
git add core/runtime/BackgroundRuntime.py testcoverage/test_loop_terminate.py
git commit -m "feat(loop): terminate support in BackgroundRuntime + dual-runtime consistency tests"
```

---

## Task 6: GUI LoopEditDialog 补齐 schema + tip

**Files:**
- Modify: `mvp/view/common/LoopEditDialog.py`(`__init__` 补齐 schema;`_KEY_TIPS` 加 terminate_msg)
- Test: `testcoverage/test_loop_terminate.py`(测补齐逻辑,不起 wx GUI)

**Interfaces:**
- Consumes: `Loop.tpl()`(Task 1)
- Produces: `LoopEditDialog` 打开旧 loop 时 `self._data` 含全部 tpl key(缺失补默认值,已有值不动)

- [ ] **Step 1: 写失败测试**

补齐逻辑应抽成一个纯函数以便无 GUI 测试。追加测试:

```python
class TestLoopSchemaMerge:

    def test_merge_fills_missing_keys(self):
        from mvp.view.common.LoopEditDialog import merge_loop_schema
        legacy = {"task_start": 2, "task_end": 5, "exception_then": "break"}
        merged = merge_loop_schema(legacy)
        assert "terminate_msg" in merged
        assert merged["terminate_msg"] == ""
        # 已有值不被覆盖
        assert merged["exception_then"] == "break"
        assert merged["task_start"] == 2

    def test_merge_preserves_all_existing(self):
        from mvp.view.common.LoopEditDialog import merge_loop_schema
        legacy = {"task_start": 3, "loop_key": "mylist", "loop_condition": "return True,'break'"}
        merged = merge_loop_schema(legacy)
        assert merged["loop_key"] == "mylist"
        assert merged["loop_condition"] == "return True,'break'"
```

- [ ] **Step 2: 运行测试,确认失败**

Run: `python -m pytest testcoverage/test_loop_terminate.py::TestLoopSchemaMerge -v`
Expected: FAIL — `ImportError: cannot import name 'merge_loop_schema'`。

- [ ] **Step 3: 实现**

在 `mvp/view/common/LoopEditDialog.py` 模块级(`_KEY_TIPS` 之后、`class LoopEditDialog` 之前)加纯函数:

```python
def merge_loop_schema(data: dict) -> dict:
    """Fill missing keys from Loop.tpl() so legacy loops expose newly added
    fields (e.g. terminate_msg). Existing values are never overwritten."""
    tpl = json.loads(Loop.tpl())
    merged = dict(tpl)
    merged.update(data)
    return merged
```

在 `LoopEditDialog.py` 顶部 import 加:

```python
from core.loop import Loop
```

在 `__init__` 解析 JSON 之后,用 merge 结果替换 `self._data`:

```python
        try:
            self._data: dict = json.loads(loop_attributes_json)
        except (json.JSONDecodeError, TypeError):
            self._data = {}

        self._data = merge_loop_schema(self._data)
        self._keys = list(self._data.keys())
```

在 `_KEY_TIPS` 字典加一行:

```python
    'exception_then': 'loop_tip_exception_then',
    'terminate_msg':  'loop_tip_terminate_msg',
    'loop_condition': 'loop_tip_loop_condition',
```

- [ ] **Step 4: 运行测试,确认通过**

Run: `python -m pytest testcoverage/test_loop_terminate.py::TestLoopSchemaMerge -v`
Expected: PASS(2 passed)。

- [ ] **Step 5: 确认不破坏 import(GUI 模块可加载)**

Run: `python -c "import json; from mvp.view.common.LoopEditDialog import merge_loop_schema; print(sorted(merge_loop_schema({'task_start':1}).keys()))"`
Expected: 打印含 `terminate_msg`、`exception_then`、`loop_condition` 等全部 key 的排序列表,无异常。

- [ ] **Step 6: Commit**

```bash
git add mvp/view/common/LoopEditDialog.py testcoverage/test_loop_terminate.py
git commit -m "feat(gui): LoopEditDialog fills missing loop schema keys (terminate_msg)"
```

---

## Task 7: i18n 文案

**Files:**
- Modify: `i18n/translations.py`(`loop_tip_exception_then` 更新;新增 `loop_tip_terminate_msg`)
- Test: `testcoverage/test_loop_terminate.py`

**Interfaces:**
- Produces: `t("loop_tip_terminate_msg")` 返回非 key 本身的真实文案

- [ ] **Step 1: 写失败测试**

```python
class TestI18n:

    def test_terminate_msg_tip_exists(self):
        from i18n.translations import t, set_locale
        set_locale("en")
        assert t("loop_tip_terminate_msg") != "loop_tip_terminate_msg"
        set_locale("zh")
        assert t("loop_tip_terminate_msg") != "loop_tip_terminate_msg"

    def test_exception_then_tip_mentions_terminate(self):
        from i18n.translations import t, set_locale
        set_locale("en")
        assert "terminate" in t("loop_tip_exception_then").lower()
```

- [ ] **Step 2: 运行测试,确认失败**

Run: `python -m pytest testcoverage/test_loop_terminate.py::TestI18n -v`
Expected: FAIL — `loop_tip_terminate_msg` 不存在(t 返回 key 本身);`exception_then` tip 未提 terminate。

- [ ] **Step 3: 实现**

在 `i18n/translations.py` 更新 `loop_tip_exception_then`,并在其后新增 `loop_tip_terminate_msg`:

```python
    "loop_tip_exception_then":  {"en": "exception_then: what to do when a task inside the loop raises an exception — \"break\" stops the loop (execution continues after it), \"continue\" skips to next iteration, \"terminate\" exits the loop AND terminates the whole execution (treated as a failure)", "zh": "exception_then: 循环内任务出错时的处理方式 — \"break\" 终止循环(循环后继续执行)，\"continue\" 跳过本次继续，\"terminate\" 退出循环并终结整个 execution(视为失败)"},
    "loop_tip_terminate_msg":   {"en": "terminate_msg: optional message (supports f-string against data_chain, e.g. {loop_item}) raised when exception_then=\"terminate\" or loop_condition returns (True,'terminate'); empty → auto default message with loop code and task number", "zh": "terminate_msg: 可选消息(支持 f-string 表达式，如 {loop_item})，当 exception_then=\"terminate\" 或 loop_condition 返回 (True,'terminate') 时抛出；为空时自动生成含循环代码和任务序号的默认消息"},
```

- [ ] **Step 4: 运行测试,确认通过**

Run: `python -m pytest testcoverage/test_loop_terminate.py::TestI18n -v`
Expected: PASS(2 passed)。

- [ ] **Step 5: Commit**

```bash
git add i18n/translations.py testcoverage/test_loop_terminate.py
git commit -m "feat(i18n): loop_tip_terminate_msg + update exception_then tip"
```

---

## Task 8: 同步 portable + 全量回归

**Files:**
- 由 `python portable/sync_portable.py` 生成:`portable/core/loop.py`、`portable/core/execution.py`、`portable/core/runtime/BackgroundRuntime.py` 等
- 不手改 portable 文件

**Interfaces:**
- Consumes: Task 1–7 的全部主仓改动

- [ ] **Step 1: 同步 portable**

Run: `python portable/sync_portable.py`
Expected: 脚本成功,报告从主仓复制了 `core/loop.py`、`core/execution.py`、`core/runtime/BackgroundRuntime.py`(mvp/i18n 是否纳入 portable 由 manifest 决定——以脚本实际输出为准)。

- [ ] **Step 2: 校验 portable 已含 terminate**

Run: `grep -n "LoopTerminateError\|terminate_msg" portable/core/loop.py portable/core/execution.py portable/core/runtime/BackgroundRuntime.py`
Expected: 三个文件都出现 `LoopTerminateError` / `terminate_msg`,与主仓一致。

- [ ] **Step 3: 全量测试回归**

Run: `python -m pytest testcoverage/ -v`
Expected: 全部 PASS(重点确认 test_loop_terminate.py 全绿、无回归)。

- [ ] **Step 4: headless 冒烟(确认引擎整体没坏)**

Run: `python testcoverage/nogui_smoke.py`
Expected: 退出码 0,打印 `"ok": true`。

- [ ] **Step 5: Commit**

```bash
git add portable/
git commit -m "chore(portable): sync loop terminate changes from main"
```

---

## Self-Review

**1. Spec coverage:**
- §2.1 抛异常终结 → Task 2/3/5 ✅
- §2.2 复用 exception_then + terminate_msg → Task 1 ✅
- §3 两条路径 → Task 2(异常)+ Task 3(condition)✅
- §4.1 loop.py(异常类/tpl/getter)→ Task 1 ✅
- §4.2 execution.py(4 改动点)→ Task 2+3 ✅
- §4.3 BackgroundRuntime → Task 5 ✅
- §4.4 LoopEditDialog 补齐 schema → Task 6 ✅
- §4.5 i18n → Task 7 ✅
- §4.6 portable 同步 → Task 8 ✅
- §5 表达式上下文 → Task 2 `_build_terminate_msg` + Task 4 兜底 ✅
- §6 测试策略(内存构造 + 双实现一致性)→ Task 2–5 ✅
- §7 向后兼容 → Task 1(getter 兜底)+ Task 2(未知 policy 透传)+ Task 6(merge 不覆盖)✅

**2. Placeholder scan:** 无 TBD/TODO;所有代码步骤含真实代码。Task 5 Step 1 有一处"执行者先 grep 确认 BG 加载方式"——这是对镜像实现入口的必要前置确认,非占位(已给出确定的 monkeypatch 方案 + 回退说明)。

**3. Type consistency:**
- `LoopTerminateError`(Task 1)在 Task 2/3/5 一致使用 ✅
- `_build_terminate_msg(current_loop, processor, state, data_chain, exc)` 签名在 Task 2 定义,Task 3/5 一致调用 ✅
- `get_terminate_msg()`(Task 1)在 Task 2 `_build_terminate_msg` 内使用 ✅
- `merge_loop_schema(data)`(Task 6)测试与实现一致 ✅

**4. Review Focus:** 五项均已映射到 owning task 的测试:未知 policy→Task 2;condition terminate 无 msg→Task 3;表达式未解析变量→Task 4;双实现一致性→Task 5;GUI 补齐不丢值→Task 6 ✅
