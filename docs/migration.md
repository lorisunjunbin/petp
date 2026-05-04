# Parameter Migration Guide

For users who downloaded PETP **before 2026-05-02** and have custom YAML files using old parameter names.

---

## Who Needs This?

You can **safely ignore this** if you:
- Downloaded PETP after 2026-05-02 (new installs already use the new names)
- Only use OOTB (out-of-the-box) executions without custom modifications
- Run `python tools/migrate_params.py --dry-run` and see "No parameter renames needed"

---

## What Changed

The 2026-05-02 update standardized all processor parameter names to consistent `snake_case` conventions. If you have existing `.yaml` files under `core/executions/` or `core/pipelines/` that use old parameter names, run the migration script.

---

## Usage

```bash
# 1. Preview changes (no files modified)
python tools/migrate_params.py --dry-run

# 2. Apply the migration
python tools/migrate_params.py

# 3. (Optional) Scan a custom path
python tools/migrate_params.py --path /your/custom/executions/folder
```

The script is idempotent — running it multiple times on already-migrated files produces no changes.

---

## Key Renames

| Old Name | New Name | Affected Processors |
|----------|----------|-------------------|
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
| `verify: "Y\|N"` | `verify: "yes\|no"` | HTTP_REQUEST (value normalization) |

---

## Naming Conventions (New Standard)

| Category | Convention | Examples |
|----------|-----------|----------|
| File paths | `file_path`, `source_path`, `target_path` | never `filepath`, `sourcefolder` |
| Output keys | `data_key` (general), `value_key` (Selenium collect) | never `target_xlsx_key`, `output_key` |
| Booleans | always `"yes\|no"` lowercase | never `"Y\|N"`, `"Yes\|No"` |
| Code params | suffix `_fn` for function bodies | `condition_fn`, `filter_fn`, `resp_fn`, `map_fn` |
| LLM API env | `api_key_env` | never `key_name_gemini`, `api_key_name` |
| All params | `snake_case` only | never `useCache`, `collectby` |
| Selenium locator | `find_by` | never `clickby`, `keyinby`, `collectby` |
| Collection ref | `source_key`, `target_key` | never `given_collection`, `target_collection` |
