doFTEST=0
doFIT=1
doPACKAGER=0
doCALCPHOSYST=0
MASS=''
if [ "$doFTEST" -eq "1" ]; then
    if [ "$doFIT" -eq "0" ]; then
	MASS='_125'
	echo "ciao"
    fi
fi

#YEAR=""
#YEAR2="2016"
YEAR="_2017"
YEAR2="2017"

DATE="26_06_2019"
#EXT="singleHiggs"$YEAR2
EXT="nodes"$YEAR2
PHOTONSYSTFILE=dat/photonCatSyst.dat # without systematics
#PHOTONSYSTFILE=dat/photonCatSyst_${EXT}.dat

INDIR=""

if   [ $YEAR2 == 2016 ]; then
    INDIR="/eos/user/f/fmonti/HHbbgg_run2/workspaces/2016/TAGSORTER_HHwithttHkiller_ttHlep_ttHhad/shifted_v2/"
elif [ $YEAR2 == 2017 ]; then
    INDIR="/eos/user/f/fmonti/HHbbgg_run2/workspaces/2017/TAGSORTER_HHwithttHkiller_ttHlep_ttHhad/shifted_v2/"
fi

OUTDIR="output/out_fit_${DATE}_${EXT}/"
if [ $doFTEST -gt 0 ]; then
   OUTDIR="output/out_${DATE}_${EXT}/"
   #MASS=_125
   doFIT=0
fi
CONFIGDAT="output/out_${DATE}_${EXT}/dat/newConfig_${EXT}.dat"
#runLocal='--runLocal'
runLocal=''

BATCH=LSF
DEFAULTQUEUE="workday"
#DEFAULTQUEUE="culo"
#CATS="DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11"
CATS="DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11,TTHLeptonicTag_0,TTHLeptonicTag_1,ZHLeptonicTag,WHLeptonicTag,VHLeptonicLooseTag,TTHHadronicTag_0,TTHHadronicTag_1,TTHHadronicTag_2,VBFTag_0,VBFTag_1,VBFTag_2,VHMetTag,VHHadronicTag,UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3"
REFTAG="DoubleHTag_0"
INTLUMI=77.4

SCALES="HighR9EE,LowR9EE,HighR9EB,LowR9EB"
SMEARS="HighR9EERho,LowR9EERho,HighR9EEPhi,LowR9EEPhi,HighR9EBPhi,LowR9EBPhi,HighR9EBRho,LowR9EBRho"
SCALESCORR="MaterialCentralBarrel,MaterialOuterBarrel,MaterialForward"
SCALESGLOBAL="NonLinearity,Geant4,LightYield,Absolute"

##############for tests##############
#PROCS="GluGluToHHTo2B2G_node_SM_13TeV_madgraph_generated_2017"
#REFPROC="GluGluToHHTo2B2G_node_SM_13TeV_madgraph_generated_2017"
#INFILES="output_GluGluToHHTo2B2G_node_SM_13TeV-madgraph_generated_2017$MASS"
#####################################

PROCS=""
REFPROC=""
INFILES=""

if   [ $YEAR2 == 2016 ]; then
    PROCS="GluGluToHHTo2B2G_node_SM_13TeV_madgraph,GluGluHToGG_M_125_13TeV_powheg_pythia8,VBFHToGG_M_125_13TeV_powheg_pythia8,ttHToGG_M125_13TeV_powheg_pythia8_v2,VHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8"
    REFPROC="ttHToGG_M125_13TeV_powheg_pythia8_v2"
    INFILES="output_GluGluToHHTo2B2G_node_SM_13TeV-madgraph$MASS,output_GluGluHToGG_M-125_13TeV_powheg_pythia8$MASS,output_VBFHToGG_M-125_13TeV_powheg_pythia8$MASS,output_ttHToGG_M125_13TeV_powheg_pythia8_v2$MASS,output_VHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8$MASS"
elif [ $YEAR2 == 2017 ]; then
    PROCS="GluGluToHHTo2B2G_node_SM_13TeV_madgraph_2017,GluGluHToGG_M_125_13TeV_powheg_pythia8_2017,VBFHToGG_M_125_13TeV_powheg_pythia8_2017,ttHToGG_M125_13TeV_powheg_pythia8_2017,VHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8_2017"
    REFPROC="ttHToGG_M125_13TeV_powheg_pythia8_2017"
    INFILES="output_GluGluToHHTo2B2G_node_SM_13TeV-madgraph_2017$MASS,output_GluGluHToGG_M-125_13TeV_powheg_pythia8_2017$MASS,output_VBFHToGG_M-125_13TeV_powheg_pythia8_2017$MASS,output_ttHToGG_M125_13TeV_powheg_pythia8_2017$MASS,output_VHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8_2017$MASS"
