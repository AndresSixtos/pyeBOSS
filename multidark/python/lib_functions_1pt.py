# data modules
import glob
import sys
import astropy.io.fits as fits
import os
from os.path import join
import cPickle
import time
# numerical modules
import numpy as n
from scipy.interpolate import interp1d
from scipy.misc import derivative
from scipy.optimize import minimize
from scipy.optimize import curve_fit

# plotting modules
import matplotlib
matplotlib.use('pdf')
matplotlib.rcParams['font.size']=12
import matplotlib.pyplot as p

# mass function theory
from hmf import MassFunction
from astropy.cosmology import FlatLambdaCDM
import astropy.units as u
cosmo = FlatLambdaCDM(H0=67.77*u.km/u.s/u.Mpc, Om0=0.307115, Ob0=0.048206)

# Fitting functions
# velocity function
vf = lambda v, A, v0, alpha, beta : n.log10( 10**A * (10**v/10**v0)**(-beta) * n.e**(- (10**v/10**v0)**(alpha) ) )

# sheth and tormen function
fnu_ST = lambda nu, A, a, p: A * (2./n.pi)**(0.5) * (a*nu) * ( 1 + (a * nu) **(-2.*p) ) * n.e**( -( a * nu )**2. / 2.) 
log_fnu_ST = lambda logNu, Anorm, a, q : n.log10( fnu_ST(10.**logNu, Anorm, a, q) )
log_fnu_ST_ps = lambda logNu, ps : n.log10( fnu_ST(10.**logNu, ps[0], ps[1], ps[2]) )

p_ST_despali = [0.333, 0.794, 0.247]
p_ST_sheth = [0.3222, 0.707, 0.3]
p_T08_klypin = [0.224, 1.67, 1.80, 1.48]
p_T08_RP = [0.144, 1.351, 3.113, 1.187]

# tinker function 
fsigma_T08 = lambda sigma, A, a, b, c :  A *(1+ (b/sigma)**a) * n.e**(-c/sigma**2.)
log_fsigma_T08 = lambda  logsigma, A, a, b, c :  n.log10(A *(1+ (b/(10**logsigma))**a) * n.e**(-c/(10**logsigma)**2.))
log_fsigma_T08_ps = lambda logsigma, ps : log_fsigma_T08(logsigma, ps[0], ps[1], ps[2], ps[3])

#fnu_SMT = lambda nu, Anorm, a, q : Anorm * (2./n.pi)**(0.5) * (a*nu) * ( 1 + (a*nu) **(-2*q) ) * n.e**( - (a*nu)**2. / 2.) # 
#fnu_SMT = lambda nu, Anorm, a, q : Anorm *a * (2.*n.pi)**(-0.5) *  ( 1 + (a**2*nu) **(-q) ) * n.e**( - a**2*nu / 2.)
#log_fnu_ST01 = lambda logNu, Anorm, a, q : n.log10( fnu_SMT(10.**logNu, Anorm, a, q) )
#log_fnu_ST01_ps = lambda logNu, ps : n.log10( fnu_SMT(10.**logNu, ps[0], ps[1], ps[2]) )

# MULTIDARK TABLE GENERIC FUNCTIONS
mSelection = lambda data, qty, logNpmin : (data["log_"+qty]>data["logMpart"]+logNpmin)
#, limits_04, limits_10, limits_25, limits_40
#((data["boxLength"]==400.)&(data["log_"+qty+"_min"]>limits_04[0]) &(data["log_"+qty+"_max"]<limits_04[1])) | ((data["boxLength"]==1000.)&(data["log_"+qty+"_min"]>limits_10[0]) &(data["log_"+qty+"_max"]<limits_10[1])) |  ((data["boxLength"]==2500.)&(data["log_"+qty+"_min"]>limits_25[0]) &(data["log_"+qty+"_max"]<limits_25[1])) |  ((data["boxLength"]==4000.)&(data["log_"+qty+"_min"]>limits_40[0])&(data["log_"+qty+"_max"]<limits_40[1])) 

zSelection = lambda data, zmin, zmax : (data["redshift"]>zmin)&(data["redshift"]<zmax)

nSelection = lambda data, NminCount, cos : (data['dN_counts_'+cos]>NminCount)

# MVIR 1point FUNCTION 

def plot_mvir_function_data(log_mvir, logsigM1, logNu, log_MF, log_MF_c, redshift, zmin, zmax, cos = "cen", figName="", dir=join(os.environ['MULTIDARK_LIGHTCONE_DIR'], 'mvir')):
	"""
	:param log_mvir: x coordinates
	:param log_VF: y coordinates
	:param redshift: color coordinate
	:param zmin: minimum redshift
	:param zmax: maximum redshift
	:param cos: centra or satelitte. Default: "cen"
	:param figName: string to be added to the figure name. Default:=""
	:param dir: working directory. Default: join( os.environ['MULTIDARK_LIGHTCONE_DIR'], qty), :param qty: quantity studied. Default: 'mvir'
	"""
	# now the plots
	p.figure(0,(6,6))
	p.axes([0.17,0.17,0.75,0.75])
	sc1=p.scatter(logsigM1, log_MF, c=redshift, s=5, marker='o',label="MD "+cos+" data", rasterized=True, vmin=zmin, vmax = zmax)
	sc1.set_edgecolor('face')
	cb = p.colorbar(shrink=0.8)
	cb.set_label("redshift")
	sigs = n.arange(-0.5,.6, 0.01)
	#p.plot(-sigs, log_fsigma_T08_ps(sigs, p_T08_klypin), 'k--', label='K 16 M200c')
	p.plot(-sigs, log_fsigma_T08_ps(sigs, p_T08_RP), 'b--', label='RP 16')
	p.xlabel(r'$ln(\sigma^{-1})$')
	p.ylabel(r'$\log_{10}\left[ \frac{M}{\rho_m} \frac{dn}{d\ln M} \left|\frac{d\ln M }{d\ln \sigma}\right|\right] $') 
	 # log$_{10}[ n(>M)]')
	gl = p.legend(loc=3,fontsize=10)
	gl.set_frame_on(False)
	p.ylim((-3.5,0))
	p.grid()
	p.savefig(join(dir,"mvir-"+figName+cos+"-differential-function-data-xSigma.png"))
	p.clf()
	
	p.figure(0,(6,6))
	p.axes([0.17,0.17,0.75,0.75])
	sc1=p.scatter(logNu, log_MF, c=redshift, s=5, marker='o',label="MD "+cos+" data", rasterized=True, vmin=zmin, vmax = zmax)
	sc1.set_edgecolor('face')
	cb = p.colorbar(shrink=0.8)
	cb.set_label("redshift")
	nus = n.arange(-0.3,1., 0.05)
	p.plot(nus, log_fnu_ST_ps(nus, p_ST_despali), 'k--', label='Despali 16')
	p.plot(nus, log_fnu_ST_ps(nus, p_ST_sheth), 'b--', label='Sheth 01')
	p.xlabel(r'$ln(\nu)$')
	p.ylabel(r'$\log_{10}\left[ \frac{M}{\rho_m} \frac{dn}{d\ln M} \left|\frac{d\ln M }{d\ln \sigma}\right|\right] $') 
	 # log$_{10}[ n(>M)]')
	gl = p.legend(loc=3,fontsize=10)
	gl.set_frame_on(False)
	p.ylim((-3.5,0))
	p.xlim((-0.3, 0.8))
	p.grid()
	p.savefig(join(dir,"mvir-"+figName+cos+"-differential-function-data-xNu.png"))
	p.clf()
	"""
	p.figure(0,(6,6))
	p.axes([0.17,0.17,0.75,0.75])
	sc1=p.scatter(log_mvir, log_MF, c=redshift, s=5, marker='o',label="MD "+cos+" data", rasterized=True, vmin=zmin, vmax = zmax)
	sc1.set_edgecolor('face')
	cb = p.colorbar(shrink=0.8)
	cb.set_label("redshift")
	p.xlabel(r'log$_{10}[M_{vir}/(h^{-1}M_\odot)]$')
	p.ylabel(r'log$_{10} (M^2/\rho_m) dn(M)/dM$') 
	 # log$_{10}[ n(>M)]')
	gl = p.legend(loc=3,fontsize=10)
	gl.set_frame_on(False)
	p.ylim((-4.5,-1))
	p.xlim((9.5,16))
	p.grid()
	p.savefig(join(dir,"mvir-"+figName+cos+"-differential-function-data-xMass.png"))
	p.clf()
	
	p.figure(0,(6,6))
	p.axes([0.17,0.17,0.75,0.75])
	sc1=p.scatter(logsigM1, log_MF, c=redshift, s=5, marker='o',label="MD "+cos+" data", rasterized=True, vmin=zmin, vmax = zmax)
	sc1.set_edgecolor('face')
	cb = p.colorbar(shrink=0.8)
	cb.set_label("redshift")
	p.xlabel(r'$ln(\sigma^{-1})$')
	p.ylabel(r'log$_{10} (M^2/\rho_m) dn(M)/dM$') 
	 # log$_{10}[ n(>M)]')
	gl = p.legend(loc=3,fontsize=10)
	gl.set_frame_on(False)
	p.ylim((-4.5,-1))
	p.grid()
	p.savefig(join(dir,"mvir-"+figName+cos+"-differential-function-data-xSigma.png"))
	p.clf()
	
	p.figure(0,(6,6))
	p.axes([0.17,0.17,0.75,0.75])
	sc1=p.scatter(log_mvir, log_MF_c, c=redshift, s=5, marker='o',label="MD "+cos+" data", rasterized=True, vmin=zmin, vmax = zmax)
	sc1.set_edgecolor('face')
	cb = p.colorbar(shrink=0.8)
	cb.set_label("redshift")
	p.xlabel(r'log$_{10}[M_{vir}/(h^{-1}M_\odot)]$')
	p.ylabel(r'log$_{10} (M^2/\rho_m) n(>M)$') 
	gl = p.legend(loc=3,fontsize=10)
	gl.set_frame_on(False)
	p.ylim((-4.5,-1))
	p.xlim((9.5,16))
	p.grid()
	p.savefig(join(dir,"mvir-"+figName+cos+"-cumulative-function-data-xMass.png"))
	p.clf()
	"""
	
