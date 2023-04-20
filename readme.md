# ![image](./image/petp_small.png) PET-P

This is a techno-person RPA toolkit, a configurable handy task runner/execution engine built by python, friendly for
DevOps, and automation tests.

**PET** is short for Pipeline-Execution-Task, which represents the execution unit up-down, pipeline may combine multiple
executions,
and each one contains various tasks. The last **P** means processor, which handles the specific task one-to-one.

    Pipeline  1:n Execution
    Execution 1:n Task
    Task      1:1 Processor

## What-Can-Do:

    Orchestrate below available task(s) as Execution, dataset based loop and time based loop. 
    Combine Execution(s) as Pipline, run once or as cron.

    - Browser-related tasks by selenium, able to covert selenium IDE recording to PETP tasks.
    - SSH/SFTP tasks(paramiko)
    - HTML/XML parser(beautiful soup)
    - File-related tasks, open/write/move/delete/etc.
    - Read records from csv/excel
    - Send email
    - Send http request
    - Input dialog / Show message
    - Mouse click/scroll(pyautogui)
    - Database CRUD, mysql supported(Hana/postgresql is coming soon)

MacOS

![image](https://raw.githubusercontent.com/lorisunjunbin/petp/master/image/PETP_overview.png)

Windows

![image](https://raw.githubusercontent.com/lorisunjunbin/petp/master/image/PETP_overview_windows.png)

## Run first Execution within 4 steps:

![image](https://raw.githubusercontent.com/lorisunjunbin/petp/master/image/user_manual.png)

## Install & Run

    1, Install Chrome and python3
    https://www.python.org/downloads/

    2, Install dependencies
    > pip install -r requirements.txt
    OR 
    2,Install dependencies one by one 
    > pip install selenium
    > pip install wxpython
    > pip install ...other listed in requirements.txt, install without cache:  --no-cache-dir 

    3, Run: 
    > python PETP.py

    4, Still not running? most of the issue is missing dependiceis xxx, pls install xxx accordingly.
    > pip install xxx

## TO-DO:

- Create more [processors](./core/processors)
    - processor of: chatGPT - https://platform.openai.com/docs/api-reference/introduction
    - processor of: Pillow - https://pillow.readthedocs.io/en/stable/

- Able to easily create customized processors.


## DONE:

2023-04: PYTUBEProcessor, download youtube videos.

2022-11: Samplify & Optimize entire [UI](./mvp/view).

2022-11: clean & restructure code UI event binding.

2022-10: Enhancement [GUI](./mvp) none-blocking execution

2022-09: Support last run feature

2022-09: MOUSE_CLICKProcessor & MOUSE_SCROLLProcessor, ootb_keep_screen_unlocked

2022-07: DB_ACCESSProcessor, Mysql supported.

2022-07: Update to Selenium 4.3.0

2022-06: Update to python 3.10 and wxpython 4.1.2.

2022-05: Mac m1 cpu, fix wxpython install issue, pack and build wheel locally.

2022-04-06: ZIPProcessor, verified under Windows.

2022-03-28： Loop for times

2021-09-22: Execution grid copy & paste, right-click on the row, context menu show up, then Copy or Paste

2021-10-02: [BEAUTIFUL_SOUPProcessor](./core/processors/BEAUTIFUL_SOUPProcessor.py)

## Appreciate for

- [wxpython](https://www.wxpython.org/) & [wxglade](https://wxglade.sourceforge.net/)

- [selenium](https://selenium-python.readthedocs.io/) & [chromedriver](https://chromedriver.chromium.org/downloads)

## tips:

- Upgrade [chromedriver](https://chromedriver.chromium.org/downloads) if got error of mismatched version (selenium task
  only).

- Install Wxpython snapshot

> Downloan from https://wxpython.org/Phoenix/snapshot-builds/

> pip install --force-reinstall wxPython-4.2.1a1.dev5539+906adf71-cp310-cp310-win_amd64.whl

> pip install --force-reinstall wxPython-4.2.1a1.dev5539+906adf71-cp310-cp310-macosx_10_10_universal2.whl

> pip install --force-reinstall wxPython-4.2.1a1.dev5545+a3b6cfec-cp310-cp310-macosx_10_10_universal2.whl

- Link python 3

> ln -s -f /usr/local/bin/python3 /usr/local/bin/python

> ln -s -f /usr/local/bin/pip3 /usr/local/bin/pip

- Update all lib on macOS

> pip list --outdated | grep -v '^\-e' | cut -d = -f 1 | xargs -n1 pip install -U
  
  
