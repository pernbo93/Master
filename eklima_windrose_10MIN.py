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

#Define which filename
    filenames = glob.glob(inputdir+"/"+'met_mast_w*.txt')
    np_array_list = []
    for filename in filenames:
        print(filename)
        df = pd.read_csv(filename,sep=";",names=['station_id','date','direction','speed']) 
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])
        df = df.dropna(subset=['direction'])
        df= df.dropna(subset=['speed'])

        np_array_list.append(df.as_matrix())

    comb_np_array = np.vstack(np_array_list)
    big_frame = pd.DataFrame(comb_np_array)

    big_frame.columns = ['station_id','date','direction','speed']
    big_frame['date']= pd.to_datetime(big_frame['date'])
    big_frame['station_id']= big_frame['station_id'].astype(str)
    big_frame['direction']= big_frame['direction'].astype('float64')
    big_frame['speed']= big_frame['speed'].astype('float64')
    big_frame.index = big_frame['date']
    del big_frame['date']


# Calm conditions
    calm = 0.5

# Remove too small wind speed values!
    big_frame=big_frame.loc[(big_frame['speed'] > calm )]

    w_H = big_frame.loc[big_frame['station_id'] == '18210 (506)'] 
    w_B = big_frame.loc[big_frame['station_id'] == '18700 (506)'] 


    plt.hist([0, 1])
    plt.close()

#A quick way to create new windrose axes...
    def new_axes():
    	fig = plt.figure(figsize=(12, 10), dpi=80, facecolor='w', edgecolor='w')
    	rect = [0.1, 0.1, 0.8, 0.8]
    	ax = wr.WindroseAxes(fig, rect, axisbg='w')
    	fig.add_axes(ax)
    	return ax

    outfilename='eklima_rose_Hovin_10MIN_25.png'
    ax = new_axes()
    ax.bar(w_H['direction'], w_H['speed'], opening=0.8, edgecolor='white', bins=np.arange(0.5, 15, 2))
    plt.title('Hovin - OBS - 25m', y=1.08, fontsize=16, fontweight='bold')
    #locc = plticker.MultipleLocator(base=500.0) # this locator puts ticks at regular intervals
    #ax.xaxis.set_major_locator(locc)
    ax.set_xlim(0,2500)
    ax.set_ylim(0,2500)
    ax.yaxis.set_ticks(np.arange(0,2500,500))
    ax.yaxis.set_ticklabels(np.arange(0,2500,500))
    ax.set_legend()
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.3), title='Value [m/s]', fontsize=10)
    plt.savefig(outfilename)

    outfilename2='eklima_rose_Blindern_10MIN_26.png'
    ax2 = new_axes()
    ax2.bar(w_B['direction'], w_B['speed'], opening=0.8, edgecolor='white', bins=np.arange(0.5, 15, 2))
    plt.title('Blinder - OBS - 26.5m', y=1.08, fontsize=16, fontweight='bold')
    ax2.set_ylim(0,2500)
    ax2.set_xlim(0,2500)
    ax2.yaxis.set_ticks(np.arange(0,2500,500))
    ax2.yaxis.set_ticklabels(np.arange(0,2500,500))
    ax2.set_legend()
    ax2.legend(loc='center left', bbox_to_anchor=(1, 0.3), title='Value [m/s]', fontsize=10)
    plt.savefig(outfilename2)


    #plt.show()


if __name__ == "__main__":
    main()
