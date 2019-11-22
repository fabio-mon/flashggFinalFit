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
parser.add_option("--hhReweightDir",default='/work/nchernya/DiHiggs/inputs/25_10_2019/trees/kl_kt/',help="hh reweighting directory with all txt files" )
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
specOpts = OptionGroup(parser,"Specific options")
specOpts.add_option("--datacard",default=None)
specOpts.add_option("--files",default=None)
specOpts.add_option("--outDir",default=None)
specOpts.add_option("--justThisSyst",default=None)
specOpts.add_option("--method",default=None)
specOpts.add_option("--label",default=None)
specOpts.add_option("--expected",type="int",default=1)
specOpts.add_option("--mh",type="float",default=None)
specOpts.add_option("--expectSignal",type="float",default=None)
parser.add_option_group(specOpts)
(opts,args) = parser.parse_args()

allowedMethods = ['Asymptotic']

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
      sub_file.write('set -x\n')
  sub_file.write('touch %s.run\n'%os.path.abspath(sub_file.name))
  sub_file.write('cd %s\n'%os.getcwd())
  if (opts.batch == "T3CH"):
      sub_file.write('source $VO_CMS_SW_DIR/cmsset_default.sh\n')
      sub_file.write('source /mnt/t3nfs01/data01/swshare/glite/external/etc/profile.d/grid-env.sh\n')
      sub_file.write('export SCRAM_ARCH=slc6_amd64_gcc481\n')
      sub_file.write('export LD_LIBRARY_PATH=/swshare/glite/d-cache/dcap/lib/:$LD_LIBRARY_PATH\n')
      sub_file.write('set +x\n') 
  sub_file.write('eval `scramv1 runtime -sh`\n')
  if (opts.batch == "T3CH"):
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
    if (opts.batch == "T3CH") : 
          command = 'qsub -q %s -o %s.log -e %s.err %s > out.txt'%(opts.queue,os.path.abspath(sub_file.name),os.path.abspath(sub_file.name),os.path.abspath(sub_file.name))
          print command
          system(command)

def writeAsymptotic(jobid,card,outtag):
    print '[INFO] Writing Asymptotic'
    file = open('%s/sub_job%d.sh'%(opts.outDir,jobid),'w')
    writePreamble(file)
    exec_line = ''
    exec_line +=  'combine %s/%s -n %s -M Asymptotic -m 125.00 --cminDefaultMinimizerType=Minuit2 -L $CMSSW_BASE/lib/$SCRAM_ARCH/libHiggsAnalysisGBRLikelihood.so  --rRelAcc 0.001 '%(os.getcwd(),card,outtag)
    if opts.S0: exec_line += ' -s 0 '
    if opts.expected: exec_line += ' --run=blind -t -1'
    writePostamble(file,exec_line,outtag)


#######################################
system('mkdir -p %s/Jobs/'%opts.outDir)
counter=0
with open(opts.hhReweightDir+"config.json","r") as rew_json:
  rew_dict = json.load(rew_json)
for ikl in range(0,rew_dict['Nkl']):
  kl = rew_dict['klmin'] + ikl*(rew_dict['klmax']-rew_dict['klmin']+1)/rew_dict['Nkl']
  kl_str = ("{:.6f}".format(kl)).replace('.','d').replace('-','m') 
  for ikt in range(0,rew_dict['Nkt']):
    kt = rew_dict['ktmin'] + ikt*(rew_dict['ktmax']-rew_dict['ktmin']+1)/rew_dict['Nkt']
    kt_str = ("{:.6f}".format(kt)).replace('.','d').replace('-','m') 
    hhcard_name = opts.datacard.replace('.txt','_kl_%s_kt_%s.txt'%(kl_str,kt_str))
    outtag = '_kl_%s_kt_%s'%(kl_str,kt_str)
    print "job ", counter , " , kl =  ", kl, " ,kt =  ", kt, '  outtag = ',outtag
    writeAsymptotic(counter,hhcard_name,outtag)
    counter =  counter+1
