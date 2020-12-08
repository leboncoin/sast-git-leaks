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
    _min_number_commits = 10
    _commits = list()

    def __init__(self, data: dict, path: Path, data_path: Path, report_path: Path, loggername: str, limit: int) -> None:
        self._logger = logging.getLogger(loggername)
        super().__init__(data, path, data_path, report_path, loggername, limit)
        self._tool_data['last_commit_path'] = data_path / data['data_last_commit_filename'].format(
            name=self._tool_data['name'],
            repo=path.parts[-1].replace(' ', '_').lower()
        )
        self._tool_data['last_commit_cmd'] = self._tool_data['last_commit_cmd'].format(
            repo_path=path.resolve()
        )
        self._commits = self._get_commits_from_log(path.resolve())
        if self._tool_data['number_commits'] < self._min_number_commits:
            self._tool_data['number_commits'] = self._min_number_commits
        if self._check_last_commit():
            self._tool_data['cmd_get_nth_commit'] += self._tool_data['cmd_get_nth_commit_from'].format(commit=self._tool_data["last_commit"])

    def _check_last_commit(self) -> bool:
        '''
        Try to check if he can find the last commit used
        Return last commit or None
        '''
        self._logger.debug('Checking last commit...')
        if self._tool_data['last_commit_path'].exists():
            if not self._tool_data['last_commit_path'].is_file():
                raise Expection(f'Bad path for last commit [{self._tool_data["last_commit_path"].resolve()}]')
            try:
                self._tool_data['last_commit'] = self._tool_data['last_commit_path'].read_text().rstrip()
            except Exception as e:
                raise Exception(f'Unable to read last commit file [{self._tool_data["last_commit_path"].resolve()}]: {e}')
            else:
                self._logger.info(f'Last commit found: {self._tool_data["last_commit"]}')
                return True
        else:
            return False

    def _update_last_commit(self) -> bool:
        '''
        Update last commit checked to optimize gitleaks
        '''
        self._logger.debug('Updating last commit file')
        if "last_commit" not in self._tool_data or len(self._tool_data["last_commit"]) == 0:
            self._logger.error('Unable to find last commit hash')
            return False
        else:
            last_commit = self._tool_data['last_commit']
            if last_commit is not None:
                last_commit = last_commit.rstrip()
                if re.fullmatch(r'^[0-9a-f]+$', last_commit) is not None:
                    if not self._tool_data["last_commit_path"].parent.exists():
                        try:
                            self._tool_data["last_commit_path"].parent.mkdir(parents=True)
                        except Exception as e:
                            self._logger.error(f'Unable to create directory [{self._tool_data["last_commit_path"].parent.resolve()}]: {e}')
                            return False
                    try:
                        self._tool_data["last_commit_path"].write_text(f'{last_commit}\n')
                    except Exception as e:
                        self._logger.error(f'Unable to update last commit file [{self._tool_data["last_commit_path"]}]: {e}')
                        return False
                    else:
                        self._tool_data["last_commit"] = last_commit
                else:
                    self._logger.error(f'Unable to find valid sha1 (size 40), found: [{self._tool_data["last_commit"]}]')
                    return False
            else:
                self._logger.error('Unable to find output for the last commit command')
                return False
            self._logger.info(f'Last commit file updated: {self._tool_data["last_commit"]}')
            return True

    def load_data(self, path: Path) -> bool:
        '''
        Loads data and import them from json format
        We don't consider an undifined file as an error because
        some tools may not generate report
        '''
        self._logger.debug("LOADING DATA")
        if not path.exists():
            self._logger.debug(f'No report found for [{path.resolve()}]')
            return True
        self._logger.debug("PATH ==> {}".format(path))
        data = read_json(path)
        self._logger.debug("DATA ==> {}".format(data))
        if data is not False:
            self._tool_report = data
        return data != False

    def generate_report(self) -> bool:
        '''
        Generate data from _data
        '''
        self._logger.info('Generating report')
        for line in self._tool_report:
            self._report.append({
                'title': f'[{self._tool_data["name"]}]: {line["rule"]}',
                'criticity': 'medium',
                'component': line['file'],
                'reason': f'Commit: `{line["commit"]}` | Rule: **{line["rule"]}** | Code: `{line["line"]}`'
            })
        return True

    def _get_commits_from_log(self, path):
        '''
        Get commits from git log command
        '''
        command = self._tool_data['cmd_get_commits'].format(repo_path=path)
        if "last_commit" in self._tool_data and  self._tool_data["last_commit"] is not None:
            command += f'{self._tool_data["last_commit"]}..'
        if not self._run_command(command):
            self._logger.error(f'Unable to get commits from {command}')
            return False
        commits = self._output_command.rstrip().split('\n')
        return commits

    def _get_commit_from_log(self, command: str):
        '''
        Use command to get a commit from git log and try to return it
        '''
        if not self._run_command(command):
            return False
        git_to_commit = self._output_command
        if len(git_to_commit) == 0:
            return None
        else:
            return git_to_commit

    def process(self, generate_report=True, write_report=True, clean=True) -> bool:
        '''
        Generate report, then add last commit checked
        As git repo may be big, we have to split it
        '''
        self._logger.debug("Processing...")
        if self._check_lock_file():
            self._logger.warning(f'{self._tool_data["name"].capitalize()}: Repo {self._repo_path} is already being inspected')
            return False
        else:
            if not self._create_lock_file():
                return False
        index = 0
        commits = self._commits
        if self._limit > 0:
            if self._limit < len(self._commits):
                commits = self._commits[:self._limit]
        commits_reverse = commits[::-1]
        while index < len(commits_reverse):
            self._logger.debug(f'Index [{index}]')
            end = index + self._tool_data['number_commits'] - 1
            if end >= len(commits_reverse):
                end = -1
            commit_from = commits_reverse[end]
            commit_to = commits_reverse[index]
            command = self._command
            command += self._tool_data['arg_commit_from'].format(commit=commit_from)
            command += self._tool_data['arg_commit_to'].format(commit=commit_to)
            self._logger.debug(f'Command to run => {command}')
            if not self._run_command(command):
                self._logger.error(f'Unable to run command. Aborted!')
                if clean:
                    self.clean()
                self._remove_lock_file()
                return False
            else:
                self._tool_data["last_commit"] = commit_from
                if not self._update_last_commit():
                    self._logger.warning('Unable to update last commit, next check will start from the old last commit (if any)')
            if generate_report:
                if not self.load_data(self._tool_report_path):
                    if clean:
                        self.clean()
                    self._remove_lock_file()
                    return False
                if not self.generate_report():
                    self._logger.error(f'Unable to generate report for index {index}: Aborted.')
                    if clean:
                        self.clean()
                    self._remove_lock_file()
                    return False
            if write_report:
                if not self.write_csv_report():
                    self._logger.error(f'Unable to write report for index {index}: Aborted.')
                    if clean:
                        self.clean()
                    self._remove_lock_file()
                    return False
                else:
                    self.clean()
            index += self._tool_data['number_commits']
        self._remove_lock_file()
        return True
