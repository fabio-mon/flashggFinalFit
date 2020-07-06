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



def reweight_rho(what,df0,df1,df_to_be_reweighted):
    m0, bins = np.histogram(df0[what],bins=np.linspace(0,70,35),weights=df0["weight"],normed=True)
    m1, _ = np.histogram(df1[what],bins=bins,weights=df1["weight"],normed=True)
    #weights = m0.astype(np.float32) / m1.astype(np.float32)
    weights = np.divide(m0.astype(np.float32), m1.astype(np.float32), out=np.ones_like(m0.astype(np.float32)), where=(m1.astype(np.float32)!=0))
    weights[np.isnan(weights)] = 1.
    weights[np.where(bins[:-1]>50)] = 1.
    df_to_be_reweighted["%s_bin"%what] = pd.cut(df_to_be_reweighted[what],bins,labels=range(0,bins.shape[-1]-1))
    rewei = df_to_be_reweighted[["%s_bin"%what,"weight"]].apply(lambda x: weights[x[0]]*x[1], axis=1, raw=True)
    df_to_be_reweighted["weight"] = rewei * df_to_be_reweighted["weight"].sum() / rewei.sum()


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def getSystLabelsWeights(isMET = False):
    phosystlabels=[]
    jetsystlabels=[]
    metsystlabels=[]
    systlabels=['']
    for direction in ["Up","Down"]:
        phosystlabels.append("MvaShift%s01sigma" % direction)
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
        jetsystlabels.append("PUJIDShift%s01sigma" % direction)
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

    systweights = [ "PreselSF", "electronVetoSF", "TriggerWeight", "FracRVWeight",  "MuonIDWeight", "MuonIsoWeight", "ElectronIDWeight", "ElectronRecoWeight", "JetBTagReshapeWeight"] #, "JetBTagReshapeWeight"]
    #systweights = ["JetBTagReshapeWeight","PreselSF", "electronVetoSF", "TriggerWeight","LooseMvaSF"] 
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

  Mjj = ROOT.RooRealVar("Mjj","Mjj",125,70,190)
  Mjj.setConstant(False)
  #Mjj.setBins(480)
  Mjj.setBins(120)
  getattr(ws, 'import')(Mjj)


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
def add_dataset_to_workspace(data=None,ws=None,name=None,systematics_labels=[],btag_norm = 1.,nlo_renormalization = 1.,save_every_nth_event = 1,add_benchmarks = False, benchmark_num = -1, benchmark_norm = 1.):

  #apply selection to extract correct recobin
  #recobin_data = apply_selecetion(data,selection_name)

  #define argument set  
  arg_set = ROOT.RooArgSet(ws.var("weight"))
  variables = ["CMS_hgg_mass","Mjj","dZ" ] #, "btagReshapeWeight"] #ttHScore
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
#Apply proper NNLO x BR for NLO samples, otherwise x 1. is applied
  data['weight'] *= nlo_renormalization 
  
  data.event = data.event.astype('int64')
  total_sum_events = sum(data['weight'])
  used_sum_events = sum(data.query('event %% %d!=0'%save_every_nth_event)['weight']) #using only events not used in the training

  #Fill the dataset with values
  for index,row in data.iterrows():
    for var in variables:
      if var=='dZ' :  #to ensure only one fit (i.e. all RV fit)
        ws.var(var).setVal( 0. )
        ws.var(var).setConstant()
      else : 
        ws.var(var).setVal( row[ var ] )

    w_val = row['weight']

    if save_every_nth_event!=1 : #if it is 1 then we do not need to discard any events
      if row["event"]%save_every_nth_event==0 : 
          w_val = 0.
      else : w_val = w_val*total_sum_events/used_sum_events ## because discaring exactly half of events 


    roodataset.add( arg_set, w_val )

  #Add to the workspace
  getattr(ws, 'import')(roodataset)

  return [name]
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  
def eval_nnlo_xsec_ggF(kl):
   SF = 1.115  #1.115 is sigma_NNLO+FTapprox / sigma_NLO for SM = 31.05/27.84
   #fit to the parabola  
   A = 62.5339
   eA = 2.9369
   B = -44.3231
   eB = 1.9286
   C = 9.6340
   eC = 0.5185
   
   return SF*(A+B*kl+C*kl*kl)   
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  
def get_options():

    parser = OptionParser()
    ###########################For final result before unblinding with VBF add lepton Veto #####################
    parser.add_option("--inp-files",type='string',dest='inp_files',default='qqh,tth,vh,ggh')  
    #parser.add_option("--inp-files",type='string',dest='inp_files',default='hh')  
    #parser.add_option("--inp-files",type='string',dest='inp_files',default='qqHH_CV_1_C2V_1_kl_1,qqHH_CV_1_C2V_2_kl_1,qqHH_CV_1_C2V_1_kl_2,qqHH_CV_1_C2V_1_kl_0,qqHH_CV_0p5_C2V_1_kl_1,qqHH_CV_1p5_C2V_1_kl_1')  
    #parser.add_option("--inp-files",type='string',dest='inp_files',default='hh_nlo_cHHH0,hh_nlo_cHHH1,hh_nlo_cHHH2p45,hh_nlo_cHHH5,qqHH_CV_1_C2V_1_kl_1,qqHH_CV_1_C2V_2_kl_1,qqHH_CV_1_C2V_1_kl_2,qqHH_CV_1_C2V_1_kl_0,qqHH_CV_0p5_C2V_1_kl_1,qqHH_CV_1p5_C2V_1_kl_1')  
    #parser.add_option("--inp-files",type='string',dest='inp_files',default='hh_nlo_cHHH0,hh_nlo_cHHH1,hh_nlo_cHHH2p45,hh_nlo_cHHH5')  
    #parser.add_option("--inp-files",type='string',dest='inp_files',default='hh_nlo_cHHH0,hh_nlo_cHHH1,hh_nlo_cHHH2p45,hh_nlo_cHHH5')  
    #parser.add_option("--inp-dir",type='string',dest="inp_dir",default='/work/nchernya/DiHiggs/inputs/04_02_2020/trees/')
    #parser.add_option("--out-dir",type='string',dest="out_dir",default='/work/nchernya/DiHiggs/inputs/18_02_2020/')
    #parser.add_option("--inp-dir",type='string',dest="inp_dir",default='/work/nchernya/DiHiggs/inputs/18_02_2020/nlo_fixed/')
    #parser.add_option("--out-dir",type='string',dest="out_dir",default='/work/nchernya/DiHiggs/inputs/18_02_2020/nlo_updated/')
    #parser.add_option("--inp-dir",type='string',dest="inp_dir",default='/scratch/nchernya/HHbbgg/18_02_2020/trees_systematics/nlo/')
    #parser.add_option("--out-dir",type='string',dest="out_dir",default='/scratch/nchernya/HHbbgg/18_02_2020/workspaces_systematics/')
    parser.add_option("--inp-dir",type='string',dest="inp_dir",default='/work/nchernya/DiHiggs/inputs/16_06_2020/trees/')
    parser.add_option("--out-dir",type='string',dest="out_dir",default='/work/nchernya/DiHiggs/inputs/16_06_2020/')
    #parser.add_option("--cats",type='string',dest="cats",default='DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11')
    parser.add_option("--cats",type='string',dest="cats",default='DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11,VBFDoubleHTag_0,VBFDoubleHTag_1')
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
    parser.add_option("--nosysts",action="store_true", dest="nosysts", default=False)
    parser.add_option("--year",type='string',dest="year",default='2016')
    parser.add_option("--add_benchmarks",action="store_true", dest="add_benchmarks",default=False)
    parser.add_option("--config",type='string',dest="config",default='/work/nchernya/DiHiggs/inputs/20_12_2019/reweighting_normalization_18_12_2019.json')
    parser.add_option("--btag_config",type='string',dest="btag_config",default='/work/nchernya/DiHiggs/CMSSW_7_4_7/src/flashggFinalFit/MetaData_HHbbgg/btagSF_22_04_2020.json')
    parser.add_option("--LHEweight_rescale",type='string',dest="LHEweight_rescale",default='/work/nchernya/DiHiggs/CMSSW_7_4_7/src/flashggFinalFit/MetaData_HHbbgg/HH_NLO_gen_xsec_22_04_2020.json')
    parser.add_option("--doNLO",action="store_true", dest="doNLO",default=False)
    return parser.parse_args()
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  

