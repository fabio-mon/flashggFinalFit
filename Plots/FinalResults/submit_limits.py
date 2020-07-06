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
import subprocess


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
#parser.add_option("--cats",default="DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11", help = "categories")
parser.add_option("--cats",default="DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11,VBFDoubleHTag_0,VBFDoubleHTag_1", help = "categories")
parser.add_option("--channels_to_run",default="all", help = "which channels to run on")
#parser.add_option("--freeze_kl_fit_params",default = "--freezeNuisances param0_DoubleHTag_0,param1_DoubleHTag_0,param2_DoubleHTag_0,param0_DoubleHTag_1,param1_DoubleHTag_1,param2_DoubleHTag_1,param0_DoubleHTag_2,param1_DoubleHTag_2,param2_DoubleHTag_2,param0_DoubleHTag_3,param1_DoubleHTag_3,param2_DoubleHTag_3,param0_DoubleHTag_4,param1_DoubleHTag_4,param2_DoubleHTag_4,param0_DoubleHTag_5,param1_DoubleHTag_5,param2_DoubleHTag_5,param0_DoubleHTag_6,param1_DoubleHTag_6,param2_DoubleHTag_6,param0_DoubleHTag_7,param1_DoubleHTag_7,param2_DoubleHTag_7,param0_DoubleHTag_8,param1_DoubleHTag_8,param2_DoubleHTag_8,param0_DoubleHTag_9,param1_DoubleHTag_9,param2_DoubleHTag_9,param0_DoubleHTag_10,param1_DoubleHTag_10,param2_DoubleHTag_10,param0_DoubleHTag_11,param1_DoubleHTag_11,param2_DoubleHTag_11")
parser.add_option("--freeze_kl_fit_params",default = "--freezeParameters param0_DoubleHTag_0,param1_DoubleHTag_0,param2_DoubleHTag_0,param0_DoubleHTag_1,param1_DoubleHTag_1,param2_DoubleHTag_1,param0_DoubleHTag_2,param1_DoubleHTag_2,param2_DoubleHTag_2,param0_DoubleHTag_3,param1_DoubleHTag_3,param2_DoubleHTag_3,param0_DoubleHTag_4,param1_DoubleHTag_4,param2_DoubleHTag_4,param0_DoubleHTag_5,param1_DoubleHTag_5,param2_DoubleHTag_5,param0_DoubleHTag_6,param1_DoubleHTag_6,param2_DoubleHTag_6,param0_DoubleHTag_7,param1_DoubleHTag_7,param2_DoubleHTag_7,param0_DoubleHTag_8,param1_DoubleHTag_8,param2_DoubleHTag_8,param0_DoubleHTag_9,param1_DoubleHTag_9,param2_DoubleHTag_9,param0_DoubleHTag_10,param1_DoubleHTag_10,param2_DoubleHTag_10,param0_DoubleHTag_11,param1_DoubleHTag_11,param2_DoubleHTag_11")
parser.add_option("--klGridConfig",default='/work/nchernya/DiHiggs/CMSSW_7_4_7/src/flashggFinalFit/MetaData_HHbbgg/kl_grids/kl_grid_fine.json',help="grid for kl" )
parser.add_option("--c2vGridConfig",default='/work/nchernya/DiHiggs/CMSSW_7_4_7/src/flashggFinalFit/MetaData_HHbbgg/c2v_grids/c2v_grid_finish.json',help="grid for c2v scan" )
parser.add_option("--cvGridConfig",default='/work/nchernya/DiHiggs/CMSSW_7_4_7/src/flashggFinalFit/MetaData_HHbbgg/cv_grids/cv_grid_finish.json',help="grid for cv scan" )
parser.add_option("--addOption",type="string",default="",help="additional combine ooptions " )
parser.add_option("--do2D",type="int",default=0,help="do 2D or 1D " )
parser.add_option("--doNLOHH",type="int",default=0,help="do NLO HH model or not " )
parser.add_option("--whatToFloat",type="string",default="r",help="what to float : r, r_qqhh or r_gghh " )
parser.add_option("--Nbench",type="int",default=14,help="nunber of benchmarks" )
parser.add_option("--do_excl_scan",default=False,action="store_true",help="do exclusion scan?" )
parser.add_option("--do_limit",default=False,action="store_true",help="do U.L.?" )
parser.add_option("--coupling_param",type="string",default="kl",help="coupling parameter : kl,c2v,cv" )
parser.add_option("--do_benchmarks_scan",default=False,action="store_true",help="do benchmark scan?" )
parser.add_option("--do_likelihood",default=False,action="store_true",help="prepare datacard for likelihood" )
parser.add_option("--do_signal_fit",default=False,action="store_true",help="do simple fit" )
parser.add_option("--likelihood_float_mu",default=False,action="store_true",help="likelihood, float r" )
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
      #sub_file.write('#SBATCH --mem=4gb\n') #only for some very comp expensive jobs
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
 # if (opts.batch == "T3CH" ) : sub_file.write('cd $TMPDIR\n')
  if( opts.batch == "HTCONDOR" ):
    sub_file.write('cd -\n')
    sub_file.write('number=$RANDOM\n')
    sub_file.write('mkdir -p scratch_$number\n')
    sub_file.write('cd scratch_$number\n')


