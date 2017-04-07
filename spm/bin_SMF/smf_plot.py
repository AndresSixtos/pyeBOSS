import astropy.cosmology as co
aa=co.Planck15
import astropy.io.fits as fits
import matplotlib.pyplot as p
import numpy as n
import os

import sys

# global cosmo quantities
z_min = float(sys.argv[1])
z_max = float(sys.argv[2])
#imf = 'kroupa'
lO2_min = float(sys.argv[3]) # 'salpeter'

SNlimit = 5


smf_ilbert13 = lambda M, M_star, phi_1s, alpha_1s, phi_2s, alpha_2s : ( phi_1s * (M/M_star) ** alpha_1s + phi_2s * (M/M_star) ** alpha_2s ) * n.e ** (-M/M_star) * (M/ M_star)

lineSelection = lambda catalog, lineName : (catalog[lineName+'_flux']>0.)& (catalog[lineName+'_fluxErr'] >0.) & (catalog[lineName+'_flux'] > SNlimit * catalog[lineName+'_fluxErr']) # & (catalog[lineName+'_luminosity']>0)& (catalog[lineName+'_luminosity']<1e50)

ff_dir = os.path.join(os.environ['DATA_DIR'], 'spm', 'firefly')
ll_dir = os.path.join(os.environ['DATA_DIR'], 'spm', 'literature')
co_dir = os.path.join(os.environ['DATA_DIR'], 'COSMOS' )

out_dir = os.path.join(os.environ['DATA_DIR'], 'spm', 'results')

path_2_cosmos_cat = os.path.join( co_dir, "photoz_vers2.0_010312.fits")
path_2_vvdsW_cat = os.path.join( ff_dir, "VVDS_WIDE_summary.v1.spm.fits" )
path_2_vipers_cat = os.path.join( ff_dir, "VIPERS_W14_summary_v2.1.linesFitted.spm.fits" )
path_2_vvdsD_cat = os.path.join( ff_dir, "VVDS_DEEP_summary.v1.spm.fits" )
path_2_deep2_cat = os.path.join( ff_dir, "zcat.deep2.dr4.v4.LFcatalogTC.Planck15.spm.fits" )

cosmos = fits.open(path_2_cosmos_cat)[1].data
deep2   = fits.open(path_2_deep2_cat)[1].data
vvdsD   = fits.open(path_2_vvdsD_cat)[1].data
vvdsW   = fits.open(path_2_vvdsW_cat)[1].data
vipers   = fits.open(path_2_vipers_cat)[1].data

path_ilbert13_SMF = os.path.join(ll_dir, "ilbert_2013_mass_function_params.txt")
zmin, zmax, N, M_comp, M_star, phi_1s, alpha_1s, phi_2s, alpha_2s, log_rho_s = n.loadtxt(os.path.join( ll_dir, "ilbert_2013_mass_function_params.txt"), unpack=True)

#smfs_ilbert13 = n.array([lambda mass : smf_ilbert13( mass , 10**M_star[ii], phi_1s[ii]*10**(-3), alpha_1s[ii], phi_2s[ii]*10**(-3), alpha_2s[ii] ) for ii in range(len(M_star)) ])

smf01 = lambda mass : smf_ilbert13( mass , 10**M_star[0], phi_1s[0]*10**(-3), alpha_1s[0], phi_2s[0]*10**(-3), alpha_2s[0] )
print 10**M_star[0], phi_1s[0]*10**(-3), alpha_1s[0], phi_2s[0]*10**(-3), alpha_2s[0]
smf08 = lambda mass : smf_ilbert13( mass , 10**M_star[2], phi_1s[2]*10**(-3), alpha_1s[2], phi_2s[2]*10**(-3), alpha_2s[2] )
print 10**M_star[2], phi_1s[2]*10**(-3), alpha_1s[2], phi_2s[2]*10**(-3), alpha_2s[2] 

volume_per_deg2 = ( aa.comoving_volume(z_max) -  aa.comoving_volume(z_min) ) * n.pi / 129600.
volume_per_deg2_val = volume_per_deg2.value

# global spm quantities

# stat functions
ld = lambda selection : len(selection.nonzero()[0])

# stats about DEEP2 run
area1=0.60
area2=0.62
area3=0.90
area4=0.66
if z_min>=0.7:
    area_deep2 = area1+area2+area3+area4
else :
    area_deep2 = 0.6
    
area_vvdsD = 0.6
area_vvdsW =  5.785
area_vipers = 24.
area_cosmos = 1.52

