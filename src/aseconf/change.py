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


class ChangeHeader(Configure):
	""" """
	def __init__(self, *args):
		super().__init__(*args)

		if 'add info' in self.mode_params:
			pass

		if 'transfer info' in self.mode_params:
			# Load file containing the header
			try:
				self.header_structures = self.load_structure(self.mode_params['header file'])
			except:
				self.error_msg(
					'CRITICAL ERROR',
					'Config file contains no header file!',
					'Please choose a header file that ',
					'Global:\n  box size:  x y z',
					'to the YAML input file.'
				)
				sys.exit()


	def run(self):
		""" """
		for i, a in enumerate(self.header_structures):
			if i in self.structures:
				del a.calc, self.atoms[i].calc

				if ('transfer info' in self.mode_params) and (
					self.mode_params['transfer info'] is not None):
					transfer_items = set(self.mode_params['transfer info'])

				if ('add info' in self.mode_params) and (
					self.mode_params['add info'] is not None):
					add_items = self.mode_params['add info']

				# Transfer items
				for item in transfer_items:
					self.atoms[i].info[item] = a.info[item]

				# Add new items to info
				for item in add_items.keys():
					self.atoms[i].info[item] = str(add_items[item])

			else:
				pass

		if self.output_structure:
			self.save_structure(self.atoms, append=False)





	def save_structure(self, structure, append=True):
		"""If an output filename has been given, the the output is saved to a
		file by appending all atoms objects to the file."""
		if self.output_structure:
			write(self.output_structure, structure, append=append)
		else:
			pass

