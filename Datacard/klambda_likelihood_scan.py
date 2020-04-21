import os,sys,copy,math
import numpy as np
import shutil
import json
import ROOT as r
from optparse import OptionParser
from ROOT import TCanvas,TGraph,TLegend
from array import array


parser = OptionParser()
parser.add_option("--DatacardDir",default='./cards/MAR1620_HHsignal_HHcats_WITHSYST_v4/',help="datacard directory" )
(options,args)=parser.parse_args()

##########################################################################################################
### SETTINGS

#SignalProcs='tth_2016,tth_2017,tth_2018'
SignalProcs='hh_node_SM_2016,hh_node_SM_2017,hh_node_SM_2018'
#SignalProcs='hh_node_SM_2016,hh_node_SM_2017,hh_node_SM_2018,tth_2016,tth_2017,tth_2018'
#SignalProcs='ggh_2017,qqh_2017,hh_node_SM_2017,vh_2017,ggh_2018,qqh_2018,hh_node_SM_2018,vh_2018,ggh_2016,qqh_2016,hh_node_SM_2016,vh_2016,tth_2016,tth_2017,tth_2018,thq_2016,thq_2017,thq_2018'

rewProc = SignalProcs
#rewProc = 'hh_node_SM_2016,hh_node_SM_2017,hh_node_SM_2018,tth_2016,tth_2017,tth_2018'

#Categories='DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11,TTHHadronicTag_0,TTHHadronicTag_1,TTHHadronicTag_2,TTHHadronicTag_3,TTHLeptonicTag_0,TTHLeptonicTag_1,TTHLeptonicTag_2,TTHLeptonicTag_3'
Categories2D='DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11'
#Categories='DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11'
Categories='DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11'#,TTHHadronicTag_0,TTHHadronicTag_1,TTHHadronicTag_2,TTHHadronicTag_3,TTHLeptonicTag_0,TTHLeptonicTag_1,TTHLeptonicTag_2,TTHLeptonicTag_3,UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3'

MCWorkspaces='\
/eos/user/f/fmonti/HHbbgg_run2/workspaces/MAR1620/ws/output_ggh_2016.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/MAR1620/ws/output_hh_node_SM_2016.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/MAR1620/ws/output_qqh_2016.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/MAR1620/ws/output_tth_2016.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/MAR1620/ws/output_vh_2016.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/MAR1620/ws/output_thq_2016.root,\
\
/eos/user/f/fmonti/HHbbgg_run2/workspaces/MAR1620/ws/output_ggh_2017.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/MAR1620/ws/output_hh_node_SM_2017.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/MAR1620/ws/output_qqh_2017.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/MAR1620/ws/output_tth_2017.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/MAR1620/ws/output_vh_2017.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/MAR1620/ws/output_thq_2017.root,\
\
/eos/user/f/fmonti/HHbbgg_run2/workspaces/MAR1620/ws/output_ggh_2018.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/MAR1620/ws/output_hh_node_SM_2018.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/MAR1620/ws/output_qqh_2018.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/MAR1620/ws/output_tth_2018.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/MAR1620/ws/output_vh_2018.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/MAR1620/ws/output_thq_2018.root,\
\
/eos/user/f/fmonti/HHbbgg_run2/workspaces/MAR1620/ws/output_hh_node_SM_Untagged_2017.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/MAR1620/ws/output_hh_node_SM_Untagged_2018.root'

MCModels='/eos/user/f/fmonti/HHbbgg_run2/workspaces/MAR1620/SIGmodel/CMS-HGG_sigfit_MggMjj_2016_2017_2018_MAR1620.root'
DataWorkspace='/eos/user/f/fmonti/HHbbgg_run2/workspaces/MAR1620/BKGmodel/CMS-HGG_multipdf1D_TTHandUntaggedTags_MAR1620.root'
DataWorkspace2D="/eos/user/f/fmonti/HHbbgg_run2/workspaces/MAR1620/BKGmodel/CMS-HGGHJJ_DoubleEG_Mjj_70GeV_MAR1620.root"
AllProcs='ggh_2016,qqh_2016,hh_node_SM_2016,vh_2016,tth_2016,thq_2016,ggh_2017,qqh_2017,hh_node_SM_2017,vh_2017,tth_2017,thq_2017,ggh_2018,qqh_2018,hh_node_SM_2018,vh_2018,tth_2018,thq_2018'
doSyst=1
Scales="../Signal/dat/photonCatSyst.dat"
Smears="../Signal/dat/photonCatSyst.dat"
Scalescorr=""
Scaleglobals=""
IntLumi2016=35.91
IntLumi2017=41.53 
IntLumi2018=59.35

##########################################################################################################

##############################################
#produce the SM datacard
print("mkdir -p %s"%options.DatacardDir)
#os.sysyem("mkdir %s"%options.DatacardDir)

SMdatacard=os.path.abspath(options.DatacardDir+"/SMdatacard.txt")

command  ="python makeParametricModelDatacardFLASHgg.py "
command +="-i %s "%MCWorkspaces
command +="-s %s "%MCModels
command +="--nodesFile %s "%MCModels
command +="--signalProc %s "%SignalProcs
command +="-d %s "%DataWorkspace
command +="--dataFile2D %s "%DataWorkspace2D
command +="-p %s "%AllProcs
command +="-c %s "%Categories
command +="--cats2D %s "%Categories2D
command +="--photonCatScales %s "%Scales
command +="--photonCatSmears %s "%Smears
command +="--globalScales %s "%Scaleglobals
command +="--photonCatScalesCorr %s "%Scalescorr
command +="--isMultiPdf "
command +="--intLumi2016 %f "%IntLumi2016
command +="--intLumi2017 %f "%IntLumi2017
command +="--intLumi2018 %f "%IntLumi2018
command +="--do_HHbbgg_systematics %i "%doSyst
#command +="--do2D "#--btagReshapeFalse 1 "
command +="-o %s "%SMdatacard

print "SM datacard command: "+command
