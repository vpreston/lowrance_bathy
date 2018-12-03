#!/usr/bin/python
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import csv

def parse_lowrance(sounding_file, nav_file, write_filename="out.csv"):
	''' Extracts the critical information from the files in order to write master data file'''

	# First extract the sounding data
	data = open(sounding_file)
	parsed_reading = []
	for line in data:
		if 'No' in line:
			# Extract the time stamp and convert to Universal Seconds
			base_time = line.strip('/n').split(',')[0].split(' ')[1]
			uni_time = float(base_time.split(':')[0])*60.*60. + float(base_time.split(':')[1])*60. + float(base_time.split(':')[2])
		elif 'Time' in line:
			# Skip periodic lines of trash data
			pass
		else:
			# The rest of the data is sounding information
			dist_out = line.split('	')[1] # lateral (port, starboard) offset of the scan
			dist_down = line.split('	')[3] # depth reading
			if 'time' not in dist_out:
				parsed_reading.append([uni_time, float(dist_out), float(dist_down)]) # write time, lateral distance, and depth to list

	print 'Sonar Data Parsed' # status output

	# Now get the nav data and insert it into the table
	data = open(nav_file)
	complete_data = []
	for i,line in enumerate(data):
		if 'Date' in line:
			# Skip lines of trash data
			pass
		else:
			# All other lines will contain a timestamp and the navigation data of interest
			base_time = line.strip('/n').split(',')[1]
			uni_time = float(base_time.split(':')[0])*60.*60. + float(base_time.split(':')[1])*60. + float(base_time.split(':')[2])
			lat = float(line.split(',')[2])
			lon = float(line.split(',')[3])
			heading = float(line.split(',')[4])

			# Match the timestamps and the navigation reading in the sounding file
			for l in parsed_reading:
				if l[0] == uni_time:
					complete_data.append(l+[lat,lon,heading])

	# Write the complete structure to file
	with open(write_filename,"w") as f:
	    wr = csv.writer(f)
	    wr.writerows(complete_data)

	print 'Raw Nav Data Inserted' # Send status message

def plot_xyz(xyz_file):
	data = open(site_xyz)
	x = []
	y = []
	z = []
	for line in data:
		if 'X' not in line:
			x.append(float(line.split(',')[0]))
			y.append(float(line.split(',')[1]))
			z.append(float(line.split(',')[2]))

	fig = plt.figure()
	ax = fig.add_subplot(111, projection='3d')
	ax.scatter(x,y,z,c=z)
	ax.set_xlabel('Easting')
	ax.set_ylabel('Northing')
	ax.set_zlabel('Depth')
	plt.show()


if __name__ == '__main__':
	# File of the Sounding Data
	site_reading = '/home/vpreston/Documents/courses/2.688/Project/Sonar0002_sl3.txt'
	# File of the Lowrance Navigation Data
	site_nav = '/home/vpreston/Documents/courses/2.688/Project/Sonar0002_sl3.csv'
	# File of XYZ values parsed by SonarWiz
	site_xyz = '/home/vpreston/Documents/courses/2.688/Project/kelp/Sonar0002_sl3.xyz'	

	# Create a CSV file of the sounding and navigation data
	parse_lowrance(site_reading, site_nav, 'out_all.csv')

	# Plots the XYZ file (the "raw data")
	plot_xyz(site_xyz)

