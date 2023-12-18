#!/usr/bin/python

import argparse
from importlib.metadata import version

def create_parser():
	parser = argparse.ArgumentParser(
		prog = 'asemd',
		formatter_class=argparse.RawTextHelpFormatter,
		description = f'''

To run this script, call e.g.,

$ asemd NVE input.in 

which will run an NVE ensemble simulation using the parameters in the input 
file. The input must be written in YAML format. See example below.''',
	epilog = '''
This script is used to run MD simulations using the ASE suite. The purpose 
of this program is to provide a means for running different types of 
modes using only one script and using only one input file for all modes 
of simulation. The program is run from the terminal similar to GROMACS.

The input file should include titles for each set of variables, global- and at 
least one more mode/ensemble. Under each category, a set of input parameters
should be indented by 2 or 4 spaces. Setting and parameter should be separated 
by ':'.

----------Example------------
Global:
  input structure: input.pdb
  box size: 10 10 10

NVT:
  temperature: 300
  friction: 0.01
  time step: 2
  calculator: EMT
  steps: 10
-----------------------------

GLOBAL INPUT:
input structure:\tSpecifies the starting structure.
calculator:\t\tSpecifies the ASE calculator to be used. If using a custom 
			calculator, this should be the name of a python script that contain
			the proper calculator definition.
#starting index:\tSpecifies the index used in reading .traj-input structures. 
#			Defaults to -1
box size:\t\tWidth of the simulation box for x, y and z.
periodic:\t\tBoolean for periodic boundary conditions.
log path:\t\tPath to log file.

MODE INPUT:
optimiser:\t\tMinimisation optimiser. Choose between BFGS, GPMin or MDMin.
output:\t\t\tName of output file with extention.
temperature:\t\tSpecifies the temperature in Kelvin used in simulations.
time step:\t\tWidth of the time step in fs.
steps:\t\t\tNumber of simulation steps.
dump interval:\t\tCoordinate dump interval for output.
name:\t\t\tSpecifies the name of a particular run in the log file.
friction:\t\tSets the friction constant for the Langevin thermostat (NVT).
pfactor:\t\tThe pressure factor used for the parrinello-Rahman barostat (NPT).
external stress:\tExternal stress tensor used in NPT ensembles.
thermostat timescale:\tCharacteristic timescale of Nosé-Hoover thermostat (NPT).
range:\t\t\tThe range used when fitting an eauation of state. Set start stop and
\t\t\tnum-points.
method\t\t\tThe equation of state method. Default is Birch-Murnaghan.
'''
	)
	parser.add_argument(
		'--version',
		action='version',
		version=f'asemd ver. {version("asemd")}'
	)
	
	# Define arguments/flags for running program
	parser.add_argument(
		'--test',
		action='store_true',
		help='This flag hinders all output files and is only used for testing.'
	)
	parser.add_argument(
		'mode',
		metavar='mode',
		choices=['EMIN', 'SP', 'EOS', 'NVE', 'NVT', 'NPT'],
		help='Sets the run-mode to EMIN, SP, EOS, NVE, NVT or NPT.'
	)
	parser.add_argument(
		'input',
		metavar='input.in',
		help='Assigns a file with input paramters written in YAML format.'
	)
	parser.add_argument(
		'-s',
		'--structure',
		dest='input_structure',
		metavar='file.xyz',
		help='Overrides global structure assigned in the input file with a custom\nfile. Possible to use .pdb and .traj in addition to .xyz-files.'
	)
	parser.add_argument(
		'-o',
		'--output',
		metavar='file.xyz',
		help='Overrides output name. Possible to use .pdb and .traj in addition to\n.xyz-files.'
	)

	parser.add_argument(
		'-opt',
		'--optimiser',
		metavar='optimiser',
		help='Overrides the optimiser specified in the input file. Only for EMIN.'
	)
	parser.add_argument(
		'-n',
		'--name',
		metavar='name',
		help='Overrides the name in the output file (if any). Not for EMIN.'
	)
	parser.add_argument(
		'--dump',
		dest='DUMP_INTERVAL',
		help='Overrides the dump interval in the input file.'
	)
	parser.add_argument(
		'--start',
		dest='STARTING_INDEX',
		help='Overrides the starting index of trajectory inputs. If starting from\nlast dump, set -1.'
	)

	parser.add_argument(
		'--steps',
		dest='STEPS',
		help='Overrides the number of steps in the input.'
	)
	parser.add_argument(
		'--fmax',
		dest='FMAX',
		help='Overrides the force criteria used during energy minimisation.'
	)
	parser.add_argument(
		'--temp',
		dest='TEMPERATURE',
		help='Override input temperature (K).'
	)
	parser.add_argument(
		'--time-step',
		dest='TIME_STEP',
		help='Overrides the time step of the input file (fs).'
	)
	parser.add_argument(
		'--friction',
		dest='FRICTION',
		help='Overrides the friction constant used in the NVT ensemble (fs).'
	)
	parser.add_argument(
		'--pfactor',
		dest='PFACTOR',
		help='Overrides the pfactor used in the NPT ensemble (bar).'
	)
	parser.add_argument(
		'--timescale',
		dest='CHARACTERSISTIC_TIMESCALE',
		help='Overrides the characteristic timescale used in the NPT ensemble (fs).'
	)
	parser.add_argument(
		'--stress',
		dest='external_stress',
		metavar='external_stress',
		help='Overrides the external stress tensor used in the NPT ensemble.'
	)
	#parser.add_argument(
	#	'--range',
	#	dest='eos_range',
	#	metavar='start stop num-points',
	#	help='Overrides the scaling range used in equation of state determination,\ne.g. 0.95 1.05 5.'
	#)

	return parser