BR_hhbbgg = 0.58*0.00227*2
qqHH_NNLO_kfactor = 1.0347 #1.726/1.668 is sigma_NNLO+FTapprox / sigma_MG5 for SM 

treeDirName = 'tagsDumper/trees/'
#treeDirName = ''
(opt,args) = get_options()
year=opt.year
if opt.nosysts : systematics = [''],[]
else : systematics = getSystLabelsWeights()
mass = '125'
masses = [-5,5.]
cats = opt.cats.split(',')
MVAcats = opt.MVAcats.split(',')
MXcats = opt.MXcats.split(',')
nMVA =len(MVAcats)-1 
nMX = int(len(cats)/(len(MVAcats)-1))
cat_def = {}
for mva_num in range(0,nMVA):
  for mx_num in range(0,nMX):
    cat_num = mva_num*nMX+mx_num 
    cat_name = "DoubleHTag_%d"%(cat_num)
    cat_def[cat_name] = {"MVA" : [],"MX":[]}
    cat_def[cat_name]["MVA"] = [float(MVAcats[nMVA - mva_num]),float(MVAcats[nMVA - (mva_num+1)])]
    cat_def[cat_name]["MX"] = [float(MXcats[mva_num*(nMX+1) + (nMX - mx_num)]),float(MXcats[mva_num*(nMX+1) + (nMX - (mx_num+1))])]
