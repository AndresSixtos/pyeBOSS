import astropy.units as uu
import astropy.cosmology as co
aa = co.Planck13
#aah = co.FlatLambdaCDM(H0=100.0 *uu.km / (uu.Mpc *uu.s), Om0=0.307, Tcmb0=2.725 *uu.K, Neff=3.05, m_nu=[ 0.  ,  0. ,   0.06]*uu.eV, Ob0=0.0483)
#rhom = aa.critical_density0.to(uu.solMass*uu.Mpc**-3).value
#aa.critical_density0.to(uu.solMass*uu.Mpc**-3).value
#aah.critical_density0.to(uu.solMass*uu.Mpc**-3).value

from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import interp1d
import numpy as n
import matplotlib
matplotlib.use('pdf')
matplotlib.rcParams['font.size']=12
import matplotlib.pyplot as p
import glob
import sys
from scipy.optimize import curve_fit
import cPickle
from os.path import join
from scipy.optimize import minimize

dir = "/Volumes/data/BigMD/mvirFunction/"
Pdir = "/Volumes/data/BigMD/mvirFunction/plots/"

def getVF(b0, b1, val,volume,label="SMD",completeness = 100, maxV=16,errFactor=1.):
    """returns the cumulative function n(>X) """
    Nc = n.array([ n.sum(val[ii:]) for ii in range(len(val)) ])
    xData_A = (10**b0+10**b1)/2.
    yData_A = Nc/(volume ) 
    yDataErr_A = errFactor/val**0.5
    sel = (yDataErr_A!=n.inf)&(yData_A>0) &(yData_A * volume >= 1) &(xData_A > completeness)&(xData_A < maxV)
    xData = xData_A[sel]
    yData = yData_A[sel]
    yDataErr = yDataErr_A[sel]*yData_A[sel]
    return xData,yData,yDataErr,volume

def getDiffVF(b0, b1, val,volume,label="SMD",completeness = 100, maxV=16,errFactor=1.):
    """returns the differential function dn / dX """
    xData_A = (10**b0+10**b1)/2.
    yData_A = val/(volume * (10**b1-10**b0))
    yDataErr_A = errFactor/val**0.5
    sel = (yDataErr_A!=n.inf)&(yData_A>0) &(yDataErr_A<1.) & (yDataErr_A>0.) &(xData_A > completeness)&(xData_A < maxV)
    xData = xData_A[sel]
    yData = yData_A[sel]
    yDataErr = yDataErr_A[sel]*yData_A[sel]
    return xData,yData,yDataErr,volume

#saundersFct=lambda v, A, logv0,alpha,sig : 10**A * ( v /10**logv0)**(alpha) * n.e**( -n.log10( 1 + v /10**logv0)/(2*sig**2.))
#schechterFct=lambda v, A, logv0,alpha, sig : 10**A * ( v /10**logv0)**(alpha) * n.e**( - v / 10**logv0 /(2*sig**2.) )
#ps * (10**logl/10**logls)**(a+1) * n.e**(-10**logl/10**logls)
#doublePL=lambda v,A,logv0 ,a,b: 10**A * 10**( (1+a)*( v - 10**logv0) + b )


mf = lambda v, A, v0, alpha, beta : 10**A * (v/10**v0)**beta * n.e**(- (v/10**v0)**alpha )

limits_04 = [1e7, 1e12]
limits_10 = [1e11, 1e14]
limits_25 = [1e12, 1e15]
limits_40 = [1e13, 1e16]
zmin = 0.
zmax = 5.

dir_04 = "/data2/DATA/eBOSS/Multidark-lightcones/MD_0.4Gpc/"
dir_10 = "/data2/DATA/eBOSS/Multidark-lightcones/MD_1Gpc_new_rockS/"
dir_25 = "/data2/DATA/eBOSS/Multidark-lightcones/MD_2.5Gpc/"
dir_40 = "/data2/DATA/eBOSS/Multidark-lightcones/MD_4Gpc/"

