import pandas as pd
import root_pandas as rpd
import numpy as np
import ROOT
import json

from root_numpy import tree2array

from optparse import OptionParser

###BSM nodes for HHbbgg
whichNodes = ['SM']
#whichNodes = list(np.arange(0,12,1))
#whichNodes.append('SM')
#whichNodes.append('box')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def getSystLabelsWeights(isMET = False):
    phosystlabels=[]
    jetsystlabels=[]
    metsystlabels=[]
    systlabels=['']
    for direction in ["Up","Down"]:
     #   phosystlabels.append("MvaShift%s01sigma" % direction)
        phosystlabels.append("SigmaEOverEShift%s01sigma" % direction)
     #   phosystlabels.append("MaterialCentralBarrel%s01sigma" % direction)
     #   phosystlabels.append("MaterialOuterBarrel%s01sigma" % direction)
     #   phosystlabels.append("MaterialForward%s01sigma" % direction)
     #   phosystlabels.append("FNUFEB%s01sigma" % direction)
     #   phosystlabels.append("FNUFEE%s01sigma" % direction)
     #   phosystlabels.append("MCScaleGain6EB%s01sigma" % direction)
     #   phosystlabels.append("MCScaleGain1EB%s01sigma" % direction)
        jetsystlabels.append("JEC%s01sigma" % direction)
        jetsystlabels.append("JER%s01sigma" % direction)
     #   jetsystlabels.append("PUJIDShift%s01sigma" % direction)
     #   metsystlabels.append("metJecUncertainty%s01sigma" % direction)
     #   metsystlabels.append("metJerUncertainty%s01sigma" % direction)
     #   metsystlabels.append("metPhoUncertainty%s01sigma" % direction)
     #   metsystlabels.append("metUncUncertainty%s01sigma" % direction)
     #   for r9 in ["HighR9","LowR9"]:
     #       for region in ["EB","EE"]:
     #           phosystlabels.append("ShowerShape%s%s%s01sigma"%(r9,region,direction))
     #           phosystlabels.append("MCScale%s%s%s01sigma" % (r9,region,direction))
     #           for var in ["Rho","Phi"]:
     #               phosystlabels.append("MCSmear%s%s%s%s01sigma" % (r9,region,var,direction))
    systlabels += phosystlabels
    systlabels += jetsystlabels
    if isMET:
        systlabels += metsystlabels

    #systweights = ["UnmatchedPUWeight", "MvaLinearSyst", "LooseMvaSF", "PreselSF", "electronVetoSF", "TriggerWeight", "FracRVWeight", "FracRVNvtxWeight", "ElectronWeight", "MuonIDWeight", "MuonIsoWeight", "JetBTagCutWeight"] #, "JetBTagReshapeWeight"]
    systweights = ["JetBTagReshapeWeight","PreselSF", "electronVetoSF", "TriggerWeight","LooseMvaSF"] 
    return systlabels,systweights


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def add_mc_vars_to_workspace(ws=None, systematics_labels=[],add_benchmarks = False):
  IntLumi = ROOT.RooRealVar("IntLumi","IntLumi",1000)
  IntLumi.setConstant(True)
  getattr(ws, 'import')(IntLumi)

  weight = ROOT.RooRealVar("weight","weight",1)
  weight.setConstant(False)
  getattr(ws, 'import')(weight)
  
  btagweight = ROOT.RooRealVar("btagReshapeWeight","btagReshapeWeight",1)
  btagweight.setConstant(False)
  getattr(ws, 'import')(btagweight)

  CMS_hgg_mass = ROOT.RooRealVar("CMS_hgg_mass","CMS_hgg_mass",125,100,180)
  CMS_hgg_mass.setConstant(False)
  CMS_hgg_mass.setBins(160)
  getattr(ws, 'import')(CMS_hgg_mass)

  dZ = ROOT.RooRealVar("dZ","dZ",0.0,-20,20)
  dZ.setConstant(False)
  dZ.setBins(40)
  getattr(ws, 'import')(dZ)

 # ttHScore = ROOT.RooRealVar("ttHScore","ttHScore",0.5,0.,1.)
 # ttHScore.setConstant(False)
 # ttHScore.setBins(40)
 # getattr(ws, 'import')(ttHScore)

  if add_benchmarks: 
    # for benchmark_num in whichNodes:
    #     benchmark = ROOT.RooRealVar("benchmark_reweight_%s"%benchmark_num,"benchmark_reweight_%s"%benchmark_num,0,100.) 
    #     benchmark.setConstant(False)
     #    benchmark.setBins(40)
     #    getattr(ws, 'import')(benchmark)
     eventNumber = ROOT.RooRealVar("event","event",0,1000000.) 
     eventNumber.setConstant(False)
     eventNumber.setBins(40)
     getattr(ws, 'import')(eventNumber)

  if systematics_labels!=[] :
     directions = ["Up01sigma", "Down01sigma"]
     for syst in systematics_labels:
          for ddir in directions:
             rrv = ROOT.RooRealVar(str(syst)+str(ddir), str(syst)+str(ddir), -1000, 1000)
             rrv.setConstant(False)
             rrv.setBins(40)
             getattr(ws, 'import')(rrv)
     rrv = ROOT.RooRealVar("centralObjectWeight","centralObjectWeight", -1000, 1000)
     rrv.setConstant(False)
     rrv.setBins(40)
     getattr(ws, 'import')(rrv)



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def calculate_benchmark_normalization(normalizations,year,benchmark_num):
    return normalizations[year]["benchmark_%s_normalization"%benchmark_num]
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def apply_selection(data=None,reco_name=None):
  #function to split up ttree into recobins
  #if 'reco5' in reco_name: recobin_data = data[(data['pTH_reco']>=350.)]
  #recobin_data = recobin_data[((recobin_data['mgg']>=100.)&(recobin_data['mgg']<=180.))]
  return recobin_data
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def add_dataset_to_workspace(data=None,ws=None,name=None,systematics_labels=[],btag_norm = 1.,add_benchmarks = False, benchmark_num = -1, benchmark_norm = 1.):

  #apply selection to extract correct recobin
  #recobin_data = apply_selecetion(data,selection_name)

  #define argument set  
  arg_set = ROOT.RooArgSet(ws.var("weight"))
  variables = ["CMS_hgg_mass","dZ", "btagReshapeWeight"] #ttHScore
  if add_benchmarks :
  #   variables.append("benchmark_reweight_%s"%benchmark_num)
     variables.append("event")
  if systematics_labels!=[] :
    directions = ["Up01sigma", "Down01sigma"]
    for syst in systematics_labels:
        for ddir in directions:
           variables.append(syst+ddir)
    variables.append('centralObjectWeight')
  for var in variables :
      print var
      arg_set.add(ws.var(var))

  #define roodataset to add to workspace
  roodataset = ROOT.RooDataSet (name, name, arg_set, "weight" )

  if add_benchmarks :
      data['weight'] *= data["benchmark_reweight_%s"%benchmark_num]/benchmark_norm

