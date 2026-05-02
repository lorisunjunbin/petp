#!/usr/bin/env python3
"""
Migration script for PETP processor parameter renaming.

Scans all YAML execution/pipeline files and renames old parameter names
to their new canonical names within the JSON `input` strings.

Usage:
    python tools/migrate_params.py --dry-run     # Preview changes
    python tools/migrate_params.py               # Apply changes
    python tools/migrate_params.py --path /custom/path  # Custom scan path
"""

import argparse
import json
import logging
import os
import re
import sys

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
log = logging.getLogger(__name__)

# === Rename mapping: { processor_type: { old_param: new_param } } ===
RENAME_MAP = {
    "FIB": {
        "useCache": "use_cache",
    },
    "AI_LLM_GEMINI_SETUP": {
        "key_name_gemini": "api_key_env",
    },
    "AI_LLM_DEEPSEEK_SETUP": {
        "api_key_name": "api_key_env",
    },
    "AI_LLM_ZHIPU_SETUP": {
        "api_key_name": "api_key_env",
    },
    "FILE_WATCH_MOVE": {
        "sourcefile": "source_path",
        "targetfile": "target_path",
        "filepath_key": "data_key",
    },
    "FOLDER_WATCH_MOVE": {
        "sourcefolder": "source_path",
        "targetfolder": "target_path",
        "targetfilespath_key": "data_key",
        "expectcount": "expect_count",
    },
    "CSV_2_XLSX": {
        "csv_file_path": "source_path",
        "xlsx_file_path": "target_path",
        "target_xlsx_key": "data_key",
        "dlr": "delimiter",
    },
    "FILE_CHOOSER": {
        "filepath": "file_path",
        "filepath_key": "file_path_key",
    },
    "SCREENSHOT": {
        "filepath": "file_path",
        "filepath_key": "file_path_key",
    },
    "HTTP_REQUEST": {
        "resp_func_body": "resp_fn",
        "filter_func_body": "filter_fn",
        "convert_func_body": "convert_fn",
    },
    "FIND_THEN_CLICK": {
        "by_condition": "condition_fn",
        "clickby": "find_by",
    },
    "FIND_THEN_COLLECT": {
        "collectby": "find_by",
    },
    "FIND_MULTI_THEN_CLICK": {
        "findby": "find_by",
    },
    "FIND_MULTI_THEN_COLLECT": {
        "collectby": "find_by",
    },
    "FIND_THEN_KEYIN": {
        "keyinby": "find_by",
        "clearb4keyin": "clear_before_input",
    },
    "ZIP": {
        "sourcefolder": "source_path",
        "sourcelist": "source_list",
        "zipname": "zip_name",
        "targetfolder": "target_path",
        "pathinzip": "path_in_zip",
        "pathbereplaced": "path_to_replace",
    },
    "DATA_MAPPING": {
        "given_collection": "source_key",
        "target_collection": "target_key",
        "lambda": "map_fn",
    },
    "DATA_FILTER": {
        "given_collection": "source_key",
        "filtered_collection": "target_key",
        "lambda": "filter_fn",
    },
    "DATA_COLLECT": {
        "clean_b4_collect": "clean_before_collect",
    },
    "DATA_GROUPBY": {
        "given_collection": "source_key",
        "target_dict_key": "data_key",
    },
    "DATA_MASKING": {
        "given_collection": "source_key",
        "masking_columnnum": "masking_column",
    },
    "DATA_MULTI_MASKING": {
        "given_collection": "source_key",
    },
    "RUN_SSH_COMMAND": {
        "output_key": "data_key",
    },
    "CAPTCHA": {
        "result_key": "data_key",
    },
}

# === Value normalization: { processor_type: { param_name: { old_value: new_value } } } ===
VALUE_NORMALIZE = {
    "HTTP_REQUEST": {
        "verify": {"Y": "yes", "N": "no"},
    },
    "DATA_MASKING": {
        "masking_dict_inverted": {"Yes": "yes", "No": "no"},
    },
}


def find_yaml_files(base_path):
    """Find all .yaml files recursively under the given path."""
    yaml_files = []
    for root, dirs, files in os.walk(base_path):
        for f in files:
            if f.endswith('.yaml'):
                yaml_files.append(os.path.join(root, f))
    return sorted(yaml_files)


