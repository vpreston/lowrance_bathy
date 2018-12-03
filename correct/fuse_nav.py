#!/usr/bin/python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv
import utm
import datetime
import time
import scipy
import scipy.signal
from scipy.interpolate import griddata
from scipy import stats
import copy
import warnings
import sys


def get_seconds(x):
	''' Helper function for time conversion. Recommended that this is specialized for particular
	data inputs'''
	return x/1000. - 1.773165*24*60.*60.
	# return x/1000. - 1.76785*24*60.*60.

def interp_pix(gps_df, att_df):
	att_df = att_df.drop_duplicates(subset='TimeUS',keep='last').set_index('TimeUS')
	gps_df = gps_df.drop_duplicates(subset='TimeUS',keep='last').set_index('TimeUS')
	gps_df_index = gps_df.index
	full_pix = pd.concat([gps_df,att_df], axis=1, keys=['gps','eul'])
	full_pix = full_pix.interpolate()
	full_pix = full_pix.loc[gps_df_index]
	full_pix.columns = full_pix.columns.droplevel()
	full_df = full_pix.reset_index()
	return full_df

def get_rotated(pix, son, const_roll_offset = -2.0, save_file='data_to_fit.csv'):
	''' Function to perform rotation on data by parsing the data stuctures pix and son'''
	moment = son.Time.values #get the time values
	heading = son.Heading.values
	lateral = son.Lateral.values
	depth = son.Smoothed_Depth.values 
	easting = son.Easting.values
	northing = son.Northing.values
	rc = np.deg2rad(const_roll_offset) # apply a constant roll offset in the event that the sonar was mounted improperly
	const_mat = np.array(((1,0,0),(0,np.cos(rc), -np.sin(rc)), (0, np.sin(rc), np.cos(rc))));

	projx = []
	projy = []
	projz = []
	last_t = 0

	for t in range(len(moment)):
		if last_t != moment[t]: #if we've hanged times, get the next relevant nav data to use
			active_roll = pix.loc[pix.index == moment[t]]['Smoothed_Roll'].values[0]
			active_pitch = pix.loc[pix.index == moment[t]]['Smoothed_Pitch'].values[0]
		
		if depth[t] < 25.0 and lateral[t] < 0.: #NOTE you may want to change or remove this if structure for your data
			h = np.deg2rad(heading[t])
			r = np.deg2rad(-active_roll)
			# r = np.deg2rad(active_roll)
			p = np.deg2rad(active_pitch)

			# Make the rotation matrix
			yaw_mat = np.array(((np.sin(h), np.cos(h), 0), (np.cos(h), -np.sin(h), 0), (0, 0, 1)));
			pitch_mat = np.array(((np.cos(p),0, np.sin(p)), (0,1,0), (-np.sin(p), 0, np.cos(p))));
			roll_mat = np.array(((1,0,0),(0,np.cos(r), -np.sin(r)), (0, np.sin(r), np.cos(r))));

			# Apply rotation
			coord = np.array((0., lateral[t], depth[t]))
			rot_coord = np.dot(np.dot(np.dot(np.dot(coord,const_mat),yaw_mat),roll_mat),pitch_mat);
			# gps_coord = utm.to_latlon(rot_coord[0]+cx, rot_coord[1]+cy, 19, 'T' )
			projx.append(rot_coord[0]+easting[t])
			projy.append(rot_coord[1]+northing[t])
			projz.append(rot_coord[2])
		last_t = moment[t]

	# After the correction, anomolous points can be easily extracted if not already done so
	smoother = pd.DataFrame()
	smoother.loc[:,'X'] = projx
	smoother.loc[:,'Y'] = projy
	smoother.loc[:,'Z'] = projz

	replacer = peak_detection(smoother.X.values,window=1000,threshold=2.5)
	smoother.loc[:,'Smoothed_X'] = replacer

	replacer = peak_detection(smoother.Y.values,window=1000,threshold=2.5)
	smoother.loc[:,'Smoothed_Y'] = replacer

	replacer = peak_detection(smoother.Z.values,window=5000)
	smoother.loc[:,'Smoothed_Z'] = smoother.Z.values#replacer

	smoother.interpolate(inplace=True)
	smoother.dropna(inplace=True)
	smoother.drop_duplicates(subset=['Smoothed_X','Smoothed_Y'])

	# Save the new point cloud object
	smoother.to_csv('data_to_fit.csv')

	# Return the point cloud for diagnostic plotting
	return smoother.Smoothed_X.values, smoother.Smoothed_Y.values, smoother.Smoothed_Z.values

