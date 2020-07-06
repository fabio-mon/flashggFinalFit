doFTEST=0
doFIT=0
doPACKAGER=1
doPLOTS=0
doCALCPHOSYST=0 #Not needed, only for shape syst, checked to be negligible
MASS=''

#YEAR="2016"
#YEAR="2017"
YEAR="2018"


#DATE="24_01_2020"
#DATE="04_02_2020"
DATE="2020"
EXT="singleHiggs"$YEAR
#DATE="22_04_2020"
#DATE="27_03_2020"
#EXT="singleHiggs"$YEAR
#EXT="hhNLO"$YEAR
#EXT="qqHH"$YEAR


#EXT="nodes"$YEAR
#EXT="vbfhh"$YEAR
PHOTONSYSTFILE=dat/photonCatSyst.dat # without systematics
#PHOTONSYSTFILE=dat/photonCatSyst_${EXT}.dat

INDIR="/eos/user/f/fmonti/HHbbgg_run2/workspaces/FEB2020/ws${YEAR}/"
OUTDIR="output/out_fit_${DATE}_${EXT}"
if [ $doFTEST -gt 0 ]; then
   OUTDIR="output/out_${DATE}_${EXT}"
   #MASS=_125
 #  doFIT=0
fi
CONFIGDAT="output/out_${DATE}_${EXT}/dat/newConfig_${EXT}.dat"
#runLocal='--runLocal'
runLocal=''

#COndor
#BATCH=HTCONDOR
#DEFAULTQUEUE=espresso  #espresso : 20min.  microcentury - 1h, longlunch-2h, workday - 8h, tomorrow -1d

BATCH=T3CH
DEFAULTQUEUE="short.q " #for slurm not used  #-l h_vmem=6g"  #increase memory for systematics -l h_vmem=6g
CATS="DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11,TTHHadronicTag_0,TTHHadronicTag_1,TTHHadronicTag_2,TTHHadronicTag_3,TTHLeptonicTag_0,TTHLeptonicTag_1,TTHLeptonicTag_2,TTHLeptonicTag_3"

#CATS="DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11"
#CATS="DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11,VBFDoubleHTag_0"


REFTAG="DoubleHTag_0"
INTLUMI=136.8

###########Not needed, only for shape syst, checked to be negligible
SCALES="HighR9EE,LowR9EE,HighR9EB,LowR9EB"
SMEARS="HighR9EERho,LowR9EERho,HighR9EEPhi,LowR9EEPhi,HighR9EBPhi,LowR9EBPhi,HighR9EBRho,LowR9EBRho"
SCALESCORR="MaterialCentralBarrel,MaterialOuterBarrel,MaterialForward"
SCALESGLOBAL="NonLinearity,Geant4,LightYield,Absolute"


#############SINGLE HIGGS ############
PROCS="ggh_${YEAR},tth_${YEAR},qqh_${YEAR},vh_${YEAR},thq_${YEAR}"
REFPROC="tth_${YEAR}"
INFILES="output_ggh_${YEAR},output_tth_${YEAR},output_qqh_${YEAR},output_vh_${YEAR},output_thq_${YEAR}"
REFTAG="DoubleHTag_9"
###tests##
#PROCS="tth_${YEAR}"
#REFPROC="tth_${YEAR}"
#INFILES="output_ggh_${YEAR},output_tth_${YEAR},output_qqh_${YEAR},output_vh_${YEAR}"
#REFTAG="DoubleHTag_9"
#############HH NLO ############
#REFPROC="ggHH_kl_0_kt_1_${YEAR}"
#PROCS="ggHH_kl_0_kt_1_${YEAR},ggHH_kl_1_kt_1_${YEAR},ggHH_kl_2p45_kt_1_${YEAR},ggHH_kl_5_kt_1_${YEAR}"
#INFILES="output_ggHH_kl_0_kt_1_${YEAR},output_ggHH_kl_1_kt_1_${YEAR},output_ggHH_kl_2p45_kt_1_${YEAR},output_ggHH_kl_5_kt_1_${YEAR}"
############# qqHH NLO ############
REFPROC="qqHH_CV_1_C2V_2_kl_1_${YEAR}"
REFTAG="VBFDoubleHTag_0"
PROCS="qqHH_CV_1_C2V_1_kl_1_${YEAR},qqHH_CV_1_C2V_2_kl_1_${YEAR},qqHH_CV_1_C2V_1_kl_2_${YEAR},qqHH_CV_1_C2V_1_kl_0_${YEAR},qqHH_CV_0p5_C2V_1_kl_1_${YEAR},qqHH_CV_1p5_C2V_1_kl_1_${YEAR}"
INFILES="output_qqHH_CV_1_C2V_1_kl_1_${YEAR},output_qqHH_CV_1_C2V_2_kl_1_${YEAR},output_qqHH_CV_1_C2V_1_kl_2_${YEAR},output_qqHH_CV_1_C2V_1_kl_0_${YEAR},output_qqHH_CV_0p5_C2V_1_kl_1_${YEAR},output_qqHH_CV_1p5_C2V_1_kl_1_${YEAR}"
################################



