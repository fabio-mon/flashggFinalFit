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
parser.add_option("--cats",default="DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11", help = "categories")
parser.add_option("--channels_to_run",default="all", help = "which channels to run on")
parser.add_option("--freeze_kl_fit_params",default=True,action="store_true",help="freeze klambda fit parameters")
parser.add_option("--hhReweightDir",default='/work/nchernya/DiHiggs/inputs/25_10_2019/trees/kl_kt_finebinning/',help="hh reweighting directory with all txt files" )
parser.add_option("--do_kl_scan",default=False,action="store_true",help="do kl scan?" )
parser.add_option("--do_kl_likelihood",default=False,action="store_true",help="prepare datacard for kl likelihood" )
parser.add_option("--generateAsimovHHSM",default=False,action="store_true",help="generate SM S+B HH Asimov" )
parser.add_option("-q","--queue",default='short.q',help="Which batch queue")
parser.add_option("--dryRun",default=False,action="store_true",help="Dont submit")
parser.add_option("--parallel",default=False,action="store_true",help="Run local fits in multithreading")
parser.add_option("--runLocal",default=False,action="store_true",help="Run locally")
parser.add_option("--hadd",help="Trawl passed directory and hadd files. To be used when jobs are complete.")
parser.add_option("--resubmitFailures",help=" Provide directory and the script will find failed jobs and resubmit them")
parser.add_option("-v","--verbose",default=False,action="store_true")
parser.add_option("--poix",default="r")
parser.add_option("--S0",default=False,action="store_true",help="Stats only")
parser.add_option("--batch",default="T3CH",help="Which batch system to use (LSF,IC)")
parser.add_option("--prefix",default="./")
parser.add_option("--freezeAll",default=False,action="store_true",help="Freeze all nuisances")
parser.add_option("--float",default="",action="store",help="Freeze all nuisances")
parser.add_option("--postFitAll",default=False,action="store_true",help="Use post-fit nuisances for all methods")
parser.add_option("--hhReweightSM",default='',help="hh base SM card" )
parser.add_option("--Nkl",type="int",default=1,help="Number of kl points")
parser.add_option("--klmin",type="float",default=1.,help="kl min")
parser.add_option("--klmax",type="float",default=1.,help="kl max")
parser.add_option("--Nkt",type="int",default=1,help="Number of kt points")
parser.add_option("--ktmin",type="float",default=1.,help="kt min")
parser.add_option("--ktmax",type="float",default=1.,help="kt max")

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

freezing_option_str = ""
if opts.freeze_kl_fit_params:
    freezing_option_str = "--freezeNuisances "
    for c in opts.cats.split(","):
        for ipar in range(0,3):
            freezing_option_str += "param%i_%s,"%(ipar,c)
    freezing_option_str = freezing_option_str.rstrip(',')

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
  sub_file.write('touch %s.run\n'%os.path.abspath(sub_file.name))
  sub_file.write('cd %s\n'%os.getcwd())
  sub_file.write('eval `scramv1 runtime -sh`\n')
  sub_file.write('cd -\n')

def writePostamble(sub_file, exec_line,outtag):
  #print "[INFO] writing to postamble"
  sub_file.write('if ( %s ) then\n'%exec_line)
  sub_file.write('\t mv higgsCombine%s*.root %s\n'%(outtag,os.path.abspath(opts.outDir)))
  sub_file.write('\t touch %s.done\n'%os.path.abspath(sub_file.name))
  sub_file.write('else\n')
  sub_file.write('\t touch %s.fail\n'%os.path.abspath(sub_file.name))
  sub_file.write('fi\n')
  sub_file.write('rm -f %s.run\n'%os.path.abspath(sub_file.name))

  sub_file.close()
  system('chmod +x %s'%os.path.abspath(sub_file.name))
  if opts.runLocal:
      print 'bash %s > %s.log'%(os.path.abspath(sub_file.name),os.path.abspath(sub_file.name))
      if not opts.dryRun:
          system('bash %s > %s.log'%(os.path.abspath(sub_file.name),os.path.abspath(sub_file.name)))
  elif opts.queue:
    system('rm -f %s.done'%os.path.abspath(sub_file.name))
    system('rm -f %s.fail'%os.path.abspath(sub_file.name))
    system('rm -f %s.log'%os.path.abspath(sub_file.name))
    system('rm -f %s.err'%os.path.abspath(sub_file.name))

def writeAsymptotic(jobid,card,outtag):
    print '[INFO] Writing Asymptotic'
    file = open('%s/jobs/sub_job%d.sh'%(opts.outDir,jobid),'w')
    writePreamble(file)
    exec_line =  'combine %s -n %s -M Asymptotic -m 125.00 --cminDefaultMinimizerType=Minuit2 -L $CMSSW_BASE/lib/$SCRAM_ARCH/libHiggsAnalysisGBRLikelihood.so  --rRelAcc 0.001 '%(card,outtag)
    if opts.S0: exec_line += ' -s 0 '
    if opts.expected: exec_line += ' --run=blind -t -1'
    writePostamble(file,exec_line,outtag)
    file.close()


