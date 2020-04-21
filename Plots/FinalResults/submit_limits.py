#!/usr/bin/env python

import os
import numpy
import sys
import fnmatch
from copy import deepcopy as copy
import re
import json

from optparse import OptionParser
from optparse import OptionGroup


from Queue import Queue

from threading import Thread, Semaphore
from multiprocessing import cpu_count

class Wrap:
    def __init__(self, func, args, queue):
        self.queue = queue
        self.func = func
        self.args = args
        
    def __call__(self):
        ret = self.func( *self.args )
        self.queue.put( ret  )

    
class Parallel:
    def __init__(self,ncpu):
        self.running = Queue(ncpu)
        self.returned = Queue()
        self.njobs = 0
  
    def run(self,cmd,args):
        wrap = Wrap( self, (cmd,args), self.returned )
        self.njobs += 1
        thread = Thread(None,wrap)
        thread.start()
        
    def __call__(self,cmd,args):
        if type(cmd) == str:
            print cmd
            for a in args:
                cmd += " %s " % a
            args = (cmd,)
            cmd = commands.getstatusoutput
        self.running.put((cmd,args))
        ret = cmd( *args ) 
        self.running.get()
        self.running.task_done()
        return ret


parser = OptionParser()
parser.add_option("-d","--datfile",help="Pick up running options from datfile")
parser.add_option("--cmssw",default='/work/nchernya/DiHiggs/CMSSW_10_2_13/src/HiggsAnalysis/CombinedLimit/',help="path to CMSSW" )
parser.add_option("--cats",default="DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11", help = "categories")
parser.add_option("--channels_to_run",default="all", help = "which channels to run on")
#parser.add_option("--freeze_kl_fit_params",default = "--freezeNuisances param0_DoubleHTag_0,param1_DoubleHTag_0,param2_DoubleHTag_0,param0_DoubleHTag_1,param1_DoubleHTag_1,param2_DoubleHTag_1,param0_DoubleHTag_2,param1_DoubleHTag_2,param2_DoubleHTag_2,param0_DoubleHTag_3,param1_DoubleHTag_3,param2_DoubleHTag_3,param0_DoubleHTag_4,param1_DoubleHTag_4,param2_DoubleHTag_4,param0_DoubleHTag_5,param1_DoubleHTag_5,param2_DoubleHTag_5,param0_DoubleHTag_6,param1_DoubleHTag_6,param2_DoubleHTag_6,param0_DoubleHTag_7,param1_DoubleHTag_7,param2_DoubleHTag_7,param0_DoubleHTag_8,param1_DoubleHTag_8,param2_DoubleHTag_8,param0_DoubleHTag_9,param1_DoubleHTag_9,param2_DoubleHTag_9,param0_DoubleHTag_10,param1_DoubleHTag_10,param2_DoubleHTag_10,param0_DoubleHTag_11,param1_DoubleHTag_11,param2_DoubleHTag_11")
parser.add_option("--freeze_kl_fit_params",default = "--freezeParameters param0_DoubleHTag_0,param1_DoubleHTag_0,param2_DoubleHTag_0,param0_DoubleHTag_1,param1_DoubleHTag_1,param2_DoubleHTag_1,param0_DoubleHTag_2,param1_DoubleHTag_2,param2_DoubleHTag_2,param0_DoubleHTag_3,param1_DoubleHTag_3,param2_DoubleHTag_3,param0_DoubleHTag_4,param1_DoubleHTag_4,param2_DoubleHTag_4,param0_DoubleHTag_5,param1_DoubleHTag_5,param2_DoubleHTag_5,param0_DoubleHTag_6,param1_DoubleHTag_6,param2_DoubleHTag_6,param0_DoubleHTag_7,param1_DoubleHTag_7,param2_DoubleHTag_7,param0_DoubleHTag_8,param1_DoubleHTag_8,param2_DoubleHTag_8,param0_DoubleHTag_9,param1_DoubleHTag_9,param2_DoubleHTag_9,param0_DoubleHTag_10,param1_DoubleHTag_10,param2_DoubleHTag_10,param0_DoubleHTag_11,param1_DoubleHTag_11,param2_DoubleHTag_11")
parser.add_option("--hhReweightDir",default='/work/nchernya/DiHiggs/inputs/18_02_2020/categorizedTrees/kl_kt_finebinning/',help="hh reweighting directory with all txt files" )
parser.add_option("--do2D",type="int",default=0,help="do 2D or 1D " )
parser.add_option("--doNLOHH",type="int",default=0,help="do NLO HH model or not " )
parser.add_option("--do_kl_scan",default=False,action="store_true",help="do kl scan?" )
parser.add_option("--Nbench",type="int",default=14,help="nunber of benchmarks" )
parser.add_option("--do_benchmarks_scan",default=False,action="store_true",help="do benchmark scan?" )
parser.add_option("--do_kl_likelihood",default=False,action="store_true",help="prepare datacard for kl likelihood" )
parser.add_option("--kl_likelihood_float_mu",default=False,action="store_true",help="kl likelihood, float r" )
parser.add_option("--generateAsimovHHSM",default=False,action="store_true",help="generate SM S+B HH Asimov" )
parser.add_option("-q","--queue",default='short.q',help="Which batch queue")
parser.add_option("--dryRun",default=False,action="store_true",help="Dont submit")
parser.add_option("--parallel",default=False,action="store_true",help="Run local fits in multithreading")
parser.add_option("--runLocal",default=False,action="store_true",help="Run locally")
parser.add_option("--hadd",help="Trawl passed directory and hadd files. To be used when jobs are complete.")
parser.add_option("--resubmitFailures",help=" Provide directory and the script will find failed jobs and resubmit them")
parser.add_option("-v","--verbose",default=False,action="store_true")
parser.add_option("--poix",default="r")
parser.add_option("--S0",default=False,action="store_true",help="Stats only, not sure this will work, please make sure it does take into account discrete profiling. Risk at your own risk.")
parser.add_option("--batch",default="T3CH",help="Which batch system to use (LSF,IC)")
parser.add_option("--prefix",default="./")
parser.add_option("--freezeAll",default=False,action="store_true",help="Freeze all nuisances")
parser.add_option("--float",default="",action="store",help="Freeze all nuisances")
parser.add_option("--postFitAll",default=False,action="store_true",help="Use post-fit nuisances for all methods")
specOpts = OptionGroup(parser,"Specific options")
specOpts.add_option("--datacard",default=None)
specOpts.add_option("--files",default=None)
specOpts.add_option("--outDir",default=None)
specOpts.add_option("--outtag",default=None)
specOpts.add_option("--justThisSyst",default=None)
specOpts.add_option("--method",default=None)
specOpts.add_option("--label",default=None)
specOpts.add_option("--expected",type="int",default=1)
specOpts.add_option("--toysFile",default=None)
specOpts.add_option("--mh",type="float",default=None)
specOpts.add_option("--expectSignal",type="float",default=None)
specOpts.add_option("--jobs",type="int",default=None)
specOpts.add_option("--pointsperjob",type="int",default=1)
parser.add_option_group(specOpts)
(opts,args) = parser.parse_args()

