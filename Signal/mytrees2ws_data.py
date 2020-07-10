import os
import pandas as pd
import root_pandas as rpd
import numpy as np
import ROOT
import json

from root_numpy import tree2array

from optparse import OptionParser

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#def add_mc_vars_to_workspace(ws=None, systematics_labels=[],add_benchmarks = False):
def add_mc_vars_to_workspace(ws=None,mjjLow=70, systematics_labels=[],add_benchmarks = False):

  IntLumi = ROOT.RooRealVar("IntLumi","IntLumi",1000)
  IntLumi.setConstant(True)
  getattr(ws, 'import')(IntLumi)

  weight = ROOT.RooRealVar("weight","weight",1)
  weight.setConstant(False)
  getattr(ws, 'import')(weight)

  CMS_hgg_mass = ROOT.RooRealVar("CMS_hgg_mass","CMS_hgg_mass",125,100,180)
  CMS_hgg_mass.setConstant(False)
  #CMS_hgg_mass.setBins(160)
  CMS_hgg_mass.setBins(80)
  getattr(ws, 'import')(CMS_hgg_mass)

  Mjj = ROOT.RooRealVar("Mjj","Mjj",125,mjjLow,190)
  Mjj.setConstant(False)
  if mjjLow==90 : Mjj.setBins(25)
  else : Mjj.setBins(30)
  getattr(ws, 'import')(Mjj)

  dZ = ROOT.RooRealVar("dZ","dZ",0.0,-20,20)
  dZ.setConstant(False)
  dZ.setBins(40)
  getattr(ws, 'import')(dZ)

#  ttHScore = ROOT.RooRealVar("ttHScore","ttHScore",0.5,0.,1.)
#  ttHScore.setConstant(False)
#  ttHScore.setBins(40)
#  getattr(ws, 'import')(ttHScore)


def apply_selection(data=None,reco_name=None):
  #function to split up ttree into recobins
  #if 'reco5' in reco_name: recobin_data = data[(data['pTH_reco']>=350.)]
  #recobin_data = recobin_data[((recobin_data['mgg']>=100.)&(recobin_data['mgg']<=180.))]
  return recobin_data
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def add_dataset_to_workspace(data=None,ws=None,name=None,systematics_labels=[],add_benchmarks = False, benchmark_num = -1, benchmark_norm = 1.):

  #apply selection to extract correct recobin
  #recobin_data = apply_selecetion(data,selection_name)

  #define argument set  
  arg_set = ROOT.RooArgSet(ws.var("weight"))
  variables = ["CMS_hgg_mass","Mjj","dZ" ]#, "ttHScore"] #ttHScore
  for var in variables :
      arg_set.add(ws.var(var))

  #define roodataset to add to workspace
  roodataset = ROOT.RooDataSet (name, name, arg_set, "weight" )

  #Fill the dataset with values
  for index,row in data.iterrows():
    for var in variables:
      if var=='dZ' :  #to ensure only one fit (i.e. all RV fit)
        ws.var(var).setVal( 0. )
        ws.var(var).setConstant()
      else : 
        ws.var(var).setVal( row[ var ] )

    w_val = row['weight']

    roodataset.add( arg_set, w_val )

  #Add to the workspace
  getattr(ws, 'import')(roodataset)

  return [name]
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  
def get_options():

    parser = OptionParser()
    parser.add_option("--inp-files",type='string',dest='inp_files',default='/eos/user/f/fmonti/HHbbgg_run2/workspaces/FEB2020/DoubleEG/output_DoubleEG_all3years.root')  #2016
    parser.add_option("--out-dir",type='string',dest="out_dir",default='/eos/user/f/fmonti/HHbbgg_run2/workspaces/FEB2020/DoubleEG/ws/')
    parser.add_option("--outtag",type='string',dest="outtag",default='_cats70GeV')
    parser.add_option("--MjjLow",type='float',dest="MjjLow",default='70')
    parser.add_option("--cats",type='string',dest="cats",default='DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11,TTHHadronicTag_0,TTHHadronicTag_1,TTHHadronicTag_2,TTHHadronicTag_3,TTHLeptonicTag_0,TTHLeptonicTag_1,TTHLeptonicTag_2,TTHLeptonicTag_3')
    return parser.parse_args()
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  

(opt,args) = get_options()
cats = opt.cats.split(',')
input_files = opt.inp_files.split(',')
target_names = []

for num,f in enumerate(input_files):
   print 'doing file ',f
   target_names.append('Data_13TeV') 
   tfile = ROOT.TFile(f)
   #define roo fit workspace
   datasets=[]
   ws = ROOT.RooWorkspace("cms_hgg_13TeV", "cms_hgg_13TeV")
   #Assemble roorealvariable set
   add_mc_vars_to_workspace( ws,opt.MjjLow,'' )  # do not add them for the main systematics file
   for cat in cats : 
       print 'doing cat ',cat
       name = target_names[num]+'_'+cat
       data = pd.DataFrame(tree2array(tfile.Get("tagsDumper/trees/%s"%name)))
       data['leadingJet_pt_Mjj'] = data['leadJet_pt']/data['Mjj']
       #data['subleadingJet_pt_Mjj'] = data['subleadingJet_pt']/data['Mjj'] #ivan
       if ('DoubleHTag' in cat):
         print "this is a DoubleHTag --> i require Mjj>0"
         data = data.query("(Mjj>0.)")
         if not ('VBFDoubleHTag' in cat): 
           print "this is NOT a VBFDoubleHTag --> I will require leadingJet_pt_Mjj>0.55" 
           data = data.query("(leadingJet_pt_Mjj>0.55)")  #1/2.5 for all categories
         if ('DoubleHTag_10' in cat) or ('DoubleHTag_11' in cat): 
           print "this is DoubleHTag_10 or DoubleHTag_11 --> I will require Mjj>90."
           data = data.query("(Mjj>90.)")  #1/2.5 for all categories
      
 
       datasets += add_dataset_to_workspace( data, ws, name,'') #systemaitcs[1] : this should be done for nominal only, to add weights
         
   outfilename = (opt.out_dir+"/"+os.path.basename(f)).replace(".root",opt.outtag+".root")
   print "saving output in "+outfilename
   f_out = ROOT.TFile.Open(outfilename,"RECREATE")
   dir_ws = f_out.mkdir("tagsDumper")
   dir_ws.cd()
   ws.Write()
   f_out.Close()
