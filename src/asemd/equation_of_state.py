#!/usr/bin/python

import os
import datetime
import numpy as np
import pandas as pd

from ase.io import read, write
from ase.io.trajectory import Trajectory
from ase.eos import EquationOfState
from ase.io import read
import ase.units as units

from asemd.configure import Configure


class EquationState(Configure):
	""" """
	def __init__(self, log_file=False, *args):
		super().__init__(*args)
		self.log_file = log_file

		#self.attribute_map = {
		#	'forces':'get_forces',
		#	'energies':'get_potential_energies',
		#	'momenta':'get_momenta',
		#	'momenta':'get_momenta',
		#	'velocities':'get_velocities'
		#}
		if 'method' in self.mode_params:
			self.method = self.mode_params['method']
		else:
			self.method = 'birchmurnaghan'
			self.mode_params['method'] = self.method


		eos_range = self.mode_params['range'].split()
		eos_range = [float(s) for s in eos_range]
		self.start, self.stop, self.num_points = eos_range
		self.num_points = int(self.num_points)

		# Needed in order to make tmp files with same name as intended output
		if self.output_structure:
			self.ext = self.output_structure.split('.')[-1]

		self.data = {}
		#mode_param_df = pd.DataFrame.from_dict(mode_input, orient='index', columns=[''])	
		#self.out = pd.DataFrame.from_dict(self.data, orient='index', columns=['V0', 'E0', 'B'])

	def run(self):
		"""Evaluates an equation of state on the given set of structures."""
		for i, a in enumerate(self.atoms):
			if i+1 in self.structures:

				if i < 0:
					del self.atoms[i-1].calc
				try:
					a.calc = self.acquire_calc(self.calculator)
				except:
					self.error_msg(
						'CRITICAL ERROR',
						'Missing calculator!',
						'Select EMT (for testing) or specify a python script that contains all calculator\ndefinitions by including:',
						'Global/MODE:\n  calculator: EMT/name_of_script',
						'in the YAML input file.'
					)
					sys.exit()

				if len(self.atoms) > 1:
					start = datetime.datetime.now()
				
				self.size_variation(i, a)
				self.data[i+1] = self.run_eos(i, a)

				if len(self.atoms) > 1:
					end = datetime.datetime.now()
					print(f'Structure {i+1} of ({len(self.atoms)}) completed after {end-start}\n')
		
		self.out = pd.DataFrame.from_dict(self.data, orient='index', columns=['V0 [Å^3]', 'E0 [eV]', 'B [GPa]'])
		self.out.reindex(self.structures)
		
		if len(self.structures) <= 100:
			print(self.out.to_string())
		else:
			self.error_msg(
				'Warning',
				'Too many structures to print tabulated summary of output.',
				'Please refer to the log file stored under logs/.'
			)
		
		if self.log_file:
			with open(self.log_file, 'a') as f:
				print(self.out.to_string(), file=f)

		if self.output_structure is False:
			try:
				os.remove(self.traj_name)
			except:
				pass


	def size_variation(self, index, atoms):
		""" """
		if self.output_structure:
			self.traj_name = self.output_structure.replace('.'+self.ext, f'_{index}.traj')
		else:
			self.traj_name = 'eos_test.traj'
		traj = Trajectory(self.traj_name, 'w')
		

		for sfactor in np.linspace(self.start, self.stop, self.num_points):
			atoms.set_cell(atoms.get_cell()*sfactor, scale_atoms=True)
			atoms.get_potential_energy()
			traj.write(atoms)


	def run_eos(self, index, atoms):
		""" """
		configs = read(self.traj_name+'@:0'+f'{self.num_points}')
		
		# Extract volumes and energies:
		volumes = [conf.get_volume() for conf in configs]
		energies = [conf.get_potential_energy() for conf in configs]

		# Removes possible spaces and hyphens from method name
		try:
			self.method = self.method.replace(' ', '')
		except:
			pass
		try:
			self.method = self.method.replace('-', '')
		except:
			pass
		eos = EquationOfState(volumes, energies, eos=self.method.lower())
		v0, e0, B = eos.fit()

		Pout = f'Pressure: {B/units.kJ*1.0e24:.4f},'
		Eout = f'minimum energy: {e0:.4f} eV,'
		Vout = f'minimum volume: {v0:.4f} Å^3'
		######## NO GOODNESS OF FIT MEASURE!
		print(Pout, Eout, Vout)

		#if self.output_structure is False:
		#	png_name = self.output_structure.replace('.'+self.ext, f'_{index}.png')
		#	eos.plot(png_name)

		return [v0, e0, B]



	def save_structure(self, structure):
		"""If an output filename has been given, the the output is saved to a
		file by appending all atoms objects to the file."""
		if self.output_structure:
			write(self.output_structure, structure, append=True)
		else:
			pass