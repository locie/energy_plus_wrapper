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

this package works well when docker is properly install and configured (https://www.docker.com/products/docker).

as fallback, a proper install of energy-plus v 8.4.0 on linux system should do the trick, with docker=False on the running function.

Usage
=====

very simple use:

.. code:: python

    from energyplus_wrapper import run
    result = run('in.idf', 'in.epw')


API
===

.. code:: python

    run()
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
            docker {bool} -- if True, the simulation will run containerized
                on docker image (cellier/eplus). (default: {True})
                Thanks to Nicholas Long nicholas.long@nrel.gov for the base image.
            ep_ver {str} -- the energy-plus version used (default: {"8-4-0"})
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
