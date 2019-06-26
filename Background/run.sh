#DATE=25_04_2019
DATE=13_06_2019

#./bin/fTest -i /eos/user/f/fmonti/HHbbgg_run2/workspaces/output_DoubleEG_2016_2017_v2.root --saveMultiPdf CMS-HGG_multipdf_HHbbgg_2016_2017_${DATE}.root --isData 1 -f DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11

./scripts/subBkgPlots.py -b /afs/cern.ch/user/f/fmonti/work/flashggFinalFit/CMSSW_7_4_7/src/flashggFinalFit/Background/CMS-HGG_multipdf_HHbbgg_2016_2017_13_06_2019.root -d plots/plots_${DATE}/ -S 13 --isMultiPdf  --useBinnedData  --doBands --massStep 5 -s    /afs/cern.ch/user/f/fmonti/work/flashggFinalFit/CMSSW_7_4_7/src/flashggFinalFit/Signal/output/CMS-HGG_sigfit_2016_2017_merged.root    -L 100 -H 180 -f DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11 -l  CAT_0,CAT_1,CAT_2,CAT_3,CAT_4,CAT_5,CAT_6,CAT_7,CAT_8,CAT_9,CAT_10,CAT_11 --intLumi 77.4 --runLocal

