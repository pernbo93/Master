#!bin/bash

# to run the script in background:
# chmod u+x main_script.bash
# nohup ./main_script.bash > log_mainplots.txt &

export PATH=/projects/NS1000K/pernbo/ncl:/projects/NS1000K/pernbo/python:$PATH

module use --append /projects/NS1000K/modulefiles
module load python/anaconda3


mkdir -p /projects/NS1000K/pernbo/scripts/Mainplots

cd /projects/NS1000K/pernbo/scripts/Mainplots

wrf_to_file_Munch.ncl
wrf_to_file_Hovin.ncl
wrf_to_file_Blindern.ncl

wrf_Munch_temp.py --inputdir=/projects/NS1000K/pernbo/ncl
wrf_Hovin_temp.py --inputdir=/projects/NS1000K/pernbo/ncl
wrf_Blinder_temp.py --inputdir=/projects/NS1000K/pernbo/ncl

wrf_Munch_wind.py --inputdir=/projects/NS1000K/pernbo/ncl
wrf_Hovin_wind.py --inputdir=/projects/NS1000K/pernbo/ncl
wrf_Blinder_wind.py --inputdir=/projects/NS1000K/pernbo/ncl

wrf_Munch_rose.py --inputdir=/projects/NS1000K/pernbo/ncl
wrf_Hovin_rose.py --inputdir=/projects/NS1000K/pernbo/ncl
wrf_Blinder_rose.py --inputdir=/projects/NS1000K/pernbo/ncl

obs_windrose.py  --inputdir=/projects/NS1000K/pernbo/ALL_OBSERVATIONS/clean
eklima_windrose.py  --inputdir=/projects/NS1000K/pernbo/ncl

obs_windrose_10MIN.py  --inputdir=/projects/NS1000K/pernbo/ALL_OBSERVATIONS/clean
eklima_windrose_10MIN.py  --inputdir=/projects/NS1000K/pernbo/ncl