dir_boxes =  n.array([dir_04, dir_10, dir_25, dir_40])
zList_files = n.array([ join(dir_box, "snapshots","redshift-list.txt") for dir_box in dir_boxes])
qty_limits = n.array([limits_04, limits_10, limits_25, limits_40])
volume_boxes =  n.array([400.**3., 1000**3., 2500**3., 4000.**3.])

property_dir = "properties/vmax-mvir"
type = "hist"
cos = "Central" # centrak or satellite ?
qty = "mvir"

print "we consider the ",type,"of",qty,"of", cos
print "in the redshift range",zmin,zmax
print "for the boxes",dir_boxes
#print zList_files
print "within the following limits for each box",qty_limits
print "each box has a volume of",volume_boxes, "Mpc3/h3"

fileName = type + "-"+ cos +"-"+ qty +"-*.dat"

fileList = n.array(glob.glob(join(dir_04, property_dir,fileName)))
fileList.sort()

xData_04,yData_04,yDataErr_04,z_04 = [], [], [], []
nSN, aSN = n.loadtxt(zList_files[0], unpack=True, dtype={'names': ('nSN', 'aSN'), 'formats': ('i4', 'f4')})
conversion = dict(n.transpose([ nSN, 1/aSN-1 ]))

for ii in range(len(fileList)):
    SMDfile = fileList[ii]
    print SMDfile
    b0_04, b1_04, val_04 = n.loadtxt(SMDfile,unpack=True)
    xData_04_ii,yData_04_ii,yDataErr_04_ii,volume_04_ii = getVF(b0_04, b1_04, val_04,400.**3.,completeness = limits_04[0], maxV = limits_04[1])
    print SMDfile.split('-')[-1][:-4]
    z_04_ii = conversion[float(SMDfile.split('-')[-1][:-4])]*n.ones_like(xData_04_ii)
    if z_04_ii[0]<zmax :
        xData_04.append(xData_04_ii)
        yData_04.append(yData_04_ii)
        yDataErr_04.append(yDataErr_04_ii)
        z_04.append(z_04_ii)

z_04 = n.hstack((z_04))
xData_04 = n.hstack((xData_04))
yData_04 = n.hstack((yData_04))
yDataErr_04 = n.hstack((yDataErr_04))

n.savetxt(join(dir_04, property_dir, type + "-"+ cos +"-"+ qty  +"ALL_MD_0.4Gpc.dat"),n.transpose([xData_04,z_04,yData_04,yDataErr_04]))

############ 1 Gpc ##############
fileList = glob.glob(join(dir_10, property_dir,fileName))
xData_10,yData_10,yDataErr_10,z_10 = [], [], [], []
nSN, aSN = n.loadtxt(zList_files[1], unpack=True, dtype={'names': ('nSN', 'aSN'), 'formats': ('i4', 'f4')})
conversion = dict(n.transpose([ nSN, 1/aSN-1 ]))

for ii in range(len(fileList)):
    SMDfile = fileList[ii]
    print SMDfile
    b0_10, b1_10, val_10 = n.loadtxt(SMDfile,unpack=True)
    xData_10_ii,yData_10_ii,yDataErr_10_ii,volume_10_ii = getVF(b0_10, b1_10, val_10,1000.**3.,completeness = limits_10[0], maxV = limits_10[1])
    z_10_ii = conversion[float(SMDfile.split('-')[-1][:-4])]*n.ones_like(xData_10_ii)
    if z_10_ii[0]<zmax :
        xData_10.append(xData_10_ii)
        yData_10.append(yData_10_ii)
        yDataErr_10.append(yDataErr_10_ii)
        z_10.append(z_10_ii)

z_10 = n.hstack((z_10))
xData_10 = n.hstack((xData_10))
yData_10 = n.hstack((yData_10))
yDataErr_10 = n.hstack((yDataErr_10))

n.savetxt(join(dir_10, property_dir, type + "-"+ cos +"-"+ qty  +"ALL_MD_1Gpc"+".dat"),n.transpose([xData_10,z_10,yData_10,yDataErr_10]))

