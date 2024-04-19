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

MacOS

![image](https://raw.githubusercontent.com/lorisunjunbin/petp/master/image/PETP_overview.png)

Windows

![image](https://raw.githubusercontent.com/lorisunjunbin/petp/master/image/PETP_overview_windows.png)

## Run first Execution within 4 steps:

![image](https://raw.githubusercontent.com/lorisunjunbin/petp/master/image/user_manual.png)

## Install & Run

1, Download & Install [python3.x](https://www.python.org/downloads/)

2, Install UI widgets, download wxpython for certain python
version. [*.whl](https://wxpython.org/Phoenix/snapshot-builds/), then run

    > pip install --force-reinstall wxPython-4.2.2a1.dev5626+a1184286-cp312-cp312-macosx_10_10_universal2.whl

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

6, Build executable for MacOS & Windows, the executable is under dist folder.

```bash
    python PETP_build.py
```

## TO-DO:

- Create more [processors](./core/processors)
    - provide the ability to access from web perspective.
    - processor of chatGPT - https://platform.openai.com/docs/api-reference/introduction
    - processor of Pillow - https://pillow.readthedocs.io/en/stable/

- Able to easily create customized processors.

## DONE

2024-04: on-demand loading processors from ./core/processors folder.

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

- [selenium](https://selenium-python.readthedocs.io/) & [chromedriver](https://chromedriver.chromium.org/downloads)

## tips:

- Upgrade [chromedriver](https://googlechromelabs.github.io/chrome-for-testing/) if you get an error of mismatched
  version (selenium task
  only). Deprecated website: https://chromedriver.chromium.org/downloads/version-selection

- Install Wxpython snapshot

> Download from https://wxpython.org/Phoenix/snapshot-builds/

> pip install --force-reinstall wxPython-4.2.1a1.dev5539+906adf71-cp310-cp310-win_amd64.whl

> pip install --force-reinstall wxPython-4.2.1a1.dev5539+906adf71-cp310-cp310-macosx_10_10_universal2.whl

> pip install --force-reinstall wxPython-4.2.1a1.dev5545+a3b6cfec-cp310-cp310-macosx_10_10_universal2.whl

> pip install --force-reinstall wxPython-4.2.2a1.dev5590+a5bb3d9b-cp311-cp311-macosx_10_10_universal2.whl

> pip install --force-reinstall wxPython-4.2.2a1.dev5613+83db65a2-cp311-cp311-macosx_10_10_universal2.whl

> pip install --force-reinstall wxPython-4.2.2a1.dev5622+e4fd9a3e-cp311-cp311-macosx_10_10_universal2.whl

> pip3.12 install --force-reinstall wxPython-4.2.2a1.dev5626+a1184286-cp312-cp312-macosx_10_10_universal2.whl

> pip3.12 install --force-reinstall wxPython-4.2.2a1.dev5633+11c4a777-cp312-cp312-macosx_10_10_universal2.whl

> pip3.12 install --force-reinstall wxPython-4.2.2a1.dev5644+87674de9-cp312-cp312-macosx_10_10_universal2.whl

> pip3.12 install --force-reinstall wxPython-4.2.2a1.dev5654+0c545000-cp312-cp312-macosx_10_10_universal2.whl

> pip3.12 install --force-reinstall wxPython-4.2.2a1.dev5656+15fe9aaa-cp312-cp312-macosx_10_10_universal2.whl

- Link python 3

> ln -s -f /usr/local/bin/python3 /usr/local/bin/python

> ln -s -f /usr/local/bin/pip3 /usr/local/bin/pip

- Update all lib on macOS

``` bash 
pip3 list --outdated | grep -v '^\-e' | cut -d = -f 1 | xargs -n1 pip3 install -U
```  

## remove previous version of python:

https://www.ianmaddaus.com/post/manage-multiple-versions-python-mac/

``` bash
sudo rm -rf /Library/Frameworks/Python.framework/Versions/3.11
sudo rm -rf '/Applications/Python 3.11'
```
