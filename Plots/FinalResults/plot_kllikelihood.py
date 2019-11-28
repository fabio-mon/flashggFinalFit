import ROOT
import re, optparse
from optparse import OptionParser
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)

def extra_texts():
    # print "... drawing extra texts"
    ### extra text
    cmstextfont   = 61  # font of the "CMS" label
    cmstextsize   = 0.05  # font size of the "CMS" label
    chantextsize = 18
    extratextfont = 52     # for the "preliminary"
    extratextsize = 0.76 * cmstextsize # for the "preliminary"
    lumitextfont  = 42
    cmstextinframe = False

    yoffset = -0.046

    lumibox = ROOT.TLatex  (0.9, 0.964+yoffset, "136.8 fb^{-1} (13 TeV)")
    lumibox.SetNDC()
    lumibox.SetTextAlign(31)
    lumibox.SetTextSize(extratextsize)
    lumibox.SetTextFont(lumitextfont)
    lumibox.SetTextColor(ROOT.kBlack)

    # xpos  = 0.177
    xpos  = 0.137
    if cmstextinframe:
        ypos  = 0.94 ## inside the frame
    else:
        ypos  = 0.995  ## ouside the frame
    CMSbox = ROOT.TLatex  (xpos, ypos+yoffset+0.01, "CMS")       
    CMSbox.SetNDC()
    CMSbox.SetTextSize(cmstextsize)
    CMSbox.SetTextFont(cmstextfont)
    CMSbox.SetTextColor(ROOT.kBlack)
    CMSbox.SetTextAlign(13) ## inside the frame

    # simBox = ROOT.TLatex  (xpos, ypos - 0.05+yoffset, "Simulation")
    simBox = ROOT.TLatex  (xpos + 0.12, ypos+yoffset, "")
    simBox.SetNDC()
    simBox.SetTextSize(extratextsize)
    simBox.SetTextFont(extratextfont)
    simBox.SetTextColor(ROOT.kBlack)
    simBox.SetTextAlign(13)


    channelLabel = ROOT.TLatex  (0.6-0.05, 0.8, "HH #rightarrow #gamma#gammab#bar{b}")
    channelLabel.SetNDC()
    # channelLabel.SetTextAlign(31)
    channelLabel.SetTextSize(1.15*extratextsize)
    channelLabel.SetTextFont(lumitextfont)
    channelLabel.SetTextColor(ROOT.kBlack)


    return [lumibox, CMSbox, simBox, channelLabel]
    # lumibox.Draw()
    # CMSbox.Draw()
    # simBox.Draw()
    # channelLabel.Draw()

def create_gr(tree,color):
  gr = ROOT.TGraph()
  kl_list = []
  deltaNll_list = []

  for ipt in range(0, tree.GetEntries()): 
    if (ipt%2)!=0:    ## for some reason, point nr 0 is not the first in the scan -> skip it, when submitting job it is every first one
      tree.GetEntry(ipt)
      kl_list.append(tree.kl)
      deltaNll_list.append(2.*tree.deltaNLL)
  kl_list, deltaNll_list = zip(*sorted(zip(kl_list, deltaNll_list)))

  for i in range(0,len(kl_list)): 
    gr.SetPoint(gr.GetN(), kl_list[i], deltaNll_list[i]) ## plot -2 log L

  gr.SetMarkerStyle(8)
  gr.SetMarkerColor(color)
  gr.SetLineColor(color)
  gr.SetLineWidth(2)
  gr.SetMarkerSize(0.8)
  return gr

###########OPTIONS
parser = OptionParser()
parser.add_option("--indir", help="Input directory ")
parser.add_option("--infile", help="Input file ")
parser.add_option("--outdir",default='plots/', help="Output directory ")
parser.add_option("--outtag", help="Output tag")
parser.add_option("--zoom", action="store_true" , help="Zoom the plot ")
parser.add_option("--unblind", action="store_true",help="Observed is present or not ",default=True)
#parser.add_option("--channels_to_run",default="all,DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11", help = "which channels to run on")
parser.add_option("--channels_to_run",default="all", help = "which channels to run on")
(options,args)=parser.parse_args()
###########


fInName = '%s/%s'%(options.indir,options.infile)
fname = fInName
colors = [1,
ROOT.kRed+0,ROOT.kOrange+0,ROOT.kGreen+1,ROOT.kBlue-6,
ROOT.kRed+1,ROOT.kOrange-3,ROOT.kGreen+2,ROOT.kBlue+0,
ROOT.kRed+2,ROOT.kOrange+2,ROOT.kGreen+3,ROOT.kBlue+1]
graphs = []
xmin = -6
xmax = 11
ymax = 10
dolegend = False
if options.zoom:
  xmin = -3
  xmax = 7
  ymax = 2
for ich,ch in enumerate(options.channels_to_run.split(",")):
   if ch!="all" :
      fname =  fInName.replace("all",ch) 
      xmin = -20
      xmax = 20
      ymax = .6
      dolegend = True
   fIn = ROOT.TFile.Open(fname)
   tree = fIn.Get('limit')
   graphs.append(create_gr(tree,colors[ich]))

c1 = ROOT.TCanvas('c1', 'c1', 600, 600)
c1.SetFrameLineWidth(3)
c1.SetBottomMargin(0.13)
c1.SetLeftMargin(0.13)


frame = ROOT.TH1D('frame', ';#kappa_{#lambda};-2#Deltaln(L)', 100, xmin, xmax)
frame.SetMinimum(0)
frame.SetMaximum(ymax)
frame.GetXaxis().SetTitleSize(0.05)
frame.GetYaxis().SetTitleSize(0.05)
frame.GetXaxis().SetTitleOffset(1.25)
frame.GetYaxis().SetTitleOffset(1.25)
frame.Draw()

for gr in graphs :
  if not dolegend : gr.Draw('PLsame')
  else : gr.Draw('Lsame')
  ROOT.gDirectory.Append(gr)

### lines
sigmas = [1,1.96]
CL = [68,95]
lines = []
for s in sigmas:
    l = ROOT.TLine(xmin, s*s, xmax, s*s)
    l.SetLineStyle(7)
    l.SetLineWidth(1)
    l.SetLineColor(ROOT.kGray+2)
    lines.append(l)
for l in lines: l.Draw()

## text for sigmas
labels = []
for isigma,s in enumerate(sigmas):
    lab = ROOT.TLatex(xmax + 0.03*(xmax-xmin), s*s, "%d%%" % CL[isigma])
    lab.SetTextFont(42)
    lab.SetTextColor(lines[0].GetLineColor())
    lab.SetTextSize(0.04)
    labels.append(lab)
for l in labels: l.Draw()

et = extra_texts()
for t in et: t.Draw()

legend = ROOT.TLegend(0.2,0.43,0.36,0.9)
legend.SetBorderSize(0)
legend.SetFillStyle(-1)
legend.SetTextFont(42)
legend.SetTextSize(0.03)
for ich,ch in enumerate(options.channels_to_run.split(",")):
   if ch=="all" :
    legend.AddEntry(graphs[ich],"Combined","L")
   else : legend.AddEntry(graphs[ich],"CAT %s"%(ch.replace("DoubleHTag_","")),"L")
if dolegend : legend.Draw("same")

outname = '%s/klambda_likelihood_%s'%(options.outdir,options.outtag)
if options.zoom : outname+="_zoom"
c1.Print('%s.pdf'%outname, 'pdf')

### also dump to a ROOT file
fOut = ROOT.TFile('%s.root'%outname, 'recreate')
fOut.cd()
gr.SetName('kl_likelihood')
gr.Write()
