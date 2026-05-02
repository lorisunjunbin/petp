#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import sys
import os
import re
import json
import argparse

CJK_RE = re.compile(r'[\u4e00-\u9fff]')
ALLOW_TOKENS = {
    'URL', 'JSON', 'HTTP', 'HTTPS', 'API', 'SQL', 'CSV', 'XLSX', 'Excel', 'Chrome',
    'SFTP', 'SSH', 'OCR', 'MCP', 'LLM', 'Gemini', 'DeepSeek', 'Ollama', 'ZhipuAI',
    'data_chain', 'xpath', 'id', 'css', 'markdown', 'zip', 'png', 'base64', 'base85',
    'hexlify', 'a85', 'base16', 'base32', 'base32hex', 'Top-p', 'Python', 'YouTube',
    'OAuth', 'XSRF', 'CSRF', 'Session', 'dict', 'list'
}


def parse_param_lines(text):
    params = []
    param_lines = {}
    for line in text.split('\n'):
        line = line.strip()
        m = re.match(r'^-\s+([a-zA-Z0-9_]+)\s*:(.*)$', line)
        if m:
            p_name, p_desc = m.group(1), m.group(2)
            params.append(p_name)
            param_lines[p_name] = p_desc
    return params, param_lines


def looks_untranslated_tail(tail):
    if CJK_RE.search(tail):
        return False
    words = re.findall(r'[A-Za-z][A-Za-z0-9_./:-]*', tail)
    if not words:
        return False
    return any(word not in ALLOW_TOKENS for word in words)


def find_zh_english_bullets(zh_text):
    issues = []
    for line in zh_text.splitlines():
        line = line.strip()
        if not line.startswith('- ') or ':' not in line:
            continue
        _, tail = line.split(':', 1)
        if looks_untranslated_tail(tail.strip()):
            issues.append(line)
    return issues

def main():
    parser = argparse.ArgumentParser(description="Sync or check Processor descriptions with i18n translations.")
    parser.add_argument('--check', action='store_true', help="Only check for mismatches and exit with error code if any.")
    parser.add_argument('--update', action='store_true', help="Update i18n/desc_translations.py to match core/processors DESC.")
    parser.add_argument('--check-zh', action='store_true', help="Check zh bullet lines for likely untranslated English text.")
    args = parser.parse_args()

    if not args.check and not args.update and not args.check_zh:
        parser.print_help()
        sys.exit(1)

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    processor_dir = os.path.join(project_root, 'core', 'processors')
    desc_translations_path = os.path.join(project_root, 'i18n', 'desc_translations.py')

    sys.path.insert(0, project_root)
    try:
        from i18n.desc_translations import DESC_TRANSLATIONS
    except ImportError as e:
        print(f"Error importing DESC_TRANSLATIONS: {e}")
        sys.exit(1)

    with open(desc_translations_path, 'r', encoding='utf-8') as f:
        translations_content = f.read()

    changes_needed = []
    zh_english_issues = []

    for filename in os.listdir(processor_dir):
        if not filename.endswith('Processor.py') or filename.startswith('__'):
            continue

        proc_name = filename[:-12]
        desc_key = f"desc_{proc_name}"

        if desc_key not in DESC_TRANSLATIONS:
            continue

        zh_text = DESC_TRANSLATIONS[desc_key].get('zh', '')
        zh_bullets = find_zh_english_bullets(zh_text)
        if zh_bullets:
            zh_english_issues.append({'desc_key': desc_key, 'lines': zh_bullets})

        # Read the file to get DESC using regex
        file_path = os.path.join(processor_dir, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        desc_match = re.search(r'DESC:\s*str\s*=\s*(?:\'\'\'|""")\s*(.*?)\s*(?:\'\'\'|""")', content, re.DOTALL)
        if not desc_match:
            continue

        desc_text = desc_match.group(1)

        # Extract params from DESC (English) and zh text.
        en_params, en_param_lines = parse_param_lines(desc_text)
        zh_params, zh_param_lines = parse_param_lines(zh_text)

        if en_params != zh_params:
            changes_needed.append({
                'desc_key': desc_key,
                'en_params': en_params,
                'en_param_lines': en_param_lines,
                'zh_text': zh_text,
                'zh_param_lines': zh_param_lines
            })

    if args.update:
        if changes_needed:
            print(f"Found {len(changes_needed)} processors with mismatched parameters.")
        for change in changes_needed:
            desc_key = change['desc_key']
            en_params = change['en_params']
            en_param_lines = change['en_param_lines']
            zh_text = change['zh_text']
            zh_param_lines = change['zh_param_lines']

            # Construct new ZH text
            zh_prefix = []
            for line in zh_text.split('\n'):
                line_stripped = line.strip()
                m = re.match(r'^-\s+([a-zA-Z0-9_]+)\s*:', line_stripped)
                if m:
                    break
                zh_prefix.append(line)

            new_zh_lines = zh_prefix
            if new_zh_lines and new_zh_lines[-1].strip() != '':
                new_zh_lines.append('')

            for p_name in en_params:
                if p_name in zh_param_lines:
                    new_zh_lines.append(f"- {p_name}:{zh_param_lines[p_name]}")
                else:
                    new_zh_lines.append(f"- {p_name}:{en_param_lines[p_name]}")

            new_zh_text = '\n'.join(new_zh_lines)

            pattern = r'("' + desc_key + r'":\s*\{\s*"zh":\s*\(\s*)(.*?)(\s*\)\s*,\s*\})'
            def replacer(match, text=new_zh_text):
                lines = text.split('\n')
                formatted_lines = [f'             {json.dumps(line + chr(10))}' for line in lines]
                return match.group(1) + '\n' + '\n'.join(formatted_lines) + match.group(3)

            translations_content = re.sub(pattern, replacer, translations_content, flags=re.DOTALL)

        with open(desc_translations_path, 'w', encoding='utf-8') as f:
            f.write(translations_content)

        if changes_needed:
            print(f"Successfully updated {len(changes_needed)} processors in {desc_translations_path}.")
        else:
            print("No parameter mismatches found, nothing updated.")

    exit_code = 0
    if args.check:
        if changes_needed:
            print(f"Found {len(changes_needed)} processors with mismatched parameters.")
            for change in changes_needed:
                print(f"Mismatch in {change['desc_key']}: expected {change['en_params']}")
            exit_code = 1
        else:
            print("All processor parameter translations are up to date.")

    if args.check_zh:
        if zh_english_issues:
            print(f"Found {len(zh_english_issues)} desc entries with likely untranslated zh bullet text.")
            for issue in zh_english_issues:
                for line in issue['lines']:
                    print(f"{issue['desc_key']}: {line}")
            exit_code = 1
        else:
            print("No likely untranslated English found in zh bullet lines.")

    sys.exit(exit_code)

if __name__ == '__main__':
    main()
