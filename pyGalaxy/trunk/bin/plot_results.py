#! /usr/bin/env python

"""
This script produces the stacks for emission line luminosity limited samples.
"""
import matplotlib
matplotlib.use('pdf')
import matplotlib.pyplot as p
import numpy as n
import os
from os.path import join

path_to_summary_table = join(os.environ['SPECTRASTACKS_DIR'], "results", "table_v0.data")

data = n.loadtxt(path_to_summary_table)	

ok = (data[2]<0.85)&(data[2]>0.7)

lineWavelength,Survey,Redshift,L_MIN,L_MAX,L_MEAN,N_in_stack,R_stack,spm_light_age,spm_light_age_err_plus,spm_light_age_err_minus,spm_light_metallicity,spm_light_metallicity_err_plus,spm_light_metallicity_err_minus,spm_stellar_mass,spm_stellar_mass_err_plus,spm_stellar_mass_err_minus,spm_EBV,gp_EBV_4862_4341,gp_EBV_4862_4341_err,gp_EBV_4862_4102,gp_EBV_4862_4102_err,gp_BD_4102_4341,gp_BD_4102_4341_err,gp_SFR_O2_3728,gp_SFR_O2_3728_err,gp_SFR_H1_4862,gp_SFR_H1_4862_err,gp_12logOH_tremonti04,gp_12logOH_tremonti04_err,gp_12logOH_tremonti04_intrinsic,gp_12logOH_tremonti04_intrinsic_err = data.T[ok].T

# EBV comparison
#spm_EBV
#gp_EBV_4862_4341,gp_EBV_4862_4341_err,

ok = (gp_EBV_4862_4341!=-9999.99) &  (gp_EBV_4862_4341_err!=-9999.99)

p.figure(0,(6,6))
p.axes([0.17,0.17,0.8,0.8])
p.errorbar(spm_EBV[ok], gp_EBV_4862_4341[ok], yerr=gp_EBV_4862_4341_err[ok],fmt='o',elinewidth=2, mfc='none')
p.plot([-1,2],[-1,2],'k--')
p.legend(loc=2)
p.xlabel('E(B-V) SPM')
p.ylabel(r'E(B-V) GP $H\beta -H\delta$')
p.xlim((-1,2))
p.ylim((-1,2))
p.grid()
p.savefig( join(os.environ['SPECTRASTACKS_DIR'], "plots", "ebv-comparison-1.png"))
p.clf()

#spm_EBV
#gp_EBV_4862_4102,gp_EBV_4862_4102_err

ok = (gp_EBV_4862_4102!=-9999.99) &  (gp_EBV_4862_4102_err!=-9999.99)

p.figure(0,(6,6))
p.axes([0.17,0.17,0.8,0.8])
p.errorbar(spm_EBV[ok], gp_EBV_4862_4102[ok], yerr=gp_EBV_4862_4102_err[ok],fmt='o',elinewidth=2, mfc='none')
p.plot([-1,2],[-1,2],'k--')
p.legend(loc=2)
p.xlabel('E(B-V) SPM')
p.ylabel(r'E(B-V) GP $H\beta -H\gamma$')
p.xlim((-1,2))
p.ylim((-1,2))
p.grid()
p.savefig( join(os.environ['SPECTRASTACKS_DIR'], "plots", "ebv-comparison-2.png"))
p.clf()

# metallicity comparison
#spm_light_metallicity,spm_light_metallicity_err_plus,spm_light_metallicity_err_minus
#gp_12logOH_tremonti04,gp_12logOH_tremonti04_err,

ok = (gp_12logOH_tremonti04!=-9999.99) &  (gp_12logOH_tremonti04_err!=-9999.99)

p.figure(0,(6,6))
p.axes([0.17,0.17,0.8,0.8])
p.errorbar(x=spm_light_metallicity[ok], xerr=[spm_light_metallicity_err_plus[ok], spm_light_metallicity_err_minus[ok]], y=gp_12logOH_tremonti04[ok], yerr=gp_12logOH_tremonti04_err[ok],fmt='o',elinewidth=2, mfc='none')
p.plot([-1,2],[-1,2],'k--')
p.legend(loc=2)
p.xlabel('log(Z/Zsun) SPM')
p.ylabel(r'12+log(O/H) GP')
#p.xlim((-1,2))
#p.ylim((-1,2))
p.grid()
p.savefig( join(os.environ['SPECTRASTACKS_DIR'], "plots", "metal-comparison-1.png"))
p.clf()

