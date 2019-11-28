#!/bin/sh
doFTEST=0
doFIT=1
doPACKAGER=0
doCALCPHOSYST=0
YEAR="2017"
LABEL="20_11_2019"
LABEL="${LABEL}_year${YEAR}"
#DEFAULTQUEUE="microcentury"
DEFAULTQUEUE="culo"
CATS="DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11,THQLeptonicTag,TTHHadronicTag_0,TTHHadronicTag_1,TTHHadronicTag_2,TTHHadronicTag_3,TTHLeptonicTag_0,TTHLeptonicTag_1,TTHLeptonicTag_2,TTHLeptonicTag_3,UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,VBFTag_0,VBFTag_1,VBFTag_2,VHHadronicTag,VHLeptonicLooseTag,VHMetTag,WHLeptonicTag,ZHLeptonicTag"
#CATS="DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11,TTHHadronicTag_0,TTHHadronicTag_1,TTHHadronicTag_2,TTHHadronicTag_3,TTHLeptonicTag_0,TTHLeptonicTag_1,TTHLeptonicTag_2,TTHLeptonicTag_3,UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,VBFTag_0,VBFTag_1,VBFTag_2,VHHadronicTag,VHLeptonicLooseTag,VHMetTag,WHLeptonicTag,ZHLeptonicTag"
PROCS=("ggh" "hh_node_SM" "qqh" "vh" "tth")
REFTAG=""
REFPROC=""
INTLUMI=1.

INDIR=""
if   [ $YEAR == 2016 ]; then
    INDIR="/eos/user/f/fmonti/HHbbgg_run2/workspaces/NOV142019/ws2016/"
    INTLUMI=38 #the result derived using this value are not considered in any of the following steps, I set it just for consistency
elif [ $YEAR == 2017 ]; then
    INDIR="/eos/user/f/fmonti/HHbbgg_run2/workspaces/NOV142019/ws2017/"
    INTLUMI=45 #the result derived using this value are not considered in any of the following steps, I set it just for consistency
elif [ $YEAR == 2018 ]; then
    INDIR="/eos/user/f/fmonti/HHbbgg_run2/workspaces/NOV142019/ws2018/"
    INTLUMI=63 #the result derived using this value are not considered in any of the following steps, I set it just for consistency
fi

#create INFILESTRING and PROCSTRING
PROCSTRING=""
INFILESTRING=""
for PROC in "${PROCS[@]}"
do
    PROCNAME="${PROC}_${YEAR}"
    #INFILENAME="${PROC}${YEAR}_13TeV_125.root"
    #INFILENAME="output_${PROC}_${YEAR}"
    INFILENAME="${PROC}_${YEAR}.root"
    if [ "$PROCSTRING" != "" ]; then
	PROCSTRING="${PROCSTRING},"
	INFILESTRING="${INFILESTRING},"
    fi
    PROCSTRING="${PROCSTRING}${PROCNAME}"
    INFILESTRING="${INFILESTRING}${INFILENAME}"
done

echo PROCSTRING $PROCSTRING
echo INFILESTRING $INFILESTRING

CURRDIR=${PWD}
OUTDIR="output/out_fit_$LABEL/"
if [ $doFTEST -gt 0 ]; then
   OUTDIR="output/out_$LABEL/"
   doFIT=0
fi
CONFIGDAT="output/out_$LABEL/dat/newConfig_${LABEL}.dat"

####################################################
################## CALCPHOSYSTCONSTS ###################
####################################################
PHOTONSYSTFILE=dat/photonCatSyst.dat # without systematics
SCALES="HighR9EE,LowR9EE,HighR9EB,LowR9EB"
SMEARS="HighR9EERho,LowR9EERho,HighR9EEPhi,LowR9EEPhi,HighR9EBPhi,LowR9EBPhi,HighR9EBRho,LowR9EBRho"
SCALESCORR="MaterialCentralBarrel,MaterialOuterBarrel,MaterialForward"
SCALESGLOBAL="NonLinearity,Geant4,LightYield,Absolute"
#PHOTONSYSTFILE=dat/photonCatSyst_${EXT}.dat
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

  if [ -e ${OUTDIR}/dat/newConfig_${LABEL}.dat ]; then
    echo "[INFO] sigFTest dat file $OUTDIR/dat/newConfig_${LABEL}.dat already exists, so SKIPPING SIGNAL FTEST"
  else
    echo "[INFO] sigFTest dat file $OUTDIR/dat/newConfig_${LABEL}.dat  DOES NOT already exist, so PERFORMING SIGNAL FTEST"

    mkdir -p $OUTDIR/fTest
    echo "=============================="
    echo "Running Signal F-Test"
    echo "-->Determine Number of gaussians"
    echo "=============================="
    echo "./MysubmitSignalFTest.py --procs $PROCSTRING --flashggCats $CATS --outDir $OUTDIR -i $INFILESTRING --indir $INDIR -q $DEFAULTQUEUE $runLocal"
   ./MysubmitSignalFTest.py --procs $PROCSTRING --flashggCats $CATS --outDir $OUTDIR -i $INFILESTRING --indir $INDIR -q $DEFAULTQUEUE $runLocal
