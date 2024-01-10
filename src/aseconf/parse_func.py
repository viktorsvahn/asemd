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
  structures: 1-3 5 (apply on first to third, and fifth structure)
  transfer info:
    - some_info_type
  add info:
    new: info (will add new=info to header)
-----------------------------

GLOBAL INPUT:
  input structure:      Specifies the starting structure.

MODE INPUT:
  header file:          File that contains new headers to replace those in the 
                        input.xyz file.
  output:               Name of output file with extention.
  structures:           Set structure indices (not zero indexed) that will be 
                        evaluated, e.g. 1 5 8-10.
  transfer info:        List of info tags that are to be transfered from the header file
                        to the input file.
  add info:             Indented definitions that should be added as info tags
                        to the input file.
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
start_index_help = '''\
Overrides the starting index of trajectory inputs. If
starting from last dump, set -1.'''
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
		choices=['CH'],
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
		'--start',
		dest='STARTING_INDEX',
		help=start_index_help
	)

	return parser
