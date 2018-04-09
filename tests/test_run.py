#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from energyplus_wrapper import run


@pytest.mark.parametrize("bin_path",
                         [None,
                          "tests/EnergyPlus-8-4-0"])
def test_run(bin_path):
    run('tests/in.idf',
        'tests/in.epw',
        idd_file='tests/Energy+.idd',
        bin_path=bin_path)


if __name__ == '__main__':
    import logging
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler())
    logger.setLevel("DEBUG")
    test_run(None)
