#!/usr/bin/python
from optparse import OptionParser
import sys
import os
import myutilities

#const parameters
wsname = "tagsDumper/cms_hgg_13TeV"
mass_shifts = [-5.,0.,5.]
higgs_mass = 125.

#parse arguments
parser = OptionParser()
parser.add_option("-i", "--infilename",  action="store",      type="str", dest="infilename",                         help="input file name")
parser.add_option("-p", "--process",     action="store",      type="str", dest="process",        default="",         help="process name")
parser.add_option("-o", "--outfilename", action="store",      type="str", dest="outfilename",    default="",         help="output file name")
parser.add_option("-d", "--outdir",      action="store",      type="str", dest="outdir",         default="",         help="output directory name")

(options, args) = parser.parse_args()


#infer process name, if not provided --> NOTE: could make mistakes
process=options.process
if process=="":
   process=myutilities.inferprocessname(options.infilename,wsname)
print "inferred process name is "+process 


import ROOT
from ROOT import * 
#open input file
infile = TFile(options.infilename)
ws = infile.Get(wsname)
dataset_list = ws.allData()

#loop over the mass shifts to apply
for mass_shift in mass_shifts:
    mass=higgs_mass+mass_shift

    #define new process name
    newprocname=process
    possible_mass_labels=["M125","M_125","M-125","m125","m_125","m-125","125"]
    for mass_label in possible_mass_labels:
        newprocname=newprocname.replace(mass_label,("%i"%mass))
    if(newprocname.find("%i"%mass)==-1):
        newprocname+=("_%i"%mass)
    print "new process name is "+newprocname

    #get/generate the output file name 
    outfilename=options.outfilename
    if outfilename=="":
        outfilename=newprocname+".root"
    else:
        outfilename=outfilename.replace(".root","_%i.root"%mass)

    outfile = TFile(options.outdir+"/"+outfilename,"RECREATE")
    outfile.mkdir("tagsDumper")
    outfile.cd("tagsDumper")
    outws = RooWorkspace("cms_hgg_13TeV","cms_hgg_13TeV")

    #loop over datasets --> rename, shift and save datasets
    for dataset in dataset_list:
  
        #get category name
        ss=ostringstream()	
        dataset.printName(ss)
        datasetname = ss.str()
        print "doing dataset "+datasetname
        catname=datasetname.replace(process+"_","")
        print "category name is "+catname

        if mass!=125:
            shifted_dataset = ws.data(datasetname).Clone(newprocname+"_"+catname).reduce(RooArgSet(ws.var("CMS_hgg_mass"),ws.var("dZ"),ws.var("centralObjectWeight")))
            shifted_dataset.SetName(newprocname+"_"+catname)
            shifted_dataset.changeObservableName("CMS_hgg_mass","CMS_hgg_mass_old")
            oldmass = shifted_dataset.get()["CMS_hgg_mass_old"]
            newmass = RooFormulaVar( "CMS_hgg_mass", "CMS_hgg_mass", "(@0+%.1f)"%mass,RooArgList(oldmass) )
            shifted_dataset.addColumn(newmass).setRange(100,180)
            getattr(outws, 'import')(shifted_dataset, RooCmdArg())
        else:
            shifted_dataset = ws.data(datasetname).reduce(RooArgSet(ws.var("CMS_hgg_mass"),ws.var("dZ"),ws.var("centralObjectWeight")))
            shifted_dataset.SetName(newprocname+"_"+catname)
            getattr(outws, 'import')(shifted_dataset, RooCmdArg())

    print "saving output to "+options.outdir+"/"+outfilename  
    outws.Write()
    outfile.Close()

infile.Close()
