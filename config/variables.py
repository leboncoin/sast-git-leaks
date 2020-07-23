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

# GITLEAKS VARIABLES
GITLEAKS = {
    'class': 'Gitleaks',
    'name': 'gitleaks',
    'bin': 'gitleaks',
    'cmd': '{binary} {args} --repo-path="{path}"',
}
GITLEAKS['report'] = REPORT_PATH / GITLEAKS['name'] / 'gitleaks_report.json'
GITLEAKS['args'] = f'--verbose --report={GITLEAKS["report"].resolve()}'
GITLEAKS['arg_commit'] = ' --commit-to={commit}'
GITLEAKS['data_path'] = DATA_PATH / GITLEAKS['name']
GITLEAKS['data_last_commit_filename'] = '{name}_{repo}.txt'
GITLEAKS['last_commit_cmd'] = 'git -C {repo_path} rev-parse HEAD'

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
    GITLEAKS['name']: GITLEAKS,
    SHHGIT['name']: SHHGIT
}