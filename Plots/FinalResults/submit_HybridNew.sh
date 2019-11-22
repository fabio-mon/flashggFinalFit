#!/bin/bash

mydir="/work/nchernya/DiHiggs/CMSSW_7_4_7/src/flashggFinalFit/Plots/FinalResults/"
cd $mydir

eval `scramv1 runtime -sh`
cmsenv


min=0.6
max=1.0
numpoints=10
rmin=0.4
rmax=1.6
maxjobs=320   #toys per job : 250

signame="nodeSM"
date="06_05_2019"
datacard=$mydir"Datacards/cms_HHbbgg_datacard_${signame}_${date}_systematics.txt"

num=0

while [ $num -lt $numpoints ]
do
	job=0
	while [ $job -lt $maxjobs ]
	do
		qsub -q all.q comb_HybridNew.sh $min $max $numpoints $rmin $rmax $num $signame $date $datacard
		job=$(( $job + 1 ))
	done
	num=$(( $num + 1 ))
done
