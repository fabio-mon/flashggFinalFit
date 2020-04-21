import ROOT
from ROOT import *
from ROOT import gStyle
import sys
import numpy as np



gROOT.SetBatch(True)
gROOT.ProcessLineSync(".x /work/nchernya/setTDRStyle.C")
gROOT.ForceStyle()
gStyle.SetPadTopMargin(0.06)
gStyle.SetPadRightMargin(0.04)
gStyle.SetPadLeftMargin(0.15)

filename=sys.argv[1]
mu=sys.argv[2]
cat=sys.argv[3]
outtag=sys.argv[4]

fit_funcs=['Exp1,Pow1,Bern1']
toy_func='Bern3'
path=''
 
canv = ROOT.TCanvas("canv","canv",900,900)
archive=[]
f = ROOT.TFile.Open(path+filename)
#tree = f.Get("tree_fit_sb")#only for FitDiagnostic
tree = f.Get("limit")#only for FitDiagnostic
hist_all = ROOT.TH1F("hist_all","hist_all",40,0,20)
#tree.Draw("((r-%s)/rErr)>>hist_all"%mu,"fit_status==0")  #only for FitDiagnostic
r = []
rLow = []
rUp = []
for inum,entry in enumerate(tree):
  if (inum)%3==0 : r.append(tree.r)
  if (inum)%3==1 : rLow.append(tree.r)
  if (inum)%3==2 : rUp.append(tree.r)
r=np.array(r)
rLow=np.array(rLow)
#rErr = abs(r-rLow)
rErr = abs((rUp-rLow)/2.)
for i in range(0,len(r)):
  hist_all.Fill((rErr[i]))
#n_toys = tree.GetEntries("fit_status==0")
n_toys = int(tree.GetEntries()/3.)
print n_toys,hist_all.Integral()

mean = hist_all.GetMean()
rms =  hist_all.GetRMS()
hist_all.SetStats(False)
hist_all.SetLineColor(1)
hist_all.SetLineWidth(2)
ymax=hist_all.GetMaximum()*1.1
hist_all.GetYaxis().SetRangeUser(0.,ymax)
hist_all.GetXaxis().SetTitle("#sigma")
hist_all.GetYaxis().SetTitle("Toys")
hist_all.Draw()
print hist_all.Integral()
 

pave22 = ROOT.TPaveText(0.7,0.85,0.95,0.9,"NDC")
pave22.AddText("%s"%cat)
pave22.SetFillColor(0)
pave22.SetTextFont(42)
pave22.SetTextColor(ROOT.kBlue)
pave22.SetTextSize(0.04)
pave22.SetBorderSize(0)
pave22.Draw()
gPad.Update()


pave2 = ROOT.TPaveText(0.2,0.65,0.4,0.9,"NDC")
pave2.AddText("Toy : "+toy_func)
pave2.AddText("# toys =%0.2f"%n_toys)
pave2.AddText("#mu_{inj}=%s"%mu)
pave2.AddText("Mean =%0.1f"%hist_all.GetMean())
pave2.AddText("RMS=%0.1f"%hist_all.GetRMS())
pave2.SetFillColor(0)
pave2.SetTextFont(42)
pave2.SetTextColor(ROOT.kBlue)
pave2.SetTextSize(0.04)
pave2.SetBorderSize(0)
pave2.Draw();
gPad.Update()
right,top   = gStyle.GetPadRightMargin(),gStyle.GetPadTopMargin()
pave2.SetY1NDC(pave2.GetY2NDC()-top*0.9*pave2.GetListOfLines().GetSize())
pave2.Draw();
archive+=[pave2]
archive+=[pave22]
canv.SaveAs("plots/plot_sigma_inj%s_%s_multiDim_%s_%s.pdf"%(mu,toy_func,cat,outtag))
canv.SaveAs("plots/plot_sigma_inj%s_%s_multiDim_%s_%s.jpg"%(mu,toy_func,cat,outtag))
