# asemd
`asemd` is a script that allows a user to run molecular dynamics (MD) simulations, using the atomic simulation enviroment (ASE), directly from the terminal. This offers more flexibility when itcomes to running MD simulations using bash scripts without requiring the user to edit the MD scripts. Using this script, it is possible to run an energy minimisation, single-point calculations, NVE, NVT and an NPT ensemble using a single terminal command and an input file.

## Installation
To install the program, place all files in a folder, run
```
cd /local/install/path
git clone https://github.com/viktorsvahn/asemd.git
python3 -m pip install .
```

## Running
Once installed and having generated a config file in some direcotry that also contain starting structures, the user may run, e.g.,
```
asemd NVE config.in (--test)
```
to run an NVE simulation using the settings from the file `config.in`. The test-flag ensures that neither logs nor structure files are saved and is used for testing purposes.

For additional information surrounding this package, please use
```
asemd --help
```
which includes a more in-depth user guide.

## Input file
THe input file is written in the YAML format which is human readable and intuitive. Each input file consist of at least two sections---Global and EMIN/SP/NVE/NVT/NPT. The global section contains global variables such as an input structure, geometry of the simulation enviroment and whether or not periodic boundary conditions are to be used (bool). The next section has information regarding the simulation mode (EMIN or ensemble), written in capital letters. This section includes temperature, time steps, what calculator is going to be used etc. Each section ends with a ':' and all variables underneath it must be indented by 2 or 4 spaces. Variables and values should also be separated by a ':'.

An example of a basic config is:
```
Global:
  input structure: input.pdb
  box size: 10 10 10
  periodic: True

EMIN:
  optimiser: MDMin
  calculator: EMT
  steps: 10
  output: emin.pdb

SP:
  calculator: some_calc_script
  evaluate:
    - forces
  output: forces.xyz

NVE:
  calculator: some_calc_script
  steps: 10
  temperature: 300
  time step: 2
  output: nve.traj
```
The different extensions used in this example shows what possibilitites there are and do not imply any restrictions related to the different modes. The order in which parameters appear is arbitrary. Further, **please note** that the EMT calculator is just used as an example and should not really be used for anything other than making sure that the system runs.

Calculator scripts must include a `calculator` variable that defines a calculator object of choice, just
like one would define an EMT calculator.

For more info on how the package is built, please refer to the wiki page.