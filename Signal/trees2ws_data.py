import os
import pandas as pd
import numpy as np
import ROOT
import json

from root_numpy import tree2array

from optparse import OptionParser

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def add_mc_vars_to_workspace(ws=None, systematics_labels=[],add_benchmarks = False):
  IntLumi = ROOT.RooRealVar("IntLumi","IntLumi",1000)
  IntLumi.setConstant(True)
  getattr(ws, 'import')(IntLumi)

  weight = ROOT.RooRealVar("weight","weight",1)
  weight.setConstant(False)
  getattr(ws, 'import')(weight)

  CMS_hgg_mass = ROOT.RooRealVar("CMS_hgg_mass","CMS_hgg_mass",125,100,180)
  CMS_hgg_mass.setConstant(False)
  CMS_hgg_mass.setBins(160)
  getattr(ws, 'import')(CMS_hgg_mass)

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
  variables = ["CMS_hgg_mass","dZ"]#, "ttHScore"] #ttHScore
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
    parser.add_option("--cats",type='string',dest="cats",default='DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11,TTHHadronicTag_0,TTHHadronicTag_1,TTHHadronicTag_2,TTHHadronicTag_3,TTHLeptonicTag_0,TTHLeptonicTag_1,TTHLeptonicTag_2,TTHLeptonicTag_3')
    return parser.parse_args()
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  

(opt,args) = get_options()
cats = opt.cats.split(',')
input_files = opt.inp_files.split(',')
target_names = []

for num,f in enumerate(input_files):
   target_names.append('Data_13TeV') 
   input_files[num] = 'output_' + f 


for num,f in enumerate(input_files):
   print 'doing file ',f
   tfile = ROOT.TFile(opt.inp_dir + f+".root")
   #define roo fit workspace
   datasets=[]
   ws = ROOT.RooWorkspace("cms_hgg_13TeV", "cms_hgg_13TeV")
   #Assemble roorealvariable set
   add_mc_vars_to_workspace( ws,'' )  # do not add them for the main systematics file
   for cat in cats : 
       print 'doing cat ',cat
       name = target_names[num]+'_'+cat
       data = pd.DataFrame(tree2array(tfile.Get("tagsDumper/trees/%s"%name)))
 
       datasets += add_dataset_to_workspace( data, ws, name,'') #systemaitcs[1] : this should be done for nominal only, to add weights
         
   f_out = ROOT.TFile.Open("%s/%s.root"%(opt.out_dir,input_files[num]),"RECREATE")
   dir_ws = f_out.mkdir("tagsDumper")
   dir_ws.cd()
   ws.Write()
   f_out.Close()
