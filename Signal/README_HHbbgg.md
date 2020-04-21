### Running Signal and Single Higgs bkg models for Mgg: 

### First, one has to prepare a workspaces from the flashgg ntuples (trees). ### 

When running flashgg workspaces with systematics, too much memory is taken and jobs do not finish. For this reason we create flashgg trees (dumpTrees = True , dumpWorkspaces = False) and then convert them to the workspaces. If you alreeady have workspaces (dumpWorkspaces = True), then you can move on to the next step (running f-test and fit). 

In flashgg one can specify the name of the output trees. Since different years of data taking are treated differently, we need to rename the workspaces to have a year in the name. I am doing it alerady at the stage of producing the flashgg ntuples. My convention for the names is the following : hh2016/2017/2018 for doubleH signal and vh2016(vh2017, vh2018), qqh(2016/2017/2018), ggh(..), tth(..) for single higgs. Most likely you will not have the same convention in the begining, it is not a problem but you have to make sure you adjust a bit the expected names in the scripts  (will be described further).

To create workspaces from trees : 
```
cd flashggFinalFit/Signal/
python trees2ws.py --year 2016 ...and other options 
```

You have to specify the location of the trees, the output directory, the names of the input files, etc in the . options : 
https://github.com/chernyavskaya/flashggFinalFit/blob/fullRunII_Oct2019/Signal/trees2ws.py#L181-L189
--add_benchmarks option is needed to do the reweighting of the signal to eiher SM signal or any of the 12 benchmarks. 
You can specify which nodes to use here :
https://github.com/chernyavskaya/flashggFinalFit/blob/fullRunII_Oct2019/Signal/trees2ws.py#L12
In addition each benchmark has to be normalized to the total sum of all events (without any preselection), this is saved in this json which is specified in this line :
https://github.com/chernyavskaya/flashggFinalFit/blob/fullRunII_Oct2019/Signal/trees2ws.py#L188
and can be found here :
https://github.com/chernyavskaya/flashggFinalFit/blob/fullRunII_Oct2019/MetaData_HHbbgg/reweighting_normalization_18_12_2019.json

You might wonder why these lines are here :
https://github.com/chernyavskaya/flashggFinalFit/blob/fullRunII_Oct2019/Signal/trees2ws.py#L213-L216
This is done in case you are looking at the hh MC , but do not wish to do the reweighting, which means what you are taking not a real SM (in case of 2017/2018), in order to make sure one does not mix up these ones, 'generated' is added to the name.

In order to preserve the normalization of the MC after applying the btag shape weight, signals and single higgs MC should be renormalized using the btag SF factors that are found in this json : 
https://github.com/chernyavskaya/flashggFinalFit/blob/fullRunII_Oct2019/MetaData_HHbbgg/btagSF_15_01_2019.jsonand has to be specified here :
https://github.com/chernyavskaya/flashggFinalFit/blob/fullRunII_Oct2019/Signal/trees2ws.py#L189

By default this script is run with systematics, in order to run without systematics : --nosysts

The current script relies on the fact that the trees are named in the following way name+year+ _ + 13TeV_125_13TeV :
https://github.com/chernyavskaya/flashggFinalFit/blob/fullRunII_Oct2019/Signal/trees2ws.py#L212
for example : tth2016_13TeV_125_13TeV_DoubleHTag_11
If you do not have it done like this, you should modify this line accordingly :
https://github.com/chernyavskaya/flashggFinalFit/blob/fullRunII_Oct2019/Signal/trees2ws.py#L212

If you wish to create workspaces from the trees that are not yet categorized (doCategorization=False in flashgg), then you can use this script to create workspaces. Both of these scripts can be very easily merged in one by adding an option 'doCategorization' in the first one, but I have not done it yet. 
https://github.com/chernyavskaya/flashggFinalFit/blob/fullRunII_Oct2019/Signal/trees2ws_incl.py
Categorization should be specified here :
https://github.com/chernyavskaya/flashggFinalFit/blob/fullRunII_Oct2019/Signal/trees2ws_incl.py#L188-L191

These scripts are relatively fast for single Higgs. HH samples for 2017 and 2018 are vrey large though, and processing with systematics takes about 30 min. 

### Now you have the workspaces ready, we can move on to the signal model. ###

First we run *signalFtest* to determine the number of gausians needed to describe signal 
(for more info see general README in Signal directory). Beware that this script is not perfect and one has to look at the plots produced 
and maybe adjust the *config.dat* file that was written in flashggFinalFit/Signal/dat with more accurate number of gaussians.

After the config file is prepared, we can run script to create a Signal and Resonant Single Higgs bkg models 
(for now it is counted as signal, but in final datacards we specify it is background).

