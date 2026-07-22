import importlib.util
import json
import logging
import os
import re
import time
from threading import Condition
from typing import TYPE_CHECKING, Any

from cachetools import LRUCache

from core.loop import Loop
from core.task import Task
from utils.DateUtil import DateUtil
from utils.LogRedactor import redact_sensitive
from utils.OSUtils import OSUtils

if TYPE_CHECKING:
    from mvp.view.PETPView import PETPView
else:
    PETPView = Any


class Processor:
    SEPARATOR: str = '|>'
    ITEM_SEPARATOR: str = '[>'
    # Default cryptocode salt — kept for backward compatibility with pre-2026-05
    # ciphertext. Override via env var PETP_SALT or ~/.petp/secret to make
    # encrypted passwords actually secret (the default value is public).
    _DEFAULT_SALT: str = 'petpisawesome'
    SALT: str = _DEFAULT_SALT
    _salt_resolved: bool = False

    TPL: str
    DESC: str = f''' 
        - Explain the usage of current  processor 
        - overview
        - parameter explanation
        - give example
    '''

    # Available categories:
    CATE_AI_LLM: str = 'AI_LLM'
    CATE_DEFAULT: str = 'Default'
    CATE_FILE: str = 'File'
    CATE_ZIP: str = 'Zip'
    CATE_SELENIUM: str = 'Selenium'
    CATE_MOUSE: str = 'Mouse'
    CATE_GUI: str = 'GUI'
    CATE_EMAIL: str = 'Email'
    CATE_DATABASE: str = 'Database'
    CATE_PARAMIKO: str = 'Paramiko'
    CATE_JSON: str = 'JSON'
    CATE_EXCEL: str = 'Excel'
    CATE_GENERAL: str = 'General'
    CATE_YUTUBE: str = 'Youtube'
    CATE_DATA_PROCESSING: str = 'DataProcessing'
    CATE_HTTP: str = 'HTTP'
    CATE_JAVASCRIPT: str = 'JAVASCRIPT'

    is_in_loop: False
    current_loop: Loop

    task: Task
    input_param: dict
    condition: Condition
    view: PETPView
    execution: any
    category: str = 'default'

    # cached_processor_classes = {}
    global _cached_processor_classes
    _cached_processor_classes = {}

    global _cached_category_map
    _cached_category_map = {}

    # Bounded so long-running loops with unique f-strings cannot grow this without limit.
    global _expr_code_cache
    _expr_code_cache = LRUCache(maxsize=2048)

    PARAM_PATTERN = re.compile(r"\{\{\s*([^{}]+?)\s*\}\}")

    # Block dunder access in expression2str f-string substitution to prevent sandbox escape
    # via object graph (e.g. {self.__init__.__globals__["os"]}).
    # NOTE: only the *inside* of {...} is scanned — string literals like "__session_key" or
    # CSS classes "i8-text-input__input" routinely appear in yaml and must remain valid.
    # Combined with restricted __builtins__ below, this closes the f-string RCE path.
    _FSTRING_FIELD_PATTERN = re.compile(r'\{([^{}]*)\}')
    _DUNDER_PATTERN = re.compile(r'__[a-zA-Z]')

    # Whitelist of builtins exposed to expression2str eval. Anything not listed is unavailable.
    # Excludes __import__, open, eval, exec, compile, globals, locals, vars, getattr, hasattr.
    # getattr/hasattr removed: they enabled info disclosure via {getattr(p,'task').data_chain}
    # which exposes the entire data_chain (passwords, tokens) — direct attribute access
    # like {p.task} is also blocked because dunder pre-scan rejects __getattribute__ chains,
    # but that defense relies on p.task being a normal attribute. Removing getattr/hasattr
    # eliminates dynamic attribute name lookup as a sandbox-bypass primitive.
    _SAFE_BUILTINS = {
        'len': len, 'str': str, 'int': int, 'float': float, 'bool': bool,
        'list': list, 'dict': dict, 'set': set, 'tuple': tuple,
        'min': min, 'max': max, 'sum': sum, 'abs': abs, 'round': round,
        'range': range, 'sorted': sorted, 'enumerate': enumerate, 'zip': zip,
        'filter': filter, 'map': map, 'any': any, 'all': all, 'reversed': reversed,
        'isinstance': isinstance, 'repr': repr,
        'print': print,
        'True': True, 'False': False, 'None': None,
    }

    def process(self) -> None:
        # must be implemented in subclass
        pass

    def get_json_param(self, param_key) -> dict:
        data_json = self.expression2str(self.get_param(param_key))
        return json.loads(data_json) if data_json else {}

    def get_category(self) -> str:
        return self.category

    def do_process(self):
        logging.info('[%s] input: %s', self.task.type, redact_sensitive(self.input_param))
        if self._should_skip_by_fn():
            return
        self.process()

    def _should_skip_by_fn(self) -> bool:
        # Optional cross-cutting gate: when a task carries a `skip_if_fn` whose body
        # returns True, skip the whole processor BEFORE process() runs. Handy when a
        # task's locator is built from a data_chain value that may be absent — no point
        # waiting out a timeout for an element that was never meant to exist.
        if not self.has_param('skip_if_fn'):
            return False
        from utils.CodeExplainerUtil import CodeExplainerUtil
        body = self.get_param('skip_if_fn')
        fn = CodeExplainerUtil.create_and_execute_func('skip_if', '(p)', body)
        skip = bool(fn(self))
        if skip:
            logging.info('[%s] skipped by skip_if_fn', self.task.type)
        return skip

    def log_noop(self, reason):
        """Log a step that COMPLETED WITHOUT DOING ITS WORK (a soft skip / no-op):
        element not found under skip_timeout_error, condition_fn returned False,
        click intercepted-and-skipped, etc. Uses a distinct ``[NOOP]`` prefix so
        these "green but nothing happened" cases stand out in the log and can be
        grepped — the failure mode where the run looks successful but the target
        system got no data."""
        logging.warning('[NOOP] %s: %s', type(self).__name__, reason)

    def resolve_timeout_msg(self, timeout=None):
        """Read and expression-resolve the optional business ``timeout_msg`` param.

        Uses ``expression2str`` directly (not ``explain_optional``, which would
        discard a value still containing an unresolved ``{var}`` — but a
        ``timeout_msg`` is MEANT to contain expressions like
        ``Can not find the supplier {supplier_name} in {timeout} seconds.``).
        The processor's local ``timeout`` is passed as an extra local so
        ``{timeout}`` resolves without touching the shared data_chain. Returns ''
        when the param is absent."""
        if not self.has_param('timeout_msg'):
            return ''
        return self.expression2str(self.get_param('timeout_msg'),
                                   extra_locals={'timeout': timeout})

    def fail_or_skip(self, msg, skip_err, prefix=None, timeout_msg=''):
        """Uniform skip_timeout_error handling: soft-skip (log a [NOOP] and
        return) when ``skip_err``, else raise. ``prefix`` defaults to the
        processor class name. Used by Selenium processors so the skip/raise
        shape isn't copy-pasted.

        ``timeout_msg`` is an optional caller-supplied business message. It is
        appended to the raised exception ONLY when raising (skip_err is False),
        so a hard failure can carry domain context (e.g. "供应商属性未选中，请检查
        数据"). It is intentionally NOT added to the soft-skip [NOOP] log, which
        already states the skip reason."""
        full = '%s: %s' % (prefix or type(self).__name__, msg)
        if skip_err:
            self.log_noop('%s (skip_timeout_error=yes)' % full)
            return
        if timeout_msg:
            full = '%s -- %s' % (full, timeout_msg)
        raise Exception(full)

    def handle_ui_thread_callback(self, given):
        pass

    def set_current_loop(self, loop):
        self.current_loop = loop

    def get_current_loop(self):
        return self.current_loop

    def set_in_loop(self, is_in_loop):
        self.is_in_loop = is_in_loop

    def set_view(self, view):
        self.view = view

    def set_execution(self, execution):
        self.execution = execution

    def get_view(self):
        return self.view

    def set_condition(self, condition: Condition):
        self.condition = condition

    def get_condition(self):
        return self.condition

    def need_skip(self):
        # if run in cron and skip_in_pipeline is yes.
        if self.has_param("skip_in_pipeline") and self.has_param("run_in_pipeline"):
            skip_in_pipeline = self.get_param("skip_in_pipeline")
            run_in_pipeline = self.get_param("run_in_pipeline")
            if "yes" == skip_in_pipeline.lower() and "yes" == run_in_pipeline.lower():
                return True

        return False

    def extra_wait(self):
        if self.has_param("wait"):
            wait_in_seconds = int(self.get_param("wait"))
            if wait_in_seconds > 0:
                time.sleep(wait_in_seconds)

    def get_tpl(self):
        return self.TPL

    def get_desc(self):
        return f'''
        ----------------------------------------------------{self.get_localized_desc()}    ----------------------------------------------------'''

    @classmethod
    def get_localized_desc(cls):
        from i18n.translations import get_locale, TRANSLATIONS
        if get_locale() != 'zh':
            return cls.DESC
        key = f"desc_{cls.__name__.replace('Processor', '')}"
        entry = TRANSLATIONS.get(key)
        if entry and 'zh' in entry:
            return entry['zh']
        return cls.DESC
    def str_to_date(self, date_str, format_str='%Y-%m-%d'):
        return DateUtil.get_date(date_str, format_str)

    def get_now_with_delta_in_str(self, delta=0, df="%Y-%m-%d %H:%M:%S"):
        return DateUtil.get_now_with_delta_in_str(delta, df)

    def get_now_str(self):
        return DateUtil.get_now_in_str()

    def get_now_in_str(self, df="%Y%m%d%H%M%S"):
        return DateUtil.get_now_in_str(df)

    def get_ddir(self):
        from utils.AppPaths import get_download_dir
        return get_download_dir()

    def get_rdir(self):
        return os.path.realpath(f'.{os.sep}resources')

    def get_tdir(self):
        return os.path.realpath(f'.{os.sep}testcoverage')

    def get_sdir(self):
        return os.path.realpath(f'.{os.sep}webapp{os.sep}shared')

    def set_task(self, task: Task):
        self.task = task
        self.input_param = json.loads(self.task.input)

    def get_param_bool_if_equal(self, name, true_flag='yes'):
        return True \
            if self.has_param(name) and true_flag == self.input_param[name].lower() \
            else False

    def explain_param_or_default(self, name, default=''):
        # Use when the param may legitimately contain a dynamic expression like "{var}" that
        # should be evaluated against data_chain. If the key is missing from data_chain,
        # expression2str returns the literal string "{var}" — callers that need to distinguish
        # "unresolved" from "intentional value" should use explain_optional instead.
        return self.expression2str(self.get_param(name)) if self.has_param(name) else default

    def explain_optional(self, name, default=''):
        # Use for truly optional params where "{var}" appearing in the result always means
        # the caller forgot to pass the value (i.e. it was never resolved from data_chain).
        # Examples: attachment path, email filter fields, CC/BCC addresses.
        # Do NOT use when the param value itself is expected to be a dynamic expression —
        # e.g. a template string or a computed path that the user deliberately wrote as "{x}".
        value = self.explain_param_or_default(name, default)
        if isinstance(value, str) and value.startswith('{') and value.endswith('}'):
            return default
        return value

    def explain_param_as_int(self, name, default=0):
        return int(self.expression2str(self.get_param(name))) if self.has_param(name) else default

    def explain_param_as_float(self, name, default=0.0):
        return float(self.expression2str(self.get_param(name))) if self.has_param(name) else default

    def get_param(self, name):
        if self.has_param(name):
            return self.input_param[name]

    def has_param(self, name):

        return name in self.input_param and \
            (
                len(self.input_param[name]) > 0
                if type(self.input_param[name]) is str
                else not self.input_param[name] is None
            )

    # ------------------------------------------------------------------
    # region: Data & expression helpers (data_chain ops, expression2str, feed_tpl, ...)
    # ------------------------------------------------------------------

    def get_all_params(self):
        return self.input_param

    def append_data_for_loop(self, k, v):
        """
        keep the data @ data_chain[loop_code][current_idx][k] = v
        """
        d = self.task.data_chain
        l = self.get_current_loop()
        loop_code = l.get_loop_code()
        loop_index_key = l.get_loop_index_key()
        current_idx = d[loop_index_key]

        if not loop_code in d:
            d[loop_code] = {}

        if not current_idx in d[loop_code]:
            d[loop_code][current_idx] = {}

        d[loop_code][current_idx][k] = v

        if not l.get_item_key() in d[loop_code][current_idx]:
            d[loop_code][current_idx][l.get_item_key()] = d[l.get_item_key()]

    def get_data_by_loop(self, k):
        d = self.task.data_chain
        l = self.get_current_loop()
        loop_code = l.get_loop_code()
        loop_index_key = l.get_loop_index_key()
        current_idx = d[loop_index_key]
        return d[loop_code][current_idx][k]

    def populate_data(self, k, v):
        d = self.task.data_chain
        if k in d:
            logging.warning('key [ %s ] occupied and overwritten!', k)
        d[k] = v
        logging.info('[%s] output: %s', self.task.type, k)
        logging.debug('[%s] output: %s --> %s', self.task.type, k, v)

    def get_data_by_param_default_data(self, param, default_data_name):
        return self.get_data(self.get_param(param)) if self.has_param(param) else self.get_data(default_data_name)

    def get_data_by_param_default_param(self, param, default_param_name):
        return self.get_data(self.get_param(param)) if self.has_param(param) else self.expression2str(
            self.get_param(default_param_name))

    def get_data(self, k):
        return self._get_data(self.task.data_chain, k)

    def get_data_chain_str(self):
        return str(self.task.data_chain)

    def get_data_chain_json(self):
        return json.dumps(self.task.data_chain, default=lambda o: f"<not-serializable: {type(o).__qualname__}>")

    def get_data_chain(self):
        return self.task.data_chain

    def has_data(self, k):
        try:
            return k in self.task.data_chain
        except:
            return hasattr(self.task.data_chain, k)

    def del_data(self, k):
        if (self.has_data(k)):
            del self.task.data_chain[k]

    def _get_data(self, obj, key):
        if not obj or not key:
            return None
        try:
            return obj[key]
        except:
            return getattr(obj, key, None)

    def get_deep_data(self, keys):
        result: any = self.task.data_chain

        for key in keys:
            result = self._get_data(result, key)

        return result

    _EXPR_STRATEGIES = (
        lambda e: "f'" + e + "'",
        lambda e: 'f"' + e + '"',
        lambda e: "f" + e,
    )

    def expression2str(self, expression, none_if_not_matched=False, extra_locals=None):
        """
        Evaluate an expression as an f-string against the current data_chain context.

        Strategy (tried in order):
          1. Wrap in single quotes:  eval("f'<expression>'")
             → suits bare templates like:  Hello {name}
          2. Wrap in double quotes:  eval('f"<expression>"')
             → suits templates that contain single quotes: it's {name}
          3. Expression already quoted: eval("f<expression>")
             → suits literals like: f"Hello {name}"  or  f'Hi {name}'
          4. Fallback: return the original string unchanged.

        Local variables from data_chain are injected so that {key} references resolve.
        ``extra_locals`` (optional dict) supplies additional runtime values (e.g.
        {'timeout': 10}) layered on top of data_chain without mutating it.
        """
        if expression is None:
            return None

        if isinstance(expression, (int, float)):
            return str(expression)

        if isinstance(expression, str) and '{' not in expression:
            return expression

        # Dunder pre-scan: any '__<letter>' token (e.g. __import__, __class__, __globals__)
        # inside an f-string field {...} is rejected before eval to prevent object-graph
        # sandbox escape. CPython auto-injects __builtins__ even when globals dict is empty,
        # so eval-time defense alone is insufficient.
        # Plain string literals like "__session_key" or CSS "items__abc" are NOT scanned —
        # they pass through f-string formatting as text.
        if isinstance(expression, str):
            for field in self._FSTRING_FIELD_PATTERN.findall(expression):
                if self._DUNDER_PATTERN.search(field):
                    logging.warning("expression2str rejected dunder access in field=%r expression=%r",
                                    field, expression)
                    if none_if_not_matched:
                        return None
                    return expression

        local_vars = {'self': self, 'os': os, 'json': json, 'p':self}
        try:
            if self.task and self.task.data_chain:
                local_vars.update(self.task.data_chain)
        except Exception:
            pass
        # extra_locals are layered LAST so caller-supplied runtime values (e.g.
        # {timeout}) resolve even when absent from data_chain, and shadow any
        # like-named data_chain key without mutating the shared chain.
        if extra_locals:
            local_vars.update(extra_locals)

        # Restricted globals: only whitelisted builtins. Combined with dunder pre-scan,
        # this blocks __import__, open, eval, exec, compile, and object-graph traversal.
        eval_globals = {'__builtins__': self._SAFE_BUILTINS}

        cached = _expr_code_cache.get(expression)
        if cached is not None:
            strategy_idx, code_obj = cached
            try:
                return eval(code_obj, eval_globals, local_vars)
            except Exception as e:
                logging.error(f"expression2str cached strategy-{strategy_idx + 1} failed for expression={expression!r}: {e}")
                if none_if_not_matched:
                    return None
                return expression

        for idx, build_src in enumerate(self._EXPR_STRATEGIES):
            src = build_src(expression)
            try:
                code_obj = compile(src, '<expr>', 'eval')
            except SyntaxError:
                continue
            try:
                result = eval(code_obj, eval_globals, local_vars)
                _expr_code_cache[expression] = (idx, code_obj)
                return result
            except Exception as e:
                logging.error(f"expression2str attempt-{idx + 1} failed for expression={expression!r}: {e}")

        if none_if_not_matched:
            return None

        return expression

    def str2dict(self, str) -> dict:
        result = {}
        for kv in str.split(self.SEPARATOR):
            key0value1 = kv.split(self.ITEM_SEPARATOR)
            result[key0value1[0]] = key0value1[1]
        return result

    def feed_tpl(self, given: str, params: dict) -> str:
        """
        Replace placeholders in format {{key}} using values from params.
        Keep original token when key is absent in params.
        """
        if not isinstance(given, str) or not given:
            return given

        if not isinstance(params, dict) or not params:
            return given

        def _replace(match):
            key = match.group(1).strip()
            if key not in params:
                return match.group(0)
            value = params.get(key)
            return '' if value is None else str(value)

        return self.PARAM_PATTERN.sub(_replace, given)

    def prop2dict(self, prop_content: str) -> dict:
        result = {}

        if isinstance(prop_content, dict):
            return dict(prop_content)

        if isinstance(prop_content, (bytes, bytearray)):
            prop_content = prop_content.decode('utf-8', errors='replace')

        if not isinstance(prop_content, str) or not prop_content:
            return result

        for line in prop_content.splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            if '=' not in line:
                continue

            key, value = line.split('=', 1)
            key = key.strip()
            if not key:
                continue
            result[key] = value.strip()

        return result

    def json2dict(self, json_str: str) -> dict:
        if isinstance(json_str, (dict, list)):
            return json_str

        if isinstance(json_str, (bytes, bytearray)):
            json_str = json_str.decode('utf-8', errors='replace')

        return json.loads(json_str)

    def str2list(self, str) -> list:
        return str.split(self.SEPARATOR)

    def decrypt(self, str):
        return Processor.decrypt_pwd(str)

    def split_into_2d_array(self, arr, size):
        result = []
        for i in range(0, len(arr), size):
            result.append(arr[i:i + size])
        return result

    # ------------------------------------------------------------------
    # region: Crypto helpers (encrypt/decrypt password using cryptocode + SALT)
    # ------------------------------------------------------------------

    @staticmethod
    def encrypt_pwd(str) -> str:
        import cryptocode
        return cryptocode.encrypt(str, Processor._resolve_salt())

    @staticmethod
    def decrypt_pwd(str):
        import cryptocode
        return cryptocode.decrypt(str, Processor._resolve_salt())

    @staticmethod
    def _resolve_salt() -> str:
        """Return the cryptocode salt, resolving once and caching.

        Lookup order (first hit wins):
          1. Env var PETP_SALT
          2. ~/.petp/secret  (file mode must be 0600 on POSIX or it is ignored
             with a warning — guard against leaking via group/world-readable copy)
          3. Default 'petpisawesome' (PUBLIC — pre-2026-05 ciphertext compat)

        When the default falls through, a one-time WARNING is logged so
        operators know their encrypted passwords are not actually secret.
        """
        if Processor._salt_resolved:
            return Processor.SALT

        env_salt = os.environ.get('PETP_SALT')
        if env_salt:
            Processor.SALT = env_salt
            Processor._salt_resolved = True
            logging.info("PETP salt loaded from env PETP_SALT")
            return Processor.SALT

        try:
            secret_path = os.path.expanduser('~/.petp/secret')
            if os.path.isfile(secret_path):
                if os.name == 'posix':
                    mode = os.stat(secret_path).st_mode & 0o777
                    if mode & 0o077:
                        logging.warning(
                            "PETP salt file %s mode is %o — must be 0600 to be trusted; ignoring",
                            secret_path, mode,
                        )
                    else:
                        with open(secret_path, 'r', encoding='utf-8') as f:
                            value = f.read().strip()
                        if value:
                            Processor.SALT = value
                            Processor._salt_resolved = True
                            logging.info("PETP salt loaded from %s", secret_path)
                            return Processor.SALT
                else:
                    with open(secret_path, 'r', encoding='utf-8') as f:
                        value = f.read().strip()
                    if value:
                        Processor.SALT = value
                        Processor._salt_resolved = True
                        logging.info("PETP salt loaded from %s", secret_path)
                        return Processor.SALT
        except Exception as e:
            logging.warning("Reading PETP salt file failed: %s", e)

        Processor._salt_resolved = True
        logging.warning(
            "PETP using DEFAULT public salt — encrypted passwords are NOT secret. "
            "Set env PETP_SALT or write ~/.petp/secret (mode 0600) to enable real encryption."
        )
        return Processor.SALT

    # ------------------------------------------------------------------
    # region: Static registry (processor discovery + dynamic class loading)
    # ------------------------------------------------------------------

    @staticmethod
    def get_processors():
        processors = OSUtils.get_file_list(os.path.realpath('core') + os.sep + 'processors')
        result = list(
            map(
                lambda p: p.replace('Processor.py', ''),
                filter(lambda p: 'Processor.py' in p, processors)
            )
        )
        result.sort()
        return result

    @staticmethod
    def get_category_map() -> dict:
        """Return {processor_name: category_string} for all processors.

        Reads source files directly — no class loading, no instantiation.
        Result is cached at module level.
        """
        global _cached_category_map
        if _cached_category_map:
            return _cached_category_map
        processors_dir = os.path.realpath('core') + os.sep + 'processors'
        for name in Processor.get_processors():
            path = os.path.join(processors_dir, name + 'Processor.py')
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    src = f.read()
                m = re.search(r'def get_category.*?return\s+super\(\)\.(\w+)', src, re.DOTALL)
                if m:
                    attr = m.group(1)
                    _cached_category_map[name] = getattr(Processor, attr, '')
                else:
                    _cached_category_map[name] = ''
            except Exception:
                _cached_category_map[name] = ''
        return _cached_category_map

    @staticmethod
    def get_processor_by_type(prefix: str):
        file_path = os.path.realpath('core') + os.sep + 'processors' + os.sep + prefix + 'Processor.py'
        class_name = prefix + 'Processor'
        class_cache_key = f'{file_path}::{class_name}'

        if class_cache_key not in _cached_processor_classes:
            processor_clazz = Processor.load_class_from_file(file_path, class_name)
            _cached_processor_classes[class_cache_key] = processor_clazz

        return _cached_processor_classes[class_cache_key]()

    @staticmethod
    def load_class_from_file(file_path, class_name):
        spec = importlib.util.spec_from_file_location(class_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        clazz = getattr(module, class_name)
        return clazz
