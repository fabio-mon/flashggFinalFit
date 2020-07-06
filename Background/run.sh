#DATE=25_04_2019
#DATE=25_10_2019
#DATE=24_01_2020
DATE=22_04_2020
#DATE=27_03_2020
YEAR=2016_2017_2018
#YEAR=2016_2017
#YEAR=2018


############################# 1 D ##########################
#./bin/fTest -i /work/nchernya/DiHiggs/inputs/${DATE}/output_DoubleEG_${YEAR}_${DATE}.root --saveMultiPdf CMS-HGG_multipdf_HHbbgg_${YEAR}_${DATE}.root --isData 1 -f DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11

#./scripts/subBkgPlots.py -b  outputs/CMS-HGG_multipdf_HHbbgg_${YEAR}_${DATE}.root -d plots/plots_${DATE}/ -S 13 --isMultiPdf  --useBinnedData  --doBands --massStep 5 -s   /work/nchernya/DiHiggs/CMSSW_7_4_7/src/flashggFinalFit/Signal/output/CMS-HGG_sigfit_${YEAR}_${DATE}.root    -L 100 -H 180 -f DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11 -l  CAT_0,CAT_1,CAT_2,CAT_3,CAT_4,CAT_5,CAT_6,CAT_7,CAT_8,CAT_9,CAT_10,CAT_11 --intLumi 136.8 --runLocal

#MC BG
#./bin/fTest -i /work/nchernya/DiHiggs/inputs/${DATE}/output_BG_MC_${YEAR}_${DATE}.root --saveMultiPdf CMS-HGG_multipdf_MCbg_HHbbgg_${YEAR}_${DATE}.root --isData 1 -f DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11
#./bin/fTest -i /work/nchernya/DiHiggs/inputs/${DATE}/output_BG_MCbjets_${YEAR}_${DATE}.root --saveMultiPdf CMS-HGG_multipdf_MCbgbjets_HHbbgg_${YEAR}_${DATE}.root --isData 1 -f DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11

#MC BG
#./scripts/subBkgPlots.py -b  outputs/CMS-HGG_multipdf_MCbg_HHbbgg_${YEAR}_${DATE}.root -d plots/plots_MCBG_${DATE}/ -S 13 --isMultiPdf  --useBinnedData  --doBands --massStep 5 -s   /work/nchernya/DiHiggs/CMSSW_7_4_7/src/flashggFinalFit/Signal/output/CMS-HGG_sigfit_${YEAR}_${DATE}.root    -L 100 -H 180 -f DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11 -l  CAT_0,CAT_1,CAT_2,CAT_3,CAT_4,CAT_5,CAT_6,CAT_7,CAT_8,CAT_9,CAT_10,CAT_11 --intLumi 136.8 --runLocal
#./scripts/subBkgPlots.py -b  outputs/CMS-HGG_multipdf_MCbgbjets_HHbbgg_${YEAR}_${DATE}.root -d plots/plots_MCBGbjets_${DATE}/ -S 13 --isMultiPdf  --useBinnedData  --doBands --massStep 5 -s   /work/nchernya/DiHiggs/CMSSW_7_4_7/src/flashggFinalFit/Signal/output/CMS-HGG_sigfit_${YEAR}_${DATE}.root    -L 100 -H 180 -f DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11 -l  CAT_0,CAT_1,CAT_2,CAT_3,CAT_4,CAT_5,CAT_6,CAT_7,CAT_8,CAT_9,CAT_10,CAT_11 --intLumi 136.8 --runLocal

############################# 2 D ##########################

#2D #MC
#addition=''
#addition=_cats70GeV
addition=_cats90GeV
name2D=DoubleEG
#name2D=BG_MCbgbjets
#name2D=BG_MCbgbjets_woGjets
#name2D=BG_MCbg
name2D=${name2D}${addition}
outtag=ftest
json2D=Env_json_high.dat
input2D=output_${name2D}_${YEAR}_${DATE}.root
#outputdir=plots/plots2D/${name2D}_${DATE}_${outtag}_MjjUnblinded_MggBlinded_rebin
outputdir=plots/plots2D/${name2D}_${DATE}_${outtag}


#name2D=BG_MCbg_woGjets
#outtag=opt
#input2D=output_${name2D}_${YEAR}_${DATE}.root
#outputdir=plots/plots2D/${name2D}_${DATE}_${outtag}

