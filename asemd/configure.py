#!/usr/bin/python


import copy
import sys
import os

from ase.io import read, iread, write
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

		# Raise error if no calcualtor has been specified
		if ('calculator' not in self.mode_params) or (
				self.mode_params['calculator'] == None):
			print('Missing calculator!')
			print('''Choose EMT (for testing) or specify a python script that contain all calculator\ndefinitions by including:\n  calculator: EMT/name_of_sctipt\nin the YAML input file.''')
		else:
			self.calculator = self.mode_params['calculator']

		# Collect geometry variables
		self.pbc = self.global_params['periodic']
		size = global_params['box size'].split(' ')
		self.size = [float(s) for s in size]

		# Reads all structures in an atoms object into a list of structures
		atoms = read(self.input_structure, ':')
		self.num_structures = len(atoms)
		if self.num_structures > 1:
			#self.atoms = copy.deepcopy(atoms)
			self.atoms = atoms
			for a in self.atoms:
				a.calc = self.acquire_calc(self.calculator)
				a.set_cell(self.size)
				a.set_pbc(self.pbc)
		else:
			#self.atoms = copy.deepcopy(atoms[0])
			self.atoms = atoms[0]
			self.atoms.calc = self.acquire_calc(self.calculator)
			self.atoms.set_cell(self.size)
			self.atoms.set_pbc(self.pbc)


	def acquire_calc(self, arg=None):
		"""Method that acquires a chose calculator. If no argument is passed,
		the method will arbitrarily choose the EMT calculator used for testing 
		purposes. 

		The calculator used for actual simulations should be defined
		in a separate python script. To choose such a calculator, this method
		should be passed with the name of the script as an argument."""
		if arg == (None or 'EMT'):
			calculator = EMT()
		elif arg is not None:
			path = os.getcwd()+'/'
			sys.path.append(path)
			#sys.path.append(self.input_structure)
			calculator = __import__(arg)
		else:
			print('Missing calculator!')
			print('''Choose EMT (for testing) or specify a python script that contain all calculator\ndefinitions by including:\n  calculator: EMT/name_of_sctipt\nin the YAML input file.''')
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