def plot_mvir_function_data_perBox(log_mvir, log_VF, MD04, MD10, MD25, MD25NW, MD40, MD40NW, cos = "cen", figName="", dir=join(os.environ['MULTIDARK_LIGHTCONE_DIR'], 'mvir')):
	"""
	:param log_mvir: x coordinates
	:param log_VF: y coordinates
	:param cos: centra or satelitte. Default: "cen"
	:param figName: string to be added to the figure name. Default:=""
	:param dir: working directory. Default: join( os.environ['MULTIDARK_LIGHTCONE_DIR'], qty), :param qty: quantity studied. Default: 'mvir'
	"""
	p.figure(0,(6,6))
	p.axes([0.17,0.17,0.75,0.75])
	p.plot(log_mvir[MD04], log_VF[MD04],marker='1',label="MD04",ls='')
	p.plot(log_mvir[MD10], log_VF[MD10],marker='2',label="MD10",ls='')
	p.plot(log_mvir[MD25], log_VF[MD25],marker='|',label="MD25",ls='')
	p.plot(log_mvir[MD40], log_VF[MD40],marker='_',label="MD40",ls='')
	p.plot(log_mvir[MD25NW], log_VF[MD25NW],marker='+',label="MD25NW",ls='')
	p.plot(log_mvir[MD40NW], log_VF[MD40NW],marker='x',label="MD40NW",ls='')
	p.xlabel(r'log$_{10}[M_{vir}/(M_\odot)]$')
	p.ylabel(r'$\log_{10}\left[ \frac{M}{\rho_m} \frac{dn}{d\ln M} \left|\frac{d\ln M }{d\ln \sigma}\right|\right] $') 
	gl = p.legend(loc=3,fontsize=10)
	gl.set_frame_on(False)
	p.ylim((-4.5,0))
	p.xlim((9.5,16))
	p.grid()
	p.savefig(join(dir,"mvir-"+figName+cos+"-differential-function-data-perBox.png"))
	p.clf()


def plot_mvir_function_jackknife_poisson_error(x, y, MD04, MD10, MD25, MD25NW, MD40, MD40NW, cos = "cen", dir=join(os.environ['MULTIDARK_LIGHTCONE_DIR'], 'mvir')):
	"""
	:param x: x coordinates
	:param y: y coordinates
	:param cos: centra or satelitte. Default: "cen"
	:param dir: working directory. Default: join( os.environ['MULTIDARK_LIGHTCONE_DIR'], qty), :param qty: quantity studied. Default: 'mvir'
	"""
	p.figure(0,(6,6))
	p.axes([0.17,0.17,0.75,0.75])
	p.plot(x, y, 'ko', label='all', alpha=0.01)
	p.plot(x[MD04], y[MD04],marker='x',label="MD04",ls='')
	p.plot(x[MD10], y[MD10],marker='+',label="MD10",ls='')
	p.plot(x[MD25], y[MD25],marker='^',label="MD25",ls='')
	p.plot(x[MD40], y[MD40],marker='v',label="MD40",ls='')
	p.plot(x[MD25NW], y[MD25NW],marker='^',label="MD25NW",ls='')
	p.plot(x[MD40NW], y[MD40NW],marker='v',label="MD40NW",ls='')
	xx = n.logspace(-4,0,20)
	p.plot(xx, xx*3., ls='--', label='y=3x')
	#p.axhline(Npmin**-0.5, c='r', ls='--', label='min counts cut')#r'$1/\sqrt{10^3}$')
	#p.axhline((10**6.87)**-0.5, c='k', ls='--', label='min mvir cut')#r'$1/\sqrt{10^{4.87}}$')
	#p.xlim((2e-4,4e-1))
	#p.ylim((2e-4,4e-1))
	p.ylabel(r'$1/\sqrt{count} \; [\%]$')
	p.xlabel(r'Jackknife  Resampling Error [%]')
	p.yscale('log')
	p.xscale('log')
	gl = p.legend(loc=0,fontsize=10)
	gl.set_frame_on(False)
	p.grid()
	p.savefig(join(dir,"mvir-"+cos+"-jackknife-countsSqrt.png"))
	p.clf()

