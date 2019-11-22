import ROOT
from ROOT import *
from optparse import OptionParser, make_option
import sys
import os
from math import sqrt
import json

#date = '06_05_2019' 
date = '25_10_2019'

#filename = '/work/nchernya/DiHiggs/CMSSW_7_4_7/src/flashggFinalFit/Signal/output/CMS-HGG_sigfit_all2016_2017_%s.root'%date
#filename_bkg = '/work/nchernya/DiHiggs/CMSSW_7_4_7/src/flashggFinalFit/Background/outputs/CMS-HGG_multipdf_HHbbgg_2016_2017_%s.root'%date

filename = '/work/nchernya/DiHiggs/CMSSW_7_4_7/src/flashggFinalFit/Signal/output/CMS-HGG_sigfit_all2016_2017_2018_%s.root'%date
filename_bkg = '/work/nchernya/DiHiggs/CMSSW_7_4_7/src/flashggFinalFit/Background/outputs/CMS-HGG_multipdf_HHbbgg_2016_2017_2018_%s.root'%date
wsname = 'wsig_13TeV'
wsname_bkg = 'multipdf'

symbol = ''  #for keynote
#symbol = '&'  #for latex

num_cat = 12
lumi_2016=35.9*1000
lumi_2017=41.5*1000
lumi_2018=59.5*1000
SMsignal=31.05*0.58*0.00227*2  #new most updated x-sec

names="hh_SM_generated_2016,tth_2016,ggh_2016,qqh_2016,vh_2016,hh_SM_generated_2017,tth_2017,ggh_2017,qqh_2017,vh_2017,hh_SM_generated_2018,tth_2018,ggh_2018,qqh_2018,vh_2018".split(',')
#names="hh_SM_2016,tth_2016,ggh_2016,qqh_2016,vh_2016,hh_SM_2017,tth_2017,ggh_2017,qqh_2017,vh_2017,hh_SM_generated_2018,tth_2018,ggh_2018,qqh_2018,vh_2018".split(',')

sum_entries = dict()
sum_entries_bkg = dict()

entries_per_cat = dict()

tfile = TFile(filename)
ws = tfile.Get(wsname)
for name in names:
	print '%s\t'%(name),
	sum=0.
	lumi = 1.
	if '2016' in name : lumi = lumi_2016
	if '2017' in name : lumi = lumi_2017
	if '2018' in name : lumi = lumi_2018
	entries_per_cat[name] = [] 
	for cat in range(0,num_cat):
		ws_name = 'hggpdfsmrel_13TeV_%s_DoubleHTag_%d_norm'%(name,cat)
		var = (ws.var('MH'))
		var.setVal(125.)
		entries = (ws.function(ws_name).getVal())
		sum_entries[name] = entries
		#print entries , lumi
		count = entries*lumi
		if 'hh_SM' in name or 'HH' in name : 
			count*=SMsignal
		sum+=count
		entries_per_cat[name].append(count)
	#	print '%.2f\t'%(count),
		print '%.4f\t'%(count),'%s'%symbol,
	print '%.2f'%sum



filename_bkg_2016 = '/work/nchernya/DiHiggs/inputs/%s/output_DoubleEG_2016_%s.root'%(date,date)
filename_bkg_2017 = '/work/nchernya/DiHiggs/inputs/%s/output_DoubleEG_2017_%s.root'%(date,date)
filename_bkg_total = '/work/nchernya/DiHiggs/inputs/%s/output_DoubleEG_2016_2017_2018_%s.root'%(date,date)
#filename_bkg_total = '/work/nchernya/DiHiggs/inputs/%s/output_DoubleEG_2016_2017_%s.root'%(date,date)
#years=['2016','2017','Total']
years=['Total']
print 'Data with blinded 115 < Mgg < 135'
#for num,name in enumerate([filename_bkg_2016,filename_bkg_2017,filename_bkg_total]):
for num,name in enumerate([filename_bkg_total]):
	tfile = TFile(name)
	wsname_bkg = 'tagsDumper/cms_hgg_13TeV'
	ws_bkg = tfile.Get(wsname_bkg)
	sum_bkg=0.
	print 'Data %s\t'%years[num],
	entries_per_cat['Data'+years[num]] = [] 
	for cat in range(0,num_cat):
		catname = 'Data_13TeV_DoubleHTag_%d'%(cat)
		entries = ws_bkg.data(catname).sumEntries()
		entries_blinded=0
		for event in range(0,ws_bkg.data(catname).numEntries()):
			if (ws_bkg.data(catname).get(event).getRealValue("CMS_hgg_mass") > 135.) or (ws_bkg.data(catname).get(event).getRealValue("CMS_hgg_mass") < 115.):
				entries_blinded+=1
		sum_entries_bkg[catname] = entries
		sum_bkg+=entries_blinded
	#	print '%d\t'%(entries),'&',
		print '%d\t'%(entries_blinded),'%s'%symbol,
		entries_per_cat['Data'+years[num]].append(entries_blinded)
	print '%d\t'%(sum_bkg)



result = open("full_yields_%s.txt"%date,"w")
result.write(json.dumps(entries_per_cat))
