import ROOT
from ROOT import TFile, TTree, TCanvas, TGraph, TMultiGraph, TGraphErrors, TLegend,TH1F
import subprocess # to execute shell command
ROOT.gROOT.SetBatch(ROOT.kTRUE)
from optparse import OptionParser

# GET limits from root file
def getLimits(file_name):

    file = TFile(file_name)
    tree = file.Get("limit")

    limits = [ ]
    for quantile in tree:
        limits.append(tree.limit)
      #  print ">>>   %.2f" % limits[-1]

    return limits[:6]

def convert_reorder(number,limit):
   limit_str=[]
   limit_str.append("%d"%number)
   limit_str.append("%.5f"%limit[2])
   if not options.unblind : limit_str.append("%.5f"%limit[2])   #if no observed, then append again expected
   else : limit_str.append("%.5f"%limit[5])   #if no observed, then append again expected
   limit_str.append("%.5f"%limit[4])
   limit_str.append("%.5f"%limit[3])
   limit_str.append("%.5f"%limit[1])
   limit_str.append("%.5f"%limit[0])
   return limit_str


# PLOT upper limits
def plotUpperLimits(labels):
    f = open('%s/benchmarks_limits_%s.txt'%(options.indir,options.outtag), 'w')
    names = 'BENCH,EXP,OBS,+2sigma,+1sigma,-1sigma,-2sigma'.split(',')
    f.write(('\t\t\t').join(names[0:]) + '\n')
    N = len(labels)
    limits_str = []
    for i in range(N):
        #file_name = options.indir+"/higgsCombine_"+labels[i]+"_"+options.outtag+".Asymptotic.mH125.root"
        file_name = options.indir+"/higgsCombine_"+labels[i]+"_"+options.outtag+".AsymptoticLimits.mH125.root"
        limit = getLimits(file_name)
        limit_str = convert_reorder(i+1,limit)
        f.write(('\t\t\t').join(limit_str[0:]) + '\n')
    f.close()

# MAIN
parser = OptionParser()
parser.add_option("--indir", help="Input directory ")
parser.add_option("--outdir", help="Output directory ")
parser.add_option("--outtag", help="Output tag ")
parser.add_option("--unblind", action="store_true",help="Observed is present or not ",default=False)

(options,args)=parser.parse_args()

labels = [] 
#for node in range(0,12):
#   label = "node%d"%node
#   labels.append(label)
#labels.append("nodeSM")
#labels.append("nodebox")

for node in range(0,14):
   label = "benchmarks_%d"%node
   labels.append(label)


plotUpperLimits(labels)

