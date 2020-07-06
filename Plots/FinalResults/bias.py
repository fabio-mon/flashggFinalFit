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
hist_all = ROOT.TH1F("hist_all","hist_all",32,-4,4)
#tree.Draw("((r-%s)/rErr)>>hist_all"%mu,"fit_status==0")  #only for FitDiagnostic
r = []
rLow = []
rUp = []
safe=False
n_toys=0
for inum,entry in enumerate(tree):
  if (inum)%3==0 : 
     #if tree.r>0.0101 :  #if have to do one sided gaussian because of negative poisson
     if tree.r>-100000. :  #no condition
       r.append(tree.r)
       safe=True
       n_toys+=1
     else : safe=False
  if (inum)%3==1 : 
     if safe :
       rLow.append(tree.r)
  if (inum)%3==2 : 
     if safe :
       rUp.append(tree.r)
r=np.array(r)
rLow=np.array(rLow)
#rErr = abs(r-rLow)
#rErr = abs(rUp-r)
rErr = abs((rUp-rLow)/2.)
for i in range(0,len(r)):
  hist_all.Fill((r[i]-float(mu))/(rErr[i]))
#n_toys = tree.GetEntries("fit_status==0")
print n_toys,hist_all.Integral()

mean = hist_all.GetMean()
rms =  hist_all.GetRMS()
print 'Mean = ',mean
print 'RMS = ',rms
hist_all.SetStats(False)
hist_all.SetLineColor(1)
hist_all.SetLineWidth(2)
ymax=hist_all.GetMaximum()*1.1
hist_all.GetYaxis().SetRangeUser(0.,ymax)
hist_all.GetXaxis().SetTitle("(#mu-#mu_{inj})/#sigma")
hist_all.GetYaxis().SetTitle("Toys")
hist_all.Draw()
print hist_all.Integral()
func = ROOT.TF1("func","gaus",-3,3)
func.SetLineColor(ROOT.kRed)
func.SetLineWidth(3)
hist_all.Fit(func,"R")
 

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
pave2.AddText("Fit :")
#pave2.AddText("#mu=%0.2f"%func.GetParameter(1))
#pave2.AddText("#sigma=%0.2f"%func.GetParameter(2))
pave2.AddText("#mu=%0.2f#pm%.2f"%(func.GetParameter(1),func.GetParError(1)))
pave2.AddText("#sigma=%0.2f#pm%.2f"%(func.GetParameter(2),func.GetParError(2)))
#pave2.AddText("Mean=%0.2f"%(mean))
#pave2.AddText("RMS=%0.2f"%(rms))
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
canv.SaveAs("plots/plot_inj%s_%s_multiDim_%s_%s.pdf"%(mu,toy_func,cat,outtag))
canv.SaveAs("plots/plot_inj%s_%s_multiDim_%s_%s.jpg"%(mu,toy_func,cat,outtag))
