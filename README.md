energy+ wrapper
===============

This little library has been written in order to run energy+ simulation
in linux and windows in a thread-safe way.

The main goal is to ensure a stable behaviour across platform and
version, and to make the link between the e+ building model tools
written in python and the different analysis and optimization tools.

Install
=======

For now, the package is available on PyPI, and via the github repo.

``` {.sourceCode .shell}
pip install energyplus-wrapper
pip install git+git://github.com/locie/energy_plus_wrapper.git
```

for the requirements.

Usage
=====

very simple use:

``` {.sourceCode .python}
from energyplus_wrapper import run
result = run('in.idf', 'in.epw')
```

API
===

The main function take the idf file as input. Two secondary function
provide a launch from the model content as string
[run\_from\_str]{.title-ref}, and as eppy IDF
[run\_from\_eppy]{.title-ref}. These three function share the same
signature, excepted the first one.

``` {.sourceCode .python}
def run(idf_file, weather_file,
        working_dir=".",
        idd_file=None,
        simulname=None,
        prefix="eplus",
        out_dir=tempfile.gettempdir(),
        keep_data=False,
        keep_data_err=True,
        bin_path=None,
        eplus_path=None):
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
        e+ install directory if $EPLUS_DIR set, else find it on working
        dir.)
    simulname : str or None, optional (default None)
        this name will be used for temp dir id and saved outputs.
        If not provided, uuid.uuid1() is used. Be careful to avoid naming
        collision : the run will alway be done in separated folders, but the
        output files can overwrite each other if the simulname is the same.
    prefix : str, optional
        prefix of output files (default: "eplus")
    out_dir : str, optional
        temporary output directory (default: OS default temp folder).
    keep_data : bool, optional
        if True, do not remove the temporary folder after the simulation
        (default: False)
    keep_data_err : bool, optional
        if True, copy the temporary folder on out_dir / "failed" if the
        simulation fail. (default: True)
    bin_path : None, optional
        if provided, path to the EnergyPlus binary. If not provided (default),
        find it on eplus_path / EnergyPlus (if eplus_path set), or
        use the global variable EPLUS_PATH (id set), or finally
        consider that EnergyPlus is on the path
    eplus_path : None, optional
        if provided, path to the EnergyPlus.


    Returns
    -------
    pandas.DataFrame or list of pandas.DataFrame or None
        Only the csv outputs are handled : the output of the
        function will be None if any csv are generated, a pandas DataFrame
        if only one csv is generated (which seems to be the usual user
        case) or a list of DataFrames if many csv are generated.
    """
```
