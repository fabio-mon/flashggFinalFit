#!/usr/bin/env python
import os
import sys
import fnmatch
from copy import deepcopy as copy
import re

from optparse import OptionParser
from optparse import OptionGroup

parser = OptionParser()
parser.add_option("-i","--infile",                                          help="Signal Workspace")
parser.add_option("-q","--queue",                                           help="Which batch queue")
parser.add_option("--runLocal",    default=False,      action="store_true", help="Run locally")
parser.add_option("--outDir",      default=None,                            help="ouput directory")
parser.add_option("--procs",       default=None,                            help="process(es) name(s)")
parser.add_option("--flashggCats", default=None,                            help="category names")       
parser.add_option("--indir",       default="",                              help="infile directory ")
(opts,args) = parser.parse_args()


os.system('mkdir -p %s/fTestJobs/outputs'%opts.outDir)
counter=0
indirOpt = ""
if opts.indir:
    indirOpt = " --indir "+str(opts.indir)
for proc in  opts.procs.split(","):
  for cat in opts.flashggCats.split(","):
    print "job ", counter , " - ", proc, " - ", cat
    scriptname='%s/fTestJobs/sub%d.sh'%(opts.outDir,counter)
    scriptfile = open(scriptname,'w')
    scriptfile.write('#!/bin/bash\n')
    scriptfile.write('cd %s\n'%os.getcwd())
    scriptfile.write('eval `scramv1 runtime -sh`\n')
    scriptfile.write('cd -\n')
    scriptfile.write('number=$RANDOM\n')
    scriptfile.write('mkdir -p scratch_$number\n')
    scriptfile.write('cd scratch_$number\n')
    exec_line = "%s/bin/signalFTest -i %s  -p %s -f %s --considerOnly %s -o %s/%s --datfilename %s/%s/fTestJobs/outputs/config_%d.dat %s\n" %(os.getcwd(), opts.infile,proc,opts.flashggCats,cat,os.getcwd(),opts.outDir,os.getcwd(),opts.outDir, counter,indirOpt)

    scriptfile.write('\t echo "PREPARING TO RUN "\n')
    scriptfile.write('\t touch %s.run\n'%os.path.abspath(scriptname))
    scriptfile.write('if ( %s ) then\n'%exec_line)
    #scriptfile.write('\t mv higgsCombine*.root %s\n'%os.path.abspath(opts.outDir))
    scriptfile.write('\t echo "DONE" \n')
    scriptfile.write('\t touch %s.done\n'%os.path.abspath(scriptname))
    scriptfile.write('else\n')
    scriptfile.write('\t echo "FAIL" \n')
    scriptfile.write('\t touch %s.fail\n'%os.path.abspath(scriptname))
    scriptfile.write('fi\n')
    scriptfile.write('cd -\n')
    scriptfile.write('\t echo "RM RUN "\n')
    scriptfile.write('rm -f %s.run\n'%os.path.abspath(scriptname))
    scriptfile.write('rm -rf scratch_$number\n')

    counter =  counter+1
    scriptfile.close()
    os.system('chmod +x %s'%os.path.abspath(scriptname))
    if opts.runLocal:
      os.system('bash %s > %s.log'%(os.path.abspath(scriptname),os.path.abspath(scriptname)))
      sys.exit()
    ++counter

if opts.queue:
  os.system('rm -f %s.done'%os.path.abspath(scriptname))
  os.system('rm -f %s.fail'%os.path.abspath(scriptname))
  os.system('rm -f %s.log'%os.path.abspath(scriptname))
  os.system('rm -f %s.err'%os.path.abspath(scriptname))
  condorsubname=os.path.abspath('%s/fTestJobs/condorsub.sub'%opts.outDir)
  condorsub = open(condorsubname,'w')
  #condorsub.write('requirements = (OpSysAndVer =?= "SLCern6")\n')
  condorsub.write("executable            = $(scriptname)\n")
  condorsub.write("output                = $(scriptname).out\n")
  condorsub.write("error                 = $(scriptname).err\n")
  condorsub.write("log                   = "+os.path.abspath(condorsubname)+".log\n")
  condorsub.write('+JobFlavour           = "'+opts.queue+'"\n')
  condorsub.write("queue scriptname matching %s/fTestJobs/sub*.sh\n"%os.path.abspath(opts.outDir))
  condorsub.close()
  print "condor_submit "+condorsubname
  os.system("condor_submit "+condorsubname)
