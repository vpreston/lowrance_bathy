# lowrance_bathy
A repo exploring how feasible it is to resolve raw data from structure scans taken with a Lowrance fishfinder and pixhawk-mounted IMU/GPS unit. 

Lowrance is a manufacturer of fishfinders which can be used to depth sound in a variety of marine environments. The scripts in this repository look at the raw data from the Lowrance HDS7 structure scan unit. This repository assumes that data from the Lowrance system (sl3 files) have already been converted into constituent navigation and sounding csv osv, txt, or xyz files for parsing.

Pixhawks are hobby autopilots popular for drone technology. Integrated with fairly sophisticated IMU and GPS units, a pixhawk is used as an example IMU insertion type to correct for information not encoded in the Lowrance data. Ostensibly, any IMU device can be used, assuming that is has been pre-parsed into a .csv file for injecting with the code in this repository.

The workflow for processing the data is to:
* __Parse:__ Parse the constutent IMU and Sonar files with Python to create a combined data base
* __Correct:__ Apply smoothing, navigation correction, outlier removal, etc from the data base onto the sounding data to generate a clean dataset with Python
* __Analyze:__ Visualize or analyze the data as desired. MatLab is used in this repository, but similar visualizations or analyses could be done in another language

In each folder in this directory, the files for each step of the workflow can be found. 

## Parse
The script `parse_nav.py` can be run on the command line as follows:

```python parse_nav.py path_to_sounding_data path_to_lowrance_nav_data path_to_xyz_data```

Please note that depending on the size of your files, this can take some time. A cleaned csv of the data from the sounding and nav files will be generated and saved in the location from which you ran this command. You can open the script and change the name or hardcode the location of where to save the data. The XYZ data will be parsed and plotted. 

## Correct
The script `fuse_nav.py` can be fun on the command line in one two ways:

```python fuse_nav.py path_to_soundnav_data```
```python fuse_nav.py path_to_soundnav_data path_to_pixgps_data path_to_piximu_data```

The first method will create a new CSV file of afile with the lowrance sounding and nav data (the output of `process_nav.py` for instance) of the same data with Latitude and Longitude coordinates appended for the data (useful for comparing to PixHawk nav data).

The second method will take the lowrance sounding and nav data, the pixhawk gps log, and the pixhawk imu data and fuse them into an interpolated dataset (sounding data is preserved, and the pixhawk data is projected onto the time axes of that data). It then performs smoothing and rotation operations and saves an output csv of the projected xyz data and the smoothed xyz data. The output can then be used to perform various analyzes on the data.

For the correction there are a number of parameters and options. It is encouraged that the user open the code and gain some familiarity with it to best tweak the smoothing, filtering, interpolation, and rotations for their data.

## Analyze
The data for the project originating this repo was processed using MatLab. Similar analyses could be performed using python or other language of choice. 

The script `linear_smooth_model.m` and `loess_smooth_model.m` provide two different ways of reading in the data from the output of the correction script described above to make a linear-iterpolation model or a local quadratic regression model of the observations.

The script `compare_model_groundtruth.m` will read in a ground truth model csv you provide of the region of interest, and will project the spatial points into the model generated from the observations fro the Lowrance system. It will then provide several visualizations and indications of the quality of the ft between the projected points and the groundtruth points.

## Utilities
Miscellaneous helper code (parsing .mat structures of the pixhawk for example) are provided in this file.