input_files = opt.inp_files.split(',')
input_names = []
target_names = []
target_files = []
btag_normalization_dict = json.loads(open(opt.btag_config).read())
LHEweight_rescale_dict = json.loads(open(opt.LHEweight_rescale).read())
normalization_file = open(opt.config).read()
normalizations = json.loads(normalization_file)
if opt.add_benchmarks : print 'Adding benchmarks'

for num,f in enumerate(input_files):
   name=f
   if 'hh_SM' in f and not opt.add_benchmarks: name='hh'
   if not opt.doNLO : 
      input_names.append(name+year+'_13TeV_125_13TeV')
      target_names.append(f +'_%s_13TeV'%year)
      target_files.append('output_' + f +'_%s'%year )
   elif not 'vbfhh' in name and not 'qqHH' in name:
      input_names.append('hh'+year+'_13TeV_125_13TeV')
      target = 'ggHH_kl_%s_kt_1'%(name[name.find('cHHH')+len('cHHH'):])
      target_names.append(target +'_%s_13TeV'%year)
      target_files.append('output_' + target +'_%s'%year )
   elif 'qqHH' in name :
      input_names.append('vbfhh'+year+'_13TeV_125_13TeV')
      target = name
      target_names.append(target +'_%s_13TeV'%year)
      target_files.append('output_' + target +'_%s'%year )

#opt.inp_dir = opt.inp_dir+'/' + year + '/'
#opt.inp_dir = opt.inp_dir+'/rho_rew_'+year+ '_v2/' #ivan

