# 参数迁移指南

适用于 **2026-05-02 之前** 下载 PETP 且有使用旧参数名的自定义 YAML 文件的用户。

---

## 谁需要这个？

以下情况可以 **安全忽略**：
- 2026-05-02 之后下载的 PETP（新安装已使用新参数名）
- 仅使用 OOTB（开箱即用）Execution，未进行自定义修改
- 运行 `python tools/migrate_params.py --dry-run` 显示 "No parameter renames needed"

---

## 变更内容

2026-05-02 更新将所有处理器参数名标准化为统一的 `snake_case` 命名规范。如果你在 `core/executions/` 或 `core/pipelines/` 下有使用旧参数名的 `.yaml` 文件，请运行迁移脚本。

---

## 使用方法

```bash
# 1. 预览变更（不修改文件）
python tools/migrate_params.py --dry-run

# 2. 执行迁移
python tools/migrate_params.py

# 3. （可选）扫描自定义路径
python tools/migrate_params.py --path /your/custom/executions/folder
```

脚本幂等 — 对已迁移的文件多次运行不会产生任何变更。

---

## 主要重命名

| 旧名称 | 新名称 | 影响的处理器 |
|--------|--------|-------------|
| `useCache` | `use_cache` | FIB |
| `sourcefile` / `sourcefolder` | `source_path` | FILE_WATCH_MOVE, FOLDER_WATCH_MOVE, ZIP |
| `targetfile` / `targetfolder` | `target_path` | FILE_WATCH_MOVE, FOLDER_WATCH_MOVE, ZIP |
| `filepath` | `file_path` | FILE_CHOOSER, SCREENSHOT |
| `clickby` / `collectby` / `keyinby` / `findby` | `find_by` | FIND_THEN_CLICK, FIND_THEN_COLLECT, FIND_THEN_KEYIN, FIND_MULTI_* |
| `resp_func_body` / `filter_func_body` / `convert_func_body` | `resp_fn` / `filter_fn` / `convert_fn` | HTTP_REQUEST |
| `given_collection` | `source_key` | DATA_MAPPING, DATA_FILTER, DATA_GROUPBY, DATA_MASKING, DATA_MULTI_MASKING |
| `lambda` | `map_fn` / `filter_fn` | DATA_MAPPING, DATA_FILTER |
| `output_key` / `result_key` | `data_key` | RUN_SSH_COMMAND, CAPTCHA |
| `key_name_gemini` / `api_key_name` | `api_key_env` | AI_LLM_GEMINI_SETUP, AI_LLM_DEEPSEEK_SETUP, AI_LLM_ZHIPU_SETUP |
| `verify: "Y\|N"` | `verify: "yes\|no"` | HTTP_REQUEST（值规范化） |

---

## 命名规范（新标准）

| 分类 | 规范 | 示例 |
|------|------|------|
| 文件路径 | `file_path`、`source_path`、`target_path` | 禁止 `filepath`、`sourcefolder` |
| 输出键 | `data_key`（通用）、`value_key`（Selenium collect） | 禁止 `target_xlsx_key`、`output_key` |
| 布尔值 | 统一 `"yes\|no"` 小写 | 禁止 `"Y\|N"`、`"Yes\|No"` |
| 代码参数 | `_fn` 后缀表示函数体 | `condition_fn`、`filter_fn`、`resp_fn`、`map_fn` |
| LLM API 环境变量 | `api_key_env` | 禁止 `key_name_gemini`、`api_key_name` |
| 所有参数 | 仅 `snake_case` | 禁止 `useCache`、`collectby` |
| Selenium 定位器 | `find_by` | 禁止 `clickby`、`keyinby`、`collectby` |
| 集合引用 | `source_key`、`target_key` | 禁止 `given_collection`、`target_collection` |
