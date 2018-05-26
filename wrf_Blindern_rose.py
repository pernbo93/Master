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

import windrose as wr
import matplotlib.ticker as plticker

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
    filenames = glob.glob(inputdir+"/"+'wrf_wind_Blindern.txt')
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

# Calm conditions
    calm = 0.5

# Remove too small wind speed values!
    big_frame_wrf=big_frame_wrf.loc[(big_frame_wrf['Speed'] > calm )]


    plt.hist([0, 1])
    plt.close()

#A quick way to create new windrose axes...
    def new_axes():
    	fig = plt.figure(figsize=(12, 10), dpi=80, facecolor='w', edgecolor='w')
    	rect = [0.1, 0.1, 0.8, 0.8]
    	ax = wr.WindroseAxes(fig, rect, axisbg='w')
    	fig.add_axes(ax)
    	return ax

    for label, bfw in big_frame_wrf.groupby('gridbox', sort=False):
        for height, bfww in bfw.groupby('height', sort=False):
            outfilename='Blindern_rose_'+label+str(height)+'.png'
            if height == 26.5:
                ax = new_axes()
                ax.bar(bfww['Direction'], bfww['Speed'], opening=0.8, edgecolor='white', bins=np.arange(0.5, 15, 2))
                plt.title('Blindern - WRF - {}m - {}'.format(height,label), y=1.08, fontsize=16, fontweight='bold')
                ax.set_xlim(0,450)
                ax.set_ylim(0,450)
                ax.yaxis.set_ticks(np.arange(0,450,50))
                ax.yaxis.set_ticklabels(np.arange(0,450,50))
                ax.set_legend()
                ax.legend(loc='center left', bbox_to_anchor=(1, 0.3), title='Value [m/s]', fontsize=10) 
            plt.savefig(outfilename)   


    #plt.show()


if __name__ == "__main__":
    main()
