
#!/usr/bin/python

import sys
import math
import datetime
import numpy as np

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



		# NOT IMPLEMENTED
		FRAC = 0.15
		self.LAST_STEPS = math.ceil(self.STEPS*FRAC)
		self.FIRST_STEPS = self.STEPS - self.LAST_STEPS
		#print(FIRST_STEPS, LAST_STEPS)

		

		if (self.STEPS is None) and (self.FMAX is None):
			self.error_msg(
				'CRITICAL ERROR',
				'No minimisation criteria given!',
				'Choose the number of STEPS or maximum allowed force by including one of:\n  STEPS: number\n  FMAX: value\nin the YAML input file.',
				'Minimisation aborted.'
			)
			sys.exit()

		
		# Want to be able to save traj and determine trends
		#self.energy_tails = []

	def run(self):
		"""Runs an energy minimisation using the chosen optimiser.

		The method requires the number of steps, a maximum force--criteria or both."""

		# log, steps, last energy and f, save series of last energy and f
		energy_tail = []

		# Checks for presence of selected structure handle
		# Prints warning if not present
		if (self.structure_handle is False) and (False in self.handle_test):
			self.error_msg(
				'Warning:',
				'Could not find the structure handle within in the metadata.',
				'This information may not appear in the stdout'
			)

		for i, a in enumerate(self.atoms):
			# Removing this might cause slurm to not produce any output
			print('', flush=True)
			if i in self.structures:
				self.printout = []

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


				# Initiate dynamic optimiser object
				opt = global_vars.get(self.mode_params['optimiser'])
				if self.log_file is None:
					#self.dyn = opt(a, logfile='-')
					self.dyn = opt(a)
				else:	
					self.dyn = opt(a, logfile=self.log_file)
				

				# Logging and saving
				#if self.output_structure and 'traj' in self.output_structure:
				#	print('FFODSHOSDFHSDFOHFGSDFOHNSDFS')
				#	self.save_traj(a)
				
				#self.structure_info(a)
				#self.dyn.attach(self.print_energy, interval=self.DUMP_INTERVAL)
				if self.output_structure:
					with open(self.log_file, 'a') as f:
						if i != 0:
							print('', file=f)
						print(f'Structure: {i+1} (of {len(self.atoms)})', file=f)


				# Run the minimisation
				if (self.STEPS is None) and (self.FMAX is not None):
					self.dyn.run(fmax=self.FMAX)

				elif (self.STEPS is not None) and (self.FMAX is None):
					self.dyn.run(steps=self.FIRST_STEPS, fmax=1e-6)

				elif (self.STEPS is not None) and (self.FMAX is not None):
					self.dyn.run(steps=self.FIRST_STEPS, fmax=self.FMAX)

				"""
				# Run the minimisation
				if (self.STEPS is None) and (self.FMAX is not None):
					self.dyn.run(fmax=self.FMAX)
					


				elif (self.STEPS is not None) and (self.FMAX is None):
					self.dyn.run(steps=self.FIRST_STEPS)
					for STEP in range(self.LAST_STEPS):
						self.dyn.run()
						fx, fy, fz = a.get_forces()[:,0], a.get_forces()[:,1], a.get_forces()[:,2]
						forces = (fx**2 + fy**2 + fz**2)**0.5
						energy = a.get_potential_energy()

						eout = f'Potential energy: {energy:.4f}'
						fout = f'max force: {max(forces):.4f}'
						print(f'Step: {STEP+self.FIRST_STEPS+1}', eout, fout)


				elif (self.STEPS is not None) and (self.FMAX is not None):
					self.dyn.run(steps=self.FIRST_STEPS, fmax=self.FMAX)
					for STEP in range(self.LAST_STEPS):
						self.dyn.run(fmax=self.FMAX)
						fx, fy, fz = a.get_forces()[:,0], a.get_forces()[:,1], a.get_forces()[:,2]
						forces = (fx**2 + fy**2 + fz**2)**0.5
						energy = a.get_potential_energy()

						eout = f'Potential energy: {energy:.4f}'
						fout = f'max force: {max(forces):.4f}'
						print(f'Step: {STEP+self.FIRST_STEPS+1}', eout, fout)

				"""

				####### Inefficient! Need to extract this from the dyn object!
				fx, fy, fz = a.get_forces()[:,0], a.get_forces()[:,1], a.get_forces()[:,2]
				forces = (fx**2 + fy**2 + fz**2)**0.5
				energy = a.get_potential_energy()
				
				if len(self.atoms) > 1:
					end = datetime.datetime.now()
					print(f'Structure {i+1} of ({len(self.atoms)}) completed after {end-start}')

				print(f'potential energy: {energy:.4f}')
				print(f'max force: {max(forces):.4f}\n')
				

				if self.output_structure:
					with open(self.log_file, 'a') as f:
						print(f'Completed after {end-start}\n', file=f)

			if i % self.DUMP_INTERVAL == 0:
				self.save_structure(a)

			del a.calc


	def save_structure(self, a):
		"""If an output filename has been given, the the output is saved to a
		file by appending all atoms objects to the file."""
		if self.output_structure:
			write(self.output_structure, a, append=True)
		else:
			pass

	def save_traj(self, atoms):
		"""Method that generates a trajectory object."""
		# Generate a trajectory object and attaches it to the dynamic object
		if self.output_structure:
			ext = self.output_structure.split('.')[-1]
			new_filename = self.output_structure.replace('.'+ext, '_tmp.traj')

			self.traj = Trajectory(new_filename, 'w', atoms)
			self.dyn.attach(self.traj.write, interval=self.DUMP_INTERVAL)
		else:
			pass