def plot_mvir_function_data_error(log_mvir, error, redshift, label, zmin, zmax, cos = "cen", figName="mvir-cen-data04-uncertainty.png", dir=join(os.environ['MULTIDARK_LIGHTCONE_DIR'], 'mvir')):
	"""
	:param log_mvir: x coordinates
	:param error: y coordinates
	:param redshift: color coordinate
	:param label: label in the caption
	:param zmin: minimum redshift
	:param zmax: maximum redshift
	:param cos: centra or satelitte. Default: "cen"
	:param figName: string to be added to the figure name. Default:=""
	:param dir: working directory. Default: join( os.environ['MULTIDARK_LIGHTCONE_DIR'], qty), :param qty: quantity studied. Default: 'mvir'
	"""
	p.figure(0,(6,6))
	p.axes([0.17,0.17,0.75,0.75])
	sc1=p.scatter(log_mvir, 100*error, c=redshift, s=5, marker='o',label=label, rasterized=True, vmin=zmin, vmax = zmax)
	sc1.set_edgecolor('face')
	cb = p.colorbar(shrink=0.8)
	cb.set_label("redshift")
	p.xlabel(r'log$_{10}[V_{max}/(km \; s^{-1})]$')
	p.ylabel(r'JK relative error [%]') 
	gl = p.legend(loc=3,fontsize=10)
	gl.set_frame_on(False)
	p.ylim((2e-2,30))
	#p.xlim((1.5, 3.5))
	p.yscale('log')
	p.grid()
	p.savefig(join(dir,figName))
	p.clf()

def fit_mvir_function_z0(data, x_data, y_data , y_err, p0, 	tolerance = 0.03, cos = "cen", dir=join(os.environ['MULTIDARK_LIGHTCONE_DIR'], 'mvir')):
	"""
	Fits a function to the mvir data
	:param data: data table of the selected points for the fit
	:param x_data: x coordinate
	:param y_data: y coordinate
	:param y_err: error
	:param p0: first guess
	:param tolerance: percentage error tolerance to compute how many points are outside of the fit
	:param cos: central or satelitte
	:param mode: fitting mode, "curve_fit" or "minimize"
	:param dir: working dir
	:param qty: mvir here
	:return: result of the fit: best parameter array and covariance matrix
	produces a plot of the residuals
	"""
	pOpt, pCov=curve_fit(log_fnu_ST, x_data, y_data, p0, y_err, maxfev=500000)#, bounds=boundaries)
	print "best params=", pOpt
	print "err=", pCov.diagonal()**0.5
		
	x_model = n.arange(n.min(x_data),n.max(x_data),0.005)
	y_model = log_fnu_ST(x_model, pOpt[0], pOpt[1], pOpt[2])
	n.savetxt(join(dir,"mvir-"+cos+"-differential-function-z0-model-pts.txt"),n.transpose([x_model, y_model]) )
	outfile=open(join(dir,"mvir-"+cos+"-diff-function-z0-params.pkl"), 'w')
	cPickle.dump([pOpt, pCov], outfile)
	outfile.close()
			
	f_diff =  y_data - log_fnu_ST(x_data, pOpt[0], pOpt[1], pOpt[2])

	MD_sel_fun=lambda name : (data["boxName"]==name)
	MDnames= n.array(['MD_0.4Gpc', 'MD_1Gpc', 'MD_2.5Gpc','MD_4Gpc','MD_2.5GpcNW','MD_4GpcNW'])
	MDsels=n.array([MD_sel_fun(name) for name in MDnames])

	f_diff_fun = lambda MDs:  y_data[MDs] - log_fnu_ST(x_data[MDs], pOpt[0], pOpt[1], pOpt[2])
	f_diffs = n.array([f_diff_fun(MD) for MD in MDsels])

	print "================================"

	# now the plots
	p.figure(0,(6,6))
	p.axes([0.17,0.17,0.75,0.75])
	for index, fd in enumerate(f_diffs):
		inTol = (abs(10**fd-1)<tolerance)
		print index
		if len(fd)>0:
			p.errorbar(x_data[MDsels[index]], 10**fd, yerr = y_err[MDsels[index]] , rasterized=True, fmt='none', label=MDnames[index])
			print len(inTol.nonzero()[0]), len(fd), 100.*len(inTol.nonzero()[0])/ len(fd)

	p.axhline(1.01,c='k',ls='--',label=r'syst $\pm1\%$')
	p.axhline(0.99,c='k',ls='--')
	p.xlabel(r'$log_{10}(\nu)$')
	p.ylabel(r'data/model') 
	gl = p.legend(loc=0,fontsize=10)
	gl.set_frame_on(False)
	#p.xlim((-0.7,0.6))
	p.ylim((0.92,1.08))
	#p.yscale('log')
	p.grid()
	p.savefig(join(dir,"fit-"+cos+"-differential-function-residual-log.png"))
	p.clf()
	return pOpt, pCov

# VMAX 1point FUNCTION 
def plot_jackknife_poisson_error(x, y, MD04, MD10, MD25, MD25NW, MD40, MD40NW, cos = "cen", dir=join(os.environ['MULTIDARK_LIGHTCONE_DIR'], 'vmax')):
	"""
	:param x: x coordinates
	:param y: y coordinates
	:param cos: centra or satelitte. Default: "cen"
	:param dir: working directory. Default: join( os.environ['MULTIDARK_LIGHTCONE_DIR'], qty), :param qty: quantity studied. Default: 'vmax'
	"""
	p.figure(0,(6,6))
	p.axes([0.17,0.17,0.75,0.75])
	p.plot(x, y, 'ko', label='all', alpha=0.01)
	p.plot(x[MD04], y[MD04],marker='x',label="MD04",ls='')
	p.plot(x[MD10], y[MD10],marker='+',label="MD10",ls='')
	p.plot(x[MD25], y[MD25],marker='^',label="MD25",ls='')
	p.plot(x[MD40], y[MD40],marker='v',label="MD40",ls='')
	p.plot(x[MD25NW], y[MD25NW],marker='^',label="MD25NW",ls='')
	p.plot(x[MD40NW], y[MD40NW],marker='v',label="MD40NW",ls='')
	xx = n.logspace(-4,0,20)
	p.plot(xx, xx*3., ls='--', label='y=3x')
	#p.axhline(Npmin**-0.5, c='r', ls='--', label='min counts cut')#r'$1/\sqrt{10^3}$')
	#p.axhline((10**6.87)**-0.5, c='k', ls='--', label='min vmax cut')#r'$1/\sqrt{10^{4.87}}$')
	p.xlim((1e-4,1))
	p.ylim((1e-4,1))
	p.ylabel(r'$1/\sqrt{count} \; [\%]$')
	p.xlabel(r'Jackknife  Resampling Error [%]')
	p.yscale('log')
	p.xscale('log')
	gl = p.legend(loc=0,fontsize=10)
	gl.set_frame_on(False)
	p.grid()
	p.savefig(join(dir,"jackknife-countsSqrt-"+cos+".png"))
	p.clf()