#./bin/fTest2D -i /work/nchernya/DiHiggs/inputs/${DATE}/${input2D} --saveMultiPdf  CMS-HGG_multipdf2D_${name2D}_${outtag}_HHbbgg_${YEAR}_${DATE}.root --isData 1 -f DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11 --isFlashgg 1  -c 12 -D ${outputdir} -d ${outputdir}/res.dat --jsonForEnvelope $json2D
#./bin/fTest2D -i /work/nchernya/DiHiggs/inputs/${DATE}/${input2D} --saveMultiPdf  CMS-HGG_multipdf2D_${name2D}_${outtag}_HHbbgg_${YEAR}_${DATE}.root --isData 1 -f DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11 --isFlashgg 1  -c 12 -D ${outputdir} -d ${outputdir}/res.dat 
#./bin/fTest2D -i /work/nchernya/DiHiggs/inputs/${DATE}/Data_70GeV_Mgg_blind/${input2D} --saveMultiPdf  CMS-HGG_multipdf2D_${name2D}_${outtag}_HHbbgg_${YEAR}_${DATE}.root --isData 1 -f DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9 --isFlashgg 1  -c 10 -D ${outputdir} -d ${outputdir}/res.dat 
#./bin/fTest2D -i /work/nchernya/DiHiggs/inputs/${DATE}/Data_90GeV_Mgg_blind/${input2D} --saveMultiPdf  CMS-HGG_multipdf2D_${name2D}_${outtag}_HHbbgg_${YEAR}_${DATE}.root --isData 1 -f DoubleHTag_10,DoubleHTag_11 --isFlashgg 1  -c 1 -D ${outputdir} -d ${outputdir}/res.dat 
#./bin/fTest2D -i /work/nchernya/DiHiggs/inputs/${DATE}/Data_70GeV_rebin/${input2D} --saveMultiPdf  CMS-HGG_multipdf2D_${name2D}_${outtag}_HHbbgg_${YEAR}_${DATE}_rebin.root --isData 1 -f DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9 --isFlashgg 1  -c 10 -D ${outputdir} -d ${outputdir}/res.dat
 
#./bin/fTest2D -i /work/nchernya/DiHiggs/inputs/${DATE}//${input2D} --saveMultiPdf  CMS-HGG_multipdf2D_${name2D}_${outtag}_HHbbgg_${YEAR}_${DATE}.root --isData 1 -f DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,VBFDoubleHTag_0 --isFlashgg 1  -c 11 -D ${outputdir} -d ${outputdir}/res.dat 
./bin/fTest2D -i /work/nchernya/DiHiggs/inputs/${DATE}/${input2D} --saveMultiPdf  CMS-HGG_multipdf2D_${name2D}_${outtag}_HHbbgg_${YEAR}_${DATE}.root --isData 1 -f DoubleHTag_10,DoubleHTag_11 --isFlashgg 1  -c 1 -D ${outputdir} -d ${outputdir}/res.dat 


#VBF cat
#./bin/fTest2D -i /work/nchernya/DiHiggs/inputs/${DATE}/${input2D} --saveMultiPdf  CMS-HGG_multipdf2D_${name2D}_${outtag}_HHbbgg_${YEAR}_${DATE}.root --isData 1 -f DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11,VBFDoubleHTag_0 --isFlashgg 1  -c 12 -D ${outputdir} -d ${outputdir}/res.dat 

##Plots
lowblind=105
highblind=145
low=70
high=190
variable='Mjj'
plotdir='plots/plots2D/Mjj_18_02_2020/'

#lowblind=115
#highblind=135
#low=100
#high=180
#variable='CMS_hgg_mass'
#plotdir='plots/plots2D/Mgg_18_02_2020/'

#2D Data
#./bin/fTest2D -i /work/nchernya/DiHiggs/inputs/${DATE}/output_DoubleEG_${YEAR}_${DATE}.root --saveMultiPdf CMS-HGG_multipdf2D_100x100bins_HHbbgg_${YEAR}_${DATE}_ivanhighjson.root --isData 1 -f DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11 --isFlashgg 1  -c 12 -D plots/fTest2D_data/ -d plots/fTest2D_data//res.dat --jsonForEnvelope Env_json_ivan_high.dat  # _high.dat


./bin/fTest2D -i /eos/user/f/fmonti/HHbbgg_run2/workspaces/FEB2020/DoubleEG/ws//output_DoubleEG_all3years.root --saveMultiPdf CMS-HGG_multipdf2D_DoubleEG_ivanjson_HHbbgg_all3years_FEB2020.root --isData 1 -f DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11 --isFlashgg 1  -c 12 -D /eos/user/f/fmonti/HHbbgg_run2/workspaces/FEB2020/plots/ -d /eos/user/f/fmonti/HHbbgg_run2/workspaces/FEB2020/res.dat --jsonForEnvelope /afs/cern.ch/user/f/fmonti/work/flashggFinalFit2/CMSSW_7_4_7/src/flashggFinalFit/MetaData_HHbbgg/Env_json_ivan.dat

#./scripts/subBkgPlots2D.py -b CMS-HGG_multipdf2D_DoubleEG_opt_HHbbgg_2016_2017_2018_18_02_2020.root  -d ${plotdir} -S 13 --isMultiPdf   --massStep 5 -s /work/nchernya/DiHiggs/CMSSW_7_4_7/src/flashggFinalFit/Plots/FinalResults/inputs/CMS-HGG_sigfit_MggMjj_${YEAR}_${DATE}.root   --variableName  ${variable}   -L $low -H $high  --lowblind ${lowblind} --highblind ${highblind}   -f DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11 -l  CAT_0,CAT_1,CAT_2,CAT_3,CAT_4,CAT_5,CAT_6,CAT_7,CAT_8,CAT_9,CAT_10,CAT_11 --intLumi 136.8 --runLocal

