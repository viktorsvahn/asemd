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

import asemd.energy_min as emin
import asemd.single_point as sp
import asemd.equation_of_state as eos
import asemd.md as md
import asemd.parse_func as pf


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
ensemble_methods = {
	'NVE': 'VelocityVerlet',
	'NVT': 'Langevin',
	'NPT': 'NPT'
}

modes = {
	'EMIN':'Energy minimisation',
	'SP':'Single point energy calculation',
	'EOS':'Equation of state',
	'NVE':'Microcanonical ensemble',
	'NVT':'Canonical ensemble',
	'NPT':'Isobaric ensemble'
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
		structures = args.structures
		mode_input['structures'] = structures

	if args.test == False:
		if args.output:
			output_structure = args.output
			mode_input['output'] = output_structure
		else:
			output_structure = mode_input['output']
	else:
		output_structure = False

	if args.STEPS:
		STEPS = int(args.STEPS)
		mode_input['steps'] = STEPS
	elif 'steps' in mode_input:
		STEPS = int(mode_input['steps'])
	else:
		STEPS = None

	if args.DUMP_INTERVAL:
		DUMP_INTERVAL = int(args.DUMP_INTERVAL)
		mode_input['dump interval'] = DUMP_INTERVAL
	elif 'dump interval' in mode_input:
		DUMP_INTERVAL = int(mode_input['dump interval'])
	else:
		DUMP_INTERVAL = 1

	if args.test == False:
		log_path = global_input['log path']
		# Create a log dir and save logs if a dit has been specified

		if 'log path' in global_input:
			#if not os.path.exists(path+log_path): 
			if not os.path.exists(log_path): 
				#os.makedirs(log_path)
				os.makedirs(log_path)
			else:
				pass

		# Name log file after date and mode		
		if 'name' in mode_input:
			log_name = mode_input['name']
			name_test = False
		else:
			log_name = time.strftime("%Y%m%d")
			name_test = True
		# Name log file after date and mode		
		log_file = f'{log_path}{mode}_{log_name}.log'

	else:
		name_test = False
		log_file = None


	# SETUP ###################################################################
	# ENERGY MINIMISATION
	if mode == 'EMIN':

		# CLI arguments have priority over the input file as a rule
		if args.optimiser:
			optimiser = args.optimiser
			mode_input['optimiser'] = optimiser
		elif mode_input['optimiser']:
			optimiser = mode_input['optimiser']
		else:
			print('No optimiser chosen!')
			print('''Select optimiser by including:\n  optimiser: BFGS/MDMin/GPMin\nin the YAML input file.''')

		if args.FMAX:
			FMAX = float(args.FMAX)
			mode_input['fmax'] = FMAX
		elif 'fmax' in mode_input:
			FMAX = float(mode_input['fmax'])
		else:
			FMAX = None


		# Initialise an energy minimisation object
		setup = emin.EnergyMinimisation(
			optimiser,
			STEPS,
			FMAX,
			DUMP_INTERVAL,
			log_file,
			mode_input,
			global_input,
			path+input_structure,
			output_structure
		)


	# SINGLE POINT EVALUATION
	elif mode == 'SP':
		# Initiate a single point caluclation object
		setup = sp.SinglePoint(
			log_file,
			mode_input,
			global_input,
			path+input_structure,
			output_structure
		)


	# EQUATION OF STATE
	elif mode == 'EOS':

		# Initiate a equation of state object
		setup = eos.EquationState(
			log_file,
			mode_input,
			global_input,
			path+input_structure,
			output_structure
		)
	

	# INITIALISE ENSEMBLE VARIABLES ###########################################
	elif mode in ensemble_methods.keys():
		
		# CLI arguments have priority over the input file as a rule
		if args.TEMPERATURE:
			TEMPERATURE = float(args.TEMPERATURE)
			mode_input['temperature'] = TEMPERATURE
		elif 'temperature' in mode_input:
			TEMPERATURE = float(mode_input['temperature'])
		else:
			TEMPERATURE = None

		if args.TIME_STEP:
			TIME_STEP = float(args.TIME_STEP)
			mode_input['time step'] = TIME_STEP
		elif 'time step' in mode_input:
			TIME_STEP = float(mode_input['time step'])
		else:
			TIME_STEP = None

		if args.FRICTION:
			FRICTION = float(args.FRICTION)
			mode_input['friction'] = FRICTION
		elif 'friction' in mode_input:
			FRICTION = float(mode_input['friction'])
		else:
			FRICTION = None

		if args.PFACTOR:
			PFACTOR = float(args.PFACTOR)
			mode_input['pfactor'] = PFACTOR
		elif 'pfactor' in mode_input:
			PFACTOR = mode_input['pfactor']
		else:
			PFACTOR = None

		if args.external_stress is not None:
			if len(args.external_stress) > 1:
				external_stress = list(args.external_stress)
			else:
				external_stress = float(args.external_stress)
			mode_input['external stress'] = external_stress
		elif 'external stress' in mode_input:
			if len(args.external_stress) > 1:
				external_stress = list(mode_input['external stress'])
			else:
				external_stress = float(mode_input['external stress'])
		else:
			external_stress = 0

		if args.CHARACTERSISTIC_TIMESCALE:
			CHARACTERSISTIC_TIMESCALE = float(args.CHARACTERSISTIC_TIMESCALE)
			mode_input['thermostat timescale'] = CHARACTERSISTIC_TIMESCALE
		elif 'thermostat timescale' in mode_input:
			CHARACTERSISTIC_TIMESCALE = float(mode_input['thermostat timescale'])
		else:
			CHARACTERSISTIC_TIMESCALE = None


		# Initiate molecular dynamics object
		setup = md.MolecularDynamics(
			STEPS,
			TIME_STEP,
			TEMPERATURE,
			FRICTION,
			PFACTOR,
			CHARACTERSISTIC_TIMESCALE,
			DUMP_INTERVAL,
			external_stress,
			log_file,
			mode_input,
			global_input,
			path+input_structure,
			output_structure
		)

		if mode == 'NVE':
			setup.nve()

		elif mode == 'NVT':
			setup.nvt()
		
		elif mode == 'NPT':
			setup.npt()


	# RUN SETUP ###############################################################	
	print(f'Running from: {path}')
	
	# Remove certain params from dataframe printout
	df_hide_mode = [
		'name'
	]
	df_hide_global = [
		'log path'
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

	# Write input parameters to log file
	if (args.test == False) and (log_file is not None):
		with open(log_file, 'a') as f:
			print('='*80, file=f)
			print('Input:', file=f)
			print(param_df, file=f)
			print(f'\nStarted: {start}\n', file=f)


	# Runs the setup initialised for a given mode
	if name_test:
		setup.error_msg(
			'Warning:',
			'No name for this run has been specified!',
			'Log file will now be named by date.',
			'Running multiple instances of the same mode simultaneously will result in\noutputs being mixed up.',
		)
	

	setup.run()


	print('\nFinished!')
	end = datetime.datetime.now()
	print(f'Completed: {end} (elapsed time: {end-start})')

	# Additional information to log file.
	if (args.test == False) and (log_file is not None):
		with open(log_file, 'a') as f:
			print(f'\nCompleted: {end} (elapsed time: {end-start})\n', file=f)


if __name__ == '__main__':
	main()