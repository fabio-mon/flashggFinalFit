import ROOT
from ROOT import TH1F,TFile, TCanvas, TGraph,TGraphAsymmErrors, TLegend
import numpy as np
import json

nodes ="SM,1,11".split(",") 
differential = True

year='2018'
#filename = "/scratch/nchernya/HHbbgg/18_02_2020/output_hh_2018_gen.root"
filename = "/scratch/nchernya/HHbbgg/18_02_2020/output_hh_%s_gen.root"%year
#and categorized (but without pt/Mjj > 0.25 
file = TFile(filename)
#treeReco = file.Get("tagsDumper/trees/hh2018_13TeV_125_13TeV_DoubleHTag_0")
treeReco = file.Get("hh%s_13TeV_125_13TeV_DoubleHTag_0"%year)
treeGen = file.Get("genDiphotonDumper/trees/hh2018_13TeV_125_13TeV_DoubleHTag_0")
treeGen2 = file.Get("genDiphotonDumper/trees/hh2018_13TeV_125_13TeV_NoTag_0")
renorm_file = open('/work/nchernya/DiHiggs/inputs/20_12_2019/reweighting_normalization_18_12_2019.json').read()
normalizations_json = json.loads(renorm_file)

MVAcats = [0.37,0.62,0.78,1]
selections = ["1"]
selection_names = ["Preselection","MVA0 [0.78-1.00]","MVA1 [0.62-0.78]","MVA2 [0.37-0.62]"]
nMVA =len(MVAcats)-1 
for mva_num in reversed(range(0,nMVA)):
  selections.append("((MVAOutputTransformed > %.2f) && (MVAOutputTransformed < %.2f))"%(MVAcats[mva_num],MVAcats[mva_num+1]))

NBINS = 10;
edges = np.linspace(250,800,NBINS+1)

mhh_hist_nodes = []

for node in nodes :
 hists_reco = []
 hists_gen = []
 grs = []
 colors = [ROOT.kBlack,ROOT.kRed+0,ROOT.kOrange-3,ROOT.kGreen+1]
 for i_s, sel in enumerate(selections):
   hMhhreco = TH1F("hMhhreco_%s_%s"%(node,i_s),"hMhhreco_%s_%s"%(node,i_s),NBINS,edges)
   hMhhreco_fine = TH1F("hMhhreco_fine_%s_%s"%(node,i_s),"hMhhreco_fine_%s_%s"%(node,i_s),50,250,1000)
   hMhhgen = TH1F("hMhhgen_%s_%s"%(node,i_s),"hMhhgen_%s_%s"%(node,i_s),NBINS,edges)
   treeReco.Draw("genMhh>>hMhhreco_%s_%s"%(node,i_s),"%s*weight*benchmark_reweight_%s/%.3f"%(sel,node,normalizations_json[year]["benchmark_%s_normalization"%node]))
   treeReco.Draw("genMhh>>hMhhreco_fine_%s_%s"%(node,i_s),"%s*weight*benchmark_reweight_%s/%.3f"%(sel,node,normalizations_json[year]["benchmark_%s_normalization"%node]))
   treeGen.Draw("mhh>>hMhhgen_%s_%s"%(node,i_s),"weight*benchmark_reweight_%s/%.3f/1.06"%(node,normalizations_json[year]["benchmark_%s_normalization"%node]))
   treeGen2.Draw("mhh>>+hMhhgen_%s_%s"%(node,i_s),"weight*benchmark_reweight_%s/%.3f/1.06"%(node,normalizations_json[year]["benchmark_%s_normalization"%node]))
   normalization = hMhhreco.Integral(0,NBINS+1)
   normalizationGen = hMhhgen.Integral(0,NBINS+1)
   print "Selection, norm : ",sel,normalization, normalizationGen
   hists_reco.append(hMhhreco)
   hists_gen.append(hMhhgen)
   if i_s==0:mhh_hist_nodes.append(hMhhreco_fine)

   hMhhreco_norm = hMhhreco.Clone("hMhhreco_norm_%s_%s"%(node,i_s))
   hMhhreco_norm.Scale(1./hMhhreco_norm.Integral())
   print "test : ",hMhhreco_norm.Integral(),hMhhreco.Integral()
   if differential : hMhhreco_norm.Multiply(hMhhreco) 
   print "test 2 : ",hMhhreco_norm.Integral(),hMhhreco.Integral()
   gr = TGraphAsymmErrors()
   gr.Divide(hMhhreco_norm,hMhhgen,"cl=0.683 b(1,1) mode")
   gr.SetLineColor(colors[i_s])
   gr.SetMarkerColor(colors[i_s])
   gr.SetMarkerStyle(20+i_s)
   gr.SetMarkerSize(2)
   grs.append(gr)
 

 c1 = TCanvas("c","",900,900)
 c1.SetGrid()
 hEff = TH1F("hEff_%s"%node,"",NBINS,edges)
 hEff.GetYaxis().SetTitleOffset(1.3)
 hEff.GetYaxis().SetTitle("Efficiency x acceptance")
 if differential : hEff.GetYaxis().SetTitle("Efficiency x acceptance (M(HH))")
 hEff.GetXaxis().SetTitle("M(HH) (GeV)")
 hEff.SetStats(0)
 if "SM" in node : hEff.SetTitle("HH #rightarrow #gamma#gammab#bar{b} SM")
 else : hEff.SetTitle("BSM node %s"%node)
 hEff.GetYaxis().SetRangeUser(0.,1.05)
 if differential : hEff.GetYaxis().SetRangeUser(0.,0.18)
 hEff.Draw()
 legend = TLegend(0.3,0.62,0.55,0.85)
 legend.SetBorderSize(0)
 legend.SetFillStyle(-1)
 legend.SetTextFont(42)
 legend.SetTextSize(0.04)
 for i_gr,gr in enumerate(grs):
   gr.Draw("PEsame")
   legend.AddEntry(gr,selection_names[i_gr],"P")
 legend.Draw("same")
 savename = "plots/efficiency_mhh_split_node_%s.pdf"%node
 if differential : savename = savename.replace(".pdf","_differential.pdf")
 c1.Print(savename)

 


c2 = TCanvas("c2","",900,900)
frame = TH1F("frame_%s"%node,"",NBINS,edges)
frame.GetYaxis().SetTitleOffset(1.3)
frame.GetYaxis().SetTitle("A.U.")
frame.GetXaxis().SetTitle("M(HH) (GeV)")
frame.SetStats(0)
frame.SetTitle("")
frame.GetYaxis().SetRangeUser(0.,mhh_hist_nodes[0].GetMaximum()*1.3)
frame.Draw()
legend = TLegend(0.7,0.62,0.85,0.85)
legend.SetBorderSize(0)
legend.SetFillStyle(-1)
legend.SetTextFont(42)
legend.SetTextSize(0.04)
for i_h,hist in enumerate(mhh_hist_nodes):
  hist.SetLineColor(colors[i_h])
  hist.SetLineWidth(2)
  hist.SetMarkerColor(colors[i_h])
  hist.SetMarkerStyle(20+i_h)
  hist.Draw("HISTsame")
  legend.AddEntry(hist,"Node %s"%nodes[i_h],"L")
legend.Draw("same")
c2.Print("plots/mhh_nodes.pdf")
 