#    return 1
    LOOP=1
    while (( $LOOP == 1 )) ; do
	echo "my jobs"
	condor_q
	echo
	echo "RUNNING:"
	ll ${CURRDIR}/${OUTDIR}"/fTestJobs/sub*.sh.run" | wc -l
	echo
	echo "DONE:"
	ll ${CURRDIR}/${OUTDIR}"/fTestJobs/sub*.sh.done" | wc -l
	echo
	echo "FAIL:"
	ll ${CURRDIR}/${OUTDIR}"/fTestJobs/sub*.sh.fail" | wc -l
	echo
	echo 'If you are fine digit "continue"'
	read -r input
	if [[ $input = continue ]]; then
	    LOOP=0
	fi
    done

    cat $OUTDIR/fTestJobs/outputs/* > dat/newConfig_${LABEL}_temp.dat
    sort -u dat/newConfig_${LABEL}_temp.dat  > dat/tmp_newConfig_${LABEL}_temp.dat 
    mv dat/tmp_newConfig_${LABEL}_temp.dat dat/newConfig_${LABEL}_temp.dat
    cp dat/newConfig_${LABEL}_temp.dat $OUTDIR/dat/copy_newConfig_${LABEL}_temp.dat
    rm -rf $OUTDIR/sigfTest
    cp -r $OUTDIR/fTest $OUTDIR/BACKUP_fTest
    mv $OUTDIR/fTest $OUTDIR/sigfTest
    echo "[INFO] sigFtest completed"
    echo "[INFO] using the results of the F-test as they are and building the signal model"
    echo "If you want to amend the number of gaussians, do it in $PWD/dat/newConfig_${LABEL}.dat and re-run!"
    cp dat/newConfig_${LABEL}_temp.dat dat/newConfig_${LABEL}.dat
    cp dat/newConfig_${LABEL}_temp.dat $OUTDIR/dat/newConfig_${LABEL}.dat
    CONFIGDAT=$OUTDIR/dat/newConfig_${LABEL}.dat
    echo 'New CONFIG IS '$CONFIGDAT
    source makeOnepdf.sh $OUTDIR
  fi
fi



############################################################

if [ $doFIT -gt 0 ]; then

  REFPROCOPT=""
  if [ "$REFPROC" != "" ]; then
    REFPROCOPT="--refProc $REFPROC"
  fi

  REFTAGOPT=""
  if [ "$REFTAG" != "" ]; then
    REFTAGOPT="--refTag $REFTAG"
  fi

  echo "./MysubmitSignalFit.py --indir $INDIR -i $INFILESTRING -d ${CONFIGDAT} --mhLow=120 --mhHigh=130 --procs $PROCSTRING -s $PHOTONSYSTFILE --changeIntLumi ${INTLUMI} $REFPROCOPT $REFTAGOPT -p $OUTDIR/sigfit  --q "$DEFAULTQUEUE"  -f $CATS  -o ${OUTDIR}/CMS-HGG_sigfit_${LABEL}.root $runLocal -y $YEAR"
  ./MysubmitSignalFit.py --indir $INDIR -i $INFILESTRING -d ${CONFIGDAT} --mhLow=120 --mhHigh=130 --procs $PROCSTRING -s $PHOTONSYSTFILE --changeIntLumi ${INTLUMI} $REFPROCOPT $REFTAGOPT -p $OUTDIR/sigfit  -q "$DEFAULTQUEUE"  -f $CATS  -o ${OUTDIR}/CMS-HGG_sigfit_${LABEL}.root $runLocal -y $YEAR

  echo "python mergeWorkspaces.py ${OUTDIR}/CMS-HGG_sigfit_${LABEL}_${DATE}.root ${OUTDIR}/CMS-HGG_sigfit_*.root"
fi

######################Combined output for 2016+2017################
#OUTDIR="output/out_20_02_2019_set20162017"
#PROCS1="GluGluToHHTo2B2G_node_0_13TeV_madgraph,GluGluToHHTo2B2G_node_1_13TeV_madgraph,GluGluToHHTo2B2G_node_2_13TeV_madgraph,GluGluToHHTo2B2G_node_3_13TeV_madgraph,GluGluToHHTo2B2G_node_4_13TeV_madgraph,GluGluToHHTo2B2G_node_5_13TeV_madgraph,GluGluToHHTo2B2G_node_6_13TeV_madgraph,GluGluToHHTo2B2G_node_7_13TeV_madgraph,GluGluToHHTo2B2G_node_8_13TeV_madgraph,GluGluToHHTo2B2G_node_9_13TeV_madgraph,GluGluToHHTo2B2G_node_10_13TeV_madgraph,GluGluToHHTo2B2G_node_11_13TeV_madgraph"
#YEAR='_2017'
#PROCS2="GluGluToHHTo2B2G_node_0_13TeV_madgraph$YEAR,GluGluToHHTo2B2G_node_1_13TeV_madgraph$YEAR,GluGluToHHTo2B2G_node_2_13TeV_madgraph$YEAR,GluGluToHHTo2B2G_node_3_13TeV_madgraph$YEAR,GluGluToHHTo2B2G_node_4_13TeV_madgraph$YEAR,GluGluToHHTo2B2G_node_5_13TeV_madgraph$YEAR,GluGluToHHTo2B2G_node_6_13TeV_madgraph$YEAR,GluGluToHHTo2B2G_node_7_13TeV_madgraph$YEAR,GluGluToHHTo2B2G_node_8_13TeV_madgraph$YEAR,GluGluToHHTo2B2G_node_9_13TeV_madgraph$YEAR,GluGluToHHTo2B2G_node_10_13TeV_madgraph$YEAR,GluGluToHHTo2B2G_node_11_13TeV_madgraph$YEAR"
#PROCS="$PROCS1,$PROCS2"
#LABEL="nodes2016_2017"



################################DO NOT USE PACKAGER . IT IS MESSED UP IN CURRENT MASTER BRANCH############
PROC_SM="GluGluToHHTo2B2G_node_SM_13TeV_madgraph$YEAR"
LUMI=35.9
if [ $YEAR == "2017" ]; then
	LUMI=41.5
fi

if [ $doPACKAGER -gt 0 ]; then
	echo 'in the packager'
	#ls $PWD/$OUTDIR/CMS-HGG_sigfit_*.root > out.txt
	#echo "ls ../Signal/$OUTDIR/CMS-HGG_sigfit_${LABEL}_*.root > out.txt"
	#ls $PWD/$OUTDIR/CMS-HGG_sigfit_*.root > out.txt
	#echo "ls ../Signal/$OUTDIR/CMS-HGG_sigfit_${LABEL}_*.root > out.txt"
	#inputfile="output/out_fit_06_05_2019_nodes2016/SM_node_2016.txt"
	ls $PWD/$OUTDIR/CMS-HGG_sigfit_${LABEL}_GluGluToHHTo2B2G_node_SM_13TeV_madgraph${YEAR}_DoubleHTag_*.root > $OUTDIR/SM_node_$YEAR.txt
	inputfile="$OUTDIR/SM_node_$YEAR.txt"
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

#./bin/PackageOutput  --skipMasses 120,130 -i $SIGFILES --procs $PROC_SM -l $LUMI -p $OUTDIR/sigfit -W wsig_13TeV -f $CATS -L 120 -H 130 -o $OUTDIR/CMS-HGG_sigfit_${LABEL}_SMonly_${DATE}.root > package.out

#./bin/makeParametricSignalModelPlots -i  ${OUTDIR}/CMS-HGG_sigfit_${LABEL}_SMonly_${DATE}.root -o $OUTDIR/signalModel -p GluGluToHHTo2B2G_node_SM_13TeV_madgraph$YEAR -f $CATS 

#echo "./bin/PackageOutput -i $SIGFILES --procs $PROCS -l $INTLUMI -p $OUTDIR/sigfit -W wsig_13TeV -f $CATS -L 120 -H 130 -o $OUTDIR/CMS-HGG_sigfit_$LABEL.root"
#./bin/PackageOutput  --skipMasses 120,130 -i $SIGFILES --procs $PROCS -l $INTLUMI -p $OUTDIR/sigfit -W wsig_13TeV -f $CATS -L 120 -H 130 -o $OUTDIR/CMS-HGG_sigfit_${LABEL}_test.root > package.out
#./bin/PackageOutput -i $SIGFILES --procs $PROCS -l $INTLUMI -p $OUTDIR/sigfit -W wsig_13TeV -f $CATS -L 120 -H 130 -o $OUTDIR/CMS-HGG_sigfit_${LABEL}_test.root > package.out