fi
#############NODES ############
#PROCS="GluGluToHHTo2B2G_node_SM_13TeV_madgraph$YEAR,GluGluToHHTo2B2G_node_box_13TeV_madgraph$YEAR,GluGluToHHTo2B2G_node_0_13TeV_madgraph$YEAR,GluGluToHHTo2B2G_node_1_13TeV_madgraph$YEAR,GluGluToHHTo2B2G_node_2_13TeV_madgraph$YEAR,GluGluToHHTo2B2G_node_3_13TeV_madgraph$YEAR,GluGluToHHTo2B2G_node_4_13TeV_madgraph$YEAR,GluGluToHHTo2B2G_node_5_13TeV_madgraph$YEAR,GluGluToHHTo2B2G_node_6_13TeV_madgraph$YEAR,GluGluToHHTo2B2G_node_7_13TeV_madgraph$YEAR,GluGluToHHTo2B2G_node_8_13TeV_madgraph$YEAR,GluGluToHHTo2B2G_node_9_13TeV_madgraph$YEAR,GluGluToHHTo2B2G_node_10_13TeV_madgraph$YEAR,GluGluToHHTo2B2G_node_11_13TeV_madgraph$YEAR"
#PROCS="GluGluToHHTo2B2G_node_SM_13TeV_madgraph$YEAR"
#REFPROC="GluGluToHHTo2B2G_node_SM_13TeV_madgraph$YEAR"
#INFILES="output_GluGluToHHTo2B2G_node_SM_13TeV-madgraph$YEAR$MASS,output_GluGluToHHTo2B2G_node_box_13TeV-madgraph$YEAR$MASS,output_GluGluToHHTo2B2G_node_0_13TeV-madgraph$YEAR$MASS,output_GluGluToHHTo2B2G_node_1_13TeV-madgraph$YEAR$MASS,output_GluGluToHHTo2B2G_node_2_13TeV-madgraph$YEAR$MASS,output_GluGluToHHTo2B2G_node_3_13TeV-madgraph$YEAR$MASS,output_GluGluToHHTo2B2G_node_4_13TeV-madgraph$YEAR$MASS,output_GluGluToHHTo2B2G_node_5_13TeV-madgraph$YEAR$MASS,output_GluGluToHHTo2B2G_node_6_13TeV-madgraph$YEAR$MASS,output_GluGluToHHTo2B2G_node_7_13TeV-madgraph$YEAR$MASS,output_GluGluToHHTo2B2G_node_8_13TeV-madgraph$YEAR$MASS,output_GluGluToHHTo2B2G_node_9_13TeV-madgraph$YEAR$MASS,output_GluGluToHHTo2B2G_node_10_13TeV-madgraph$YEAR$MASS,output_GluGluToHHTo2B2G_node_11_13TeV-madgraph$YEAR$MASS"
#INFILES="output_GluGluToHHTo2B2G_node_SM_13TeV-madgraph$YEAR$MASS"
################################


####################################################
################## CALCPHOSYSTCONSTS ###################
####################################################

if [ $doCALCPHOSYST == 1 ]; then

  echo "=============================="
  echo "Running calcPho"
  echo "-->Determine effect of photon systematics"
  echo "=============================="

  echo "./bin/calcPhotonSystConsts -i $INFILES --indir $INDIR -o $PHOTONSYSTFILE -p $PROCS -s $SCALES -S $SCALESCORR -g $SCALESGLOBAL -r $SMEARS -D $OUTDIR -f $CATS"
  ./bin/calcPhotonSystConsts -i $INFILES --indir $INDIR -o $PHOTONSYSTFILE -p $PROCS -s $SCALES -S $SCALESCORR -g $SCALESGLOBAL -r $SMEARS -D $OUTDIR -f $CATS
  mkdir -p $OUTDIR/dat
  cp $PHOTONSYSTFILE $OUTDIR/$PHOTONSYSTFILE
fi

####################################################
################## SIGNAL F-TEST ###################
####################################################

