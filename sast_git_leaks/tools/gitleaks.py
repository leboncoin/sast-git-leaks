# -*- coding: utf-8 -*-
'''
Sast Git Leaks

Copyright 2020 Leboncoin
Licensed under the Apache License
Written by Fabien Martinez <fabien.martinez+github@adevinta.com>
'''
from pathlib import Path
import re

from .import ToolAbstract
from ..utils import read_json
from .. import logger as logging


class Gitleaks(ToolAbstract):
    _last_commit_cmd = None
    _last_commit_path = None
    _last_commit = None

    def __init__(self, data: dict, path: Path, data_path: Path, report_path: Path) -> None:
        self._logger = logging.getLogger(__name__)
        self._last_commit_path = data_path / data['data_last_commit_filename'].format(
            name=data['name'],
            repo=path.parts[-1].replace(' ', '_').lower()
        )
        self._last_commit_cmd = data['last_commit_cmd'].format(
            repo_path=path.resolve()
        )
        if self._check_last_commit():
            self._logger.info(f'Last commit found: [{self._last_commit}]')
            data['args'] += data['arg_commit'].format(
                commit=self._last_commit
            )
        super().__init__(data, path, data_path, report_path)

    def _check_last_commit(self) -> bool:
        '''
        Try to check if he can find the last commit used
        Return last commit or None
        '''
        self._logger.debug('Checking last commit...')
        if self._last_commit_path.exists():
            if not self._last_commit_path.is_file():
                raise Expection(f'Bad path for last commit [{self._last_commit_path.resolve()}]')
            try:
                self._last_commit = self._last_commit_path.read_text().rstrip()
            except Exception as e:
                raise Exception(f'Unable to read last commit file [{self._last_commit_path.resolve()}]: {e}')
            else:
                self._logger.info(f'Last commit found: {self._last_commit}')
                return True
        else:
            return False

    def _update_last_commit(self) -> bool:
        '''
        Update last commit checked to optimize gitleaks
        '''
        self._logger.debug('Updating last commit file')
        if not self._run_command(self._last_commit_cmd):
            self._logger.error('Unable to update last commit file')
            return False
        else:
            last_commit = self._output_command
            if last_commit is not None:
                last_commit = last_commit.rstrip()
                if re.fullmatch(r'^[0-9a-f]{40}$', last_commit) is not None:
                    if not self._last_commit_path.parent.exists():
                        try:
                            self._last_commit_path.parent.mkdir(parents=True)
                        except Exception as e:
                            self._logger.error(f'Unable to create directory [{self._last_commit_path.parent.resolve()}]: {e}')
                            return False
                    try:
                        self._last_commit_path.write_text(f'{last_commit}\n')
                    except Exception as e:
                        self._logger.error(f'Unable to update last commit file [{self._last_commit_path}]: {e}')
                        return False
                    else:
                        self._last_commit = last_commit
                else:
                    self._logger.error(f'Unable to find valid sha1 (size 40), found: [{self._last_commit}]')
                    return False
            else:
                self._logger.error('Unable to find output for the last commit command')
                return False
            self._logger.info(f'Last commit file updated: {self._last_commit}')
            return True

    def load_data(self, path: Path) -> bool:
        '''
        Loads data and import them from json format
        We don't consider an undifined file as an error because
        some tools may not generate report
        '''
        if not path.exists():
            self._logger.debug(f'No report found for [{path.resolve()}]')
            return True
        data = read_json(path)
        if data is not False:
            self._data = data
        return data != False

    def generate_report(self) -> None:
        '''
        Generate data from _data
        '''
        self._logger.info('Generating report')
        for line in self._data:
            self._report.append({
                'title': f'[{self._name}]: {line["rule"]}',
                'criticity': 'medium',
                'component': line['file'],
                'reason': f'Commit: `{line["commit"]}\nRule: `{line["rule"]}\nCode: `{line["line"]}`'
            })

    def process(self) -> bool:
        '''
        Generate report, then add last commit checked
        '''
        if not super().process():
            return False
        if not self._update_last_commit():
            self._logger.warning('Unable to update last commit, next check will start from the old last commit (if any)')
        return True