allowedMethods = ['Asymptotic','MultiDimFit','GenerateOnly']

defaults = copy(opts)
print "INFO - queue ", opts.queue
def system(exec_line):
  #print "[INFO] defining exec_line"
  #if opts.verbose: print '\t', exec_line
  os.system(exec_line)


def writePreamble(sub_file):
  workdir = os.getcwd()
  #print "[INFO] writing preamble"
  sub_file.write('#!/bin/bash\n')
  if (opts.batch == "T3CH"):
      sub_file.write('#SBATCH --job-name=test_combine_slurm\n')
      sub_file.write('#SBATCH --account=t3\n')
      sub_file.write('#SBATCH --nodes=1\n')
      sub_file.write('#SBATCH -o %s.log\n'%os.path.abspath(sub_file.name))
      sub_file.write('#SBATCH -o %s.err\n'%os.path.abspath(sub_file.name))
      sub_file.write('set -x\n')
  if (opts.batch == "T3CH_qsub"):
      sub_file.write('set -x\n')
  sub_file.write('touch %s.run\n'%os.path.abspath(sub_file.name))
  sub_file.write('cd %s\n'%os.getcwd())
  if (opts.batch == "T3CH_qsub"):
      sub_file.write('source $VO_CMS_SW_DIR/cmsset_default.sh\n')
      sub_file.write('source /mnt/t3nfs01/data01/swshare/glite/external/etc/profile.d/grid-env.sh\n')
      sub_file.write('export SCRAM_ARCH=slc6_amd64_gcc481\n')
      sub_file.write('export LD_LIBRARY_PATH=/swshare/glite/d-cache/dcap/lib/:$LD_LIBRARY_PATH\n')
      sub_file.write('set +x\n') 
  if (opts.batch == "T3CH"):
      sub_file.write('cd %s\n'%opts.cmssw)
  sub_file.write('eval `scramv1 runtime -sh`\n')
  sub_file.write('export PYTHONPATH=/work/nchernya/DiHiggs/CMSSW_7_4_7/src/flashggFinalFit/Plots/FinalResults/:$PYTHONPATH\n')
  sub_file.write('cd %s\n'%os.getcwd())
  if (opts.batch == "T3CH_qsub"):
      sub_file.write('set -x\n') 
  #sub_file.write('cd -\n')
 # if (opts.batch == "T3CH" ) : sub_file.write('cd $TMPDIR\n')
 # sub_file.write('number=$RANDOM\n')
 # sub_file.write('mkdir -p scratch_$number\n')
  #sub_file.write('cd scratch_$number\n')