def fit_mvir_function_zTrend(data, x_data, y_data, z_data , y_err, ps0=[0., 0., 0.], 	tolerance = 0.03, cos = "cen", mode = "curve_fit", dir=join(os.environ['MULTIDARK_LIGHTCONE_DIR'], 'mvir'), zmin=0, zmax=2.5):
	"""
	Fits a function to the mvir data
	:param data: data table of the selected points for the fit
	:param x_data: x coordinate
	:param y_data: y coordinate
	:param z_data: redshift coordinate
	:param y_err: error
	:param ps0: first guess
	:param tolerance: percentage error tolerance to compute how many points are outside of the fit
	:param cos: central or satelitte
	:param mode: fitting mode, "curve_fit" or "minimize"
	:param dir: working dir
	:param qty: mvir here
	:return: result of the fit: best parameter array and covariance matrix
	produces a plot of the residuals
	"""
	outfile=open(join(dir,"mvir-"+cos+"-diff-function-z0-params.pkl"), 'r')
	pOpt, pCov = cPickle.load(outfile)
	outfile.close()
	A0, a0, p0 = pOpt
	
	Az = lambda z, A1 : A0+z*A1
	az = lambda z, a1 : a0+z*a1
	pz = lambda z, p1 : p0+z*p1
	delta_c=1.686
	Anorm0=0.333
	fnu_SMT = lambda nu, Anorm, a, q : Anorm * (2./n.pi)**(0.5) * (a*nu) * ( 1 + (a*nu) **(-2*q) ) * n.e**( - (a*nu)**2. / 2.) 
	log_fnu_ST01 = lambda logNu, Anorm, a, q : n.log10( fnu_SMT(10.**logNu, Anorm, a, q) )
	log_fnu_ST01_ps = lambda logSigma, ps : n.log10( fnu_SMT(10.**logNu, ps[0], ps[1], ps[2]) )
	
	f_SMT_z = lambda sigma, z, A1, a1, p1: Az(z, A1) * (2.*az(z, a1)/n.pi)**(0.5) * ( 1 + ((delta_c/sigma)**2./az(z, a1)) **(pz(z, p1)) ) * n.e**( - az(z, a1) * (delta_c/sigma)**2. / 2.) * (delta_c/sigma)

	log_f_ST01_zt_ps = lambda logSigma, z, ps : n.log10( f_SMT_z(10.**logSigma, z, ps[0], ps[1], ps[2]) )

	print "mode: minimize"
	chi2fun = lambda ps : n.sum( (log_f_ST01_zt_ps(x_data, z_data, ps) - y_data)**2. / (y_err)**2. )/(len(y_data) - len(ps0))
	res = minimize(chi2fun, ps0, method='Powell',options={'xtol': 1e-8, 'disp': True, 'maxiter' : 5000000000000})
	pOpt = res.x
	pCov = res.direc
	print "best params=",pOpt
	print "err=",pCov.diagonal()**0.5 
		
	#x_model = n.arange(n.min(x_data),n.max(x_data),0.005)
	#y_model = log_f_ST01_zt_ps(x_model, pOpt)
	#n.savetxt(join(dir,"mvir-"+cos+"-differential-function-zTrend-model-pts.txt"),n.transpose([x_model, y_model]) )
	outfile=open(join(dir,"mvir-"+cos+"-diff-function-zTrend-params.pkl"), 'w')
	cPickle.dump([pOpt, pCov], outfile)
	outfile.close()
			
	f_diff =  y_data - log_f_ST01_zt_ps(x_data, z_data, pOpt)
	
	MD_sel_fun=lambda name : (data["boxName"]==name)
	MDnames= n.array(['MD_0.4Gpc', 'MD_1Gpc', 'MD_2.5Gpc','MD_4Gpc','MD_2.5GpcNW','MD_4GpcNW'])
	MDsels=n.array([MD_sel_fun(name) for name in MDnames])
	
	f_diff_fun = lambda MDs:  y_data[MDs] - log_f_ST01_zt_ps(x_data[MDs], z_data[MDs], pOpt)
	f_diffs = n.array([f_diff_fun(MD) for MD in MDsels])
	
	print "================================"
	
	# now the plots
	p.figure(0,(6,6))
	p.axes([0.17,0.17,0.75,0.75])
	for index, fd in enumerate(f_diffs):
		inTol = (abs(10**fd-1)<tolerance)
		print index
		if len(fd)>0:
			p.errorbar(x_data[MDsels[index]], 10**fd, yerr = y_err[MDsels[index]] , rasterized=True, fmt='none', label=MDnames[index])
			print len(inTol.nonzero()[0]), len(fd), 100.*len(inTol.nonzero()[0])/ len(fd)

	p.axhline(1.01,c='k',ls='--',label=r'syst $\pm1\%$')
	p.axhline(0.99,c='k',ls='--')
	p.xlabel(r'$log_{10}(\sigma)$')
	p.ylabel(r'data/model') 
	gl = p.legend(loc=0,fontsize=10)
	gl.set_frame_on(False)
	#p.xlim((-0.7,0.6))
	p.ylim((0.9,1.1))
	#p.yscale('log')
	p.grid()
	p.savefig(join(dir,"mvir-"+cos+"-differential-function-fit-ztrend-residual-log.png"))
	p.clf()
	p.figure(1,(6,6))
	p.axes([0.17,0.17,0.75,0.75])
	sc1=p.scatter(x_data, log_f_ST01_zt_ps(x_data, z_data, pOpt), c=z_data, s=5, marker='o',label="MD "+cos+" model", rasterized=True, vmin=zmin, vmax = zmax)
	sc1.set_edgecolor('face')
	cb = p.colorbar(shrink=0.8)
	cb.set_label("redshift")
	p.xlabel(r'$log_{10}(\sigma)$')
	p.ylabel(r'model Mvir Function') 
	gl = p.legend(loc=0,fontsize=10)
	gl.set_frame_on(False)
	p.grid()
	p.savefig(join(dir,"mvir-"+cos+"-differential-function-fit-ztrend-model.png"))
	p.clf()
	return pOpt, pCov

def plot_vmax_function_data_error(log_vmax, error, redshift, label, zmin, zmax, cos = "cen", figName="vmax-cen-data04-uncertainty.png", dir=join(os.environ['MULTIDARK_LIGHTCONE_DIR'], 'vmax')):
	"""
	:param log_vmax: x coordinates
	:param error: y coordinates
	:param redshift: color coordinate
	:param label: label in the caption
	:param zmin: minimum redshift
	:param zmax: maximum redshift
	:param cos: centra or satelitte. Default: "cen"
	:param figName: string to be added to the figure name. Default:=""
	:param dir: working directory. Default: join( os.environ['MULTIDARK_LIGHTCONE_DIR'], qty), :param qty: quantity studied. Default: 'vmax'
	"""
	p.figure(0,(6,6))
	p.axes([0.17,0.17,0.75,0.75])
	sc1=p.scatter(log_vmax, 100*error, c=redshift, s=5, marker='o',label=label, rasterized=True, vmin=zmin, vmax = zmax)
	sc1.set_edgecolor('face')
	cb = p.colorbar(shrink=0.8)
	cb.set_label("redshift")
	p.xlabel(r'log$_{10}[V_{max}/(km \; s^{-1})]$')
	p.ylabel(r'JK relative error [%]') 
	gl = p.legend(loc=3,fontsize=10)
	gl.set_frame_on(False)
	p.ylim((2e-2,30))
	#p.xlim((1.5, 3.5))
	p.yscale('log')
	p.grid()
	p.savefig(join(dir,figName))
	p.clf()

