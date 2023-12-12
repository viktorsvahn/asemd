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
		self.count = 0

		# Raise error if no calcualtor has been specified
		if ('calculator' not in self.mode_params) or (
				self.mode_params['calculator'] == None):
			print('Missing calculator!')
			print('''Choose EMT (for testing) or specify a python script that contains all calculator\ndefinitions by including:\n  calculator: EMT/name_of_script\nin the YAML input file.''')
		else:
			self.calculator = self.mode_params['calculator']

		# Collect geometry variables and indices
		if 'periodic' in self.mode_params:
			self.pbc = self.mode_params['periodic']
		else:
			self.pbc = False
			self.mode_params['periodic'] = self.pbc

		print(self.pbc)

		if 'box size' in self.mode_params:
			size = mode_params['box size'].split(' ')
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
		print(type(self.atoms))
		for a in self.atoms:
			a.set_cell(self.size)
			a.set_pbc(self.pbc)
			a.calc = self.acquire_calc(self.calculator)

		# Remove any previous files with the same name as target output
		if self.output_structure and (
			os.path.exists(self.output_structure)):
			print('-'*80)
			print('Warning:')
			print(f'Target output file {self.output_structure} already exist.')
			ext = self.output_structure.split('.')[-1]
			self.output_structure = self.output_structure.replace('.'+ext, '')
			self.output_structure += '_'+time.strftime("%Y%m%d-%H%M%S")+'.'+ext
			print(f'Created a new outfile called {self.output_structure}')
			print('-'*80)	
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

	def print_energy(self):
		"""Print potential-, kinetic energy (together with temperature) and the 
		total energy of the system.
		"""
		epot = self.atoms.get_potential_energy()/len(self.atoms)
		ekin = self.atoms.get_kinetic_energy()/len(self.atoms)
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

