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
import subprocess
import argparse
from importlib import import_module

from config import variables
from sast_git_leaks import logger as logging
from sast_git_leaks import utils


def load_tool(tool: dict, path: Path, logger: logging, report_path: Path, loggername: str):
    '''
    Load tool module then instantiate tool
    '''
    for variable in variables.MANDATORY_TOOL_VARIABLES:
        if variable not in tool:
            logger.error(f'Unable to find mandatory variable {variable}!')
            return False
    try:
        obj = getattr(
            import_module(f'sast_git_leaks.tools.{tool["name"]}'),
            tool['class']
            )(
                tool,
                path,
                variables.DATA_PATH,
                report_path,
                loggername
            )
    except Exception as e:
        logger.error(f'Unable to load {tool["name"]}: {e}', exc_info=True)
        return False
    else:
        logger.info(f'Tool {tool["name"]} loaded')
        return obj


def load_tools(tools_loaded: str, path: Path, logger: logging, report_path: Path, loggername: str):
    '''
    Check which tools to load from argument
    '''
    to_load = tools_loaded.replace(' ', '').lower().split(',')
    tools = []
    tools_names = variables.TOOLS.keys()
    tmp_names = set(tools_names)
    tools_to_load = dict()
    if 'all' in to_load:
        tools_to_load = variables.TOOLS
    else:
        for index, value in enumerate(to_load):
            if value in tmp_names:
                name = to_load[index]
                tools_to_load[name] = variables.TOOLS[name]
    logger.info(f'Loading tools...')
    for data in tools_to_load.values():
        obj = load_tool(data, path, logger, report_path, loggername)
        if obj is False:
            logger.info(f'Load tools  aborted.')
            return False
        tools.append({'name': data['name'], 'object': obj})
    return tools


def main():
    logging.setup_logging(variables.LOG_FILENAME.absolute())
    logger = logging.getLogger(variables.LOG_ENV)
    tools_names = variables.TOOLS.keys()
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--repo', help='name of the repo to scan', required=True)
    parser.add_argument('-o', '--output', help='name of the json report', required=True)
    parser.add_argument('-t', '--tools', help=f'tools to use ({",".join(tools_names)})', default='all')
    parser.add_argument('-v', '--volume', help='directory to keep data', default=variables.DATA_PATH)
    args = parser.parse_args()
    repo_path = Path(args.repo)
    logger.info(f'Repository to check: {repo_path}')
    if not repo_path.is_dir():
        logger.error(f"Wront repo path [{repo_path}]!")
        sys.exit(1)
    report_path = Path(args.output)
    logger.info(f'Report path: {report_path}')
    variables.DATA_PATH = Path(args.volume)
    if not variables.DATA_PATH.exists():
        logger.info(f'Creating data folder [{variables.DATA_PATH.resolve()}]')
        try:
            variables.DATA_PATH.mkdir(parents=True)
        except Exception as e:
            logger.error(f'Unable to create data directory [{variables.DATA_PATH.resolve()}]: {e}')
            sys.exit(1)
    else:
        if not variables.DATA_PATH.is_dir():
            logger.error(f'Unable to find a valid data path for [{variables.DATA_PATH.resolve()}]')
            sys.exit(1)
    tools = load_tools(args.tools, repo_path, logger, report_path, variables.LOG_ENV)
    if tools is False:
        sys.exit(1)
    logger.info(f'Tools loaded: {", ".join([tool["name"] for tool in tools])}')
    for tool in tools:
        logger.info(f'Running {tool["name"]}')
        if not tool['object'].process():
            logger.error(f'Failed to run {tool["name"]}')

if __name__ == "__main__":
    main()
