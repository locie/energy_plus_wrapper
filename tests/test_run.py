#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
The test will only run under linux, as it rely on `ensure_eplus_root`

A cross-platform version of this function will be welcome (and is planned).

tests
├── Energy+.idd
├── in_8-4-0.idf
├── in_8-5-0.idf
├── in_8-7-0.idf
├── in.epw
└── test_run.py
"""

import functools as ft
import multiprocessing as mp
import pickle

import pytest

from energyplus_wrapper import EPlusRunner, ensure_eplus_root
import joblib

base_download = "https://github.com/NREL/EnergyPlus/releases/download"

eplus_url = {
    "8-4-0": (
        f"{base_download}/v8.4.0-Update1/" "EnergyPlus-8.4.0-09f5359d8a-Linux-x86_64.sh"
    ),
    "8-5-0": f"{base_download}/v8.5.0/EnergyPlus-8.5.0-c87e61b44b-Linux-x86_64.sh",
    "8-7-0": f"{base_download}/v8.7.0/EnergyPlus-8.7.0-78a111df4a-Linux-x86_64.sh",
}


@pytest.mark.parametrize("version", ["8-4-0", "8-7-0"])
def test_run(version):
    root = ensure_eplus_root(eplus_url[version])
    runner = EPlusRunner(root)
    return runner.run_one(
        "tests/in_%s.idf" % version, "tests/in.epw", backup_strategy=None
    )


@pytest.mark.parametrize("version", ["8-4-0", "8-7-0"])
def test_run_many_serial(version):
    root = ensure_eplus_root(eplus_url[version])
    runner = EPlusRunner(root)
    samples = {key: ("tests/in_%s.idf" % version, "tests/in.epw") for key in range(8)}
    with joblib.parallel_backend("loky", n_jobs=1):
        runner.run_many(samples, backup_strategy=None)


@pytest.mark.parametrize("version", ["8-4-0", "8-7-0"])
def test_serialize(version):
    root = ensure_eplus_root(eplus_url[version])
    runner = EPlusRunner(root)
    pickle.loads(pickle.dumps(runner))


@pytest.mark.parametrize("version", ["8-4-0", "8-7-0"])
def test_run_many_mp(version):
    root = ensure_eplus_root(eplus_url[version])
    runner = EPlusRunner(root)
    samples = {key: ("tests/in_%s.idf" % version, "tests/in.epw") for key in range(8)}
    with joblib.parallel_backend("multiprocessing", n_jobs=-1):
        runner.run_many(samples, backup_strategy=None)