#!/bin/bash

# Usage of this scipt
#./s_sb_errorbands.sh <index> <working directory> <MHhat> <Muhat>
# your input rool file must be called inputfile.root
nToys=1
MHhat=$3
Muhat=$4
dir=$2 
((startIndex=$1*10000))
index=$startIndex

STOREDIR="/work/nchernya/DiHiggs/CMSSW_7_4_7/src/flashggFinalFit/Plots/FinalResults/Postfit_plots_12_06_2020/" #FIXME should be made configurable

cd $dir
#eval `scramv1 runtime -sh`

while (( $index < $startIndex+ $nToys)); 
do
set -x
combine $STOREDIR/inputfile.root  -m $MHhat --snapshotName MultiDimFit -M GenerateOnly --toysFrequentist --bypassFrequentistFit -t 1 --expectSignal=$Muhat -n combout_step0_$index --saveToys -s -1 --X-rtd TMCSO_AdaptivePseudoAsimov=0 --X-rtd TMCSO_PseudoAsimov=0 --cminDefaultMinimizerStrategy 0 --cminFallbackAlgo Minuit2,Migrad,0:0.1 --X-rt MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 --redefineSignalPOIs r  --freezeParameters r_gghh,r_qqhh,kt,kl,CV,C2V

mv higgsCombinecombout_step0_${index}.GenerateOnly*.root $STOREDIR/higgsCombinecombout_step0_done_$index.root

combine $STOREDIR/inputfile.root --toysFile $STOREDIR/higgsCombinecombout_step0_done_$index.root -m $MHhat -M MultiDimFit -P r --floatOtherPOIs=1 --saveWorkspace -t 1 -n combout_step1_$index --X-rtd TMCSO_AdaptivePseudoAsimov=0 --X-rtd TMCSO_PseudoAsimov=0 --cminDefaultMinimizerStrategy 0 --cminFallbackAlgo Minuit2,Migrad,0:0.1 --X-rt MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 --redefineSignalPOIs r  --freezeParameters r_gghh,r_qqhh,kt,kl,CV,C2V

mv higgsCombinecombout_step1_${index}.MultiDimFit*.root $STOREDIR/higgsCombinecombout_step1_done_$index.root

combine $STOREDIR/higgsCombinecombout_step1_done_$index.root -m $MHhat --snapshotName MultiDimFit -M GenerateOnly --saveToys -t -1 -n combout_step2_$index --expectSignal=0 --X-rtd TMCSO_AdaptivePseudoAsimov=0 --X-rtd TMCSO_PseudoAsimov=0 --cminDefaultMinimizerStrategy 0 --cminFallbackAlgo Minuit2,Migrad,0:0.1 --X-rt MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 --redefineSignalPOIs r  --freezeParameters r_gghh,r_qqhh,kt,kl,CV,C2V

mv higgsCombinecombout_step2_${index}.GenerateOnly*.root $STOREDIR/higgsCombinecombout_step2_done_$index.root

(( index=$index+1))
set +x
done;


###to submit jobs : 
#To submit jobs with condor : 
#p=0 ; while (( $p<200 )); do qsub -q hep.q -l h_rt=10:0:0 -l h_vmem=12G $PWD/../scripts/s_sb_errorbandsHH2D.sh $p $PWD 125.0 0.308; (( p=$p+1 )) ; done
#
#So submit jobs with slurm : 
#
#p=0 ; while (( $p<200 )); do sbatch --account t3 --nodes=1 --job-name=test_toys --wrap "../scripts/s_sb_errorbandsHH2D.sh $p $PWD 125. 0.308"; (( p=$p+1 )) ; done
