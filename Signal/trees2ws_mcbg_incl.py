import pandas as pd
import root_pandas as rpd
import numpy as np
import ROOT
import json
import os

from root_numpy import tree2array

from optparse import OptionParser

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def add_mc_vars_to_workspace(ws=None,mjjLow = 70, systematics_labels=[],add_benchmarks = False):
  IntLumi = ROOT.RooRealVar("IntLumi","IntLumi",1000)
  IntLumi.setConstant(True)
  getattr(ws, 'import')(IntLumi)

  weight = ROOT.RooRealVar("weight","weight",1)
  weight.setConstant(False)
  getattr(ws, 'import')(weight)

  CMS_hgg_mass = ROOT.RooRealVar("CMS_hgg_mass","CMS_hgg_mass",125,100,180)
  CMS_hgg_mass.setConstant(False)
  #CMS_hgg_mass.setBins(160)
  CMS_hgg_mass.setBins(101)
  getattr(ws, 'import')(CMS_hgg_mass)

  Mjj = ROOT.RooRealVar("Mjj","Mjj",125,mjjLow,190)
  Mjj.setConstant(False)
  #Mjj.setBins(480)
  Mjj.setBins(101)
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
def add_dataset_to_workspace(data=None,ws=None,name=None,SF=1.,lumi=1.):

  #apply selection to extract correct recobin
  #recobin_data = apply_selecetion(data,selection_name)

  #define argument set  
  arg_set = ROOT.RooArgSet(ws.var("weight"))
  variables = ["CMS_hgg_mass","dZ","Mjj" ]#, "ttHScore"] #ttHScore
  for var in variables :
      arg_set.add(ws.var(var))

  #define roodataset to add to workspace
  roodataset = ROOT.RooDataSet (name, name, arg_set, "weight" )

  data['weight'] *= SF 
  print 'applying SF = ', SF
  data['weight'] *= lumi
  print 'applying lumi = ', lumi

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


