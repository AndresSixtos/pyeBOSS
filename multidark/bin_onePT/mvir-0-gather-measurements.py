import glob
from os.path import join
import numpy as n
import astropy.io.fits as fits
import lib_functions_1pt as lib
import os
import sys

#Quantity studied
qty = "mvir"

# redshift lists
dir_boxes =  n.array([os.environ['MD04_DIR'], os.environ['MD10_DIR'], os.environ['MD25_DIR'], os.environ['MD40_DIR'], os.environ['MD25NW_DIR'], os.environ['MD40NW_DIR']])
zList_files = n.array([ join(dir_box,"redshift-list.txt") for dir_box in dir_boxes])

# one point function lists
fileC = n.array(glob.glob( join(os.environ['MULTIDARK_LIGHTCONE_DIR'],"MD_*Gpc*", "properties", qty,"*t_*_Central_JKresampling.pkl")))
fileB = n.array(glob.glob( join( os.environ['MULTIDARK_LIGHTCONE_DIR'],"MD_*Gpc*","properties", qty,"*t_*_"+qty+"_JKresampling.bins")))
fileS = n.array(glob.glob( join( os.environ['MULTIDARK_LIGHTCONE_DIR'],"MD_*Gpc*","properties", qty,"*t_*_Satellite_JKresampling.pkl")))
"""
fileC = n.array(glob.glob( join(os.environ['MULTIDARK_LIGHTCONE_DIR'],"MD_4GpcNW", "properties", qty,"*t_*_Central_JKresampling.pkl")))
fileB = n.array(glob.glob( join( os.environ['MULTIDARK_LIGHTCONE_DIR'],"MD_4GpcNW","properties", qty,"*t_*_"+qty+"_JKresampling.bins")))
fileS = n.array(glob.glob( join( os.environ['MULTIDARK_LIGHTCONE_DIR'],"MD_4GpcNW","properties", qty,"*t_*_Satellite_JKresampling.pkl")))
"""
fileC.sort()
fileS.sort()
fileB.sort()
print len(fileC), len(fileB), len(fileS)


print "considers ",len(fileC), qty , " function files"

for ii, el in enumerate(fileC):
	print el
	print fileS[ii]
	print fileB[ii]
	lib.convert_pkl_mass(fileC[ii], fileS[ii], fileB[ii], qty)

sys.exit()
# rebinning here
#solve bins = 0 problem

n.arange()
n.hstack((n.arange(8,14,0.25), n.arange(14,16,0.05)))

#if logmvir < 14 :
Nrb = 5.
idSplit = int(n.searchsorted(d0['log_mvir'],14)/Nrb)*Nrb
split_array= lambda array: [array[:idSplit], array[idSplit:]]

#variables :
# 
def rebinMe(trb, mod, Nrb = 5):
	# split
	part1, part2 = split_array(trb)
	# rebin
	take_middle_val = lambda part: part[2::Nrb]
	take_mean_val = lambda part: (part[0::Nrb] + part[1::Nrb] + part[2::Nrb] + part[3::Nrb] + part[4::Nrb])/Nrb.
	take_sum_val = lambda part: part[0::Nrb] + part[1::Nrb] + part[2::3] + part[3::Nrb] + part[4::Nrb]
	if mode == 'middle' :
		part1b = take_middle_val(part1)
	if mode == 'mean' :
		part1b = take_mean_val(part1)
	if mode == 'sum' :
		part1b = take_sum_val(part1)
	return n.hstack((part1b, part2))

trb = d0['log_mvir']
mode = 'middle'
trb_o = rebinMe(trb, mode)

col6c = do["dN_counts_cen"] 
col6cc = do["dN_counts_cen_c"]
col7c = do["dNdV_cen"] 
col7cc = do["dNdV_cen_c"]
col8c = do["dNdlnM_cen"] 
col8cc = do["dNdlnM_cen_c"]
col9c = do["std90_pc_cen"] 
col9cc = do["std90_pc_cen_c"]

print qty
af = n.array(glob.glob(join(os.environ['MULTIDARK_LIGHTCONE_DIR'], qty, "data", "MD_*_"+qty+".fits") ) )
print af[0]
d0 = fits.open(af[0])[1].data
print len(d0['log_mvir']), d0['log_mvir']

import sys
sys.exit()

for ii in range(1,len(af),1):
	d1 = fits.open(af[ii])[1].data
	d0 = n.hstack((d0,d1))

hdu2 = fits.BinTableHDU.from_columns(d0)

writeName = join(os.environ['MULTIDARK_LIGHTCONE_DIR'], qty, "MD_"+qty+"_summary.fits")
if os.path.isfile(writeName):
	os.remove(writeName)
	
hdu2.writeto( writeName )



