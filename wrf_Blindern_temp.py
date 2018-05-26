#!/usr/bin/env python
#
# (C) Copyright 2014 UIO.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0. 
# 
# 
# Creation: July 2017 - Anne Fouilloux - University of Oslo
#
# Usage:
#
#./test_read.py --inputdir=$PWD

import os
from optparse import OptionParser
import os.path
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def mkdir_p(file):
    if file != "" and file != ".":
        path = os.path.dirname(file)
        try:
            os.stat(path)
        except:
            os.makedirs(path)

def main():
    usage = """usage: %prog  --inputdir=input_directory [--outputdir=output_directory]  """

    parser = OptionParser(usage=usage)
    parser.add_option("-s", "--inputdir", dest="inputdir",
                      help="root directory for reading input files", metavar="inputdir" )

    parser.add_option("--outputdir", dest="outputdir",
                      help="root directory for storing output files", metavar="outputdir")

    (options, args) = parser.parse_args()

    if not options.inputdir:
        parser.error("Input directory where files to read are located must be specified!")
    else:
        inputdir=options.inputdir


    if not options.outputdir:
# if WORKDIR is defined, we will use it otherwise files 
# will be stored in the current directory
        outputdir=os.environ.get("WORKDIR",".")
    else:
        outputdir=options.outputdir

#--- READ WRF DATA
    filenames = glob.glob(inputdir+"/"+'wrf_temp_Blindern.txt')
    np_wrf_array_list = []
    for filename in filenames:
        print(filename)
        df = pd.read_csv(filename,sep=",",names=['date','gridbox','height','temp']) 
        df['date'] = pd.to_datetime(df['date'],
                                   format="%Y-%m-%d_%H:%M:%S")

        #df = df.dropna(subset=['date'])
        #dft= df.dropna(subset=['T'])
        #dft= df.dropna(subset=['height'])
        np_wrf_array_list.append(df.as_matrix())

# collect all info for temperature sensors
    comb_np_wrf_array = np.vstack(np_wrf_array_list)
    big_frame_wrf = pd.DataFrame(comb_np_wrf_array)

    big_frame_wrf.columns = ['date', 'gridbox', 'height', 'temp']
    big_frame_wrf['date']= pd.to_datetime(big_frame_wrf['date'])
    big_frame_wrf['gridbox']= big_frame_wrf['gridbox'].astype(str)
    big_frame_wrf['height']= big_frame_wrf['height'].astype('float64')
    big_frame_wrf['temp']= big_frame_wrf['temp'].astype('float64')
    big_frame_wrf.index = big_frame_wrf['date']
    del big_frame_wrf['date']

#--- READ EKLIMA DATA
    filenames = glob.glob(inputdir+"/"+'met_mast.txt')
    np_array_list = []
    for filename in filenames:
        print(filename)
        df = pd.read_csv(filename,sep=";",names=['station_id','date','direction','speed','T_2m','T_10m']) 
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])
        df = df.dropna(subset=['direction'])
        df= df.dropna(subset=['speed'])
        df= df.dropna(subset=['T_2m'])
        df= df.dropna(subset=['T_10m'])

        np_array_list.append(df.as_matrix())

    comb_np_array = np.vstack(np_array_list)
    big_frame = pd.DataFrame(comb_np_array)

    big_frame.columns = ['station_id','date','direction','speed','T_2m','T_10m']
    big_frame['date']= pd.to_datetime(big_frame['date'])
    big_frame['direction']= big_frame['direction'].astype('float64')
    big_frame['speed']= big_frame['speed'].astype('float64')
    big_frame['T_2m']= big_frame['T_2m'].astype('float64')
    big_frame['T_10m']= big_frame['T_10m'].astype('float64')
    big_frame.index = big_frame['date']
    del big_frame['date']

#### !!!!! REMEMBER TO REMOVE!!! JUST FOR TESTING#############################
    big_frame = big_frame.loc[(big_frame.index >= '2018-01-30 17:00:00') & (big_frame.index <= '2018-01-30 18:00:00')]
#############################################################################

# ----- OBS
    
    station_2 = big_frame.loc[big_frame['station_id'] == 18700] 
    station_2 = station_2['T_2m'] 
 
    station_10 = big_frame.loc[big_frame['station_id'] == 18700]
    station_10 = station_10['T_10m']    


#--- Scatterplot
    i=-15
    j=10
    x = np.linspace(i, j, -i+j-1.) #for perfect-line
    y = x

    color = 'indigo'
    for label, bfw in big_frame_wrf.groupby('gridbox', sort=False):
        for height, bfww in bfw.groupby('height', sort=False):
            outfilename='Blindern_temp_'+label+str(height)+'.png'
            if height == 2:
                bfwww = pd.concat([station_2, bfww['temp']], axis=1)
                bfwww.columns = bfwww.columns.str.replace('temp','WRF')
                bfwww.columns = bfwww.columns.str.replace('T_2m','Observations')
                bfwww = bfwww.dropna()
                bfwww.plot.scatter(figsize=(10,10), x='Observations', y='WRF', c=color, grid=True)
                plt.suptitle('Comparison of temperature data at {}m - {}'.format(height,label), fontweight='bold', fontsize=20)
                plt.ylabel('WRF, ($\degree$C)', size=16, weight='bold')
                plt.xlabel('Observations, ($\degree$C)', size=16, weight='bold')
                plt.axes().set_aspect('equal', 'box')
                plt.yticks(fontweight="bold")
                plt.xticks(fontweight="bold") 
                plt.plot(x, y, '-', color='gray')   
            elif height == 10:
                bfwww = pd.concat([station_10, bfww['temp']], axis=1)
                bfwww.columns = bfwww.columns.str.replace('temp','WRF')
                bfwww.columns = bfwww.columns.str.replace('T_10m','Observations')
                bfwww = bfwww.dropna()
                bfwww.plot.scatter(figsize=(10,10), x='Observations', y='WRF', c=color, grid=True)
                plt.suptitle('Comparison of temperature data at {}m - {}'.format(height,label), fontweight='bold', fontsize=20)
                plt.ylabel('WRF, ($\degree$C)', size=16, weight='bold')
                plt.xlabel('Observations, ($\degree$C)', size=16, weight='bold')
                plt.axes().set_aspect('equal', 'box')
                plt.yticks(fontweight="bold")
                plt.xticks(fontweight="bold") 
                plt.plot(x, y, '-', color='gray')
            plt.savefig(outfilename)   

  
   # plt.show()



if __name__ == "__main__":
    main()