############ 2.5 Gpc ##############

fileList = glob.glob(join(dir_25, property_dir,fileName))
xData_25,yData_25,yDataErr_25,z_25 = [], [], [], []
nSN, aSN = n.loadtxt(zList_files[2], unpack=True, dtype={'names': ('nSN', 'aSN'), 'formats': ('i4', 'f4')})
conversion = dict(n.transpose([ nSN, 1/aSN-1 ]))

for ii in range(len(fileList)):
    SMDfile = fileList[ii]
    print SMDfile
    b0_25, b1_25, val_25 = n.loadtxt(SMDfile,unpack=True)
    xData_25_ii,yData_25_ii,yDataErr_25_ii,volume_25_ii = getVF(b0_25, b1_25, val_25,2500.**3.,completeness = limits_25[0], maxV = limits_25[1])
    z_25_ii = conversion[float(SMDfile.split('-')[-1][:-4])]*n.ones_like(xData_25_ii)
    if z_25_ii[0]<zmax :
        xData_25.append(xData_25_ii)
        yData_25.append(yData_25_ii)
        yDataErr_25.append(yDataErr_25_ii)
        z_25.append(z_25_ii)

z_25 = n.hstack((z_25))
xData_25 = n.hstack((xData_25))
yData_25 = n.hstack((yData_25))
yDataErr_25 = n.hstack((yDataErr_25))

n.savetxt(join(dir_25, property_dir, type + "-"+ cos +"-"+ qty  +"ALL_MD_2.5Gpc"+".dat"),n.transpose([xData_25,z_25,yData_25,yDataErr_25]))

############ 4 Gpc ##############

fileList = glob.glob(join(dir_40, property_dir,fileName))
xData_40,yData_40,yDataErr_40,z_40 = [], [], [], []
nSN, aSN = n.loadtxt(zList_files[3], unpack=True, dtype={'names': ('nSN', 'aSN'), 'formats': ('i4', 'f4')})
conversion = dict(n.transpose([ nSN, 1/aSN-1 ]))

for ii in range(len(fileList)):
    SMDfile = fileList[ii]
    print SMDfile
    b0_40, b1_40, val_40 = n.loadtxt(SMDfile,unpack=True)
    xData_40_ii,yData_40_ii,yDataErr_40_ii,volume_40_ii = getVF(b0_40, b1_40, val_40,4000.**3.,completeness = limits_40[0], maxV = limits_40[1])
    z_40_ii = conversion[float(SMDfile.split('-')[-1][:-4])]*n.ones_like(xData_40_ii)
    if z_40_ii[0]<zmax :
        xData_40.append(xData_40_ii)
        yData_40.append(yData_40_ii)
        yDataErr_40.append(yDataErr_40_ii)
        z_40.append(z_40_ii)

z_40 = n.hstack((z_40))
xData_40 = n.hstack((xData_40))
yData_40 = n.hstack((yData_40))
yDataErr_40 = n.hstack((yDataErr_40))

n.savetxt(join(dir_40, property_dir, type + "-"+ cos +"-"+ qty  +"ALL_MD_4Gpc"+".dat"),n.transpose([xData_40,z_40,yData_40,yDataErr_40]))

sys.exit()

xData_04,z_04,yData_04,yDataErr_04 = n.loadtxt(join(dir_04, property_dir, type + "-"+ cos +"-"+ qty  +"ALL_MD_0.4Gpc"+".dat"),unpack=True)
xData_10,z_10,yData_10,yDataErr_10 = n.loadtxt(join(dir_10, property_dir, type + "-"+ cos +"-"+ qty  +"ALL_MD_1Gpc"+".dat"),unpack=True)
xData_25,z_25,yData_25,yDataErr_25 = n.loadtxt(join(dir_25, property_dir, type + "-"+ cos +"-"+ qty  +"ALL_MD_2.5Gpc"+".dat"),unpack=True)
xData_40,z_40,yData_40,yDataErr_40 = n.loadtxt(join(dir_40, property_dir, type + "-"+ cos +"-"+ qty  +"ALL_MD_4Gpc"+".dat"),unpack=True)