def writePostamble(sub_file, exec_line,outtag):

  #print "[INFO] writing to postamble"
  sub_file.write('if ( %s ) then\n'%exec_line)
  sub_file.write('\t mv higgsCombine%s*.root %s\n'%(outtag,os.path.abspath(opts.outDir)))
  sub_file.write('\t touch %s.done\n'%os.path.abspath(sub_file.name))
  sub_file.write('else\n')
  sub_file.write('\t touch %s.fail\n'%os.path.abspath(sub_file.name))
  sub_file.write('fi\n')
  sub_file.write('rm -f %s.run\n'%os.path.abspath(sub_file.name))
  sub_file.write('rm -rf scratch_$number\n')
  sub_file.close()
  system('chmod +x %s'%os.path.abspath(sub_file.name))
  if opts.runLocal:
     system('bash %s > %s.log'%(os.path.abspath(sub_file.name),os.path.abspath(sub_file.name)))
  elif opts.queue:
    system('rm -f %s.done'%os.path.abspath(sub_file.name))
    system('rm -f %s.fail'%os.path.abspath(sub_file.name))
    system('rm -f %s.log'%os.path.abspath(sub_file.name))
    system('rm -f %s.err'%os.path.abspath(sub_file.name))
    if (opts.batch == "LSF") : system('bsub -q %s -o %s.log %s'%(opts.queue,os.path.abspath(sub_file.name),os.path.abspath(sub_file.name)))
    if (opts.batch == "IC") : system('qsub -q %s -o %s.log -e %s.err %s > out.txt'%(opts.queue,os.path.abspath(sub_file.name),os.path.abspath(sub_file.name),os.path.abspath(sub_file.name)))
    if (opts.batch == "T3CH_qsub") : 
          command = 'qsub -q %s -o %s.log -e %s.err %s > out.txt'%(opts.queue,os.path.abspath(sub_file.name),os.path.abspath(sub_file.name),os.path.abspath(sub_file.name))
          print command
          system(command)
    if (opts.batch == "T3CH") : 
          command = 'sbatch %s > out.txt'%(os.path.abspath(sub_file.name))
          print command
          system(command)

def writeAsymptotic(jobid,card,outtag):
    print '[INFO] Writing Asymptotic'
    file = open('%s/Jobs/sub_job%d.sh'%(opts.outDir,jobid),'w')
    writePreamble(file)
    exec_line =  'combine %s/%s -n %s -M Asymptotic -m 125.00 --cminDefaultMinimizerType=Minuit2 -L $CMSSW_BASE/lib/$SCRAM_ARCH/libHiggsAnalysisGBRLikelihood.so  --rRelAcc 0.001 '%(os.getcwd(),card,outtag)
    if opts.S0: exec_line += ' -S 0 '
    if opts.expected: exec_line += ' --run=blind -t -1'
    writePostamble(file,exec_line,outtag)


def text2workspace(card,mask=False,model=''):
    if '.root' in card : 
       return '\n'
    print '[INFO] Converting text to workspace'
    if not mask : exec_line = "text2workspace.py %s/%s %s\n"%(os.getcwd(),card,model)
    else  : exec_line = "text2workspace.py %s/%s  --channel-masks %s\n"%(os.getcwd(),card,model)
    return exec_line


