#!/bin/sh

YEAR="2018"
OUTDIR=""
declare -a filenames

if   [[ $YEAR == "2016" ]]; then
    filenames+=("/eos/user/f/fmonti/HHbbgg_run2/workspaces/legacy_runII_vmix12_2016_ttHkillerON_first_HH_second_tthLep/output_GluGluHToGG_M-125_13TeV_powheg_pythia8.root" 
	"/eos/user/f/fmonti/HHbbgg_run2/workspaces/legacy_runII_vmix12_2016_ttHkillerON_first_HH_second_tthLep/output_GluGluToHHTo2B2G_node_SM_13TeV-madgraph.root" 
	"/eos/user/f/fmonti/HHbbgg_run2/workspaces/legacy_runII_vmix12_2016_ttHkillerON_first_HH_second_tthLep/output_VBFHToGG_M-125_13TeV_powheg_pythia8.root" 
	"/eos/user/f/fmonti/HHbbgg_run2/workspaces/legacy_runII_vmix12_2016_ttHkillerON_first_HH_second_tthLep/output_VHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root" 
	"/eos/user/f/fmonti/HHbbgg_run2/workspaces/legacy_runII_vmix12_2016_ttHkillerON_first_HH_second_tthLep/output_ttHToGG_M125_13TeV_powheg_pythia8_v2.root")
    OUTDIR="/eos/user/f/fmonti/HHbbgg_run2/workspaces/legacy_runII_vmix12_2016_ttHkillerON_first_HH_second_tthLep/renamed_v3/"
elif [[ $YEAR == "2017" ]]; then
    echo "hi"
    filenames+=("/eos/user/f/fmonti/HHbbgg_run2/workspaces/legacy_runII_v2_2017_ttHkillerON_first_HH_second_tthLep/output_GluGluHToGG_M-125_13TeV_powheg_pythia8.root"  
	"/eos/user/f/fmonti/HHbbgg_run2/workspaces/legacy_runII_v2_2017_ttHkillerON_first_HH_second_tthLep/output_GluGluToHHTo2B2G_node_SM_13TeV-madgraph.root" 
	"/eos/user/f/fmonti/HHbbgg_run2/workspaces/legacy_runII_v2_2017_ttHkillerON_first_HH_second_tthLep/output_VBFHToGG_M-125_13TeV_powheg_pythia8.root" 
	"/eos/user/f/fmonti/HHbbgg_run2/workspaces/legacy_runII_v2_2017_ttHkillerON_first_HH_second_tthLep/output_VHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root" 
	"/eos/user/f/fmonti/HHbbgg_run2/workspaces/legacy_runII_v2_2017_ttHkillerON_first_HH_second_tthLep/output_ttHToGG_M125_13TeV_powheg_pythia8.root")
    OUTDIR="/eos/user/f/fmonti/HHbbgg_run2/workspaces/legacy_runII_v2_2017_ttHkillerON_first_HH_second_tthLep/renamed_v3/"
elif [[ $YEAR == "2018" ]]; then
    filenames+=("/eos/user/f/fmonti/HHbbgg_run2/workspaces/legacy_runII_v2_2018_ttHkillerON_first_HH_second_tthLep/output_GluGluHToGG_M-125_13TeV_powheg_pythia8.root" \
	"/eos/user/f/fmonti/HHbbgg_run2/workspaces/legacy_runII_v2_2018_ttHkillerON_first_HH_second_tthLep/output_GluGluToHHTo2B2G_node_SM_TuneCP5_PSWeights_13TeV-madgraph-pythia8.root" \
	"/eos/user/f/fmonti/HHbbgg_run2/workspaces/legacy_runII_v2_2018_ttHkillerON_first_HH_second_tthLep/output_VBFHToGG_M-125_13TeV_powheg_pythia8.root" \
	"/eos/user/f/fmonti/HHbbgg_run2/workspaces/legacy_runII_v2_2018_ttHkillerON_first_HH_second_tthLep/output_VHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root" \
	"/eos/user/f/fmonti/HHbbgg_run2/workspaces/legacy_runII_v2_2018_ttHkillerON_first_HH_second_tthLep/output_ttHJetToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root")
    OUTDIR="/eos/user/f/fmonti/HHbbgg_run2/workspaces/legacy_runII_v2_2018_ttHkillerON_first_HH_second_tthLep/renamed_v3/"
fi
echo "filenames "$filenames
for filename in "${filenames[@]}"
do
  echo "-----------------------------------------------------------------------------------"
  echo ">>>> Renaming "${filename}
  mkdir -p $OUTDIR
  /afs/cern.ch/user/f/fmonti/work/flashggFinalFit/CMSSW_7_4_7/src/flashggFinalFit/Signal/test/MyrenameDatasets.py -i ${filename} -y $YEAR -d $OUTDIR
done

