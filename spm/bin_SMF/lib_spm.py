# on ds52 
import astropy.io.fits as fits
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as p
import numpy as n
import os
import sys

z_min, z_max = 0., 1.6

out_dir = os.path.join(os.environ['OBS_REPO'], 'spm', 'results')

#previous catalogs
ll_dir = os.path.join(os.environ['OBS_REPO'], 'spm', 'literature')

path_2_pS_salpeter_cat = os.path.join( ll_dir, "portsmouth_stellarmass_starforming_salp-26.fits.gz" )
path_2_pB_salpeter_cat = os.path.join( ll_dir, "portsmouth_stellarmass_starforming_salp-DR12-boss.fits.gz" )

path_2_pS_kroupa_cat = os.path.join( ll_dir, "portsmouth_stellarmass_starforming_krou-26.fits.gz" )
path_2_pB_kroupa_cat = os.path.join( ll_dir, "portsmouth_stellarmass_starforming_krou-DR12-boss.fits.gz" )

path_2_ppS_kroupa_cat = os.path.join( ll_dir, "portsmouth_stellarmass_passive_krou-26.fits.gz")
path_2_ppB_kroupa_cat = os.path.join( ll_dir, "portsmouth_stellarmass_passive_krou-DR12-boss.fits.gz")

path_2_ppS_salpeter_cat = os.path.join( ll_dir, "portsmouth_stellarmass_passive_salp-26.fits.gz")
path_2_ppB_salpeter_cat = os.path.join( ll_dir, "portsmouth_stellarmass_passive_salp-DR12-boss.fits.gz")

cosmos_dir = os.path.join(os.environ['OBS_REPO'], 'COSMOS', 'catalogs' )
path_2_cosmos_cat = os.path.join( cosmos_dir, "photoz-2.0", "photoz_vers2.0_010312.fits")
path_2_cosmos_cat = os.path.join( cosmos_dir, "COSMOS2015_Laigle+_v1.1.fits.gz")


# FIREFLY CATALOGS
# SDSS data and catalogs
sdss_dir = os.path.join(os.environ['OBS_REPO'], 'SDSS', 'dr14')
path_2_spall_sdss_dr14_cat = os.path.join( sdss_dir, "specObj-SDSS-dr14.fits" )
path_2_spall_boss_dr14_cat = os.path.join( sdss_dir, "specObj-BOSS-dr14.fits" )
path_2_sdss_cat = os.path.join( sdss_dir, 'firefly', "FireflyGalaxySdss26.fits" )
path_2_eboss_cat = os.path.join( sdss_dir, 'firefly', "FireflyGalaxyEbossDR14.fits" )

# DEEP SURVEYS
deep2_dir = os.path.join(os.environ['OBS_REPO'], 'DEEP2')
path_2_deep2_cat = os.path.join( deep2_dir, "zcat.deep2.dr4.v4.LFcatalogTC.Planck15.spm.v2.fits" )

vipers_dir = os.path.join(os.environ['OBS_REPO'], 'VIPERS')
path_2_vipers_cat = os.path.join( vipers_dir, "VIPERS_W14_summary_v2.1.linesFitted.spm.fits" )

vvds_dir = os.path.join(os.environ['OBS_REPO'], 'VVDS')
path_2_vvdsW_cat = os.path.join( vvds_dir, "catalogs", "VVDS_WIDE_summary.v1.spm.fits" )
path_2_vvdsD_cat = os.path.join( vvds_dir, "catalogs", "VVDS_DEEP_summary.v1.spm.fits" )

# path_2_F16_cat = os.path.join( sdss_dir, "RA_DEC_z_w_fluxOII_Mstar_grcol_Mr_lumOII.dat" )

# OPENS THE CATALOGS
deep2   = fits.open(path_2_deep2_cat)[1].data
vvdsD   = fits.open(path_2_vvdsD_cat)[1].data
vvdsW   = fits.open(path_2_vvdsW_cat)[1].data
vipers   = fits.open(path_2_vipers_cat)[1].data
sdss   = fits.open(path_2_sdss_cat)[1].data
boss   = fits.open(path_2_eboss_cat)[1].data
cosmos = fits.open(path_2_cosmos_cat)[1].data

#sdss_12_portSF_kr   = fits.open(path_2_pS_kroupa_cat)[1].data
#boss_12_portSF_kr   = fits.open(path_2_pB_kroupa_cat)[1].data
#sdss_12_portPA_kr   = fits.open(path_2_ppS_kroupa_cat)[1].data
#boss_12_portPA_kr   = fits.open(path_2_ppB_kroupa_cat)[1].data
#sdss_12_portSF_sa   = fits.open(path_2_pS_salpeter_cat)[1].data
#boss_12_portSF_sa   = fits.open(path_2_pB_salpeter_cat)[1].data
#sdss_12_portPA_sa   = fits.open(path_2_ppS_salpeter_cat)[1].data
#boss_12_portPA_sa   = fits.open(path_2_ppB_salpeter_cat)[1].data

#RA, DEC, z, weigth, O2flux, M_star, gr_color, Mr_5logh, O2luminosity = n.loadtxt(path_2_F16_cat, unpack=True)

# stat functions
ld = lambda selection : len(selection.nonzero()[0])
sld = lambda selection : str(len(selection.nonzero()[0]))

