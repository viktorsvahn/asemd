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

from aseconf.configure import Configure


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
					'CH:\n  header file:  filename.xyz',
					'to the YAML input file.'
				)
				sys.exit()

		self.transfered_info = {}
		self.transfered_arrays = {}
		self.added_data = {}


	def run(self):
		"""Transfers information tags in the headers between files or adds new
		tags as specifiged in the config file."""
		# output data is stored as nested dicts to allow for the tracking of
		# unique indices, for each transfered/added info tag.

		for i, a in enumerate(self.header_structures):
			if i in self.structures:

				# Transfer info items between files
				if ('transfer info' in self.mode_params) and (
					self.mode_params['transfer info'] is not None):
					transfer_info = set(self.mode_params['transfer info'])
					
					transfer_info_dict = {}
					for item in transfer_info:
						try:
							transfer = a.info[item]
							self.atoms[i].info[item] = transfer
							transfer_info_dict[item] = transfer
						except:
							print(f'Transfer of {item} in structure {i+1} (of {len(self.atoms)}) failed')
					self.transfered_info[i+1] = transfer_info_dict

				# Transfer arrays between files
				if ('transfer arrays' in self.mode_params) and (
					self.mode_params['transfer arrays'] is not None):
					transfer_arrays = set(self.mode_params['transfer arrays'])

					transfer_arrays_dict = {}
					for item in transfer_arrays:
						try:
							transfer = a.arrays[item]
							self.atoms[i].arrays[item] = transfer
							transfer_arrays_dict[item] = 'True'
						except:
							print(f'Transfer of {item} in structure {i+1} (of {len(self.atoms)}) failed')
					self.transfered_arrays[i+1] = transfer_arrays_dict

				# Add new items to info
				if ('add info' in self.mode_params) and (
					self.mode_params['add info'] is not None):
					add_items = self.mode_params['add info']

					add_dict = {}
					for item in add_items.keys():
						add = add_items[item]
						self.atoms[i].info[item] = add
						add_dict[item] = add
					self.added_data[i+1] = add_dict

			else:
				pass

		# Stack and print output to stdout
		transfer_info_out = pd.DataFrame.from_dict(self.transfered_info, orient='index')
		transfer_arrays_out = pd.DataFrame.from_dict(self.transfered_arrays, orient='index')
		add_out = pd.DataFrame.from_dict(self.added_data, orient='index')
		
		# Create multilevel datafram using concatenation
		out = {
			'Added tags':add_out,
			'Transfered tags':transfer_info_out,
			'Transfered arrays':transfer_arrays_out,
		}
		out = pd.concat(out, axis=1)
		

		if len(self.structures) <= 100:
			print(out.to_string())
		else:
			print(out)
			print(
				f'Altered data in {len(self.structures)} (of {len(self.atoms)}) structures.',
			)

		# Save output structure with altered headers
		if self.output_structure:
			self.save_structure(self.atoms, append=False)


	def save_structure(self, structure, append=True):
		"""If an output filename has been given, the the output is saved to a
		file by appending all atoms objects to the file."""
		if self.output_structure:
			write(self.output_structure, structure, append=append)
		else:
			pass

