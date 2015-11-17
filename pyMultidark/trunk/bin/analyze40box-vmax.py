from MultiDark import *
box = MultiDarkSimulation(Lbox=2500.0 * uu.Mpc,wdir="/data2/DATA/eBOSS/Multidark-lightcones", boxDir = "MD_4Gpc",snl =  n.array(glob.glob(join("/data2/DATA/eBOSS/Multidark-lightcones" , "MD_4Gpc", "snapshots", "hlist_?.?????.list"))) ,zsl = None,zArray = n.arange(0.2,2.4,1e-1),Hbox = 67.77 * uu.km / (uu.s * uu.Mpc),Melement = 96000000000.0)

print box.snl
for ii in n.arange(len(box.snl)):
	box.computeSingleDistributionFunction(ii,'vmax', n.arange(0,3.5,0.01))
	box.combinesSingleDistributionFunction(ii,'vmax', n.arange(0,3.5,0.01),type = "Central")
	box.combinesSingleDistributionFunction(ii,'vmax', n.arange(0,3.5,0.01),type = "Satellite")