To make it easier I prepared a pretty general bash script to execute all steps : 
```
cd flashggFinalFit/Signal/
source runSignalScripts_bbgg.sh
```

https://github.com/chernyavskaya/flashggFinalFit/blob/fullRunII_Oct2019/Signal/runSignalScripts_bbgg.sh
https://github.com/chernyavskaya/flashggFinalFit/blob/fullRunII_Oct2019/Signal/runSignalScripts_bbgg.sh#L1
You do not have to use it, you can run each step one by one if you wish. I submit jobs for each process and each category, but you can run it locally https://github.com/chernyavskaya/flashggFinalFit/blob/fullRunII_Oct2019/Signal/runSignalScripts_bbgg.sh#L25

Steps you need to do in order :
```
doFTEST=1
doFIT=1
merge everything in one file : python mergeWorkspaces.py final_Mgg_workspace.root all_workspaces_you_just_created.root
doPACKAGER=1 (optional, for pretty plots only)
```

You have to edit all relevant info : input dir, input files, processes, etc :
https://github.com/chernyavskaya/flashggFinalFit/blob/fullRunII_Oct2019/Signal/runSignalScripts_bbgg.sh#L17
https://github.com/chernyavskaya/flashggFinalFit/blob/fullRunII_Oct2019/Signal/runSignalScripts_bbgg.sh#L9
https://github.com/chernyavskaya/flashggFinalFit/blob/fullRunII_Oct2019/Signal/runSignalScripts_bbgg.sh#L13

Running F-test should not cause any trouble. After that you will run the fit using the optimal number of gaussians found at the previous F-test step :
https://github.com/chernyavskaya/flashggFinalFit/blob/fullRunII_Oct2019/Signal/runSignalScripts_bbgg.sh#L2

if you run each category in a single job, you will have to merge the output :
https://github.com/chernyavskaya/flashggFinalFit/blob/fullRunII_Oct2019/Signal/runSignalScripts_bbgg.sh#L145

It might happen that the fit fails and then the merge will fail as well. In this case, identify for which category and process it failed, check the number of gaussians from the f-test in the config, look at the plots for this category created during the f-test, and most likley you will see that it chose the wrong number of gaussians. Adjust the number of gaussian in the config, and rerun the fit.

Now if everything went well, you fill have the final workspaces(signal and single higgs) to be used for the final fit. 


### Running Signal and Single Higgs bkg models for Mjj: 
```
./bin/MjjSignalFit -t models_file.rs -d input_dir  -p plot_dir --year 2017  --procs tth  -o outdir -i inputfiles

```
My command for signal :
```
./bin/MjjSignalFit -t flashggFinalFit/MetaData_HHbbgg/models_2D_higgs_mjj70_16_02_2020.rs -d input_dir  -p plot_dir --year 2017  --procs hh_node_SM  -o outdir 
```
My command for single Higgs :
```
./bin/MjjSignalFit -t flashggFinalFit/MetaData_HHbbgg/models_2D_higgs_mjj70_16_02_2020.rs -d input_dir  -p plot_dir --year 2017  --procs tth,ggh,vh,qqh  -o outdir -m true
```

All the available options are summarized in the OptionParser : 
https://github.com/chernyavskaya/flashggFinalFit/blob/fullRunII_approval1D/Signal/test/MjjSignalFit.cpp#L70

If you want to merge datasets into 3 MVA categories to perform fits , do -m true

If you do not provide any inputs files, then the following convention will be assumed : indir_+"output_"+iproc+"_"+year_+".root";

You need to provide a template fit file :
https://github.com/chernyavskaya/flashggFinalFit/blob/fullRunII_approval1D/Signal/test/MjjSignalFit.cpp#L75
example : https://github.com/chernyavskaya/flashggFinalFit/blob/fullRunII_approval1D/MetaData_HHbbgg/models_2D_higgs_mjj70_11_02_2020.rs

Name of the input workspace is the same as for everything else in flashggFinalFits framework 'tagsDumper/cms_hgg_13TeV' : 
https://github.com/chernyavskaya/flashggFinalFit/blob/fullRunII_approval1D/Signal/test/MjjSignalFit.cpp#L141

When all fits are prepared .root files are saved. They should be merged the same way as for Mgg fits using : 
```
mergeWorkspace.py workspace_out_mjj.root *.root
```

Now we need to merge Mgg workspaces and Mjj in one final workspace file : 
```
python createMjjMggModel.py -.... options for input files, etc
```
https://github.com/chernyavskaya/flashggFinalFit/blob/fullRunII_approval1D/Signal/test/createMjjMggModel.py

Done! Now you can prepare the datacards.