xData_40,yData_40,yDataErr_40,z_40 = [], [], [], []
for ii in range(len(fileList)):
    SMDfile = fileList[ii]
    b0_40, b1_40, val_40 = n.loadtxt(SMDfile,unpack=True)
    xData_40_ii,yData_40_ii,yDataErr_40_ii,volume_40_ii = getDiffVF(b0_40, b1_40, val_40,4000.**3.,completeness = limits_40[0], maxV = limits_40[1])
    z_40_ii = (1/float(SMDfile.split('-')[-1][:-4])-1)*n.ones_like(xData_40_ii)
    if z_40_ii[0]<zmax :
        xData_40.append(xData_40_ii)
        yData_40.append(yData_40_ii)
        yDataErr_40.append(yDataErr_40_ii)
        z_40.append(z_40_ii)

z_40 = n.hstack((z_40))
xData_40 = n.hstack((xData_40))
yData_40 = n.hstack((yData_40))
yDataErr_40 = n.hstack((yDataErr_40))

n.savetxt(join(dir, "data", type + "-"+ cos +"-"+ qty  +"MD_4Gpc-diff"+".dat"),n.transpose([xData_40,z_40,yData_40,yDataErr_40]))


################################ Plot differential halo mass function  ################################


xData_04,z_04,yData_04,yDataErr_04 = n.loadtxt(join(dir,"data", type + "-"+ cos +"-"+ qty  +"MD_0.4Gpc-diff"+".dat"),unpack=True)
xData_10,z_10,yData_10,yDataErr_10 = n.loadtxt(join(dir,"data", type + "-"+ cos +"-"+ qty  +"MD_1Gpc-diff"+".dat"),unpack=True)
xData_25,z_25,yData_25,yDataErr_25 = n.loadtxt(join(dir,"data", type + "-"+ cos +"-"+ qty  +"MD_2.5Gpc-diff"+".dat"),unpack=True)
xData_40,z_40,yData_40,yDataErr_40 = n.loadtxt(join(dir,"data", type + "-"+ cos +"-"+ qty  +"MD_4Gpc-diff"+".dat"),unpack=True)

rhom_04 = n.array([aa.critical_density(zz).to(uu.solMass*uu.Mpc**-3).value/aa.h**2 for zz in z_04])
rhom_10 = n.array([aa.critical_density(zz).to(uu.solMass*uu.Mpc**-3).value/aa.h**2 for zz in z_10])
rhom_25 = n.array([aa.critical_density(zz).to(uu.solMass*uu.Mpc**-3).value/aa.h**2 for zz in z_25])
rhom_40 = n.array([aa.critical_density(zz).to(uu.solMass*uu.Mpc**-3).value/aa.h**2 for zz in z_40])

rhom_04 = n.array([aa.critical_density(zz).to(uu.solMass*uu.Mpc**-3).value for zz in z_04])
rhom_10 = n.array([aa.critical_density(zz).to(uu.solMass*uu.Mpc**-3).value for zz in z_10])
rhom_25 = n.array([aa.critical_density(zz).to(uu.solMass*uu.Mpc**-3).value for zz in z_25])
rhom_40 = n.array([aa.critical_density(zz).to(uu.solMass*uu.Mpc**-3).value for zz in z_40])

dat = n.loadtxt("/Volumes/data/BigMD/mVector_PLANCK_HMD.txt", unpack=True)

p.figure(1,(6,6))
p.axes([0.17,0.17,0.75,0.75])

p.plot(n.log10(dat[0]),n.log10(dat[0]*dat[0]*dat[5]),'k--',lw=2)

