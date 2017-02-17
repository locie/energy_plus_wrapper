energy+ wrapper
==========================

This little library has been written in order to run energy+ simulation in linux and windows with or without the use of docker image in a thread-safe way.

The main goal is to ensure a stable behaviour across platform and version, and
to make the link between the e+ building model tools written in python and the different analysis and optimization tools.

A lot remains to do:

* Write proper documentation
* Write tests coverage
* Ensure stability and cross-platform compatibility
* Deal with != energy-plus version
* Write a DockerFile which can handle these != version
* Write a command-line tool (using click ?) ? Maybe not that useful..

Credits
-------

- `Distribute`_
- `Buildout`_
- `modern-package-template`_

.. _Buildout: http://www.buildout.org/
.. _Distribute: http://pypi.python.org/pypi/distribute
