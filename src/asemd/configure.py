#!/usr/bin/python


import copy
import sys
import os
import time

from ase.io import read, iread, write
from ase.io.trajectory import Trajectory
from ase.calculators.emt import EMT
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


		# Switch that allows one to force new output files to overwrite old ones
		# with identical names
		if 'overwrite' in self.global_params:
			self.overwrite = True
		else:
			self.overwrite = False
			self.global_params['overwrite'] = self.overwrite

		# Raise error if no calcualtor has been specified
		if 'calculator' not in self.mode_params:
			self.calculator = False
		else:
			self.calculator = self.mode_params['calculator']

		# Collect geometry variables and indices
		if 'periodic' in self.global_params:
			self.pbc = self.global_params['periodic']
		else:
			self.pbc = False
			self.mode_params['periodic'] = self.pbc

		if 'box size' in self.global_params:
			size = global_params['box size'].split(' ')
			self.size = [float(s) for s in size]
		else:
			self.size = False

		if 'structure index' in self.mode_params:
			self.STRUCTURE_INDEX = self.mode_params['structure index']
		else:
			if 'traj' in self.input_structure:
				self.STRUCTURE_INDEX = -1
				self.mode_params['structure index'] = self.STRUCTURE_INDEX
			else:
				self.STRUCTURE_INDEX = False

		# Generate atoms-object list from input structure(s)
		self.atoms = self.load_structure(self.input_structure)
		for a in self.atoms:
			# Terminate if no cell size in input
			try:
				a.set_cell(self.size)
			except:
				self.error_msg(
					'CRITICAL ERROR',
					'Input file contains no cell parameters!',
					'Please set cell size (Å) manually by adding:',
					'Global:\n  box size:  x y z',
					'to the YAML input file.'
				)
				sys.exit()
			
			# Assing PBC status
			a.set_pbc(self.pbc)

			# If first calculator cannot be assigned, raise error and terminate
			try:
				a.calc = self.acquire_calc(self.calculator)
			except:
				self.error_msg(
					'CRITICAL ERROR',
					'Missing calculator!',
					'Select EMT (for testing) or specify a python script that contains all calculator\ndefinitions by including:',
					'MODE:\n  calculator: EMT/name_of_script',
					'in the YAML input file.'
				)
				sys.exit()

		# If previous output exist, create new files datetime handle
		if self.output_structure and (
			os.path.exists(self.output_structure)):
			if self.overwrite:
				os.remove(self.output_structure)

			else:
				# Adds datetime infor just before extension if filename is taken
				ext = self.output_structure.split('.')[-1]
				new_filename = self.output_structure.replace('.'+ext, '')
				new_filename += '_'+time.strftime("%Y%m%d-%H%M%S")+'.'+ext

				self.error_msg(
					'Warning:',
					f'Target output file {self.output_structure} already exist.',
					f'Created a new outfile called {new_filename}'
				)
				self.output_structure = new_filename
		else:
			pass


		# Input will only be read as a traj if name includes correct extension
		# Otherwise it will be treated as a .pdb or .xyz file that may, or may
		# not, include several structures. If this attempt fails, an error is
		# raised, implying that the input may be a .traj file regardless of its
		# extension.
		"""
		if 'traj' in self.input_structure:
			# If file is trajecory, input
			self.atoms = Trajectory(self.input_structure)[self.STRUCTURE_INDEX]
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
		if 'structure handle' in self.mode_params:
			self.structure_handle = self.mode_params['structure handle']
		else:
			self.structure_handle = False
		
		info = [a.info.keys() for a in self.atoms]
		self.handle_test = {(self.structure_handle in handle) for handle in info}
		


	def acquire_calc(self, arg=None):
		"""Method that acquires a chose calculator. If no argument is passed,
		the method will arbitrarily choose the EMT calculator used for testing 
		purposes. 

		The calculator used for actual simulations should be defined
		in a separate python script. To choose such a calculator, this method
		should be passed with the name of the script as an argument."""
		if arg == (None or 'EMT'):
			calculator = EMT()
		else:
			calculator = __import__(arg).calculator
		return calculator

	def print_energy(self, atoms=None):
		"""Print potential-, kinetic energy (together with temperature) and the 
		total energy of the system.
		"""
		if atoms is None:
			atoms = self.atoms
		epot = atoms.get_potential_energy()/len(atoms)
		ekin = atoms.get_kinetic_energy()/len(atoms)
		etot = epot + ekin
		temp = ekin/(1.5*units.kB)
		print(f'Energy per atom: Epot: {epot:.4f} eV, Ekin: {ekin:.4f} eV (T: {temp:3.0f} K), Etot: {etot:.4} eV')

	def load_structure(self, filename):
		"""Reads input files and stores them in an iterable list."""
		if 'traj' in self.input_structure:
			structure_list = [Trajectory(filename)[self.STRUCTURE_INDEX]]
		else:
			if self.STRUCTURE_INDEX:
				structure_list = [read(filename, ':')[self.STRUCTURE_INDEX]]
			else:
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
		stdout.

		Additional data can be printed by specifying data='..' as an argument."""
		
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