def writeMultiDimFitLikelihood(card,toysFile,channels="all",kl_range="-10,15",freezing_option_str=""):
    print "[INFO] writing multidim fit"
    mask_str = ""
    if channels!="all" :
       for cat in opts.cats.split(","):
         if channels != cat:
           mask_str += ",mask_%s_13TeV=1"%(cat)
    for i in range(opts.jobs):
       file = open('%s/jobs/sub_%s_job_kl_%d.sh'%(opts.outDir,channels,i),'w')
       writePreamble(file)
       exec_line = 'combine %s -M MultiDimFit -m 125.00 --algo grid --points %s -P kl --floatOtherPOIs 0 --setPhysicsModelParameterRanges kl=%s --setPhysicsModelParameters r=1%s --firstPoint=%d --lastPoint=%d -n MultiDim_%s_%s_Job%d -L $CMSSW_BASE/lib/$SCRAM_ARCH/libHiggsAnalysisGBRLikelihood.so %s '%(card,opts.pointsperjob*opts.jobs,kl_range,mask_str,i*opts.pointsperjob,(i+1)*opts.pointsperjob-1,channels,opts.outtag,i,freezing_option_str)
       if opts.S0: exec_line += ' -s 0 '
       if opts.expected: exec_line += ' -t -1 --toysFile %s'%toysFile
       writePostamble(file,exec_line,"MultiDim_%s_%s_Job%d"%(channels,opts.outtag,i))



def generateAsimovHHSM(card,channels="all",freezing_option_str=""):
    print "[INFO] generating Asimov SM S+B for channels : %s"%channels
    mask_str = ""
    if channels!="all" :
       for cat in opts.cats.split(","):
         if channels != cat:
           mask_str += ",mask_%s_13TeV=1"%(cat)
    if(freezing_option_str!=""):
        freezing_option_str += ",kl"
    else:
        freezing_option_str = "--freezeNuisances  kl"
    exec_line = "combine %s  -m 125.00  -M GenerateOnly -t -1 --saveToys -n SM_AsimovToy_%s_%s --setPhysicsModelParameters kl=1,r=1%s %s"%(card,channels,opts.outtag,mask_str,freezing_option_str)
    print "EXECUTING "+exec_line
    system(exec_line)
    system('mv higgsCombineSM_AsimovToy_*%s*.root %s\n'%(opts.outtag,os.path.abspath(opts.outDir)))
    

def checkValidMethod():
  print "[INFO] checking valid methods"
  if opts.method not in allowedMethods: sys.exit('%s is not a valid method'%opts.method)


#######################################
checkValidMethod()
system('mkdir -p %s/jobs/'%opts.outDir)
if opts.do_kl_scan:
    counter=0
    Nkl = opts.Nkl
    klmin = opts.klmin
    klmax = opts.klmax
    Nkt = opts.Nkt
    ktmin = opts.ktmin
    ktmax = opts.ktmax
    for ikl in range(0,Nkl):
        kl = klmin + (ikl+0.5)*(klmax-klmin)/Nkl;
        for ikt in range(0,Nkt):
            kt = ktmin + (ikt+0.5)*(ktmax-ktmin)/Nkt;
            hhcard_name = opts.hhReweightSM.replace('.txt','_kl_%.3f_kt_%.3f.txt'%(kl,kt))
            outtag = '_kl_%.3f_kt_%.3f'%(kl,kt)
            print "job ", counter , " , kl =  ", kl, " ,kt =  ", kt, '  outtag = ',outtag
            writeAsymptotic(counter,hhcard_name,outtag)
            counter =  counter+1

    #write sub file
    print("writing .sub file")
    condorsubname = os.path.abspath('%s/jobs/sub_jobs.sub'%opts.outDir)
    condorsub = open(condorsubname,'w')
    #condorsub.write('requirements = (OpSysAndVer =?= "SLCern6")\n')
    condorsub.write("executable            = $(scriptname)\n")
    condorsub.write("output                = $(scriptname).out\n")
    condorsub.write("error                 = $(scriptname).err\n")
    condorsub.write("log                   = $(scriptname).log\n")
    condorsub.write('+JobFlavour           = "'+opts.queue+'"\n')
    condorsub.write("queue scriptname matching %s/jobs/sub*.sh"%opts.outDir)
    condorsub.close()
    print("condor_submit "+condorsubname)
    if not opts.dryRun:    
        os.system("condor_submit "+condorsubname)

elif opts.do_kl_likelihood:
    toysFile = opts.toysFile
    kl_range = "-10,15"
    for ch in opts.channels_to_run.split(","):
       if ch!="all" : 
          toysFile = opts.toysFile.replace("all",ch)
          kl_range = "-20,20"
       writeMultiDimFitLikelihood(opts.datacard,toysFile,ch,kl_range,freezing_option_str)

    #write sub file
    print("writing .sub file")
    condorsubname = os.path.abspath('%s/jobs/sub_jobs.sub'%opts.outDir)
    condorsub = open(condorsubname,'w')
    #condorsub.write('requirements = (OpSysAndVer =?= "SLCern6")\n')
    condorsub.write("executable            = $(scriptname)\n")
    condorsub.write("output                = $(scriptname).out\n")
    condorsub.write("error                 = $(scriptname).err\n")
    condorsub.write("log                   = $(scriptname).log\n")
    condorsub.write('+JobFlavour           = "'+opts.queue+'"\n')
    condorsub.write("queue scriptname matching %s/jobs/sub*.sh"%opts.outDir)
    condorsub.close()
    print("condor_submit "+condorsubname)
    if not opts.dryRun:    
        os.system("condor_submit "+condorsubname)

elif opts.generateAsimovHHSM:
    for ch in opts.channels_to_run.split(","): 
      generateAsimovHHSM(opts.datacard,ch,freezing_option_str)
    
