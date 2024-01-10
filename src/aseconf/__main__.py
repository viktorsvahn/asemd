#!/usr/bin/python


import argparse
import yaml
import time
import datetime
import os
import sys
import copy
import pandas as pd
import numpy as np

import aseconf.parse_func as pf
import aseconf.change as ch


# Initiate parser using function defined in parse_func.py
parser = pf.create_parser()

# Collect args using parser
args = parser.parse_args()
mode = args.mode
input_file = args.input

# Paths
path = os.getcwd()+'/'
sys.path.append(path) # Cannot load external calculator module without this!

# Read input file
with open(path+input_file, 'r') as f:
	inp = yaml.safe_load(f)

mode_input = inp[mode]
global_input = inp['Global']

# Collects- and appends all local variables to the global variables
# This is used to select arbitrary methods from strings using get(attr)
# For example, global_vars is a dictionary where all modules imported as
# 'from x import y' are found as {y:x}. Using global_vars.get(y)() is equivalent
# to calling 'x.y()'.
global_vars = globals().copy()
global_vars.update(locals())

# Mapping between input mode and class name for each relevant ASE-object

modes = {
	'CH':'Change headers in a structure file',
}

# Removes case-sensitivity from mode-input parameters
mode_input = {key.lower():val for key, val in mode_input.items()}


def main():
	# INITIALISE SHARED VARIABLES #############################################
	# CLI arguments have priority over the input file as a rule
	if args.input_structure:
		input_structure = args.input_structure
		global_input['input file'] = input_structure
	else:
		input_structure = global_input['input file']

	if args.structures:
		structures = ''.join(args.structures)
		print(type(structures))
		mode_input['structures'] = structures


	if args.test == False:
		if args.output:
			output_structure = args.output
			mode_input['output'] = output_structure
		else:
			output_structure = mode_input['output']
	else:
		output_structure = False


	# SETUP ###################################################################
	# ENERGY MINIMISATION
	if mode == 'CH':

		# Initialise an energy minimisation object
		setup = ch.ChangeHeader(
			mode_input,
			global_input,
			path+input_structure,
			output_structure
		)




	# RUN SETUP ###############################################################	
	print(f'Running from: {path}')
	
	# Remove certain params from dataframe printout
	df_hide_mode = [
		'name'
	]
	df_hide_global = [
		'log path',
		'calculator',
		'box size',
		'periodic',
		'overwrite',
	]

	for param in df_hide_mode:
		try:
			mode_input.pop(param)
		except:
			pass
	
	for param in df_hide_global:
		try:
			global_input.pop(param)
		except:
			pass		

	#print(mode_input)
	#print(global_input)
	# Merge input dictionaries into a single one and generate a dataframe
	inputs = {**global_input, **mode_input}
	param_df = pd.DataFrame.from_dict(inputs, orient='index', columns=[''])


	if (mode == 'NPT') and (PFACTOR == None):
		print(f'Mode: NVT (Canonical ensemble using a Nosé-Hoover thermostat.)')
	else:
		print(f'Mode: {mode} ({modes[mode]})')
	if args.test:
		print('Running in test mode. No logs or outputs will be saved.')
	print('\nInput:')
	print(param_df, '\n')

	start = datetime.datetime.now()
	print(f'\nStarted: {start}\n')


	setup.run()


	print('\nFinished!')
	end = datetime.datetime.now()
	print(f'Completed: {end} (elapsed time: {end-start})')



if __name__ == '__main__':
	main()