s_04 = (z_04 == 0)
y_04 = n.log10(yData_04*xData_04**2./rhom_04)
y_04 = n.log10(yData_04*xData_04*xData_04)
p.plot(n.log10(xData_04[s_04]), y_04[s_04], marker ='o', mfc='None',mec='r',ls='none', label="SMD", rasterized=True)

s_10 = (z_10 == 0)
y_10 = n.log10(yData_10*xData_10**2./rhom_10)
y_10 = n.log10(yData_10*xData_10*xData_10)
p.plot(n.log10(xData_10[s_10]),y_10[s_10], marker ='v', mfc='None',mec='c',ls='none', label="MDPL", rasterized=True)

s_25 = (z_25 == 0)
y_25 = n.log10(yData_25*xData_25**2./rhom_25)
y_25 = n.log10(yData_25*xData_25*xData_25)
p.plot(n.log10(xData_25[s_25]),y_25[s_25], marker ='s', mfc='None',mec='m',ls='none', label="BigMD", rasterized=True)

s_40 = (z_40 == 0)
y_40 = n.log10(yData_40*xData_40**2./rhom_40)
y_40 = n.log10(yData_40*xData_40*xData_40)
p.plot(n.log10(xData_40[s_40]),y_40[s_40], marker ='p', mfc='None',mec='b',ls='none', label="HMD", rasterized=True)

p.xlabel(r'log$_{10}[M_{vir}/(h^{-1}M_\odot)]$')
p.ylabel(r'log$_{10}[(M^2/\rho_m) \; dn/dM]')
p.legend(loc=3)
p.grid()
p.savefig(Pdir + "mvir-function2.pdf")
p.clf()

sys.exit()

fig = p.figure(1,(9,9))
ax = fig.add_subplot(111, projection='3d')

sc1 = ax.scatter(n.log10(xData_04),z_04,n.log10(yData_04*xData_04**2./rhom_04), s=n.ones_like(z_04)*3, c='r', marker='o',label="SMD", rasterized=True)
sc1.set_edgecolor('face')

sc1 = ax.scatter(n.log10(xData_10),z_10,n.log10(yData_10*xData_10**2./rhom_10), s=n.ones_like(z_10)*3, c='c', marker='v',label="MDPL", rasterized=True)
sc1.set_edgecolor('face')

sc1 = ax.scatter(n.log10(xData_25),z_25,n.log10(yData_25*xData_25**2./rhom_25), s=n.ones_like(z_25)*3, c='m', marker='s',label="BigMD", rasterized=True)
sc1.set_edgecolor('face')

sc1 = ax.scatter(n.log10(xData_40),z_40,n.log10(yData_40*xData_40**2./rhom_40), s=n.ones_like(z_40)*3, c='b', marker='p',label="HMD", rasterized=True)
sc1.set_edgecolor('face')

ax.legend()
ax.set_xlabel(r'$log_{10}[M_{vir}/(h^{-1}M_\odot)]$')
ax.set_ylabel('redshift')
ax.set_ylim((0,zmax))
ax.set_zlabel(r'$log_{10}[(M^2/\rho_m) \; dn/dM]$')
ax.set_zlim((-4,0))
p.savefig(Pdir + "mvir-function-3d-diff.pdf")
p.show()



sys.exit()

################################ Model Fits on the cumulative function ################################

xData_04,z_04,yData_04,yDataErr_04 = n.loadtxt(join(dir,"data", type + "-"+ cos +"-"+ qty  +"MD_0.4Gpc"+".dat"),unpack=True)
xData_10,z_10,yData_10,yDataErr_10 = n.loadtxt(join(dir,"data", type + "-"+ cos +"-"+ qty  +"MD_1Gpc"+".dat"),unpack=True)
xData_25,z_25,yData_25,yDataErr_25 = n.loadtxt(join(dir,"data", type + "-"+ cos +"-"+ qty  +"MD_2.5Gpc"+".dat"),unpack=True)
xData_40,z_40,yData_40,yDataErr_40 = n.loadtxt(join(dir,"data", type + "-"+ cos +"-"+ qty  +"MD_4Gpc"+".dat"),unpack=True)