#Restore normalization from the btag reshaping weights#
  data['weight'] *= btag_norm
#######################################################

  #Fill the dataset with values
  for index,row in data.iterrows():
    for var in variables:
      if var=='dZ' :  #to ensure only one fit (i.e. all RV fit)
        ws.var(var).setVal( 0. )
        ws.var(var).setConstant()
      else : 
        ws.var(var).setVal( row[ var ] )

    w_val = row['weight']

    if add_benchmarks :
      if row["event"]%2!=0 : 
          w_val = 0.
      else : w_val = w_val*2. ## because discaring exactly half of events 


    roodataset.add( arg_set, w_val )

  #Add to the workspace
  getattr(ws, 'import')(roodataset)

  return [name]
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  
def get_options():

    parser = OptionParser()
    #parser.add_option("--inp-files",type='string',dest='inp_files',default='qqh,tth,vh,ggh')  
    parser.add_option("--inp-files",type='string',dest='inp_files',default='hh')  
    parser.add_option("--inp-dir",type='string',dest="inp_dir",default='/scratch/nchernya/HHbbgg/04_02_2020/trees_systematics/')
    parser.add_option("--out-dir",type='string',dest="out_dir",default='/scratch/nchernya/HHbbgg/18_02_2020/workspaces_systematics/')
    parser.add_option("--cats",type='string',dest="cats",default='DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11')
    parser.add_option("--nosysts",action="store_true", dest="nosysts", default=False)
    parser.add_option("--year",type='string',dest="year",default='2016')
    parser.add_option("--add_benchmarks",action="store_true", dest="add_benchmarks",default=False)
    parser.add_option("--config",type='string',dest="config",default='/work/nchernya/DiHiggs/inputs/20_12_2019/reweighting_normalization_18_12_2019.json')
    parser.add_option("--btag_config",type='string',dest="btag_config",default='/work/nchernya/DiHiggs/inputs/20_12_2019/btagSF_08_04_2020.json')
    return parser.parse_args()
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  

(opt,args) = get_options()
year=opt.year
if opt.nosysts : systematics = [''],[]
else : systematics = getSystLabelsWeights()
mass = '125'
masses = [-5,5.]
cats = opt.cats.split(',')
input_files = opt.inp_files.split(',')
input_names = []
target_names = []
target_files = []
btag_normalization_dict = json.loads(open(opt.btag_config).read())
normalization_file = open(opt.config).read()
normalizations = json.loads(normalization_file)
if opt.add_benchmarks : print 'Adding benchmarks'

for num,f in enumerate(input_files):
   name=f
   if 'hh_SM' in f and not opt.add_benchmarks: name='hh'
   input_names.append(name+year+'_13TeV_125_13TeV')
   if 'hh' in f and not opt.add_benchmarks:
      target_names.append(f +'_generated_%s_13TeV'%year) 
      target_files.append('output_' + f + '_generated_%s'%year )
   else :
      target_names.append(f +'_%s_13TeV'%year)
      target_files.append('output_' + f +'_%s'%year )

#opt.inp_dir = opt.inp_dir+'/' + year + '/'

