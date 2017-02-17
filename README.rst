energy+ wrapper
==========================

This little library has been written in order to run energy+ simulation in linux and windows with or without the use of docker image in a thread-safe way.

The main goal is to ensure a stable behaviour across platform and version, and
to make the link between the e+ building model tools written in python and the different analysis and optimization tools.

Install
=======

For now, te package isn't available on PyPI, only on the github repo.

.. code:: shell
    pip install git+git://github.com/celliern/energy_plus_wrapper.git

and

.. code:: shell
    pip install -r https://raw.githubusercontent.com/celliern/energy_plus_wrapper/master/requirements.txt

for the requirements.

Usage
=====

very simple use:

.. code:: python
    from energyplus_wrapper import run
    result = run('in.idf', 'in.epw')

TODO
====

* Write proper documentation
* Write tests coverage (fies in.idf and in.epw are here for that).
* Ensure stability and cross-platform compatibility
* Deal with != energy-plus version
* Write a DockerFile which can handle these != version (one adaptative or one per version?)
* Write a command-line tool (using click ?) ? Maybe not that useful..

Credits
-------

- `Distribute`_
- `Buildout`_
- `modern-package-template`_

.. _Buildout: http://www.buildout.org/
.. _Distribute: http://pypi.python.org/pypi/distribute
