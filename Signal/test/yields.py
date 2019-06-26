import ROOT
from ROOT import *
from optparse import OptionParser, make_option
import sys
import os
from math import sqrt
import json

date = '06_05_2019'
filename = '/afs/cern.ch/user/f/fmonti/work/flashggFinalFit/CMSSW_7_4_7/src/flashggFinalFit/Signal/output/CMS-HGG_sigfit_2016_2017_merged.root'
filename_bkg = '/afs/cern.ch/user/f/fmonti/work/flashggFinalFit/CMSSW_7_4_7/src/flashggFinalFit/Background/CMS-HGG_multipdf_HHbbgg_2016_2017_13_06_2019.root'
wsname = 'wsig_13TeV'
wsname_bkg = 'multipdf'

symbol = ''  #for keynote
#symbol = '&'  #for latex

num_cat = 12
lumi_2016=35.9*1000
lumi_2017=41.5*1000
SMsignal=33.49*0.58*0.00227*2
#lumi_2016=1000.
#lumi_2017=1000.
#SMsignal=1
names=[
"GluGluHToGG_M_125_13TeV_powheg_pythia8",
"GluGluToHHTo2B2G_node_SM_13TeV_madgraph",
"VBFHToGG_M_125_13TeV_powheg_pythia8",
"VHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8",
"ttHToGG_M125_13TeV_powheg_pythia8_v2",
"GluGluHToGG_M_125_13TeV_powheg_pythia8_2017",                    
"GluGluToHHTo2B2G_node_SM_13TeV_madgraph_2017",
"VBFHToGG_M_125_13TeV_powheg_pythia8_2017",                       
"VHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8_2017",
"ttHToGG_M125_13TeV_powheg_pythia8_2017"
]
tpMap = {
"GluGluHToGG_M_125_13TeV_powheg_pythia8":"GF_2016",
"GluGluToHHTo2B2G_node_SM_13TeV_madgraph":"HHbbgg_2016",
"VBFHToGG_M_125_13TeV_powheg_pythia8":"VBF_2016",
"VHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8":"VH_2016",
"ttHToGG_M125_13TeV_powheg_pythia8_v2":"ttH_2016",
"GluGluHToGG_M_125_13TeV_powheg_pythia8_2017":"GF_2017",                    
"GluGluToHHTo2B2G_node_SM_13TeV_madgraph_2017":"HHbbgg_2017",
"VBFHToGG_M_125_13TeV_powheg_pythia8_2017":"VBF_2017",                       
"VHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8_2017":"VH_2017",
"ttHToGG_M125_13TeV_powheg_pythia8_2017":"ttH_2017"
}
#names='GluGluToHHTo2B2G_node_SM_13TeV_madgraph,GluGluHToGG_M_125_13TeV_powheg_pythia8,VBFHToGG_M_125_13TeV_powheg_pythia8,ttHToGG_M125_13TeV_powheg_pythia8_v2,VHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8,GluGluToHHTo2B2G_node_SM_13TeV_madgraph_generated_2017,GluGluHToGG_M_125_13TeV_powheg_pythia8_2017,VBFHToGG_M_125_13TeV_powheg_pythia8_2017,ttHToGG_M125_13TeV_powheg_pythia8_2017,VHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8_2017'.split(',')
#tpMap = {"GluGluToHHTo2B2G_node_SM_13TeV_madgraph_generated":"HHbbgg_2016","GluGluHToGG_M_125_13TeV_powheg_pythia8":"GF_2016","VBFHToGG_M_125_13TeV_powheg_pythia8":"VBF_2016","ttHToGG_M125_13TeV_powheg_pythia8_v2":"ttH_2016","VHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8":"VH_2016","GluGluToHHTo2B2G_node_SM_13TeV_madgraph_generated_2017":"HHbbgg_2017","GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8_2017":"GF_2017","GluGluHToGG_M_125_13TeV_powheg_pythia8_2017":"GF_2017","VBFHToGG_M_125_13TeV_powheg_pythia8_2017":"VBF_2017","ttHToGG_M125_13TeV_powheg_pythia8_2017":"ttH_2017","VHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8_2017":"VH_2017"}

#names='GluGluToHHTo2B2G_node_SM_13TeV_madgraph_generated,GluGluToHHTo2B2G_node_SM_13TeV_madgraph_generated_2017,GluGluToHHTo2B2G_node_SM_13TeV_madgraph,GluGluToHHTo2B2G_node_SM_13TeV_madgraph_2017'.split(',')
#tpMap = {"GluGluToHHTo2B2G_node_SM_13TeV_madgraph_generated":"HHbbgg_2016","GluGluToHHTo2B2G_node_SM_13TeV_madgraph_generated_2017":"HHbbgg_2017","GluGluToHHTo2B2G_node_SM_13TeV_madgraph":"HHbbgg_2016_node","GluGluToHHTo2B2G_node_SM_13TeV_madgraph_2017":"HHbbgg_2017_node"}