def plot_vmax_function_data(log_vmax, log_VF, log_VF_c, redshift, zmin, zmax, cos = "cen", figName="", dir=join(os.environ['MULTIDARK_LIGHTCONE_DIR'], 'vmax')):
	"""
	:param log_vmax: x coordinates
	:param log_VF: y coordinates
	:param redshift: color coordinate
	:param zmin: minimum redshift
	:param zmax: maximum redshift
	:param cos: centra or satelitte. Default: "cen"
	:param figName: string to be added to the figure name. Default:=""
	:param dir: working directory. Default: join( os.environ['MULTIDARK_LIGHTCONE_DIR'], qty), :param qty: quantity studied. Default: 'vmax'
	"""
	# now the plots
	p.figure(0,(6,6))
	p.axes([0.17,0.17,0.75,0.75])
	sc1=p.scatter(log_vmax, log_VF, c=redshift, s=5, marker='o',label="MD "+cos+" data", rasterized=True, vmin=zmin, vmax = zmax)
	sc1.set_edgecolor('face')
	cb = p.colorbar(shrink=0.8)
	cb.set_label("redshift")
	p.xlabel(r'log$_{10}[V_{max}/(km \; s^{-1})]$')
	p.ylabel(r'log$_{10} [(V^3/H^3(z)\; dn(V)/dlnV]$') # log$_{10}[ n(>M)]')
	gl = p.legend(loc=3,fontsize=10)
	gl.set_frame_on(False)
	p.ylim((-5.5,0))
	#p.xlim((1.5, 3.5))
	#p.ylim((-3.5,-1))
	p.grid()
	p.savefig(join(dir,"vmax-"+figName+cos+"-differential-function-data.png"))
	p.clf()
	
	p.figure(0,(6,6))
	p.axes([0.17,0.17,0.75,0.75])
	sc1=p.scatter(log_vmax, log_VF_c, c=redshift, s=5, marker='o',label="MD "+cos+" data", rasterized=True, vmin=zmin, vmax = zmax)
	sc1.set_edgecolor('face')
	cb = p.colorbar(shrink=0.8)
	cb.set_label("redshift")
	p.xlabel(r'log$_{10}[V_{max}/(km \; s^{-1})]$')
	p.ylabel(r'log$_{10} [V^3/H^3(z)\; n(>V)]$') # log$_{10}[ n(>M)]')
	gl = p.legend(loc=3,fontsize=10)
	gl.set_frame_on(False)
	#p.ylim((-8,1))
	#p.xlim((1.5, 3.5))
	#p.yscale('log')
	p.grid()
	p.savefig(join(dir,"vmax-"+figName+cos+"-cumulative-function-data.png"))
	p.clf()

def plot_vmax_function_data_perBox(log_vmax, log_VF, log_VF_c, MD04, MD10, MD25, MD25NW, MD40, MD40NW, cos = "cen", figName="", dir=join(os.environ['MULTIDARK_LIGHTCONE_DIR'], 'vmax')):
	"""
	:param log_vmax: x coordinates
	:param log_VF: y coordinates
	:param cos: centra or satelitte. Default: "cen"
	:param figName: string to be added to the figure name. Default:=""
	:param dir: working directory. Default: join( os.environ['MULTIDARK_LIGHTCONE_DIR'], qty), :param qty: quantity studied. Default: 'vmax'
	"""
	# now the plots
	p.figure(0,(6,6))
	p.axes([0.17,0.17,0.75,0.75])
	p.plot(log_vmax[MD04], log_VF[MD04],marker='1',label="MD04",ls='')
	p.plot(log_vmax[MD10], log_VF[MD10],marker='2',label="MD10",ls='')
	p.plot(log_vmax[MD25], log_VF[MD25],marker='|',label="MD25",ls='')
	p.plot(log_vmax[MD40], log_VF[MD40],marker='_',label="MD40",ls='')
	p.plot(log_vmax[MD25NW], log_VF[MD25NW],marker='+',label="MD25NW",ls='')
	p.plot(log_vmax[MD40NW], log_VF[MD40NW],marker='x',label="MD40NW",ls='')
	p.xlabel(r'log$_{10}[V_{max}/(km \; s^{-1})]$')
	p.ylabel(r'log$_{10} [(V^3/H^3(z)\; dn(V)/dlnV]$') # log$_{10}[ n(>M)]')
	gl = p.legend(loc=3,fontsize=10)
	gl.set_frame_on(False)
	#p.ylim((-8,1))
	#p.xlim((1.5, 3.5))
	p.ylim((-5.5,0))
	p.grid()
	p.savefig(join(dir,"vmax-"+figName+cos+"-differential-function-data-perBox.png"))
	p.clf()

def fit_vmax_function_z0(data, x_data, y_data , y_err, p0, 	tolerance = 0.03, cos = "cen", mode = "curve_fit", dir=join(os.environ['MULTIDARK_LIGHTCONE_DIR'], 'vmax')):
	"""
	Fits a function to the vmax data
	:param data: data table of the selected points for the fit
	:param x_data: x coordinate
	:param y_data: y coordinate
	:param y_err: error
	:param p0: first guess
	:param tolerance: percentage error tolerance to compute how many points are outside of the fit
	:param cos: central or satelitte
	:param mode: fitting mode, "curve_fit" or "minimize"
	:param dir: working dir
	:param qty: vmax here
	:return: result of the fit: best parameter array and covariance matrix
	produces a plot of the residuals
	"""
	if mode == "curve_fit":
		print "mode: curve_fit"
		pOpt, pCov=curve_fit(vf, x_data, y_data, p0, y_err, maxfev=500000)#, bounds=boundaries)
		print "best params=",pOpt[0], pOpt[1], pOpt[2], pOpt[3]
		print "err=",pCov[0][0]**0.5, pCov[1][1]**0.5, pCov[2][2]**0.5, pCov[3][3]**0.5
		
	if mode == "minimize":
		print "mode: minimize"
		chi2fun = lambda ps : n.sum( (vf(x_data, ps) - y_data)**2. / (y_err)**2. )/(len(y_data) - len(ps))
		res = minimize(chi2fun, p0, method='Powell',options={'xtol': 1e-8, 'disp': True, 'maxiter' : 5000000000000})
		pOpt = res.x
		pCov = res.direc
		print "best params=",pOpt[0], pOpt[1], pOpt[2], pOpt[3]
		print "err=",pCov[0][0]**0.5, pCov[1][1]**0.5, pCov[2][2]**0.5, pCov[3][3]**0.5
		
	x_model = n.arange(n.min(x_data),n.max(x_data),0.005)
	y_model = vf(x_model, pOpt[0], pOpt[1], pOpt[2], pOpt[3])
	n.savetxt(join(dir,"vmax-"+cos+"-differential-function-z0-model-pts.txt"),n.transpose([x_model, y_model]) )
	outfile=open(join(dir,"vmax-"+cos+"-diff-function-z0-params.pkl"), 'w')
	cPickle.dump([pOpt, pCov], outfile)
	outfile.close()
			
	f_diff =  y_data - vf(x_data, pOpt[0], pOpt[1], pOpt[2], pOpt[3])
	
	MD_sel_fun=lambda name : (data["boxName"]==name)
	MDnames= n.array(['MD_0.4Gpc', 'MD_1Gpc', 'MD_2.5Gpc','MD_4Gpc','MD_2.5GpcNW','MD_4GpcNW'])
	MDsels=n.array([MD_sel_fun(name) for name in MDnames])
	
	f_diff_fun = lambda MDs:  y_data[MDs] - vf(x_data[MDs], pOpt[0], pOpt[1], pOpt[2], pOpt[3])
	f_diffs = n.array([f_diff_fun(MD) for MD in MDsels])
	
	print "================================"
	
	# now the plots
	p.figure(0,(6,6))
	p.axes([0.17,0.17,0.75,0.75])
	for index, fd in enumerate(f_diffs):
		inTol = (abs(10**fd-1)<tolerance)
		print index
		if len(fd)>0:
			p.errorbar(x_data[MDsels[index]], 10**fd, yerr = y_err[MDsels[index]] , rasterized=True, fmt='none', label=MDnames[index])
			print len(inTol.nonzero()[0]), len(fd), 100.*len(inTol.nonzero()[0])/ len(fd)

	p.axhline(1.01,c='k',ls='--',label=r'syst $\pm1\%$')
	p.axhline(0.99,c='k',ls='--')
	p.xlabel(r'$log(V_{max})$')
	p.ylabel(r'data/model') 
	gl = p.legend(loc=0,fontsize=10)
	gl.set_frame_on(False)
	#p.xlim((-0.7,0.6))
	#p.ylim((-0.05,0.05))
	#p.yscale('log')
	p.grid()
	p.savefig(join(dir,"vmax-"+cos+"-differential-function-fit-residual-log.png"))
	p.clf()
	return pOpt, pCov

