# -*- coding: utf-8 -*-
'''
Sast Git Leaks

Copyright 2020 Leboncoin
Licensed under the Apache License
Written by Fabien Martinez <fabien.martinez+github@adevinta.com>
'''
from pathlib import Path
from uuid import uuid4


CONFIG_PATH = Path(__file__).parent
DATA_PATH = CONFIG_PATH / '..' / 'data'
REPORT_PATH = CONFIG_PATH / '..' / 'reports'
LOG_FILENAME = CONFIG_PATH / 'log.yml'

MODULE_TOOLS_PATH = 'sast_git_leaks.tools'

MANDATORY_TOOL_VARIABLES = ['class', 'name', 'bin', 'cmd', 'args']

# GITLEAKS VARIABLES
GITLEAKS = {
    'class': 'Gitleaks',
    'name': 'gitleaks',
    'bin': 'gitleaks',
    'cmd': '{binary} {args} --repo-path="{path}"',
}
GITLEAKS['report'] = REPORT_PATH / GITLEAKS['name'] / f'gitleaks_report_{str(uuid4()).replace("-", "_")}'
GITLEAKS['conf'] = CONFIG_PATH / GITLEAKS['name'] / 'leaky-repo.toml'
GITLEAKS['args'] = f'--report={GITLEAKS["report"].resolve()} --config={GITLEAKS["conf"].resolve()}'
GITLEAKS['data_last_commit_filename'] = '{name}_{repo}.txt'
GITLEAKS['last_commit_cmd'] = 'git -C {repo_path} rev-parse HEAD'
GITLEAKS['arg_commit_to'] = ' --commit-to={commit}'
GITLEAKS['arg_commit_from'] = ' --commit-from={commit}'
GITLEAKS['number_commits'] = 100
GITLEAKS['cmd_get_nth_commit'] = 'git -C {repo_path} log --format=format:%H -1 --skip={value}'
GITLEAKS['cmd_get_commits'] = 'git -C {repo_path} log --format=format:%H'
GITLEAKS['cmd_get_nth_commit_from'] = ' {commit}..'

# SHHGIT VARIABLES
SHHGIT = {
    'class': 'Shhgit',
    'name': 'shhgit',
    'bin': 'shhgit',
    'cmd': '{binary} {args} --local "{path}"'
}
SHHGIT['report'] = REPORT_PATH / SHHGIT['name'] / f'shhgit_report_{str(uuid4()).replace("-", "_")}.csv'
SHHGIT['conf'] = CONFIG_PATH / SHHGIT['name']
SHHGIT['args'] = f'--config-path {SHHGIT["conf"].resolve()} --csv-path={SHHGIT["report"].resolve()}'

# TOOLS VARIABLES
# DON'T FORGET TO ADD YOUR TOOLS HERE

TOOLS = {
    GITLEAKS['name']: GITLEAKS,
    SHHGIT['name']: SHHGIT
}
