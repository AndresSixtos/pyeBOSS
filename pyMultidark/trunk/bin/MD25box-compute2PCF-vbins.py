from MultiDark import *

box = MultiDarkSimulation(Lbox=2500.0 * uu.Mpc, boxDir = "MD_2.5Gpc")

all=n.array([ 22, 46, 74 ])
for ii in range(len(all)):
	a= all[ii]
	ll = n.array( glob.glob( "/data2/DATA/eBOSS/Multidark-lightcones/MD_2.5Gpc/snapshots/hlist_"+str(a)+"_Nb*.fits" ) )
	box.compute2PCF(ll)


