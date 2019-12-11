import os,sys,copy,math
import numpy as np
import shutil
import json
import ROOT as r
from optparse import OptionParser
from ROOT import TCanvas,TGraph,TLegend
from array import array


parser = OptionParser()
parser.add_option("--DatacardDir",default='./cards/klscan_tthandhh_extended_fine/',help="datacard directory" )
(options,args)=parser.parse_args()

##########################################################################################################
### SETTINGS

#SignalProcs='tth_2016,tth_2017,tth_2018'
#SignalProcs='hh_node_SM_2016,hh_node_SM_2017,hh_node_SM_2018'
SignalProcs='hh_node_SM_2016,hh_node_SM_2017,hh_node_SM_2018,tth_2016,tth_2017,tth_2018'
#SignalProcs='ggh_2017,qqh_2017,hh_node_SM_2017,vh_2017,ggh_2018,qqh_2018,hh_node_SM_2018,vh_2018,ggh_2016,qqh_2016,hh_node_SM_2016,vh_2016,tth_2016,tth_2017,tth_2018'

#Categories='DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11'
Categories='DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11,THQLeptonicTag,TTHHadronicTag_0,TTHHadronicTag_1,TTHHadronicTag_2,TTHHadronicTag_3,TTHLeptonicTag_0,TTHLeptonicTag_1,TTHLeptonicTag_2,TTHLeptonicTag_3,UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,VBFTag_0,VBFTag_1,VBFTag_2,VHHadronicTag,VHLeptonicLooseTag,VHMetTag,WHLeptonicTag' #,ZHLeptonicTag'

#Nkl =   16
#klmin = -5.5
#klmax = 10.5
#Nkt =    7
#ktmin =  0.65
#ktmax =  1.35

Nkl   = 35
klmin = -6.25
klmax = 11.25
Nkt   = 21
ktmin = -2.1
ktmax =  2.1

#hhReweightDir = "/eos/user/f/fmonti/HHbbgg_run2/workspaces/NOV142019/ktkl_yields/"
hhReweightDir = "/eos/user/f/fmonti/HHbbgg_run2/workspaces/NOV142019/ktkl_yields_extended_fine/"

MCWorkspaces='/eos/user/f/fmonti/HHbbgg_run2/workspaces/NOV142019/ws2016/ggh_2016.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/NOV142019/ws2016/hh_node_SM_2016.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/NOV142019/ws2016/qqh_2016.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/NOV142019/ws2016/tth_2016.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/NOV142019/ws2016/vh_2016.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/NOV142019/ws2017/ggh_2017.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/NOV142019/ws2017/hh_node_SM_2017.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/NOV142019/ws2017/qqh_2017.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/NOV142019/ws2017/tth_2017.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/NOV142019/ws2017/vh_2017.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/NOV142019/ws2018/ggh_2018.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/NOV142019/ws2018/hh_node_SM_2018.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/NOV142019/ws2018/qqh_2018.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/NOV142019/ws2018/tth_2018.root,/eos/user/f/fmonti/HHbbgg_run2/workspaces/NOV142019/ws2018/vh_2018.root'
MCModels='/afs/cern.ch/user/f/fmonti/work/flashggFinalFit/CMSSW_7_4_7/src/flashggFinalFit/Signal/output/out_fit_20_11_2019_all3years.root'
DataWorkspace='/afs/cern.ch/user/f/fmonti/work/flashggFinalFit/CMSSW_7_4_7/src/flashggFinalFit/Background/CMS-HGG_multipdf_HHbbgg_allyears_20_11_2019.root'
AllProcs='ggh_2017,qqh_2017,hh_node_SM_2017,vh_2017,ggh_2018,qqh_2018,hh_node_SM_2018,vh_2018,ggh_2016,qqh_2016,hh_node_SM_2016,vh_2016,tth_2016,tth_2017,tth_2018'

Scales=""
Smears=""
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
command +="--signalProc %s "%SignalProcs
command +="-d %s "%DataWorkspace
command +="-p %s "%AllProcs
command +="-c %s "%Categories
command +="--photonCatScales %s "%Scales
command +="--photonCatSmears %s "%Smears
command +="--globalScales %s "%Scaleglobals
command +="--photonCatScalesCorr %s "%Scalescorr
command +="--isMultiPdf "
command +="--intLumi2016 %f "%IntLumi2016
command +="--intLumi2017 %f "%IntLumi2017
command +="--intLumi2018 %f "%IntLumi2018
command +="-o %s "%SMdatacard
print "SM datacard command: "+command
#os.system(command) 

##############################################
#produce a datacard for each kl kt point

rewProc = SignalProcs

command = command.replace(" -o "," --hhReweightSM ")
command += " --do_kl_scan "
command += " --Nkl %i --klmin %f --klmax %f --Nkt %i --ktmin  %f --ktmax %f"%(Nkl,klmin,klmax,Nkt,ktmin,ktmax)
command += " --hhReweightDir %s "%hhReweightDir
command += " --rewProc %s "%rewProc
command += " --toSkip NoTag,ZHLeptonicTag,TTHDiLeptonTag"
print "kl,kt datacards command: "+command
#os.system(command)

