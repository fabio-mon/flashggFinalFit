import ROOT
from ROOT import *
from optparse import OptionParser, make_option
import sys
import os
from math import sqrt
import json

#date = '06_05_2019' 
date = '18_02_2020'
#date = '22_04_2020'
#date = '27_03_2020'
#date = '03_02_2020'

#filename = '/work/nchernya/DiHiggs/CMSSW_7_4_7/src/flashggFinalFit/Signal/output/CMS-HGG_sigfit_all2016_2017_%s.root'%date
#filename_bkg = '/work/nchernya/DiHiggs/CMSSW_7_4_7/src/flashggFinalFit/Background/outputs/CMS-HGG_multipdf_HHbbgg_2016_2017_%s.root'%date

#filename = '/work/nchernya/DiHiggs/CMSSW_7_4_7/src/flashggFinalFit/Signal/output/CMS-HGG_sigfit_all2016_2017_2018_%s.root'%date
#filename = '/work/nchernya/DiHiggs/CMSSW_7_4_7/src/flashggFinalFit/Plots/FinalResults/inputs/CMS-HGG_sigfit_2016_2017_2018_%s.root'%date
#filename = '/work/nchernya/DiHiggs/CMSSW_7_4_7/src/flashggFinalFit/Plots/FinalResults/inputs/CMS-HGG_sigfit_MggMjj_2016_2017_2018_%s.root'%date
#filename = '/work/nchernya/DiHiggs/CMSSW_7_4_7/src/flashggFinalFit/Plots/FinalResults/inputs/CMS-HGG_sigfit_MggMjj_2016_2017_2018_%s_vbfhh2018.root'%date
#filename = '/work/nchernya/DiHiggs/CMSSW_7_4_7/src/flashggFinalFit/Plots/FinalResults/vbfhh_soumya/update/workspace_Mjj.root'
#filename = '/work/nchernya/DiHiggs/CMSSW_7_4_7/src/flashggFinalFit/Plots/FinalResults/vbfhh_soumya/update/CMS-HGG_sigfit_MggMjj_2018_25_03_2020.root'
#filename = '/work/nchernya/DiHiggs/CMSSW_7_4_7/src/flashggFinalFit/Plots/FinalResults/inputs/CMS-HGG_sigfit_MggMjj_2018_%s.root'%date
#filename = '/work/nchernya/DiHiggs/CMSSW_7_4_7/src/flashggFinalFit/Plots/FinalResults/inputs/CMS-HGG_sigfit_MggMjj_2018_27_03_2020.root'
#filename = '/work/nchernya/DiHiggs/CMSSW_7_4_7/src/flashggFinalFit/Plots/FinalResults/inputs/CMS-HGG_sigfit_MggMjj_2016_2017_2018_18_02_2020_Mjj_merged_70GeV.root'
filename = '/work/nchernya/DiHiggs/CMSSW_7_4_7/src/flashggFinalFit/Plots/FinalResults/inputs/CMS-HGG_sigfit_MggMjj_2016_2017_2018_18_02_2020_nlo_merged_70GeV.root'
#filename = '/work/nchernya/DiHiggs/CMSSW_7_4_7/src/flashggFinalFit/Plots/FinalResults/inputs/CMS-HGG_sigfit_MggMjj_2018_22_04_2020_70GeV.root'
#filename = '/work/nchernya/DiHiggs/CMSSW_7_4_7/src/flashggFinalFit/Signal/output/mjj/18_02_2020_soumya/workspace_out_wo_ggHH_2018.root'
#filename = '/work/nchernya/DiHiggs/CMSSW_7_4_7/src/flashggFinalFit/Plots/FinalResults/inputs/CMS-HGG_sigfit_MggMjj_2016_2017_2018_%s_Mjj_merged_70GeV.root'%date
#CMS-HGG_sigfit_2016_2017_2018_25_10_2019.root' #CMS-HGG_sigfit_allAndNodes2016_2017_2018_25_10_2019.root'
#filename = '/work/nchernya/DiHiggs/CMSSW_7_4_7/src/flashggFinalFit/Plots/FinalResults/inputs/CMS-HGG_sigfit_nodes2018_25_10_2019.root'
wsname = 'wsig_13TeV'
wsname_bkg = 'multipdf'

symbol = ''  #for keynote
#symbol = '&'  #for latex

#lumi_2016=35.9*1000
#lumi_2017=41.5*1000
#lumi_2018=59.5*1000
lumi_2016=1000
lumi_2017=1000
lumi_2018=1000
SMsignal=31.05*0.58*0.00227*2  #new most updated x-sec
vbfSMsignal=1.726*0.58*0.00227*2  #new most updated x-sec

