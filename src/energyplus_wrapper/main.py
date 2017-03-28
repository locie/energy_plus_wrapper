#!/usr/bin/env python
# coding=utf8

import os
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


def log_subprocess_output(pipe):
    for line in iter(pipe.readline, b''):  # b'\n'-separated lines
        eplus_logger.info(line.decode().strip('\n'))


def _assert_files(idf_file, weather_file, working_dir,
                  idd_file, out_dir):
    """Ensure the files and directory are here and convert them as path.Path

    This function will coerce the string as a path.py Path and assert if
    mandatory files or directory are missing.
    """

    if idd_file is not None:
        idd_file = Path(idd_file)
        logger.debug('looking for idd file (%s)' % idd_file.abspath())
        if not idd_file.isfile():
            raise IOError("IDD file not found")

    working_dir = Path(working_dir)
    logger.debug(
        'checking if working directory (%s) exist' %
        working_dir.abspath())
    if not working_dir.isdir():
        raise IOError("Working directory does not exist")

    if out_dir is not None:
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


def exec_command_line(tmp, idd_file, idf_file, weather_file,
                      prefix, docker_tag, keep_data_err, out_dir):
    """Build the command line used in subprocess.Popen

    Construct the command line passed as argument to subprocess.Popen depending
    docker or local e+ installation is used.
    """
    if (docker_tag != '') and (docker_tag is not None):
        control_name = "docker_%i" % os.getpid()
        command = (['docker', 'run', '--rm', '--name', control_name,
                    '-v', '%s:/var/simdata/' % tmp,
                    'celliern/energy_plus:%s' % docker_tag,
                    'EnergyPlus',
                    "-w", "/var/simdata/%s" % weather_file.basename(),
                    "-p", prefix,
                    "-d", "/var/simdata/"] +
                   (["-i", "/var/simdata/%s" % idd_file.basename()]
                    if idd_file is not None else []) +
                   ["-s", "d",
                    "-r",
                    "/var/simdata/%s" % idf_file.basename()])
        logger.debug('command line : %s' % ' '.join(command))

        logger.info('starting energy plus simulation...')
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        with process.stdout:
            log_subprocess_output(process.stdout)
        if process.wait() != 0:
            if keep_data_err:
                failed_dir = out_dir / "failed"
                failed_dir.mkdir_p()
                tmp.copytree(failed_dir / tmp.basename())
            for action in ('kill', 'rm'):
                kill_process = subprocess.Popen(['docker', action, 'ctr_name'],
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.PIPE)
                if kill_process.wait() != 0:
                    raise RuntimeError(kill_process.stderr.read())
            tmp.rmtree_p()
            raise RuntimeError("System call failure")

    else:
        command = (['EnergyPlus',
                    "-w", tmp / weather_file.basename(),
                    "-p", prefix,
                    "-d", tmp.abspath()] +
                   (["-i", tmp / idd_file.basename()]
                    if idd_file is not None else []) +
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
            log_subprocess_output(process.stdout)
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
        docker_tag='latest'):
    """
    energyplus runner using docker image (by default) or local installation.

    Run an energy-plus simulation with the model file (a .idf file),
    a weather file (should be a .epw) as required arguments. The output will be
    a pandas dataframe or a list of dataframe or None, depending of how many
    csv has been generated during the simulation, and requested in the model
    file.
    The simulation can be containerized inside a docker image (by default) or
    with local energy-plus binary. The later is not thread-safe yet and less
    stable (due to the difficulty to ensure same behaviour accross platforms.)
    # TODO: ensure same behaviour across != platform
    # TODO: ensure same behaviour with != versions

    Arguments:
        idf_file {str} -- the file describing the model (.idf)
        weather_file {str} -- the file describing the weather data (.epw)

    Keyword Arguments:
        working_dir {str} -- working directory (default: {"."})
        prefix {str} -- prefix of output file (default: {"eplus"})
        idd_file {str} -- base energy-plus file (default: {None},
            using the one provided by energy-plus)
        out_dir {str} -- output_directory (default: {"/tmp"})
        keep_data {bool} -- the data are put on temporary directory
            if False (the default), this directory is deleted after the run.
            Otherwise, the data will remain in place (default: {False})
        docker_tag {str} -- if not empty, the simulation will run containerized
            on docker image (cellier/energy_plus:{docker_tag}).
            Thanks to Nicholas Long nicholas.long@nrel.gov for the base image.
            If empty string or None, fallback to local installed e+.
            (default: {"latest"}, the 8.6.0 version.)
        # TODO : write a nice tool to detect installed version of eplus
        # for the != platforms (versioning in e+ seem strange..)

    Output:
        result_dataframes {pandas.DataFrame or
                           list of pandas.DataFrame or
                           None} --
            for now, only the csv outputs are handled : the output of the
            fonction will be None if any csv are generated, a pandas DataFrame
            if only one csv is generated (which seems to be the usual user
            case) or a list of DataFrames if many csv are generated.
    """

    logger.info('check consistency of input files')
    idf_file, weather_file, working_dir, idd_file, out_dir = \
        _assert_files(idf_file, weather_file, working_dir, idd_file, out_dir)
    with tempdir(prefix='eplus_run_', dir=out_dir) as tmp:
        logger.debug('tempory dir (%s) created' % tmp)

        if idd_file is not None:
            idd_file.copy(tmp)
        weather_file.copy(tmp)
        idf_file.copy(tmp)

        exec_command_line(tmp, idd_file, idf_file,
                          weather_file, prefix, docker_tag,
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
        tmp.rmtree_p()
        return result_dataframes