def writePostamble(sub_file, exec_line,outtag):

  #print "[INFO] writing to postamble"
  sub_file.write('if ( %s ) then\n'%exec_line)
  sub_file.write('\t mv higgsCombine%s.*root %s\n'%(outtag,os.path.abspath(opts.outDir)))
  sub_file.write('\t touch %s.done\n'%os.path.abspath(sub_file.name))
  sub_file.write('else\n')
  sub_file.write('\t touch %s.fail\n'%os.path.abspath(sub_file.name))
  sub_file.write('fi\n')
  sub_file.write('rm -f %s.run\n'%os.path.abspath(sub_file.name))
  sub_file.write('rm -rf scratch_$number\n')
  sub_file.close()
  system('chmod +x %s'%os.path.abspath(sub_file.name))
  if opts.runLocal:
     #system('bash %s > %s.log'%(os.path.abspath(sub_file.name),os.path.abspath(sub_file.name)))
     system('bash %s '%(os.path.abspath(sub_file.name)))
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
    if( opts.batch == "HTCONDOR" ):
      sub_file_name = re.sub("\.sh","",os.path.abspath(sub_file.name))
      HTCondorSubfile = open("%s.sub"%sub_file_name,'w')
      HTCondorSubfile.write('+JobFlavour = "%s"\n'%(opts.queue))
      HTCondorSubfile.write('\n')
      HTCondorSubfile.write('executable  = %s.sh\n'%sub_file_name)
      HTCondorSubfile.write('output  = %s.out\n'%sub_file_name)
      HTCondorSubfile.write('error  = %s.err\n'%sub_file_name)
      HTCondorSubfile.write('log  = %s.log\n'%sub_file_name)
      HTCondorSubfile.write('\n')
      HTCondorSubfile.write('max_retries = 1\n')
      HTCondorSubfile.write('queue 1\n')
      subprocess.Popen("condor_submit "+HTCondorSubfile.name,
                             shell=True, # bufsize=bufsize,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             close_fds=True)



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


def writeAsymptoticFor2D(jobid,card,coupling_dict={},channels="all",cats_map_mask={"MVA0":""}):
    kl=coupling_dict["kl"]
    kt=coupling_dict["kt"]
    c2v=coupling_dict["c2v"]
    cv=coupling_dict["cv"]
    print '[INFO] MultiDim Fit for 2D'
    file = open('%s/Jobs/sub_%s_%s_job_%d.sh'%(opts.outDir,channels,opts.whatToFloat,jobid),'w')
    writePreamble(file)
    mask_str = ""
    if channels!="all" and "DoubleHTag" in channels :
       for cat in opts.cats.split(","):
         if channels != cat:
           mask_str += ",mask_%s_13TeV=1"%(cat)
    elif not "DoubleHTag" in channels :
      for to_mask in set(cats_map_mask[channels])^set(opts.cats.split(",")): 
           mask_str += ",mask_%s_13TeV=1"%(to_mask)
    if opts.doNLOHH: 
       model = ' -P HHModel:HHdefault'
       exec_line = text2workspace(card,model=model)
       fix_signal_stregths = ''
       set_signal_stregths = ''
       for mu in 'r,r_gghh,r_qqhh'.split(','):
          if mu!=opts.whatToFloat:
             set_signal_stregths += "%s=1,"%mu 
             fix_signal_stregths += "%s,"%mu
       if set_signal_stregths!='' : set_signal_stregths = set_signal_stregths[0:len(set_signal_stregths)-1]#remove the comma
       if fix_signal_stregths!='' : fix_signal_stregths = fix_signal_stregths[0:len(fix_signal_stregths)-1]#remove the comma
 
       model_line =" --redefineSignalPOIs %s --freezeParameters %s,kt,kl,CV,C2V --setParameters %s,kt=%.3f,kl=%.3f,CV=%.3f,C2V=%.3f%s"%(opts.whatToFloat,fix_signal_stregths,set_signal_stregths,kt,kl,cv,c2v,mask_str)  
       exec_line += "combine %s/%s  -n %s_%s_%s  -M AsymptoticLimits -m 125. --saveWorkspace %s --X-rtd TMCSO_AdaptivePseudoAsimov=0 --X-rtd TMCSO_PseudoAsimov=0 --cminDefaultMinimizerStrategy 0 --cminFallbackAlgo Minuit2,Migrad,0:0.1 --X-rt MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 "%(os.getcwd(),card.replace(".txt",".root"),opts.outtag,opts.whatToFloat,channels,model_line)
       if opts.S0: exec_line += ' -S 0 '
       if opts.expected: exec_line += ' --run=blind -t -1'
    else: 
       exec_line = text2workspace(card)
       if opts.expected: 
          exec_line += "combine %s/%s  -n %s  -M MultiDimFit -m 125. --saveWorkspace --X-rtd TMCSO_AdaptivePseudoAsimov=0 --X-rtd TMCSO_PseudoAsimov=0 --cminDefaultMinimizerStrategy 0 --cminFallbackAlgo Minuit2,Migrad,0:0.1 --X-rt MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2"%(os.getcwd(),card.replace(".txt",".root"),opts.outtag)
          if opts.expected: exec_line += ' -t -1' 
          exec_line += '\n' 
          exec_line += "combine higgsCombine%s.MultiDimFit.mH125.root --snapshotName MultiDimFit -n %s  -M AsymptoticLimits -m 125. --saveWorkspace --X-rtd TMCSO_AdaptivePseudoAsimov=0 --X-rtd TMCSO_PseudoAsimov=0 --cminDefaultMinimizerStrategy 0 --cminFallbackAlgo Minuit2,Migrad,0:0.1 --X-rt MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2"%(opts.outtag,opts.outtag)
          if opts.S0: exec_line += ' -S 0 '
          if opts.expected: exec_line += ' --run=blind -t -1'
       else: 
          exec_line += "combine %s/%s  -n %s  -M AsymptoticLimits -m 125.  --X-rtd TMCSO_AdaptivePseudoAsimov=0 --X-rtd TMCSO_PseudoAsimov=0 --cminDefaultMinimizerStrategy 0 --cminFallbackAlgo Minuit2,Migrad,0:0.1 --X-rt MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2"%(os.getcwd(),card.replace(".txt",".root"),opts.outtag)


    writePostamble(file,exec_line,"%s_%s_%s"%(opts.outtag,opts.whatToFloat,channels))



def writeMultiDimFitLikelihood(card,toysFile,channels="all",param_range="kl=-10,15",cats_map_mask={"MVA0":""}):
    print "[INFO] writing multidim fit"
    param = opts.coupling_param
    if 'c2v' in param or 'cv' in param : param=param.upper()
    mask_str = ""
    if channels!="all" and "DoubleHTag" in channels :
       for cat in opts.cats.split(","):
         if channels != cat:
           mask_str += ",mask_%s_13TeV=1"%(cat)
    elif not "DoubleHTag" in channels :
      for to_mask in set(cats_map_mask[channels])^set(opts.cats.split(",")): 
           mask_str += ",mask_%s_13TeV=1"%(to_mask)
    for i in range(opts.jobs):
       file = open('%s/Jobs/sub_%s_job_%s_%d.sh'%(opts.outDir,channels,param,i),'w')
       writePreamble(file)
       set_parameters = ''
       for p in 'kt,kl,CV,C2V,r,r_qqhh,r_gghh'.split(','):
          if not p in param.split(','):
             set_parameters += "%s=1,"%p
       if set_parameters!='' : set_parameters = set_parameters[0:len(set_parameters)-1]#remove the comma

       if not opts.likelihood_float_mu: #to run with r=1
          if not opts.do2D : exec_line = 'combine %s/%s -M MultiDimFit -m 125.00 --algo grid --points %s -P %s --floatOtherPOIs 0 --setPhysicsModelParameterRanges %s --setPhysicsModelParameters r=1%s --firstPoint=%d --lastPoint=%d -n MultiDim_%s_%s_Job%d -L $CMSSW_BASE/lib/$SCRAM_ARCH/libHiggsAnalysisGBRLikelihood.so %s '%(os.getcwd(),card,opts.pointsperjob*opts.jobs,param,param_range,mask_str,i*opts.pointsperjob,(i+1)*opts.pointsperjob-1,channels,opts.outtag,i,opts.freeze_kl_fit_params)
          else : 
             if opts.doNLOHH: 
                exec_line = 'combine %s/%s -M MultiDimFit -m 125.00 --algo grid --points %s  --redefineSignalPOIs %s  --setParameterRanges %s --setParameters %s%s --freezeParameters r,r_gghh,r_qqhh,kt,kl,CV,C2V  --firstPoint=%d --lastPoint=%d -n MultiDim_%s_%s_Job%d -L $CMSSW_BASE/lib/$SCRAM_ARCH/libHiggsAnalysisGBRLikelihood.so --X-rtd TMCSO_AdaptivePseudoAsimov=0 --X-rtd TMCSO_PseudoAsimov=0 --cminDefaultMinimizerStrategy 0 --cminFallbackAlgo Minuit2,Migrad,0:0.1 --X-rt MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 '%(os.getcwd(),card.replace('.txt','.root'),opts.pointsperjob*opts.jobs,param,param_range,set_parameters,mask_str,i*opts.pointsperjob,(i+1)*opts.pointsperjob-1,channels,opts.outtag,i)
             else: 
                exec_line = 'combine %s/%s -M MultiDimFit -m 125.00 --algo grid --points %s -P %s --floatOtherPOIs 0 --setParameterRanges %s --setParameters r=1%s --firstPoint=%d --lastPoint=%d -n MultiDim_%s_%s_Job%d -L $CMSSW_BASE/lib/$SCRAM_ARCH/libHiggsAnalysisGBRLikelihood.so %s --X-rtd TMCSO_AdaptivePseudoAsimov=0 --X-rtd TMCSO_PseudoAsimov=0 --cminDefaultMinimizerStrategy 0 --cminFallbackAlgo Minuit2,Migrad,0:0.1 --X-rt MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 '%(os.getcwd(),card.replace('.txt','.root'),opts.pointsperjob*opts.jobs,param,param_range,mask_str,i*opts.pointsperjob,(i+1)*opts.pointsperjob-1,channels,opts.outtag,i,opts.freeze_kl_fit_params)
       else:
         if not opts.do2D : exec_line = 'combine %s/%s -M MultiDimFit -m 125.00 --algo grid --points %s -P %s --floatOtherPOIs 1 --setPhysicsModelParameterRanges %s:r=-20,20  --firstPoint=%d --lastPoint=%d -n MultiDim_%s_%s_Job%d -L $CMSSW_BASE/lib/$SCRAM_ARCH/libHiggsAnalysisGBRLikelihood.so %s '%(os.getcwd(),card,opts.pointsperjob*opts.jobs,param,param_range,i*opts.pointsperjob,(i+1)*opts.pointsperjob-1,channels,opts.outtag,i,opts.freeze_kl_fit_params)
         else : exec_line = 'combine %s/%s -M MultiDimFit -m 125.00 --algo grid --points %s -P %s  --floatOtherPOIs 1 --setParameterRanges %s:r=-20,20  --firstPoint=%d --lastPoint=%d -n MultiDim_%s_%s_Job%d -L $CMSSW_BASE/lib/$SCRAM_ARCH/libHiggsAnalysisGBRLikelihood.so %s --X-rtd TMCSO_AdaptivePseudoAsimov=0 --X-rtd TMCSO_PseudoAsimov=0 --cminDefaultMinimizerStrategy 0 --cminFallbackAlgo Minuit2,Migrad,0:0.1 --X-rt MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 '%(os.getcwd(),card.replace('.txt','.root'),opts.pointsperjob*opts.jobs,param,param_range,i*opts.pointsperjob,(i+1)*opts.pointsperjob-1,channels,opts.outtag,i,opts.freeze_kl_fit_params)
         if mask_str!='' : exec_line += ' --setParameters %s '%mask_str[1:]#remove the comma
       if opts.S0: exec_line += ' -S 0 '
       if opts.expected: 
           exec_line += ' -t -1 '
           if toysFile : exec_line += ' --toysFile %s'%toysFile
       writePostamble(file,exec_line,"MultiDim_%s_%s_Job%d"%(channels,opts.outtag,i))


def writeMultiDimFit(card,channels="all",cats_map_mask={"MVA0":""}):
    print "[INFO] writing multidim fit"
    file = open('%s/Jobs/sub_job.sh'%(opts.outDir),'w')
    writePreamble(file)
    mask_str = ""
    if channels!="all" and "DoubleHTag" in channels :
       for cat in opts.cats.split(","):
         if channels != cat:
           mask_str += ",mask_%s_13TeV=1"%(cat)
    elif not "DoubleHTag" in channels :
      for to_mask in set(cats_map_mask[channels])^set(opts.cats.split(",")): 
           mask_str += ",mask_%s_13TeV=1"%(to_mask)
    if opts.doNLOHH: 
       model = ' -P HHModel:HHdefault'
       exec_line = text2workspace(card,model=model)
       fix_signal_stregths = ''
       set_signal_stregths = ''
       bounds = '--autoBoundsPOIs %s --autoMaxPOIs %s'%(opts.whatToFloat,opts.whatToFloat) 
       for mu in 'r,r_gghh,r_qqhh'.split(','):
          if not mu in opts.whatToFloat.split(','):
             set_signal_stregths += "%s=1,"%mu 
             fix_signal_stregths += "%s,"%mu
       if set_signal_stregths!='' : set_signal_stregths = set_signal_stregths[0:len(set_signal_stregths)-1]#remove the comma
       if fix_signal_stregths!='' : fix_signal_stregths = fix_signal_stregths[0:len(fix_signal_stregths)-1]#remove the comma
 
       model_line =" --redefineSignalPOIs %s  %s  --freezeParameters %s,kt,kl,CV,C2V --setParameters %s,kt=1,kl=1,CV=1,C2V=1"%(opts.whatToFloat,bounds,fix_signal_stregths,set_signal_stregths)  
 
       exec_line = 'combine %s/%s -M MultiDimFit -m 125.00 --algo singles  %s%s  -n MultiDim_floating_%s_%s_%s -L $CMSSW_BASE/lib/$SCRAM_ARCH/libHiggsAnalysisGBRLikelihood.so --X-rtd TMCSO_AdaptivePseudoAsimov=0 --X-rtd TMCSO_PseudoAsimov=0 --cminDefaultMinimizerStrategy 0 --cminFallbackAlgo Minuit2,Migrad,0:0.1 --X-rt MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 %s '%(os.getcwd(),card.replace('.txt','.root'),model_line,mask_str,opts.whatToFloat.replace(',','_'),channels,opts.outtag,opts.addOption)
       if opts.S0: exec_line += ' -S 0 '
       if opts.expected: 
           exec_line += ' -t -1 '
       writePostamble(file,exec_line,"MultiDim_floating_%s_%s_%s"%(opts.whatToFloat.replace(',','_'),channels,opts.outtag))






def generateAsimovHHSM(card,channels="all",cats_map_mask={"MVA0":""}):
    print "[INFO] generating Asimov SM S+B for channels : %s"%channels
    exec_line = ""
    if '.txt' in card : exec_line = text2workspace(card,mask=True)
    mask_str = ""
    if channels!="all" and "DoubleH" in channels :
       for cat in opts.cats.split(","):
         if channels != cat:
           mask_str += ",mask_%s_13TeV=1"%(cat)
    elif not "DoubleH" in channels :
      for to_mask in set(cats_map_mask[channels])^set(opts.cats.split(",")): 
           mask_str += ",mask_%s_13TeV=1"%(to_mask)
    if not opts.do2D : exec_line += "combine %s/%s  -M GenerateOnly -m 125.00 -t -1 --saveToys -n SM_AsimovToy_%s_%s --setPhysicsModelParameters kl=1,r=1%s %s,kl"%(os.getcwd(),card,channels,opts.outtag,mask_str,opts.freeze_kl_fit_params)
    else : exec_line += "combine %s/%s  -M GenerateOnly -m 125.00 -t -1 --saveToys -n SM_AsimovToy_%s_%s --setParameters kl=1.0,r=1%s %s,kl  --X-rtd TMCSO_AdaptivePseudoAsimov=0 --X-rtd TMCSO_PseudoAsimov=0  --cminDefaultMinimizerStrategy 0 --cminFallbackAlgo Minuit2,Migrad,0:0.1 --X-rt MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2  "%(os.getcwd(),card.replace('.txt','.root'),channels,opts.outtag,mask_str,opts.freeze_kl_fit_params)
    system(exec_line)
    system('mv higgsCombineSM_AsimovToy_*%s.*root %s\n'%(opts.outtag,os.path.abspath(opts.outDir)))
    

def checkValidMethod():
  print "[INFO] checking valid methods"
  if opts.method not in allowedMethods: sys.exit('%s is not a valid method'%opts.method)


#######################################
cats_map = {}
cats_map['MVA0'] = 'DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3'.split(',')
cats_map['MVA1'] = 'DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7'.split(',')
cats_map['MVA2'] = 'DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11'.split(',')
cats_map['ggF'] = 'DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11'.split(',')
cats_map['VBF'] = 'VBFDoubleHTag_0,VBFDoubleHTag_1'.split(',')
cats_map['all'] = 'DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11,VBFDoubleHTag_0,VBFDoubleHTag_1'.split(',')

coupling_dict = {}
coupling_dict["kl"] = 1.
coupling_dict["kt"] = 1.
coupling_dict["c2v"] = 1.
coupling_dict["cv"] = 1.


checkValidMethod()
system('mkdir -p %s/Jobs/'%opts.outDir)

param = opts.coupling_param
parameter_file = ''
if 'kl' in param : parameter_file = opts.klGridConfig
if 'c2v' in param : parameter_file = opts.c2vGridConfig
if 'cv' in param : parameter_file = opts.cvGridConfig
if opts.do_excl_scan:  
  with open(parameter_file,"r") as rew_json:
    rew_dict = json.load(rew_json)
  counter=0
  couplmin=rew_dict['%smin'%param]
  couplmax=rew_dict['%smax'%param]
  Ncoupl=rew_dict['N%s'%param]
  couplstep=rew_dict['%sstep'%param]
  for icoupl in range(0,Ncoupl):
    coupl = couplmin + icoupl*couplstep
    coupl_str = ("{:.6f}".format(coupl)).replace('.','d').replace('-','m') 
    if opts.doNLOHH : hhcard_name = opts.datacard
    else : hhcard_name = opts.datacard.replace('.txt','_kl_%s_kt_1d000000.txt'%(kl_str)) #for LO ntuples, old
    outtag = '_%s_%s'%(param,coupl_str)+'_'+opts.outtag
    print "job ", counter , " , %s =  "%param, coupl, '  outtag = ',outtag
    coupling_dict['%s'%param]=coupl
    if not opts.do2D : 
       writeAsymptotic(counter,hhcard_name)
    else :
       for ch in opts.channels_to_run.split(","):
         writeAsymptoticFor2D(counter,hhcard_name,coupling_dict,ch,cats_map)
    counter =  counter+1
if opts.do_limit:  
    if opts.doNLOHH : hhcard_name = opts.datacard
    if opts.do2D : 
       for ch in opts.channels_to_run.split(","):
         writeAsymptoticFor2D(1,hhcard_name,coupling_dict,ch,cats_map)
if opts.do_benchmarks_scan:
  counter=0
  Nbenchmarks = opts.Nbench  #12 + SM + box
  for inode in range(0,Nbenchmarks):
      hhcard_name = opts.datacard.replace('.txt','_benchmark_%d.txt'%(inode))
      outtag = '_benchmarks_%d'%(inode)+'_'+opts.outtag
      print "job ", counter , " , benchmark =  ", inode
      if not opts.do2D : 
         writeAsymptotic(counter,hhcard_name)
      else :
        for ch in opts.channels_to_run.split(","):
           writeAsymptoticFor2D(counter,hhcard_name,coupling_dict,ch,cats_map)
      counter =  counter+1
elif opts.do_likelihood:
    toysFile = opts.toysFile
    if param=='kl' : param_range = "kl=-10,15"
    if param=='c2v' : param_range = "C2V=-4,6"
    if param=='cv' : param_range = "CV=-3,3"
    if param=='cv,c2v' : param_range = "CV=-2,2:C2V=-3,3"
    if param=='r_gghh,r_qqhh' : param_range = "r_gghh=-20,20:r_qqhh=-300,300"
    if param=='r_qqhh' : param_range = "r_qqhh=-200,200"
    for ch in opts.channels_to_run.split(","):
       if ch!="all" : 
          if not opts.doNLOHH: 
             toysFile = opts.toysFile.replace("all",ch)
          if param=='kl' : param_range = "kl=-20,20"
          if param=='kl' and 'VBF' in ch: param_range = "kl=-40,40"
          if param=='c2v' : param_range = "C2V=-8,8"
          if param=='cv' : param_range = "CV=-6,6"
          if param=='r_gghh,r_qqhh' : param_range = "r_gghh=-20,20:r_qqhh=-300,300"
          if param=='r_qqhh' : param_range = "r_qqhh=-200,200"
       writeMultiDimFitLikelihood(opts.datacard,toysFile,ch,param_range,cats_map)
elif opts.generateAsimovHHSM:
    for ch in opts.channels_to_run.split(","): 
      generateAsimovHHSM(opts.datacard,ch,cats_map)
elif opts.do_signal_fit:
    for ch in opts.channels_to_run.split(","):
       writeMultiDimFit(opts.datacard,ch,cats_map)
    

    