##############################################
#convert the txt datacards to root datacards
text2workspace_jobs_dir = "%s/text2workspace_jobs/"%options.DatacardDir
os.system("mkdir -p "+text2workspace_jobs_dir)
SM_rootdatacardname = SMdatacard.replace('.txt','.root')
text2workspace_command = 'text2workspace.py -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel --PO verbose -m 125.00'
if any("hh" in proc for proc in SignalProcs.split(',')):
    text2workspace_command += ' --PO \'map=.*/hh_node_SM*:mu_hh[1,0,2]\' '
if any("tth" in proc for proc in SignalProcs.split(',')):
    text2workspace_command += ' --PO \'map=.*/tth*:mu_tth[1,0,2]\' '
if any("qqh" in proc for proc in SignalProcs.split(',')):
    text2workspace_command += ' --PO \'map=.*/qqh*:mu_qqh[1,0,2]\' '
if any("vh" in proc for proc in SignalProcs.split(',')):
    text2workspace_command += ' --PO \'map=.*/vh*:mu_vh[1,0,2]\' '
if any("ggh" in proc for proc in SignalProcs.split(',')):
    text2workspace_command += ' --PO \'map=.*/ggh*:mu_ggh[1,0,2]\' '
text2workspace_command += ' %s -o %s '%(SMdatacard,SM_rootdatacardname)
#print text2workspace_command
#os.system(text2workspace_command)                                                  
text2workspace_scriptname = text2workspace_jobs_dir+"/job_SM.sh"
text2workspace_script = open(text2workspace_scriptname ,'w')
text2workspace_script.write('#!/bin/sh\ncd %s\neval `scramv1 runtime -sh`\ncd -\n'%os.getcwd())
text2workspace_script.write(text2workspace_command+"\n")
text2workspace_script.write("echo DONE \n")
text2workspace_script.close()
os.system("chmod +x "+text2workspace_scriptname);

for ikl in range(0,Nkl):
    kl = klmin + (ikl+0.5)*(klmax-klmin)/Nkl
    for ikt in range(0,Nkt):
        kt = ktmin + (ikt+0.5)*(ktmax-ktmin)/Nkt;
        txtdatacardname = SMdatacard.replace('.txt','_kl_%.3f_kt_%.3f.txt'%(kl,kt))
        rootdatacardname = txtdatacardname.replace('.txt','.root')
        text2workspace_command = 'text2workspace.py -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel --PO verbose -m 125.00'
        if any("hh" in proc for proc in SignalProcs.split(',')):
            text2workspace_command += ' --PO \'map=.*/hh_node_SM*:mu_hh[1,0,2]\' '
        if any("tth" in proc for proc in SignalProcs.split(',')):
            text2workspace_command += ' --PO \'map=.*/tth*:mu_tth[1,0,2]\' '
        if any("qqh" in proc for proc in SignalProcs.split(',')):
            text2workspace_command += ' --PO \'map=.*/qqh*:mu_qqh[1,0,2]\' '
        if any("vh" in proc for proc in SignalProcs.split(',')):
            text2workspace_command += ' --PO \'map=.*/vh*:mu_vh[1,0,2]\' '
        if any("ggh" in proc for proc in SignalProcs.split(',')):
            text2workspace_command += ' --PO \'map=.*/ggh*:mu_ggh[1,0,2]\' '
        text2workspace_command += ' %s -o %s '%(txtdatacardname,rootdatacardname)
        #print text2workspace_command
        #os.system(text2workspace_command)
        text2workspace_scriptname = text2workspace_jobs_dir+"/job_kl_%.3f_kt_%.3f.sh"%(kl,kt)
        text2workspace_script = open(text2workspace_scriptname ,'w')
        text2workspace_script.write('#!/bin/sh\ncd %s\neval `scramv1 runtime -sh`\ncd -\n'%os.getcwd())
        text2workspace_script.write(text2workspace_command+"\n")
        text2workspace_script.write("echo DONE \n")
        text2workspace_script.close()
        os.system("chmod +x "+text2workspace_scriptname);

print("writing .sub file")
condorsubname = text2workspace_jobs_dir+"/submit_jobs.sub"
condorsub = open(condorsubname,'w')
#condorsub.write('requirements = (OpSysAndVer =?= "SLCern6")\n')
condorsub.write("executable            = $(scriptname)\n")
condorsub.write("output                = $(scriptname).out\n")
condorsub.write("error                 = $(scriptname).err\n")
condorsub.write("log                   = $(scriptname).log\n")
condorsub.write('+JobFlavour           = "microcentury"\n')
condorsub.write("queue scriptname matching %s/job_*.sh"%(os.path.abspath(text2workspace_jobs_dir)))
condorsub.close()
print("condor_submit "+condorsubname)


##############################################                                                                                                          
#generate an Asimov distribution for the SM expectation of sig (klambda = 1) + bkg
parametersettings_option=""
if any("hh" in proc for proc in SignalProcs.split(',')):
    if(parametersettings_option==""):
        parametersettings_option=" --setPhysicsModelParameters mu_hh=1"
    else:
        parametersettings_option+=",mu_hh=1"