def writeAsymptoticFor2D(jobid,card,outtag,kl=1.):
    print '[INFO] MultiDim Fit for 2D'
    file = open('%s/Jobs/sub_job%d.sh'%(opts.outDir,jobid),'w')
    writePreamble(file)
    if opts.doNLOHH: 
       model = ' -P HHModel:HHdefault'
       exec_line = text2workspace(card,model=model)
       exec_line += "combine %s/%s  -n %s  -M AsymptoticLimits -m 125. --saveWorkspace --redefineSignalPOIs r --setParameters r_qqhh=1,r_gghh=1,kt=1,kl=%.3f,CV=1,C2V=1 --freezeParameters r_gghh,r_qqhh,kt,kl,CV,C2V  --X-rtd TMCSO_AdaptivePseudoAsimov=0 --X-rtd TMCSO_PseudoAsimov=0 --cminDefaultMinimizerStrategy 0 --cminFallbackAlgo Minuit2,Migrad,0:0.1 --X-rt MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 "%(os.getcwd(),card.replace(".txt",".root"),outtag,kl)
       if opts.S0: exec_line += ' -S 0 '
       if opts.expected: exec_line += ' --run=blind -t -1'
    else: 
       exec_line = text2workspace(card)
       if opts.expected: 
          exec_line += "combine %s/%s  -n %s  -M MultiDimFit -m 125. --saveWorkspace --X-rtd TMCSO_AdaptivePseudoAsimov=0 --X-rtd TMCSO_PseudoAsimov=0 --cminDefaultMinimizerStrategy 0 --cminFallbackAlgo Minuit2,Migrad,0:0.1 --X-rt MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2"%(os.getcwd(),card.replace(".txt",".root"),outtag)
          if opts.expected: exec_line += ' -t -1' 
          exec_line += '\n' 
          exec_line += "combine higgsCombine%s.MultiDimFit.mH125.root --snapshotName MultiDimFit -n %s  -M AsymptoticLimits -m 125. --saveWorkspace --X-rtd TMCSO_AdaptivePseudoAsimov=0 --X-rtd TMCSO_PseudoAsimov=0 --cminDefaultMinimizerStrategy 0 --cminFallbackAlgo Minuit2,Migrad,0:0.1 --X-rt MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2"%(outtag,outtag)
          if opts.S0: exec_line += ' -S 0 '
          if opts.expected: exec_line += ' --run=blind -t -1'
       else: 
          exec_line += "combine %s/%s  -n %s  -M AsymptoticLimits -m 125.  --X-rtd TMCSO_AdaptivePseudoAsimov=0 --X-rtd TMCSO_PseudoAsimov=0 --cminDefaultMinimizerStrategy 0 --cminFallbackAlgo Minuit2,Migrad,0:0.1 --X-rt MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2"%(os.getcwd(),card.replace(".txt",".root"),outtag)


    writePostamble(file,exec_line,outtag)



