# ![image](./image/petp_small.png) PET-P 

This is techno person RPA toolkit, handy task runner/execution engine, RPA robot build by python. 

**PET** is short for Pipeline-Execution-Task, which represents the execution unit up-down, pipeline may combine multiple executions, each execution contains multiple tasks. 
The last **P** means processor, which handle the specific task one-to-one. 

    Pipeline  1:n Execution
    Execution 1:n Task
    Task      1:1 Processor

GUI(wxpython) Windows / macOS

![image](./image/petp_overview.png)

## What-Can-Do

    - Browser-related tasks(selenium)
    - cover selenium IDE recording to PETP tasks.
    - SSH/SFTP tasks(paramiko)
    - File-related tasks, open/write/move/delete/etc.
    - csv/excel 
    - sending email
    - sending http request
    - input dialog / show message
    
## Install & Run

    1, Install Chrome and python3
    https://www.python.org/downloads/

    2, Install dependencies  
    > pip install -r requirements.txt

    3, Run: 
    > python PETP.py

## TO-DO

- Create more [processors](./core/processors)
- Enhance [GUI](./mvp) none-blocking execution

## tips:
- Update all lib on macOS
   >pip list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1  | xargs -n1 pip install -U
- Upgrade [chromedriver](https://chromedriver.chromium.org/downloads) if got mismatched version issue.
     
