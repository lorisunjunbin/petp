import json
import logging
import os
import re
from typing import List, Optional, Tuple

from core.processors.sub.llm.BaseLLMClient import BaseLLMClient, LLMResponse
from core.processor import Processor
from core.task import Task
from core.loop import Loop
from i18n.translations import t

SYSTEM_PROMPT_ZH = """你是 PETP 执行流程生成助手。根据用户的自然语言描述，生成 PETP Execution 的 Task 序列。请用中文回复。

## 可用 Processor 列表：

{processor_context}

## 输出规则：
- 如果信息不足以生成完整流程，用 JSON 格式追问：
  {{"action": "ask", "questions": ["问题1", "问题2"]}}

- 如果信息充足，生成 Task 序列：
  {{"action": "generate", "tasks": [
    {{"type": "INITIAL_PARAMS", "input": {{"key": "value"}}}},
    {{"type": "GO_TO_PAGE", "input": {{"url": "{{url}}"}}}},
    ...
  ], "loops": []}}

- 用户要求修改时，用增量修改格式：
  {{"action": "modify", "operations": [
    {{"op": "insert", "after": 3, "tasks": [{{"type": "WAIT_SECONDS", "input": {{"wait_seconds": "3"}}}}]}},
    {{"op": "delete", "index": 5}},
    {{"op": "replace", "index": 2, "task": {{"type": "...", "input": {{...}}}}}}
  ]}}

- 参数值中使用 {{variable_name}} 引用 data_chain 中的变量
- 密码类参数使用占位符 "__ENCRYPTED__"，后续由用户在 GUI 中加密填写
- loops 格式：{{"task_start": 5, "task_end": 10, "loop_key": "collection_key", "loop_times": "0", "loop_index_key": "loop_idx", "item_key": "loop_item"}}
- task index 从 1 开始计数
"""

SYSTEM_PROMPT_EN = """You are a PETP Execution generator assistant. Generate Task sequences based on natural language descriptions. Reply in English.

## Available Processors:

{processor_context}

## Output Rules:
- If you need more information, ask in JSON format:
  {{"action": "ask", "questions": ["question1", "question2"]}}

- If you have enough information, generate the Task sequence:
  {{"action": "generate", "tasks": [
    {{"type": "INITIAL_PARAMS", "input": {{"key": "value"}}}},
    {{"type": "GO_TO_PAGE", "input": {{"url": "{{url}}"}}}},
    ...
  ], "loops": []}}

- For modifications, use incremental format:
  {{"action": "modify", "operations": [
    {{"op": "insert", "after": 3, "tasks": [{{"type": "WAIT_SECONDS", "input": {{"wait_seconds": "3"}}}}]}},
    {{"op": "delete", "index": 5}},
    {{"op": "replace", "index": 2, "task": {{"type": "...", "input": {{...}}}}}}
  ]}}

- Use {{variable_name}} in parameter values to reference data_chain variables
- Use "__ENCRYPTED__" as placeholder for password values
- loops format: {{"task_start": 5, "task_end": 10, "loop_key": "collection_key", "loop_times": "0", "loop_index_key": "loop_idx", "item_key": "loop_item"}}
- task index starts from 1
"""


def resolve_api_key(raw: str) -> str:
    m = re.fullmatch(r'\$\{(.+)\}', raw.strip())
    if m:
        return os.environ.get(m.group(1), '')
    return raw


