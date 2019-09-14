
SOMEINPUTFILE='/eos/user/f/fmonti/HHbbgg_run2/workspaces/legacy_runII_v2_2017_ttHkillerON_first_HH_second_tthLep/shifted_v3/ggh2017_13TeV_125.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/legacy_runII_v2_2017_ttHkillerON_first_HH_second_tthLep/shifted_v3/hh2017_13TeV_125.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/legacy_runII_v2_2017_ttHkillerON_first_HH_second_tthLep/shifted_v3/qqh2017_13TeV_125.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/legacy_runII_v2_2017_ttHkillerON_first_HH_second_tthLep/shifted_v3/tth2017_13TeV_125.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/legacy_runII_v2_2017_ttHkillerON_first_HH_second_tthLep/shifted_v3/vh2017_13TeV_125.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/legacy_runII_v2_2018_ttHkillerON_first_HH_second_tthLep/shifted_v3/ggh2018_13TeV_125.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/legacy_runII_v2_2018_ttHkillerON_first_HH_second_tthLep/shifted_v3/hh2018_13TeV_125.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/legacy_runII_v2_2018_ttHkillerON_first_HH_second_tthLep/shifted_v3/qqh2018_13TeV_125.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/legacy_runII_v2_2018_ttHkillerON_first_HH_second_tthLep/shifted_v3/tth2018_13TeV_125.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/legacy_runII_v2_2018_ttHkillerON_first_HH_second_tthLep/shifted_v3/vh2018_13TeV_125.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/legacy_runII_vmix12_2016_ttHkillerON_first_HH_second_tthLep/shifted_v3/ggh2016_13TeV_125.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/legacy_runII_vmix12_2016_ttHkillerON_first_HH_second_tthLep/shifted_v3/hh2016_13TeV_125.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/legacy_runII_vmix12_2016_ttHkillerON_first_HH_second_tthLep/shifted_v3/qqh2016_13TeV_125.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/legacy_runII_vmix12_2016_ttHkillerON_first_HH_second_tthLep/shifted_v3/tth2016_13TeV_125.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/legacy_runII_vmix12_2016_ttHkillerON_first_HH_second_tthLep/shifted_v3/vh2016_13TeV_125.root'

#for simplicity one single rootfile with all the 3 years !!!
SIGNALFILE='/afs/cern.ch/user/f/fmonti/work/flashggFinalFit/CMSSW_7_4_7/src/flashggFinalFit/Signal/output/out_fit_12_8_2019_newNaming2_allyears.root'

#SMSIGNAL='hh2016,hh2017,hh2018'
SMSIGNAL='tth2016,tth2017,tth2018'
#SMSIGNAL='hh2016,hh2017,hh2018,tth2016,tth2017,tth2018'

DATAFILE='/afs/cern.ch/user/f/fmonti/work/flashggFinalFit/CMSSW_7_4_7/src/flashggFinalFit/Background/CMS-HGG_multipdf_HHbbgg_allyears_12_08_2019.root'

#PROCS='ggh2017,qqh2017,tth2017,vh2017,ggh2018,qqh2018,tth2018,vh2018,ggh2016,qqh2016,tth2016,vh2016'
PROCS='ggh2017,qqh2017,hh2017,vh2017,ggh2018,qqh2018,hh2018,vh2018,ggh2016,qqh2016,hh2016,vh2016'
#PROCS='ggh2016,qqh2016,vh2016,ggh2017,qqh2017,vh2017,ggh2018,qqh2018,vh2018'

#CATS='DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11'
CATS='DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11,TTHHadronicTag_0,TTHHadronicTag_1,TTHHadronicTag_2,TTHHadronicTag_3,TTHLeptonicTag_0,TTHLeptonicTag_1,TTHLeptonicTag_2,TTHLeptonicTag_3,UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,VBFTag_0,VBFTag_1,VBFTag_2,VHHadronicTag,VHLeptonicLooseTag,VHMetTag,WHLeptonicTag,ZHLeptonicTag'

SCALES=""
SMEARS=""
SCALESCORR=""
SCALESGLOBAL=""
INTLUMI2016=27.89
INTLUMI2017=41.00 
INTLUMI2018=38.79

