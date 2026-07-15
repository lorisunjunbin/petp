# PETP Portable Runtime

A self-contained PETP Execution runtime. `cp -r portable/` into any Python
project, or `cf push` it to Cloud Foundry. Runs headless (including Selenium
browser automation).

## Usage (called from Python)

```python
from portable.petp_run import run
result = run("YOUR_EXECUTION", {"key": "value"})
# result: {"ok": bool, "data": {...}, "error": str|None, "meta": {...}}
# python petp_run.py T_Supplier_Creation_CPTDC '{"supplier_name":"ABCD","last_name":"yabang","first_name":"doufu","cell":"13899999999","email":"6666666@qq.com"}'
```

Command line: `python portable/petp_run.py SMOKE_TEST`

> NOTE: `import portable.petp_run` (or running `petp_run.py` directly) calls
> `os.chdir()` into the `portable/` directory (the "convention cwd" design) and
> does **not** restore the caller's original cwd.

## Workflow: edit in GUI → copy → run in portable

The intended usage is: PETP desktop GUI as the **editor**, portable as the
**runtime**, with the YAML as the contract between them:

1. Author / debug the Execution visually in the PETP desktop GUI (step by step).
2. `Ctrl+S` to save — this writes `core/executions/<NAME>.yaml`.
3. Copy that YAML into portable: `cp <NAME>.yaml portable/core/executions/`.
4. Run: `cd portable && python petp_run.py <NAME>`.

Both sides share the same engine code and YAML format (portable's `core/` is a
copy of the main repo's), so a GUI-authored Execution loads in portable **with
no conversion**.

Boundaries to note:

- **GUI-only Processors are unavailable**: `FILE_CHOOSER`, `MOUSE_CLICK`,
  `MOUSE_POSITION`, `MOUSE_SCROLL` are excluded (cannot run headless). An
  Execution using them fails in portable with `FileNotFoundError` (Processor
  not found).
- **Dependencies must match**: if an Execution uses a Processor with heavy
  dependencies (e.g. Excel Processors need pandas/openpyxl), add them to
  `requirements.txt` (currently only Selenium-related + requests).

## Chrome binaries (must be placed manually)

**Not in git** (the whole `webdriver/` is excluded by `.gitignore`).
`chrome-headless-shell` and `chromedriver` must be downloaded manually from
Chrome for Testing:

**Download page (stable channel):** https://googlechromelabs.github.io/chrome-for-testing/#stable

The chrome and chromedriver major versions must match (pick both zips from the
same version row on that page).

- **CF (linux64)**: download `chrome-headless-shell-linux64` +
  `chromedriver-linux64`, unzip, and put the **entire directory contents** into
  `portable/webdriver/linux/` (keep the .pak/.dat/locales resources; place the
  `chrome-headless-shell` and `chromedriver` binaries in that directory).
- **Local (mac-arm64)**: download `chrome-headless-shell-mac-arm64` +
  `chromedriver-mac-arm64`, unzip into `portable/webdriver/darwin/` (same layout).

After placing them, make the binaries executable:
`chmod +x webdriver/<system>/chrome-headless-shell webdriver/<system>/chromedriver`.

> **macOS one-time step**: if the first run triggers a Gatekeeper block such as
> "libGLESv2.dylib" Not Opened, strip the quarantine attribute from the whole
> directory: `xattr -dr com.apple.quarantine portable/webdriver/darwin`.
> (Linux/CF have no such mechanism — not needed there.)

The `PETP_CHROME_BINARY` env var overrides auto-detection (point it at a binary,
absolute or relative path). Resolution order: `PETP_CHROME_BINARY` >
`webdriver/<system>/chrome-headless-shell` > `webdriver/<system>/chrome`
(`<system>` = `sys.platform`, e.g. `linux` / `darwin`). On CF, `manifest.yml`
already sets `PETP_CHROME_BINARY=webdriver/linux/chrome-headless-shell`.

## Environment variables

| Variable | Default | Effect |
|---|---|---|
| `PETP_HEADLESS` | (unset) | `true` forces headless Chrome. `petp_run.py` sets it to `true`. |
| `PETP_CHROME_BINARY` | (auto) | Path to the Chrome binary; overrides bundled auto-detection. |
| `PETP_BROWSER_LANG` | `zh-CN` | Headless browser UI / `Accept-Language` locale (`--lang` + `intl.accept_languages`). Set `en-US` (or others) to make locale-sensitive sites like Ariba render in that language. |

All are read by `utils/SeleniumUtil.py` at driver creation and only take effect
in headless mode. On CF they are declared in `manifest.yml`.

## Keeping in sync with the main repo (avoid stale copies)

The engine code (`core/`, `utils/`, event class) is a **copy** of the main repo.
After the main repo changes any of these, run from the repo root:

```bash
python portable/sync_portable.py
```

It re-copies the engine/utils and runs an import smoke check. It does **not**
overwrite your `core/executions/`, `webdriver/`, `config/`, or CF config
(`manifest.yml`/`apt.yml`).

> The sync copy list is a hand-maintained allowlist. When the main repo adds a
> new engine dependency file, register it in `sync_portable.py`'s `COPY_FILES` /
> `COPY_DIRS`. The smoke check only catches import-time (module top-level)
> breakage, not lazy/runtime imports inside untested processors.

> `utils/` is copied as a whole directory (not an allowlist). Currently no module
> under `utils/` imports wx/pyautogui at the top level, so it is safe to import
> headless; if a GUI-only util is ever added to `utils/` (top-level `import wx`
> etc.), exclude it in `sync_portable.py` to avoid crashing portable at import
> time in a headless environment.

## Cloud Foundry deployment

```bash
cd portable
cf push
```

`manifest.yml` uses the apt-buildpack (installs the .so libs chrome needs, see
`apt.yml`) + python-buildpack.

- If chrome fails to start on CF with `cannot open shared object file: libXXX.so`,
  add the corresponding package to `apt.yml` and re-push (the `apt.yml` package
  list is an initial version; iterate based on actual errors).
- If it reports `GLIBC_2.xx not found`, the chrome binary is not the
  linux64/glibc≤2.35 build — use Chrome for Testing linux64 (do NOT use the
  chromium installed via apt in Debian/Docker; that is usually a higher glibc,
  incompatible with CF's cflinuxfs4).

## Excluded Processors

`FILE_CHOOSER`, `MOUSE_CLICK`, `MOUSE_POSITION`, `MOUSE_SCROLL` (GUI-only,
top-level dependency on pyautogui, cannot run headless). The other 73 Processors
are all available.
