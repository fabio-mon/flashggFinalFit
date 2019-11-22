doFTEST=0
doFIT=1
doPACKAGER=0
doCALCPHOSYST=0
MASS=''

#YEAR="2016"
YEAR="2017"
#YEAR="2018"

DATE="25_10_2019"
#EXT="singleHiggs"$YEAR
EXT="nodes"$YEAR
PHOTONSYSTFILE=dat/photonCatSyst.dat # without systematics
#PHOTONSYSTFILE=dat/photonCatSyst_${EXT}.dat

INDIR="/mnt/t3nfs01/data01/shome/nchernya/DiHiggs/inputs/${DATE}/"
OUTDIR="output/out_fit_${DATE}_${EXT}"
if [ $doFTEST -gt 0 ]; then
   OUTDIR="output/out_${DATE}_${EXT}"
   #MASS=_125
 #  doFIT=0
fi
CONFIGDAT="output/out_${DATE}_${EXT}/dat/newConfig_${EXT}.dat"
#runLocal='--runLocal'
runLocal=''

BATCH=T3CH
DEFAULTQUEUE="short.q -l h_vmem=6g"  #increase memory for systematics -l h_vmem=6g
#CATS="DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11"
CATS="DoubleHTag_0,DoubleHTag_1,DoubleHTag_3,DoubleHTag_9,DoubleHTag_11"
REFTAG="DoubleHTag_0"
INTLUMI=136.8

SCALES="HighR9EE,LowR9EE,HighR9EB,LowR9EB"
SMEARS="HighR9EERho,LowR9EERho,HighR9EEPhi,LowR9EEPhi,HighR9EBPhi,LowR9EBPhi,HighR9EBRho,LowR9EBRho"
SCALESCORR="MaterialCentralBarrel,MaterialOuterBarrel,MaterialForward"
SCALESGLOBAL="NonLinearity,Geant4,LightYield,Absolute"

##############for tests##############
#PROCS="hh_SM_generated_${YEAR}"
#REFPROC="hh_SM_generated_${YEAR}"
#INFILES="output_hh_SM_generated_${YEAR}"
#####################################

#############SINGLE HIGGS ############
#PROCS="hh_SM_generated_${YEAR},ggh_${YEAR},tth_${YEAR},qqh_${YEAR},vh_${YEAR}"
#REFPROC="tth_${YEAR}"
#INFILES="output_hh_SM_generated_${YEAR},output_ggh_${YEAR},output_tth_${YEAR},output_qqh_${YEAR},output_vh_${YEAR}"