def get_basic_stat(catalog, z_name, z_flg, name, zflg_min, imf='kroupa'):
    catalog_zOk = (catalog[z_name] > z_min) & (catalog[z_flg]>=zflg_min) 
    catalog_stat = (catalog_zOk) & (catalog[z_name] > z_min) & (catalog[z_name] < z_max) & (catalog['SSR']>0) & (catalog['TSR']>0) & (catalog['SSR']<=1.0001) & (catalog['TSR']<=1.0001)
    catalog_sel = (catalog_stat) & (catalog['stellar_mass_'+imf] < 14. ) & (catalog['stellar_mass_'+imf] > 0 )  & (catalog['stellar_mass_'+imf] > catalog['stellar_mass_err_plus_'+imf] ) & (catalog['stellar_mass_'+imf] > catalog['stellar_mass_err_minus_'+imf] ) & (catalog['stellar_mass_err_minus_'+imf]  + catalog['stellar_mass_err_plus_'+imf] <0.4)
    l_o2 = lineSelection(catalog, "O2_3728") & catalog_stat
    l_o3 = lineSelection(catalog, "O3_5007") & catalog_stat
    l_hb = lineSelection(catalog, "H1_4862") & catalog_stat
    m_catalog = catalog['stellar_mass_'+imf]
    w_catalog = 1. / (catalog['TSR'] * catalog['SSR'])
    print name, '& $',len(catalog), "$ & $", ld(catalog_zOk),"$ & $", ld(catalog_stat), "\\;(", ld(catalog_sel),")$ & $", ld(l_o2), "\\;(", ld(catalog_sel & l_o2),")$ & $", ld(l_o3), "\\;(", ld(catalog_sel & l_o3),")$ & $", ld(l_hb), "\\;(", ld(catalog_sel & l_hb),")$ \\\\"
    return catalog_sel, m_catalog, w_catalog, l_o2, l_o3, l_hb
    
def get_hist(masses, weights, mbins):
    NN = n.histogram(masses, mbins)[0]
    NW = n.histogram(masses, mbins, weights = weights)[0]
    xx = (mbins[1:] + mbins[:-1])/2.
    return xx, NW, NN**(-0.5)*NW

