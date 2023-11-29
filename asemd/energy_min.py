#!/usr/bin/python


from ase.optimize import BFGS, MDMin, GPMin
from ase.io import read, write

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
			*args
		):
		super().__init__(*args)
		self.optimiser = optimiser
		self.STEPS = STEPS
		self.FMAX= FMAX


	def run(self):
		"""Runs an energy minimisation using the chosen optimiser.

		The method requires the number step, a maximum force criteria or both."""
		
		# Initiate dynamic optimiser object
		self.dyn = global_vars.get(self.mode_params['optimiser'])(self.atoms)
		
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

		# Saves output after obtaining properties
		self.save_structure()

	def save_structure(self):
		"""If an output filename has been given, the the output is saved to a
		file by appending all atoms objects to the file."""
		if self.output_structure:
			write(self.output_structure, self.atoms)
		else:
			pass