#############NODES ############
REFPROC="hh_node_SM_$YEAR"
#PROCS="hh_node_SM_$YEAR,hh_node_box_$YEAR,hh_node_0_$YEAR,hh_node_1_$YEAR,hh_node_2_$YEAR,hh_node_3_$YEAR,hh_node_4_$YEAR,hh_node_5_$YEAR,hh_node_6_$YEAR,hh_node_7_$YEAR,hh_node_8_$YEAR,hh_node_9_$YEAR,hh_node_10_$YEAR,hh_node_11_$YEAR"
#INFILES="output_hh_node_SM_$YEAR,output_hh_node_box_$YEAR,output_hh_node_0_$YEAR,output_hh_node_1_$YEAR,output_hh_node_2_$YEAR,output_hh_node_3_$YEAR,output_hh_node_4_$YEAR,output_hh_node_5_$YEAR,output_hh_node_6_$YEAR,output_hh_node_7_$YEAR,output_hh_node_8_$YEAR,output_hh_node_9_$YEAR,output_hh_node_10_$YEAR,output_hh_node_11_$YEAR"
PROCS="hh_node_SM_$YEAR,hh_node_4_$YEAR,hh_node_6_$YEAR,hh_node_7_$YEAR,hh_node_9_$YEAR,hh_node_10_$YEAR,hh_node_11_$YEAR"
INFILES="output_hh_node_SM_$YEAR,output_hh_node_4_$YEAR,output_hh_node_6_$YEAR,output_hh_node_7_$YEAR,output_hh_node_9_$YEAR,output_hh_node_10_$YEAR,output_hh_node_11_$YEAR"
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

    PEND=`ls -l $OUTDIR/fTestJobs/sub*| grep -v "\.run" | grep -v "\.done" | grep -v "\.fail" | grep -v "\.err" |grep -v "\.log"  |wc -l`
    TOTAL=`ls -l $OUTDIR/fTestJobs/sub*| grep "\.sh"  |wc -l`
    echo "PEND $PEND"
    while (( $PEND > 0 )) ; do
      PEND=`ls -l $OUTDIR/fTestJobs/sub* | grep -v "\.run" | grep -v "\.done" | grep -v "\.fail" | grep -v "\.err" | grep -v "\.log" |wc -l`
      RUN=`ls -l $OUTDIR/fTestJobs/sub* | grep "\.run" |wc -l`
      FAIL=`ls -l $OUTDIR/fTestJobs/sub* | grep "\.fail" |wc -l`
      DONE=`ls -l $OUTDIR/fTestJobs/sub* | grep "\.done" |wc -l`
      (( PEND=$PEND-$RUN-$FAIL-$DONE ))
      echo " PEND $PEND - RUN $RUN - DONE $DONE - FAIL $FAIL"
      if (( $RUN > 0 )) ; then PEND=1 ; fi
	   if (( $DONE == $TOTAL )) ; then PEND=0; fi
      if (( $FAIL > 0 )) ; then 
          echo "ERROR at least one job failed :"
          ls -l $OUTDIR/fTestJobs/sub* | grep "\.fail"
          return 
      fi
      sleep 10
    done
    mkdir -p $OUTDIR/dat
    cat $OUTDIR/fTestJobs/outputs/* > dat/newConfig_${EXT}_temp.dat
    sort -u dat/newConfig_${EXT}_temp.dat  > dat/tmp_newConfig_${EXT}_temp.dat 
    mv dat/tmp_newConfig_${EXT}_temp.dat dat/newConfig_${EXT}_temp.dat
    cp dat/newConfig_${EXT}_temp.dat $OUTDIR/dat/copy_newConfig_${EXT}_temp.dat
    rm -rf $OUTDIR/sigfTest
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



################################DO NOT USE PACKAGER FOR THE LIMITS . IT IS MESSED UP IN CURRENT MASTER BRANCH. BUT IT IS STILL CAN BE USED FOR PLOTTING############
PROC_SM="GluGluToHHTo2B2G_node_SM_13TeV_madgraph$YEAR"
LUMI=35.9
if [ $YEAR == "2017" ]; then
	LUMI=41.5
fi

if [ $doPACKAGER -gt 0 ]; then
	echo 'in the packager'
	#ls $PWD/$OUTDIR/CMS-HGG_sigfit_*.root > out.txt
	#echo "ls ../Signal/$OUTDIR/CMS-HGG_sigfit_${EXT}_*.root > out.txt"
	#ls $PWD/$OUTDIR/CMS-HGG_sigfit_*.root > out.txt
	#echo "ls ../Signal/$OUTDIR/CMS-HGG_sigfit_${EXT}_*.root > out.txt"
	#inputfile="output/out_fit_06_05_2019_nodes2016/SM_node_2016.txt"
	ls $PWD/$OUTDIR/CMS-HGG_sigfit_${EXT}_GluGluToHHTo2B2G_node_SM_13TeV_madgraph${YEAR}_DoubleHTag_*.root > $OUTDIR/SM_node_$YEAR.txt
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

#./bin/PackageOutput  --skipMasses 120,130 -i $SIGFILES --procs $PROC_SM -l $LUMI -p $OUTDIR/sigfit -W wsig_13TeV -f $CATS -L 120 -H 130 -o $OUTDIR/CMS-HGG_sigfit_${EXT}_SMonly_${DATE}.root > package.out

#./bin/makeParametricSignalModelPlots -i  ${OUTDIR}/CMS-HGG_sigfit_${EXT}_SMonly_${DATE}.root -o $OUTDIR/signalModel -p GluGluToHHTo2B2G_node_SM_13TeV_madgraph$YEAR -f $CATS 

#echo "./bin/PackageOutput -i $SIGFILES --procs $PROCS -l $INTLUMI -p $OUTDIR/sigfit -W wsig_13TeV -f $CATS -L 120 -H 130 -o $OUTDIR/CMS-HGG_sigfit_$EXT.root"
#./bin/PackageOutput  --skipMasses 120,130 -i $SIGFILES --procs $PROCS -l $INTLUMI -p $OUTDIR/sigfit -W wsig_13TeV -f $CATS -L 120 -H 130 -o $OUTDIR/CMS-HGG_sigfit_${EXT}_test.root > package.out
#./bin/PackageOutput -i $SIGFILES --procs $PROCS -l $INTLUMI -p $OUTDIR/sigfit -W wsig_13TeV -f $CATS -L 120 -H 130 -o $OUTDIR/CMS-HGG_sigfit_${EXT}_test.root > package.out
