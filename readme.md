# ![image](./image/petp_small.png) PET-P

This is a techno-person RPA toolkit, a configurable handy task runner/execution engine built by Python, friendly for
DevOps, and automation tests.

**PET** is short for Pipeline-Execution-Task, which represents the execution unit up-down, the pipeline may combine
multiple
executions,
and each one contains various tasks. The last **P** means processor, which handles the specific task one-to-one.

    Pipeline  1:n Execution
    Execution 1:n Task
    Task      1:1 Processor

## What-Can-Do:

    Orchestrate below available task(s) as Execution, dataset-based loop and time-based loop. 
    Combine Execution(s) as pipeline, run once, or as cron.

    - Browser-related tasks by selenium, able to covert selenium IDE recording to PETP tasks.
    - SSH/SFTP tasks(paramiko)
    - HTML/XML parser(beautiful soup)
    - File-related tasks, open/write/move/delete/etc.
    - Read records from CSV/Excel
    - Send email
    - Send HTTP request
    - Input dialog / Show message
    - Mouse click/scroll(pyautogui)
    - Database CRUD for MySQL, Hana, Postgres, Sqlite
    - String encode/decode and hash
    - AI-LLM: DEEPSEEK, GEMINI, OLLAMA
    - Data Visualization: Matplotlib
    - LLM MCP support

MacOS