def migrate_input_json(task_type, input_json_str, file_path):
    """
    Given a processor type and its input JSON string,
    apply parameter renames and value normalization.
    Returns (new_json_str, changes_list) where changes_list records what was changed.
    """
    changes = []

    if task_type not in RENAME_MAP and task_type not in VALUE_NORMALIZE:
        return input_json_str, changes

    try:
        params = json.loads(input_json_str)
    except json.JSONDecodeError:
        log.warning('  Cannot parse JSON in %s for type %s: %s', file_path, task_type, input_json_str[:80])
        return input_json_str, changes

    # Apply renames
    if task_type in RENAME_MAP:
        for old_name, new_name in RENAME_MAP[task_type].items():
            if old_name in params:
                params[new_name] = params.pop(old_name)
                changes.append(f'  rename: "{old_name}" -> "{new_name}"')

    # Apply value normalization
    if task_type in VALUE_NORMALIZE:
        for param_name, value_map in VALUE_NORMALIZE[task_type].items():
            actual_key = param_name
            # Check if param was just renamed
            if task_type in RENAME_MAP and param_name in RENAME_MAP[task_type]:
                actual_key = RENAME_MAP[task_type][param_name]
            if actual_key in params and params[actual_key] in value_map:
                old_val = params[actual_key]
                new_val = value_map[old_val]
                params[actual_key] = new_val
                changes.append(f'  normalize value: {actual_key} "{old_val}" -> "{new_val}"')

    if changes:
        new_json_str = json.dumps(params, ensure_ascii=False, separators=(',', ':'))
        return new_json_str, changes

    return input_json_str, changes


def process_yaml_file(file_path, dry_run=False):
    """
    Process a single YAML file, applying parameter renames to task inputs.
    Uses regex to find task blocks and extract type + input fields.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    all_changes = []

    # Strategy: find all Task blocks via regex.
    # Each task block starts with "- !!python/object:core.task.Task" and contains
    # indented fields: input, skipped, type (in alphabetical order).
    # The input field value is a YAML quoted string (possibly multi-line).

    # Split into task blocks
    task_pattern = re.compile(r'- !!python/object:core\.task\.Task\n((?:  .+\n?)*)', re.MULTILINE)

    def replace_task_block(match):
        nonlocal all_changes
        block = match.group(0)

        # Extract type
        type_match = re.search(r'^\s*type:\s*(.+)$', block, re.MULTILINE)
        if not type_match:
            return block
        task_type = type_match.group(1).strip()

        # Extract input (single-quoted multi-line)
        input_match = re.search(r"^(\s*input:\s*)'((?:[^']|'')*)'", block, re.MULTILINE | re.DOTALL)
        if not input_match:
            return block

        prefix = input_match.group(1)
        raw_json = input_match.group(2).replace("''", "'")

        # Clean up YAML multi-line formatting (remove newlines + extra spaces)
        cleaned_json = re.sub(r'\n\s+', ' ', raw_json).strip()

        new_json, changes = migrate_input_json(task_type, cleaned_json, file_path)
        if not changes:
            return block

        all_changes.append(f'[{task_type}] in {os.path.basename(file_path)}:')
        all_changes.extend(changes)

        escaped = new_json.replace("'", "''")
        new_input = f"{prefix}'{escaped}'"

        # Replace the old input line(s) with the new single-line input
        new_block = re.sub(
            r"^(\s*input:\s*)'(?:[^']|'')*'",
            lambda m: f"{m.group(1)}'{escaped}'",
            block,
            count=1,
            flags=re.MULTILINE | re.DOTALL
        )
        return new_block

    new_content = task_pattern.sub(replace_task_block, content)

    if new_content != content:
        if not dry_run:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

    return all_changes


def main():
    parser = argparse.ArgumentParser(description='Migrate PETP processor parameter names in YAML files.')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without modifying files')
    parser.add_argument('--path', type=str, default=None,
                        help='Custom path to scan (default: core/executions and core/pipelines)')
    args = parser.parse_args()

    # Determine project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    if args.path:
        scan_paths = [args.path]
    else:
        scan_paths = [
            os.path.join(project_root, 'core', 'executions'),
            os.path.join(project_root, 'core', 'pipelines'),
        ]

    all_changes = []
    files_modified = 0

    for scan_path in scan_paths:
        if not os.path.exists(scan_path):
            log.warning('Path does not exist: %s', scan_path)
            continue

        yaml_files = find_yaml_files(scan_path)
        log.info('Scanning %d YAML files in %s', len(yaml_files), scan_path)

        for yaml_file in yaml_files:
            changes = process_yaml_file(yaml_file, dry_run=args.dry_run)
            if changes:
                all_changes.extend(changes)
                files_modified += 1

    # Report
    if all_changes:
        mode = "[DRY RUN]" if args.dry_run else "[APPLIED]"
        print(f'\n{mode} Parameter migration summary:')
        print('=' * 60)
        for change in all_changes:
            print(change)
        print('=' * 60)
        print(f'Files affected: {files_modified}')
    else:
        print('No parameter renames needed.')

    return 0


if __name__ == '__main__':
    sys.exit(main())