def get_basic_stat_firefly_DR14(catalog, z_name, z_err_name, class_name, zwarning, name, zflg_val, prefix):
    catalog_zOk =(catalog[z_err_name] > 0.) & (catalog[z_name] > catalog[z_err_name])  & (catalog[class_name]=='GALAXY')  & (catalog[zwarning]==zflg_val) & (catalog[z_name] > z_min) & (catalog[z_name] < z_max) 
    catalog_sel = (catalog_zOk) & (catalog[prefix+'stellar_mass'] < 10**14. ) & (catalog[prefix+'stellar_mass'] > 0 )  & (catalog[prefix+'stellar_mass'] > catalog[prefix+'stellar_mass_low'] ) & (catalog[prefix+'stellar_mass'] < catalog[prefix+'stellar_mass_up'] ) & ( - n.log10(catalog[prefix+'stellar_mass_low'])  + n.log10(catalog[prefix+'stellar_mass_up']) < 0.4 )
    m_catalog = n.log10(catalog[prefix+'stellar_mass'])
    w_catalog =  n.ones_like(catalog[prefix+'stellar_mass'])
    return name + '& $' +str(len(catalog))+ "$ & $"+ sld(catalog_zOk)+"$ & $"+ sld(catalog_sel)+"$ \\\\"
    #return catalog_sel, m_catalog, w_catalog

def get_basic_stat_deep2(catalog, z_name, z_flg, name, zflg_min, prefix):
    catalog_zOk = (catalog[z_name] > z_min) & (catalog[z_flg]>=zflg_min) & (catalog[z_name] > z_min) & (catalog[z_name] < z_max) & (catalog['SSR']>0) & (catalog['TSR']>0) & (catalog['SSR']<=1.0001) & (catalog['TSR']<=1.0001)
    catalog_sel = (catalog_zOk) & (catalog[prefix+'stellar_mass'] < 10**14. ) & (catalog[prefix+'stellar_mass'] > 0. )  & (catalog[prefix+'stellar_mass'] > catalog[prefix+'stellar_mass_low'] ) & (catalog[prefix+'stellar_mass'] < catalog[prefix+'stellar_mass_up'] ) & ( - n.log10(catalog[prefix+'stellar_mass_low'])  + n.log10(catalog[prefix+'stellar_mass_up']) < 0.4 )
    m_catalog = n.log10(catalog[prefix+'stellar_mass'])
    w_catalog = 1. / (catalog['TSR'] * catalog['SSR'])
    return name + '& $' +str(len(catalog))+ "$ & $"+ sld(catalog_zOk)+"$ & $"+ sld(catalog_sel)+"$ \\\\"
    #return catalog_sel, m_catalog, w_catalog

def get_basic_stat_DR12(catalog, z_name, z_err_name, name, zflg_val):
    catalog_zOk =(catalog[z_err_name] > 0.) & (catalog[z_name] > catalog[z_err_name]) & (catalog[z_name] > z_min) & (catalog[z_name] < z_max) 
    catalog_sel = (catalog_zOk) & (catalog['LOGMASS'] < 14. ) & (catalog['LOGMASS'] > 0 ) & (catalog['MAXLOGMASS'] - catalog['MINLOGMASS'] <0.4) & (catalog['LOGMASS'] < catalog['MAXLOGMASS'] ) & (catalog['LOGMASS'] > catalog['MINLOGMASS'] )
    m_catalog = catalog['LOGMASS']
    w_catalog =  n.ones_like(catalog['LOGMASS'])
    return name + '& $' +str(len(catalog))+ "$ & $"+ sld(catalog_zOk)+"$ & $"+ sld(catalog_sel)+"$ \\\\"
    #return catalog_sel, m_catalog, w_catalog

SNlimit = 5
lineSelection = lambda catalog, lineName : (catalog[lineName+'_flux']>0.)& (catalog[lineName+'_fluxErr'] >0.) & (catalog[lineName+'_flux'] > SNlimit * catalog[lineName+'_fluxErr']) # & (catalog[lineName+'_luminosity']>0)& (catalog[lineName+'_luminosity']<1e50)

def get_line_stat_deep2(catalog, z_name, z_flg, name, zflg_min, prefix):
    catalog_zOk = (catalog[z_name] > z_min) & (catalog[z_flg]>=zflg_min) & (catalog[z_name] > z_min) & (catalog[z_name] < z_max) & (catalog['SSR']>0) & (catalog['TSR']>0) & (catalog['SSR']<=1.0001) & (catalog['TSR']<=1.0001)
    catalog_sel = (catalog_zOk) & (catalog[prefix+'stellar_mass'] < 10**14. ) & (catalog[prefix+'stellar_mass'] > 10**5. )  & (catalog[prefix+'stellar_mass'] < catalog[prefix+'stellar_mass_up'] ) & (catalog[prefix+'stellar_mass'] > catalog[prefix+'stellar_mass_low'] ) & (-n.log10(catalog[prefix+'stellar_mass_low'])  + n.log10(catalog[prefix+'stellar_mass_up']) < 1.)
    l_o2 = lineSelection(catalog, "O2_3728") & catalog_zOk
    l_o3 = lineSelection(catalog, "O3_5007") & catalog_zOk
    l_hb = lineSelection(catalog, "H1_4862") & catalog_zOk
    m_catalog = n.log10(catalog[prefix+'stellar_mass'])
    w_catalog = 1. / (catalog['TSR'] * catalog['SSR'])
    return name +  '& $' + str(len(catalog)) +  "$ & $" +  sld(catalog_zOk) + "$ & $" +  "\\;(" +  sld(catalog_sel) + ")$ & $" +  sld(l_o2) +  "\\;(" +  sld(catalog_sel & l_o2) + ")$ & $" +  sld(l_o3) +  "\\;(" +  sld(catalog_sel & l_o3) + ")$ & $" +  sld(l_hb) +  "\\;(" +  sld(catalog_sel & l_hb) + ")$ \\\\"
    #return catalog_sel, m_catalog, w_catalog, l_o2, l_o3, l_hb
    