# -*- coding: utf-8 -*-
'''
Sast Git Leaks

Copyright 2020 Leboncoin
Licensed under the Apache License
Written by Ankirama
'''
from pathlib import Path

from .import ToolAbstract
from ..utils import read_csv
from .. import logger as logging


class Shhgit(ToolAbstract):
    def __init__(self, data: dict, path: Path) -> None:
        self._logger = logging.getLogger(__name__)
        super().__init__(data, path)

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
            self._data = data
        return data != False

    def generate_report(self) -> None:
        '''
        Generate data from _data
        '''
        for line in self._data:
            self._report.append({
                'title': line['Signature name'],
                'criticity': 'medium',
                'component': line['Matching file'],
                'reason': line['Matches']
            })