data_structure = pd.DataFrame(data=None)
for num,f in enumerate(input_files):
#for num,f in enumerate(opt.inp_files2D.split(',') ):  #ivan
 print 'doing file ',f,input_names[num]
 tfilename = opt.inp_dir + "output_"+f+"_%s.root"%year
 #tfilename = opt.inp_dir + "output_"+f+".root" #ivan
 tfile = ROOT.TFile(tfilename)
 if not opt.add_benchmarks : whichNodes = [1]
 save_every_nth_event = 1
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
         if syst!='' : 
             name = input_names[num]+'_'+cat+'_'+syst
             initial_name = input_names[num]+'_DoubleHTag_0_' + syst
         else : 
             name = input_names[num]+'_'+cat
             initial_name = input_names[num]+'_DoubleHTag_0'
         #if opt.doCategorization : selection = "(MX <= %.2f and MX > %.2f) and (MVAOutputTransformed <= %.2f and MVAOutputTransformed > %.2f) and (ttHScore >= %.2f) "%(cat_def[cat]["MX"][0],cat_def[cat]["MX"][1],cat_def[cat]["MVA"][0],cat_def[cat]["MVA"][1],opt.ttHScore)
         if opt.doCategorization : selection = "(MX <= %.2f and MX > %.2f) and (HHbbggMVA <= %.2f and HHbbggMVA > %.2f) and (ttHScore >= %.2f) "%(cat_def[cat]["MX"][0],cat_def[cat]["MX"][1],cat_def[cat]["MVA"][0],cat_def[cat]["MVA"][1],opt.ttHScore)
         if not opt.doCategorization : 
				initial_name = name
				selection = "(Mjj>0)"
         #data = pd.DataFrame(tree2array(tfile.Get("tagsDumper/trees/%s"%name)))
         if (tfile.Get("%s"%(treeDirName+initial_name)).GetEntries())!=0 :
            data = rpd.read_root(tfilename,'%s'%(treeDirName+initial_name)).query(selection)
            data['leadingJet_pt_Mjj'] = data['leadingJet_pt']/data['Mjj']
            data['subleadingJet_pt_Mjj'] = data['subleadingJet_pt']/data['Mjj']
            #data = data.query("(leadingJet_pt_Mjj>0.55)")  #1/2.5 for all categories
            if not 'VBFDoubleHTag' in cat : 
					data = data.query("(leadingJet_pt_Mjj>0.55)")  #1/2.5 for all categories
					print 'doing the pt/Mjj>0.55 cut' 

            if opt.doNLO and not ('qqHH' in target_names[num]) : data = data.query("(abs(genweight)<0.1)") #remove crazy LHE weights 
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
         else : systematics_labels =[] #systemaitcs[1] : this should be done for nominal only, to add weights
         nlo_renormalization = 1.
         if opt.doNLO and not ('qqHH' in target_names[num]): 
             sample_name = target_names[num][0:target_names[num].find('kt_1')+len('kt_1')]
             nlo_renormalization =  (eval_nnlo_xsec_ggF(LHEweight_rescale_dict[sample_name]['kl'])*BR_hhbbgg)*LHEweight_rescale_dict[sample_name]['LHE_SF_powheg'][year] #ggHH normalization for NLO samples
         if opt.doNLO and ('qqHH' in target_names[num]): 
             save_every_nth_event = 4 # one quater of events used for vbfhh training
             sample_name = target_names[num][0:target_names[num].find('_201')]#remove the year from the name
             nlo_renormalization =  LHEweight_rescale_dict[sample_name]['gen_xsec_MG5']*qqHH_NNLO_kfactor*BR_hhbbgg #qqHH normalization
             print  LHEweight_rescale_dict[sample_name]['gen_xsec_MG5'], qqHH_NNLO_kfactor, BR_hhbbgg #qqHH normalization
         print nlo_renormalization,sum(data["weight"]) 
         if not opt.add_benchmarks : systematics_datasets += add_dataset_to_workspace( data, ws, newname,systematics_labels,btag_norm = btag_renorm,nlo_renormalization=nlo_renormalization,save_every_nth_event=save_every_nth_event) #systemaitcs[1] : this should be done for nominal only, to add weights
         else :
             save_every_nth_event=1 
             systematics_datasets += add_dataset_to_workspace( data, ws, newname,systematics_labels,btag_norm = btag_renorm,nlo_renormalization=nlo_renormalization,save_every_nth_event=save_every_nth_event, add_benchmarks=opt.add_benchmarks,benchmark_num=benchmark_num,benchmark_norm = calculate_benchmark_normalization(normalizations,year,benchmark_num))
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
