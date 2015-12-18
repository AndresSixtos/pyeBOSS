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

#saundersFct=lambda v, A, logv0,alpha,sig : 10**A * ( v /10**logv0)**(alpha) * n.e**( -n.log10( 1 + v /10**logv0)/(2*sig**2.))
#schechterFct=lambda v, A, logv0,alpha, sig : 10**A * ( v /10**logv0)**(alpha) * n.e**( - v / 10**logv0 /(2*sig**2.) )
#ps * (10**logl/10**logls)**(a+1) * n.e**(-10**logl/10**logls)
#doublePL=lambda v,A,logv0 ,a,b: 10**A * 10**( (1+a)*( v - 10**logv0) + b )

mf = lambda v, A, v0, alpha, beta : 10**A * (v/10**v0)**beta * n.e**(- (v/10**v0)**alpha )

# limits at z0
limits_04 = [1e10, 5e12]
limits_10 = [5e11, 5e13]
limits_25 = [5e12, 5e14]
limits_40 = [1e13, 5e15]
zmin = 0.
zmax = 5

NDecimal = 4

dir = join("D:","\data","BigMD","M200cFunction")

qty_limits = n.array([limits_04, limits_10, limits_25, limits_40])
volume_boxes =  n.array([400.**3., 1000**3., 2500**3., 4000.**3.])

cos = "Central" # centrak or satellite ?
qty = "M200c"

print "we consider the ",type,"of",qty,"of", cos
print "in the redshift range",zmin,zmax
#print zList_files
print "within the following limits for each box",qty_limits
print "each box has a volume of",volume_boxes, "Mpc3/h3"

################################ Plot cumulative halo mass function and model at z=0  ################################

xData_04,z_04,yData_04,yDataErr_04 = n.loadtxt(join(dir,"hist-Central-M200c_ALL_cumulative_MD_0.4Gpc.dat"),unpack=True)
xData_10,z_10,yData_10,yDataErr_10 = n.loadtxt(join(dir,"hist-Central-M200c_ALL_cumulative_MD_1Gpc.dat"),unpack=True)
xData_25,z_25,yData_25,yDataErr_25 = n.loadtxt(join(dir,"hist-Central-M200c_ALL_cumulative_MD_2.5Gpc.dat"),unpack=True)
xData_40,z_40,yData_40,yDataErr_40 = n.loadtxt(join(dir,"hist-Central-M200c_ALL_cumulative_MD_4Gpc.dat"),unpack=True)

s_04 = (z_04 >= 0.0) & (z_04 <= zmax)
s_10 = (z_10 >= 0.0) & (z_10 <= zmax)
s_25 = (z_25 >= 0.0) & (z_25 <= zmax)
s_40 = (z_40 >= 0.0) & (z_40 <= zmax)

redshift = n.hstack(( z_04[s_04], z_10[s_10], z_25[s_25], z_40[s_40]))
print "all redshifts available:", set(redshift)
M200c = n.log10(n.hstack(( xData_04[s_04], xData_10[s_10], xData_25[s_25], xData_40[s_40])))
print "min and max masses available:", n.min(M200c), n.max(M200c)
yData = n.log10(n.hstack(( yData_04[s_04], yData_10[s_10], yData_25[s_25], yData_40[s_40])))
print "min and max Y available:", n.min(yData), n.max(yData)
yDataErr = abs(n.hstack(( yDataErr_04[s_04], yDataErr_10[s_10], yDataErr_25[s_25], yDataErr_40[s_40])) / yData)
print "min and max Y error available:", n.min(yDataErr), n.max(yDataErr)


p.figure(0,(6,6))
p.axes([0.17,0.17,0.75,0.75])

sc1=p.scatter(M200c, yData, c=redshift,s=10, marker='o',label="MD data", rasterized=True)
sc1.set_edgecolor('face')
cb = p.colorbar()
p.xlabel(r'log$_{10}[M_{200c}/(h^{-1}M_\odot)]$')
p.ylabel(r' n(>M)') # log$_{10}[ n(>M)]')
p.legend(loc=3)
p.grid()
p.savefig(join(dir , "M200c-cumulative-function-data.pdf"))
p.clf()

sys.exit()
################ now does the fits at redshift 0

s_04 = (z_04 <= 0.01)
s_10 = (z_10 <= 0.01)
s_25 = (z_25 <= 0.01)
s_40 = (z_40 <= 0.01)

