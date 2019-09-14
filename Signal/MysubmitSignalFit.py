#!/usr/bin/env python

import os
import numpy
import sys
import fnmatch
from copy import deepcopy as copy
import re

from optparse import OptionParser
from optparse import OptionGroup

replacement_dictionary = {
    "hh"  : ["hh"  , "DoubleHTag_0"],
    "tth" : ["tth" , "TTHHadronicTag_3"],
    "ggh" : ["ggh" , "UntaggedTag_3"], 
    "qqh" : ["ggh" , "UntaggedTag_3"],
    "vh"  : ["ggh" , "UntaggedTag_3"]
    }

parser = OptionParser()
parser.add_option("-y","--year",help="Year")
parser.add_option("-i","--infile",help="Signal Workspace")
parser.add_option("-d","--datfile",help="dat file")
parser.add_option("-s","--systdatfile",help="systematics dat file")
parser.add_option("--mhLow",default="120",help="mh Low")
parser.add_option("--mhHigh",default="130",help="mh High")
parser.add_option("-q","--queue",help="Which batch queue")
parser.add_option("--runLocal",default=False,action="store_true",help="Run locally")
parser.add_option("--changeIntLumi",default="1.")
parser.add_option("-o","--outfilename",default=None)
parser.add_option("-p","--outDir",default="./")
parser.add_option("--procs",default=None)
parser.add_option("--useDCB_1G",default="0")
parser.add_option("--useSSF",default="0")
parser.add_option("--massList",default="120,125,130")
parser.add_option("-f","--flashggCats",default=None)
parser.add_option("--bs",default=5.14)
parser.add_option("--expected",type="int",default=None)
parser.add_option("--refProc",default="",help="ref replacement process")
parser.add_option("--refTag",default="",help="ref replacement tag ")
parser.add_option("--indir",default="",help="infile directory ")
(opts,args) = parser.parse_args()

  
os.system('mkdir -p %s/SignalFitJobs/outputs'%opts.outDir)
print ('mkdir -p %s/SignalFitJobs/outputs'%opts.outDir)
counter=0
indirOpt = ""

if opts.indir:
    indirOpt = " --indir "+str(opts.indir)

print "Generating rootfilenames for shifted masses"
fileliststring = ""
for filename125 in opts.infile.split(","):
    for m in opts.massList.split(","):
        filename=filename125.replace("_125.root","_"+m+".root")
        if fileliststring!="":
            fileliststring+=","+filename
        else:
            fileliststring+=filename
    
print "--> here is the list: "+fileliststring

for proc in  opts.procs.split(","):

  refProcOpt = ""
  if opts.refProc!="":
    refProcOpt = " --refProc "+str(opts.refProc)

  refTagOpt = ""
  if opts.refTag!="":
    refTagOpt = " --refTag "+str(opts.refTag)

  #auto find reference proc if not provided yet
  if opts.refProc=="" and opts.refTag=="":
    for myrefproc in replacement_dictionary:
      if myrefproc in proc:
        referenceproc=replacement_dictionary[myrefproc][0]+opts.year
        refProcOpt = " --refProc "+referenceproc
        refTagOpt = " --refTag "+replacement_dictionary[myrefproc][1]
        print "automatic replacement proc,tag is "+referenceproc+","+replacement_dictionary[myrefproc][1] 
        break

  for cat in opts.flashggCats.split(","):
    print "job ", counter , " - ", proc, " - ", cat
    scriptname=('%s/SignalFitJobs/sub%d.sh'%(opts.outDir,counter))
    scriptfile = open(scriptname,'w')
    #print "[INFO] writing preamble"
    scriptfile.write('#!/bin/bash\n')
    scriptfile.write('cd %s\n'%os.getcwd())
    scriptfile.write('eval `scramv1 runtime -sh`\n')
    scriptfile.write('number=$RANDOM\n')
    scriptfile.write('mkdir -p scratch_$number\n')
    scriptfile.write('cd scratch_$number\n')
    counter =  counter+1
    bsRW=0
    if (float(opts.bs)==0):
      bsRW=0
    else:
      bsRW=1
    exec_line = "%s/bin/SignalFit --verbose 0 -i %s -d %s/%s  --mhLow=%s --mhHigh=%s -s %s/%s --procs %s -o  %s/%s -p %s/%s -f %s --changeIntLumi %s --binnedFit 1 --nBins 320 --split %s,%s --beamSpotReweigh %d --dataBeamSpotWidth %f --massList %s --useDCBplusGaus %s --useSSF %s %s %s %s" %(os.getcwd(), fileliststring,os.getcwd(),opts.datfile,opts.mhLow, opts.mhHigh, os.getcwd(),opts.systdatfile, opts.procs,os.getcwd(),opts.outfilename.replace(".root","_%s_%s.root"%(proc,cat)), os.getcwd(),opts.outDir, opts.flashggCats ,opts.changeIntLumi, proc,cat,bsRW,float(opts.bs), opts.massList, opts.useDCB_1G, opts.useSSF,refProcOpt,refTagOpt,indirOpt)
    #print exec_line
    #print "[INFO] writing to postamble"
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
    scriptfile.close()
    os.system('chmod +x %s'%os.path.abspath(scriptname))
    if opts.runLocal:
      os.system('bash %s > %s.log'%(os.path.abspath(scriptname),os.path.abspath(scriptname)))
    elif opts.queue:
      os.system('rm -f %s.done'%os.path.abspath(scriptname))
      os.system('rm -f %s.fail'%os.path.abspath(scriptname))
      os.system('rm -f %s.log'%os.path.abspath(scriptname))
      os.system('rm -f %s.err'%os.path.abspath(scriptname))

print("writing .sub file")
condorsubname = os.path.abspath('%s/SignalFitJobs/condorsub.sub'%opts.outDir)
condorsub = open(condorsubname,'w')
condorsub.write('requirements = (OpSysAndVer =?= "SLCern6")\n')
condorsub.write("executable            = $(scriptname)\n")
condorsub.write("output                = $(scriptname).out\n")
condorsub.write("error                 = $(scriptname).err\n")
condorsub.write("log                   = $(scriptname).log\n")
condorsub.write('+JobFlavour           = "'+opts.queue+'"\n')
condorsub.write("queue scriptname matching %s/SignalFitJobs/sub*.sh"%opts.outDir)
condorsub.close()
print("condor_submit "+condorsubname)
os.system("condor_submit "+condorsubname)
