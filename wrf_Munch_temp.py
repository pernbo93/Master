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
    filenames = glob.glob(inputdir+"/"+'wrf_temp_Munch.txt')
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
#    print(big_frame_wrf)

#--- READ OBS DATA
    filenames2 = sorted(glob.glob(inputdir+"/"+'18*.TXT'))
    npt_array_list = []
    npw_array_list = []
    for filename in filenames2:
        print(filename)
        df = pd.read_csv(filename,sep=",", names=['date','station_id','T']) 
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])
        dfw=df[df['T'].isnull()]
        dfw['station_id']=dfw['station_id'].str.replace('-','+-').str.split('+')
        dfw['speed'] = dfw['station_id'].apply(lambda x:x[1])
        dfw['direction'] = dfw['station_id'].apply(lambda x:x[2])
        dfw['T'] = dfw['station_id'].apply(lambda x:x[3])
        dfw['u'] = dfw['station_id'].apply(lambda x:x[4])
        dfw['v'] = dfw['station_id'].apply(lambda x:x[5])
        dfw['var'] = dfw['station_id'].apply(lambda x:x[6])
        dfw['station_id'] = dfw['station_id'].apply(lambda x:x[0])
        dft= df.dropna(subset=['T'])
        dft['T'] = [x.lstrip(' T:') for x in dft['T']]
        dft['station_id'] = [x.lstrip(' ') for x in dft['station_id']]
        npt_array_list.append(dft.as_matrix())
        npw_array_list.append(dfw.as_matrix())

# collect all info for temperature sensors
    comb_npt_array = np.vstack(npt_array_list)
    big_frame_t = pd.DataFrame(comb_npt_array)

    big_frame_t.columns = ['date','station_id','T']
    big_frame_t['date']= pd.to_datetime(big_frame_t['date'])
    big_frame_t['T']= big_frame_t['T'].astype('float64')
    big_frame_t.index = big_frame_t['date']
    del big_frame_t['date']
    big_frame_t=big_frame_t.loc[(big_frame_t['T'] >-17) & (big_frame_t['T'] <40)]

#--- Calibrating Measurements 
# Function to define correction 
    def func_12(x):
        return x

    def func_C6(x):
        return x - (-6E-06*x + 0.0623)

    def func_99(x):
        return x - (-0.0072*x + 0.1849)

    def func_DB(x):
        return x - (0.0074*x - 0.2795)

    def func_27(x):
        return x - (0.0037*x - 0.0429)

    def func_BF(x):
        return x - (0.0005*x + 0.0609)

# Plotting corrected temp, wind speed and wind dir ############################
# Color/Station 
    stations = {'12 BE 0D 09 00 00':'2m',
                'C6 7D 0D 09 00 00':'10m',
                '99 7B 0D 09 00 00':'30m',
                'DB 6E 0D 09 00 00':'50m',
                '27 B0 0D 09 00 00':'65m',
                'BF 8E 0D 09 00 00':'75m'
                }

    colors_temp = {'12 BE 0D 09 00 00':'blue',
                   'C6 7D 0D 09 00 00':'green',
                   '99 7B 0D 09 00 00':'cyan',
                   'DB 6E 0D 09 00 00':'orange',
                   '27 B0 0D 09 00 00':'magenta',
                   'BF 8E 0D 09 00 00':'red'
                   }


    colors_wrf = {'20':'green',
                   '30':'cyan',
                   '50':'orange',
                   '65':'magenta',
                   '75':'red'
                   }

# ----- OBS
    
    station_2 = big_frame_t.loc[big_frame_t['station_id'] == '12 BE 0D 09 00 00'] #get obs at height
    average_2 = station_2['T'].resample('10Min').mean()       #take 10min mean of obs
    average_2 = average_2[average_2.index.minute == 0]       #get only first 10min mean of every hour

    station_10 = big_frame_t.loc[big_frame_t['station_id'] == 'C6 7D 0D 09 00 00']
    station_10['T'] = station_10['T'].apply(func_C6)    
    average_10 = station_10['T'].resample('10Min').mean()       
    average_10 = average_10[average_10.index.minute == 0]       

    station_30 = big_frame_t.loc[big_frame_t['station_id'] == '99 7B 0D 09 00 00']
    station_30['T'] = station_30['T'].apply(func_99)
    average_30 = station_30['T'].resample('10Min').mean()
    average_30 = average_30[average_30.index.minute == 0]

    station_50 = big_frame_t.loc[big_frame_t['station_id'] == 'DB 6E 0D 09 00 00']
    station_50['T'] = station_50['T'].apply(func_DB)
    average_50 = station_50['T'].resample('10Min').mean()
    average_50 = average_50[average_50.index.minute == 0]

    station_65 = big_frame_t.loc[big_frame_t['station_id'] == '27 B0 0D 09 00 00']
    station_65['T'] = station_65['T'].apply(func_27)
    average_65 = station_65['T'].resample('10Min').mean()
    average_65 = average_65[average_65.index.minute == 0]

    station_75 = big_frame_t.loc[big_frame_t['station_id'] == 'BF 8E 0D 09 00 00']
    station_75['T'] = station_75['T'].apply(func_BF)
    average_75 = station_75['T'].resample('10Min').mean()
    average_75 = average_75[average_75.index.minute == 0]