redshift = n.hstack(( z_04[s_04], z_10[s_10], z_25[s_25], z_40[s_40]))
print "all redshifts available:", set(redshift)
M200c = n.log10(n.hstack(( xData_04[s_04], xData_10[s_10], xData_25[s_25], xData_40[s_40])))
print "min and max masses available:", n.min(M200c), n.max(M200c)
yData = n.log10(n.hstack(( yData_04[s_04], yData_10[s_10], yData_25[s_25], yData_40[s_40])))
print "min and max Y available:", n.min(yData), n.max(yData)
yDataErr = abs(n.hstack(( yDataErr_04[s_04], yDataErr_10[s_10], yDataErr_25[s_25], yDataErr_40[s_40])) / yData)
print "min and max Y error available:", n.min(yDataErr), n.max(yDataErr)



# with minimize

p0 = n.array([-3.5, 13.5, 0.8, -0.78])

vf = lambda v, A, v0, alpha, beta : n.log10( 10**A * (10**v/10**v0)**beta * n.e**(- (10**v/10**v0)**alpha ) )
#vfbis = lambda v, p0 : vf(v, p0[0], p0[1], p0[2], p0[3])
#chi2fun = lambda p0 : n.sum( (vfbis(M200c,p0) - yData)**2. / (yDataErr*100)**2 )/len(yDataErr)

#print "looks for the optimum parameters with minimize Powell"
#res_z0 = minimize(chi2fun, p0, method='Powell',options={'xtol': 1e-6, 'disp': True, 'maxiter' : 50000000, 'nfev': 1800000})

#print "ndof=",len(yDataErr)
#print res_z0


# with curve fit
print "with curve fit"
popt, cov = curve_fit(vf, M200c, yData, p0 = p0 , maxfev = 5000000)
print popt, cov
A0, vcut0, a0, b0 = n.round(popt,NDecimal)

print "redshift 0 model for the M200c cumulative function :"
print "A(z=0) & = "+str(A0)+ r"\pm ", n.round(cov[0][0]**0.5, NDecimal), r'\\'
print r" M_{200c}^{cut}(z=0) & = "+str(vcut0)+ r"\pm ", n.round(cov[1][1]**0.5, NDecimal), r'\\'
print r" \alpha(z=0) & = "+str(a0)+ r"\pm ", n.round(cov[2][2]**0.5, NDecimal), r'\\'
print r" \beta(z=0) & = "+str(b0)+ r"\pm ", n.round(cov[3][3]**0.5, NDecimal), r'\\'

p.figure(0,(6,6))
p.axes([0.17,0.17,0.75,0.75])

p.plot(n.log10(xData_04[s_04][::3]), n.log10(yData_04[s_04][::3]), marker ='o', mfc='None',mec='r',ls='none', label="SMD", rasterized=True)
p.plot(n.log10(xData_10[s_10][::3]), n.log10(yData_10[s_10][::3]), marker ='v', mfc='None',mec='c',ls='none', label="MDPL", rasterized=True)
p.plot(n.log10(xData_25[s_25][::3]), n.log10(yData_25[s_25][::3]), marker ='s', mfc='None',mec='m',ls='none', label="BigMD", rasterized=True)
p.plot(n.log10(xData_40[s_40][::3]), n.log10(yData_40[s_40][::3]), marker ='p', mfc='None',mec='b',ls='none', label="HMD", rasterized=True)

xModel = n.arange(n.min(M200c),n.max(M200c),0.1)
#yModel = vfbis(xModel,res_z0.x)

yModel_CF = vf(xModel, A0, vcut0, a0, b0)

#p.plot(xModel, yModel,'k--',label="model")

p.plot(xModel, yModel_CF,'r--',label="model")

p.xlabel(r'log$_{10}[M_{200c}/(h^{-1}M_\odot)]$')
p.ylabel(r' n(>M)') # log$_{10}[ n(>M)]')
p.legend(loc=3)
p.title(str(A0)+" "+str(vcut0)+" "+str(a0)+" "+str(b0))
p.grid()
p.savefig(join(dir , "M200c-cumulative-function-z0.pdf"))
p.clf()


################################ Model Fits on the cumulative function, evolution with redshift ################################

