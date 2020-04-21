import ROOT
from ROOT import *
from optparse import OptionParser, make_option
import sys
import os
from math import sqrt
import json

date = '18_02_2020'

filename = '/work/nchernya/DiHiggs/inputs/18_02_2020/nlo_updated/'

symbol = ''  #for keynote
#symbol = '&'  #for latex

names="ggHH_kl_0_kt_1,ggHH_kl_1_kt_1,ggHH_kl_2p45_kt_1,ggHH_kl_5_kt_1".split(',')

sum_entries = dict()

entries_per_cat = dict()
num_cat = 12
for name in names:
	print '%s\t'%(name),
	entries_per_cat[name] = [] 
	for cat in range(0,num_cat):
		sum=0.
		for year in '2016,2017,2018'.split(','):
		#for year in '2018'.split(','):
			tfile = TFile(filename+'/output_%s_%s.root'%(name,year))
			wsname = 'tagsDumper/cms_hgg_13TeV'
			ws = tfile.Get(wsname)
			ws_name = '%s_%s_13TeV_125_DoubleHTag_%d'%(name,year,cat)
			#entries = (ws.data(ws_name).numEntries())
			entries = (ws.data(ws_name).sumEntries())
			sum+=entries
		entries_per_cat[name].append(sum)
		#print '%d\t'%(sum),'%s'%symbol,
		print '%3f\t'%(sum),'%s'%symbol,
	print 



