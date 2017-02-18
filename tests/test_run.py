#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from energyplus_wrapper import run


@pytest.mark.parametrize("tag", ["8.2.0", "8.3.0",
                                 "8.4.0", "8.5.0",
                                 "8.6.0", "latest"])
def test_docker_run(tag):
    run('tests/in.idf',
        'tests/in.epw', docker_tag=tag)