if any("tth" in proc for proc in SignalProcs.split(',')):
    if(parametersettings_option==""):
        parametersettings_option=" --setPhysicsModelParameters mu_tth=1"
    else:
        parametersettings_option+=",mu_tth=1"
if any("vh" in proc for proc in SignalProcs.split(',')):
    if(parametersettings_option==""):
        parametersettings_option=" --setPhysicsModelParameters mu_vh=1"
    else:
        parametersettings_option+=",mu_vh=1"
if any("qqh" in proc for proc in SignalProcs.split(',')):
    if(parametersettings_option==""):
        parametersettings_option=" --setPhysicsModelParameters mu_qqh=1"
    else:
        parametersettings_option+=",mu_qqh=1"
if any("ggh" in proc for proc in SignalProcs.split(',')):
    if(parametersettings_option==""):
        parametersettings_option=" --setPhysicsModelParameters mu_ggh=1"
    else:
        parametersettings_option+=",mu_ggh=1"

parametersettings_option+=" "

print "... generating SM expectation"
asimov_command =  "combine -M GenerateOnly -t -1 -m 125.00"
asimov_command += parametersettings_option
asimov_command += "--saveToys "
asimov_command += "-n SM_toys "
asimov_command += SM_rootdatacardname
asimov_name = "higgsCombineSM_toys.GenerateOnly.mH125.123456.root"
print "asimov command: "+asimov_command+" && mv "+asimov_name+" "+options.DatacardDir
asimov_name = os.path.abspath(options.DatacardDir+"/"+asimov_name)
#os.system(asimov_command)

##############################################                                                                                                          
#run combine for each point of the grid
likelihood_jobs_dir = "%s/likelihood_jobs/"%options.DatacardDir
likelihood_out_dir = "%s/likelihood_out/"%options.DatacardDir
os.system("mkdir -p "+likelihood_jobs_dir)
os.system("mkdir -p "+likelihood_out_dir)

fixPOI_option_r1 = parametersettings_option.replace("--setPhysicsModelParameters","--fixedPointPOIs")
fixPOI_option_r0 = fixPOI_option_r1.replace("=1","=0")

for ikl in range(0,Nkl):
    kl = klmin + (ikl+0.5)*(klmax-klmin)/Nkl
    for ikt in range(0,Nkt):
        kt = ktmin + (ikt+0.5)*(ktmax-ktmin)/Nkt;
        rootdatacardname = SMdatacard.replace('.txt','_kl_%.3f_kt_%.3f.root'%(kl,kt))
        likelihood_command_r1  = "combine -M MultiDimFit --algo fixed --saveNLL -t -1 -m 125.00 "
        likelihood_command_r1 += fixPOI_option_r1
        likelihood_command_r1 += " --toysFile %s "%asimov_name
        likelihood_command_r1 += " -n bbgg_result_r1_kl_%.3f_kt_%.3f "%(kl,kt)
        likelihood_command_r1 += rootdatacardname
        likelihood_command_r0  = "combine -M MultiDimFit --algo fixed --saveNLL -t -1 -m 125.00 "
        likelihood_command_r0 += fixPOI_option_r0
        likelihood_command_r0 += " --toysFile %s "%asimov_name
        likelihood_command_r0 += " -n bbgg_result_r0_kl_%.3f_kt_%.3f "%(kl,kt)
        likelihood_command_r0 += rootdatacardname
        #print "likelihood command: "+likelihood_command_r1
        #os.system(likelihood_command_r1)
        likelihood_scriptname = likelihood_jobs_dir+"/job_kl_%.3f_kt_%.3f.sh"%(kl,kt)
        likelihood_script = open(likelihood_scriptname ,'w')
        likelihood_script.write('#!/bin/sh\ncd %s\neval `scramv1 runtime -sh`\ncd -\n'%os.getcwd())
        likelihood_script.write(likelihood_command_r1+"\n")
        likelihood_script.write(likelihood_command_r0+"\n")
        likelihood_script.write("cp *bbgg_result_r*_kl_%.3f_kt_%.3f*.root %s\n"%(kl,kt,os.path.abspath(likelihood_out_dir)) )
        likelihood_script.write("echo DONE \n")
        likelihood_script.close()
        os.system("chmod +x "+likelihood_scriptname);


print("writing .sub file")
condorsubname = likelihood_jobs_dir+"/submit_jobs.sub"
condorsub = open(condorsubname,'w')
#condorsub.write('requirements = (OpSysAndVer =?= "SLCern6")\n')
condorsub.write("executable            = $(scriptname)\n")
condorsub.write("output                = $(scriptname).out\n")
condorsub.write("error                 = $(scriptname).err\n")
condorsub.write("log                   = $(scriptname).log\n")
condorsub.write('+JobFlavour           = "microcentury"\n')
condorsub.write("queue scriptname matching %s/job_*.sh"%(os.path.abspath(likelihood_jobs_dir)))
condorsub.close()
print("condor_submit "+condorsubname)