#############NODES ############
#REFPROC="hh_node_SM_$YEAR"
#PROCS="hh_node_SM_$YEAR"
#INFILES="output_hh_node_SM_$YEAR"
################################
#REFPROC="vbfhh_$YEAR"
#PROCS="vbfhh_$YEAR"
#INFILES="output_vbfhh_$YEAR"


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
    ./python/submitSignaFTest.py --procs $PROCS --flashggCats $CATS --outDir $OUTDIR -i $INFILES --indir $INDIR    --batch $BATCH $runLocal  -q "$DEFAULTQUEUE" 

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
  echo "./python/submitSignalFit.py --indir $INDIR -i $INFILES -d ${CONFIGDAT} --mhLow=120 --mhHigh=130 --procs $PROCS -s $PHOTONSYSTFILE --changeIntLumi ${INTLUMI} --refProc $REFPROC --refTag $REFTAG -p $OUTDIR/sigfit  --batch $BATCH  -f $CATS  -o ${OUTDIR}/CMS-HGG_sigfit_${EXT}.root $runLocal -q "$DEFAULTQUEUE" " 
  ./python/submitSignalFit.py --indir $INDIR -i $INFILES -d ${CONFIGDAT} --mhLow=120 --mhHigh=130 --procs $PROCS -s $PHOTONSYSTFILE --changeIntLumi ${INTLUMI} --refProc $REFPROC --refTag $REFTAG -p $OUTDIR/sigfit  --batch $BATCH -f $CATS  -o ${OUTDIR}/CMS-HGG_sigfit_${EXT}.root $runLocal -q "$DEFAULTQUEUE" 

  echo "python mergeWorkspaces.py ${OUTDIR}/CMS-HGG_sigfit_${EXT}_${DATE}.root ${OUTDIR}/CMS-HGG_sigfit_*.root"
fi


###############################Packager is used for plotting only #############################
LUMI=35.9
if [ $YEAR == "2016" ]; then
	LUMI=35.9
fi
if [ $YEAR == "2017" ]; then
	LUMI=41.5
fi
if [ $YEAR == "2018" ]; then
	LUMI=59.4
fi




if [ $YEAR == "2018" ]; then
	LUMI=137.
fi
###########paper_plots
CATS="DoubleHTag_0" 
PROC_SM="hh_node_SM_$YEAR"
PROCS="hh_node_SM_$YEAR"
DATE="18_02_2020" #paper plots
EXT="nodes"$YEAR
OUTDIR="output/out_fit_${DATE}_${EXT}"
############

###########VBF plots
#CATS="VBFDoubleHTag_0,VBFDoubleHTag_1" 
#PROCS="qqHH_CV_1_C2V_1_kl_1_${YEAR},qqHH_CV_1_C2V_0_kl_1_${YEAR}"
#DATE="12_06_2020" 
#EXT="vbfhh"$YEAR
#OUTDIR="output/out_fit_${DATE}_${EXT}"
############


if [ $doPACKAGER -gt 0 ]; then
	echo 'in the packager'
	for PROC_SM in $(echo $PROCS | sed "s/,/ /g")
	do
		ls $PWD/$OUTDIR/CMS-HGG_sigfit_${EXT}_${PROC_SM}_*DoubleHTag_*.root > $OUTDIR/${PROC_SM}.txt
		inputfile="$OUTDIR/${PROC_SM}.txt"
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
	   ./bin/PackageOutput  --skipMasses 120,130 -i $SIGFILES --procs $PROC_SM -l $LUMI -p $OUTDIR/sigfit -W wsig_13TeV -f $CATS -L 120 -H 130 -o $OUTDIR/CMS-HGG_sigfit_${EXT}_${PROC_SM}_packager.root > package.out
	   ./bin/makeParametricSignalModelPlots -i  ${OUTDIR}/CMS-HGG_sigfit_${EXT}_${PROC_SM}_packager.root -o $OUTDIR/signalModel -p $PROC_SM -f $CATS 
	done
fi

if [ $doPLOTS -gt 0 ]; then
	./bin/makeParametricSignalModelPlots -i  ${OUTDIR}/CMS-HGG_sigfit_${EXT}_${PROC_SM}_packager.root -o $OUTDIR/signalModel -p $PROC_SM -f $CATS 
fi

