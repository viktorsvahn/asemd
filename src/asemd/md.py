#!/usr/bin/python

import sys
import datetime
import numpy as np

from ase.md.velocitydistribution import MaxwellBoltzmannDistribution
from ase.io.trajectory import Trajectory
from ase.md.verlet import VelocityVerlet
from ase.md.langevin import Langevin
from ase.md.npt import NPT
from ase.io import read, write
from ase import units
from ase.md import MDLogger

from asemd.configure import Configure

# Collects- and appends all local variables to the global variables
# This is used to select arbitrary methods from strings using get(attr)
# For example, global_vars is a dictionary where all modules imported as
# 'from x import y' are found as {y:x}. Using global_vars.get(y)() is equivalent
# to calling 'x.y()'.
global_vars = globals().copy()
global_vars.update(locals())


class MolecularDynamics(Configure):
	"""Runs molecular dynamics simulations either in microcanonical, canonical 
	or in an isobaric isothermal ensemble. All simulations are preceded by an
	initialisiation of initial velocites according to the Maxwell-Boltzmann
	distribution of velocities at the given temperature.

	Once an enseblme has been selected for a given instance of the class the
	simulation can be run by calling the run-method on the instance.

	Logs and trajectories are saved if names for these have been provided."""
	def __init__(self,
			STEPS,
			TEMPERATURE,
			TIME_STEP,
			FRICTION,
			PFACTOR,
			CHARACTERSISTIC_TIMESCALE,
			DUMP_INTERVAL,
			external_stress,
			log_file,
			*args
		):
		super().__init__(*args)
		self.STEPS = STEPS
		self.TEMPERATURE = TEMPERATURE
		self.TIME_STEP = TIME_STEP
		self.FRICTION = FRICTION
		self.PFACTOR = PFACTOR
		self.CHARACTERSISTIC_TIMESCALE = CHARACTERSISTIC_TIMESCALE
		self.DUMP_INTERVAL = DUMP_INTERVAL
		self.external_stress = external_stress
		self.log_file = log_file	

		# This is used together with self.print_energy_wrapper and allows us to 
		# attach self.print_energy to the dynamic object inside a loop.
		self.atoms_handle = 0

		# Stores a set of dynamic objects for each atoms object.
		self.dyns = []


	def run(self):
		"""Runs a molecular dynamics simulation under a chosen ensemble."""
		for i, d in enumerate(self.dyns):
			# Handles are used to 		
			self.dyns_handle = d
			self.atoms_handle = self.atoms[i]

			del self.atoms_handle.calc
			try:
				self.atoms_handle.calc = self.acquire_calc(self.calculator)
			except:
				self.error_msg(
					'CRITICAL ERROR',
					'Missing calculator!',
					'Select EMT (for testing) or specify a python script that contains all calculator\ndefinitions by including:',
					'Global/MODE:\n  calculator: EMT/name_of_script',
					'in the YAML input file.'
				)
				sys.exit()
			
			# Set initial velocities based on temperature
			MaxwellBoltzmannDistribution(self.atoms_handle, temperature_K=self.TEMPERATURE)
			
			if len(self.atoms) > 1:
				start = datetime.datetime.now()
			print(f'Running structure: {i+1} (of {len(self.atoms)})')

			# Add output generator to dynamic object for info during run
			d.attach(self.print_energy_wrapper, interval=self.DUMP_INTERVAL)
			
			# Logging and trajectory saving
			if self.output_structure:
				traj_name = f'{i}_'+self.output_structure
				self.traj = Trajectory(traj_name, 'w', self.atoms[i])
				d.attach(self.traj.write, interval=self.DUMP_INTERVAL)
				
				# Logging
				logger = MDLogger(
					d,
					self.atoms[i],
					peratom=False,
					logfile=self.log_file,
					mode='a'
				)
				d.attach(
					logger,
				)
				
				with open(self.log_file, 'a') as f:
					if i != 0:
						print('', file=f)
					print(f'Structure: {i+1} (of {len(self.atoms)})', file=f)


			# Running
			d.run(steps=self.STEPS)


			if len(self.atoms) > 1:
				end = datetime.datetime.now()
				#print(f'Potential energy: {energy:.4f} eV')
				print(f'Completed after {end-start}\n')
				with open(self.log_file, 'a') as f:
					print(f'Completed after {end-start}\n', file=f)


	# Ensemble initialisation methods
	def nve(self):
		"""Sets up a dynamic object for a microcanonical ensemble simulation."""
		for i, a in enumerate(self.atoms):
			# Initiate dynamic object
			dyn = VelocityVerlet(
				a,
				timestep=self.TIME_STEP*units.fs
			)
			
			self.dyns.append(dyn)

	def nvt(self):
		"""Sets up a dynamic object for a canonical ensemble simulation using
		a Langevin thermostat."""
		for i, a in enumerate(self.atoms):
			# Initiate dynamic object
			dyn = Langevin(
				a,
				timestep=self.TIME_STEP*units.fs,
				temperature_K=self.TEMPERATURE,
				friction=self.FRICTION
			)

			self.dyns.append(dyn)


	def npt(self):
		"""Sets up a dynamic object for an isobaric ensemble simulation using 
		a Nosé-Hoover thermostat and a Parrinello-Rahman barostat."""
		for i, a in enumerate(self.atoms):
			print(self.PFACTOR, type(self.PFACTOR))
			if self.PFACTOR is not None:
				self.PFACTOR = float(self.PFACTOR)
			else:
				pass

			dyn = NPT(
				a,
				timestep=self.TIME_STEP*units.fs,
				temperature_K=self.TEMPERATURE,
				pfactor=self.PFACTOR*units.GPa*(units.fs**2),
				ttime=self.CHARACTERSISTIC_TIMESCALE*units.fs,
				externalstress = self.external_stress*units.bar
			)

			self.dyns.append(dyn)

	# Auxillary methods
	def print_energy_wrapper(self):
		"""Wrapper function that allows self.print_energy to be attached to 
		dynamic objects within a loop."""
		return self.print_energy(self.atoms_handle)
	

	#def save_traj(self, dyn=None):
	#	"""Method that generates a trajectory object."""
	#	# Generate a trajectory object and attaches it to the dynamic object
	#
	#	if dyn is None:
	#		dyn = self.dyns
	#
	#	if self.output_structure:
	#		self.traj = Trajectory(self.output_structure, 'w', self.atoms)
	#		self.dyn.attach(self.traj.write, interval=self.DUMP_INTERVAL)
	
	#def save_log(self, dyn=None):
	#	"""Logging capabilities for simulations."""
	#	# Generate log object and attach it to dynamic object
	#	if dyn is None:
	#		dyn = self.dyns
	#
	#	logger = MDLogger(
	#		dyn,
	#		self.atoms_handle,
	#		peratom=False,
	#		logfile=self.log_file,
	#		mode='a'
	#	)
	#	dyn.attach(
	#		logger,
	#		peratom=False
	#	)
	

	#def save_traj_wrapper(self):
	#	"""Wrapper function that allows self.save_log to be attached to 
	#	dynamic objects within a loop."""
	#	return self.save_traj(self.dyns_handle)
	
	#def save_log_wrapper(self):
	#	"""Wrapper function that allows self.save_log to be attached to 
	#	dynamic objects within a loop."""
	#	return self.save_log(self.dyns_handle)
