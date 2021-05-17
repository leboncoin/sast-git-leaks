#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Sast Git Leaks

Copyright 2020 Leboncoin
Licensed under the Apache License
Written by Fabien Martinez <fabien.martinez+github@adevinta.com>
'''
import sys
from pathlib import Path
import argparse

from config import variables
from sast_git_leaks.utils import set_logging
from sast_git_leaks import process


def main():
    set_logging()
    tools_names = variables.TOOLS.keys()
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--repo', help='name of the repo to scan', required=True)
    parser.add_argument('-o', '--output', help='name of the report (default to csv)', required=True)
    parser.add_argument('-t', '--tools', help=f'tools to use ({",".join(tools_names)})', default='all')
    parser.add_argument('-v', '--volume', help='directory to keep data', default=variables.DATA_PATH)
    parser.add_argument('-l', '--limit', help='limit number of commits to check', default=-1, type=int)
    parser.add_argument('-j', '--json', help='write report in json format', action='store_true')
    args = parser.parse_args()
    volume = None
    if args.volume:
        volume = args.volume
    if not process(
        Path(args.repo),
        args.output,
        variables,
        volume,
        args.limit,
        args.tools
    ):
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
