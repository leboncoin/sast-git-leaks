# -*- coding: utf-8 -*-
'''
Sast Git Leaks

Copyright 2020 Leboncoin
Licensed under the Apache License
Written by Fabien Martinez <fabien.martinez+github@adevinta.com>
'''
import csv
import json
from pathlib import Path

from . import logger as logging

LOGGER = logging.getLogger('Sast Git Leaks')

def read_csv(path: Path):
    '''
    Read csv file and return list of rows
    '''
    LOGGER.debug(f'Trying to get csv file [{path}]')
    try:
        with path.open(mode='r', encoding='utf-8') as f:
            try:
                csv_data = csv.DictReader(f)
            except Exception as e:
                LOGGER.error(f'Unable to get csv data from [{path.resolve()}]: {e}')
                return False
            try:
                data = [line for line in csv_data]
            except Exception as e:
                LOGGER.error(f'Unable to get csv data from [{path.resolve()}]: {e}')
                return False
    except Exception as e:
        LOGGER.error(f'Unable to read file [{path.resolve()}]: {e}')
        return False
    else:
        LOGGER.info(f'Data successfully extracted from [{path}]')
        return data


def write_csv(path: Path, data: list, headers: list, write_headers=False):
    '''
    Write data in csv file
    '''
#    LOGGER.info(f'Adding {len(data)} rows in file {path.resolve()}')
    try:
        with path.open(mode='a', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers, delimiter=',', quotechar='"')
            if write_headers:
                writer.writeheader()
            for line in data:
                writer.writerow(line)
    except Exception as e:
        LOGGER.error(f'Unable to add lines in {path.resolve()}: {e}')
        return False
    else:
        return True

def read_json(path: Path):
    '''
    Read json file and return a dict
    '''
    LOGGER.debug(f'Trying to get json file [{path}]')
    try:
        with path.open(mode='r', encoding='utf-8') as f:
            try:
                json_data = json.load(f)
            except Exception as e:
                LOGGER.error(f'Unable to get json data from [{path.resolve()}]: {e}')
                return False
    except Exception as e:
        LOGGER.error(f'Unable to read file [{path.resolve()}]: {e}')
        return False
    else:
        LOGGER.info(f'Data successfully extracted from [{path}]')
        return json_data


def create_dir(path: Path) -> bool:
    '''
    Check if directory exists, if not create it
    '''
    if path.exists():
        if not path.is_dir():
            LOGGER.error(f'Unable to create {path.resolve()}: It already exists and isn\'t a dir')
            return False
        else:
            LOGGER.debug(f'Directory {path.resolve()} already exists.')
            return True
    else:
        try:
            path.mkdir(parents=True)
        except Exception as e:
            LOGGER.error(f'Unable to create directory [{path.resolve()}]: {e}')
            return False
    return True


def clean_file(path: Path) -> bool:
    '''
    Check if file exists, then remove it
    '''
    LOGGER.debug(f'Removing file {path.resolve()}')
    if path.exists():
        if path.is_file():
            try:
                path.unlink()
            except Exception as e:
                LOGGER.error(f'Unable to remove file [{path.resolve()}]: {e}')
                return False
            else:
                LOGGER.info(f'File [{path.resolve()}] removed')
                return True
        else:
            LOGGER.error(f'Wrong type file for [{path.resolve()}]: Aborted')
            return False
    return True
