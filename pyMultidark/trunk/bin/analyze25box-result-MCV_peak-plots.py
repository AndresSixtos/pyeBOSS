import numpy as n
import matplotlib.pyplot as p
import glob
import sys

Pdir = "/Volumes/data/BigMD/2.5Gpc/plots/"
dir = "/Volumes/data/BigMD/2.5Gpc/"

ARbins = n.loadtxt('/Volumes/data/BigMD/2.5Gpc/AccRate.bins')
Vbins = n.loadtxt('/Volumes/data/BigMD/2.5Gpc/Vpeak.bins')
Mbins = n.loadtxt('/Volumes/data/BigMD/2.5Gpc/Mpeak.bins')


centralList = n.array(glob.glob(dir+"hist2d-central-Mpeak-Accrate-?.?????.dat"))
centralList.sort()
print centralList

X,Y= n.meshgrid(ARbins, Mbins)

volume = (2500.)**3. 
norm = volume * n.median(Mbins[1:]-Mbins[:-1]) *n.median(ARbins[1:]-ARbins[:-1]) 
print norm , n.log10(0.8/norm)

p.figure(1,(10,6))
for iii,el in enumerate(centralList) :
    z=1./float(el.split('-')[-1][:-4])-1.
    data = n.loadtxt(el,unpack=True)
    p.title("z="+str(n.round(z,3)))
    p.pcolormesh(X, Y, n.log10(data.T/norm),vmin=n.log10(0.8/norm),vmax=-4,rasterized=True)
    cb = p.colorbar(shrink=0.7)
    cb.set_label('N/(V dlogM dAR) ')
    p.ylim((11,16))
    p.ylabel(r'log $M_{peak}$ [km/s]')
    p.xlim((0,50000))
    p.xlabel('Accretion rate Msun/h/yr at Mpeak')
    p.savefig(Pdir + "plot-hist2d-central-Mpeak-Accrate-"+str(n.round(z,5))+".pdf")
    p.clf()


sys.exit()



centralList = n.array(glob.glob(dir+"hist2d-central-Vpeak-Accrate-?.?????.dat"))
centralList.sort()
print centralList

X,Y= n.meshgrid(ARbins, Vbins)

volume = (2500.)**3. 
norm = volume * n.median(Vbins[1:]-Vbins[:-1]) *n.median(ARbins[1:]-ARbins[:-1]) 
p.figure(1,(10,6))
for iii,el in enumerate(centralList) :
    z=1./float(el.split('-')[-1][:-4])-1.
    data = n.loadtxt(el,unpack=True)
    p.title("z="+str(n.round(z,3)))
    p.pcolormesh(X, Y, n.log10(data.T/norm),vmin=n.log10(0.8/norm),vmax=-4,rasterized=True)
    cb = p.colorbar(shrink=0.7)
    cb.set_label('N/(V dlogV dAR) ')
    p.ylim((1.5,3.5))
    p.ylabel(r'log $V_{peak}$ [km/s]')
    p.xlim((0,50000))
    p.xlabel('Growth Rate of Mpeak [z, z+0.5] Msun/h/yr')
    p.savefig(Pdir + "plot-hist2d-central-Vpeak-Accrate-"+str(n.round(z,5))+".pdf")
    p.clf()





centralList = n.array(glob.glob(dir+"hist-sat-Mpeak-?.?????.dat"))
centralList.sort()
print centralList

p.figure(1,(10,6))

for iii,el in enumerate(centralList) :
    z=1./float(el.split('-')[-1][:-4])-1.
    b0,b1,val = n.loadtxt(el,unpack=True)
    p.plot((10**b0+10**b1)/2.,val/(volume * (b1 - b0) ),label="z="+str(n.round(z,3)), rasterized=True)
    
    if iii%15==0 :
        p.axhline(1/(volume*n.median((b1 - b0))),label=r'1/(dlogMx2500$^3$)')
        p.axvline(23593750000.0*100, label='100 Mp')
        p.xlim((23593750000.0*50,5e16))
        p.ylim((0.5/(volume*n.median((b1 - b0))), 1e-1))
        p.xlabel(r'$M_{peak}$ [M$_\odot$/h]')
        p.ylabel(r'N($V_1<M_{peak}<V_2$) / dlog Mpeak / Volume [ h/M$_\odot$ . h3/Mpc3 ]')
        p.xscale('log')    
        p.yscale('log')    
        p.legend()
        p.grid()
        p.savefig(Pdir + "plot-hist-sat-Mpeak-"+str(iii)+".pdf")
        p.clf()



