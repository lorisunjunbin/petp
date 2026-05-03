#!/usr/bin/env python3
"""
Migration script: Convert old provider-specific AI_LLM processor types to the new unified types.

Usage:
    python scripts/migrate_ai_llm_yaml.py                  # apply changes
    python scripts/migrate_ai_llm_yaml.py --dry-run        # preview changes only

Mapping:
    AI_LLM_DEEPSEEK_SETUP      -> AI_LLM_SETUP (provider: deepseek)
    AI_LLM_ZHIPU_SETUP         -> AI_LLM_SETUP (provider: zhipu)
    AI_LLM_GEMINI_SETUP        -> AI_LLM_SETUP (provider: gemini)
    AI_LLM_DEEPSEEK_QANDA      -> AI_LLM_QANDA
    AI_LLM_ZHIPU_QANDA         -> AI_LLM_QANDA
    AI_LLM_GEMINI_QANDA        -> AI_LLM_QANDA
    AI_LLM_OLLAMA_QANDA        -> AI_LLM_QANDA (+ inserts AI_LLM_SETUP task before it)
    AI_LLM_DEEPSEEK_QANDA_MCP  -> AI_LLM_QANDA_MCP
    AI_LLM_ZHIPU_QANDA_MCP     -> AI_LLM_QANDA_MCP
    AI_LLM_GEMINI_QANDA_MCP    -> AI_LLM_QANDA_MCP
    AI_LLM_OLLAMA_QANDA_MCP    -> AI_LLM_QANDA_MCP (+ inserts AI_LLM_SETUP task before it)
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml
from core.task import Task
from core.execution import Execution

SCAN_DIRS = ['core/executions', 'core/pipelines']

SETUP_PROVIDER_MAP = {
    'AI_LLM_DEEPSEEK_SETUP': 'deepseek',
    'AI_LLM_ZHIPU_SETUP': 'zhipu',
    'AI_LLM_GEMINI_SETUP': 'gemini',
}

QANDA_PROVIDER_MAP = {
    'AI_LLM_DEEPSEEK_QANDA': 'deepseek',
    'AI_LLM_ZHIPU_QANDA': 'zhipu',
    'AI_LLM_GEMINI_QANDA': 'gemini',
    'AI_LLM_OLLAMA_QANDA': 'ollama',
}

QANDA_MCP_PROVIDER_MAP = {
    'AI_LLM_DEEPSEEK_QANDA_MCP': 'deepseek',
    'AI_LLM_ZHIPU_QANDA_MCP': 'zhipu',
    'AI_LLM_GEMINI_QANDA_MCP': 'gemini',
    'AI_LLM_OLLAMA_QANDA_MCP': 'ollama',
}

ALL_OLD_TYPES = set(SETUP_PROVIDER_MAP.keys()) | set(QANDA_PROVIDER_MAP.keys()) | set(QANDA_MCP_PROVIDER_MAP.keys())


def find_yaml_files(base_dir):
    yaml_files = []
    for scan_dir in SCAN_DIRS:
        full_dir = os.path.join(base_dir, scan_dir)
        if not os.path.isdir(full_dir):
            continue
        for fname in sorted(os.listdir(full_dir)):
            if fname.endswith('.yaml') or fname.endswith('.yml'):
                yaml_files.append(os.path.join(full_dir, fname))
    return yaml_files


def load_execution(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return yaml.unsafe_load(f)


def save_execution(filepath, obj):
    with open(filepath, 'w', encoding='utf-8') as f:
        yaml.dump(obj, f, allow_unicode=True, default_flow_style=False)


def parse_input(input_str):
    if not input_str:
        return {}
    try:
        return json.loads(input_str)
    except (json.JSONDecodeError, TypeError):
        return {}


def dump_input(params):
    return json.dumps(params, ensure_ascii=False)


def make_ollama_setup_task(model, llm_data_key):
    input_str = dump_input({
        'provider': 'ollama',
        'model': model,
        'llm_data_key': llm_data_key,
    })
    return Task(type='AI_LLM_SETUP', input=input_str, skipped=False)


def migrate_task_list(task_list):
    changes = []
    new_list = []

    for task in task_list:
        old_type = task.type

        if old_type in SETUP_PROVIDER_MAP:
            provider = SETUP_PROVIDER_MAP[old_type]
            params = parse_input(task.input)
            params['provider'] = provider
            task.type = 'AI_LLM_SETUP'
            task.input = dump_input(params)
            new_list.append(task)
            changes.append(f'{old_type} -> AI_LLM_SETUP (provider={provider})')

        elif old_type in QANDA_PROVIDER_MAP:
            provider = QANDA_PROVIDER_MAP[old_type]
            params = parse_input(task.input)

            if provider == 'ollama':
                model = params.get('model', 'deepseek-r1:7b')
                llm_data_key = params.get('llm_data_key', 'llm_ollama')
                if 'llm_data_key' not in params:
                    params['llm_data_key'] = llm_data_key
                params.pop('role', None)
                setup_task = make_ollama_setup_task(model, llm_data_key)
                new_list.append(setup_task)
                changes.append(f'  [inserted] AI_LLM_SETUP (provider=ollama, model={model})')

            task.type = 'AI_LLM_QANDA'
            task.input = dump_input(params)
            new_list.append(task)
            changes.append(f'{old_type} -> AI_LLM_QANDA')

        elif old_type in QANDA_MCP_PROVIDER_MAP:
            provider = QANDA_MCP_PROVIDER_MAP[old_type]
            params = parse_input(task.input)

            if provider == 'ollama':
                model = params.get('model', 'deepseek-r1:7b')
                llm_data_key = params.get('llm_data_key', 'llm_ollama')
                if 'llm_data_key' not in params:
                    params['llm_data_key'] = llm_data_key
                setup_task = make_ollama_setup_task(model, llm_data_key)
                new_list.append(setup_task)
                changes.append(f'  [inserted] AI_LLM_SETUP (provider=ollama, model={model})')

            task.type = 'AI_LLM_QANDA_MCP'
            task.input = dump_input(params)
            new_list.append(task)
            changes.append(f'{old_type} -> AI_LLM_QANDA_MCP')

        else:
            new_list.append(task)

    return new_list, changes


def process_file(filepath, dry_run=False):
    try:
        obj = load_execution(filepath)
    except Exception as e:
        print(f"  WARNING: Could not parse {filepath}: {e}")
        return None

    if not hasattr(obj, 'list') or not obj.list:
        return None

    # Check if any task has an old type
    has_old = any(getattr(t, 'type', '') in ALL_OLD_TYPES for t in obj.list)
    if not has_old:
        return None

    new_list, changes = migrate_task_list(obj.list)

    if not changes:
        return None

    if not dry_run:
        obj.list = new_list
        save_execution(filepath, obj)

    return changes


def main():
    parser = argparse.ArgumentParser(description='Migrate AI_LLM processor types in YAML files')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without writing')
    parser.add_argument('--base-dir', default='.', help='Project root directory')
    args = parser.parse_args()

    base_dir = os.path.abspath(args.base_dir)
    os.chdir(base_dir)
    yaml_files = find_yaml_files(base_dir)

    if not yaml_files:
        print(f"No YAML files found in {SCAN_DIRS} under {base_dir}")
        sys.exit(1)

    total_changes = 0
    mode_label = "[DRY RUN] " if args.dry_run else ""

    print(f"{mode_label}Scanning {len(yaml_files)} YAML files...")
    print()

    for filepath in yaml_files:
        rel_path = os.path.relpath(filepath, base_dir)
        changes = process_file(filepath, dry_run=args.dry_run)
        if changes:
            print(f"{mode_label}{rel_path}:")
            for c in changes:
                print(f"    {c}")
            total_changes += len(changes)

    print()
    if total_changes == 0:
        print("No migrations needed.")
    else:
        action = "would be made" if args.dry_run else "applied"
        print(f"{total_changes} change(s) {action}.")

    if args.dry_run and total_changes > 0:
        print("\nRun without --dry-run to apply changes.")


if __name__ == '__main__':
    main()
