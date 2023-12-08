#!/usr/bin/python

import numpy as np

from ase.io import read, write

from asemd.configure import Configure


class SinglePoint(Configure):
	"""Carries out a single point calculation on all structures in a given 
	input structure for different properties such as forces and energy.

	Evaluation of charges has not yet been implemented.
	
	Methods:
	run: Runs the single point calculations within the instance object.
	acquire_property: Evaluates a given property an all atoms-objects found in 
	the input file. The single point mode has support for input files that 
	contain multiple structures.

	Supported properties:
		- Forces
		- Energies
		- Momenta
		- Stress
		- Velocities"""


	

	def __init__(self, *args):
		super().__init__(*args)

		self.attribute_map = {
			'forces':'get_forces',
			'energies':'get_potential_energies',
			'momenta':'get_momenta',
			'momenta':'get_momenta',
			'velocities':'get_velocities'
		}

	def run(self):
		"""Runs the single point evaluation of the properties that have been
		specified in the YAML input file.

		Supported properties:
		- forces
		- energies
		- momenta
		- stress
		- velocities"""

		# Checks to see if properties have been assigned correctly in the input
		if ('evaluate' in self.mode_params) and (self.mode_params['evaluate'] is not None):
			self.evaluate = set(self.mode_params['evaluate'])

			# Runs evaluation on all attributes
			for attribute in self.evaluate:
				self.acquire_property(attribute)
			
		else:
			print('Nothing to evaluate!')
			print('Choose a property to evaluate by including:\nevaluate:\n  - property\nin the YAML input file.')

		# Saves output after obtaining properties
		self.save_structure()

	def acquire_property(self, attribute):
		"""Evaluates the input structure for the properties specified in the 
		input."""
		# This is achieved using the getattr-method which concatenates the first
		# and second arguments as first.second. For example, if first=a and 
		# second='get_forces', then attr=a.get_forces. The added parenthesis
		# results in the correct expression a.get_forces().
		if self.num_structures > 1:
			for a in self.atoms:
				a.arrays.pop(attribute)
				prop = getattr(a, self.attribute_map[attribute])()
				a.arrays[attribute] = prop
		else:
			self.atoms.arrays.pop(attribute)
			prop = getattr(self.atoms, attribute)()
			self.atoms.arrays[attribute] = prop

	def save_structure(self):
			"""If an output filename has been given, the the output is saved to a
			file by appending all atoms objects to the file."""
			if self.output_structure:
				write(self.output_structure, self.atoms)
			else:
				pass