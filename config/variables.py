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

# TOOLS VARIABLES
# DON'T FORGET TO ADD YOUR TOOLS HERE

TOOLS = {
}