centralList = n.array(glob.glob(dir+"hist-central-Mpeak-?.?????.dat"))
centralList.sort()
print centralList

volume = (2500.)**3. 

p.figure(1,(10,6))

for iii,el in enumerate(centralList) :
    z=1./float(el.split('-')[-1][:-4])-1.
    b0,b1,val = n.loadtxt(el,unpack=True)
    p.plot((10**b0+10**b1)/2.,val/(volume * (b1 - b0) ),label="z="+str(n.round(z,3)), rasterized=True)

    if iii%15==0 :
        p.axhline(1/(volume*n.median((b1 - b0))),label=r'1/(dlogMx2500$^3$)')
        p.axvline(23593750000.0*100, label='100 Mp')
        p.xlim((23593750000.0*50,5e16))
        p.ylim((0.5/(volume*n.median((b1 - b0))), 1e-1))
        p.xlabel(r'$M_{peak}$ [M$_\odot$/h]')
        p.ylabel(r'N($V_1<M_{peak}<V_2$) / dlog Mpeak / Volume [ h/M$_\odot$. h3/Mpc3 ]')
        p.xscale('log')    
        p.yscale('log')    
        p.legend()
        p.grid()
        p.savefig(Pdir + "plot-hist-central-Mpeak-"+str(iii)+".pdf")
        p.clf()


sys.exit()





volume = (2500.)**3. 

centralList = n.array(glob.glob(dir+"hist-sat-Vpeak-?.?????.dat"))
centralList.sort()


p.figure(1,(10,6))

for iii,el in enumerate(centralList) :
    z=1./float(el.split('-')[-1][:-4])-1.
    b0,b1,val = n.loadtxt(el,unpack=True)
    p.plot((10**b0+10**b1)/2.,val/(volume * (b1 - b0) ),label="z="+str(n.round(z,3)), rasterized=True)
    
    if iii%15==0 :
        p.axhline(1/(volume*n.median((b1 - b0))),label=r'1/(0.01x2500$^3$)')
        p.xlim((100,1e5))
        p.ylim((0.5/(volume*n.median((b1 - b0))), 1e-1))
        p.xlabel(r'$V_{peak}$ [km/s]')
        p.ylabel(r'N($V_1<V_{peak}<V_2$) / dlog Vpeak / Volume [ s/km . h3/Mpc3 ]')
        p.xscale('log')    
        p.yscale('log')    
        p.legend()
        p.grid()
        p.savefig(Pdir + "plot-hist-sat-Vpeak-"+str(iii)+".pdf")
        p.clf()



centralList = n.array(glob.glob(dir+"hist-central-Vpeak-?.?????.dat"))
centralList.sort()

volume = (2500.)**3. 

p.figure(1,(10,6))

for iii,el in enumerate(centralList) :
    z=1./float(el.split('-')[-1][:-4])-1.
    b0,b1,val = n.loadtxt(el,unpack=True)
    p.plot((10**b0+10**b1)/2.,val/(volume * (b1 - b0) ),label="z="+str(n.round(z,3)), rasterized=True)

    if iii%15==0 :
        p.axhline(1/(volume*n.median((b1 - b0))),label=r'1/(0.01x2500$^3$)')
        p.xlim((100,1e5))
        p.ylim((0.5/(volume*n.median((b1 - b0))), 1e-1))
        p.xlabel(r'$V_{peak}$ [km/s]')
        p.ylabel(r'N($V_1<V_{peak}<V_2$) / dlog Vpeak / Volume [ s/km . h3/Mpc3 ]')
        p.xscale('log')    
        p.yscale('log')    
        p.legend()
        p.grid()
        p.savefig(Pdir + "plot-hist-central-Vpeak-"+str(iii)+".pdf")
        p.clf()


sys.exit()




zzz=[]
for ii in range(len(centralList)):
    zzz.append( centralList[ii].split('-')[-1][:-4] )

Zset = list(set(zzz))

