#!/bin/sh

YEAR="2017"
INDIR=""
OUTDIR=""
procs=("ggh" "hh" "qqh" "vh" "tth")
declare -a filenames

if   [[ $YEAR == "2016" ]]; then
    INDIR="/eos/user/f/fmonti/HHbbgg_run2/workspaces/legacy_runII_vmix12_2016_ttHkillerON_first_HH_second_tthLep/renamed_v4/"
    OUTDIR="/eos/user/f/fmonti/HHbbgg_run2/workspaces/legacy_runII_vmix12_2016_ttHkillerON_first_HH_second_tthLep/shifted_v4/"
elif [[ $YEAR == "2017" ]]; then
    INDIR="/eos/user/f/fmonti/HHbbgg_run2/workspaces/legacy_runII_v2_2017_ttHkillerON_first_HH_second_tthLep/renamed_v4/"
    OUTDIR="/eos/user/f/fmonti/HHbbgg_run2/workspaces/legacy_runII_v2_2017_ttHkillerON_first_HH_second_tthLep/shifted_v4/"
elif [[ $YEAR == "2018" ]]; then
    INDIR="/eos/user/f/fmonti/HHbbgg_run2/workspaces/legacy_runII_v2_2018_ttHkillerON_first_HH_second_tthLep/renamed_v4/"
    OUTDIR="/eos/user/f/fmonti/HHbbgg_run2/workspaces/legacy_runII_v2_2018_ttHkillerON_first_HH_second_tthLep/shifted_v4/"
fi
mkdir -p $OUTDIR
for proc in "${procs[@]}"
do
  filename=$INDIR"/"${proc}$YEAR"_13TeV_125.root"
  echo "-----------------------------------------------------------------------------------"
  echo ">>>> Shifting "${filename}
  /afs/cern.ch/user/f/fmonti/work/flashggFinalFit/CMSSW_7_4_7/src/flashggFinalFit/Signal/test/MyshiftDatasets.py -i ${filename} -d $OUTDIR
done