def writeMultiDimFitLikelihood(card,toysFile,channels="all",kl_range="-10,15",cats_map_mask={"MVA0":""}):
    print "[INFO] writing multidim fit"
    mask_str = ""
    if channels!="all" and not "MVA" in channels :
       for cat in opts.cats.split(","):
         if channels != cat:
           mask_str += ",mask_%s_13TeV=1"%(cat)
    elif "MVA" in channels :
      for to_mask in set(cats_map_mask[channels])^set(opts.cats.split(",")): 
           mask_str += ",mask_%s_13TeV=1"%(to_mask)
    for i in range(opts.jobs):
       file = open('%s/Jobs/sub_%s_job_kl_%d.sh'%(opts.outDir,channels,i),'w')
       writePreamble(file)
       if not opts.kl_likelihood_float_mu: #to run with r=1
          if not opts.do2D : exec_line = 'combine %s/%s -M MultiDimFit -m 125.00 --algo grid --points %s -P kl --floatOtherPOIs 0 --setPhysicsModelParameterRanges kl=%s --setPhysicsModelParameters r=1%s --firstPoint=%d --lastPoint=%d -n MultiDim_%s_%s_Job%d -L $CMSSW_BASE/lib/$SCRAM_ARCH/libHiggsAnalysisGBRLikelihood.so %s '%(os.getcwd(),card,opts.pointsperjob*opts.jobs,kl_range,mask_str,i*opts.pointsperjob,(i+1)*opts.pointsperjob-1,channels,opts.outtag,i,opts.freeze_kl_fit_params)
          else : 
             if opts.doNLOHH: 
                exec_line = 'combine %s/%s -M MultiDimFit -m 125.00 --algo grid --points %s  --redefineSignalPOIs kl  --setParameterRanges kl=%s --setParameters r=1,r_qqhh=1,r_gghh=1,kt=1,CV=1,C2V=1%s --freezeParameters r,r_gghh,r_qqhh,kt,kl,CV,C2V  --firstPoint=%d --lastPoint=%d -n MultiDim_%s_%s_Job%d -L $CMSSW_BASE/lib/$SCRAM_ARCH/libHiggsAnalysisGBRLikelihood.so --X-rtd TMCSO_AdaptivePseudoAsimov=0 --X-rtd TMCSO_PseudoAsimov=0 --cminDefaultMinimizerStrategy 0 --cminFallbackAlgo Minuit2,Migrad,0:0.1 --X-rt MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 '%(os.getcwd(),card.replace('.txt','.root'),opts.pointsperjob*opts.jobs,kl_range,mask_str,i*opts.pointsperjob,(i+1)*opts.pointsperjob-1,channels,opts.outtag,i)
             else: 
                exec_line = 'combine %s/%s -M MultiDimFit -m 125.00 --algo grid --points %s -P kl --floatOtherPOIs 0 --setParameterRanges kl=%s --setParameters r=1%s --firstPoint=%d --lastPoint=%d -n MultiDim_%s_%s_Job%d -L $CMSSW_BASE/lib/$SCRAM_ARCH/libHiggsAnalysisGBRLikelihood.so %s --X-rtd TMCSO_AdaptivePseudoAsimov=0 --X-rtd TMCSO_PseudoAsimov=0 --cminDefaultMinimizerStrategy 0 --cminFallbackAlgo Minuit2,Migrad,0:0.1 --X-rt MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 '%(os.getcwd(),card.replace('.txt','.root'),opts.pointsperjob*opts.jobs,kl_range,mask_str,i*opts.pointsperjob,(i+1)*opts.pointsperjob-1,channels,opts.outtag,i,opts.freeze_kl_fit_params)
       else:
         if not opts.do2D : exec_line = 'combine %s/%s -M MultiDimFit -m 125.00 --algo grid --points %s -P kl --floatOtherPOIs 1 --setPhysicsModelParameterRanges kl=%s:r=-20,20  --firstPoint=%d --lastPoint=%d -n MultiDim_%s_%s_Job%d -L $CMSSW_BASE/lib/$SCRAM_ARCH/libHiggsAnalysisGBRLikelihood.so %s '%(os.getcwd(),card,opts.pointsperjob*opts.jobs,kl_range,i*opts.pointsperjob,(i+1)*opts.pointsperjob-1,channels,opts.outtag,i,opts.freeze_kl_fit_params)
         else : exec_line = 'combine %s/%s -M MultiDimFit -m 125.00 --algo grid --points %s -P kl  --floatOtherPOIs 1 --setParameterRanges kl=%s:r=-20,20  --firstPoint=%d --lastPoint=%d -n MultiDim_%s_%s_Job%d -L $CMSSW_BASE/lib/$SCRAM_ARCH/libHiggsAnalysisGBRLikelihood.so %s --X-rtd TMCSO_AdaptivePseudoAsimov=0 --X-rtd TMCSO_PseudoAsimov=0 --cminDefaultMinimizerStrategy 0 --cminFallbackAlgo Minuit2,Migrad,0:0.1 --X-rt MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 '%(os.getcwd(),card.replace('.txt','.root'),opts.pointsperjob*opts.jobs,kl_range,i*opts.pointsperjob,(i+1)*opts.pointsperjob-1,channels,opts.outtag,i,opts.freeze_kl_fit_params)
         if mask_str!='' : exec_line += ' --setParameters %s '%mask_str[1:]#remove the comma
       if opts.S0: exec_line += ' -S 0 '
       if opts.expected: 
           exec_line += ' -t -1 '
           if toysFile : exec_line += ' --toysFile %s'%toysFile
       writePostamble(file,exec_line,"MultiDim_%s_%s_Job%d"%(channels,opts.outtag,i))