def cleanOverlapDiphotons(dataframe):
      print 'cleaning overlap from diphotons'
      dataframe['overlapSave']  = np.ones_like(dataframe.index).astype(np.int8)
      #for data this wont be called anyway
      for index, df in dataframe.iterrows(): 
        cflavLeading = 0 #correct flavours
        hflav = df['leadingJet_hflav'] #4 if c, 5 if b, 0 if light jets
        pflav = df['leadingJet_pflav']
        if  hflav != 0 :
            cflavLeading = hflav
        else : #not a heavy jet
            if abs(pflav) == 4 or abs(pflav) == 5 :
                cflavLeading = 0 
            else : cflavLeading = pflav
        
        cflavSubLeading = 0 
        hflav = df['subleadingJet_hflav'] #4 if c, 5 if b, 0 if light jets
        pflav = df['subleadingJet_pflav']
        if  hflav != 0 :
            cflavSubLeading = hflav
        else : #not a heavy jet
            if abs(pflav) == 4 or abs(pflav) == 5 :
                cflavSubLeading = 0 
            else : cflavSubLeading = pflav
            
            
        if abs(cflavSubLeading)==5 or abs(cflavLeading)==5 :
            dataframe.at[index,'overlapSave']=0
        else : dataframe.at[index,'overlapSave']=1
      dataframe["weight"] *= dataframe['overlapSave']

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  
def get_options():

    parser = OptionParser()
    #parser.add_option("--inp-files",type='string',dest='inp_files',default='DiPhotonJetsBox_,GJet_Pt-20to40_,GJet_Pt-40toInf_')  
    #parser.add_option("--inp-files",type='string',dest='inp_files',default='DiPhotonJetsBox_,DiPhotonJetsBox1BJet,DiPhotonJetsBox2BJets,GJet_Pt-20to40_,GJet_Pt-40toInf_')  
    parser.add_option("--inp-files",type='string',dest='inp_files',default='DiPhotonJetsBox_,DiPhotonJetsBox1BJet,DiPhotonJetsBox2BJets')  
  #  parser.add_option("--inp-files",type='string',dest='inp_files',default='DiPhotonJetsBox_,GJet_Pt-20to40_,GJet_Pt-40toInf_')  
    parser.add_option("--inp-dir",type='string',dest="inp_dir",default='/work/nchernya/DiHiggs/inputs/18_02_2020/vbfhh_mva095/')
    #parser.add_option("--out-dir",type='string',dest="out_dir",default='/work/nchernya/DiHiggs/inputs/18_02_2020/MCbgbjets_workspace_90GeV/')
    parser.add_option("--out-dir",type='string',dest="out_dir",default='/work/nchernya/DiHiggs/inputs/27_03_2020/')
    #parser.add_option("--inp-dir",type='string',dest="inp_dir",default='/scratch/nchernya/HHbbgg/ivan_ntuples_13_02_2020/')
    #parser.add_option("--out-dir",type='string',dest="out_dir",default='/work/nchernya/DiHiggs/inputs/15_02_2020/')
    parser.add_option("--outtag",type='string',dest="outtag",default='_cats70GeV')
    parser.add_option("--year",type='string',dest="year",default='2016')
    #parser.add_option("--cats",type='string',dest="cats",default='DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11')
    parser.add_option("--cats",type='string',dest="cats",default='DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11,VBFDoubleHTag_0')
    #parser.add_option("--cats",type='string',dest="cats",default='DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9')
    #parser.add_option("--cats",type='string',dest="cats",default='DoubleHTag_10,DoubleHTag_11')
    parser.add_option("--MjjLow",type='float',dest="MjjLow",default='70')
    #parser.add_option("--MVAcats",type='string',dest="MVAcats",default='0.44,0.67,0.79,1')
    #parser.add_option("--MXcats",type='string',dest="MXcats",default='250,385,470,640,10000,250,345,440,515,10000,250,330,365,545,10000')
   # parser.add_option("--MVAcats",type='string',dest="MVAcats",default='0.248,0.450,0.728,1')
   # parser.add_option("--MXcats",type='string',dest="MXcats",default='250,376,521,603,10000,250.,376,521,603,10000,250,376,521,603,10000')  #2d
    parser.add_option("--MVAcats",type='string',dest="MVAcats",default='0.37,0.62,0.78,1')
    parser.add_option("--MXcats",type='string',dest="MXcats",default='250,385,510,600,10000,250.,330,360,540,10000,250,330,375,585,10000')  #2d
    #parser.add_option("--MVAcats",type='string',dest="MVAcats",default='0.33,0.55,0.68,1')
    #parser.add_option("--MXcats",type='string',dest="MXcats",default='250,360,470,600,10000,250,330,365,540,10000,250,330,360,615,10000')
    parser.add_option("--ttHScore",type='float',dest="ttHScore",default=0.26)
    parser.add_option("--doCategorization",action="store_true", dest="doCategorization",default=False)
    return parser.parse_args()
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  

treeDirName = 'tagsDumper/trees/'
#treeDirName = ''
SF = 2.9
remove_diphoton_overlap = True
lumi_dict = {}
lumi_dict['2016'] = 35.9 
lumi_dict['2017'] = 41.5
lumi_dict['2018'] = 59.4
(opt,args) = get_options()
year=opt.year
cats = opt.cats.split(',')
MVAcats = opt.MVAcats.split(',')
MXcats = opt.MXcats.split(',')
nMVA =len(MVAcats)-1 
nMX = int(12/(len(MVAcats)-1))
cat_def = {}
for mva_num in range(0,nMVA):
  for mx_num in range(0,nMX):
    cat_num = mva_num*nMX+mx_num 
    cat_name = "DoubleHTag_%d"%(cat_num)
    cat_def[cat_name] = {"MVA" : [],"MX":[]}
    cat_def[cat_name]["MVA"] = [float(MVAcats[nMVA - mva_num]),float(MVAcats[nMVA - (mva_num+1)])]
    cat_def[cat_name]["MX"] = [float(MXcats[mva_num*(nMX+1) + (nMX - mx_num)]),float(MXcats[mva_num*(nMX+1) + (nMX - (mx_num+1))])]


