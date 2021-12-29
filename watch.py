#!python3
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler,FileSystemEvent
import time 
import threading
import yaml
import subprocess
from os import getcwd
from sys import exit
from argparse import ArgumentParser

ongoingTask = False

class MyHandler(FileSystemEventHandler):
    def __init__(self,job,conf):
        super().__init__()
        self._conf = conf
        self._parentDirectory = job['dir']
        self._throttleInterval = job['throttle']
        self._seheduledTask = None
        self._ongoingTask = False
    
    def _backup(self,startTime):
        global ongoingTask
        while time.time() < startTime or ongoingTask:
            time.sleep(1)
        ongoingTask = True
        logging.log(logging.INFO,f"Backup Started {self._parentDirectory}")
        env = conf['env']
        password = conf['password-command']
        repo = conf['repo']
        logfile = conf['logfile']
        command = f"{env} {conf['restic-path']} -r {repo} --password-command='{password}' --exclude-file {conf['exclude-file']} backup {self._parentDirectory}"
        logging.log(logging.INFO,command)
        s = subprocess.run(command,shell=True,capture_output=True)
        logging.log(logging.INFO,s.stdout.decode())
        logging.log(logging.ERROR,s.stderr.decode())
        ongoingTask = False
        self._ongoingTask = False
        logging.log(logging.INFO,f"Backup Finished {self._parentDirectory}")

    def on_any_event(self, event:FileSystemEvent):
        if not self._ongoingTask:
            self._ongoingTask = True
            self._seheduledTask = threading.Thread(target=self._backup,args=(time.time()+int(self._throttleInterval),))
            self._seheduledTask.start()  
            logging.log(logging.INFO,f"Backup Scheduled {self._parentDirectory}")  

if __name__ == '__main__':
    
    parser = ArgumentParser(description='Restic Backup Watcher')
    parser.add_argument('-c','--config',help='Path for config file (default=./config.yml)')
    args = parser.parse_args()
    if args.config is not None:
        configPath = args.config
    else:
        configPath = './config.yml'
    try:
        with open(configPath) as f:
            conf = yaml.load(f,Loader=yaml.BaseLoader)
    except FileNotFoundError:
        print("config.yml not found. Aborting...")
        exit(1)
    observer = Observer()
    print("Watchdog Service Started")
    for job in conf['jobs']:
        observer.schedule(MyHandler(job,conf),job['dir'],recursive=True)    
    logging.basicConfig(filename=conf['logfile'],level=logging.INFO,format='%(asctime)s - %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
    logging.log(logging.INFO,conf['jobs'])
    observer.start()
    try:
        while True:
            time.sleep(5)
    finally:
        observer.stop()
        observer.join()