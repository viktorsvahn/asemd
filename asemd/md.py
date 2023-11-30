#!/usr/bin/python


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

		# Set initial velocities based on temperature
		MaxwellBoltzmannDistribution(self.atoms, temperature_K=self.TEMPERATURE)


	# Auxillary methods
	def save_traj(self):
		"""Method that generates a trajectory object."""
		# Generate a trajectory object and attaches it to the dynamic object
		if self.output_structure:
			self.traj = Trajectory(self.output_structure, 'w', self.atoms)
			self.dyn.attach(self.traj.write, interval=self.DUMP_INTERVAL)

	def save_log(self):
		"""Logging capabilities for simulations."""
		# Generate log object and attach it to dynamic object
		logger = MDLogger(
			self.dyn,
			self.atoms,
			logfile=self.log_file,
			mode='a'
		)
		self.dyn.attach(
			logger
		)
		
	def run(self):
		"""Runs a molecular dynamics simulation under a chosen ensemble."""
		# Add output generator to dynamic object for info during run
		self.dyn.attach(self.print_energy, interval=self.DUMP_INTERVAL)

		# Logging
		self.save_traj()
		self.save_log()

		# Running
		self.dyn.run(steps=self.STEPS)


	# Ensemble methods
	def nve(self):
		"""Sets up a dynamic object for a microcanonical ensemble simulation."""
		# Initiate dynamic object
		self.dyn = VelocityVerlet(
			self.atoms,
			timestep=self.TIME_STEP*units.fs
		)

	def nvt(self):
		"""Sets up a dynamic object for a canonical ensemble simulation using
		a Langevin thermostat."""
		# Initiate dynamic object
		self.dyn = Langevin(
			self.atoms,
			timestep=self.TIME_STEP*units.fs,
			temperature_K=self.TEMPERATURE,
			friction=self.FRICTION
		)

	def npt(self):
		"""Sets up a dynamic object for an isobaric ensemble simulation using 
		a Nosé-Hoover thermostat and a Parrinello-Rahman barostat."""
		self.dyn = NPT(
			self.atoms,
			timestep=self.TIME_STEP*units.fs,
			temperature_K=self.TEMPERATURE,
			pfactor=self.PFACTOR*units.GPa*(units.fs**2),
			ttime=self.CHARACTERSISTIC_TIMESCALE*units.fs,
			externalstress = self.external_stress*units.bar
		)