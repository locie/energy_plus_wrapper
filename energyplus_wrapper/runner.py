#!/usr/bin/env python
# coding=utf-8

import re
from warnings import warn

import attr
import plumbum
from joblib import Parallel, delayed
from path import Path, tempdir, tempfile
from plumbum import ProcessExecutionError

from coolname import generate_slug
from eppy.modeleditor import IDF

from .simulation import Simulation

idf_version_pattern = re.compile(r"EnergyPlus Version (\d\.\d)")
idd_version_pattern = re.compile(r"IDD_Version (\d\.\d)")

@attr.s
class EPlusRunner:
    energy_plus_root = attr.ib(type=str, converter=Path)
    temp_dir = attr.ib(type=str, factory=tempfile.gettempdir)

    def check_idf_version(self, idf_file):
        with open(idf_file) as f:
            idf_str = f.read()
            version = idf_version_pattern.findall(idf_str)[0]
        return version

    @property
    def eplus_version(self):
        with open(self.idd_file) as f:
            idd_str = f.read()
            version = idd_version_pattern.findall(idd_str)[0]
        return version

    @property
    def eplus_base_exec(self):
        return plumbum.local[self.energy_plus_root / "energyplus"]

    @property
    def eplus_cmd(self):
        return self.eplus_base_exec["-s", "d", "-r", "-x", "-i", self.idd_file, "-w"]

    @property
    def idd_file(self):
        return self.energy_plus_root / "Energy+.idd"

    def check_version_compat(self, idf_file, version_mismatch_action="raise"):
        idf_version = self.check_idf_version(idf_file)
        eplus_version = self.eplus_version
        if idf_version != eplus_version:
            msg = (f"idf version ({idf_version}) and EnergyPlus version ({eplus_version}) does not match."
                    " According to the EnergyPlus versions, this can prevent the simulation to run"
                    " or lead to silent error.")
            if version_mismatch_action == "raise":
                raise ValueError(msg)
            elif version_mismatch_action == "warn":
                warn(msg)
            return False
        return True

    def run_one(
        self,
        idf,
        epw_file,
        backup_strategy="on_error",
        backup_dir="./backup",
        simulation_name=None,
        custom_process=None,
        version_mismatch_action="raise",
    ):
        if simulation_name is None:
            simulation_name = generate_slug()

        if backup_strategy not in ["on_error", "always", None]:
            raise ValueError(
                "`backup_strategy` argument should be either 'on_error', 'always' or None."
            )
        backup_dir = Path(backup_dir).abspath()

        with tempdir(dir=self.temp_dir) as td, td:
            idf_file = idf
            if not Path(idf_file).exists():
                idf_file = td / "eppy_idf.idf"
                if isinstance(idf, IDF):
                    # it's a eppy IDF file, we have to translate before writting it
                    idf = idf.idfstr()
                with open(idf_file, "w") as idf_descriptor:
                    idf_descriptor.write(idf)
            idf_file, epw_file = map(Path, (idf_file, epw_file))
            self.check_version_compat(idf_file, version_mismatch_action=version_mismatch_action)

            sim = Simulation(
                simulation_name, idf_file, epw_file, self.idd_file, working_dir=td
            )
            if custom_process is not None:
                sim._process_results = custom_process
            try:
                sim.run(self.eplus_cmd)
            except (ProcessExecutionError, KeyboardInterrupt):
                if backup_strategy == "on_error":
                    sim.backup(backup_dir)
                raise
            finally:
                if backup_strategy == "always":
                    sim.backup(backup_dir)

        return sim

    def run_many(
        self,
        samples,
        backup_strategy="on_error",
        backup_dir="./backup",
        simulation_name=None,
        custom_process=None,
    ):
        sims = Parallel()(
            delayed(self.run_one)(
                idf,
                epw_file,
                backup_strategy="on_error",
                backup_dir="./backup",
                simulation_name=None,
                custom_process=None,
            )
            for idf, epw_file in samples.values()
        )
        return {key: sim for key, sim in zip(samples.keys(), sims)}