sum_entries = dict()
sum_entries_bkg = dict()

entries_per_cat = dict()

tfile = TFile(filename)
ws = tfile.Get(wsname)
for name in names:
	print '%s\t'%(tpMap[name]),
	sum=0.
	lumi = 1.
	if '2017' in name : lumi = lumi_2017
	else : lumi = lumi_2016
	entries_per_cat[tpMap[name]] = [] 
	for cat in range(0,num_cat):
		ws_name = 'hggpdfsmrel_13TeV_%s_DoubleHTag_%d_norm'%(name,cat)
		#print "Trying to get "+ws_name
		var = (ws.var('MH'))
		var.setVal(125.)
		entries = (ws.function(ws_name).getVal())
		sum_entries[name] = entries
		#print entries , lumi
		count = entries*lumi
		if 'HHbbgg' in tpMap[name] : 
			count*=SMsignal
		#	if 'node' in tpMap[name] : count*=2.
		sum+=count
		entries_per_cat[tpMap[name]].append(count)
	#	print '%.2f\t'%(count),
		print '%.4f\t'%(count),'%s'%symbol,
	print '%.2f'%sum



#tfile = TFile(filename_bkg)
#ws_bkg = tfile.Get(wsname_bkg)
#sum_bkg=0.
#dataname = 'Data 2016+2017'
#print '%s\t'%dataname,
#entries_per_cat[dataname] = [] 
#for cat in range(0,num_cat):
#	name = 'roohist_data_mass_DoubleHTag_%d'%(cat)
#	entries = ws_bkg.data(name).sumEntries()
#	sum_entries_bkg[name] = entries
#	sum_bkg+=entries
#	entries_per_cat[dataname].append(entries)
##	print '%d\t'%(entries),'&',
##	print '%d\t'%(entries),'%s'%symbol,
##print '%d'%sum_bkg

########################
#filename_bkg_2016 = '/afs/cern.ch/work/n/nchernya/ETH/DiHiggs/root_file/13_12_2018/2016/output_DoubleEG_micheli-ReMiniAOD2016-DeepCSV-bRegression-prod-uAOD-all.root'
#filename_bkg_2017 = '/afs/cern.ch/work/n/nchernya/ETH/DiHiggs/root_file/13_12_2018/2017/output_DoubleEG_spigazzi-RunIIFall17-3_2_0-RunIIFall17-3_2_0-all.root'
#filename_bkg_total = '/afs/cern.ch/work/n/nchernya/ETH/DiHiggs/root_file/13_12_2018/output_DoubleEG_2016_2017_13_12_2018.root'
#filename_bkg_2016 = '/work/nchernya/DiHiggs/inputs/27_02_2019/2016/output_DoubleEG_micheli-ReMiniAOD2016-DeepCSV-27_02_2019.root'
#filename_bkg_2017 = '/work/nchernya/DiHiggs/inputs/27_02_2019/2017/output_DoubleEG_spigazzi-RunIIFall17-3_2_0-RunIIFall17-27_02_2019.root'
#filename_bkg_total = '/work/nchernya/DiHiggs/inputs/27_02_2019/output_DoubleEG_2016_2017_27_02_2019.root'
#filename_bkg_2016 = '/work/nchernya/DiHiggs/inputs/01_03_2019/output_DoubleEG_2016.root'
#filename_bkg_2017 = '/work/nchernya/DiHiggs/inputs/01_03_2019/output_DoubleEG_2017_only_13_12_2018.root'
#filename_bkg_total = '/work/nchernya/DiHiggs/inputs/01_03_2019/output_DoubleEG_2016_2017_01_03_2019.root'
filename_bkg_2016 = '/eos/user/f/fmonti/HHbbgg_run2/workspaces/2016/TAGSORTER_HHwithttHkiller_ttHlep_ttHhad/output_DoubleEG_micheli-LegacyReReco-20180629-1-v0-Run2016.root'
filename_bkg_2017 = '/eos/user/f/fmonti/HHbbgg_run2/workspaces/2017/TAGSORTER_HHwithttHkiller_ttHlep_ttHhad/output_DoubleEG_spigazzi-RunIIFall17-3_2_0-RunIIFall17-3_2_0-v0-Run2017.root'
filename_bkg_total = '/eos/user/f/fmonti/HHbbgg_run2/workspaces/output_DoubleEG_2016_2017_v2.root'
years=['2016','2017','Total']
print 'Data with blinded 115 < Mgg < 135'
for num,name in enumerate([filename_bkg_2016,filename_bkg_2017,filename_bkg_total]):
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
