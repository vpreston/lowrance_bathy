# lowrance_bathy
A repo exploring how feasible it is to resolve raw data from structure scans taken with a Lowrance fishfinder and pixhawk-mounted IMU/GPS unit. 

Lowrance is a manufacturer of fishfinders which can be used to depth sound in a variety of marine environments. The scripts in this repository look at the raw data from the Lowrance HDS7 structure scan unit. This repository assumes that data from the Lowrance system (sl3 files) have already been converted into constituent navigation and sounding csv osv, txt, or xyz files for parsing.

Pixhawks are hobby autopilots popular for drone technology. Integrated with fairly sophisticated IMU and GPS units, a pixhawk is used as an example IMU insertion type to correct for information not encoded in the Lowrance data. Ostensibly, any IMU device can be used, assuming that is has been pre-parsed into a .csv file for injecting with the code in this repository.

The workflow for processing the data is to:
* __Parse:__ Parse the constutent IMU and Sonar files with Python to create a combined data base
* __Correct:__ Apply smoothing, navigation correction, outlier removal, etc from the data base onto the sounding data to generate a clean dataset with Python
* __Analyze:__ Visualize or analyze the data as desired. MatLab is used in this repository, but similar visualizations or analyses could be done in another language

In each folder in this directory, the files for each step of the workflow can be found.
