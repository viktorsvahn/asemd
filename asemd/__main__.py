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

import asemd.single_point as sp
import asemd.energy_min as emin
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


ensemble_methods = {
	'NVE': 'VelocityVerlet',
	'NVT': 'Langevin',
	'NPT': 'NPT'
}

modes = {
	'EMIN':'Energy minimisation',
	'SP':'Single point energy calculation',
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
		global_input['input structure'] = input_structure
	else:
		input_structure = global_input['input structure']

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
		STEPS = mode_input['steps']
	else:
		STEPS = None

	if args.DUMP_INTERVAL:
		DUMP_INTERVAL = int(args.DUMP_INTERVAL)
		mode_input['dump interval'] = DUMP_INTERVAL
	elif 'dump interval' in mode_input:
		DUMP_INTERVAL = mode_input['dump interval']
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
		log_file = f'{log_path}{time.strftime("%Y%m%d")}_{mode}.log'
	else:
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
			FMAX = mode_input['fmax']
		else:
			FMAX = None


		# Initialise an energy minimisation object
		setup = emin.EnergyMinimisation(
			optimiser,
			STEPS,
			FMAX,
			DUMP_INTERVAL,
			mode_input,
			global_input,
			path+input_structure,
			output_structure
		)


	# SINGLE POINT EVALUATION
	elif mode == 'SP':
		# Initiate a single point caluclation object
		setup = sp.SinglePoint(
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
			TEMPERATURE = mode_input['temperature']
		else:
			TEMPERATURE = None

		if args.TIME_STEP:
			TIME_STEP = float(args.TIME_STEP)
			mode_input['time step'] = TIME_STEP
		elif 'time step' in mode_input:
			TIME_STEP = mode_input['time step']
		else:
			TIME_STEP = None

		if args.FRICTION:
			FRICTION = float(args.FRICTION)
			mode_input['friction'] = FRICTION
		elif 'friction' in mode_input:
			FRICTION = mode_input['friction']
		else:
			FRICTION = None

		if args.PFACTOR:
			PFACTOR = float(args.PFACTOR)
			mode_input['pfactor'] = PFACTOR
		elif 'pfactor' in mode_input:
			PFACTOR = mode_input['pfactor']
		else:
			PFACTOR = 1

		if args.external_stress:
			if len(args.external_stress) > 1:
				external_stress = float(args.external_stress)
			else:
				external_stress = list(args.external_stress)
			mode_input['external stress'] = external_stress
		elif 'external stress' in mode_input:
			external_stress = mode_input['external stress']
		else:
			external_stress = 1

		if args.CHARACTERSISTIC_TIMESCALE:
			CHARACTERSISTIC_TIMESCALE = float(args.CHARACTERSISTIC_TIMESCALE)
			mode_input['thermostat timescale'] = CHARACTERSISTIC_TIMESCALE
		elif 'thermostat timescale' in mode_input:
			CHARACTERSISTIC_TIMESCALE = mode_input['thermostat timescale']
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
	
	# Stack input variables in a dataframe
	param_df = pd.DataFrame.from_dict(mode_input, orient='index', columns=[''])

	print(f'Mode: {mode} ({modes[mode]})')
	if args.test:
		print('Running in test mode. No logs or outputs will be saved.')
	print('\nInput:')
	print(param_df, '\n')

	start = datetime.datetime.now()
	print(f'\nStarted: {start}\n')

	# Write input parameters to log file
	if args.test == False:
		if log_file is not None:
			#with open(path+log_file, 'a') as f:
			with open(log_file, 'a') as f:
				print('='*80, file=f)
				print('Input:', file=f)
				print(param_df, file=f)
				print(f'\nStarted: {start}\n', file=f)


	# Runs the setup initialised for a given mode
	setup.run()


	print('\nFinished!')
	end = datetime.datetime.now()
	print(f'Completed: {end} (elapsed time: {end-start})')

	# Additional information to log file.
	if args.test == False:
		if log_file is not None:
			#with open(path+log_file, 'a') as f:
			with open(log_file, 'a') as f:
				print(f'\nCompleted: {end} (elapsed time: {end-start})\n', file=f)
				


if __name__ == '__main__':
	main()