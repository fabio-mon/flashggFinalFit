
SOMEINPUTFILE='/eos/user/f/fmonti/HHbbgg_run2/workspaces/2016/TAGSORTER_HHwithttHkiller_ttHlep_ttHhad/shifted/output_GluGluToHHTo2B2G_node_SM_13TeV-madgraph_125.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/2016/TAGSORTER_HHwithttHkiller_ttHlep_ttHhad/shifted/output_GluGluHToGG_M-125_13TeV_powheg_pythia8_125.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/2016/TAGSORTER_HHwithttHkiller_ttHlep_ttHhad/shifted/output_VBFHToGG_M-125_13TeV_powheg_pythia8_125.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/2016/TAGSORTER_HHwithttHkiller_ttHlep_ttHhad/shifted/output_ttHToGG_M125_13TeV_powheg_pythia8_v2_125.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/2016/TAGSORTER_HHwithttHkiller_ttHlep_ttHhad/shifted/output_VHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8_125.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/2017/TAGSORTER_HHwithttHkiller_ttHlep_ttHhad/shifted/output_GluGluToHHTo2B2G_node_SM_13TeV-madgraph_2017_125.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/2017/TAGSORTER_HHwithttHkiller_ttHlep_ttHhad/shifted/output_GluGluHToGG_M-125_13TeV_powheg_pythia8_2017_125.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/2017/TAGSORTER_HHwithttHkiller_ttHlep_ttHhad/shifted/output_VBFHToGG_M-125_13TeV_powheg_pythia8_2017_125.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/2017/TAGSORTER_HHwithttHkiller_ttHlep_ttHhad/shifted/output_ttHToGG_M125_13TeV_powheg_pythia8_2017_125.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/2017/TAGSORTER_HHwithttHkiller_ttHlep_ttHhad/shifted/output_VHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8_2017_125.root'

SIGNALFILE='/afs/cern.ch/user/f/fmonti/work/flashggFinalFit/CMSSW_7_4_7/src/flashggFinalFit/Signal/output/out_fit_13_06_2019_nodes2016/CMS-HGG_sigfit_merged.root,/afs/cern.ch/user/f/fmonti/work/flashggFinalFit/CMSSW_7_4_7/src/flashggFinalFit/Signal/output/out_fit_18_06_2019_nodes2017/CMS-HGG_sigfit_merged.root'

SMSIGNAL='GluGluToHHTo2B2G_node_SM_13TeV_madgraph,GluGluToHHTo2B2G_node_SM_13TeV_madgraph_2017'

DATAFILE='/afs/cern.ch/user/f/fmonti/work/flashggFinalFit/CMSSW_7_4_7/src/flashggFinalFit/Background/CMS-HGG_multipdf_HHbbgg_2016_2017_13_06_2019.root'

PROCS='GluGluHToGG_M_125_13TeV_powheg_pythia8,VBFHToGG_M_125_13TeV_powheg_pythia8,ttHToGG_M125_13TeV_powheg_pythia8_v2,VHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8,GluGluHToGG_M_125_13TeV_powheg_pythia8_2017,VBFHToGG_M_125_13TeV_powheg_pythia8_2017,ttHToGG_M125_13TeV_powheg_pythia8_2017,VHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8_2017'

CATS='DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11'

SCALES=""
SMEARS=""
SCALESCORR=""
SCALESGLOBAL=""
INTLUMI2016=35.9
INTLUMI2017=41.5

OUTPUTDATACARD="./mydatacard.txt"

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
--intLumi $INTLUMI2016 \
--intLumi2017 $INTLUMI2017 \
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