#!/usr/bin/python
from optparse import OptionParser
import sys
import os
import myutilities

#const parameters
wsname = "tagsDumper/cms_hgg_13TeV"
process_map = { "GluGluHToGG":"ggh",
		"GluGluToHHTo2B2G":"hh",
		"VBFHToGG":"qqh",
		"VHToGG":"vh",
		"ttHJetToGG":"tth",
		"ttHToGG":"tth",
		"Data_13TeV":"Data_13TeV"}

#temporary to be removed
process_map = { "ggh":"ggh",
		"hh":"hh",
		"qqh":"qqh",
		"vh":"vh",
		"tth":"tth",
		"tth":"tth",
		"Data_13TeV":"Data_13TeV"}


#parse arguments
parser = OptionParser()
parser.add_option("-i", "--infilename",  action="store",      type="str", dest="infilename",                         help="input file name")
parser.add_option("-p", "--process",     action="store",      type="str", dest="process",        default="",         help="process name")
parser.add_option("-y", "--year",        action="store",      type="int", dest="year",                               help="year")
parser.add_option("-o", "--outfilename", action="store",      type="str", dest="outfilename",    default="",         help="output file name")
parser.add_option("-d", "--outdir",      action="store",      type="str", dest="outdir",         default="",         help="output directory name")

(options, args) = parser.parse_args()

#infer process name, if not provided --> NOTE: could make mistakes
process=options.process
if process=="":
   process=myutilities.inferprocessname(options.infilename,wsname)
print "inferred process name is "+process 

#find old and new process names
newprocname=""
for oldprocname in process_map:
    if oldprocname in process:
      newprocname=process_map[oldprocname]
      break

if newprocname=="":
  print "cannot find the specified process in my dictionary"
  sys.exit()
else:
  newprocname+=str(options.year)+"_13TeV_125"
  print "convert "+process+" to "+newprocname

#get/generate the output file name 
outfilename=options.outfilename
if outfilename=="":
  outfilename=newprocname+".root"#.replace("_M125",".root")

#loop over datasets--> rename and save
import ROOT
from ROOT import * 
infile = TFile(options.infilename)
ws = infile.Get(wsname)
dataset_list = ws.allData()

outfile = TFile(options.outdir+"/"+outfilename,"RECREATE")
outfile.mkdir("tagsDumper")
outfile.cd("tagsDumper")
outws = RooWorkspace("cms_hgg_13TeV","cms_hgg_13TeV")


for dataset in dataset_list:
  #get category name
  ss=ostringstream()	
  dataset.printName(ss)
  datasetname = ss.str()
  print "doing dataset "+datasetname
  catname=datasetname.replace(process+"_","")
  print "category name is "+catname

  #rename and clone the dataset
  newdatasetname=newprocname+"_"+catname
  print "new dataset name is "+newdatasetname
  dataset.SetNameTitle(newdatasetname,newdatasetname)
  getattr(outws, "import")(dataset, RooCmdArg())

print "saving output to "+options.outdir+"/"+outfilename  
outws.Write()
outfile.Close()
infile.Close()

