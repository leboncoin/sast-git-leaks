# -*- coding: utf-8 -*-
'''
Sast Git Leaks

Copyright 2020 Ankirama
Licensed under the Apache License
Written by Ankirama
'''
import csv
import json
from pathlib import Path

from . import logger as logging


def read_csv(path):
    '''
    Read csv file and return list of rows
    '''
    logger = logging.getLogger(__name__)
    logger.debug(f'Trying to get csv file [{path}]')
    try:
        with path.open(mode='r', encoding='utf-8') as f:
            try:
                csv_data = csv.DictReader(f)
            except Exception as e:
                logger.error(f'Unable to get csv data from [{path.resolve()}]: {e}')
                return False
    except Exception as e:
        logger.error(f'Unable to read file [{path.resolve()}]: {e}')
        return False
    else:
        if csv_data.line_num == 0:
            return []
        data = [line for line in csv_data]
        logger.info(f'Data successfuly extracted from [{path}]')
        return data


def read_json(path):
    '''
    Read json file and return a dict
    '''
    logger = logging.getLogger(__name__)
    logger.debug(f'Trying to get json file [{path}]')
    try:
        with path.open(mode='r', encoding='utf-8') as f:
            try:
                json_data = json.load(f)
            except Exception as e:
                logger.error(f'Unable to get json data from [{path.resolve()}]: {e}')
                return False
    except Exception as e:
        logger.error(f'Unable to read file [{path.resolve()}]: {e}')
        return False
    else:
        logger.info(f'Data successfuly extracted from [{path}]')
        return json_data


def clean_file(path: Path, logger) -> bool:
    '''
    Check if file exists, then remove it
    '''
    if path.exists():
        if path.is_file():
            try:
                path.unlink()
            except Exception as e:
                logger.error(f'Unable to remove file [{path.resolve()}]: {e}')
                return False
            else:
                logger.info(f'File [{path.resolve()}] removed')
                return True
        else:
            logger.error(f'Wrong type file for [{path.resolve()}]: Aborted')
            return False
    return True