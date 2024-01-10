#!/usr/bin/python


import copy
import sys
import os
import time

from ase.io import read, iread, write
from ase.io.trajectory import Trajectory
from ase.calculators.emt import EMT
from ase import Atoms
from ase import units


class Configure(object):
	"""Setup class that carries shared variables and methods, such as calculator 
	selection and energy output."""
	def __init__(self,
			mode_params,
			global_params,
			input_structure,
			output_structure
		):
		self.mode_params = mode_params
		self.global_params = global_params
		self.input_structure = input_structure
		self.output_structure = output_structure	




		#if 'structure index' in self.mode_params:
		#	self.structure_indices = self.mode_params['structure index']
		#else:
		#	if 'traj' in self.input_structure:
		#		self.structure_indices = -1
		#		self.mode_params['structure index'] = self.structure_indices
		#	else:
		#		self.structure_indices = False




		# Generate atoms-object list from input structure(s)
		self.atoms = self.load_structure(self.input_structure)
		#atoms = self.load_structure(self.input_structure)
		#self.atoms = [
		#	Atoms(
		#		a.symbols,
		#		a.get_positions(),
		#		cell=a.get_cell(),
		#		pbc=a.get_pbc()
		#) for a in atoms]

		#if 'box size' in self.global_params:
		#	if 'periodic' in self.global_params:
		#		self.atoms = [Atoms(a.symbols, a.get_positions(), cell=self.size, pbc=True) for a in atoms]
		#	else:
		#		self.atoms = [Atoms(a.symbols, a.get_positions(), cell=self.size, pbc=False) for a in atoms]
		#else:
		#	if 'periodic' in self.global_params:
		#		self.atoms = [Atoms(a.symbols, a.get_positions(), cell=a.get_cell(), pbc=True) for a in atoms]
		#	else:
		#		self.atoms = [Atoms(a.symbols, a.get_positions(), cell=a.get_cell(), pbc=False) for a in atoms]

		if 'structures' in self.mode_params:
			#self.structures = str(mode_params['structures'])
			self.structures = mode_params['structures']
			print(type(self.structures))
			self.structures = self.structures.split(' ')
			self.structures = self.acquire_index_range(self.structures)
		else:
			if 'traj' in self.input_structure:
				self.structures = -1
				self.STRUCTURE_INDEX = -1
				self.mode_params['structures'] = self.structures
			else:
				self.structures = [_ for _ in range(len(self.atoms))]

		#self.structures = self.mode_params['structures']
		"""
		for i, a in enumerate(self.atoms):
			if i+1 in self.structures:

				# Terminate if no cell size in input
				try:
					a.set_cell(self.size)
				except:
					# Would be neat to include structure-wise input parameters in
					# the log/stdout next to each evaluation.
					pass

					#self.error_msg(
					#	'CRITICAL ERROR',
					#	'Input file contains no cell parameters!',
					#	'Please set cell size (Å) manually by adding:',
					#	'Global:\n  box size:  x y z',
					#	'to the YAML input file.'
					#)
					#sys.exit()
				
				# Assing PBC status
				a.set_pbc(self.pbc)

				# If first calculator cannot be assigned, raise error and terminate
				#try:
				#	a.calc = self.acquire_calc(self.calculator)
				#except:
				#	self.error_msg(
				#		'CRITICAL ERROR',
				#		'Missing calculator!',
				#		'Select EMT (for testing) or specify a python script that contains all calculator\ndefinitions by including:',
				#		'Global/MODE:\n  calculator: EMT/name_of_script',
				#		'in the YAML input file.'
				#	)
				#	sys.exit()
		"""





		# Input will only be read as a traj if name includes correct extension
		# Otherwise it will be treated as a .pdb or .xyz file that may, or may
		# not, include several structures. If this attempt fails, an error is
		# raised, implying that the input may be a .traj file regardless of its
		# extension.
		"""
		if 'traj' in self.input_structure:
			# If file is trajecory, input
			self.atoms = Trajectory(self.input_structure)[self.structure_indices]
			self.atoms.calc = self.acquire_calc(self.calculator)
			self.atoms.set_cell(self.size)
			self.atoms.set_pbc(self.pbc)
		else:
			# Reads all structures in an atoms object into a list of structures
			atoms = read(self.input_structure, ':')
			self.num_structures = len(atoms)

			if self.num_structures > 1:
				#self.atoms = copy.deepcopy(atoms)
				self.atoms = atoms
				for a in self.atoms:
					a.calc = self.acquire_calc(self.calculator)
					if self.force_pbc:
						a.set_cell(self.size)
					else:
						pass
					a.set_pbc(self.pbc)
			elif self.num_structures == 1:
				# If list has length 1, atoms object is first, and only, element
				#self.atoms = copy.deepcopy(atoms[0])
				self.atoms = atoms[0]
				self.atoms.calc = self.acquire_calc(self.calculator)
				if self.force_pbc:
					self.atoms.set_cell(self.size)
				else:
					pass
				self.atoms.set_pbc(self.pbc)
			else:
				raise TypeError('Input structure might be a .traj-file. Change the input extention to .traj and try again.')
		"""

		#######################################################################
		# Thea idea was to have tha ability to print tags/names in the output
		# This might be redundant if indices are included in logs/stdout
		#######################################################################
		if 'structure handle' in self.mode_params:
			self.structure_handle = self.mode_params['structure handle']
		else:
			self.structure_handle = False
		
		# Logical test to see if specified handles are present in dataset
		# Used for printing warnings		
		info = [a.info.keys() for a in self.atoms]
		self.handle_test = {(self.structure_handle in handle) for handle in info}
		#######################################################################



	def load_structure(self, filename):
		"""Reads input files and stores them in an iterable list."""
		if 'traj' in self.input_structure:
			#structure_list = [Trajectory(filename)[self.structure_indices]]
			structure_list = [Trajectory(filename)][self.STRUCTURE_INDEX]
		else:
			#if self.structure_indices:
			#	structure_list = [read(filename, ':')[self.structure_indices]]
			#else:
			#	structure_list = read(filename, ':')
			structure_list = read(filename, ':')

		return structure_list
	


	def error_msg(self, *args):
		"""Envelopes (and prints) error messages with lines and adds empty 
		lines between each argument."""
		print('-'*80+'\n')
		for arg in args:
			print(arg+'\n')
		print('-'*80)

	def structure_info(self, atoms):
		"""Prints structure info (if any) from the header in an input file to
		stdout."""
		# Tries to only print specified handle, otherwise prints any
		if self.structure_handle and (True in self.handle_test):
			try:
				print(f'{self.structure_handle}: {atoms.info[self.structure_handle]}')
			except:
				pass
		else:
			info = atoms.info
			info_keys = info.keys()
			for handle in info_keys:
				print(f'{handle}: {info[handle]}')

	def acquire_index_set(self, arg):
		"""Converts a list of strings into a list of ranges and indices.

		Hyphens ('-') between numbers result in a two element list that
		can be converted to a complete range of indices using the class
		method self.acquire_index_range."""
		# A range [a,b] is generated by specifying 'a-b' in the input
		# Non-hyphenated values are treated as single indices
		if '-' in arg:
			arg = arg.split('-')
			for i,x in enumerate(arg):
				arg[i] = int(x)
		else:
			arg = int(arg)
		indices = arg
		return indices

	def acquire_index_range(self, arg):
		"""Converts a list of indices allowed for evaluation."""
		arg = [self.acquire_index_set(a) for a in arg]
		tmp = []

		# Converts a list to a complete set of indices and adds it to tmp
		# If element is non-list type, add single element to tmp
		for x in arg:
			if type(x) is list:
				if len(x)<2:
					pass
				else:
					subrange = [i-1 for i in range(x[0], x[1]+1)]
				tmp += subrange
			else:
				tmp.append(x)
		return tmp