class ExecutionGenerator:

    def __init__(self, categories: List[str], locale: str):
        self._categories = categories
        self._locale = locale
        self._messages = []
        self._total_prompt_tokens = 0
        self._total_completion_tokens = 0
        self._client: Optional[BaseLLMClient] = None
        self._model = ''
        self._available_processors = set(Processor.get_processors())

    def init_client(self, provider: str, api_key: str, base_url: str, model: str):
        resolved_key = resolve_api_key(api_key)
        kwargs = {'api_key': resolved_key}
        if base_url:
            kwargs['base_url'] = base_url
        self._client = BaseLLMClient.get_client_by_provider(provider, **kwargs)
        self._model = model
        self._messages = [{"role": "system", "content": self._build_system_prompt()}]

    def chat(self, user_message: str, current_tasks: Optional[List[Task]] = None) -> dict:
        if self._client is None:
            return {"action": "text", "content": t("ai_gen_no_config")}

        if current_tasks and len(current_tasks) > 0:
            context = self._build_context_message(current_tasks)
            self._messages.append({"role": "user", "content": f"{context}\n\n{user_message}"})
        else:
            self._messages.append({"role": "user", "content": user_message})

        try:
            response: LLMResponse = self._client.chat(
                messages=self._messages,
                model=self._model,
                temperature=0.7,
            )
            self._total_prompt_tokens += response.prompt_tokens
            self._total_completion_tokens += response.completion_tokens

            answer = response.content or response.reasoning_content or ''
            self._messages.append({"role": "assistant", "content": answer})

            return self._parse_response(answer)

        except Exception as e:
            logging.error(f'AI Generator LLM error: {e}')
            return {"action": "text", "content": str(e)}

    def get_token_usage(self) -> Tuple[int, int]:
        return self._total_prompt_tokens, self._total_completion_tokens

    def build_tasks(self, task_dicts: list) -> List[Task]:
        tasks = []
        for td in task_dicts:
            t_type = td.get('type', '')
            t_input = td.get('input', {})
            if isinstance(t_input, dict):
                t_input = json.dumps(t_input, ensure_ascii=False)
            tasks.append(Task(t_type, t_input, False))
        return tasks

    def build_loops(self, loop_dicts: list) -> List[Loop]:
        import time
        loops = []
        for ld in loop_dicts:
            loop_code = f"loop-{time.strftime('%Y%m%d%H%M%S')}"
            loop_attr = json.dumps(ld, ensure_ascii=False)
            loops.append(Loop(loop_code, loop_attr))
        return loops

    def apply_modifications(self, current_tasks: List[Task], operations: list) -> List[Task]:
        tasks = list(current_tasks)
        offset = 0
        for op_dict in operations:
            op = op_dict.get('op')
            if op == 'insert':
                after_idx = op_dict.get('after', 0) - 1 + offset
                new_tasks = self.build_tasks(op_dict.get('tasks', []))
                for i, nt in enumerate(new_tasks):
                    tasks.insert(after_idx + 1 + i, nt)
                offset += len(new_tasks)
            elif op == 'delete':
                idx = op_dict.get('index', 0) - 1 + offset
                if 0 <= idx < len(tasks):
                    tasks.pop(idx)
                    offset -= 1
            elif op == 'replace':
                idx = op_dict.get('index', 0) - 1 + offset
                if 0 <= idx < len(tasks):
                    td = op_dict.get('task', {})
                    t_type = td.get('type', '')
                    t_input = td.get('input', {})
                    if isinstance(t_input, dict):
                        t_input = json.dumps(t_input, ensure_ascii=False)
                    tasks[idx] = Task(t_type, t_input, False)
        return tasks

    def validate_tasks(self, tasks: List[Task]) -> List[str]:
        warnings = []
        for i, task in enumerate(tasks):
            if task.type not in self._available_processors:
                warnings.append(t("ai_gen_invalid_type", ptype=task.type))
        return warnings

    def generate_mcp_desc(self, tasks: List[Task]) -> Optional[str]:
        if self._client is None:
            return None

        task_summary = "\n".join(
            f"{i+1}. {tk.type}: {tk.input}" for i, tk in enumerate(tasks)
        )
        locale_hint = "请用中文回复。" if self._locale == 'zh' else "Reply in English."

        prompt = f"""{locale_hint}
Based on the following PETP Execution task list, generate a mcp_desc JSON.

Task list:
{task_summary}

Generate JSON with this exact structure:
{{"desc": "what the tool does", "inputSchema": {{"type": "object", "properties": {{"param1": {{"type": "string", "title": "param1", "description": "..."}}}}, "required": ["param1"]}}, "outParams": ["result_key"]}}

- inputSchema: derive from INITIAL_PARAMS keys (first task if type is INITIAL_PARAMS)
- outParams: derive from HTTP_RESPONSE_KEY or the last data_key written
- desc: one-line description of what this execution does

Return ONLY the JSON, no markdown wrapping."""

        messages = [{"role": "user", "content": prompt}]
        try:
            response = self._client.chat(messages=messages, model=self._model, temperature=0.3)
            self._total_prompt_tokens += response.prompt_tokens
            self._total_completion_tokens += response.completion_tokens
            return response.content or ''
        except Exception as e:
            logging.error(f'AI MCP desc generation error: {e}')
            return None

    def _build_system_prompt(self) -> str:
        template = SYSTEM_PROMPT_ZH if self._locale == 'zh' else SYSTEM_PROMPT_EN
        context = self._load_processor_context()
        return template.format(processor_context=context)

    def _load_processor_context(self) -> str:
        from i18n.translations import get_localized_desc
        always_include = {'General'}
        target_categories = set(self._categories) | always_include
        context_parts = []
        for ptype in Processor.get_processors():
            try:
                clazz = Processor.get_processor_by_type(ptype)
                if clazz.get_category() in target_categories:
                    desc = get_localized_desc(clazz, self._locale)
                    tpl = clazz.TPL if hasattr(clazz, 'TPL') else '{}'
                    context_parts.append(f"### {ptype}\nTPL: {tpl}\n{desc}")
            except Exception:
                continue
        return "\n\n".join(context_parts)

    def _build_context_message(self, tasks: List[Task]) -> str:
        lines = []
        for i, task in enumerate(tasks):
            lines.append(f"{i+1}. {task.type}: {task.input}")
        header = "当前 Task 列表：" if self._locale == 'zh' else "Current Task List:"
        return header + "\n" + "\n".join(lines)

    def _parse_response(self, text: str) -> dict:
        text = text.strip()
        if text.startswith('```'):
            text = re.sub(r'^```\w*\n?', '', text)
            text = re.sub(r'\n?```$', '', text)
            text = text.strip()

        try:
            parsed = json.loads(text)
            action = parsed.get('action', '')
            if action in ('ask', 'generate', 'modify'):
                return parsed
            return {"action": "text", "content": text}
        except json.JSONDecodeError:
            return {"action": "text", "content": text}