SMsignal=1.
vbfSMsignal=1.


#names="ggh_2016,qqh_2016,tth_2016,vh_2016,hh_node_SM_2016,ggh_2017,qqh_2017,tth_2017,vh_2017,hh_node_SM_2017,ggh_2018,qqh_2018,tth_2018,vh_2018,hh_node_SM_2018".split(',')
names="ggh_2018,qqh_2018,tth_2018,vh_2018".split(',')
names="vbfhh_2018".split(',')
names="ggh_2018,qqh_2018,tth_2018,vh_2018,hh_node_SM_2018,vbfhh_2018".split(',')

#names="ggh_2016,qqh_2016,tth_2016,vh_2016,hh_node_SM_2016,ggh_2017,qqh_2017,tth_2017,vh_2017,hh_node_SM_2017,ggh_2018,qqh_2018,tth_2018,vh_2018,hh_node_SM_2018".split(',')
#names="ggh_2016,qqh_2016,tth_2016,vh_2016,ggHH_kl_1_kt_1_2016,ggh_2017,qqh_2017,tth_2017,vh_2017,ggHH_kl_1_kt_1_2017,ggh_2018,qqh_2018,tth_2018,vh_2018,ggHH_kl_1_kt_1_2018".split(',')

#names="hh_node_SM_2016,hh_node_SM_2017,hh_node_SM_2018".split(',')
#names="ggHH_kl_1_kt_1_2016,ggHH_kl_1_kt_1_2017,ggHH_kl_1_kt_1_2018".split(',')
names="ggHH_kl_0_kt_1_2018,ggHH_kl_1_kt_1_2018,ggHH_kl_2p45_kt_1_2018,ggHH_kl_5_kt_1_2018".split(',')

sum_entries = dict()
sum_entries_bkg = dict()

entries_per_cat = dict()

num_cat = 12
for name in names:
	print '%s\t'%(name),
	sum=0.
	lumi = 1.
	if '2016' in name : lumi = lumi_2016
	if '2017' in name : lumi = lumi_2017
	if '2018' in name : lumi = lumi_2018
	entries_per_cat[name] = [] 
	for cat in range(0,num_cat):
		filename_in = filename
		if (cat==10) or (cat==11) : filename_in = filename.replace("70GeV","90GeV")
		tfile = TFile(filename_in)
		ws = tfile.Get(wsname)
		ws_name = 'hhbbggpdfsm_13TeV_%s_DoubleHTag_%d_norm'%(name,cat)
		if cat==12 : ws_name = 'hhbbggpdfsm_13TeV_%s_VBFDoubleHTag_0_norm'%(name)
		#ws_name = 'hbbpdfsm_13TeV_%s_DoubleHTag_%d_norm'%(name,cat)
		#if cat==12 : ws_name = 'hbbpdfsm_13TeV_%s_VBFDoubleHTag_0_norm'%(name)
		#ws_name = 'hggpdfsmrel_13TeV_%s_DoubleHTag_%d'%(name,cat)
		var = (ws.var('MH'))
		var.setVal(125.)
		entries = (ws.function(ws_name).getVal())
		sum_entries[name] = entries
		#print entries , lumi
		count = entries*lumi
		if 'hh_node_SM' in name : 
			count*=SMsignal
		if 'vbfhh' in name : 
			count*=vbfSMsignal
		sum+=count
		entries_per_cat[name].append(count)
	#	print '%.2f\t'%(count),
		print '%.6f\t'%(count),'%s'%symbol,
	#	print '%.6f\t'%(count),'%s'%symbol
	if symbol=='&' : 
	  print '%.2f \\\\'%sum
	#else : print '%.2f'%sum
	else : print '%.6f'%sum



