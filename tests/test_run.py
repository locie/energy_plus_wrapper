#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
You should download EPlus version 8.4, 8.5, 8.7 and put it into the tests/ folder
in order to run these tests, so the tree looks like

tests
├── Energy+.idd
├── EnergyPlus-8-4-0
├── EnergyPlus-8-5-0
├── EnergyPlus-8-7-0
├── in_8-4-0.idf
├── in_8-5-0.idf
├── in_8-7-0.idf
├── in.epw
└── test_run.py
"""

import functools as ft
import multiprocessing as mp

import pytest

from energyplus_wrapper import run


@pytest.mark.parametrize("version", ["8-4-0", "8-7-0"])
def test_run(version):
    return run(
        "tests/in_%s.idf" % version,
        "tests/in.epw",
        idd_file="tests/EnergyPlus-%s/Energy+.idd" % version,
        bin_path="tests/EnergyPlus-%s/energyplus" % version,
    )


@pytest.mark.parametrize("version", ["8-4-0", "8-7-0"])
def test_run_eplus_path(version):
    return run(
        "tests/in_%s.idf" % version,
        "tests/in.epw",
        eplus_path="tests/EnergyPlus-%s" % version,
    )


def run_mp(i, version):
    return run(
        "tests/in_%s.idf" % version,
        "tests/in.epw",
        idd_file="tests/EnergyPlus-%s/Energy+.idd" % version,
        bin_path="tests/EnergyPlus-%s/energyplus" % version,
    )


@pytest.mark.parametrize("version", ["8-4-0", "8-7-0"])
def test_run_mp(version):
    with mp.Pool() as p:
        res = p.map(ft.partial(run_mp, version=version), range(8))
    print(res)


if __name__ == "__main__":
    import logging

    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler())
    logger.setLevel("DEBUG")
    test_run_mp("8-7-0")
