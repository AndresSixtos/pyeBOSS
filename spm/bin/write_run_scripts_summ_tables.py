import os
from os.path import join
import numpy as n
def writeScript(rootName, plate):
	f=open(rootName+".sh",'w')
	f.write("#!/bin/bash \n")
	f.write("#PBS -l walltime=2:00:00 \n")
	f.write("#PBS -o "+plate+".o.$PBS_JOBID \n")
	f.write("#PBS -e "+plate+".e$PBS_JOBID \n")
	f.write("#PBS -M johan.comparat@gmail.com \n")
	f.write("module load apps/anaconda/2.4.1 \n")
	f.write("module load apps/python/2.7.8/gcc-4.4.7 \n")
	f.write("export PYTHONPATH=$PYTHONPATH:/users/comparat/pySU/galaxy/python/ \\n")
	f.write("export PYTHONPATH=$PYTHONPATH:/users/comparat/pySU/spm/python/ \n")
	f.write(" \n")
	f.write("cd /users/comparat/pySU/spm/bin \n")
	f.write("python create_summary_tables.py "+plate+" \n")
	f.write(" \n")
	f.close()

plates_all = n.loadtxt( join(os.environ['SDSSDR12_DIR'], "plateNumberList"), unpack=True, dtype='str')
plates = plates_all[:-2]
for plate in plates:
	rootName = join(os.environ['HOME'], "batchscripts_firefly_tables", plate)
	writeScript(rootName, plate)