#!/usr/bin/python

import os
import datetime
import numpy as np
import pandas as pd

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
	def __init__(self, log_file, *args):
		super().__init__(*args)
		self.log_file = log_file

		self.attribute_map = {
			'forces':'get_forces',
			'energies':'get_potential_energies',
			'momenta':'get_momenta',
			'velocities':'get_velocities',
			'charges':'get_charges'
		}

		self.output_map = {
			'forces':'Max. force [eV/Å]',
			'energy':'Potential energy [eV]',
			'energies':'Max. energies [eV]',
			'momenta':'Max. momentum [kg*m/s]',
			'velocities':'Max. velocity [m/s]',
			'charges':'Max. charge'
		}

		self.data = {}


	def run(self):
		"""Runs the single point evaluation of the properties that have been
		specified in the YAML input file.

		Supported properties:
		- forces
		- energies
		- momenta
		- stress
		- velocities"""
		for i, a in enumerate(self.atoms):
			out = {}

			# Prints timestamps and indices
			if len(self.atoms) > 1:
				start = datetime.datetime.now()
			print(f'Running structure: {i+1} (of {len(self.atoms)})')

			# Checks to see if properties have been assigned correctly in the input
			if ('evaluate' in self.mode_params) and (
				self.mode_params['evaluate'] is not None):
				self.evaluate = set(self.mode_params['evaluate'])

				# Runs evaluation on all attributes
				for attribute in self.evaluate:
					print(f'Evaluating: {attribute}')

					a.calc = self.acquire_calc(self.calculator)
					# Evaluate property
					prop = self.acquire_property(attribute, a)			
					
					# Evaluates maximum attribute qty
					# If attribute is a vector-qty, evaluate max norm
					if attribute is ('forces' or 'velocities' or 'momenta'):
						propx, propy, propz = prop[:,0], prop[:,1], prop[:,2]
						prop_vectors = (propx**2 + propy**2 + propz**2)**0.5
						out[self.output_map[attribute]] = np.max(prop_vectors)
					else:
						out[self.output_map[attribute]] = np.max(prop)
			else:
				pass

			# Stack attribute evaluations with potential energy
			energy = a.get_potential_energy()
			out[self.output_map['energy']] = energy
			self.data[i] = out

			if len(self.atoms) > 1:
				end = datetime.datetime.now()
				print(f'Potential energy: {energy:.4f} eV')
				print(f'Completed after {end-start}\n')

		#print(self.data)
		self.out = pd.DataFrame.from_dict(self.data, orient='index')
		if len(self.atoms) < 100:
			print(self.out.to_string())
		else:
			self.error_msg(
				'Too many structures to print tabulated summary of output.',
				'Please refer to the log file stored under logs/.'
			)
		
		if self.log_file:
			with open(self.log_file, 'a') as f:
				print(self.out, file=f)

		self.save_structure(None)


	def acquire_property(self, attribute, atoms):
		"""Evaluates the input structure for the properties specified in the 
		input."""
		# This is achieved using the getattr-method which concatenates the 
		# first and second arguments as first.second. For example, if first=a 
		# and second='get_forces', then attr=a.get_forces. The added parenthesis
		# results in the correct expression a.get_forces().
		
		prop = getattr(atoms, self.attribute_map[attribute])()
		atoms.arrays[attribute] = prop
		return prop

		

		
		"""		
		for i, a in enumerate(self.atoms):
			out = {}
			
			# Prints timestamps and indices
			if len(self.atoms) > 1:
				start = datetime.datetime.now()
			print(f'Running structure: {i+1} (of {len(self.atoms)})')
			

			prop = getattr(a, self.attribute_map[attribute])()
			a.arrays[attribute] = prop
			

			# Evaluates maximum attribute qty
			# If attribute is a vector-qty, evaluate max norm
			if attribute is ('energies' or 'energy'):
				out[self.output_map[attribute]] = np.max(prop)
			else:
				propx, propy, propz = prop[:,0], prop[:,1], prop[:,2]
				prop_vectors = (propx**2 + propy**2 + propz**2)**0.5
				out[self.output_map[attribute]] = np.max(prop_vectors)

			# Stack attribute evaluations with potential energy
			out[self.output_map['energy']] = a.get_potential_energy()
			self.data[i] = out

			###################################################################
			# This block should be used if 'atoms' is replaced by self.atoms
			# at line 74 in configure.py. Then, self.save_structure should be 
			# removed from self.run and write in self.save_structure should have
			# append=True set.
			###################################################################
			#try:
			#	a.arrays.pop(attribute)
			#except:
			#	prop = getattr(a, self.attribute_map[attribute])()
			#	a.arrays[attribute] = prop

				# It is important to have this method here, and not under 
				# self.run. Otherwise ASE will sometimes not forget previous 
				# evaluations and instead save duplicate evaluations on multiple 
				# structres. This requires append=True to be set. 
				# Why this occurs is unclear.
				#self.save_structure(a)

			if len(self.atoms) > 1:
				end = datetime.datetime.now()
				print(f'Completed after {end-start}\n')
		"""

	def save_structure(self, structure):
		"""If an output filename has been given, the the output is saved to a
		file by appending all atoms objects to the file."""
		if self.output_structure:
			#write(self.output_structure, structure, append=True)
			write(self.output_structure, self.atoms)
		else:
			pass