#--- Scatterplot
    x = np.linspace(-15, 10) #for perfect-line
    y = x

    color = 'navy'
    for label, bfw in big_frame_wrf.groupby('gridbox', sort=False):
    #if label == 'munch':
        for height, bfww in bfw.groupby('height', sort=False):
            outfilename='Munch_temp_'+label+str(height)+'.png'
            if height == 2:
                bfwww = pd.concat([average_2, bfww['temp']], axis=1)
                bfwww.columns = bfwww.columns.str.replace('temp','WRF')
                bfwww.columns = bfwww.columns.str.replace('T','Observations')
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
                bfwww = pd.concat([average_10, bfww['temp']], axis=1)
                bfwww.columns = bfwww.columns.str.replace('temp','WRF')
                bfwww.columns = bfwww.columns.str.replace('T','Observations')
                bfwww = bfwww.dropna()
                bfwww.plot.scatter(figsize=(10,10), x='Observations', y='WRF', c=color, grid=True)
                plt.suptitle('Comparison of temperature data at {}m - {}'.format(height,label), fontweight='bold', fontsize=20)
                plt.ylabel('WRF, ($\degree$C)', size=16, weight='bold')
                plt.xlabel('Observations, ($\degree$C)', size=16, weight='bold')
                plt.axes().set_aspect('equal', 'box')
                plt.yticks(fontweight="bold")
                plt.xticks(fontweight="bold") 
                plt.plot(x, y, '-', color='gray')   
            elif height == 30:
                bfwww = pd.concat([average_30, bfww['temp']], axis=1)
                bfwww.columns = bfwww.columns.str.replace('temp','WRF')
                bfwww.columns = bfwww.columns.str.replace('T','Observations')
                bfwww = bfwww.dropna()
                bfwww.plot.scatter(figsize=(10,10), x='Observations', y='WRF', c=color, grid=True)
                plt.suptitle('Comparison of temperature data at {}m - {}'.format(height,label), fontweight='bold', fontsize=20)
                plt.ylabel('WRF, ($\degree$C)', size=16, weight='bold')
                plt.xlabel('Observations, ($\degree$C)', size=16, weight='bold')
                plt.axes().set_aspect('equal', 'box')
                plt.yticks(fontweight="bold")
                plt.xticks(fontweight="bold") 
                plt.plot(x, y, '-', color='gray')   
            elif height == 50:
                bfwww = pd.concat([average_50, bfww['temp']], axis=1)
                bfwww.columns = bfwww.columns.str.replace('temp','WRF')
                bfwww.columns = bfwww.columns.str.replace('T','Observations')
                bfwww = bfwww.dropna()
                bfwww.plot.scatter(figsize=(10,10), x='Observations', y='WRF', c=color, grid=True)
                plt.suptitle('Comparison of temperature data at {}m - {}'.format(height,label), fontweight='bold', fontsize=20)
                plt.ylabel('WRF, ($\degree$C)', size=16, weight='bold')
                plt.xlabel('Observations, ($\degree$C)', size=16, weight='bold')
                plt.axes().set_aspect('equal', 'box')
                plt.yticks(fontweight="bold")
                plt.xticks(fontweight="bold") 
                plt.plot(x, y, '-', color='gray')   
            elif height == 65:
                bfwww = pd.concat([average_65, bfww['temp']], axis=1)
                bfwww.columns = bfwww.columns.str.replace('temp','WRF')
                bfwww.columns = bfwww.columns.str.replace('T','Observations')
                bfwww = bfwww.dropna()
                bfwww.plot.scatter(figsize=(10,10), x='Observations', y='WRF', c=color, grid=True)
                plt.suptitle('Comparison of temperature data at {}m - {}'.format(height,label), fontweight='bold', fontsize=20)
                plt.ylabel('WRF, ($\degree$C)', size=16, weight='bold')
                plt.xlabel('Observations, ($\degree$C)', size=16, weight='bold')
                plt.axes().set_aspect('equal', 'box')
                plt.yticks(fontweight="bold")
                plt.xticks(fontweight="bold") 
                plt.plot(x, y, '-', color='gray')
            elif height == 75:
                bfwww = pd.concat([average_75, bfww['temp']], axis=1)
                bfwww.columns = bfwww.columns.str.replace('temp','WRF')
                bfwww.columns = bfwww.columns.str.replace('T','Observations')
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
#    plt.show()



if __name__ == "__main__":
    main()
