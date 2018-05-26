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
    filenames = glob.glob(inputdir+"/"+'wrf_wind_Munch.txt')
    np_wrf_array_list = []
    for filename in filenames:
        print(filename)
        df = pd.read_csv(filename,sep=",",names=['date','gridbox','height','Speed','Direction']) 
        df['date'] = pd.to_datetime(df['date'],
                                   format="%Y-%m-%d_%H:%M:%S")

        #df = df.dropna(subset=['date'])
        #dft= df.dropna(subset=['T'])
        #dft= df.dropna(subset=['height'])
        np_wrf_array_list.append(df.as_matrix())

# collect all info for temperature sensors
    comb_np_wrf_array = np.vstack(np_wrf_array_list)
    big_frame_wrf = pd.DataFrame(comb_np_wrf_array)

    big_frame_wrf.columns = ['date', 'gridbox', 'height', 'Speed','Direction']
    big_frame_wrf['date']= pd.to_datetime(big_frame_wrf['date'])
    big_frame_wrf['gridbox']= big_frame_wrf['gridbox'].astype(str)
    big_frame_wrf['height']= big_frame_wrf['height'].astype('float64')
    big_frame_wrf['Speed']= big_frame_wrf['Speed'].astype('float64')
    big_frame_wrf['Direction']= big_frame_wrf['Direction'].astype('float64')
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

# collect all info for wind sensors
    comb_npw_array = np.vstack(npw_array_list)
    big_frame_w = pd.DataFrame(comb_npw_array)

    big_frame_w.columns = ['date','station_id','T','speed','direction','u','v','var']
    big_frame_w['date']= pd.to_datetime(big_frame_w['date'])
    big_frame_w['T']= big_frame_w['T'].astype('float64')
    big_frame_w['speed']= big_frame_w['speed'].astype('float64')
    big_frame_w['direction']= big_frame_w['direction'].astype('float64')
    big_frame_w['u']= big_frame_w['u'].astype('float64')
    big_frame_w['v']= big_frame_w['v'].astype('float64')
    big_frame_w.index = big_frame_w['date']
    del big_frame_w['date']

    big_frame_w = big_frame_w.loc[(big_frame_w['speed'] < 15)]
    big_frame_w = big_frame_w.loc[big_frame_w['station_id'].str.strip() != 'c']


# ----- OBS

    station_10 = big_frame_w.loc[big_frame_w['station_id'].str.strip() == 'a']
    average_10 = station_10.resample('10Min').mean()       
    average_10 = average_10[average_10.index.minute == 0]       

    station_30 = big_frame_w.loc[big_frame_w['station_id'].str.strip() == 'a']
    average_30 = station_30.resample('10Min').mean()
    average_30 = average_30[average_30.index.minute == 0]


#--- Scatterplot
    i = 0
    j = 15
    x = np.linspace(i, j, i+j-1) #for perfect-line
    y = x

    color = 'navy'
    for label, bfw in big_frame_wrf.groupby('gridbox', sort=False):
        for height, bfww in bfw.groupby('height', sort=False):
            outfilename='Munch_wind_'+label+str(height)+'.png'
            if height == 10:
                bfwww = pd.concat([average_10['speed'], bfww['Speed']], axis=1)
                bfwww.columns = bfwww.columns.str.replace('Speed','WRF')
                bfwww.columns = bfwww.columns.str.replace('speed','Observations')
                bfwww = bfwww.dropna()
                bfwww.plot.scatter(figsize=(10,10), x='Observations', y='WRF', c=color, grid=True)
                plt.suptitle('Comparison of wind speed data at {}m - {}'.format(height,label), fontweight='bold', fontsize=20)
                plt.ylabel('WRF, (m/s)', size=16, weight='bold')
                plt.xlabel('Observations, (m/s)', size=16, weight='bold')
                plt.axes().set_aspect('equal', 'box')
                plt.yticks(fontweight="bold")
                plt.xticks(fontweight="bold") 
                plt.plot(x, y, '-', color='gray')   
            elif height == 30:
                bfwww = pd.concat([average_30['speed'], bfww['Speed']], axis=1)
                bfwww.columns = bfwww.columns.str.replace('Speed','WRF')
                bfwww.columns = bfwww.columns.str.replace('speed','Observations')
                bfwww = bfwww.dropna()
                bfwww.plot.scatter(figsize=(10,10), x='Observations', y='WRF', c=color, grid=True)
                plt.suptitle('Comparison of wind speed data at {}m - {}'.format(height,label), fontweight='bold', fontsize=20)
                plt.ylabel('WRF, (m/s)', size=16, weight='bold')
                plt.xlabel('Observations, (m/s)', size=16, weight='bold')
                plt.axes().set_aspect('equal', 'box')
                plt.yticks(fontweight="bold")
                plt.xticks(fontweight="bold") 
                plt.plot(x, y, '-', color='gray')
            plt.savefig(outfilename)   
     
#    plt.show()



if __name__ == "__main__":
    main()