def plotMF_raw(imf='kroupa'):
    deep2_sel, deep2_m, deep2_w, deep2_o2, deep2_o3, deep2_hb = get_basic_stat(deep2, 'ZBEST', 'ZQUALITY', 'DEEP2', 3., imf=imf)
    vvdsD_sel, vvdsD_m, vvdsD_w, vvdsD_o2, vvdsD_o3, vvdsD_hb = get_basic_stat(vvdsD, 'Z', 'ZFLAGS', 'VVDS Deep', 2., imf=imf)
    vvdsW_sel, vvdsW_m, vvdsW_w, vvdsW_o2, vvdsW_o3, vvdsW_hb = get_basic_stat(vvdsW, 'Z', 'ZFLAGS', 'VVDS Wide', 2., imf=imf)
    vipers_sel, vipers_m, vipers_w, vipers_o2, vipers_o3, vipers_hb = get_basic_stat(vipers, 'zspec', 'zflg', 'VIPERS', 1., imf=imf)

    lbins = n.arange(40.5,44,0.25)
    x_lum = (lbins[1:] + lbins[:-1])/2.
    
    p.figure(0, (8,8))
    
    N_O2_all = n.histogram(deep2['O2_3728_luminosity'][deep2_o2], bins = 10**lbins)[0]
    N_O2_mass = n.histogram(deep2['O2_3728_luminosity'][deep2_sel & deep2_o2], bins = 10**lbins)[0]
    N_O2_all_normed = n.histogram(n.log10(deep2['O2_3728_luminosity'][deep2_o2]), bins = lbins, normed = True)[0]
    #print N_O2_all_normed
    ok_o2 = (N_O2_all>0)
    p.plot(x_lum, N_O2_all_normed/2., label = 'normed hist')
    p.plot(x_lum[ok_o2], 1. * N_O2_mass[ok_o2] / N_O2_all[ok_o2], label = 'DEEP2')
    p.axvline(lO2_min)
    p.title(str(z_min)+'<z<'+str(z_max))
    p.xlabel('[OII] luminosity')
    p.ylabel('[OII] with mass measurement /  all [OII] detections')
    #p.yscale('log')
    p.legend(loc=0, frameon = False)
    p.ylim((-0.01, 1.01))
    p.xlim((40.5, 43.5))
    p.grid()
    p.savefig(os.path.join(out_dir, "line_detection_raw_"+imf+"_"+str(z_min)+'_z_'+str(z_max)+".jpg" ))
    p.clf()
    
    dlog10m = 0.25
    mbins = n.arange(8,12.5,dlog10m)
    
    p.figure(1, (8,8))
    p.plot(mbins, smf01(10**mbins), label='Ilbert 13, 0.2<z<0.5', ls='dashed')
    p.plot(mbins, smf08(10**mbins), label='Ilbert 13, 0.8<z<1.1', ls='dashed')
    
    x, y, ye = get_hist(deep2_m[deep2_sel], weights = deep2_w[deep2_sel]/(dlog10m*n.log(10)*area_deep2*volume_per_deg2_val), mbins = mbins)
    p.errorbar(x, y, yerr = ye, label='DEEP2', lw=1)
    
    x, y, ye = get_hist(deep2_m[deep2_sel & deep2_o2 & (deep2['O2_3728_luminosity']>10**lO2_min)], weights = deep2_w[deep2_sel & deep2_o2 & (deep2['O2_3728_luminosity']>10**lO2_min)]/(dlog10m*n.log(10)*area_deep2*volume_per_deg2_val), mbins = mbins)
    p.errorbar(x, y, yerr = ye, label='DEEP2 L([OII])>'+str(lO2_min), lw=1)
    
    #x, y, ye = get_hist(vvdsD_m, weights = vvdsD_w/(dlog10m*n.log(10)*area_vvdsD*volume_per_deg2_val), mbins = mbins)
    #p.errorbar(x, y, yerr = ye, label='VVDSDEEP', lw=1)
    #x, y, ye = get_hist(vipers_m, weights = vipers_w/(dlog10m*n.log(10)*area_vipers*volume_per_deg2_val), mbins = mbins)
    #p.errorbar(x, y, yerr = ye, label='VIPERS', lw=0.5)
    #x, y, ye = get_hist(vvdsW_m, weights = vvdsW_w/(dlog10m*n.log(10)*area_vvdsW*volume_per_deg2_val), mbins = mbins)
    #p.errorbar(x, y, yerr = ye, label='VVDSWide', lw=0.5)

    #cosmos_sel = (cosmos['flag_maskI']==0) &( cosmos['K'] < 24.) &  ( cosmos['photoz'] > z_min) & (cosmos['photoz'] < z_max )
    #cosmos_w = n.ones_like(cosmos['photoz'][cosmos_sel])
    #p.hist(cosmos['mass_med'][cosmos_sel], weights = cosmos_w/(dlog10m*n.log(10)*area_cosmos*volume_per_deg2_val), bins = mbins, label='COSMOS K<24', histtype='step')
    #cosmos_sel = (cosmos['flag_maskI']==0) &  ( cosmos['R'] < 24.1) & ( cosmos['photoz'] > z_min) & (cosmos['photoz'] < z_max )
    #cosmos_w = n.ones_like(cosmos['photoz'][cosmos_sel])
    #p.hist(cosmos['mass_med'][cosmos_sel], weights = cosmos_w/(dlog10m*n.log(10)*area_cosmos*volume_per_deg2_val), bins = mbins, label='COSMOS R<24.1', histtype='step')
    #for smfEq in smfs_ilbert13:
    
    p.title(str(z_min)+'<z<'+str(z_max))
    p.xlabel(r'$\log_{10}$ (stellar mass '+imf+r" / $M_\odot$ )")
    p.ylabel(r'$\Phi(M)$ [Mpc$^{-3}$ dex$^{-1}$]')
    p.yscale('log')
    p.legend(loc=0, frameon = False)
    p.ylim((1e-8, 1e-2))
    p.xlim((9.5, 12.5))
    p.grid()
    p.savefig(os.path.join(out_dir, "SMF_raw_"+imf+"_"+str(z_min)+'_z_'+str(z_max)+".jpg" ))
    p.clf()

    p.figure(2, (8,8))
    
    x, y, ye = get_hist(deep2_m[deep2_sel], weights = deep2_w[deep2_sel]/(dlog10m*n.log(10)*area_deep2*volume_per_deg2_val), mbins = mbins)
    p.errorbar(x, y/smf08(10**x), yerr = ye/smf08(10**x), label='DEEP2', lw=1)
    
    x, y, ye = get_hist(deep2_m[deep2_sel & deep2_o2 & (deep2['O2_3728_luminosity']>10**lO2_min)], weights = deep2_w[deep2_sel & deep2_o2 & (deep2['O2_3728_luminosity']>10**lO2_min)]/(dlog10m*n.log(10)*area_deep2*volume_per_deg2_val), mbins = mbins)
    p.errorbar(x, y/smf08(10**x), yerr = ye/smf08(10**x), label='DEEP2 L([OII])>'+str(lO2_min), lw=1)
    
    p.title(str(z_min)+'<z<'+str(z_max))
    p.xlabel(r'$\log_{10}$ (stellar mass '+imf+r" / $M_\odot$ )")
    p.ylabel(r'$\Phi_{[OII]} / \Phi_{all}(M)$')
    p.yscale('log')
    p.legend(loc=0, frameon = False)
    p.ylim((1e-4, 2.))
    p.xlim((9.5, 12.5))
    p.grid()
    p.savefig(os.path.join(out_dir, "ratio_SMF_"+imf+"_"+str(z_min)+'_z_'+str(z_max)+".jpg" ))
    p.clf()
    
plotMF_raw(imf='salpeter')
plotMF_raw(imf='kroupa')