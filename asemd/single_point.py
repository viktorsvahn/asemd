#!/usr/bin/python


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

			if 'forces' in self.evaluate:
				print(self.atoms[0].arrays['forces'])
				for a in self.atoms:
					if 'forces' in a.arrays: a.arrays.pop('forces')
				print(self.atoms[0].arrays['forces'])
				self.acquire_property('get_forces')
			if 'energies' in self.evaluate:
				for a in self.atoms:
					if 'energies' in a.arrays: a.arrays.pop('energies')
				self.acquire_property('get_potential_energies')
			if 'momenta' in self.evaluate:
				for a in self.atoms:
					if 'momenta' in a.arrays: a.arrays.pop('momenta')
				self.acquire_property('get_momenta')
			if 'stress' in self.evaluate:
				for a in self.atoms:
					if 'stress' in a.arrays: a.arrays.pop('stress')
				self.acquire_property('get_stress')
			if 'velocities' in self.evaluate:
				for a in self.atoms:
					if 'velocities' in a.arrays: a.arrays.pop('velocities')
				self.acquire_property('get_velocities')
			
		else:
			print('Nothing to evaluate!')
			print('Choose a property to evaluate by including:\nevaluate:\n  - property\nin the YAML input file.')

		# Saves output after obtaining properties
		self.save_structure()

	def acquire_property(self, attribute):
		"""Evaluates the input structure for the properties specified in the 
		input."""
		#This is achieved using the getattr-method which concatenates the first
		#and second arguments as first.second. For example, if first=a and 
		#second='get_forces', then attr=a.get_forces. The added parenthesis
		#results in the correct expression a.get_forces().
		if self.num_structures > 1:
			for a in self.atoms:
				prop = getattr(a, attribute)()
		else:
			prop = getattr(self.atoms, attribute)()

	def save_structure(self):
			"""If an output filename has been given, the the output is saved to a
			file by appending all atoms objects to the file."""
			if self.output_structure:
				write(self.output_structure, self.atoms)
			else:
				pass