for el in Zset :
    centralList = n.array(glob.glob(dir+"hist-central-Vpeak-"+el+".dat"))
    centralList.sort()


    massB[:-1], massB[1:],  nnM.sum(axis=0)


    nnM = n.empty( [len(centralList),len(massB)-1] ) 
    nnV = n.empty( [len(centralList),len(vcirB)-1] )
    dataVC = n.empty( [len(centralList),len(vcirB)-1,len(concB)-1] )
    dataMC = n.empty( [len(centralList),len(massB)-1,len(concB)-1] )

    for jj in range(len(centralList)):
        f=open(centralList[jj],'r')
        nnMinter,nnVinter,nnCinter,dataMCinter,dataVCinter = cPickle.load(f)
        nnM[jj] = nnMinter
        nnV[jj] = nnVinter 
        dataMC[jj] = dataMCinter[0]
        dataVC[jj] = dataVCinter[0]
        f.close()


    n.savetxt("/data2/DATA/eBOSS/Multidark-lightcones/MD_2.5Gpc/properties/hist-central-Mpeak-"+box.get_snl()[ii].split('_')[-1][:-5]+".dat",n.transpose([massB[:-1], massB[1:],  nnM.sum(axis=0)]))

    n.savetxt("/data2/DATA/eBOSS/Multidark-lightcones/MD_2.5Gpc/properties/hist-central-Vpeak-"+box.get_snl()[ii].split('_')[-1][:-5]+".dat",n.transpose([vcirB[:-1], vcirB[1:],  nnV.sum(axis=0)]) )

    n.savetxt("/data2/DATA/eBOSS/Multidark-lightcones/MD_2.5Gpc/properties/hist2d-central-Mpeak-Accrate-"+box.get_snl()[ii].split('_')[-1][:-5]+".dat",dataMC.sum(axis=0))

    n.savetxt("/data2/DATA/eBOSS/Multidark-lightcones/MD_2.5Gpc/properties/hist2d-central-Vpeak-Accrate-"+box.get_snl()[ii].split('_')[-1][:-5]+".dat",dataVC.sum(axis=0))


    satList = n.array(glob.glob("/data2/DATA/eBOSS/Multidark-lightcones/MD_2.5Gpc/properties/*"+box.get_snl()[ii].split('_')[-1][:-5]+"*MVAmatrixSatellite*.pkl"))
    satList.sort()

    nnM = n.empty( [len(satList),len(massB)-1] ) 
    nnV = n.empty( [len(satList),len(vcirB)-1] )
    dataVC = n.empty( [len(satList),len(vcirB)-1,len(concB)-1] )
    dataMC = n.empty( [len(satList),len(massB)-1,len(concB)-1] )

    for jj in range(len(satList)):
        f=open(satList[jj],'r')
        nnMinter,nnVinter,nnCinter,dataMCinter,dataVCinter = cPickle.load(f)
        nnM[jj] = nnMinter
        nnV[jj] = nnVinter 
        dataMC[jj] = dataMCinter[0]
        dataVC[jj] = dataVCinter[0]
        f.close()


    n.savetxt("/data2/DATA/eBOSS/Multidark-lightcones/MD_2.5Gpc/properties/hist-sat-Mpeak-"+box.get_snl()[ii].split('_')[-1][:-5]+".dat",n.transpose([massB[:-1], massB[1:],  nnM.sum(axis=0)]))

    n.savetxt("/data2/DATA/eBOSS/Multidark-lightcones/MD_2.5Gpc/properties/hist-sat-Vpeak-"+box.get_snl()[ii].split('_')[-1][:-5]+".dat",n.transpose([vcirB[:-1], vcirB[1:],  nnV.sum(axis=0)]) )

    n.savetxt("/data2/DATA/eBOSS/Multidark-lightcones/MD_2.5Gpc/properties/hist2d-sat-Mpeak-Accrate-"+box.get_snl()[ii].split('_')[-1][:-5]+".dat",dataMC.sum(axis=0))

    n.savetxt("/data2/DATA/eBOSS/Multidark-lightcones/MD_2.5Gpc/properties/hist2d-sat-Vpeak-Accrate-"+box.get_snl()[ii].split('_')[-1][:-5]+".dat",dataVC.sum(axis=0))