OUTPUTDATACARD="./mydatacard_12_8_2019_newNaming2_allyears_v4onlyttHassignal.txt"

echo ./makeParametricModelDatacardFLASHgg.py \
-i $SOMEINPUTFILE \
-s $SIGNALFILE \
--signalProc $SMSIGNAL \
-d $DATAFILE \
-p $PROCS,$SMSIGNAL \
-c $CATS \
--photonCatScales $SCALES \
--photonCatSmears $SMEARS  \
--globalScales $SCALESGLOBAL \
--photonCatScalesCorr $SCALESCORR \
--isMultiPdf \
--intLumi2016 $INTLUMI2016 \
--intLumi2017 $INTLUMI2017 \
--intLumi2018 $INTLUMI2018 \
-o $OUTPUTDATACARD



return 
./makeParametricModelDatacardFLASHgg.py \
\
-d /afs/cern.ch/user/f/fmonti/work/flashggFinalFit/CMSSW_7_4_7/src/flashggFinalFit/Background/CMS-HGG_multipdf_HHbbgg_2016_2017_13_06_2019.root \
\
-s /afs/cern.ch/user/f/fmonti/work/flashggFinalFit/CMSSW_7_4_7/src/flashggFinalFit/Signal/output/out_fit_13_06_2019_nodes2016/CMS-HGG_sigfit_merged.root,/afs/cern.ch/user/f/fmonti/work/flashggFinalFit/CMSSW_7_4_7/src/flashggFinalFit/Signal/output/out_fit_18_06_2019_nodes2017/CMS-HGG_sigfit_merged.root \
\
-i /eos/user/f/fmonti/HHbbgg_run2/workspaces/2016/TAGSORTER_HHwithttHkiller_ttHlep_ttHhad/shifted/output_GluGluToHHTo2B2G_node_SM_13TeV-madgraph_125.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/2016/TAGSORTER_HHwithttHkiller_ttHlep_ttHhad/shifted/output_GluGluHToGG_M-125_13TeV_powheg_pythia8_125.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/2016/TAGSORTER_HHwithttHkiller_ttHlep_ttHhad/shifted/output_VBFHToGG_M-125_13TeV_powheg_pythia8_125.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/2016/TAGSORTER_HHwithttHkiller_ttHlep_ttHhad/shifted/output_ttHToGG_M125_13TeV_powheg_pythia8_v2_125.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/2016/TAGSORTER_HHwithttHkiller_ttHlep_ttHhad/shifted/output_VHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8_125.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/2017/TAGSORTER_HHwithttHkiller_ttHlep_ttHhad/shifted/output_GluGluToHHTo2B2G_node_SM_13TeV-madgraph_2017_125.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/2017/TAGSORTER_HHwithttHkiller_ttHlep_ttHhad/shifted/output_GluGluHToGG_M-125_13TeV_powheg_pythia8_2017_125.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/2017/TAGSORTER_HHwithttHkiller_ttHlep_ttHhad/shifted/output_VBFHToGG_M-125_13TeV_powheg_pythia8_2017_125.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/2017/TAGSORTER_HHwithttHkiller_ttHlep_ttHhad/shifted/output_ttHToGG_M125_13TeV_powheg_pythia8_2017_125.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/2017/TAGSORTER_HHwithttHkiller_ttHlep_ttHhad/shifted/output_VHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8_2017_125.root \
\
-p GluGluToHHTo2B2G_node_SM_13TeV_madgraph,GluGluHToGG_M_125_13TeV_powheg_pythia8,VBFHToGG_M_125_13TeV_powheg_pythia8,ttHToGG_M125_13TeV_powheg_pythia8_v2,VHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8,GluGluToHHTo2B2G_node_SM_13TeV_madgraph_2017,GluGluHToGG_M_125_13TeV_powheg_pythia8_2017,VBFHToGG_M_125_13TeV_powheg_pythia8_2017,ttHToGG_M125_13TeV_powheg_pythia8_2017,VHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8_2017 \
\
-c DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11 \
\
--photonCatScales ../Signal/dat/photonCatSyst.dat --photonCatSmears ../Signal/dat/photonCatSyst.dat --isMultiPdf --intLumi 35.9