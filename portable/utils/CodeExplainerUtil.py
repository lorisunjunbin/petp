import logging


# Whitelisted modules available inside dynamic _fn / _func / lambda_* function bodies.
# Mirrors the security policy of Processor.expression2str: deny __import__ and OS
# escape hatches (os, sys, subprocess); permit only the modules user code has
# legitimately needed for data manipulation.
_SAFE_MODULES = {}


def _build_safe_modules():
    if _SAFE_MODULES:
        return _SAFE_MODULES
    import re as _re
    import json as _json
    import datetime as _datetime
    import math as _math
    _SAFE_MODULES['re'] = _re
    _SAFE_MODULES['json'] = _json
    _SAFE_MODULES['datetime'] = _datetime
    _SAFE_MODULES['math'] = _math
    return _SAFE_MODULES


class CodeExplainerUtil:
    # Mapping: processor_type -> [(param_name, func_args, body_prefix)]
    # body_prefix is prepended to the raw param value before compilation
    # (e.g. COLLECTION_MERGE stores expressions without 'return ')
    DYNAMIC_FUNC_PARAMS = {
        'BEAUTIFUL_SOUP': [
            ('func_body', '(soup, p)', ''),
        ],
        'HTTP_REQUEST': [
            ('resp_func_body', '(response, p)', ''),
            ('filter_func_body', '(filename, p)', ''),
            ('convert_func_body', '(file_content, p)', ''),
        ],
        'DATA_CONVERT': [
            ('convertor_func', '(p, given)', ''),
        ],
        'DATA_MASKING': [
            ('masking_func', '(masking_dict, row, rownum, colnum, p)', ''),
            ('content_clean_func', '(content, p)', ''),
        ],
        'DATA_MULTI_MASKING': [
            ('masking_func', '(masking_dict, row, rownum, colnum, p)', ''),
            ('content_clean_func', '(content, p)', ''),
        ],
        'FIND_MULTI_THEN_COLLECT': [
            ('skip_fn', '(ele, p)', ''),
        ],
        'FIND_MULTI_THEN_CLICK': [
            ('skip_fn', '(ele, p)', ''),
        ],
        'DATA_GROUPBY': [
            ('group_by_func', '(row, p)', ''),
            ('mapping_func', '(row, p)', ''),
            ('collect_func', '(key, rows, p)', ''),
        ],
        'COLLECTION_MERGE': [
            ('lambda_finder', '(rowc1, rowc2, p)', 'return '),
            ('lambda_merge_matched', '(rowc1, rowc2, p)', 'return '),
        ],
        'OCR': [
            ('filter_func', '(line, p)', ''),
        ],
        'FIND_THEN_CLICK': [
            ('by_condition', '(p, ele)', ''),
            ('skip_if_fn', '(p)', ''),
        ],
        'FIND_THEN_KEYIN': [
            ('skip_if_fn', '(p)', ''),
        ],
        'SELECT_TREE_DROPDOWN': [
            ('skip_if_fn', '(p)', ''),
        ],
        'SELECT_MULTI_DROPDOWN': [
            ('skip_if_fn', '(p)', ''),
        ],
        'SELECT_SINGLE_DROPDOWN': [
            ('skip_if_fn', '(p)', ''),
        ],
        'SELECT_TYPE_AHEAD': [
            ('skip_if_fn', '(p)', ''),
        ],
        'DATE_PICKER': [
            ('skip_if_fn', '(p)', ''),
        ],
        'BANK_INFO_FEEDER': [
            ('skip_if_fn', '(p)', ''),
        ],
        'CONTACT_FEEDER': [
            ('skip_if_fn', '(p)', ''),
        ],
        'FILE_UPLOAD': [
            ('skip_if_fn', '(p)', ''),
        ],
        'GO_TO_TASK': [
            ('condition_fn', '(data_chain, p)', ''),
        ],
        'IF_ELSE': [
            ('condition_fn', '(data_chain, p)', ''),
        ],
    }

    # Convention-based fallback to reduce maintenance burden for new processors.
    DYNAMIC_PARAM_SUFFIXES = ('_func_body', '_func', '_fn', '_lambda')
    DYNAMIC_PARAM_PREFIXES = ('lambda_',)
    FALLBACK_FUNC_ARGS = '(*_args, **_kwargs)'

    @staticmethod
    def is_dynamic_param_name(param_name):
        if not isinstance(param_name, str):
            return False

        normalized = param_name.strip().lower()
        if not normalized:
            return False

        if 'func_body' in normalized:
            return True

        if any(normalized.endswith(suffix) for suffix in CodeExplainerUtil.DYNAMIC_PARAM_SUFFIXES):
            return True

        if any(normalized.startswith(prefix) for prefix in CodeExplainerUtil.DYNAMIC_PARAM_PREFIXES):
            return True

        return False

    @staticmethod
    def get_dynamic_param_specs_with_source(processor_type, input_dict):
        """
        Same as get_dynamic_param_specs, but also returns spec source:
        - "explicit": from DYNAMIC_FUNC_PARAMS
        - "fallback": inferred by parameter naming convention
        """
        explicit_specs = list(CodeExplainerUtil.DYNAMIC_FUNC_PARAMS.get(processor_type, []))
        specs_with_source = [(name, func_args, body_prefix, 'explicit')
                             for name, func_args, body_prefix in explicit_specs]
        known_param_names = {name for name, _, _ in explicit_specs}

        if not isinstance(input_dict, dict):
            return specs_with_source

        for param_name in input_dict.keys():
            if param_name in known_param_names:
                continue

            if CodeExplainerUtil.is_dynamic_param_name(param_name):
                specs_with_source.append((param_name, CodeExplainerUtil.FALLBACK_FUNC_ARGS, '', 'fallback'))

        return specs_with_source

    @staticmethod
    def validate_func_syntax(func_args, func_body, body_prefix=''):
        """
        Validate the syntax of a dynamic function body without executing it.
        :return: None if valid, or the error message string if invalid.
        """
        normalized_body = CodeExplainerUtil._normalize_func_body(func_body)
        full_body = body_prefix + normalized_body
        if '\n' in full_body:
            func = 'def _validate' + func_args + ':\n' + full_body
        else:
            func = 'def _validate' + func_args + ':\n\t\t' + full_body
        try:
            compile(func, '<dynamic>', 'exec')
            return None
        except SyntaxError as e:
            return str(e)

    _func_cache = {}

    @staticmethod
    def create_and_execute_func(func_name, func_args, func_body, args=None, *extra_args):
        """
        Create a function and execute it when runtime args are provided.
        :param func_name: function name
        :param func_args: function arguments
        :param func_body: function body
        :param args: first runtime argument (kept for backward compatibility)
        :param extra_args: additional runtime arguments
        """
        normalized_body = CodeExplainerUtil._normalize_func_body(func_body)
        cache_key = (func_name, func_args, normalized_body)

        if cache_key in CodeExplainerUtil._func_cache:
            dynamic_func = CodeExplainerUtil._func_cache[cache_key]
            if '\n' in normalized_body:
                func = 'def ' + func_name + func_args + ':\n' + normalized_body
            else:
                func = 'def ' + func_name + func_args + ':\n\t\t' + normalized_body
            logging.info("Reusing cached dynamic function:\n---------------\n%s\n---------------\n", func)
        else:
            if '\n' in normalized_body:
                func = 'def ' + func_name + func_args + ':\n' + normalized_body
            else:
                func = 'def ' + func_name + func_args + ':\n\t\t' + normalized_body
            logging.info("Dynamic function generated:\n---------------\n%s\n---------------\n", func)
            try:
                compile(func, '<dynamic>', 'exec')
            except SyntaxError as e:
                logging.error("Syntax error in dynamic function:\n%s\nError: %s", func, e)
                raise SyntaxError(f"Syntax error in dynamic function '{func_name}': {e}") from e
            # Sandboxed exec namespace. Mirrors Processor.expression2str policy:
            # - __builtins__ restricted to Processor._SAFE_BUILTINS (no __import__, open,
            #   eval, exec, compile, getattr*, vars, globals, locals).
            # - Whitelisted modules (re/json/datetime/math) for legitimate data work.
            # - Local namespace isolated from CodeExplainerUtil module globals — old
            #   `exec(func, globals())` leaked module state and gave full builtins.
            from core.processor import Processor as _Processor
            sandbox_globals = {
                '__builtins__': _Processor._SAFE_BUILTINS,
                **_build_safe_modules(),
            }
            local_ns = {}
            exec(func, sandbox_globals, local_ns)
            dynamic_func = local_ns[func_name]
            CodeExplainerUtil._func_cache[cache_key] = dynamic_func

        if args is not None or extra_args:
            runtime_args = [args] if args is not None else []
            runtime_args.extend(extra_args)
            return dynamic_func(*runtime_args)

        return dynamic_func

    @staticmethod
    def _normalize_func_body(func_body):
        """
        Convert escaped multiline content (e.g. "\\n", "\\t") to real
        whitespace when body was stored as a single-line escaped string.
        """
        if not isinstance(func_body, str):
            return func_body

        # Keep original behavior for already-multiline content.
        if '\n' in func_body:
            return func_body

        if '\\n' in func_body or '\\t' in func_body:
            func_body = func_body.replace('\\r\\n', '\n').replace('\\n', '\n').replace('\\t', '\t')

        # Auto-fix common paste case: multiline body without base indentation.
        # If the first non-empty line has no leading whitespace, indent all non-empty lines.
        if '\n' in func_body:
            lines = func_body.split('\n')
            first_non_empty = next((line for line in lines if line.strip()), None)
            if first_non_empty is not None and first_non_empty == first_non_empty.lstrip(' \t'):
                lines = [('    ' + line) if line.strip() else line for line in lines]
                return '\n'.join(lines)

        return func_body