xData_04,z_04,yData_04,yDataErr_04 = n.loadtxt(join(dir_04, property_dir, type + "-"+ cos +"-"+ qty  +"_ALL_cumulative_MD_0.4Gpc.dat"),unpack=True)
xData_10,z_10,yData_10,yDataErr_10 = n.loadtxt(join(dir_10, property_dir, type + "-"+ cos +"-"+ qty  +"_ALL_cumulative_MD_1Gpc.dat"),unpack=True)
xData_25,z_25,yData_25,yDataErr_25 = n.loadtxt(join(dir_25, property_dir, type + "-"+ cos +"-"+ qty  +"_ALL_cumulative_MD_2.5Gpc.dat"),unpack=True)
xData_40,z_40,yData_40,yDataErr_40 = n.loadtxt(join(dir_40, property_dir, type + "-"+ cos +"-"+ qty  +"_ALL_cumulative_MD_4Gpc.dat"),unpack=True)

s_04 = (z_04 >= 0.0) & (z_04 <= zmax)
s_10 = (z_10 >= 0.0) & (z_10 <= zmax)
s_25 = (z_25 >= 0.0) & (z_25 <= zmax)
s_40 = (z_40 >= 0.0) & (z_40 <= zmax)

redshift = n.hstack(( z_04[s_04], z_10[s_10], z_25[s_25], z_40[s_40]))
print "all redshifts available:", set(redshift)
M200c = n.log10(n.hstack(( xData_04[s_04], xData_10[s_10], xData_25[s_25], xData_40[s_40])))
print "min and max masses available:", n.min(M200c), n.max(M200c)
yData = n.log10(n.hstack(( yData_04[s_04], yData_10[s_10], yData_25[s_25], yData_40[s_40])))
print "min and max Y available:", n.min(yData), n.max(yData)
yDataErr = abs(n.hstack(( yDataErr_04[s_04], yDataErr_10[s_10], yDataErr_25[s_25], yDataErr_40[s_40])) / yData)
print "min and max Y error available:", n.min(yDataErr), n.max(yDataErr)

#vfG = lambda v, z, A0, A1, vcut0, vcut1, b0, b1 : 10**(A0 + A1 * z) * (1+ (v/10**(vcut0 + vcut1 * z))**(b0 + b1 * z) )* n.e**(- (v/10**(vcut0 + vcut1 * z))**(a0 ) )
vfG = lambda v, z, A1, vcut1, a1, b1 : n.log10( 10**(A0 + A1 * z) * (1+ (10**v/10**(vcut0 + vcut1 * z))**(b0 + b1 * z) )* n.e**(- (10**v/10**(vcut0 + vcut1 * z))**(a0 +a1*z) ))
vfGbis = lambda v, z, ps : vfG(v,z,ps[0],ps[1],ps[2],ps[3])
chi2fun = lambda ps : n.sum((vfGbis(M200c,redshift,ps) - yData)**2. ) #/ yDataErr**2. )/len(yDataErr)

p1 = n.array([ 0., 0., 0., 0.])

print "looks for the optimum parameters"
res = minimize(chi2fun, p1, method='Powell',options={'xtol': 1e-6, 'disp': True, 'maxiter' : 50000000, 'nfev': 1800000})

print "ndof=",len(yData)
print res
A1, vcut1, a1, b1 = n.round(res.x,4)

print "A(z) & = "+str(A0)+" + "+str(A1)+r'\times z \\'
print r" M_{cut}(z) & = "+str(vcut0)+" + "+str(vcut1)+r'\times z \\'
print r" \alpha(z) & = "+str(a0)+" + "+str(a1)+r'\times z \\' #+ '+str(a2)+r'\times z^2 \\'
print r" \beta(z) & = "+str(b0)+" + "+str(b1)+r'\times z \\'

# now outputs the model
xModel = n.arange(n.min(M200c),n.max(M200c),0.1)

X,Y = n.meshgrid(xModel,n.arange(0,zmax+0.025,0.025))

Z = vfGbis(X,Y,res.x)

n.savetxt(join(Pdir,"M200c-cumulative-function-best_fit.txt"),n.transpose([n.hstack((X)), n.hstack((Y)), n.hstack((Z))]) )

#######################################################
# now plots the results of the fit
print "now plots the results of the fit"

vmax_mod, z_mod, n_mod = n.loadtxt(join(Pdir,"M200c-cumulative-function-best_fit.txt"), unpack=True)

#####################

fig = p.figure(1,(9,9))
ax = fig.add_subplot(111, projection='3d')

ax.plot_wireframe(X, Y, Z, rstride=10, cstride=10)

