signal=0
signal_str=bonly
BG=BG_MCbgbjets
#BG=BG_MCbgbjets_90GeV
#BG=DoubleEG


#echo combine Datacards/cms_HHbbgg2D_${BG}_bestFittoys_datacard_nodeSM_18_02_2020.root -M GenerateOnly -m 125 --setParameters pdfindex_DoubleHTag_0_13TeV=0,pdfindex_DoubleHTag_1_13TeV=0,pdfindex_DoubleHTag_2_13TeV=0,pdfindex_DoubleHTag_3_13TeV=0,pdfindex_DoubleHTag_4_13TeV=0,pdfindex_DoubleHTag_5_13TeV=0,pdfindex_DoubleHTag_6_13TeV=0,pdfindex_DoubleHTag_7_13TeV=0,pdfindex_DoubleHTag_8_13TeV=0,pdfindex_DoubleHTag_9_13TeV=0,pdfindex_DoubleHTag_10_13TeV=0,pdfindex_DoubleHTag_11_13TeV=0 --freezeParameters pdfindex_DoubleHTag_0_13TeV,pdfindex_DoubleHTag_1_13TeV,pdfindex_DoubleHTag_2_13TeV,pdfindex_DoubleHTag_3_13TeV,pdfindex_DoubleHTag_4_13TeV,pdfindex_DoubleHTag_5_13TeV,pdfindex_DoubleHTag_6_13TeV,pdfindex_DoubleHTag_7_13TeV,pdfindex_DoubleHTag_8_13TeV,pdfindex_DoubleHTag_9_13TeV,pdfindex_DoubleHTag_10_13TeV,pdfindex_DoubleHTag_11_13TeV --expectSignal $signal --toysFrequentist -t 1000 --saveToys --X-rtd TMCSO_AdaptivePseudoAsimov=0 --X-rtd TMCSO_PseudoAsimov=0 --cminDefaultMinimizerStrategy 0 --cminFallbackAlgo Minuit2,Migrad,0:0.1 --X-rt MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 -n HHbbgg2D_${BG}_bestFittoys_nodeSM_18_02_2020_$signal_str

echo
echo


#echo combine Datacards/cms_HHbbgg2D_${BG}_biastoys_datacard_nodeSM_18_02_2020.root -M MultiDimFit --algo singles -m 125 --expectSignal $signal --toysFile higgsCombineHHbbgg2D_${BG}_bestFittoys_nodeSM_18_02_2020_${signal_str}.GenerateOnly.mH125.123456.root --X-rtd TMCSO_AdaptivePseudoAsimov=0 --X-rtd TMCSO_PseudoAsimov=0 --cminDefaultMinimizerStrategy 0 --cminFallbackAlgo Minuit2,Migrad,0:0.1 --X-rt MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 -n HHbbgg2D_${BG}_biastoys_nodeSM_18_02_2020_$signal_str -t 1000 --autoBoundsPOIs r --autoMaxPOIs r --saveFitResult

echo combine Datacards/cms_HHbbgg2D_${BG}_biastoys_datacard_nodeSM_18_02_2020.root -M MultiDimFit --algo singles -m 125 --expectSignal $signal --toysFile higgsCombineHHbbgg2D_${BG}_bestFittoys_nodeSM_18_02_2020_${signal_str}.GenerateOnly.mH125.123456.root --X-rtd TMCSO_AdaptivePseudoAsimov=0 --X-rtd TMCSO_PseudoAsimov=0 --cminDefaultMinimizerStrategy 0 --cminFallbackAlgo Minuit2,Migrad,0:0.1 --X-rt MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 -n HHbbgg2D_${BG}_biastoys_nodeSM_18_02_2020_$signal_str -t 1000 --rMin 0.01 --rMax 20 --saveFitResult






#echo combine Datacards/cms_HHbbgg2D_${BG}_bestFitCAT11_datacard_nodeSM_18_02_2020.root -M GenerateOnly -m 125 --setParameters pdfindex_DoubleHTag_11_13TeV=0 --freezeParameters pdfindex_DoubleHTag_11_13TeV --expectSignal $signal --toysFrequentist -t 1000 --saveToys --X-rtd TMCSO_AdaptivePseudoAsimov=0 --X-rtd TMCSO_PseudoAsimov=0 --cminDefaultMinimizerStrategy 0 --cminFallbackAlgo Minuit2,Migrad,0:0.1 --X-rt MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 -n HHbbgg2D_${BG}_bestFitCAT11_nodeSM_18_02_2020_$signal_str

echo
echo


#echo combine Datacards/cms_HHbbgg2D_${BG}_biasCAT11_datacard_nodeSM_18_02_2020.root -M MultiDimFit --algo singles -m 125 --expectSignal $signal --toysFile higgsCombineHHbbgg2D_${BG}_bestFitCAT11_nodeSM_18_02_2020_${signal_str}.GenerateOnly.mH125.123456.root --X-rtd TMCSO_AdaptivePseudoAsimov=0 --X-rtd TMCSO_PseudoAsimov=0 --cminDefaultMinimizerStrategy 0 --cminFallbackAlgo Minuit2,Migrad,0:0.1 --X-rt MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 -n HHbbgg2D_${BG}_biasCAT11_nodeSM_18_02_2020_$signal_str -t 1000 --autoBoundsPOIs r --autoMaxPOIs r --saveFitResult



###echo combine Datacards/cms_HHbbgg2D_BG_MCbgbjets_biasCAT11_datacard_nodeSM_18_02_2020_biasCAT11.root -M FitDiagnostics -m 125 --expectSignal $signal --toysFile higgsCombineHHbbgg2D_BG_MCbgbjets_bestFitCAT11_nodeSM_18_02_2020_${signal_str}.GenerateOnly.mH125.123456.root --X-rtd TMCSO_AdaptivePseudoAsimov=0 --X-rtd TMCSO_PseudoAsimov=0 --cminDefaultMinimizerStrategy 0 --cminFallbackAlgo Minuit2,Migrad,0:0.1 --X-rt MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 -n HHbbgg2D_BG_MCbgbjets_biasCAT11_nodeSM_18_02_2020_$signal_str -t 1000 --autoBoundsPOIs r --autoMaxPOIs r

