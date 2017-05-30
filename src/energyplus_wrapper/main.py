#!/usr/bin/env python
# coding=utf8

import logging
import subprocess

import pandas as pd
from path import Path, tempdir

logger = logging.getLogger(__name__)
logger.handlers = []
logger.addHandler(logging.NullHandler())

eplus_logger = logging.getLogger('.'.join([__name__, 'e+_log']))
eplus_logger.handlers = []
eplus_logger.addHandler(logging.NullHandler())


EPLUS_DIRECTORY = None


def _log_subprocess_output(pipe):
    for line in iter(pipe.readline, b''):  # b'\n'-separated lines
        eplus_logger.info(line.decode().strip('\n'))


def _assert_files(idf_file, weather_file, working_dir,
                  idd_file, out_dir):
    """Ensure the files and directory are here and convert them as path.Path

    This function will coerce the string as a path.py Path and assert if
    mandatory files or directory are missing.
    """

    def get_idd(eplus_directory, idd_file):
        if not idd_file and eplus_directory:
            return Path(eplus_directory) / "Energy+.idd"
        if not idd_file:
            return Path("Energy+.idd")
        return Path(idd_file)

    idd_file = get_idd(EPLUS_DIRECTORY, idd_file)
    logger.debug('looking for idd file (%s)' % idd_file.abspath())

    if not idd_file.isfile():
        raise IOError("IDD file not found")

    working_dir = Path(working_dir)
    logger.debug(
        'checking if working directory (%s) exist' %
        working_dir.abspath())
    if not working_dir.isdir():
        raise IOError("Working directory does not exist")

    out_dir = Path(out_dir)
    logger.debug(
        'checking if output directory (%s) exist' %
        out_dir.abspath())
    if not out_dir.isdir():
        raise IOError("Output directory does not exist")

    weather_file = Path(weather_file)
    logger.debug('looking for weather file (%s)' % weather_file.abspath())
    if not weather_file.isfile():
        raise IOError("Weather file not found")

    idf_file = Path(idf_file)
    logger.debug('looking for idf file (%s)' % idf_file.abspath())
    if not idf_file.isfile():
        raise IOError("IDF file not found")

    return idf_file, weather_file, working_dir, idd_file, out_dir


def _exec_command_line(tmp, idd_file, idf_file, weather_file,
                       prefix, bin_path, keep_data_err, out_dir):
    """Build the command line used in subprocess.Popen

    Construct the command line passed as argument to subprocess.Popen
    """

    def get_bin_path(eplus_directory, bin_path):
        if not bin_path and eplus_directory:
            return Path(eplus_directory) / 'EnergyPlus'
        if not bin_path:
            return 'EnergyPlus'
        return bin_path

    command = ([get_bin_path(EPLUS_DIRECTORY, bin_path),
                "-w", tmp / weather_file.basename(),
                "-p", prefix,
                "-d", tmp.abspath(),
                "-i", (tmp / idd_file.basename())] +
               ["-s", "d",
                "-r",
                tmp / idf_file.basename()])
    logger.debug('command line : %s' % ' '.join(command))

    logger.info('starting energy plus simulation...')
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    with process.stdout:
        _log_subprocess_output(process.stdout)
    if process.wait() != 0:
        if keep_data_err:
            failed_dir = out_dir / "failed"
            failed_dir.mkdir_p()
            tmp.copytree(failed_dir / tmp.basename())
        tmp.rmtree_p()
        raise RuntimeError("System call failure")
    logger.info('energy plus simulation ended')


def run(idf_file, weather_file,
        working_dir=".",
        idd_file=None,
        prefix="eplus",
        out_dir='/tmp/',
        keep_data=False,
        keep_data_err=True,
        bin_path=None):
    """
    energyplus runner using docker image (by default) or local installation.

    Run an energy-plus simulation with the model file (a .idf file),
    a weather file (should be a .epw) as required arguments. The output will be
    a pandas dataframe or a list of dataframe or None, depending of how many
    csv has been generated during the simulation, and requested in the model
    file.
    The simulation can be containerized inside a docker image (by default) or
    with local energy-plus binary. The later is not thread-safe yet and less
    stable (due to the difficulty to ensure same behaviour across platforms.)

    Parameters
    ----------
    idf_file : str
        the file describing the model (.idf)
    weather_file : str
        the file describing the weather data (.epw)
    working_dir : str, optional
        working directory (default: ".")
    idd_file : None, optional
        base energy-plus file (default: None, find Energy+.idd in the
        e+ install directory if EPLUS_DIRECTORY set, else find it on current
        folder.)
    prefix : str, optional
        prefix of output files (default: "eplus")
    out_dir : str, optional
        Output directory (default: "/tmp")
    keep_data : bool, optional
        if True, do not remove the temporary folder after the simulation
        (default: False)
    keep_data_err : bool, optional
        if True, copy the temporary folder on out_dir / "failed" if the
        simulation fail. (default: True)
    bin_path : None, optional
        if provided, path to the EnergyPlus binary. If not provided (default),
        find it on EPLUS_DIRECTORY / EnergyPlus (if EPLUS_DIRECTORY set), or
        consider that EnergyPlus is on the path

    Output
    ------
    result_dataframes! ()


    Returns
    -------
    pandas.DataFrame or list of pandas.DataFrame or None
        Only the csv outputs are handled : the output of the
        function will be None if any csv are generated, a pandas DataFrame
        if only one csv is generated (which seems to be the usual user
        case) or a list of DataFrames if many csv are generated.
    """

    logger.info('check consistency of input files')
    idf_file, weather_file, working_dir, idd_file, out_dir = \
        _assert_files(idf_file, weather_file, working_dir, idd_file, out_dir)
    with tempdir(prefix='eplus_run_', dir=out_dir) as tmp:
        logger.debug('tempory dir (%s) created' % tmp)

        idd_file.copy(tmp)
        weather_file.copy(tmp)
        idf_file.copy(tmp)

        _exec_command_line(tmp, idd_file, idf_file,
                           weather_file, prefix, bin_path,
                           keep_data_err, out_dir)

        logger.debug(
            'files generated at the end of the simulation: %s' %
            ' '.join(
                tmp.files()))

        result_dataframes = []
        logger.debug(
            'looking for csv output, return the csv files '
            'in dataframes if any')
        for file in tmp.files('*.csv'):
            logger.debug('try to store file %s in dataframe' % (file))
            result_dataframes.append(
                pd.read_csv(
                    file,
                    sep=',',
                    encoding='us-ascii'))
            logger.debug('file %s stored' % (file))
        if len(result_dataframes) == 0:
            return
        if len(result_dataframes) == 1:
            return result_dataframes.pop()
        if keep_data:
            tmp.copytree(working_dir / tmp.basename())
        return result_dataframes
