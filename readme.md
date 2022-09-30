# ![image](./image/petp_small.png) PET-P

This is techno person RPA toolkit, handy task runner/execution engine, RPA robot build by python.

**PET** is short for Pipeline-Execution-Task, which represents the execution unit up-down, pipeline may combine multiple
executions, each execution contains multiple tasks. The last **P** means processor, which handle the specific task
one-to-one.

    Pipeline  1:n Execution
    Execution 1:n Task
    Task      1:1 Processor

GUI(wxpython)

macOS

![image](https://raw.githubusercontent.com/lorisunjunbin/petp/master/image/PETP_overview.png)

Windows

![image](https://raw.githubusercontent.com/lorisunjunbin/petp/master/image/PETP_overview_windows.png)

Beautiful soup example

![image](https://raw.githubusercontent.com/lorisunjunbin/petp/master/image/Beautifulsoup.png)

## What-Can-Do

    - Browser-related tasks(selenium)
    - cover selenium IDE recording to PETP tasks.
    - SSH/SFTP tasks(paramiko)
    - HTML/XML parser(beautiful soup)
    - File-related tasks, open/write/move/delete/etc.
    - read records from csv/excel
    - support multi-loop, no nested for now.
    - sending email
    - sending http request
    - input dialog / show message
    - Database CRUD, mysql supported(Hana/postgresql is coming soon)

## Run first Execution within 4 steps:

![image](https://raw.githubusercontent.com/lorisunjunbin/petp/master/image/user_manual.jpg)

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


## TO-DO:

- Able to easily create customized processors.
- Create more [processors](./core/processors)
  - processor of: Pillow - https://pillow.readthedocs.io/en/stable/
  
- Enhance [GUI](./mvp) none-blocking execution

## DONE:

2022-09: Support last run feature

2022-09: MOUSE_CLICKProcessor & MOUSE_SCROLLProcessor, ootb_keep_screen_unlocked 

2022-07: DB_ACCESSProcessor, Mysql supported.

2022-07: Update to Selenium 4.3.0 

2022-06: Update to python 3.10 and wxpython 4.1.2. 

2022-05: Mac m1 cpu, fix wxpython install issue, pack and build wheel locally.

2022-04-06: ZIPProcessor, verfied under Windows.

2022-03-28： Loop for times

2021-09-22: Execution grid copy & paste, right-click on the row, context menu show up, then Copy or Paste

2021-10-02: [BEAUTIFUL_SOUPProcessor](./core/processors/BEAUTIFUL_SOUPProcessor.py) 


## tips:

- Update all lib on macOS
  > pip list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1 | xargs -n1 pip install -U
- Upgrade [chromedriver](https://chromedriver.chromium.org/downloads) if got error of mismatched version.

## Wxpython

https://wxpython.org/Phoenix/snapshot-builds/

ln -s -f /usr/local/bin/python3 /usr/local/bin/python
ln -s -f /usr/local/bin/pip3 /usr/local/bin/pip

> python setup.py build
> 
> python setup.py install
> 
> pip install wheel
> 
> pip wheel wxPython-4.1.1/
> 
> pip install --force-reinstall wxPython-4.1.2a1.dev5434+7d45ee6a-cp310-cp310-macosx_10_10_universal2.whl
     
