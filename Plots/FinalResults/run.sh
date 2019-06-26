DATE="26_06_2019"
OUTPUTDIR="output/"
#OUTTAG="_SMgenerated_"$DATE
SYSTEMATICS=""
c=""
OUTTAG="_SM_"${DATE}${SYSTEMATICS}
DATACARD="/afs/cern.ch/user/f/fmonti/work/flashggFinalFit/CMSSW_7_4_7/src/flashggFinalFit/Datacard/mydatacard.txt"

if [[ "$SYSTEMATICS" == "_systematics" ]]; then
    combine $DATACARD -n $OUTTAG -M Asymptotic -m 125.00 --cminDefaultMinimizerType=Minuit2 -L $CMSSW_BASE/lib/$SCRAM_ARCH/libHiggsAnalysisGBRLikelihood.so   --run=blind -t -1 --rRelAcc 0.001
else
    combine $DATACARD -n $OUTTAG -M Asymptotic -m 125.00 --cminDefaultMinimizerType=Minuit2 -L $CMSSW_BASE/lib/$SCRAM_ARCH/libHiggsAnalysisGBRLikelihood.so   --run=blind -t -1 --rRelAcc 0.001 -s 0
fi

return
#for node in `seq 0 -1`;
#for node in SM `seq 0 11`;
for node in SM box `seq 0 11`;
do
   DATACARD="Datacards/cms_HHbbgg_datacard_node${node}_${DATE}${SYSTEMATICS}.txt"
   OUTTAG="_node${node}_${DATE}${SYSTEMATICS}"
	if [[ "$SYSTEMATICS" == "_systematics" ]]; then
    	combine $DATACARD -n $OUTTAG -M Asymptotic -m 125.00 --cminDefaultMinimizerType=Minuit2 -L $CMSSW_BASE/lib/$SCRAM_ARCH/libHiggsAnalysisGBRLikelihood.so   --run=blind -t -1 --rRelAcc 0.001
	else
    	combine $DATACARD -n $OUTTAG -M Asymptotic -m 125.00 --cminDefaultMinimizerType=Minuit2 -L $CMSSW_BASE/lib/$SCRAM_ARCH/libHiggsAnalysisGBRLikelihood.so   --run=blind -t -1 --rRelAcc 0.001 -s 0
	fi
done
