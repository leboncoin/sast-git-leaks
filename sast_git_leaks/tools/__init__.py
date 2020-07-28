# -*- coding: utf-8 -*-
'''
Sast Git Leaks

Copyright 2020 Leboncoin
Licensed under the Apache License
Written by Fabien Martinez <fabien.martinez+github@adevinta.com>
'''
from typing import Union
from subprocess import getstatusoutput, Popen, PIPE
import shlex
import json
from pathlib import Path

from .. import utils

class ToolAbstract():
    '''
    Abstract class to help create child class
    '''
    _logger = None
    _data = []
    _report_path = None
    _report = list()
    _output_command = None
    _path = None
    _data_path = None
    _name = "Tool"
    _tool_report_path = None

    def __init__(self, data: dict, path: Path, data_path: Path, report_path: Path) -> None:
        '''
        data must at least contains:
            - cmd
            - bin
            - args
            - report

        cmd must have 3 format variables:
            - binary
            - args
            - path
        '''
        try:
            self._command = data['cmd'].format(
                binary=data['bin'],
                args=data['args'],
                path=path
            )
        except KeyError as e:
            raise Exception(f'Bad command! Check your config. Unable to find key [{e}]')
        except Exception as e:
            raise Exception(f'Unable to set command: {e}')
        self._name = data['name']
        self._data_path = data_path
        if not self._check_binary(data['bin']):
            raise Exception(f"Unable to find [{data['bin']}]")
        self._path = path
        self._tool_report_path = data['report']
        if not utils.create_dir(data['report'].parent, self._logger):
            raise Exception(f'Unable to create report directory!')
        self._report_path = report_path
        if self._report_path.exists():
            if not self._report_path.is_file():
                raise Exception(f'Unable to create {self._report_path.parts[-1]}: it already exists and isn\'t a file')
            else:
                self._report = utils.read_json(self._report_path)
                if self._report is False:
                    raise Exception(f'Unable to get report file content from [{self.report_path.resolve()}]')
        if not self._report_path.parent.exists():
            self._logger.warning(f'Directory [{self._report_path.parent.resolve()}] doesn\'t exist, creating it')
            try:
                self._report_path.parent.mkdir(parents=True)
            except Exception as e:
                raise Exception(f'Unable to create directory [{self._report_path.parent.resolve()}]: {e}')

    def _check_binary(self, binary_path: str) -> bool:
        '''
        Check if binary is present on the OS
        '''
        try:
            res = getstatusoutput(f'{binary_path}')
        except Exception as e:
            self._logger.error(f'Unable to find {binary_path}: {e}')
            return False
        if len(res) == 0 or res[0] == 127:
            self._logger.error(f'Unable to find {binary_path}')
            return False
        return True

    def load_data(self, path: Path) -> bool:
        '''
        Load data from Path variable
        '''
        raise NotImplemented

    def generate_report(self) -> None:
        '''
        Generate data from _data
        '''
        raise NotImplemented

    def process(self) -> bool:
        '''
        Process data by:
            - Running run_command
            - Loading report
            - Formating report (if any report found)
        '''
        self._logger.debug("Processing...")
        if not self._run_command(self._command):
            self._logger.debug('Aborted!')
            return False
        if not self.load_data(self._tool_report_path):
            return False
        self.generate_report()
        return True

    def get_report_path(self) -> Path:
        '''
        Return report path
        '''
        return self._report_path

    def _prepare_command(self, command) -> Union[str, bool]:
        '''
        Split command with shlex.split
        '''
        self._logger.debug(f'Spliting command [{command}]')
        try:
            command_split = shlex.split(command)
        except Exception as e:
            self._logger.error(f'Unable to split command [{command}]: {e}')
            return False
        else:
            return command_split

    def _run_command(self, command) -> bool:
        '''
        Run command after spliting it
        It uses the subprocess.Popen function
        '''
        self._logger.debug(f'Running command [{command}]')
        command_split = self._prepare_command(command)
        if command_split is False:
            self._logger.error('Unable to run command: Bad split command!')
            return False
        try:
            proc = Popen(command_split, stdout=PIPE, stderr=PIPE)
        except Exception as e:
            self._logger.error(f'Unable to start command [{command}: {e}')
            return False
        else:
            try:
                o, e = proc.communicate()
            except Exception as e:
                self._logger.error(f'Unable to start command [{command}')
                return False
            else:
                if len(e) > 0:
                    self._logger.error(f'Error in execution: {e.decode("utf-8")}')
                    return False
                self._output_command = o.decode('utf-8')
                self._logger.debug(f'Output from [{command}]: {self._output_command}')
        return True

    def clean(self) -> bool:
        '''
        Clean tmp report created
        '''
        self._logger.info(f'Removing {self._tool_report_path.resolve()}')
        if not utils.clean_file(self._tool_report_path, self._logger):
            self._logger.warning('Unable to clean tmp files')
            return False
        return True

    def write_report(self) -> bool:
        '''
        Append lines in our report file
        We have to load the current report file, then add data in it
        Report format: [{
            'title': 'Title',
            'criticity': 'Medium',
            'component': '/path/to/file',
            'reason': 'key, reason, ...'
        }]
        '''
        old_report = list()
        try:
            with self._report_path.open('r') as f:
                old_report = json.load(f)
        except FileNotFoundError:
            pass
        except Exception as e:
            self._logger.error(f'Unable to read [{self._report_path.resolve()}]: {e}')
            return False
        report = old_report + self._report
        try:
            with self._report_path.open('w') as f:
                f.write(json.dumps(report, separators=(',', ':'), indent=4, sort_keys=False))
        except Exception as e:
            self._logger.error(f'Unable to update file [{self._report_path.resolve()}]: {e}')
            return False
        self._logger.info('Report updated')
        return True

    def get_report(self) -> dict:
        '''
        Return generated report from process method
        '''
        return self._report