sc1 = ax.scatter(M200c, redshift,yData, s=n.ones_like(yData)*3, c='r', marker='o',label="MD data", rasterized=True)
sc1.set_edgecolor('face')

#sc1 = ax.scatter(n.log10(xData_04),z_04,n.log10(yData_04), s=n.ones_like(z_04)*3, c='r', marker='o',label="SMD", rasterized=True)
#sc1.set_edgecolor('face')
#sc1 = ax.scatter(n.log10(xData_10),z_10,n.log10(yData_10), s=n.ones_like(z_10)*3, c='c', marker='v',label="MDPL", rasterized=True)
#sc1.set_edgecolor('face')
#sc1 = ax.scatter(n.log10(xData_25),z_25,n.log10(yData_25), s=n.ones_like(z_25)*3, c='m', marker='s',label="BigMD", rasterized=True)
#sc1.set_edgecolor('face')
#sc1 = ax.scatter(n.log10(xData_40),z_40,n.log10(yData_40), s=n.ones_like(z_40)*3, c='b', marker='p',label="HMD", rasterized=True)
#sc1.set_edgecolor('face')

ax.legend()
ax.set_xlabel(r'log $M_{200c}$ [km s$^{-1}$]')
ax.set_ylabel('redshift')
ax.set_ylim((0,zmax))
ax.set_zlabel(r'log N($>M_{200c}$) [ h$^3$ Mpc$^{-3}$]')
ax.set_zlim((-10,0))
#ax.set_yscale('log')
#ax.set_zscale('log')
p.savefig(join(Pdir , "M200c-cumulative-function-allZ-model.pdf"))
p.clf()

fig = p.figure(1,(9,9))
ax = fig.add_subplot(111, projection='3d')

sc1 = ax.scatter(M200c, redshift, yData/vfGbis(M200c,redshift,res.x), s=n.ones_like(yData)*3, c='r', marker='o',label="MD data", rasterized=True)
sc1.set_edgecolor('face')

#sc1 = ax.scatter(n.log10(xData_04),z_04,yData_04/vfGbis(xData_04,z_04,res.x), s=n.ones_like(z_04)*3, c='r', marker='o',label="SMD", rasterized=True)
#sc1.set_edgecolor('face')
#sc1 = ax.scatter(n.log10(xData_10),z_10,yData_10/vfGbis(xData_10,z_10,res.x), s=n.ones_like(z_10)*3, c='c', marker='v',label="MDPL", rasterized=True)
#sc1.set_edgecolor('face')
#sc1 = ax.scatter(n.log10(xData_25),z_25,yData_25/vfGbis(xData_25,z_25,res.x), s=n.ones_like(z_25)*3, c='m', marker='s',label="BigMD", rasterized=True)
#sc1.set_edgecolor('face')
#sc1 = ax.scatter(n.log10(xData_40),z_40,yData_40/vfGbis(xData_40,z_40,res.x), s=n.ones_like(z_40)*3, c='b', marker='p',label="HMD", rasterized=True)
#sc1.set_edgecolor('face')

ax.legend()
ax.set_xlabel(r'log $M_{200c}$ [km s$^{-1}$]')
ax.set_ylabel('redshift')
ax.set_ylim((0,zmax))
ax.set_zlabel(r'Data / Model')
ax.set_zlim((0.5,1.5))
#ax.set_yscale('log')
#ax.set_zscale('log')
p.savefig(join(Pdir , "M200c-cumulative-function-allZ-modelRatio.pdf"))
p.clf()



sys.exit()
################################ Plot differential halo mass function  ################################


xData_04,z_04,yData_04,yDataErr_04 = n.loadtxt(join(dir_40, property_dir, type + "-"+ cos +"-"+ qty  +"_ALL_differential_MD_4Gpc.dat"),unpack=True)
xData_10,z_10,yData_10,yDataErr_10 = n.loadtxt(join(dir_10, property_dir, type + "-"+ cos +"-"+ qty  +"_ALL_differential_MD_1Gpc"+".dat"),unpack=True)
xData_25,z_25,yData_25,yDataErr_25 = n.loadtxt(join(dir_25, property_dir, type + "-"+ cos +"-"+ qty  +"_ALL_differential_MD_2.5Gpc"+".dat"),unpack=True)
xData_40,z_40,yData_40,yDataErr_40 = n.loadtxt(join(dir_40, property_dir, type + "-"+ cos +"-"+ qty  +"_ALL_differential_MD_4Gpc.dat"),unpack=True)

