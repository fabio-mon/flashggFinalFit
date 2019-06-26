import ROOT
from ROOT import *
from optparse import OptionParser, make_option
import sys
import os
import numpy as np


parser = OptionParser(option_list=[
#2017
#    make_option("--inp-files",type='string',dest='inp_files',default='GluGluToHHTo2B2G_node_SM_13TeV-madgraph,GluGluHToGG_M-125_13TeV_powheg_pythia8,VBFHToGG_M-125_13TeV_powheg_pythia8,VHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8,ttHToGG_M125_13TeV_powheg_pythia8'),
#    make_option("--inp-dir",type='string',dest="inp_dir",default='/eos/user/f/fmonti/HHbbgg_run2/workspaces/2017/TAGSORTER_HHwithttHkiller_ttHlep_ttHhad/renamed_v2/'),
#    make_option("--out-dir",type='string',dest="out_dir",default='/eos/user/f/fmonti/HHbbgg_run2/workspaces/2017/TAGSORTER_HHwithttHkiller_ttHlep_ttHhad/shifted_v2/'),
#    make_option("--cats",type='string',dest="cats",default='DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11,TTHLeptonicTag_0,TTHLeptonicTag_1,ZHLeptonicTag,WHLeptonicTag,VHLeptonicLooseTag,TTHHadronicTag_0,TTHHadronicTag_1,TTHHadronicTag_2,VBFTag_0,VBFTag_1,VBFTag_2,VHMetTag,VHHadronicTag,UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3'),
#    make_option("--year",type='string',dest="year",default='2017'),
#2016
    make_option("--inp-files",type='string',dest='inp_files',default='GluGluToHHTo2B2G_node_SM_13TeV-madgraph,GluGluHToGG_M-125_13TeV_powheg_pythia8,VBFHToGG_M-125_13TeV_powheg_pythia8,VHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8,ttHToGG_M125_13TeV_powheg_pythia8_v2'),
    make_option("--inp-dir",type='string',dest="inp_dir",default='/eos/user/f/fmonti/HHbbgg_run2/workspaces/2016/TAGSORTER_HHwithttHkiller_ttHlep_ttHhad/'),
    make_option("--out-dir",type='string',dest="out_dir",default='/eos/user/f/fmonti/HHbbgg_run2/workspaces/2016/TAGSORTER_HHwithttHkiller_ttHlep_ttHhad/shifted_v2/'),
    make_option("--cats",type='string',dest="cats",default='DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11,TTHLeptonicTag_0,TTHLeptonicTag_1,ZHLeptonicTag,WHLeptonicTag,VHLeptonicLooseTag,TTHHadronicTag_0,TTHHadronicTag_1,TTHHadronicTag_2,VBFTag_0,VBFTag_1,VBFTag_2,VHMetTag,VHHadronicTag,UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3'),
    make_option("--year",type='string',dest="year",default='2016'),
])

(options, args) = parser.parse_args()
cats = options.cats.split(',')
input_files = options.inp_files.split(',')

###################for nodes only#####################
#input_files=[]
#whichNodes = list(np.arange(0,12,1))
#whichNodes.append('SM')
#whichNodes.append('box')
#for i in whichNodes:
#	input_files.append('GluGluToHHTo2B2G_node_%s_13TeV-madgraph'%i)
######################################################

input_names = []
for num,f in enumerate(input_files):
	if '2016' in options.year : input_names.append(f.replace('-','_') +'_13TeV') #2016
	if '2017' in options.year : input_names.append(f.replace('-','_') +'_2017_13TeV')
	input_files[num] = 'output_' + f 

masses = [-5.,0.,5.]
higgs_mass = 125.
wsname = "tagsDumper/cms_hgg_13TeV"

for num,f in enumerate(input_files):
	print 'doing file ',f
	if '2016' in options.year : tfile = TFile(options.inp_dir + f+".root")  #2016
	if '2017' in options.year : tfile = TFile(options.inp_dir + f+"_2017.root") 
	ws = tfile.Get(wsname)
	for mass in masses :
			value = mass + higgs_mass 
			ws.Print()
			print 'doing mass ',mass
			cat_datasets=[]
			for cat in cats :
				print 'doing cat ',cat
				name = input_names[num]+'_125_'+cat
				oldname = input_names[num]+'_'+cat
				print 'oldname ',oldname
				print 'newname ',name
				if value!=125:
					#dataset = (ws.data(name)).Clone(input_names[num]+"_%d_"%value+cat)
					dataset = (ws.data(oldname)).Clone(input_names[num]+"_%d_"%value+cat).reduce(RooArgSet(ws.var("CMS_hgg_mass"),ws.var("dZ"),ws.var("centralObjectWeight")))
                                        dataset.SetName(input_names[num]+"_%d_"%value+cat)
					dataset.Print()
					dataset.changeObservableName("CMS_hgg_mass","CMS_hgg_mass_old")
					oldmass = dataset.get()["CMS_hgg_mass_old"]
					mass_new = RooFormulaVar( "CMS_hgg_mass", "CMS_hgg_mass", "(@0+%.1f)"%mass,RooArgList(oldmass) );
				#	dataset.SetName(input_names[num]+"_%d_"%value+cat)
					dataset.addColumn(mass_new).setRange(100,180)
					dataset.Print()
				else : 
                                        dataset = (ws.data(oldname).reduce(RooArgSet(ws.var("CMS_hgg_mass"),ws.var("dZ"),ws.var("centralObjectWeight"))))
                                        dataset.SetName(input_names[num]+'_125_'+cat)
				cat_datasets.append(dataset)

			f_new = options.out_dir + f +"_%d"%value
 			if '2017' in options.year : f_new = options.out_dir + f +"_2017_%d"%value
			out = TFile(f_new+".root","RECREATE")
			out.mkdir("tagsDumper")
			out.cd("tagsDumper")
			neww = RooWorkspace("cms_hgg_13TeV","cms_hgg_13TeV") ;
			for dat in cat_datasets:
				getattr(neww, 'import')(dat, RooCmdArg())
			neww.Write()
			out.Close()
#			delete dataset
#			delete oldmass
#			delete mass_new
#			delete neww
