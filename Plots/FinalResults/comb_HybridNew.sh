#!/bin/bash

source $VO_CMS_SW_DIR/cmsset_default.sh
source /swshare/psit3/etc/profile.d/cms_ui_env.sh  # for bash

mydir="/work/nchernya/DiHiggs/CMSSW_7_4_7/src/flashggFinalFit/Plots/FinalResults/output/Limits_06_05_2019_HybridNew5000_2/"

cd $mydir

eval `scramv1 runtime -sh`
shopt -s expand_aliases
cmsenv

min=$1
max=$2
numpoints=$3  #200
rmin=$4
rmax=$5
index=$6

signame=$7
date=$8
datacard=$9

point=$( echo " $min + ($index-1) * ($max-$min)/$numpoints" | bc -l )
#rmin=$( echo "$point - 100 * $point" | bc -l)
#rmax=$( echo "$point + 100 * $point" | bc -l)

echo $datacard

combine -M HybridNew --testStat=LHC --frequentist ${datacard}  -T 250  -s -1 --saveToys --saveHybridResult -n _uplim_grid_${signame}_${date}_${index}_ --clsAcc 0  --fork 4 --singlePoint $point --rMax $rmax --rMin $rmin
echo combine -M HybridNew --testStat=LHC --frequentist ${datacard}  -T 250  -s -1 --saveToys --saveHybridResult -n _uplim_grid_${signame}_${date}_${index}_ --clsAcc 0  --fork 4 --singlePoint $point --rMax $rmax --rMin $rmin

#hadd grid.root higgsComb*.root
#combine -M HybridNew --testStat=LHC --frequentist ../../Datacards/cms_HHbbgg_datacard_nodeSM_06_05_2019_systematics.txt -T 5000 --grid grid.root --expectedFromGrid 0.5 --plot cls.pdf --fork 12
#python /work/nchernya/DiHiggs/CMSSW_7_4_7/src/HiggsAnalysis/CombinedLimit/test/plotTestStatCLs.py -i grid.root -o cls.root -p r -v all -m 120 -e

#$ -o /t3home/nchernya/batch_logs/
#$ -e /t3home/nchernya/batch_logs/
