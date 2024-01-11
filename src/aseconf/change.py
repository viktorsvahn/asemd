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

		self.transfered_data = {}
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
					transfer_items = set(self.mode_params['transfer info'])
					
					transfer_dict = {}
					for item in transfer_items:
						transfer = a.info[item]
						self.atoms[i].info[item] = transfer
						transfer_dict[item] = transfer
					self.transfered_data[i+1] = transfer_dict

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
		transfer_out = pd.DataFrame.from_dict(self.transfered_data, orient='index')
		add_out = pd.DataFrame.from_dict(self.added_data, orient='index')
		out = {
			'Transfered tags':transfer_out,
			'Added tags':add_out,
		}
		# Create multilevel datafram using concatenation
		out = pd.concat(out, axis=1)
		

		# USESD FOR DEBUGGING
		#print(self.structures)



		if len(self.structures) <= 100:
			print(out.to_string())
		else:
			print(self.structures)
			print(
				f'Transfered {0} in {len(self.structures)} (of {len(self.atoms)}) structures',
				'',
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

