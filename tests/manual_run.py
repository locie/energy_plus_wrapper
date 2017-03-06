#!/usr/bin/env python
# coding=utf8

import multiprocessing as mp
from functools import partial

from energyplus_wrapper import run
import logging


log = logging.getLogger()
log.addHandler(logging.StreamHandler())
log.setLevel('DEBUG')


def test_docker_run(tag, n):
    parfunc = partial(run, 'in.idf', docker_tag='8.4.0')
    with mp.Pool() as p:
        p.map(parfunc, ['in.epw'] * n)


if __name__ == '__main__':
    test_docker_run('', 100)