redshift = n.hstack(( z_04, z_10, z_25, z_40))
mvir = n.hstack(( xData_04, xData_10, xData_25, xData_40))
yData = n.hstack(( yData_04, yData_10, yData_25, yData_40))
yDataErr = n.hstack(( yDataErr_04, yDataErr_10, yDataErr_25, yDataErr_40))

vf = lambda v, A, v0, alpha, beta : 10**A * (v/10**v0)**beta * n.e**(- (v/10**v0)**alpha )

vfG = lambda v, z, A0, A1, vcut0, vcut1, a0, a1, a2, b0, b1 : 10**(A0 + A1 * z) * (1+ (v/10**(vcut0 + vcut1 * z))**(b0 + b1 * z) )* n.e**(- (v/10**(vcut0 + vcut1 * z))**(a0 + a1 * z + a2 * z**2.) )
vfGbis = lambda v, z, p0 : vfG(v,z,p0[0],p0[1],p0[2],p0[3],p0[4],p0[5],p0[6],p0[7],p0[8])
chi2fun = lambda p0 : n.sum((vfGbis(mvir,redshift,p0) - yData)**2. / yDataErr**2. )/len(yDataErr)

"""
vfG0 = lambda v, z, A1, vcut1, a1, a2, b1 : 10**(-3.48089246 + A1 * z) * (v/10**(2.73872233 + vcut1 * z))**( -2.70150905 + b1 * z) * n.e**(- (v/10**(2.73872233 + vcut1 * z))**(1.47758206 + a1 * z + a2 * z**2.) )

vfGbis0 = lambda v, z, p0 : vfG0(v,z,p0[0],p0[1],p0[2],p0[3],p0[4])
chi2fun = lambda p0 : n.sum((vfGbis0(mvir,redshift,p0) - yData)**2. / yDataErr**2. )/len(yDataErr)

vfG0 = lambda v, z, A1, vcut1, a1, a2, b1 : 10**(-3.48089246 + A1 * z) * (v/10**(2.73872233 + vcut1 * z))**( -2.70150905 + b1 * z) * n.e**(- (v/10**(2.73872233 + vcut1 * z))**(1.47758206 + a1 * z + a2 * z**2.) )

vfGbis0 = lambda v, z, p0 : vfG0(v,z,p0[0],p0[1],p0[2],p0[3],p0[4])
chi2fun = lambda p0 : n.sum((vfGbis0(mvir,redshift,p0) - yData)**2. / yDataErr**2. )/len(yDataErr)
"""
p1 = n.array([3, 0.73575868, 12, -0.17861551, 2, -0.32736035,  0.221566, -2, 0.16587088])#4, 0.6, 2.85, -0.1, 1.77, -0.03, 0., -2.8, -0.1 ])


print "looks for the optimum parameters"
res = minimize(chi2fun, p1, method='Powell',options={'xtol': 1e-6, 'disp': True, 'maxiter' : 50000000, 'nfev': 1800000})

print "ndof=",len(yDataErr)
print res
A0, A1, vcut0, vcut1, a0, a1, a2, b0, b1 = n.round(res.x,2)
#A1, vcut1, a1, a2, b1 = n.round(res.x,2)
#A0 = -3.48
#vcut0 = 1.48
#a0 = -2.70
#b0 =  2.74

print "A(z) & = "+str(A0)+" + "+str(A1)+r'\times z \\'
print r" M_{cut}(z) & = "+str(vcut0)+" + "+str(vcut1)+r'\times z \\'
print r" \alpha(z) & = "+str(a0)+" + "+str(a1)+r'\times z + '+str(a2)+r'\times z^2 \\'
print r" \beta(z) & = "+str(b0)+" + "+str(b1)+r'\times z \\'

# now outputs the model
X,Y = n.meshgrid(n.logspace(n.log10(limits_04[0]),n.log10(limits_40[1]),200),n.arange(0,zmax,0.025))

Z = vfGbis(X,Y,res.x)