#ls dat/newConfig_${EXT}.dat
if [ $doFTEST -gt 0 ]; then
  mkdir -p $OUTDIR/dat

  if [ -e ${OUTDIR}/dat/newConfig_${EXT}.dat ]; then
    echo "[INFO] sigFTest dat file $OUTDIR/dat/newConfig_${EXT}.dat already exists, so SKIPPING SIGNAL FTEST"
  else
    echo "[INFO] sigFTest dat file $OUTDIR/dat/newConfig_${EXT}.dat  DOES NOT already exist, so PERFORMING SIGNAL FTEST"

    mkdir -p $OUTDIR/fTest
    echo "=============================="
    echo "Running Signal F-Test"
    echo "-->Determine Number of gaussians"
    echo "=============================="
    echo "./python/submitSignaFTest.py --procs $PROCS --flashggCats $CATS --outDir $OUTDIR -i $INFILES  --indir $INDIR   --batch $BATCH -q '$DEFAULTQUEUE'"
    ./python/submitSignaFTest.py --procs $PROCS --flashggCats $CATS --outDir $OUTDIR -i $INFILES --indir $INDIR    --batch $BATCH -q "$DEFAULTQUEUE" $runLocal
#    return 1
    LOOP=1
    while (( $LOOP == 1 )) ; do
	echo "my jobs"
	condor_q
	echo 'If you are fine digit "continue"'
	read -r input
	if [[ $input = continue ]]; then
	    LOOP=0
	fi
    done
    mkdir -p $OUTDIR/dat
    cat $OUTDIR/fTestJobs/outputs/* > dat/newConfig_${EXT}_temp.dat
    sort -u dat/newConfig_${EXT}_temp.dat  > dat/tmp_newConfig_${EXT}_temp.dat 
    mv dat/tmp_newConfig_${EXT}_temp.dat dat/newConfig_${EXT}_temp.dat
    cp dat/newConfig_${EXT}_temp.dat $OUTDIR/dat/copy_newConfig_${EXT}_temp.dat
    rm -rf $OUTDIR/sigfTest
    cp -r $OUTDIR/fTest $OUTDIR/BACKUP_fTest
    mv $OUTDIR/fTest $OUTDIR/sigfTest
    echo "[INFO] sigFtest completed"
    echo "[INFO] using the results of the F-test as they are and building the signal model"
    echo "If you want to amend the number of gaussians, do it in $PWD/dat/newConfig_${EXT}.dat and re-run!"
    cp dat/newConfig_${EXT}_temp.dat dat/newConfig_${EXT}.dat
    cp dat/newConfig_${EXT}_temp.dat $OUTDIR/dat/newConfig_${EXT}.dat
    CONFIGDAT=$OUTDIR/dat/newConfig_${EXT}.dat
    echo 'New CONFIG IS '$CONFIGDAT
    source makeOnepdf.sh $OUTDIR
  fi
fi



############################################################

if [ $doFIT -gt 0 ]; then
  echo "./python/submitSignalFit.py --indir $INDIR -i $INFILES -d ${CONFIGDAT} --mhLow=120 --mhHigh=130 --procs $PROCS -s $PHOTONSYSTFILE --changeIntLumi ${INTLUMI} --refProc $REFPROC --refTag $REFTAG -p $OUTDIR/sigfit  --batch $BATCH -q "$DEFAULTQUEUE"  -f $CATS  -o ${OUTDIR}/CMS-HGG_sigfit_${EXT}.root $runLocal"
  ./python/submitSignalFit.py --indir $INDIR -i $INFILES -d ${CONFIGDAT} --mhLow=120 --mhHigh=130 --procs $PROCS -s $PHOTONSYSTFILE --changeIntLumi ${INTLUMI} --refProc $REFPROC --refTag $REFTAG -p $OUTDIR/sigfit  --batch $BATCH -q "$DEFAULTQUEUE"  -f $CATS  -o ${OUTDIR}/CMS-HGG_sigfit_${EXT}.root $runLocal

  echo "python mergeWorkspaces.py ${OUTDIR}/CMS-HGG_sigfit_${EXT}_${DATE}.root ${OUTDIR}/CMS-HGG_sigfit_*.root"
fi

######################Combined output for 2016+2017################
#OUTDIR="output/out_20_02_2019_set20162017"
#PROCS1="GluGluToHHTo2B2G_node_0_13TeV_madgraph,GluGluToHHTo2B2G_node_1_13TeV_madgraph,GluGluToHHTo2B2G_node_2_13TeV_madgraph,GluGluToHHTo2B2G_node_3_13TeV_madgraph,GluGluToHHTo2B2G_node_4_13TeV_madgraph,GluGluToHHTo2B2G_node_5_13TeV_madgraph,GluGluToHHTo2B2G_node_6_13TeV_madgraph,GluGluToHHTo2B2G_node_7_13TeV_madgraph,GluGluToHHTo2B2G_node_8_13TeV_madgraph,GluGluToHHTo2B2G_node_9_13TeV_madgraph,GluGluToHHTo2B2G_node_10_13TeV_madgraph,GluGluToHHTo2B2G_node_11_13TeV_madgraph"
#YEAR='_2017'
#PROCS2="GluGluToHHTo2B2G_node_0_13TeV_madgraph$YEAR,GluGluToHHTo2B2G_node_1_13TeV_madgraph$YEAR,GluGluToHHTo2B2G_node_2_13TeV_madgraph$YEAR,GluGluToHHTo2B2G_node_3_13TeV_madgraph$YEAR,GluGluToHHTo2B2G_node_4_13TeV_madgraph$YEAR,GluGluToHHTo2B2G_node_5_13TeV_madgraph$YEAR,GluGluToHHTo2B2G_node_6_13TeV_madgraph$YEAR,GluGluToHHTo2B2G_node_7_13TeV_madgraph$YEAR,GluGluToHHTo2B2G_node_8_13TeV_madgraph$YEAR,GluGluToHHTo2B2G_node_9_13TeV_madgraph$YEAR,GluGluToHHTo2B2G_node_10_13TeV_madgraph$YEAR,GluGluToHHTo2B2G_node_11_13TeV_madgraph$YEAR"
#PROCS="$PROCS1,$PROCS2"
#EXT="nodes2016_2017"



################################DO NOT USE PACKAGER . IT IS MESSED UP IN CURRENT MASTER BRANCH############
PROC_SM="GluGluToHHTo2B2G_node_SM_13TeV_madgraph$YEAR"
LUMI=35.9
if [ $YEAR2 == "2017" ]; then
	LUMI=41.5
fi

if [ $doPACKAGER -gt 0 ]; then
	echo 'in the packager'
	#ls $PWD/$OUTDIR/CMS-HGG_sigfit_*.root > out.txt
	#echo "ls ../Signal/$OUTDIR/CMS-HGG_sigfit_${EXT}_*.root > out.txt"
	#ls $PWD/$OUTDIR/CMS-HGG_sigfit_*.root > out.txt
	#echo "ls ../Signal/$OUTDIR/CMS-HGG_sigfit_${EXT}_*.root > out.txt"
	#inputfile="output/out_fit_06_05_2019_nodes2016/SM_node_2016.txt"
	ls $PWD/$OUTDIR/CMS-HGG_sigfit_${EXT}_GluGluToHHTo2B2G_node_SM_13TeV_madgraph${YEAR}_DoubleHTag_*.root > $OUTDIR/SM_node_$YEAR2.txt
	inputfile="$OUTDIR/SM_node_$YEAR2.txt"
	counter=0
	while read p ; do
	  if (($counter==0)); then
	    SIGFILES="$p"
	  else
	    SIGFILES="$SIGFILES,$p"
	  fi
	  ((counter=$counter+1))
	done < $inputfile 
	echo "SIGFILES $SIGFILES"
fi

#./bin/PackageOutput  --skipMasses 120,130 -i $SIGFILES --procs $PROC_SM -l $LUMI -p $OUTDIR/sigfit -W wsig_13TeV -f $CATS -L 120 -H 130 -o $OUTDIR/CMS-HGG_sigfit_${EXT}_SMonly_${DATE}.root > package.out

#./bin/makeParametricSignalModelPlots -i  ${OUTDIR}/CMS-HGG_sigfit_${EXT}_SMonly_${DATE}.root -o $OUTDIR/signalModel -p GluGluToHHTo2B2G_node_SM_13TeV_madgraph$YEAR -f $CATS 

#echo "./bin/PackageOutput -i $SIGFILES --procs $PROCS -l $INTLUMI -p $OUTDIR/sigfit -W wsig_13TeV -f $CATS -L 120 -H 130 -o $OUTDIR/CMS-HGG_sigfit_$EXT.root"
#./bin/PackageOutput  --skipMasses 120,130 -i $SIGFILES --procs $PROCS -l $INTLUMI -p $OUTDIR/sigfit -W wsig_13TeV -f $CATS -L 120 -H 130 -o $OUTDIR/CMS-HGG_sigfit_${EXT}_test.root > package.out
#./bin/PackageOutput -i $SIGFILES --procs $PROCS -l $INTLUMI -p $OUTDIR/sigfit -W wsig_13TeV -f $CATS -L 120 -H 130 -o $OUTDIR/CMS-HGG_sigfit_${EXT}_test.root > package.out
