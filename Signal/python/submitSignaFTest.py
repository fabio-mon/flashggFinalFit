#!/usr/bin/env python

import os
import numpy
import sys
import fnmatch
from copy import deepcopy as copy
import re

from optparse import OptionParser
from optparse import OptionGroup

parser = OptionParser()
parser.add_option("-i","--infile",help="Signal Workspace")
parser.add_option("-q","--queue",help="Which batch queue")
parser.add_option("--runLocal",default=False,action="store_true",help="Run locally")
parser.add_option("--batch",default="LSF",help="Which batch system to use (LSF,IC)")
parser.add_option("--outDir",default=None)
parser.add_option("--procs",default=None)
parser.add_option("--flashggCats",default=None)
parser.add_option("--expected",type="int",default=None)
parser.add_option("--indir",default="",help="infile directory ")
(opts,args) = parser.parse_args()

defaults = copy(opts)
print "INFO - queue ", opts.queue
def system(exec_line):
  #print "[INFO] defining exec_line"
  #if opts.verbose: print '\t', exec_line
  os.system(exec_line)


#def strtodict(lstr):
#  print "[INFO] string to dictionariy"
#  retdict = {}
#  if not len(lstr): return retdict
#  objects = lstr.split(':')
#  for o in objects:
#    k,vs = o.split('[')
#    vs = vs.rstrip(']')
#    vs = vs.split(',')
#    retdict[k] = [float(vs[0]),float(vs[1])]
#  return retdict
#
#catRanges = strtodict(opts.catRanges)

#def writePreamble(sub_file):
#  #print "[INFO] writing preamble"
#  sub_file.write('#!/bin/bash\n')
#  sub_file.write('touch %s.run\n'%os.path.abspath(sub_file.name))
#  sub_file.write('cd %s\n'%os.getcwd())
#  sub_file.write('eval `scramv1 runtime -sh`\n')
#  sub_file.write('cd -\n')
#  sub_file.write('number=$RANDOM\n')
#  sub_file.write('mkdir -p scratch_$number\n')
#  sub_file.write('cd scratch_$number\n')

def writePreamble(sub_file):
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
  sub_file.write('cd -\n')
  if (opts.batch == "T3CH" ) : sub_file.write('cd $TMPDIR\n')
  sub_file.write('number=$RANDOM\n')
  sub_file.write('mkdir -p scratch_$number\n')
  sub_file.write('cd scratch_$number\n')


def writePostamble(sub_file, exec_line):

  #print "[INFO] writing to postamble"
  sub_file.write('if ( %s ) then\n'%exec_line)
  #sub_file.write('\t mv higgsCombine*.root %s\n'%os.path.abspath(opts.outDir))
  sub_file.write('\t touch %s.done\n'%os.path.abspath(sub_file.name))
  sub_file.write('else\n')
  sub_file.write('\t touch %s.fail\n'%os.path.abspath(sub_file.name))
  sub_file.write('fi\n')
  sub_file.write('rm -f %s.run\n'%os.path.abspath(sub_file.name))
  sub_file.write('rm -rf scratch_$number\n')
  sub_file.close()
  system('chmod +x %s'%os.path.abspath(sub_file.name))
  print 'does script exist?'
  os.system("ls %s"%os.path.abspath(sub_file.name))
  if opts.runLocal:
     system('bash %s > %s.log'%(os.path.abspath(sub_file.name),os.path.abspath(sub_file.name)))
  elif opts.queue:
    system('rm -f %s.done'%os.path.abspath(sub_file.name))
    system('rm -f %s.fail'%os.path.abspath(sub_file.name))
    system('rm -f %s.log'%os.path.abspath(sub_file.name))
    system('rm -f %s.err'%os.path.abspath(sub_file.name))
    condorsub = open(os.path.abspath(sub_file.name)+".sub",'w')
    condorsub.write('requirements = (OpSysAndVer =?= "SLCern6")\n')
    condorsub.write("executable            = "+os.path.abspath(sub_file.name)+"\n")
    condorsub.write("output                = "+os.path.abspath(sub_file.name)+".out\n")
    condorsub.write("error                 = "+os.path.abspath(sub_file.name)+".err\n")
    condorsub.write("log                   = "+os.path.abspath(sub_file.name)+".log\n")
    condorsub.write('+JobFlavour           = "'+opts.queue+'"\n')
    condorsub.write("queue 1\n")
    condorsub.close()


    if (opts.batch == "LSF") : system("condor_submit "+os.path.abspath(sub_file.name)+".sub")
    if (opts.batch == "IC") : system('qsub -q %s -o %s.log -e %s.err %s > out.txt'%(opts.queue,os.path.abspath(sub_file.name),os.path.abspath(sub_file.name),os.path.abspath(sub_file.name)))
    if (opts.batch == "T3CH") : 
          command = 'qsub -q %s -o %s.log -e %s.err %s > out.txt'%(opts.queue,os.path.abspath(sub_file.name),os.path.abspath(sub_file.name),os.path.abspath(sub_file.name))
          print command
          system(command)


#######################################
system('mkdir -p %s/fTestJobs/outputs'%opts.outDir)
counter=0
indirOpt = ""
if opts.indir:
    indirOpt = " --indir "+str(opts.indir)
for proc in  opts.procs.split(","):
  for cat in opts.flashggCats.split(","):
    print "job ", counter , " - ", proc, " - ", cat
    file = open('%s/fTestJobs/sub%d.sh'%(opts.outDir,counter),'w')
    writePreamble(file)
    counter =  counter+1
    exec_line = "%s/bin/signalFTest -i %s  -p %s -f %s --considerOnly %s -o %s/%s --datfilename %s/%s/fTestJobs/outputs/config_%d.dat %s" %(os.getcwd(), opts.infile,proc,opts.flashggCats,cat,os.getcwd(),opts.outDir,os.getcwd(),opts.outDir, counter,indirOpt)
    # print exec_line
    writePostamble(file,exec_line)
    