n.savetxt(join(dir,"data/best_fit.dat"),n.transpose([n.hstack((X)), n.hstack((Y)), n.hstack((Z))]) )

#######################################################
# now plots the results of the fit
print "now plots the results of the fit"

xData_04,z_04,yData_04,yDataErr_04 = n.loadtxt(join(dir,"data/", type + "-"+ cos +"-"+ qty  +"MD_0.4Gpc"+".dat"),unpack=True)
xData_10,z_10,yData_10,yDataErr_10 = n.loadtxt(join(dir,"data/", type + "-"+ cos +"-"+ qty  +"MD_1Gpc"+".dat"),unpack=True)
xData_25,z_25,yData_25,yDataErr_25 = n.loadtxt(join(dir,"data/", type + "-"+ cos +"-"+ qty  +"MD_2.5Gpc"+".dat"),unpack=True)
xData_40,z_40,yData_40,yDataErr_40 = n.loadtxt(join(dir,"data/", type + "-"+ cos +"-"+ qty  +"MD_4Gpc"+".dat"),unpack=True)

vmax_mod, z_mod, n_mod = n.loadtxt(join(dir,"data/best_fit.dat"), unpack=True)

#####################

fig = p.figure(1,(9,9))
ax = fig.add_subplot(111, projection='3d')
ax.plot_wireframe(n.log10(X), Y, n.log10(Z), rstride=10, cstride=10)

sc1 = ax.scatter(n.log10(xData_04),z_04,n.log10(yData_04), s=n.ones_like(z_04)*3, c='r', marker='o',label="SMD", rasterized=True)
sc1.set_edgecolor('face')

sc1 = ax.scatter(n.log10(xData_10),z_10,n.log10(yData_10), s=n.ones_like(z_10)*3, c='c', marker='v',label="MDPL", rasterized=True)
sc1.set_edgecolor('face')

sc1 = ax.scatter(n.log10(xData_25),z_25,n.log10(yData_25), s=n.ones_like(z_25)*3, c='m', marker='s',label="BigMD", rasterized=True)
sc1.set_edgecolor('face')

sc1 = ax.scatter(n.log10(xData_40),z_40,n.log10(yData_40), s=n.ones_like(z_40)*3, c='b', marker='p',label="HMD", rasterized=True)
sc1.set_edgecolor('face')

ax.legend()
ax.set_xlabel(r'log $M_{vir}$ [km s$^{-1}$]')
ax.set_ylabel('redshift')
ax.set_ylim((0,zmax))
ax.set_zlabel(r'log N($>M_{vir}$) [ h$^3$ Mpc$^{-3}$]')
ax.set_zlim((-10,0))
#ax.set_yscale('log')
#ax.set_zscale('log')
p.savefig(Pdir + "mvir-function-3d-0-z-4.pdf")
p.clf()

fig = p.figure(1,(9,9))
ax = fig.add_subplot(111, projection='3d')

sc1 = ax.scatter(n.log10(xData_04),z_04,yData_04/vfGbis(xData_04,z_04,res.x), s=n.ones_like(z_04)*3, c='r', marker='o',label="SMD", rasterized=True)
sc1.set_edgecolor('face')

sc1 = ax.scatter(n.log10(xData_10),z_10,yData_10/vfGbis(xData_10,z_10,res.x), s=n.ones_like(z_10)*3, c='c', marker='v',label="MDPL", rasterized=True)
sc1.set_edgecolor('face')

sc1 = ax.scatter(n.log10(xData_25),z_25,yData_25/vfGbis(xData_25,z_25,res.x), s=n.ones_like(z_25)*3, c='m', marker='s',label="BigMD", rasterized=True)
sc1.set_edgecolor('face')

sc1 = ax.scatter(n.log10(xData_40),z_40,yData_40/vfGbis(xData_40,z_40,res.x), s=n.ones_like(z_40)*3, c='b', marker='p',label="HMD", rasterized=True)
sc1.set_edgecolor('face')