#spm_light_metallicity,spm_light_metallicity_err_plus,spm_light_metallicity_err_minus
#gp_12logOH_tremonti04_intrinsic,gp_12logOH_tremonti04_intrinsic_err

ok = (gp_12logOH_tremonti04_intrinsic!=-9999.99) &  (gp_12logOH_tremonti04_intrinsic_err!=-9999.99)

p.figure(0,(6,6))
p.axes([0.17,0.17,0.8,0.8])
p.errorbar(x=spm_light_metallicity[ok], xerr=[spm_light_metallicity_err_plus[ok], spm_light_metallicity_err_minus[ok]], y=gp_12logOH_tremonti04_intrinsic[ok], yerr=gp_12logOH_tremonti04_intrinsic_err[ok],fmt='o',elinewidth=2, mfc='none')
p.plot([-1,2],[-1,2],'k--')
p.legend(loc=2)
p.xlabel('log(Z/Zsun) SPM')
p.ylabel(r'12+log(O/H) GP intrinsic')
#p.xlim((-1,2))
#p.ylim((-1,2))
p.grid()
p.savefig( join(os.environ['SPECTRASTACKS_DIR'], "plots", "metal-comparison-2.png"))
p.clf()

# SFR comparison

ok = (gp_SFR_O2_3728!=-9999.99) &  (gp_SFR_O2_3728_err!=-9999.99)&(gp_SFR_H1_4862!=-9999.99) &  (gp_SFR_H1_4862_err!=-9999.99)

p.figure(0,(6,6))
p.axes([0.17,0.17,0.8,0.8])
p.errorbar(x=gp_SFR_O2_3728[ok], xerr = gp_SFR_O2_3728_err[ok], y=gp_SFR_H1_4862[ok], yerr=gp_SFR_H1_4862_err[ok],fmt='o',elinewidth=2, mfc='none')
p.plot([-1,2],[-1,2],'k--')
p.legend(loc=2)
p.xlabel('SFR GP [OII]')
p.ylabel(r'SFR GP H$\beta$')
#p.xlim((-1,2))
#p.ylim((-1,2))
p.grid()
p.savefig( join(os.environ['SPECTRASTACKS_DIR'], "plots", "sfr-comparison-2.png"))
p.clf()

# mass metallicity relation
# Mannucci et al. 2010 :
y_rel = lambda x_rel : 8.90 + 0.39*x_rel - 0.20*x_rel*x_rel - 0.077*x_rel*x_rel*x_rel + 0.064*x_rel*x_rel*x_rel*x_rel

x_obs_1 = spm_stellar_mass - 0.32 * n.log10(gp_SFR_O2_3728) - 10
x_obs_2 = spm_stellar_mass - 0.32 * n.log10(gp_SFR_H1_4862) - 10
y_obs_1 = spm_light_metallicity

x_rel = n.arange(8.5,11.5,0.05) - 10 
y_pr = y_rel(x_rel)

base = (gp_SFR_O2_3728>0)& (gp_SFR_O2_3728_err>0)&(spm_stellar_mass >0)

p.figure(0,(6,6))
p.axes([0.17,0.17,0.8,0.8])
#p.plot(x_obs_1, y_obs_1, )
ok = (base) &(lineWavelength==4862.)
p.errorbar(x_obs_1[ok], 12+spm_light_metallicity[ok], yerr=[spm_light_metallicity_err_plus[ok], spm_light_metallicity_err_minus[ok]],fmt=None, mfc='none',label='Hb')
ok = (base) &(lineWavelength==5007.)
p.errorbar(x_obs_1[ok], 12+spm_light_metallicity[ok], yerr=[spm_light_metallicity_err_plus[ok], spm_light_metallicity_err_minus[ok]],fmt=None, mfc='none',label='O3')
ok = (base) &(lineWavelength==3728.)
p.errorbar(x_obs_1[ok], 12+spm_light_metallicity[ok], yerr=[spm_light_metallicity_err_plus[ok], spm_light_metallicity_err_minus[ok]],fmt=None, mfc='none',label='O2')
p.plot(x_rel, y_pr, 'k--',label='M10',lw=2)
p.ylabel(r'$12 \log(O/H)$')
p.xlabel('$\log(M_*)-0.32 \log(SFR)-10$')
p.xlim((-2,2.5))
p.legend(loc=4)
p.savefig( join(os.environ['SPECTRASTACKS_DIR'], "plots", "sfr-mass-z.png"))
p.clf()