![image](https://raw.githubusercontent.com/lorisunjunbin/petp/master/image/PETP_overview.png)

Windows

![image](https://raw.githubusercontent.com/lorisunjunbin/petp/master/image/PETP_overview_windows.png)

HTTP Enabled

![image](https://raw.githubusercontent.com/lorisunjunbin/petp/master/image/HTTP_SERVICE_ENABLED.png)

## Run first Execution within 4 steps:

![image](https://raw.githubusercontent.com/lorisunjunbin/petp/master/image/user_manual.png)

## LLM MCP Server, Clent & host:

![image](https://raw.githubusercontent.com/lorisunjunbin/petp/master/image/DEEPSEEK-MCP.png)


## Install & Run

1, Download & Install [python3.x](https://www.python.org/downloads/)

2, Install UI widgets, download wxpython for certain python
version. [*.whl](https://wxpython.org/Phoenix/snapshot-builds/), then run

    > pip3.13 install --force-reinstall wxPython-4.2.3a1.dev5757+82b1c7aa-cp313-cp313-macosx_10_13_universal2.whl

3, Install dependencies

```bash
    pip install -r requirements.txt
```

4, Run:

```bash
    python PETP.py
```

5, Still not running? most of the issue is missing dependencies xxx, pls install xxx accordingly.

    > pip install xxx

6, Build executable for Mac & Windows, the executable is under dist folder.

```bash
    python PETP_build.py
```

## TO-DO:

- Introduced LLM MCP capability, can serve as an MCP server, providing a RESTful interface

- Able to easily create customized processors.

## DONE
2026-01: New Executions: OOTB_AI_LLM_ZHIPU， OOTB_AI_LLM_ZHIPU_MCP

2026-01: Support ZHIPU Z.AI: [AI_LLM_ZHIPU_SETUPProcessor](./core/processors/AI_LLM_ZHIPU_SETUPProcessor.py) [AI_LLM_ZHIPU_QANDAProcessor](./core/processors/AI_LLM_ZHIPU_QANDAProcessor.py) [AI_LLM_ZHIPU_QANDA_MCPProcessor](./core/processors/AI_LLM_ZHIPU_QANDA_MCPProcessor.py) 

2025-10:  [STOPPERProcessor](./core/processors/STOPPERProcessor.py) [RELOAD_LOGProcessor](./core/processors/RELOAD_LOGProcessor.py)

2025-10: Upgrade to python 3.14, wxpython to wxpython-4.2.4a15981+2c2dcc52-cp314-cp314

2025-06: Execution: OOTB_AI_LLM_GEMINI_MCP， [AI_LLM_GEMINI_QANDA_MCPProcessor](./core/processors/AI_LLM_GEMINI_QANDA_MCPProcessor.py)

2025-05: Execution: Using ThreadingHTTPServer and build AdvancedInputDialog.

2025-05: Execution: OOTB_AI_LLM_OLLAMA_MCP， [AI_LLM_OLLAMA_QANDA_MCPProcessor](./core/processors/AI_LLM_OLLAMA_QANDA_MCPProcessor.py)

2025-05: OOTB_AI_LLM_DEEPSEEK_MCP， two PETP instances, one as MCP server, another as client.

2025-05: Enable http service for PETP, the execution result as http response, port 8866 by default.

2025-04: Add execution search and dropdown handling.

2025-03: Upgrade chromedriver to 134.

2025-03: upgrade [wxpython wxPython-4.2.3a1.dev5840+45f9e89f-cp313-cp313-win_amd64.whl](https://wxpython.org/Phoenix/snapshot-builds/wxPython-4.2.3a1.dev5840+45f9e89f-cp313-cp313-win_amd64.whl) for python 3.13 and windows.

2025-01: AI LLM support, Deepseek/ gemini/ ollama-local

2024-10: Upgrade to python 3.13, chromedriver 130, fix issue of pyinstaller build.

2024-08: [MATPLOTLIBProcessor](./core/processors/MATPLOTLIBProcessor.py)

2024-08: [AI_LLM_OLLAMA_QANDAProcessor](./core/processors/AI_LLM_OLLAMA_QANDAProcessor.py)

2024-08: [RUN_EXECUTIONProcessor](./core/processors/RUN_EXECUTIONProcessor.py)

2024-07: [DATA_MULTI_MASKINGProcessor](./core/processors/DATA_MULTI_MASKINGProcessor.py)

2024-07:
AI-LLM [AI_LLM_GEMINI_SETUPProcessor](./core/processors/AI_LLM_GEMINI_SETUPProcessor.py) & [AI_LLM_GEMINI_QANDAProcessor](./core/processors/AI_LLM_GEMINI_QANDAProcessor.py)

2024-07: New feature of task skipping via {"skipped":"yes"}, upgrade chromedriver to 126, modify the width of chooser
from 300 to 500

2024-06: [DATA_GROUPBYProcessor](./core/processors/DATA_GROUPBYProcessor.py)
& [DATA_MASKINGProcessor](./core/processors/DATA_MASKINGProcessor.py)

2024-05: Introduced HttpServer(python3.12), provide http service for PETP, support GET/POST request, and return JSON
response. port 8866 by default.

2024-04: after building via pyinstall, support on-demand loading processors from ./core/processors folder.

2024-03: Build PETP executable for both MacOS & Windows by [PETP_build.py](./PETP_build.py)

2024-02: provide [PETP File Viewer](./webapp/README.md) - #5

2024-02: bring in web framework for PETP, powered by Flask, supporting basic authentication.

2024-01: new feature: execute on startup.

2023-12: DATA_COLLECTProcessor, DATA_MAPPINGProcessor, FIND_MULTI_THEN_CLICKProcessor, FOLDER_WATCH_MOVEProcessor

2023-11: On-demand change log level

2023-11: [ENCODE_DECODE_STRProcessor](./core/processors/ENCODE_DECODE_STRProcessor.py) & [HASH_STRProcessor](./core/processors/HASH_STRProcessor.py)  ,
execution: ootb_encode_decode_hash_str

2023-11: Optimized logging feature, provide setting for log level, support rotating.

2023-11: [DATA_FILTERProcessor](./core/processors/DATA_FILTERProcessor.py) & [COLLECTION_MERGEProcessor](./core/processors/COLLECTION_MERGEProcessor.py)

2023-10: Update to python3.12.

2023-09: DB_ACCESSProcessor supports databases: Mysql, Postgres, Hana, Sqlite

2023-04: PYTUBEProcessor, download youtube videos.

2022-11: Samplify & Optimize entire [UI](./mvp/view).

2022-11: clean & restructure code UI event binding.

2022-10: Enhancement [GUI](./mvp) none-blocking execution

2022-09: Support last run feature

2022-09: MOUSE_CLICKProcessor & MOUSE_SCROLLProcessor, ootb_keep_screen_unlocked

2022-07: DB_ACCESSProcessor, Mysql supported.

2022-07: Update to Selenium 4.3.0

2022-06: Update to Python 3.10 and wxpython 4.1.2.

2022-05: Mac m1 CPU, fix wxpython install issue, pack and build wheel locally.

2022-04-06: ZIPProcessor, verified under Windows.

2022-03-28： Loop for times

2021-09-22: Execution grid copy & paste, right-click on the row, context menu show up, then Copy or Paste

2021-10-02: [BEAUTIFUL_SOUPProcessor](./core/processors/BEAUTIFUL_SOUPProcessor.py)

## Appreciate for

- [wxpython](https://www.wxpython.org/) & [wxglade](https://wxglade.sourceforge.net/)

- [selenium](https://selenium-python.readthedocs.io/) & [chromedriver](https://googlechromelabs.github.io/chrome-for-testing/)

## tips:

Upgrade [chromedriver](https://googlechromelabs.github.io/chrome-for-testing/) ,[and more](https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json)
if you get an error of mismatched version (selenium task only).

- Download latest snapshot version from [Wxpython snapshot](https://wxpython.org/Phoenix/snapshot-builds/)


- Install wxpython for certain python version:

> pip3.13 install --force-reinstall wxpython-4.2.4a15955+4320e9da-cp313-cp313-win_amd64.whl

> pip3.14 install --force-reinstall wxpython-4.2.45988+6573a469-cp314-cp314-macosx_11_0_arm64.whl

- Update all lib on macOS

``` bash 
pip list --outdated | grep -v '^\-e' | cut -d = -f 1 | xargs -n1 pip install -U
```  
