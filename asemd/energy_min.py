#!/usr/bin/python


from ase.optimize import BFGS, MDMin, GPMin
from ase.io import read, write
from ase.io.trajectory import Trajectory

from asemd.configure import Configure


# Collects- and appends all local variables to the global variables
# This is used to select arbitrary methods from strings using get(attr)
# For example, global_vars is a dictionary where all modules imported as
# 'from x import y' are found as {y:x}. Using global_vars.get(y)() is equivalent
# to calling 'x.y()'.
global_vars = globals().copy()
global_vars.update(locals())


class EnergyMinimisation(Configure):
	"""Carries out an energy minimisation.

	Supported optimisers:
	- BFGS (recommended)
	- MDMin
	- GPMin"""
	def __init__(self,
			optimiser,
			STEPS=None,
			FMAX=None,
			DUMP_INTERVAL=1,
			log_file=None,
			*args
		):
		super().__init__(*args)
		self.optimiser = optimiser
		self.STEPS = STEPS
		self.FMAX = FMAX
		self.DUMP_INTERVAL = DUMP_INTERVAL
		self.log_file = log_file


	def run(self):
		"""Runs an energy minimisation using the chosen optimiser.

		The method requires the number step, a maximum force criteria or both."""	
		# Initiate dynamic optimiser object
		if self.log_file is None:
			self.dyn = global_vars.get(self.mode_params['optimiser'])(self.atoms)
		else:	
			self.dyn = global_vars.get(self.mode_params['optimiser'])(self.atoms, logfile=self.log_file)
		
		# Logging
		self.save_traj()
		self.dyn.attach(self.print_energy, interval=self.DUMP_INTERVAL)
		
		#print('Starting energy:')
		#self.print_energy()

		# Run the minimisation
		if (self.STEPS is None) and (self.FMAX is None):
			print('No minimisation criteria given!')
			print('''Choose the number of STEPS or maximum allowed force by including one of:\n  STEPS: number\n  FMAX: value\nin the YAML input file.''')
		elif self.STEPS == None:
			self.dyn.run(fmax=self.FMAX)
		elif self.FMAX ==None:
			self.dyn.run(steps=self.STEPS)
		else:
			self.dyn.run(steps=self.STEPS, fmax=self.FMAX)

		#print('\nFinal energy:')
		#self.print_energy()


	def save_structure(self):
		"""If an output filename has been given, the the output is saved to a
		file by appending all atoms objects to the file."""
		if self.output_structure:
			write(self.output_structure, self.atoms)
		else:
			pass

	def save_traj(self):
		"""Method that generates a trajectory object."""
		# Generate a trajectory object and attaches it to the dynamic object
		if self.output_structure:
			self.traj = Trajectory(self.output_structure, 'w', self.atoms)
			self.dyn.attach(self.traj.write, interval=self.DUMP_INTERVAL)
		else:
			pass