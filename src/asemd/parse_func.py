#!/usr/bin/python

import argparse
from importlib.metadata import version

# Indentation with two spaces will result in a match with argparse in general
desc = f'''To run this script, call e.g.,

$ asemd NVE config.in 

which will run an NVE ensemble simulation using the parameters in the config 
file, which must be written in YAML format. See example below.'''

epi = '''
This script is used to run MD simulations, single point calcualtions, equation
of state and energy minimisations using the atomic simulation environment (ASE).
The purpose of this program is to provide a means for running different types 
of evaluation modes using only one script and using a single configuration file,
regardless of simulation mode. The program is run from a terminal similar to 
GROMACS.

The config file should include titles for each set of variables, global- and at 
least one more mode/ensemble. Under each category, a set of input parameters
should be indented by 2 or 4 spaces (consitency is important). The setting- and 
parameter should be separated by ':'.

----------Example------------
Global:
  input file: input.xyz
  calculator: some_definition_script
  box size: 10 10 10
  periodic: True
  overwrite: False
  log path: logs/

EMIN:
  name: test_name
  optimiser: BFGS
  fmax: 0.05
  steps: 100
  output: relaxed.xyz

NVT:
  name: test_name
  temperature: 300
  friction: 0.01
  time step: 2
  steps: 100
  dump interval: 2
  output: nvt_300K.traj

EOS:
  name: test
  range: 0.95 1.05 10
  method: Birch-Murnaghan
  output: eos.traj
-----------------------------

GLOBAL INPUT:
  input structure:      Specifies the starting structure.
  calculator:           Specifies the ASE calculator to be used. If using a 
                        custom calculator, this should be the name of a python 
                        script that contain the proper calculator definition.
  box size:             Width of the simulation box for x, y and z.
  periodic:             Boolean for periodic boundary conditions.
  overwrite:            Boolean for wheter or not outputs should overwrite 
                        previous files with the same name.
  log path:             Path to log file.

MODE INPUT:
  optimiser:            Minimisation optimiser. Choose between BFGS, GPMin or 
                        MDMin.
  output:               Name of output file with extention.
  temperature:          Specifies the temperature in Kelvin used in simulations.
  time step:            Width of the time step in fs.
  steps:                Number of simulation steps.
  dump interval:        Coordinate dump interval for output.
  structures:           Set structure indices (not zero indexed) that will be 
                        evaluated, e.g. 1 5 8-10.
  name:                 Specifies the name of a particular run in the log file.
  friction:             Sets the friction constant for the Langevin thermostat 
                        (NVT).
  pfactor:              The pressure factor used for a parrinello-Rahman 
                        barostat (NPT).
  external stress:      External stress tensor used in NPT ensembles.
  thermostat timescale: Characteristic timescale of a Nosé-Hoover thermostat 
                        (NPT).
  range:                The range used when fitting an eauation of state. Set 
                        start stop and num-points.
  method:               The equation of state method. Default is Birch-Murnaghan.
'''

