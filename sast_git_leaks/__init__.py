'''
Sast Git Leaks

Copyright 2020 Leboncoin
Licensed under the Apache License
Written by Fabien Martinez <fabien.martinez+github@adevinta.com>
'''
from importlib import import_module
from pathlib import Path

from . import logger as logging
from . import utils


def load_tool(variables, tool: dict, path: Path, logger: logging, report_path: Path, loggername: str, limit: int):
    '''
    Load tool module then instantiate tool
    '''
    for variable in variables.MANDATORY_TOOL_VARIABLES:
        if variable not in tool:
            logger.error(f'Unable to find mandatory variable {variable}!')
            return False
    try:
        obj = getattr(
            import_module(f'.{tool["name"]}', variables.MODULE_TOOLS_PATH),
            tool['class']
            )(
                tool,
                path,
                variables.DATA_PATH,
                report_path,
                loggername,
                limit
            )
    except Exception as e:
        logger.error(f'Unable to load {tool["name"]}: {e}', exc_info=True)
        return False
    else:
        logger.info(f'Tool {tool["name"]} loaded')
        return obj


def load_tools(variables, tools_loaded: str, path: Path, logger: logging, report_path: Path, loggername: str, limit: int):
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
    logger.info('Loading tools...')
    for data in tools_to_load.values():
        obj = load_tool(variables, data, path, logger, report_path, loggername, limit)
        if obj is False:
            logger.info('Load tools  aborted.')
            return False
        tools.append({'name': data['name'], 'object': obj})
    return tools


def process(repo_path, output, variables, volume=None, limit=-1, tools='all'):
    logger = logging.getLogger(__name__)
    logger.info(f'Repository to check: {repo_path}')
    if not repo_path.is_dir():
        logger.error(f"Wront repo path [{repo_path}]!")
        return False
    report_path = Path(f'{output}.csv')
    logger.info(f'Report path: {report_path}')
    if volume is not None:
        variables.DATA_PATH = Path(volume)
    if not variables.DATA_PATH.exists():
        logger.info(f'Creating data folder [{variables.DATA_PATH.resolve()}]')
        try:
            variables.DATA_PATH.mkdir(parents=True)
        except Exception as e:
            logger.error(f'Unable to create data directory [{variables.DATA_PATH.resolve()}]: {e}')
            return False
    else:
        if not variables.DATA_PATH.is_dir():
            logger.error(f'Unable to find a valid data path for [{variables.DATA_PATH.resolve()}]')
            return False
    tools = load_tools(variables, tools, repo_path, logger, report_path, variables.LOG_ENV, limit)
    if tools is False:
        return False
    logger.info(f'Tools loaded: {", ".join([tool["name"] for tool in tools])}')
    for tool in tools:
        logger.info(f'Running {tool["name"]}')
        if not tool['object'].process():
            logger.error(f'Failed to run {tool["name"]}')
    data = utils.read_csv(report_path)
    if not utils.convert_csv_to_json(report_path, Path(output)):
        logger.error(f'Unable to convert csv file ({report_path.resolve()}) to json file ({args.output})')
    try:
        report_path.unlink()
    except Exception as e:
        logger.warning(f'Unable to remove {report_path.resolve()}: {e}')
    return data
