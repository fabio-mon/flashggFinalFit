import ROOT
from ROOT import *
from optparse import OptionParser, make_option
import sys
import os


parser = OptionParser(option_list=[
    make_option("--inp-files",type='string',dest='inp_files',default='GluGluToHHTo2B2G_node_SM_13TeV-madgraph,GluGluHToGG_M-125_13TeV_powheg_pythia8,VBFHToGG_M-125_13TeV_powheg_pythia8,VHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8,ttHToGG_M125_13TeV_powheg_pythia8'),
    #make_option("--target-names",type='string',dest='target_names',default=''),
    make_option("--inp-dir",type='string',dest="inp_dir",default='/eos/user/f/fmonti/HHbbgg_run2/workspaces/2017/TAGSORTER_HHwithttHkiller_ttHlep_ttHhad/'),
    make_option("--year",type='string',dest="year",default='2017'),
    make_option("--out-dir",type='string',dest="out_dir",default='/eos/user/f/fmonti/HHbbgg_run2/workspaces/2017/TAGSORTER_HHwithttHkiller_ttHlep_ttHhad/renamed_v2/'),
    make_option("--cats",type='string',dest="cats",default='DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11,TTHLeptonicTag_0,TTHLeptonicTag_1,ZHLeptonicTag,WHLeptonicTag,VHLeptonicLooseTag,TTHHadronicTag_0,TTHHadronicTag_1,TTHHadronicTag_2,VBFTag_0,VBFTag_1,VBFTag_2,VHMetTag,VHHadronicTag,UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3'),])
    #make_option("--cats",type='string',dest="cats",default='DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11'),])

(options, args) = parser.parse_args()
cats = options.cats.split(',')
input_files = options.inp_files.split(',')
input_names = []
target_names = []
target_files = []
for num,f in enumerate(input_files):
	input_names.append(f.replace('-','_') +'_13TeV')
########################SM generated#################
#	if "2017" in options.year : target_names.append(f.replace('-','_') +'_generated_2017_13TeV')
#	else : target_names.append(f.replace('-','_') +'_generated_13TeV')
#	input_files[num] = 'output_' + f  +'_original_generated'
#	target_files.append('output_' + f + '_generated' )
#####################################################

	target_names.append(f.replace('-','_') +'_2017_13TeV')
	input_files[num] = 'output_' + f  
	target_files.append('output_' + f )

masses = [0.]
higgs_mass = 125.
wsname = "tagsDumper/cms_hgg_13TeV"

for num,f in enumerate(input_files):
	print 'doing file ',f
	tfile = TFile(options.inp_dir + f+".root") 
	ws = tfile.Get(wsname)
	for mass in masses :
			value = mass + higgs_mass 
			ws.Print()
			print 'doing mass ',mass
			cat_datasets=[]
			for cat in cats :
				print 'doing cat ',cat
				name = input_names[num]+'_'+cat
				print 'name ',name
				dataset = (ws.data(name)).Clone(target_names[num]+"_"+cat)
				dataset.Print()
				dataset.changeObservableName("CMS_hgg_mass","CMS_hgg_mass_oldname")
				oldmass = dataset.get()["CMS_hgg_mass_oldname"]
				mass_new = RooFormulaVar( "CMS_hgg_mass", "CMS_hgg_mass", "(@0+%.1f)"%mass,RooArgList(oldmass) );
				dataset.addColumn(mass_new).setRange(100,180)
				dataset.Print()
				cat_datasets.append(dataset)

			if "2017" in options.year : out = TFile(options.out_dir + target_files[num] +"_2017.root","RECREATE")
			else : out = TFile(options.out_dir + target_files[num] +".root","RECREATE")
			out.mkdir("tagsDumper")
			out.cd("tagsDumper")
			neww = RooWorkspace("cms_hgg_13TeV","cms_hgg_13TeV") ;
			for dat in cat_datasets:
				getattr(neww, 'import')(dat, RooCmdArg())
			neww.Write()
			out.Close()