# These statements are indented in the console and should break lines after
# only 56 characters.
#-------------------------------------------------------
version_help = f'\
asemd ver. {version("asemd")}'
#-------------------------------------------------------
test_help = '''\
This flag hinders all output files and is only used for
testing.'''
#-------------------------------------------------------
mode_help = '''\
Sets the run-mode to EMIN, SP, EOS, NVE, NVT or NPT.'''
#-------------------------------------------------------
config_help = '''\
Assigns a file with input paramters written in YAML
format.'''
#-------------------------------------------------------
input_help = '''\
Overrides global structure assigned in the input file 
with a custom file. Possible to use .pdb and .traj in 
addition to .xyz-files.'''
#-------------------------------------------------------
structures_help = '''\
Specify the position/index of the structure(s) in an 
input file. Not zero-indexed and possible to select 
ranges using x-y.'''
#-------------------------------------------------------
output_help = '''\
Overrides output name. Possible to use .pdb and .traj
in addition to .xyz-files.'''
#-------------------------------------------------------
optimiser_help = '''\
Overrides the optimiser specified in the input file. 
Only for EMIN.'''
#-------------------------------------------------------
name_help = '''\
Overrides the name in the output file (if any). Not for 
EMIN.'''
#-------------------------------------------------------
dump_interval_help = '''
Overrides the dump interval in the input file.'''
#-------------------------------------------------------
start_index_help = '''\
Overrides the starting index of trajectory inputs. If
starting from last dump, set -1.'''
#-------------------------------------------------------
steps_help = '''\
Overrides the number of steps in the input.'''
#-------------------------------------------------------
fmax_help = '''\
Overrides the force criteria used during energy mini-
misation.'''
#-------------------------------------------------------
temperature_help = '''\
Override input temperature (K).'''
#-------------------------------------------------------
time_step_help = '''\
Overrides the time step of the input file (fs).'''
#-------------------------------------------------------
friction_help = '''\
Overrides the friction constant used in the NVT ensemble
(fs).'''
#-------------------------------------------------------
pfactor_help = '''\
Overrides the pfactor used in the NPT ensemble (bar).'''
#-------------------------------------------------------
timescale_help = '''\
Overrides the characteristic timescale used in the NPT
ensemble (fs).'''
#-------------------------------------------------------
stress_help = '''\
Overrides the external stress tensor used in the NPT
ensemble.'''
#-------------------------------------------------------


def create_parser():
	parser = argparse.ArgumentParser(
		prog = 'asemd',
		formatter_class=argparse.RawTextHelpFormatter,
		description = desc,
		epilog = epi
	)
	parser.add_argument(
		'--version',
		action='version',
		version=version_help
	)
	
	# Define arguments/flags for running program
	parser.add_argument(
		'--test',
		action='store_true',
		help=test_help
	)
	parser.add_argument(
		'mode',
		metavar='mode',
		choices=['EMIN', 'SP', 'EOS', 'NVE', 'NVT', 'NPT'],
		help=mode_help
	)
	parser.add_argument(
		'input',
		metavar='input.in',
		help=config_help
	)
	parser.add_argument(
		'-i',
		'--input',
		dest='input_structure',
		metavar='file.xyz',
		help=input_help
	)
	parser.add_argument(
		'-s',
		'--structures',
		nargs='+',
		dest='structures',
		metavar='i1 i2 ...',
		help=structures_help
	)
	parser.add_argument(
		'-o',
		'--output',
		metavar='file.xyz',
		help=output_help
	)

	parser.add_argument(
		'-opt',
		'--optimiser',
		metavar='optimiser',
		help=optimiser_help
	)
	parser.add_argument(
		'-n',
		'--name',
		metavar='name',
		help=name_help
	)
	parser.add_argument(
		'--dump',
		dest='DUMP_INTERVAL',
		help=dump_interval_help
	)
	parser.add_argument(
		'--start',
		dest='STARTING_INDEX',
		help=start_index_help
	)

	parser.add_argument(
		'--steps',
		dest='STEPS',
		help=steps_help
	)
	parser.add_argument(
		'--fmax',
		dest='FMAX',
		help=fmax_help
	)
	parser.add_argument(
		'--temp',
		dest='TEMPERATURE',
		help=temperature_help
	)
	parser.add_argument(
		'--time-step',
		dest='TIME_STEP',
		help=time_step_help
	)
	parser.add_argument(
		'--friction',
		dest='FRICTION',
		help=friction_help
	)
	parser.add_argument(
		'--pfactor',
		dest='PFACTOR',
		help=pfactor_help
	)
	parser.add_argument(
		'--timescale',
		dest='CHARACTERSISTIC_TIMESCALE',
		help=timescale_help
	)
	parser.add_argument(
		'--stress',
		dest='external_stress',
		metavar='external_stress',
		help=stress_help
	)
	#parser.add_argument(
	#	'--range',
	#	dest='eos_range',
	#	metavar='start stop num-points',
	#	help='Overrides the scaling range used in equation of state determination,\ne.g. 0.95 1.05 5.'
	#)

	return parser
