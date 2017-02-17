# EnergyPlus Docker Container

This project has multiple versions of EnergyPlus ready for use in a single container.

## Example

To run EnergyPlus you should either mount your directory into the container or create a dependent container where you call `ADD . /var/simdata/energyplus`.

To mount the local folder and run EnergyPlus (on Linux only) make sure that your simulation directory is the current directory and run:

```
docker run -it --rm -v $(pwd):/var/simdata/energyplus nrel/energyplus EnergyPlus
```
