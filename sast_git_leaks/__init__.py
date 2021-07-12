'''
Sast Git Leaks

Copyright 2020 Leboncoin
Licensed under the Apache License
Written by Fabien Martinez <fabien.martinez+github@adevinta.com>
'''
from importlib import import_module
from pathlib import Path
import logging

from . import utils


LOGGER = logging.getLogger(__name__)


def load_tool(variables, tool: dict, path: Path, report_path: Path, limit: int):
    '''
    Load tool module then instantiate tool
    '''
    for variable in variables.MANDATORY_TOOL_VARIABLES:
        if variable not in tool:
            LOGGER.error(f'Unable to find mandatory variable {variable}!')
            return False
    try:
        obj = getattr(
            import_module(f'.{tool["name"]}', variables.MODULE_TOOLS_PATH),
            tool['class']
            )(
                LOGGER,
                tool,
                path,
                variables.DATA_PATH,
                report_path,
                limit
            )
    except Exception as e:
        LOGGER.error(f'Unable to load {tool["name"]}: {e}', exc_info=True)
        return False
    else:
        LOGGER.info(f'Tool {tool["name"]} loaded')
        return obj


def load_tools(variables, tools_loaded: str, path: Path, report_path: Path, limit: int):
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
    LOGGER.info('Loading tools...')
    for data in tools_to_load.values():
        obj = load_tool(variables, data, path, report_path, limit)
        if obj is False:
            LOGGER.info('Load tools  aborted.')
            return False
        tools.append({'name': data['name'], 'object': obj})
    return tools


def process(logger, repo_path, output, variables, volume=None, limit=-1, tools='all'):
    global LOGGER
    LOGGER = logger
    utils.set_logger(logger)
    LOGGER.info(f'Repository to check: {repo_path}')
    if not repo_path.is_dir():
        LOGGER.error(f"Wrong repo path {repo_path}")
        return False
    report_path = Path(f'{output}.csv')
    LOGGER.info(f'Report path: {report_path}')
    if volume is not None:
        variables.DATA_PATH = Path(volume)
    if not variables.DATA_PATH.exists():
        LOGGER.info(f'Creating data folder {variables.DATA_PATH.resolve()}')
        try:
            variables.DATA_PATH.mkdir(parents=True)
        except Exception as e:
            LOGGER.error(f'Unable to create data directory {variables.DATA_PATH.resolve()}: {e}')
            return False
    else:
        if not variables.DATA_PATH.is_dir():
            LOGGER.error(f'Unable to find a valid data path for {variables.DATA_PATH.resolve()}')
            return False
    tools = load_tools(variables, tools, repo_path, report_path, limit)
    if tools is False:
        return False
    LOGGER.info(f'Tools loaded: {", ".join([tool["name"] for tool in tools])}')
    for tool in tools:
        LOGGER.info(f'Running {tool["name"]}')
        try:
            if not tool['object'].process():
                LOGGER.error(f'Failed to run {tool["name"]}')
        except Exception as e:
            LOGGER.error(f'Failed to run {tool["name"]} process method: {e}')
            if tool['object']._check_lock_file():
                tool['object']._remove_lock_file()
    try:
        data = utils.read_csv(report_path)
    except Exception as e:
        LOGGER.error(f'Unable to read csv data from {report_path}: {e}')
        return False
    else:
        if not utils.convert_csv_to_json(report_path, Path(output)):
            LOGGER.error(f'Unable to convert csv file ({report_path.resolve()}) to json file ({args.output})')
        try:
            report_path.unlink()
        except Exception as e:
            LOGGER.warning(f'Unable to remove {report_path.resolve()}: {e}')
        return data
