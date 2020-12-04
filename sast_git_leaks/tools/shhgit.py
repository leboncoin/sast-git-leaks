# -*- coding: utf-8 -*-
'''
Sast Git Leaks

Copyright 2020 Leboncoin
Licensed under the Apache License
Written by Fabien Martinez <fabien.martinez+github@adevinta.com>
'''
from pathlib import Path

from .import ToolAbstract
from ..utils import read_csv
from .. import logger as logging


class Shhgit(ToolAbstract):
    def __init__(self, data: dict, path: Path, data_path: Path, report_path: Path, loggername: str, limit: int) -> None:
        self._logger = logging.getLogger(loggername)
        super().__init__(data, path, data_path, report_path, loggername, limit)

    def load_data(self, path: Path):
        '''
        Loads data and import them from csv format
        We don't consider an undifined file as an error because
        some tools may not generate report
        '''
        if not path.exists():
            self._logger.debug(f'No report found for [{path.resolve()}]')
            return True
        data = read_csv(path)
        if data is not False:
            self._tool_report = data
        return data != False

    def generate_report(self) -> bool:
        '''
        Generate data from _data
        '''
        for line in self._tool_report:
            matches = line["Signature name"]
            if len(line["Matches"]) > 0:
                matches = line["Matches"]
            self._report.append({
                'title': f'[{self._tool_data["name"]}]: {line["Signature name"]}',
                'criticity': 'medium',
                'component': line['Matching file'],
                'reason': matches
            })
        return True
