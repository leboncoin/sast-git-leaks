# -*- coding: utf-8 -*-
'''
Sast Git Leaks

Copyright 2020 Ankirama
Licensed under the Apache License
Written by Ankirama
'''
from pathlib import Path


CONFIG_PATH = Path(__file__).parent
DATA_PATH = CONFIG_PATH / '..' / 'data'
REPORT_PATH = CONFIG_PATH / '..' / 'reports'
LOG_FILENAME = CONFIG_PATH / 'log.yml'

# SHHGIT VARIABLES
SHHGIT = {
    'class': 'Shhgit',
    'name': 'shhgit',
    'bin': 'shhgit',
    'cmd': '{binary} {args} --local "{path}"'
}
SHHGIT['report'] = REPORT_PATH / SHHGIT['name'] / 'shhgit_report.csv'
SHHGIT['conf'] = CONFIG_PATH / SHHGIT['name']
SHHGIT['args'] = f'--config-path {SHHGIT["conf"].resolve()} --csv-path={SHHGIT["report"].resolve()}'

# TOOLS VARIABLES
# DON'T FORGET TO ADD YOUR TOOLS HERE

TOOLS = {
    SHHGIT['name']: SHHGIT
}
