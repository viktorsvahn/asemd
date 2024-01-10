#!/usr/bin/python

import argparse
from importlib.metadata import version

# Indentation with two spaces will result in a match with argparse in general
desc = f'''To run this script, call e.g.,

$ aseconf CH config.in 

which will change the headers of the specified input structure file to those 
present in another file, using the parameters in the config.in file, which must 
be written in YAML format. See example below.'''

epi = '''
This script is used to configure structure files, such as changing or altering 
the headers of ase structure files. The config file should include titles for 
each set of variables, global- and at least one mode. Under each category, a 
set of input parameters should be indented by 2 or 4 spaces (consitency is 
important). The setting- and parameter should be separated by ':'.

----------Example------------
Global:
  input file: input.xyz

CH:
  header file: different_input.xyz
  output: output.xyz
-----------------------------

GLOBAL INPUT:
  input structure:      Specifies the starting structure.

MODE INPUT:
  header file:          File that contains new headers to replace those in the 
                        input.xyz file.
  output:               Name of output file with extention.
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
		choices=['EMIN', 'SP', 'EOS', 'NVE', 'NVT', 'NPT', 'CH'],
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
