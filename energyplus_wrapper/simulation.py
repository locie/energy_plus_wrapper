#!/usr/bin/env python
# coding=utf-8

import attr
from path import Path
from plumbum import ProcessExecutionError

from .utils import process_eplus_html_report, process_eplus_time_series


@attr.s
class Simulation:
    name = attr.ib(type=str)
    idf_file = attr.ib(type=str, converter=Path)
    epw_file = attr.ib(type=str, converter=Path)
    idd_file = attr.ib(type=str, converter=Path)

    working_dir = attr.ib(type=str, converter=Path)

    status = attr.ib(type=str, default="pending")
    _log = attr.ib(type=str, default="", init=False, repr=False)
    reports = attr.ib(type=dict, default=None, repr=False)
    time_series = attr.ib(type=dict, default=None, repr=False)

    def _process_results(self):
        self.reports = dict(
            process_eplus_html_report(self.working_dir / "eplus-table.htm")
        )
        self.time_series = dict(process_eplus_time_series(self.working_dir))

    @property
    def log(self):
        return self._log

    def run(self, cmd):
        self.status = "running"
        try:
            self.status = "running"
            self._log = cmd[self.epw_file, self.idf_file]()
            self.status = "finished"
        except ProcessExecutionError:
            self.status = "failed"
            raise
        except KeyboardInterrupt:
            self.status = "interrupted"
            raise
        self._process_results()
        return self.reports

    def backup(self, backup_dir):
        (backup_dir / f"{self.status}_{self.name}").rmtree_p()
        backup_dir = Path(backup_dir).mkdir_p()
        self.working_dir.copytree(backup_dir / f"{self.status}_{self.name}")