# MULTIDARK DATA OUTPUT HANDLING
def getStat(file,volume,unitVolume):
	"""
	From the pickle file output by the Multidark class, we output the number counts (differential and cumulative) per unit volume per mass bin.
	:param file: filename
	:param volume: total volume of the box
	:param unitVolume: sub volume used in the jackknife
	:return: Number counts, cumulative number counts, count density, cumulative count density, jackknife mean, jackknife std, cumulative jackknife mean, cumulative jackknife std
	"""
	# print file
	data=cPickle.load(open(file,'r'))
	data_c = n.array([n.array([ n.sum(el[ii:]) for ii in range(len(el)) ]) for el in data])
	Ncounts = data.sum(axis=0) 
	Ncounts_c = data_c.sum(axis=0) # n.array([ n.sum(Ncounts[ii:]) for ii in range(len(Ncounts)) ])
	Nall = Ncounts / volume
	Nall_c = Ncounts_c / volume
	index=n.arange(int(data.shape[0]))
	n.random.shuffle( index )
	Ntotal = int(data.shape[0])
	# discard 100
	def get_mean_std( pcDiscard = 0.1):
		"""
		retrieves the mean and std from the jackknife
		:param pcDiscard:percentage to discard for the jackknife
		:return: mean, std, cumulative mean90 and cumulative std
		"""
		Ndiscard = Ntotal * pcDiscard
		resamp = n.arange(0,Ntotal+1, Ndiscard)
		N90 = n.array([n.sum(data[n.delete(n.arange(Ntotal), index[resamp[i]:resamp[i+1]])], axis=0) for i in range(len(resamp)-1)]) / (unitVolume*(Ntotal - Ndiscard) )
		mean90 = n.mean(N90, axis=0)
		std90 = n.std(N90, axis=0) / mean90
		N90_c = n.array([n.sum(data_c[n.delete(n.arange(Ntotal), index[resamp[i]:resamp[i+1]])], axis=0) for i in range(len(resamp)-1)]) / (unitVolume*(Ntotal - Ndiscard) )
		mean90_c = n.mean(N90_c, axis=0)
		std90_c = n.std(N90_c, axis=0) / mean90_c
		return mean90, std90, mean90_c, std90_c

	mean90, std90, mean90_c, std90_c = get_mean_std(0.1)
	#mean99, std99, mean99_c, std99_c = getMS(0.01)
	sel = Nall>1/volume
	# print std99[sel]/std90[sel]
	# print mean90[sel]/mean99[sel]
	# print Nall[sel]/mean99[sel]
	# print Nall[sel]/mean90[sel]
	return Ncounts, Ncounts_c, Nall, Nall_c, mean90, std90, mean90_c, std90_c
	
def get_hf(sigma_val=0.8228, boxRedshift=0., delta_wrt='mean'):
	#hf0 = MassFunction(cosmo_model=cosmo, sigma_8=sigma_val, z=boxRedshift)
	omega = lambda zz: cosmo.Om0*(1+zz)**3. / cosmo.efunc(zz)**2
	DeltaVir_bn98 = lambda zz : (18.*n.pi**2. + 82.*(omega(zz)-1)- 39.*(omega(zz)-1)**2.)/omega(zz)
	print "DeltaVir", DeltaVir_bn98(boxRedshift), " at z",boxRedshift
	hf1 = MassFunction(cosmo_model=cosmo, sigma_8=sigma_val, z=boxRedshift, delta_h=DeltaVir_bn98(boxRedshift), delta_wrt=delta_wrt, Mmin=7, Mmax=16.5)
	return hf1

def get_basic_info(fileC, boxZN, delta_wrt='mean'):
	if fileC.find('MD_0.4Gpc')>0:
		boxName='MD_0.4Gpc'
		nSN, aSN = n.loadtxt(join(os.environ['MD04_DIR'],"redshift-list.txt"), unpack=True, dtype={'names': ('nSN', 'aSN'), 'formats': ('i4', 'f4')})
		conversion = dict(n.transpose([ nSN, 1/aSN-1 ]))
		boxRedshift =  conversion[boxZN] 
		hf = get_hf(0.8228*0.953**0.5, boxRedshift, delta_wrt=delta_wrt)
		logmp = n.log10(9.63 * 10**7/cosmo.h)
		boxLength = 400./cosmo.h/cosmo.efunc(boxRedshift)
		massCorrection = 1. - 0.0002
		
	elif fileC.find('MD_1Gpc')>0 :
		boxName='MD_1Gpc'
		nSN, aSN = n.loadtxt(join(os.environ['MD10_DIR'],"redshift-list.txt"), unpack=True, dtype={'names': ('nSN', 'aSN'), 'formats': ('i4', 'f4')})
		conversion = dict(n.transpose([ nSN, 1/aSN-1 ]))
		boxRedshift =  conversion[boxZN] 
		#boxRedshift = 1./boxZN - 1.
		hf = get_hf(0.8228*1.004**0.5, boxRedshift, delta_wrt=delta_wrt)
		logmp = n.log10(1.51 * 10**9/cosmo.h)
		boxLength = 1000./cosmo.h/cosmo.efunc(boxRedshift)
		massCorrection = 1. - 0.0005

	elif fileC.find('MD_2.5GpcNW')>0 :
		boxName='MD_2.5GpcNW'
		nSN, aSN = n.loadtxt(join(os.environ['MD25NW_DIR'],"redshift-list.txt"), unpack=True, dtype={'names': ('nSN', 'aSN'), 'formats': ('i4', 'f4')})
		conversion = dict(n.transpose([ nSN, 1/aSN-1 ]))
		boxRedshift =  conversion[boxZN] 
		hf = get_hf(0.8228*1.01**0.5, boxRedshift, delta_wrt=delta_wrt)
		hz = 1.# hf.cosmo.H( boxRedshift ).value / 100.
		logmp = n.log10(2.359 * 10**10/cosmo.h )
		boxLength = 2500./cosmo.h/cosmo.efunc(boxRedshift)
		massCorrection = 1. - 0.001

	elif fileC.find('MD_4GpcNW')>0 :
		boxName='MD_4GpcNW'
		nSN, redshift40, aSN = n.loadtxt(join(os.environ['MD40NW_DIR'],"redshift-list.txt"), unpack=True, dtype={'names': ('nSN', 'redshift', 'aSN'), 'formats': ('i4', 'f4', 'f4')})
		conversion = dict(n.transpose([ nSN, redshift40 ]))
		boxRedshift =  conversion[boxZN] 
		hf = get_hf(0.8228*1.008**0.5, boxRedshift, delta_wrt=delta_wrt)
		hz = 1.# hf.cosmo.H( boxRedshift ).value / 100. 
		logmp = n.log10(9.6 * 10**10/cosmo.h )
		boxLength = 4000./cosmo.h/cosmo.efunc(boxRedshift)
		massCorrection = 1. - 0.003
	
	elif fileC.find('MD_2.5Gpc')>0 :
		boxName='MD_2.5Gpc'
		nSN, aSN, redshift25 = n.loadtxt(join(os.environ['MD25_DIR'],"redshift-list.txt"), unpack=True, dtype={'names': ('nSN', 'aSN', 'redshift'), 'formats': ('i4', 'f4', 'f4')})
		conversion = dict(n.transpose([ nSN, redshift25 ]))
		boxRedshift =  conversion[boxZN] 
		hf = get_hf(0.8228*1.01**0.5, boxRedshift, delta_wrt=delta_wrt)
		hz = 1.# hf.cosmo.H( boxRedshift ).value / 100.
		logmp = n.log10(2.359 * 10**10/cosmo.h)
		boxLength = 2500./cosmo.h/cosmo.efunc(boxRedshift)
		massCorrection = 1. - 0.001

	elif fileC.find('MD_4Gpc')>0 :
		boxName='MD_4Gpc'
		nSN, redshift40, aSN = n.loadtxt(join(os.environ['MD40_DIR'],"redshift-list.txt"), unpack=True, dtype={'names': ('nSN', 'redshift', 'aSN'), 'formats': ('i4', 'f4', 'f4')})
		conversion = dict(n.transpose([ nSN, redshift40 ]))
		boxRedshift =  conversion[boxZN] 
		hf = get_hf(0.8228*1.008**0.5, boxRedshift, delta_wrt=delta_wrt)
		hz = 1.# hf.cosmo.H( boxRedshift ).value / 100.
		logmp = n.log10(9.6 * 10**10 /cosmo.h )
		boxLength = 4000./cosmo.h/cosmo.efunc(boxRedshift)
		massCorrection = 1. - 0.003
	
	boxLengthComoving = boxLength * cosmo.efunc(boxRedshift)
	return hf, boxLength, boxName, boxRedshift, logmp, boxLengthComoving, massCorrection

