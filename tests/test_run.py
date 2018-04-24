#!/usr/bin/env python
# -*- coding: utf-8 -*-

import functools as ft
import multiprocessing as mp

import pytest

from energyplus_wrapper import run


@pytest.mark.parametrize("version",
                         ["8-4-0",
                          "8-7-0"])
def test_run(version):
    run('tests/in_%s.idf' % version,
        'tests/in.epw',
        idd_file='tests/EnergyPlus-%s/Energy+.idd' % version,
        bin_path="tests/EnergyPlus-%s/energyplus" % version)


def run_mp(i, version):
    run('tests/in_%s.idf' % version,
        'tests/in.epw',
        idd_file='tests/EnergyPlus-%s/Energy+.idd' % version,
        bin_path="tests/EnergyPlus-%s/energyplus" % version)


@pytest.mark.parametrize("version",
                         ["8-4-0",
                          "8-7-0"])
def test_run_mp(version):
    with mp.Pool() as p:
        p.map(ft.partial(run_mp, version=version), range(8))


if __name__ == '__main__':
    import logging
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler())
    logger.setLevel("DEBUG")
    test_run_mp("8-7-0")
