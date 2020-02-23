#!/usr/bin/env python
# coding=utf-8

import re
from typing import Callable, Dict, Mapping, Optional, Tuple, Union
from warnings import warn

import attr
import plumbum
from coolname import generate_slug
from eppy.modeleditor import IDF as eppy_IDF
from joblib import Parallel, delayed
from path import Path, tempdir, tempfile
from plumbum import ProcessExecutionError

from .simulation import Simulation

eplus_version_pattern = re.compile(r"EnergyPlus, Version (\d\.\d)")
idf_version_pattern = re.compile(r"EnergyPlus Version (\d\.\d)")
idd_version_pattern = re.compile(r"IDD_Version (\d\.\d)")


@attr.s
class EPlusRunner:
    """Object that contains all that is needed to run an EnergyPlus simulation.

    Attributes:
        energy_plus_root (Path): EnergyPlus root, where live the executable
            and the IDD file.
        temp_dir (Path, optional): where live the temporary files generated
            by EnergyPlus.
    """

    energy_plus_root = attr.ib(type=str, converter=Path)
    temp_dir = attr.ib(type=str, factory=tempfile.gettempdir)

    def get_idf_version(self, idf_file: Path) -> str:
        """extract the eplus version affiliated with the idf file.

        Arguments:
            idf_file {Path} -- idf file emplacement

        Returns:
            str -- the version as "{major}.{minor}" (e.g. "8.7")
        """
        with open(idf_file) as f:
            idf_str = f.read()
            try:
                version = idf_version_pattern.findall(idf_str)[0]
            except IndexError:
                version = False
        return version

    @property
    def idd_version(self) -> str:
        """Get the eplus version affiliated with the idd file.

        Returns:
            str -- the version as "{major}.{minor}" (e.g. "8.7")
        """
        with open(self.idd_file) as f:
            idd_str = f.read()
            try:
                version = idd_version_pattern.findall(idd_str)[0]
            except IndexError:
                version = False
        return version

    @property
    def eplus_version(self) -> str:
        """Get the eplus version for the executable itself.

        Returns:
            str -- the version as "{major}.{minor}" (e.g. "8.7")
        """
        version = eplus_version_pattern.findall(plumbum.local[self.eplus_bin]("-v"))[0]
        return version

    @property
    def idd_file(self) -> Path:
        """Get the idd file given in the EnergyPlus folder.

        Returns:
            Path -- idd file emplacement
        """
        return self.energy_plus_root / "Energy+.idd"

    @property
    def eplus_bin(self) -> Path:
        """Get the EnergyPlus executable.

        Returns:
            Path -- Eplus binary emplacement
        """
        for bin_name in ["energyplus", "EnergyPlus.exe"]:
            eplus_bin = self.energy_plus_root / "energyplus"
            if eplus_bin.exists():
                return eplus_bin
        raise FileNotFoundError("Unable to find an e+ executable in the provided energy_plus_root.")

    def check_version_compat(self, idf_file, version_mismatch_action="raise") -> bool:
        """Check version compatibility between the IDF and the EnergyPlus
        binary. Raise an error or warn the user according to
        `version_mismatch_action`.

        Arguments:
            idf_file {Path} -- idf file emplacement
            version_mismatch_action {str} -- either ["raise", "warn", "ignore"]
        Returns:
            bool -- True if the versions are the same.
        """
        if version_mismatch_action not in ["raise", "warn", "ignore"]:
            raise ValueError(
                "`version_mismatch_action` argument should be either"
                " 'raise', 'warn', 'ignore'."
            )
        idf_version = self.get_idf_version(idf_file)
        eplus_version = self.eplus_version
        if idf_version != eplus_version:
            msg = (
                f"idf version ({idf_version}) and EnergyPlus version ({eplus_version}) "
                " does not match. According to the EnergyPlus versions, this can "
                " prevent the simulation to run or lead to silent error."
            )
            if version_mismatch_action == "raise":
                raise ValueError(msg)
            elif version_mismatch_action == "warn":
                warn(msg)
            return False
        return True

    def run_one(
        self,
        idf: Union[Path, eppy_IDF, str],
        epw_file: Path,
        backup_strategy: str = "on_error",
        backup_dir: Path = "./backup",
        simulation_name: Optional[str] = None,
        custom_process: Optional[Callable[[Simulation], None]] = None,
        version_mismatch_action: str = "raise",
    ) -> Simulation:
        """Run an EnergyPlus simulation with the provided idf and weather file.

        The IDF can be either a filename or an eppy IDF
        object.

        This function is process safe (as opposite as the one available in `eppy`).

        Arguments:
            idf {Union[Path, eppy_IDF, str]} -- idf file as filename or eppy IDF object.
            epw_file {Path} -- Weather file emplacement.

        Keyword Arguments:
            backup_strategy {str} -- when to save the files generated by e+
                (either"always", "on_error" or None) (default: {"on_error"})
            backup_dir {Path} -- where to save the files generated by e+
                (default: {"./backup"})
            simulation_name {str, optional} -- The simulation name. A random will be
                generated if not provided.
            custom_process {Callable[[Simulation], None], optional} -- overwrite the
                simulation post - process. Used to customize how the EnergyPlus files
                are treated after the simulation, but before cleaning the folder.
            version_mismatch_action {str} -- should be either ["raise", "warn",
                "ignore"] (default: {"raise"})

        Returns:
            Simulation -- the simulation object
        """
        if simulation_name is None:
            simulation_name = generate_slug()

        if backup_strategy not in ["on_error", "always", None]:
            raise ValueError(
                "`backup_strategy` argument should be either 'on_error', 'always'"
                " or None."
            )
        backup_dir = Path(backup_dir)

        with tempdir(prefix="energyplus_run_", dir=self.temp_dir) as td:
            if isinstance(idf, eppy_IDF):
                idf = idf.idfstr()
                idf_file = td / "eppy_idf.idf"
                with open(idf_file, "w") as idf_descriptor:
                    idf_descriptor.write(idf)
            else:
                idf_file = idf
                if version_mismatch_action in ["raise", "warn"]:
                    self.check_version_compat(
                        idf_file, version_mismatch_action=version_mismatch_action
                    )
            idf_file, epw_file = (Path(f).abspath() for f in (idf_file, epw_file))

            with td:
                idf_file.copy(td)
                epw_file.copy(td)
                sim = Simulation(
                    simulation_name,
                    self.eplus_bin,
                    idf_file,
                    epw_file,
                    self.idd_file,
                    working_dir=td,
                    post_process=custom_process,
                )
                try:
                    sim.run()
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
        samples: Mapping[str, Tuple[Union[Path, eppy_IDF, str], Path]],
        epw_file: Optional[Path] = None,
        backup_strategy: str = "on_error",
        backup_dir: Path = "./backup",
        custom_process: Optional[Callable[[Simulation], None]] = None,
        version_mismatch_action: str = "raise",
    ) -> Dict[str, Simulation]:
        """Run multiple EnergyPlus simulation.

        Arguments:
            samples {mapping key: idf or (idf, weather_file)} -- A dict that contain a
                `run_one` arguments.
            epw_file {Path} -- Weather file emplacement. If None, it has to be in
                the samples. Otherwise, a unique weather file is used for each run.

        Keyword Arguments:
            backup_strategy {str} -- when to save the files generated by e+
                (either "always", "on_error" or None) (default: {"on_error"})
            backup_dir {Path} -- where to save the files generated by e+
                (default: {"./backup"})
            custom_process {Callable[[Simulation], None], optional} -- overwrite the
                simulation post - process. Used to customize how the EnergyPlus
                files are treated after the simulation, but before the folder clean.
            version_mismatch_action {str} -- should be either ["raise", "warn",
                "ignore"] (default: {"raise"})

        Returns:
            Dict[str, Simulation] -- the results put in a dictionnary with the same
                keys as the samples.
        """
        if epw_file and any([not isinstance(value, (Path, str, eppy_IDF)) for value in samples.values()]):
            raise ValueError("If epw_file is not None, samples should be a dict as {sim_name: idf}.")
        if epw_file:
            samples = {key: (idf, epw_file) for key, idf in samples.items()}
        sims = Parallel()(
            delayed(self.run_one)(
                idf,
                epw_file,
                backup_strategy=backup_strategy,
                backup_dir=backup_dir,
                simulation_name=key,
                custom_process=custom_process,
                version_mismatch_action=version_mismatch_action
            )
            for key, (idf, epw_file) in samples.items()
        )
        return {key: sim for key, sim in zip(samples.keys(), sims)}