data_structure = pd.DataFrame(data=None)
for num,f in enumerate(input_files):
 print 'doing file ',f,input_names[num]
 #if 'hh' in f and year=='2016':  f='hh_nodes_5_12'
 tfile = ROOT.TFile(opt.inp_dir + "output_"+f+"_%s.root"%year)
 tfilename = opt.inp_dir + "output_"+f+"_%s.root"%year
 if not opt.add_benchmarks : whichNodes = [1]
 for benchmark_num in whichNodes:
   systematics_datasets = [] 
   #define roo fit workspace
   ws = ROOT.RooWorkspace("cms_hgg_13TeV", "cms_hgg_13TeV")
   #Assemble roorealvariable set
   systematics_to_run_with = systematics[0]
   if  not opt.nosysts : systematics_to_run_with = systematics[1] #systemaitcs[1] : this should be done for nominal only, to add weights
   add_mc_vars_to_workspace( ws,systematics_to_run_with,add_benchmarks=opt.add_benchmarks)
   for syst in systematics[0] : 
      for cat_num,cat in enumerate(cats) : 
         print 'doing cat ',cat
         btag_renorm  = btag_normalization_dict["%s%s"%(input_files[num],year)]
         if syst!='' : name = input_names[num]+'_'+cat+'_'+syst
         else : name = input_names[num]+'_'+cat
         #if 'ggh' in f and year=='2016':  name='GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8_13TeV_'+cat #tmp  
         #data = pd.DataFrame(tree2array(tfile.Get("tagsDumper/trees/%s"%name)))
         if (tfile.Get("tagsDumper/trees/%s"%name).GetEntries())!=0 :
            data = rpd.read_root(tfilename,'tagsDumper/trees/%s'%name)
           # data['leadingJet_pt_Mjj'] = data['leadingJet_pt']/data['Mjj']
           # data = data.query("(leadingJet_pt_Mjj>0.55)")  #1/1.82 for all categories

            #if 'hh' in f and year=='2016': data =data.append(rpd.read_root(opt.inp_dir+"output_hh_2016_node_5_12.root",'tagsDumper/trees/%s'%name),ignore_index=True)  #just a tmp , ignore
            if cat_num == 0 :  data_structure = pd.DataFrame(data=None, columns=data.columns) 
         else :
            "USER WARNING : 0 events in ",f," syst ",syst," ,cat = ",cat 
            data = data_structure 
         if syst!='' : 
             newname = target_names[num]+'_'+mass+'_'+cat+'_'+syst
             if opt.add_benchmarks : newname =  newname.replace('hh','hh_node_%s'%benchmark_num)
         else : 
             newname = target_names[num]+'_'+mass+'_'+cat
             if opt.add_benchmarks : newname =  newname.replace('hh','hh_node_%s'%benchmark_num)
         
         if syst=='' and not opt.nosysts : systematics_labels = systematics[1] #systemaitcs[1] : this should be done for nominal only, to add weights
         else : systematics_labels =[] 
         if not opt.add_benchmarks : systematics_datasets += add_dataset_to_workspace( data, ws, newname,systematics_labels,btag_norm = btag_renorm) # this should be done for nominal only, to add weights
         else : systematics_datasets += add_dataset_to_workspace( data, ws, newname,systematics_labels,btag_norm = btag_renorm, add_benchmarks=opt.add_benchmarks,benchmark_num=benchmark_num,benchmark_norm = calculate_benchmark_normalization(normalizations,year,benchmark_num))
         #print newname, " ::: Entries =", ws.data(newname).numEntries(), ", SumEntries =", ws.data(newname).sumEntries()

         masses_array = masses
         if syst!='' and not opt.nosysts : masses_array = [] # for nominal systematics consider all masses, for systematics Up/Down only nominal mass 
         for newmass in masses_array :
             value = newmass + int(mass) 
             if syst!='' : 
               massname = target_names[num]+'_%d_'%value+cat+'_'+syst
               if opt.add_benchmarks : massname =  massname.replace('hh','hh_node_%s'%benchmark_num)
             else : 
               massname = target_names[num]+"_%d_"%value+cat
               if opt.add_benchmarks : massname =  massname.replace('hh','hh_node_%s'%benchmark_num)
             newdataset = (ws.data(newname)).Clone(massname)
             newdataset.changeObservableName("CMS_hgg_mass","CMS_hgg_mass_old")
             oldmass = newdataset.get()["CMS_hgg_mass_old"]
             mass_new = ROOT.RooFormulaVar( "CMS_hgg_mass", "CMS_hgg_mass", "(@0+%.1f)"%float(mass),ROOT.RooArgList(oldmass) );
             newdataset.addColumn(mass_new).setRange(100,180)
             getattr(ws, 'import')(newdataset)
             systematics_datasets += massname
         
   #export ws to file
   outname = target_files[num]
   if opt.add_benchmarks : 
      outname = outname.replace('hh','hh_node_%s'%benchmark_num)
   f_out = ROOT.TFile.Open("%s/%s.root"%(opt.out_dir,outname),"RECREATE")
   dir_ws = f_out.mkdir("tagsDumper")
   dir_ws.cd()
   ws.Write()
   f_out.Close()