ax.legend()
ax.set_xlabel(r'log $M_{vir}$ [km s$^{-1}$]')
ax.set_ylabel('redshift')
ax.set_ylim((0,zmax))
ax.set_zlabel(r'Data / Model')
ax.set_zlim((0,5))
#ax.set_yscale('log')
#ax.set_zscale('log')
p.savefig(Pdir + "mvir-function-3d-dataOmodel-0-z-4.pdf")
p.show()



sys.exit()

######################
# z=0
zPlot=0.
s04 = (z_04==zPlot)
s10 = (z_10==zPlot)
s25 = (z_25==zPlot)
s40 = (z_40==zPlot)

p1 = n.array([-3.51218913,  0.77575315,  2.73736166, -0.17556627,  1.39837135,  -0.23156403,  0.262158  , -2.78723582,  0.31995556])
vfG = lambda v, z, A0, A1, vcut0, vcut1, a0, a1, a2, b0, b1 : 10**(A0 + A1 * z) * (v/10**(vcut0 + vcut1 * z))**(b0 + b1 * z) * n.e**(- (v/10**(vcut0 + vcut1 * z))**(a0 + a1 * z + a2 * z**2.) )

vfGbis = lambda v, z, p0 : vfG(v,z,p0[0],p0[1],p0[2],p0[3],p0[4],p0[5],p0[6],p0[7],p0[8])


p.figure(1,(6,6))
p.axes([0.17,0.17,0.75,0.75])

p.plot(xData_04[s04],yData_04[s04]*xData_04[s04]**2.8, marker ='o', mfc='None',mec='r',ls='none', label="SMD", rasterized=True)
p.plot(xData_10[s10],yData_10[s10]*xData_10[s10]**2.8, marker ='v', mfc='None',mec='c',ls='none', label="MDPL", rasterized=True)
p.plot(xData_25[s25],yData_25[s25]*xData_25[s25]**2.8, marker ='s', mfc='None',mec='m',ls='none', label="BigMD", rasterized=True)
p.plot(xData_40[s40],yData_40[s40]*xData_40[s40]**2.8, marker ='p', mfc='None',mec='b',ls='none', label="HMD", rasterized=True)

vmax_mod = n.hstack(( xData_04[s04], xData_10[s10], xData_25[s25], xData_40[s40] ))
vmax_mod.sort()
n_mod = vfGbis(vmax_mod, zPlot, p1)

p.plot(vmax_mod, n_mod* vmax_mod**2.8, 'k--', lw=2, label=r'best fit')

p.xlabel(r'$V_{max}$ [km s$^{-1}$]')
p.ylabel(r'N($>V_{max}$) $V_{max}^{2.8}$ [ h$^3$ Mpc$^{-3}$ (km s$^{-1}$)$^{2.8}$]')
p.xscale('log')
p.xlim((80,3000))
p.yscale('log')
p.legend(loc=3)
p.grid()
p.savefig(Pdir + "vmax-function-z-"+str(zPlot)+".pdf")
p.clf()


p.figure(2,(6,6))
p.axes([0.17,0.15,0.75,0.75])
p.fill_between(xData,1+yDataErr / yData,1-yDataErr / yData,rasterized=True,alpha=0.5)
p.plot(xData, yData / vf(xData,res[0], res[1], res[2], res[3]),'k')
p.xlabel(r'$V_{max}$ [km s$^{-1}$]')
p.ylabel(r'N($>V_{max}$) / best fit')
p.xscale('log')
p.ylim((0.9,1.1))
p.xlim((40,3000))
p.title("A="+str(n.round(res[0],2))+r" v$_0$="+ str(n.round(res[1],2))+r" $\alpha$="+ str(n.round(res[2],2))+r" $\beta$="+ str(n.round(res[3],2)) )
p.grid()
p.savefig(Pdir + "fit-ratio-z0.00.pdf")
p.clf()

print n.round(z_25,3), " & ", n.round(res,3), "\\\\"



sys.exit()