def convert_pkl_mass(fileC, fileS, binFile, qty='mvir', delta_wrt='mean'):
	"""
	:param qty: one point function variable.Default: mvir.
	:param fileC: file with the central halo statistics
	:param fileS: file with the satelitte halo statistics
	:param binFile: file with the bins
	:return: a fits table containing the one point function histograms
	"""
	print "qty", qty
	boxZN = float(os.path.basename(fileC).split('_')[1])
	print boxZN
	extraName =  os.path.basename(fileS)[:-27]
	hf, boxLength, boxName, boxRedshift, logmp, boxLengthComoving, massCorrection = get_basic_info(fileC, boxZN, delta_wrt='mean')
	
	print boxName
	bins = n.log10( 10**n.loadtxt(binFile) * massCorrection )
	#bins = n.log10( 10**bins_in / hz )
	#bins = n.loadtxt(binFile)
	logmass = ( bins[1:]  + bins[:-1] )/2.
	mass = 10**logmass 
	dX = ( 10**bins[1:]  - 10**bins[:-1] )
	#dlnbin = dX / mass
	dlnbin = (bins[1:]  - bins[:-1])*n.log(10)
	#print dX / mass, dlnbin
	#selects meaningful masses 10 times particle mass
	ok = (logmass > logmp+1.0)&(logmass<16.1)
	print "bins", len(bins), bins
	print "bins[ok]", len(bins[:-1][ok]), bins[:-1][ok]
	hz = cosmo.H( boxRedshift ).value / 100.
	# m sigma relation using the sigma8 corrected power spectrum
	m2sigma = interp1d(hf.M, hf.sigma )
	sig = m2sigma( mass )
	# m nu relation: nu = (delta_c / sigma_m)**2
	m2nu = interp1d(hf.M, hf.nu )
	nnu = m2nu( mass )
	# jacobian
	toderive = interp1d(n.log(hf.M), n.log(hf.sigma))
	dlnsigmadlnm = derivative(toderive, n.log(mass) )
	#normalization by average universedensity at this redshift in the right cosmo
	rhom_units = cosmo.Om(boxRedshift)*cosmo.critical_density(boxRedshift).to(u.solMass/(u.Mpc)**3.)#/(cosmo.h)**2.
	# in units (Msun/h) / (Mpc/h)**3
	rhom = rhom_units.value # hf.mean_density#/(hz)**2. 
	print hf.mean_density, rhom / (hf.mean_density*(cosmo.h)**2.)
	
	col0 = fits.Column( name="boxName",format="14A", array= n.array([boxName for i in range(len(bins[:-1][ok]))]))
	col1 = fits.Column( name="redshift",format="D", array= boxRedshift * n.ones( len(bins[:-1][ok]) ) )
	col1b = fits.Column( name="h",format="D", array= hz * n.ones( len(bins[:-1][ok]) ) )
	col2a = fits.Column( name="boxLengthProper",format="D", array= boxLength * n.ones( len(bins[:-1][ok]) ) )
	col2b = fits.Column( name="boxLengthComoving",format="D", array= boxLengthComoving * n.ones( len(bins[:-1][ok]) ) )
	col3 = fits.Column( name="logMpart",format="D", array=  logmp* n.ones( len(bins[:-1][ok]) ) )
	col4 = fits.Column( name="rhom",format="D", array= rhom* n.ones( len(bins[:-1][ok]) ) )
	print "bin test", bins[:-1][ok]
	col5_0 = fits.Column( name="log_"+qty+"_min",format="D", array= bins[:-1][ok] )
	col5_1 = fits.Column( name="log_"+qty+"_max",format="D", array= bins[1:][ok] )
	col5_2 = fits.Column( name="log_"+qty,format="D", array= logmass[ok])
	print "test2", len( logmass[ok]), logmass[ok]
	print "columns", col5_0, col5_1, col5_2
	print "array", col5_0.array, col5_1.array, col5_2.array
	col5_3 = fits.Column( name="sigmaM",format="D", array= sig[ok] )
	col5_4 = fits.Column( name="nu2",format="D", array= nnu[ok])#hf.delta_c/sig ) # hf.growth_factor/
	col5_5 = fits.Column( name="dlnsigmaMdlnM",format="D", array= dlnsigmadlnm[ok] )
	
	unitVolume =  (boxLength *0.10)**3. # /cosmo.H(boxRedshift)
	volume = (boxLength)**3.

	Ncounts, Ncounts_c, Nall, Nall_c, mean90, std90, mean90_c, std90_c = getStat(fileC,volume,unitVolume)

	col6c = fits.Column( name="dN_counts_cen",format="D", array= Ncounts[ok] )
	col6cc = fits.Column( name="dN_counts_cen_c",format="D", array= Ncounts_c[ok])
	col7c = fits.Column( name="dNdV_cen",format="D", array= Nall[ok] )
	col7cc = fits.Column( name="dNdV_cen_c",format="D", array= Nall_c[ok] )
	col8c = fits.Column( name="dNdlnM_cen",format="D", array= Nall[ok]/dlnbin[ok] )
	col8cc = fits.Column( name="dNdlnM_cen_c",format="D", array= Nall_c[ok]/dlnbin[ok] )
	col9c = fits.Column( name="std90_pc_cen",format="D", array= std90[ok] )
	col9cc = fits.Column( name="std90_pc_cen_c",format="D", array= std90_c[ok] )

	Ncounts, Ncounts_c, Nall, Nall_c, mean90, std90, mean90_c, std90_c = getStat(fileS,volume,unitVolume)

	col6s = fits.Column( name="dN_counts_sat",format="D", array= Ncounts[ok] )
	col6sc = fits.Column( name="dN_counts_sat_c",format="D", array= Ncounts_c[ok])
	col7s = fits.Column( name="dNdV_sat",format="D", array= Nall[ok] )
	col7sc = fits.Column( name="dNdV_sat_c",format="D", array= Nall_c[ok] )
	col8s = fits.Column( name="dNdlnM_sat",format="D", array= Nall[ok]/dlnbin[ok] )
	col8sc = fits.Column( name="dNdlnM_sat_c",format="D", array= Nall_c[ok] / dlnbin[ok] )
	col9s = fits.Column( name="std90_pc_sat",format="D", array= std90[ok] )
	col9sc = fits.Column( name="std90_pc_sat_c",format="D", array= std90_c[ok] )

	tbhdu = fits.BinTableHDU.from_columns([col0, col1,col1b, col2a, col2b, col3, col4, col5_0, col5_1, col5_2, col5_3, col5_4, col5_5, col6c, col7c, col8c, col9c, col6cc, col7cc, col8cc, col9cc, col6s, col7s, col8s, col9s, col6sc, col7sc, col8sc, col9sc ])
	
	prihdr = fits.Header()
	prihdr['AUTHOR'] = 'J. Comparat'
	prihdr['DATE'] = time.time()
	prihdu = fits.PrimaryHDU(header=prihdr)
	thdulist = fits.HDUList([prihdu, tbhdu])
	
	writeName = join(os.environ['MULTIDARK_LIGHTCONE_DIR'], qty, "data", boxName+"_"+str(boxRedshift)+"_"+qty+".fits")
	if os.path.isfile(writeName):
		os.remove(writeName)
	
	thdulist.writeto(writeName)
	#return hf

