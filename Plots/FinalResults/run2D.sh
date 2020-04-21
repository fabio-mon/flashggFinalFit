#!/bin/bash

#1;5202;0cDATE="04_02_2020"
#DATE="04_02_2020_mjjnorm"
DATE="MAR1620"
#name2D=BG_MCbgbjets
#name2D=DoubleEG
#name2D=BG_MCbg
#outtag=ivanjson
#outtag=ivanjsonMC
name2D=$1
outtag=$2

combineout=HHbbgg2D_${name2D}_${outtag}_${DATE}
DATACARD="/afs/cern.ch/user/f/fmonti/work/NewflashggFinalFit/CMSSW_10_2_13/src/HiggsAnalysis/CombinedLimit/out/nadyaws/cms_HHbbgg2D_DoubleEG_cats70GeV_ftest_datacard_nodeSM_18_02_2020_cats90GeV_MjjRenamed_systematics.txt"
DATACARDroot="/afs/cern.ch/user/f/fmonti/work/NewflashggFinalFit/CMSSW_10_2_13/src/HiggsAnalysis/CombinedLimit/out/nadyaws/cms_HHbbgg2D_DoubleEG_cats70GeV_ftest_datacard_nodeSM_18_02_2020_cats90GeV_MjjRenamed_systematics.root"
#DATACARD="/afs/cern.ch/user/f/fmonti/work/flashggFinalFit2/CMSSW_7_4_7/src/flashggFinalFit/Datacard/cards/FEB2020_onlyHHsignal_alltags/SMdatacard.txt"
#DATACARDroot="/afs/cern.ch/user/f/fmonti/work/flashggFinalFit2/CMSSW_7_4_7/src/flashggFinalFit/Datacard/cards/FEB2020_onlyHHsignal_alltags/SMdatacard.root"

echo $name2D 
echo $outtag

text2workspace.py $DATACARD --channel-masks 

combine $DATACARDroot  -n $combineout  -M MultiDimFit -m 125. --saveWorkspace -t -1 --X-rtd TMCSO_AdaptivePseudoAsimov=0 --X-rtd TMCSO_PseudoAsimov=0 --cminDefaultMinimizerStrategy 0 --cminFallbackAlgo Minuit2,Migrad,0:0.1 --X-rt MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 --saveSpecifiedIndex pdfindex_DoubleHTag_0_13TeV,pdfindex_DoubleHTag_1_13TeV,pdfindex_DoubleHTag_2_13TeV,pdfindex_DoubleHTag_3_13TeV,pdfindex_DoubleHTag_4_13TeV,pdfindex_DoubleHTag_5_13TeV,pdfindex_DoubleHTag_6_13TeV,pdfindex_DoubleHTag_7_13TeV,pdfindex_DoubleHTag_8_13TeV,pdfindex_DoubleHTag_9_13TeV,pdfindex_DoubleHTag_10_13TeV,pdfindex_DoubleHTag_11_13TeV  #--setParameters mask_TTHHadronicTag_0_13TeV=1,mask_TTHHadronicTag_1_13TeV=1,mask_TTHHadronicTag_2_13TeV=1,mask_TTHHadronicTag_3_13TeV=1,mask_TTHLeptonicTag_0_13TeV=1,mask_TTHLeptonicTag_1_13TeV=1,mask_TTHLeptonicTag_2_13TeV=1,mask_TTHLeptonicTag_3_13TeV=1

combine higgsCombine${combineout}.MultiDimFit.mH125.root --snapshotName MultiDimFit -n $combineout  -M AsymptoticLimits -m 125. --saveWorkspace -t -1 --run=blind --X-rtd TMCSO_AdaptivePseudoAsimov=0 --X-rtd TMCSO_PseudoAsimov=0 --cminDefaultMinimizerStrategy 0 --cminFallbackAlgo Minuit2,Migrad,0:0.1 --X-rt MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 --saveSpecifiedIndex pdfindex_DoubleHTag_0_13TeV,pdfindex_DoubleHTag_1_13TeV,pdfindex_DoubleHTag_2_13TeV,pdfindex_DoubleHTag_3_13TeV,pdfindex_DoubleHTag_4_13TeV,pdfindex_DoubleHTag_5_13TeV,pdfindex_DoubleHTag_6_13TeV,pdfindex_DoubleHTag_7_13TeV,pdfindex_DoubleHTag_8_13TeV,pdfindex_DoubleHTag_9_13TeV,pdfindex_DoubleHTag_10_13TeV,pdfindex_DoubleHTag_11_13TeV #--setParameters mask_TTHHadronicTag_0_13TeV=1,mask_TTHHadronicTag_1_13TeV=1,mask_TTHHadronicTag_2_13TeV=1,mask_TTHHadronicTag_3_13TeV=1,mask_TTHLeptonicTag_0_13TeV=1,mask_TTHLeptonicTag_1_13TeV=1,mask_TTHLeptonicTag_2_13TeV=1,mask_TTHLeptonicTag_3_13TeV=1