opt.inp_dir = opt.inp_dir+'/' + year + '/'
#opt.inp_dir = opt.inp_dir+'/' + 'rho_rew_'+year+'_v2' + '/'   #ivan
files= os.listdir(opt.inp_dir)

input_files = []
for f in opt.inp_files.split(','):
   process  = [s for s in files if f in s]
   print process[0]
   input_files.append(process[0].replace('.root','').replace('output_','')) 
target_names = []
final_names = []

for num,f in enumerate(input_files):
   target_names.append(f.replace('-','_') +'_13TeV')
   final_names.append('Data_13TeV') 
   input_files[num] = 'output_' + f 


for num,f in enumerate(input_files):
   print 'doing file ',f
   tfile = ROOT.TFile(opt.inp_dir + f + '.root')
   tfilename = opt.inp_dir +f + '.root'
   #define roo fit workspace
   datasets=[]
   ws = ROOT.RooWorkspace("cms_hgg_13TeV", "cms_hgg_13TeV")
   #Assemble roorealvariable set
   add_mc_vars_to_workspace( ws,opt.MjjLow,'' )  # do not add them for the main systematics file
   for cat in cats : 
       print 'doing cat ',cat
       finalname = final_names[num]+'_'+cat
       initial_name = target_names[num]+'_DoubleHTag_0'
      # initial_name = "bbggSelectionTree" #ivan
       #data = pd.DataFrame(tree2array(tfile.Get("tagsDumper/trees/%s"%initial_name))).
       #selection = "(MX <= %.2f and MX > %.2f) and (HHbbggMVA <= %.2f and HHbbggMVA > %.2f) and (ttHScore >= %.2f) and ((nElectrons2018+nMuons2018)==0)"%(cat_def[cat]["MX"][0],cat_def[cat]["MX"][1],cat_def[cat]["MVA"][0],cat_def[cat]["MVA"][1],opt.ttHScore)
       selection = "(Mjj>0)"
       if opt.doCategorization : selection = "(MX <= %.2f and MX > %.2f) and (MVAOutputTransformed <= %.2f and MVAOutputTransformed > %.2f) and (ttHScore >= %.2f) "%(cat_def[cat]["MX"][0],cat_def[cat]["MX"][1],cat_def[cat]["MVA"][0],cat_def[cat]["MVA"][1],opt.ttHScore)
       if not opt.doCategorization : 
         initial_name = target_names[num]+'_'+cat
      # if '11' in cat or '10' in cat : selection+="and (Mjj>=90)"
       print 'doing selection ', selection
       #data = rpd.read_root(tfilename,'tagsDumper/trees/%s'%initial_name).query(selection)
       data = rpd.read_root(tfilename,'%s'%(treeDirName+initial_name)).query(selection)
       data['leadingJet_pt_Mjj'] = data['leadingJet_pt']/data['Mjj']
       data['subleadingJet_pt_Mjj'] = data['subleadingJet_pt']/data['Mjj']
     #  data = data.query("(leadingJet_pt_Mjj>0.4)")  #1/2.5 for all categories
       data = data.query("(leadingJet_pt_Mjj>0.55)")  #1/2.5 for all categories
       #if ('3' in cat) or ('7' in cat ) or ('11' in cat ) : 
       #    data = data.query("(leadingJet_pt_Mjj>0.4)")  #1/2.7 for all categories
       if remove_diphoton_overlap : 
         if 'DiPhotonJetsBox_' in f  : 
           print 'cleaning overlap from diphotons for sample ',f
           cleanOverlapDiphotons(data) #removing overlap from DiPhoton sample 
 
       datasets += add_dataset_to_workspace( data, ws, finalname,SF,lumi_dict[year]) 
         
   f_out = ROOT.TFile.Open("%s/%s%s_%s.root"%(opt.out_dir,input_files[num],opt.outtag,year),"RECREATE")
   dir_ws = f_out.mkdir("tagsDumper")
   dir_ws.cd()
   ws.Write()
   f_out.Close()
