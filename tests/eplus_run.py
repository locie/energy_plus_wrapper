#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from energyplus_wrapper import run
import multiprocessing as mp


def test_docker_run(i):
    run('in.idf', 'in.epw')


if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel('DEBUG')
    logger.addHandler(logging.StreamHandler())
    result_singleprocess = test_docker_run(0)
    p = mp.Pool()
    results_multiprocess = p.map(test_docker_run, range(4))
    assert all([result_singleprocess == result_multiprocess
                for result_multiprocess in results_multiprocess])
