DATE="25_10_2019"
OUTPUTDIR="output/"
SYSTEMATICS="_systematics"
OUTTAG="_SMgenerated_"${DATE}${SYSTEMATICS}
DATACARD="Datacards/cms_HHbbgg_datacard_SMgenerated_${DATE}${SYSTEMATICS}.txt"

if [[ "$SYSTEMATICS" == "_systematics" ]]; then
    combine $DATACARD -n $OUTTAG -M Asymptotic -m 125.00 --cminDefaultMinimizerType=Minuit2 -L $CMSSW_BASE/lib/$SCRAM_ARCH/libHiggsAnalysisGBRLikelihood.so   --run=blind -t -1 --rRelAcc 0.001
else
    combine $DATACARD -n $OUTTAG -M Asymptotic -m 125.00 --cminDefaultMinimizerType=Minuit2 -L $CMSSW_BASE/lib/$SCRAM_ARCH/libHiggsAnalysisGBRLikelihood.so   --run=blind -t -1 --rRelAcc 0.001 -s 0
fi

return
#for node in `seq 0 -1`;
#for node in SM box `seq 0 11`;
for node in `seq 8 11`;
do
   DATACARD="Datacards/cms_HHbbgg_datacard_node${node}_${DATE}${SYSTEMATICS}.txt"
   OUTTAG="_node${node}_${DATE}${SYSTEMATICS}"
	if [[ "$SYSTEMATICS" == "_systematics" ]]; then
    	combine $DATACARD -n $OUTTAG -M Asymptotic -m 125.00 --cminDefaultMinimizerType=Minuit2 -L $CMSSW_BASE/lib/$SCRAM_ARCH/libHiggsAnalysisGBRLikelihood.so   --run=blind -t -1 --rRelAcc 0.001
	else
    	combine $DATACARD -n $OUTTAG -M Asymptotic -m 125.00 --cminDefaultMinimizerType=Minuit2 -L $CMSSW_BASE/lib/$SCRAM_ARCH/libHiggsAnalysisGBRLikelihood.so   --run=blind -t -1 --rRelAcc 0.001 -s 0
	fi
done


#combine -M HybridNew --testStat=LHC --frequentist  Datacards/cms_HHbbgg_datacard_nodeSM_06_05_2019_systematics.txt -T 100  --saveHybridResult --clsAcc 0 --singlePoint 0.8  --rMin 0.4 --rMax 1.6  -s -1 --fork 15


#running fastScan for kl likelihood

#combine Datacards/cms_HHbbgg_datacard_nodeSM_25_10_2019_systematics_kl_likelihood.txt -M MultiDimFit --algo grid --points 100 -P kl --floatOtherPOIs 0 --setPhysicsModelParameterRanges=-20,15  --freezeNuisances param0_DoubleHTag_0,param1_DoubleHTag_0,param2_DoubleHTag_0,param0_DoubleHTag_1,param1_DoubleHTag_1,param2_DoubleHTag_1,param0_DoubleHTag_2,param1_DoubleHTag_2,param2_DoubleHTag_2,param0_DoubleHTag_3,param1_DoubleHTag_3,param2_DoubleHTag_3,param0_DoubleHTag_4,param1_DoubleHTag_4,param2_DoubleHTag_4,param0_DoubleHTag_5,param1_DoubleHTag_5,param2_DoubleHTag_5,param0_DoubleHTag_6,param1_DoubleHTag_6,param2_DoubleHTag_6,param0_DoubleHTag_7,param1_DoubleHTag_7,param2_DoubleHTag_7,param0_DoubleHTag_8,param1_DoubleHTag_8,param2_DoubleHTag_8,param0_DoubleHTag_9,param1_DoubleHTag_9,param2_DoubleHTag_9,param0_DoubleHTag_10,param1_DoubleHTag_10,param2_DoubleHTag_10,param0_DoubleHTag_11,param1_DoubleHTag_11,param2_DoubleHTag_11 --expectSignal=1 --setPhysicsModelParameters r=1 -t -1
