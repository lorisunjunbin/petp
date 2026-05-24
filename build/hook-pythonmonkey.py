"""PyInstaller hook for pythonmonkey + pminit.

pythonmonkey ships a SpiderMonkey native lib (libmozjs-*.dylib/.so/.dll), a
precompiled JS runtime under `builtin_modules/`, `node_modules/`, `lib/`, and
type defs (`*.d.ts`, `tsconfig.json`). It also has a sibling package `pminit`
whose `submodule_search_locations[0]` is used at import time
(`pythonmonkey/require.py:56`) to locate `pythonmonkey/node_modules`.

If either package is missing, frozen import dies with
`'NoneType' object has no attribute 'submodule_search_locations'` because
`importlib.util.find_spec("pminit")` returns None inside PyInstaller's
frozen importer.

Collect both: submodules + data files + native binaries.
"""
from PyInstaller.utils.hooks import collect_all

datas, binaries, hiddenimports = collect_all('pythonmonkey')

for _pkg in ('pminit',):
    _d, _b, _h = collect_all(_pkg)
    datas += _d
    binaries += _b
    hiddenimports += _h