def convert_pkl_velocity(fileC, fileS, binFile, zList_files, qty='vmax'):
	"""
	:param qty: one point function variable. Default vmax.
	:param fileC: file with the central halo statistics
	:param fileS: file with the satelitte halo statistics
	:param binFile: file with the bins
	:param zList_files: list of file with linking snapshot number and redshift
	:return: a fits table containing the one point function histograms
	"""
	print fileC.split('/')[6]
	boxName = fileC.split('/')[6]
	boxZN = float(fileC.split('/')[-1].split('_')[1])
	bins = n.loadtxt(binFile)
	#10**n.arange(0,3.5,0.01)
	dX = ( bins[1:]  - bins[:-1] ) #* n.log(10)
	dlnbin = dX / (( bins[1:]  + bins[:-1] )/2.)
	print boxName
	if boxName=='MD_0.4Gpc' :
		boxLength = 400.
		boxRedshift = 1./boxZN - 1.
		logmp = n.log10(9.63 * 10**7)
		
	if boxName=='MD_1Gpc' :
		boxLength = 1000.
		boxRedshift = 1./boxZN - 1.
		logmp = n.log10(1.51 * 10**9)

	if boxName=='MD_2.5Gpc' :
		boxLength = 2500.
		nSN, aSN = n.loadtxt(zList_files[2], unpack=True, dtype={'names': ('nSN', 'aSN'), 'formats': ('i4', 'f4')})
		conversion = dict(n.transpose([ nSN, 1/aSN-1 ]))
		boxRedshift =  conversion[boxZN] 
		logmp = n.log10(2.359 * 10**10)

	if boxName=='MD_4Gpc' :
		boxLength = 4000.
		nSN, aSN = n.loadtxt(zList_files[3], unpack=True, dtype={'names': ('nSN', 'aSN'), 'formats': ('i4', 'f4')})
		conversion = dict(n.transpose([ nSN, 1/aSN-1 ]))
		boxRedshift =  conversion[boxZN] 
		logmp = n.log10(9.6 * 10**10)

	if boxName=='MD_2.5GpcNW' :
		boxLength = 2500.
		nSN, aSN = n.loadtxt(zList_files[4], unpack=True, dtype={'names': ('nSN', 'aSN'), 'formats': ('i4', 'f4')})
		conversion = dict(n.transpose([ nSN, 1/aSN-1 ]))
		boxRedshift =  conversion[boxZN] 
		logmp = n.log10(2.359 * 10**10)

	if boxName=='MD_4GpcNW' :
		boxLength = 4000.
		nSN, aSN = n.loadtxt(zList_files[5], unpack=True, dtype={'names': ('nSN', 'aSN'), 'formats': ('i4', 'f4')})
		conversion = dict(n.transpose([ nSN, 1/aSN-1 ]))
		boxRedshift =  conversion[boxZN] 
		logmp = n.log10(9.6 * 10**10)

	col0 = fits.Column( name="boxName",format="14A", array= n.array([boxName for i in range(len(bins[:-1]))]))
	col1 = fits.Column( name="log_"+qty+"_min",format="D", array= bins[:-1] )
	col2 = fits.Column( name="log_"+qty+"_max",format="D", array= bins[1:] )
	col3 = fits.Column( name="redshift",format="D", array= boxRedshift * n.ones_like(bins[:-1]) )
	col4 = fits.Column( name="boxLength",format="D", array= boxLength * n.ones_like(bins[:-1]) )
	col4_2 = fits.Column( name="Mpart",format="D", array=  logmp* n.ones_like(bins[:-1]) )

	unitVolume =  (boxLength*0.10)**3.
	volume = (boxLength)**3.

	Ncounts, Ncounts_c, Nall, Nall_c, mean90, std90, mean90_c, std90_c = getStat(fileC,volume,unitVolume)

	col5 = fits.Column( name="dN_counts_cen",format="D", array= Ncounts )
	col6 = fits.Column( name="dN_counts_cen_c",format="D", array= Ncounts_c)
	col7 = fits.Column( name="dNdV_cen",format="D", array= Nall )
	col8 = fits.Column( name="dNdV_cen_c",format="D", array= Nall_c )
	col9 = fits.Column( name="dNdlnM_cen",format="D", array= Nall/dlnbin )
	col10 = fits.Column( name="dNdlnM_cen_c",format="D", array= Nall_c/dlnbin )
	col11 = fits.Column( name="std90_pc_cen",format="D", array= std90 )
	col12 = fits.Column( name="std90_pc_cen_c",format="D", array= std90_c )

	Ncounts, Ncounts_c, Nall, Nall_c, mean90, std90, mean90_c, std90_c = getStat(fileS,volume,unitVolume)

	col5_s = fits.Column( name="dN_counts_sat",format="D", array= Ncounts )
	col6_s = fits.Column( name="dN_counts_sat_c",format="D", array= Ncounts_c)
	col7_s = fits.Column( name="dNdV_sat",format="D", array= Nall )
	col8_s = fits.Column( name="dNdV_sat_c",format="D", array= Nall_c )
	col9_s = fits.Column( name="dNdlnM_sat",format="D", array= Nall/dlnbin )
	col10_s = fits.Column( name="dNdlnM_sat_c",format="D", array= Nall_c / dlnbin )
	col11_s = fits.Column( name="std90_pc_sat",format="D", array= std90 )
	col12_s = fits.Column( name="std90_pc_sat_c",format="D", array= std90_c )


	hdu2 = fits.BinTableHDU.from_columns([col0, col1, col2, col3, col4, col4_2, col5, col6, col7, col8, col9, col10, col11, col12, col5_s, col6_s, col7_s, col8_s, col9_s, col10_s, col11_s, col12_s])
	
	writeName = join(os.environ['MULTIDARK_LIGHTCONE_DIR'], qty, "data", boxName+"_"+str(boxRedshift)+"_"+qty+".fits")
	os.system("rm -rf "+ writeName)
	hdu2.writeto(writeName)