filename_bkg_2016 = '/work/nchernya/DiHiggs/inputs/%s/output_DoubleEG_2016_%s.root'%(date,date)
filename_bkg_2017 = '/work/nchernya/DiHiggs/inputs/%s/output_DoubleEG_2017_%s.root'%(date,date)
filename_bkg_2018 = '/work/nchernya/DiHiggs/inputs/%s/output_DoubleEG_2018_%s.root'%(date,date)
#filename_bkg_mc_2018 = '/work/nchernya/DiHiggs/inputs/%s/output_BG_MCbgbjets_woGjets_2018_%s.root'%(date,date)
#filename_bkg_mc_2018 = '/work/nchernya/DiHiggs/inputs/%s/output_BG_MCbgbjets_woGjets_2018_25_03_2020_vbfHHTag.root'%(date)
#filename_bkg_mc_2018 = '/work/nchernya/DiHiggs/inputs/%s/output_BG_MCbgbjets_woGjets_2018_%s.root'%(date,date)
filename_bkg_mc_2018 = "/work/nchernya/DiHiggs/CMSSW_7_4_7/src/flashggFinalFit/Plots/FinalResults/vbfhh_soumya/27_03_2020/soumya_stuff/output_BG_MCbgbjets_2018_27_03_2020.root"
#filename_bkg_total = '/work/nchernya/DiHiggs/inputs/%s/output_DoubleEG_2016_2017_2018_%s.root'%(date,date)
filename_bkg_total = '/work/nchernya/DiHiggs/inputs/%s/Data_nonbiased/output_DoubleEG_cats70GeV_2016_2017_2018_%s.root'%(date,date)
filename_bkg_MC = '/work/nchernya/DiHiggs/inputs/%s/output_BG_MCbg_2016_2017_2018_%s.root'%(date,date)
filename_bkg_MCbjets = '/work/nchernya/DiHiggs/inputs/%s/output_BG_MCbgbjets_2016_2017_2018_%s.root'%(date,date)
#years=['2016','2017','2018','Total']
#years=['Total']
years=['2018']
#years=['Total','MC BGbjets', 'MC BG']
print 'Data with blinded 115 < Mgg < 135'
#for num,name in enumerate([filename_bkg_2016,filename_bkg_2017,filename_bkg_2018,filename_bkg_total]):
#for num,name in enumerate([filename_bkg_total]):
for num,name in enumerate([filename_bkg_mc_2018]):
#for num,name in enumerate([filename_bkg_total,filename_bkg_MCbjets,filename_bkg_MC]):
	sum_bkg=0.
	sum_bkg_sqr=0.
	sum_bkg_error=0.
	print 'Data %s\t'%years[num],
	entries_per_cat['Data'+years[num]] = [] 
	for cat in range(0,num_cat):
		filename_in = name
		if (cat==10) or (cat==11) : filename_in = name.replace("70GeV","90GeV")
		tfile = TFile(filename_in)
		wsname_bkg = 'tagsDumper/cms_hgg_13TeV'
		ws_bkg = tfile.Get(wsname_bkg)
		catname = 'Data_13TeV_DoubleHTag_%d'%(cat)
		if cat==12 : catname = 'Data_13TeV_VBFDoubleHTag_0'
		entries = ws_bkg.data(catname).sumEntries()
		entries_blinded=0
		entries_blinded_sqr=0
		entries_blinded_error=0
		for event in range(0,ws_bkg.data(catname).numEntries()):
			if (ws_bkg.data(catname).get(event).getRealValue("CMS_hgg_mass") > 135.) or (ws_bkg.data(catname).get(event).getRealValue("CMS_hgg_mass") < 115.):
				entries_blinded_sqr+=(ws_bkg.data(catname).weight())**2
				entries_blinded+=ws_bkg.data(catname).weight()
				entries_blinded_error+=ws_bkg.data(catname).weightError()
		sum_entries_bkg[catname] = entries
		sum_bkg+=entries_blinded
		sum_bkg_sqr+=entries_blinded_sqr
		sum_bkg_error+=entries_blinded_error
		#print '%d \pm %.1f\t'%(entries_blinded,sqrt(entries_blinded_sqr)),'%s'%symbol,
		#print '%d\t'%(entries_blinded),'%s'%symbol,
		print '%.2f\t'%(entries_blinded),'%s'%symbol,
		#print '%d\t'%(entries_blinded),'%s'%symbol
		#print '%d +- %.1f\t'%(entries_blinded,sqrt(entries_blinded_sqr)),'%s'%symbol,
		entries_per_cat['Data'+years[num]].append(entries_blinded)
	if symbol=='&' : 
	  print '%d \pm %1.f\t \\\\'%(sum_bkg,sqrt(sum_bkg_sqr))
	  #print '%d +- %.1f\t \\\\'%(sum_bkg,sqrt(sum_bkg_sqr))
	#else : print '%d \pm %.1f\t'%(sum_bkg,sqrt(sum_bkg_sqr))
	#else : print '%d \pm %.1f\t'%(sum_bkg,sqrt(sum_bkg_sqr))
	else : print '%.2f\t'%(sum_bkg)
	#else : print '%d +- %.1f\t'%(sum_bkg,sqrt(sum_bkg_sqr))



result = open("output_txt/full_yields_latex_test_%s.txt"%date,"w")
result.write(json.dumps(entries_per_cat))