def peak_detection(ar,threshold=3,window=500):
	'''
	Method that extracts out data in a moving window that falls outside a zscore of threshold.
	ar (list floats) the data to be processed
	threshold (float) zscore exclusion value (above this value will be thrown away)
	window (int) size of moving window
	RETURNS new_ar (list floats) values from ar with bad values extracted
	'''
	new_ar = []
	for i in range(0,len(ar),window):
		try:
			z = np.abs(stats.zscore(np.abs(ar[i:i+window]-np.mean(ar[i:i+window]))))
			idz = np.array([z>threshold],dtype=bool)[0]
			replacer = np.array(copy.copy(ar[i:i+window]))
		except RuntimeWarning:
			z = np.abs(stats.zscore(np.abs(ar[i-1+window:-1]-np.mean(ar[i-1+window:-1]))))
			idz = np.array([z>threshold],dtype=bool)[0]
			replacer = np.array(copy.copy(ar[i-1+window:-1]))
		replacer[idz] = np.nan
		new_ar.extend(replacer)
	return new_ar


if __name__ == '__main__':

	# Assume that someone s inserting either a path to a sonar file that needs GPS data, or that they
	# are inputting three files that need to be fused together and processed
	args = sys.argv

	if len(args) == 2:
		# just going to process sonar data more
		son_data = pd.read_table(args[1],delimiter=',',header=None, names=['Time','Lateral','Depth','Easting','Northing','Heading'])
		#add gps fixes to the key coordinates
		son_data.loc[:,'Lat'] = son_data.apply(lambda x : utm.to_latlon(x['Easting'],x['Northing'],19,'T')[0],axis=1)
		son_data.loc[:,'Lon'] = son_data.apply(lambda x : utm.to_latlon(x['Easting'],x['Northing'],19,'T')[1],axis=1)
		son_data.to_csv('lat_lon_son.csv')
	else:
		site_sonar = args[1]
		site_pixhawk = args[2]
		site_pixeul = args[3]

		# Read in pre-processed data
		son_data = pd.read_table(site_sonar,delimiter=',')
		son_data.dropna(inplace=True) #drop invalid rows if they exist

		# Pull in the Nav data from the external IMU
		gps_data = pd.read_table(site_pixhawk,delimiter=',',header=None,names=['TimeUS','GMS','Lat','Lon'])
		eul_data = pd.read_table(site_pixeul,delimiter=',',header=None,names=['TimeUS','Roll','Pitch','Yaw'])
		
		# Fuse the GPS and IMU data and transform the timestamp to be common with the sonar
		pix_data = interp_pix(gps_data, eul_data)
		pix_data.loc[:,'Time'] = pix_data.apply(lambda x : get_seconds(x['GMS']),axis=1) #NOTE Hand tuning of the time scaling may need to be done

		# Project the pixhawk information into the same timeframe as the sonar
		# Method preserves the sonar data and interpolates the pixhawk data
		sonar_times = np.unique(son_data.Time)
		both = []
		both.append(son_data.drop_duplicates(subset='Time',keep='last').set_index('Time'))
		both.append(pix_data.drop_duplicates(subset='Time',keep='last').set_index('Time'))
		pix_projection = pd.concat(both, axis=1, keys=['son','pix'])
		pix_projection = pix_projection.interpolate()
		df_index = both[0].index
		mission = pix_projection.loc[df_index]
		mission.columns = pix_projection.columns.droplevel()

		# For processing, smooth and normalize the roll and pitch values before insertion
		box_pts=60
		box = np.ones(box_pts)/box_pts
		smooth_roll = np.convolve(mission.Roll.values-np.mean(mission.Roll.values), box, mode='same')
		smooth_pitch = np.convolve(mission.Pitch.values-np.mean(mission.Pitch.values), box, mode='same')

		mission.loc[:,'Smoothed_Roll'] = smooth_roll
		mission.loc[:,'Smoothed_Pitch'] = smooth_pitch

		# Also identify and remove anomolous readings
		replacer = peak_detection(son_data.Depth.values,window=100000)
		son_data.loc[:,'Smoothed_Depth'] = son_data.Depth.values#replacer
		son_data.interpolate(inplace=True)

		# Perform the rotation and visualize output in 2d
		x, y, z = get_rotated(mission, son_data.iloc[0:-1])
		print max(z), min(z)
		d = plt.scatter(x,y,c=z, vmin=0, vmax=25, alpha=0.8, edgecolors='none')
		plt.colorbar(d)
		plt.show()
