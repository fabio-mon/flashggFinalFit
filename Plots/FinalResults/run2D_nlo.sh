#!/bin/bash

DATE="18_02_2020"
name2D=DoubleEG_cats70GeV
outtag=ftest
combineout=HHbbgg2D_${name2D}_${outtag}_${DATE}_nlo_kl1_screen2
DATACARD="/afs/cern.ch/user/f/fmonti/work/NewflashggFinalFit/CMSSW_10_2_13/src/HiggsAnalysis/CombinedLimit/out/MAR1620_HHNLOsignal_HHcats_WITHSYST_v4/SMdatacard.txt"
DATACARDroot="/afs/cern.ch/user/f/fmonti/work/NewflashggFinalFit/CMSSW_10_2_13/src/HiggsAnalysis/CombinedLimit/out/MAR1620_HHNLOsignal_HHcats_WITHSYST_v4/SMdatacard.root" 

echo $name2D 
echo $outtag

#text2workspace.py $DATACARD  -P HHModel:HHdefault
echo text2workspace.py $DATACARD 

#combine $DATACARDroot -n $combineout  -M AsymptoticLimits -m 125. --saveWorkspace -t -1 --run=blind --X-rtd TMCSO_AdaptivePseudoAsimov=0 --X-rtd TMCSO_PseudoAsimov=0 --cminDefaultMinimizerStrategy 0 --cminFallbackAlgo Minuit2,Migrad,0:0.1 --X-rt MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 --redefineSignalPOIs r --setParameters r_qqhh=1,r_gghh=1,kt=1,kl=1,CV=1,C2V=1 

echo combine $DATACARDroot -n $combineout  -M AsymptoticLimits -m 125. --saveWorkspace -t -1 --run=blind --X-rtd TMCSO_AdaptivePseudoAsimov=0 --X-rtd TMCSO_PseudoAsimov=0 --cminDefaultMinimizerStrategy 0 --cminFallbackAlgo Minuit2,Migrad,0:0.1 --X-rt MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2  


#combine $DATACARDroot  -n $combineout  -M MultiDimFit -m 125. --saveWorkspace -t -1 --X-rtd TMCSO_AdaptivePseudoAsimov=0 --X-rtd TMCSO_PseudoAsimov=0 --cminDefaultMinimizerStrategy 0 --cminFallbackAlgo Minuit2,Migrad,0:0.1 --X-rt MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2

#combine higgsCombine${combineout}.MultiDimFit.mH125.root --snapshotName MultiDimFit -n $combineout  -M AsymptoticLimits -m 125. --saveWorkspace -t -1 --run=blind --X-rtd TMCSO_AdaptivePseudoAsimov=0 --X-rtd TMCSO_PseudoAsimov=0 --cminDefaultMinimizerStrategy 0 --cminFallbackAlgo Minuit2,Migrad,0:0.1 --X-rt MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2

