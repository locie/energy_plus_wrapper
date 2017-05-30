energy+ wrapper
==========================

This little library has been written in order to run energy+ simulation in linux and windows in a thread-safe way.

The main goal is to ensure a stable behaviour across platform and version, and
to make the link between the e+ building model tools written in python and the different analysis and optimization tools.

Install
=======

For now, the package is available on PyPI, and via the github repo.

.. code:: shell

    pip install energyplus-wrapper
    pip install git+git://github.com/locie/energy_plus_wrapper.git

for the requirements.

Usage
=====

very simple use:

.. code:: python

    from energyplus_wrapper import run
    result = run('in.idf', 'in.epw')


API
===

.. code:: python

    def run(idf_file, weather_file,
        working_dir=".",
        idd_file=None,
        prefix="eplus",
        out_dir='/tmp/',
        keep_data=False,
        keep_data_err=True,
        bin_path=None):
        """
        energyplus runner using local installation.

        Run an energy-plus simulation with the model file (a .idf file),
        a weather file (should be a .epw) as required arguments. The output will be
        a pandas dataframe or a list of dataframe or None, depending of how many
        csv has been generated during the simulation, and requested in the model
        file. The run is multiprocessing_safe

        Parameters
        ----------
        idf_file : str
            the file describing the model (.idf)
        weather_file : str
            the file describing the weather data (.epw)
        working_dir : str, optional
            working directory (default: ".")
        idd_file : None, optional
            base energy-plus file (default: None, find Energy+.idd in the
            e+ install directory if EPLUS_DIRECTORY set, else find it on current
            folder.)
        prefix : str, optional
            prefix of output files (default: "eplus")
        out_dir : str, optional
            Output directory (default: "/tmp")
        keep_data : bool, optional
            if True, do not remove the temporary folder after the simulation
            (default: False)
        keep_data_err : bool, optional
            if True, copy the temporary folder on out_dir / "failed" if the
            simulation fail. (default: True)
        bin_path : None, optional
            if provided, path to the EnergyPlus binary. If not provided (default),
            find it on EPLUS_DIRECTORY / EnergyPlus (if EPLUS_DIRECTORY set), or
            consider that EnergyPlus is on the path


        Returns
        -------
        pandas.DataFrame or list of pandas.DataFrame or None
            Only the csv outputs are handled : the output of the
            function will be None if any csv are generated, a pandas DataFrame
            if only one csv is generated (which seems to be the usual user
            case) or a list of DataFrames if many csv are generated.
        """

.. Credits
.. -------