#rhom_04 = n.array([aa.critical_density(zz).to(uu.solMass*uu.Mpc**-3).value/aa.h**2 for zz in z_04])
#rhom_10 = n.array([aa.critical_density(zz).to(uu.solMass*uu.Mpc**-3).value/aa.h**2 for zz in z_10])
#rhom_25 = n.array([aa.critical_density(zz).to(uu.solMass*uu.Mpc**-3).value/aa.h**2 for zz in z_25])
#rhom_40 = n.array([aa.critical_density(zz).to(uu.solMass*uu.Mpc**-3).value/aa.h**2 for zz in z_40])

rhom_04 = n.array([aa.critical_density(zz).to(uu.solMass*uu.Mpc**-3).value for zz in z_04])
rhom_10 = n.array([aa.critical_density(zz).to(uu.solMass*uu.Mpc**-3).value for zz in z_10])
rhom_25 = n.array([aa.critical_density(zz).to(uu.solMass*uu.Mpc**-3).value for zz in z_25])
rhom_40 = n.array([aa.critical_density(zz).to(uu.solMass*uu.Mpc**-3).value for zz in z_40])

p.figure(0,(6,6))
p.axes([0.17,0.17,0.75,0.75])

#p.plot(n.log10(dat[0]),n.log10(dat[0]*dat[0]*dat[5]),'k--',lw=2)
s_04 = (z_04 <= 0.01)
y_04 = n.log10(yData_04*xData_04**2./rhom_04)
#y_04 = n.log10(yData_04*xData_04*xData_04)
p.plot(n.log10(xData_04[s_04]), y_04[s_04], marker ='o', mfc='None',mec='r',ls='none', label="SMD", rasterized=True)

s_10 = (z_10 == 0)
y_10 = n.log10(yData_10*xData_10**2./rhom_10)
#y_10 = n.log10(yData_10*xData_10*xData_10)
p.plot(n.log10(xData_10[s_10]),y_10[s_10], marker ='v', mfc='None',mec='c',ls='none', label="MDPL", rasterized=True)

s_25 = (z_25 == 0)
y_25 = n.log10(yData_25*xData_25**2./rhom_25)
#y_25 = n.log10(yData_25*xData_25*xData_25)
p.plot(n.log10(xData_25[s_25]),y_25[s_25], marker ='s', mfc='None',mec='m',ls='none', label="BigMD", rasterized=True)

s_40 = (z_40 == 0)
y_40 = n.log10(yData_40*xData_40**2./rhom_40)
#y_40 = n.log10(yData_40*xData_40*xData_40)
p.plot(n.log10(xData_40[s_40]),y_40[s_40], marker ='p', mfc='None',mec='b',ls='none', label="HMD", rasterized=True)

p.xlabel(r'log$_{10}[M_{200c}/(h^{-1}M_\odot)]$')
p.ylabel(r'log$_{10}[(M^2/\rho_m) \; dn/dM]')
p.legend(loc=3)
p.grid()
p.savefig(join(Pdir , "M200c-diff-function-z0.pdf"))
p.clf()

fig = p.figure(1,(9,9))
ax = fig.add_subplot(111, projection='3d')

sc1 = ax.scatter(n.log10(xData_04),z_04,y_04, s=n.ones_like(z_04)*3, c='r', marker='o',label="SMD", rasterized=True)
sc1.set_edgecolor('face')

sc1 = ax.scatter(n.log10(xData_10),z_10,y_10, s=n.ones_like(z_10)*3, c='c', marker='v',label="MDPL", rasterized=True)
sc1.set_edgecolor('face')

sc1 = ax.scatter(n.log10(xData_25),z_25,y_25, s=n.ones_like(z_25)*3, c='m', marker='s',label="BigMD", rasterized=True)
sc1.set_edgecolor('face')

sc1 = ax.scatter(n.log10(xData_40),z_40,y_40, s=n.ones_like(z_40)*3, c='b', marker='p',label="HMD", rasterized=True)
sc1.set_edgecolor('face')

ax.legend()
ax.set_xlabel(r'$log_{10}[M_{200c}/(h^{-1}M_\odot)]$')
ax.set_ylabel('redshift')
ax.set_ylim((0,zmax))
ax.set_zlabel(r'$log_{10}[(M^2/\rho_m) \; dn/dM]$')
ax.set_zlim((-4,0))
p.savefig(join(Pdir , "M200c-diff-function-allZ.pdf"))
p.clf()

