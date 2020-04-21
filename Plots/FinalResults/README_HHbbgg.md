## Running SM, BSM limits and making plots ##


To run Asymptotic to get upper limits for SM for 1D:
```
source run.sh
```
To run 2D limit for SM :
```
source run2D.sh
```
Combine version : v8.1.0. , CMSSW_10_2_13

To run Asymptotic for BSM benchmarks using job submission (I am using sbatch system, there are several options like condor, etc available as well, you can try using them). 

To run 2D, add option --do2D

```
python submit_limits.py --method Asymptotic --do_benchmarks_scan --datacard Datacards/cms_HHbbgg_datacard_nodeSM_24_01_2020.txt --queue  short.q --outDir output/Limits_24_01_2020_benchmarks --outtag 24_01_2020_benchmarks 
````

To make plot with U.L. on x-sec times BR for all benchmark plus SM :
First prepare a .txt files with all limits from the combine .root files from previous step of running Asymptotic:
```
python prepareBenchmarkOutput.py --indir output/Limits_21_02_2019/ --outdir plots/ --outtag 21_02_2019
```
Then to make the plot:
```
python makePlotBenchmarks_withSMBox_2016Comb.py --indir output/Limits_21_02_2019/ --outdir plots/ --outtag 21_02_2019
```

To compare the limits (for now only 2 inputs are supported -> but very easily extendable for more):
```
python  makeComparisonBenchmarks.py --indir 'output/Limits_27_03_2019/,output/Limits_21_02_2019/' --outtag '27_03_2019,21_02_2019'  --outdir output/Limits_27_03_2019/ --labels 'with Mjj,w/o Mjj'
```
## Running kl scan ##
```
python submit_limits.py --method Asymptotic --do_kl_scan --datacard Datacards/cms_HHbbgg_datacard_nodeSM_24_01_2020.txt --queue  short.q --outDir output/Limits_24_01_2020_klkt/
```
Plot the scan :  
```
python plot_klambda_scan.py --indir output/Limits_24_01_2020_klkt/ --outdir plots/ --outtag 24_01_2020
```

## Running kl-likelihood ##

First you need to generate Asimov SM toy : 
```
python submit_limits.py --method GenerateOnly --generateAsimovHHSM --datacard Datacards/cms_HHbbgg_datacard_nodeSM_24_01_2020_kl_likelihood.root --outDir output/Limits_24_01_2020_klkt/ --channels_to_run all --outtag 24_01_2020 —toysFile output/Limits_24_01_2020_klkt/higgsCombineSM_AsimovToy_all_24_01_2020.GenerateOnly.mH120.123456.root
```

Then you can run d MultiDim fit : 
```
python submit_limits.py --method  MultiDimFit --do_kl_likelihood  --datacard Datacards/cms_HHbbgg_datacard_nodeSM_24_01_2020_kl_likelihood.root --jobs 10 --pointsperjob 15 --outDir output/Limits_24_01_2020_kllikelihood/ --channels_to_run all --outtag 24_01_2020 --toysFile output/Limits_24_01_2020_kllikelihood/higgsCombineSM_AsimovToy_all_24_01_2020.GenerateOnly.mH120.123456.root
```

This will consider all categories, if you want to do it only for some categories separately, you need to generate Asimov for each of them, and then run multidim fit for them separately :
```
python submit_limits.py --method  MultiDimFit --do_kl_likelihood  --datacard Datacards/cms_HHbbgg_datacard_nodeSM_24_01_2020_kl_likelihood.root --jobs 10 --pointsperjob 15 --outDir output/Limits_24_01_2020_kllikelihood/ --channels_to_run all,DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11 --outtag 24_01_2020 --toysFile output/Limits_24_01_2020_kllikelihood/higgsCombineSM_AsimovToy_all_24_01_2020.GenerateOnly.mH120.123456.root
```
To plot the kl-likelihood :
```
python plot_kllikelihood.py --indir output/Limits_24_01_2020_kllikelihood/ --outdir plots/ --outtag 24_01_2020_kllikelihood --infilehiggsCombineMultiDim_all_24_01_2020.MultiDimFit.mH120.root
```
To plot a zoomed version of the plot, pass --zoom : 
```
python plot_kllikelihood.py --indir output/Limits_24_01_2020_kllikelihood/ --outdir plots/ --outtag 24_01_2020_kllikelihood --infile higgsCombineMultiDim_all_24_01_2020.MultiDimFit.mH120.root —zoom
```