def generateAsimovHHSM(card,channels="all",cats_map_mask={"MVA0":""}):
    print "[INFO] generating Asimov SM S+B for channels : %s"%channels
    exec_line = ""
    if '.txt' in card : exec_line = text2workspace(card,mask=True)
    mask_str = ""
    if channels!="all" and not "MVA" in channels :
       for cat in opts.cats.split(","):
         if channels != cat:
           mask_str += ",mask_%s_13TeV=1"%(cat)
    elif "MVA" in channels :
      for to_mask in set(cats_map_mask[channels])^set(opts.cats.split(",")): 
           mask_str += ",mask_%s_13TeV=1"%(to_mask)
    if not opts.do2D : exec_line += "combine %s/%s  -M GenerateOnly -m 125.00 -t -1 --saveToys -n SM_AsimovToy_%s_%s --setPhysicsModelParameters kl=1,r=1%s %s,kl"%(os.getcwd(),card,channels,opts.outtag,mask_str,opts.freeze_kl_fit_params)
    else : exec_line += "combine %s/%s  -M GenerateOnly -m 125.00 -t -1 --saveToys -n SM_AsimovToy_%s_%s --setParameters kl=1.0,r=1%s %s,kl  --X-rtd TMCSO_AdaptivePseudoAsimov=0 --X-rtd TMCSO_PseudoAsimov=0  --cminDefaultMinimizerStrategy 0 --cminFallbackAlgo Minuit2,Migrad,0:0.1 --X-rt MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2  "%(os.getcwd(),card.replace('.txt','.root'),channels,opts.outtag,mask_str,opts.freeze_kl_fit_params)
    system(exec_line)
    system('mv higgsCombineSM_AsimovToy_*%s*.root %s\n'%(opts.outtag,os.path.abspath(opts.outDir)))
    

def checkValidMethod():
  print "[INFO] checking valid methods"
  if opts.method not in allowedMethods: sys.exit('%s is not a valid method'%opts.method)


#######################################
cats_map = {}
cats_map['MVA0'] = 'DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3'.split(',')
cats_map['MVA1'] = 'DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7'.split(',')
cats_map['MVA2'] = 'DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11'.split(',')


checkValidMethod()
system('mkdir -p %s/Jobs/'%opts.outDir)
if opts.do_kl_scan:
  counter=0
  with open(opts.hhReweightDir+"config.json","r") as rew_json:
    rew_dict = json.load(rew_json)
  for ikl in range(0,rew_dict['Nkl']):
    kl = rew_dict['klmin'] + ikl*rew_dict['klstep']
    kl_str = ("{:.6f}".format(kl)).replace('.','d').replace('-','m') 
    for ikt in range(0,rew_dict['Nkt']):
      kt = rew_dict['ktmin'] + ikt*rew_dict['ktstep']
      kt_str = ("{:.6f}".format(kt)).replace('.','d').replace('-','m') 
      if opts.doNLOHH : hhcard_name = opts.datacard
      else : hhcard_name = opts.datacard.replace('.txt','_kl_%s_kt_%s.txt'%(kl_str,kt_str))
      outtag = '_kl_%s_kt_%s'%(kl_str,kt_str)+'_'+opts.outtag
      print "job ", counter , " , kl =  ", kl, " ,kt =  ", kt, '  outtag = ',outtag
      if not opts.do2D : 
         writeAsymptotic(counter,hhcard_name,outtag)
      else :
         writeAsymptoticFor2D(counter,hhcard_name,outtag,kl=kl)
      counter =  counter+1
if opts.do_benchmarks_scan:
  counter=0
  Nbenchmarks = opts.Nbench  #12 + SM + box
  for inode in range(0,Nbenchmarks):
      hhcard_name = opts.datacard.replace('.txt','_benchmark_%d.txt'%(inode))
      outtag = '_benchmarks_%d'%(inode)+'_'+opts.outtag
      print "job ", counter , " , benchmark =  ", inode
      if not opts.do2D : 
         writeAsymptotic(counter,hhcard_name,outtag)
      else :
         writeAsymptoticFor2D(counter,hhcard_name,outtag)
      counter =  counter+1
elif opts.do_kl_likelihood:
    toysFile = opts.toysFile
    kl_range = "-10,15"
    for ch in opts.channels_to_run.split(","):
       if ch!="all" : 
          if not opts.doNLOHH: 
             toysFile = opts.toysFile.replace("all",ch)
          kl_range = "-20,20"
       writeMultiDimFitLikelihood(opts.datacard,toysFile,ch,kl_range,cats_map)
elif opts.generateAsimovHHSM:
    for ch in opts.channels_to_run.split(","): 
      generateAsimovHHSM(opts.datacard,ch,cats_map)
    

