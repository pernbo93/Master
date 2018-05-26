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
import matplotlib.dates as md
#import datetime

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

#Define which filename
    filenames = sorted(glob.glob(inputdir+"/"+'18*.TXT'))
    npt_array_list = []
    npw_array_list = []
    for filename in filenames:
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
        dfw['u'] = [x.lstrip('-') for x in dfw['u']]
        dfw['v'] = [x.lstrip('-') for x in dfw['v']]
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
# Remove too big or too small values!
#Should do some quality check
#AF Is it still valid? it was pretty cold in 2018...
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


# Take away measurements from station at 75m -'c'
    big_frame_w = big_frame_w[big_frame_w['station_id'].str.strip() != 'c']

# Remove too big wind speed values!
    big_frame_w=big_frame_w.loc[(big_frame_w['speed'] <15)]

# Loc periode
    big_frame_w = big_frame_w.loc[(big_frame_w.index >= '2018-01-09 01:00:00') & (big_frame_w.index <= '2018-01-18 23:00:00')]

# Calculate pressure
    p0 = 101300
    H = 8000.
    R = 287.
    cp = 1004.
    p_10 = p0*np.exp(-10./H)
    p_30 = p0*np.exp(-30./H)

    def theta_C6(x):
        return x - ((x)*(p0/p_10)**R/cp)
    def theta_99(x):
        return x - ((x)*(p0/p_30)**R/cp)

    u_10 = big_frame_w.loc[(big_frame_w['station_id'].str.strip() == 'a')]
    u_10.rename(columns={'u': 'u_10'}, inplace=True)
    u_10 = u_10['u_10'].resample('60Min').mean()

    u_30 = big_frame_w.loc[(big_frame_w['station_id'].str.strip() == 'b')]
    u_30.rename(columns={'u': 'u_30'}, inplace=True)
    u_30 = u_30['u_30'].resample('60Min').mean()

    v_10 = big_frame_w.loc[(big_frame_w['station_id'].str.strip() == 'a')]
    v_10.rename(columns={'v': 'v_10'}, inplace=True)
    v_10 = v_10['v_10'].resample('60Min').mean()

    v_30 = big_frame_w.loc[(big_frame_w['station_id'].str.strip() == 'b')]
    v_30.rename(columns={'v': 'v_30'}, inplace=True)
    v_30 = v_30['v_30'].resample('60Min').mean()

    def kelvin(x):
        return x + 273.15


# Loc speed
    speed_10 = big_frame_w.loc[(big_frame_w['station_id'].str.strip() == 'a')]
    speed_10.rename(columns={'speed': 'speed_10'}, inplace=True)
    speed_10 = speed_10['speed_10'].resample('60Min').mean()

    speed_30 = big_frame_w.loc[(big_frame_w['station_id'].str.strip() == 'b')]
    speed_30.rename(columns={'speed': 'speed_30'}, inplace=True)
    speed_30 = speed_30['speed_30'].resample('60Min').mean()

# Loc pot.temp
    temp_10 = big_frame_t.loc[(big_frame_t['station_id'] == 'C6 7D 0D 09 00 00')]
    temp_10.rename(columns={'T': 'Theta_10'}, inplace=True)
    temp_10 = temp_10['Theta_10'].apply(kelvin)
    temp_10 = temp_10.resample('60Min').mean()
    theta_10 = (temp_10*((p0/p_10)**(R/cp)))

    temp_30 = big_frame_t.loc[(big_frame_t['station_id'] == '99 7B 0D 09 00 00')]
    temp_30.rename(columns={'T': 'Theta_30'}, inplace=True)
    temp_30 = temp_30['Theta_30'].apply(kelvin)
    temp_30 = temp_30.resample('60Min').mean()
    theta_30 = (temp_30*((p0/p_30)**(R/cp)))

# Merge all variables into one data frame
    variables = pd.concat([speed_10, speed_30, theta_10, theta_30], axis=1, join_axes=[speed_10.index])
    #print(variables)

    variables2 = pd.concat([u_10, u_30, v_10, v_30, theta_10, theta_30], axis=1, join_axes=[speed_10.index])
    #print(variables2)

    #size = vari["desired column"].apply(lambda x: len(x))
    #import sys
    #sys.exit()

#    fig, ax = plt.subplots(2,1)

    fig, ax = plt.subplots(1,1)
#    variables['2018']['Theta_10'].plot(ax=ax[0], grid='on')
#    variables['2018']['Theta_30'].plot(ax=ax[0], grid='on')
    ax.plot(variables2.index.values.astype('d'), variables['Theta_10'].values, label='Theta@10')
    ax.plot(variables2.index.values.astype('d'), variables['Theta_30'].values, label='Theta@30')
#    idx = md.date2num(variables2.index.to_pydatetime())
    size = len(variables2['u_10'].values)
#    ax[1].xaxis.set_major_formatter(md.DateFormatter('%H:%M'))
    ax.barbs(variables2.index.values.astype('d'), np.ones(size) * 265, variables2['u_10'].values, variables2['v_10'].values, label='wind')

    ax.set_xticklabels(variables2.index.strftime("%m-%d"))
    ax.set_ylim(262,280)
    ax.grid()
    ax.legend(loc='best')
    #ax[1].set_xlim(left=0)
    #ax[1].set_xticklabels([])
    #ax[1].set_yticklabels([])

    #plt.grid()
#    ax[0].legend(loc='best')


# Calculate Ri for each row
    g = 9.81
    z2 = 30.
    z1 = 10.

    Ri1 =[]
    Ri2 =[]
    time = []
    for index, row in variables.iterrows():
        time.append(index)
        #print('--------')
        #print('Time:{}'.format(index))
        B = (g*(row['Theta_30']-row['Theta_10'])*(z2-z1))
        #print('B:{}'.format(B))
        M = (row['Theta_10']*((row['speed_30']-row['speed_10'])**2))
        #print('M:{}'.format(M))
        Ri = B/M
        #print('Ri:{}'.format(Ri))
        Ri1.append(Ri)

    for index, row in variables2.iterrows():
        #print('--------')
        #print('Time:{}'.format(index))
        B = (g*(row['Theta_30']-row['Theta_10'])*(z2-z1))
        #print('B:{}'.format(B))
        M = (row['Theta_10']*(((row['u_30']-row['u_10'])**2)+((row['v_30']-row['v_10'])**2)))
        #print('M:{}'.format(M))
        Ri = B/M
        #print('Ri:{}'.format(Ri))
        Ri2.append(Ri)

    #print(Ri1)
    #print(Ri2)

    #for i in Ri2:
    #    if i < 0.25:
    #        c = 'red'
    #    else
    #       c =

    plt.figure()
    #plt.plot(time, Ri1, label ='Ri_speed')
    plt.plot(time, Ri2, label ='Ri')
    plt.title('Calculated Richardson number at the Munch Mast')
    plt.grid(axis = 'y')
    plt.legend(loc='best')

    plt.show()


if __name__ == "__main__":
    main()
