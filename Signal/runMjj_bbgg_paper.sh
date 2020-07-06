#YEAR="2016"
#YEAR="2017"
YEAR="2018"
mergeYears=1  #used for all procs
mergeCats=0 #used for single Higgs and 12 DoubleHTag cats only, not for VBF

DATE="18_02_2020"
PAPER=1


#EXT="singleHiggs"$YEAR
#EXT="hhNLO"$YEAR
#EXT="qqHH"$YEAR
EXT="hh_node_SM"$YEAR

INDIR="/work/nchernya/DiHiggs/inputs/${DATE}/"
OUTDIR="output/mjj/out_mjj_${DATE}_${EXT}_test2/"
PLOTDIR="plots/mjj/mjj_fits_${DATE}_${EXT}_test2/"
#TEMPLATE="fits_config/models_2D_higgs_mjj70_16_02_2020_vbf.rs"
#TEMPLATE="fits_config/models_2D_higgs_mjj70_16_02_2020_nlo_0.rs"
TEMPLATE="fits_config/models_2D_higgs_mjj70_16_02_2020_qqHH.rs"  #working rather well for all qqHH and ggHH


#CATS="DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11,VBFDoubleHTag_0"
#CATS="DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11,VBFDoubleHTag_0,VBFDoubleHTag_1"
#CATS="DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11"
#CATS="VBFDoubleHTag_0"
#CATS="DoubleHTag_0,DoubleHTag_4,DoubleHTag_8,DoubleHTag_11"
#CATS="DoubleHTag_8,DoubleHTag_11"

CATS="DoubleHTag_0"

#############SINGLE HIGGS ############
#PROCS="ggh,tth,qqh,vh"
#############HH NLO ############
#PROCS="ggHH_kl_0_kt_1,ggHH_kl_1_kt_1,ggHH_kl_2p45_kt_1,ggHH_kl_5_kt_1"
############# qqHH NLO ############
#PROCS="qqHH_CV_1_C2V_1_kl_1,qqHH_CV_1_C2V_2_kl_1,qqHH_CV_1_C2V_1_kl_2,qqHH_CV_1_C2V_1_kl_0,qqHH_CV_0p5_C2V_1_kl_1,qqHH_CV_1p5_C2V_1_kl_1"
#PROCS="qqHH_CV_1_C2V_1_kl_1,qqHH_CV_1_C2V_2_kl_1,qqHH_CV_1_C2V_1_kl_2,qqHH_CV_1_C2V_1_kl_0,qqHH_CV_0p5_C2V_1_kl_1,qqHH_CV_1p5_C2V_1_kl_1,qqHH_CV_1_C2V_0_kl_1"
################################
#PROCS="ggHH_kl_1_kt_1"
PROCS="hh_node_SM"

set -x

for PROC in $(echo $PROCS | sed "s/,/ /g")
	do
   
		INFILEWITHYEARS=${INDIR}'output_'${PROC}'_2016.root,'${INDIR}'output_'${PROC}'_2017.root,'${INDIR}'output_'${PROC}'_2018.root'  #example if you are using merged years
		if [ $mergeCats == 1 ]; then
			if [[ $PROC == *"ggh"* ]] || [[ $PROC == *"vh"* ]] || [[ $PROC == *"tth"* ]]  || [[ $PROC == *"qqh"* ]]  ; then
				if [ $mergeYears == 1 ]; then
					./bin/MjjSignalFit -t ${TEMPLATE} -d ${INDIR}  -p ${PLOTDIR} -o ${OUTDIR} --procs ${PROC}   -y ${YEAR} --mergeYears 2016,2017,2018 --infileWithAllYears ${INFILEWITHYEARS} -m 1 -f ${CATS} --paper ${PAPER}
				else
					./bin/MjjSignalFit -t ${TEMPLATE} -d ${INDIR}  -p ${PLOTDIR} -o ${OUTDIR} --procs ${PROC}   -y ${YEAR} -m 1 -f ${CATS} --paper ${PAPER}
				fi
			else 
				echo "You are trying to merge categories for a single Higgs process, are you sure you want to do this??"		
			fi	
		else
			if [ $mergeYears == 1 ]; then
				./bin/MjjSignalFit -t ${TEMPLATE} -d ${INDIR}  -p ${PLOTDIR} -o ${OUTDIR} --procs ${PROC}   -y ${YEAR} --mergeYears 2016,2017,2018 --infileWithAllYears ${INFILEWITHYEARS} -f ${CATS} --paper ${PAPER}
			else
				./bin/MjjSignalFit -t ${TEMPLATE} -d ${INDIR}  -p ${PLOTDIR} -o ${OUTDIR} --procs ${PROC}   -y ${YEAR} -f ${CATS} --paper ${PAPER}
			fi
		fi	
done

set +x
