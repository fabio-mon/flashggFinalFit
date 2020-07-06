import re, optparse
from optparse import OptionParser
import os.path,sys
import argparse
from math import *
# from ROOT import *
import ROOT
ROOT.gROOT.SetBatch(True)
import json
from scipy.interpolate import interp1d
import numpy as np
#####

def redrawBorder():
   # this little macro redraws the axis tick marks and the pad border lines.
   ROOT.gPad.Update();
   ROOT.gPad.RedrawAxis();
   l = ROOT.TLine()
   l.SetLineWidth(3)
   l.DrawLine(ROOT.gPad.GetUxmin(), ROOT.gPad.GetUymax(), ROOT.gPad.GetUxmax(), ROOT.gPad.GetUymax());
   l.DrawLine(ROOT.gPad.GetUxmax(), ROOT.gPad.GetUymin(), ROOT.gPad.GetUxmax(), ROOT.gPad.GetUymax());
   l.DrawLine(ROOT.gPad.GetUxmin(), ROOT.gPad.GetUymin(), ROOT.gPad.GetUxmin(), ROOT.gPad.GetUymax());
   l.DrawLine(ROOT.gPad.GetUxmin(), ROOT.gPad.GetUymin(), ROOT.gPad.GetUxmax(), ROOT.gPad.GetUymin());


def getVals(fname):
	fIn = ROOT.TFile.Open(fname)
  	vals = []
	if fIn :
		tIn = fIn.Get('limit')
		if tIn.GetEntries() < 5:
			print "*** WARNING: cannot parse file", fname, "because nentries != 5"
			#raise RuntimeError('cannot parse file')
			return -1
		for i in range(0, tIn.GetEntries()):
			tIn.GetEntry(i)
			qe = tIn.quantileExpected
			lim = tIn.limit
			vals.append((qe,lim))
	else :
			vals = -1
	return vals



def eval_nnlo_xsec_ggF(kl):
   SF = 1.115  #1.115 is sigma_NNLO+FTapprox / sigma_NLO for SM = 31.05/27.84
   #fit to the parabola  
   A = 62.5339
   eA = 2.9369
   B = -44.3231
   eB = 1.9286
   C = 9.6340
   eC = 0.5185
   
   return SF*(A+B*kl+C*kl*kl)   

def nnlo_xsec_ggF_kl_wrap(x,par):
	return par[0]*eval_nnlo_xsec_ggF(x[0])



################################################################################################
###########OPTIONS
parser = OptionParser()
#parser.add_option("--gridConfig",default='/work/nchernya/DiHiggs/CMSSW_7_4_7/src/flashggFinalFit/Plots/FinalResults/c2v_grids/c2v_grid_finish.json',help="grid for coupling scan" )
#parser.add_option("--gridCrossSection",default='/work/nchernya/DiHiggs/CMSSW_7_4_7/src/flashggFinalFit/Plots/FinalResults/c2v_grids/vbfhhc2vline_finish.txt',help="theory prediction for coupling  scan for vbfhh" )
#parser.add_option("--vbfhhTheoryPrediction",default='/work/nchernya/DiHiggs/CMSSW_7_4_7/src/flashggFinalFit/Plots/FinalResults/c2v_grids/vbfhhc2vline_prediction.txt',help="theory prediction for coupling scan for vbfhh" )
parser.add_option("--gridConfig",default='/work/nchernya/DiHiggs/CMSSW_7_4_7/src/flashggFinalFit/MetaData_HHbbgg/cv_grids/cv_grid_finish.json',help="grid for coupling scan" )
parser.add_option("--gridCrossSection",default='/work/nchernya/DiHiggs/CMSSW_7_4_7/src/flashggFinalFit/MetaData_HHbbgg/cv_grids/vbfhhcvline_finish.txt',help="theory prediction for coupling  scan for vbfhh" )
parser.add_option("--vbfhhTheoryPrediction",default='/work/nchernya/DiHiggs/CMSSW_7_4_7/src/flashggFinalFit/MetaData_HHbbgg/cv_grids/vbfhhcvline_prediction.txt',help="theory prediction for coupling scan for vbfhh" )
#parser.add_option("--gridConfig",default='/work/nchernya/DiHiggs/CMSSW_7_4_7/src/flashggFinalFit/Plots/FinalResults/kl_grids/kl_grid.json',help="grid for coupling scan" )
#parser.add_option("--gridCrossSection",default='/work/nchernya/DiHiggs/CMSSW_7_4_7/src/flashggFinalFit/Plots/FinalResults/kl_grids/kl_grid_vbfhh.txt',help="theory prediction for couping scan for vbfhh" )
#parser.add_option("--vbfhhTheoryPrediction",default='/work/nchernya/DiHiggs/CMSSW_7_4_7/src/flashggFinalFit/Plots/FinalResults/kl_grids/kl_grid_vbfhh_prediction.txt',help="theory prediction for coupling scan for vbfhh" )
parser.add_option("--coupling",default='c2v',help="coupling to use for a limit : c2v,cv,kl" )
parser.add_option("--whatToFloat",default='r',help="what to float" )
parser.add_option("--indir", help="Input directory ")
parser.add_option("--outdir", help="Output directory ")
parser.add_option("--outtag", help="Output tag ")
parser.add_option("--unblind", action="store_true",help="Observed is present or not ",default=False)
parser.add_option("--nlo", action="store_true",help="NLO samples (need to normalize to cross section) ",default=False)
(options,args)=parser.parse_args()
###########
###CREATE TAGS

datalumi = "136.8 fb^{-1} (13 TeV)"
#datalumi = "59.4 fb^{-1} (13 TeV)"


c1 = ROOT.TCanvas("c1", "c1", 650, 500)
c1.SetFrameLineWidth(3)
c1.SetBottomMargin (0.15)
c1.SetRightMargin (0.05)
c1.SetLeftMargin (0.15)
c1.SetGridx()
c1.SetGridy()

mg = ROOT.TMultiGraph()


### signals are normalsed to 1fb already
scaleToXS = 1. # 
y_theo_scale = 31.05*0.58*0.00227*2  #new most updated x-sec
y_theo_scale_vbf = 1.726*0.58*0.00227*2  #new most updated x-sec
qqHH_NNLO_kfactor = 1.0347 #1.726/1.668 is sigma_NNLO+FTapprox / sigma_MG5 for SM 
BR_hhbbgg = 0.58*0.00227*2

gr2sigma = ROOT.TGraphAsymmErrors()
gr1sigma = ROOT.TGraphAsymmErrors()
grexp = ROOT.TGraph()
grobs = ROOT.TGraph()

ptsList = [] # (x, obs, exp, p2s, p1s, m1s, m2s)

coupling_xs = []
#Get XS predicted 
with open(options.gridCrossSection) as fobj:
	for line in fobj:
		row = line.split()
		coupling_xs.append(row)

### read the scan with normal width
coupling = options.coupling
coup_min =  0. 
coup_max = 0.
with open(options.gridConfig,"r") as rew_json:
  rew_dict = json.load(rew_json)
  coup_min = rew_dict['%smin'%coupling] 
  coup_max = rew_dict['%smax'%coupling] 
for icoup in range(0,rew_dict['N%s'%coupling]):
		coup = rew_dict['%smin'%coupling] + icoup*rew_dict["%sstep"%coupling]	
		coup_str = ("{:.6f}".format(coup)).replace('.','d').replace('-','m') 
		if coupling=='c2v' or coupling=='cv' : fname = options.indir + '/' + 'higgsCombine_%s_%s_%s.AsymptoticLimits.mH125.root'%(coupling,coup_str,options.outtag)
		if coupling =='kl' : fname = options.indir + '/' + 'higgsCombine_%s_%s_kt_1d000000_%s.AsymptoticLimits.mH125.root'%(coupling,coup_str,options.outtag)
		vals  = getVals(fname)
		if vals==-1 : continue
		if options.nlo :  
			xs = coupling_xs[icoup]
			if options.whatToFloat=='r' : 
				if coupling=='kl' : scaleToXS = eval_nnlo_xsec_ggF(coup)*BR_hhbbgg + float(xs[1])*1000.*BR_hhbbgg*qqHH_NNLO_kfactor 
				elif coupling=='c2v' or coupling=='cv' : scaleToXS = eval_nnlo_xsec_ggF(1.)*BR_hhbbgg + float(xs[1])*1000.*BR_hhbbgg*qqHH_NNLO_kfactor 
				#scaleToXS = eval_nnlo_xsec_ggF(1.)*BR_hhbbgg + float(xs[1])*1000.*BR_hhbbgg*qqHH_NNLO_kfactor 
			elif options.whatToFloat=='r_qqhh' : 
				#scaleToXS = float(xs[1])*1000.*BR_hhbbgg*qqHH_NNLO_kfactor 
				if coupling=='kl' : scaleToXS =  float(xs[1])*1000.*BR_hhbbgg*qqHH_NNLO_kfactor 
				elif coupling=='c2v' or coupling=='cv' : scaleToXS =  float(xs[1])*1000.*BR_hhbbgg*qqHH_NNLO_kfactor 
			elif options.whatToFloat=='r_gghh' : 
				if coupling=='kl' : scaleToXS = eval_nnlo_xsec_ggF(coup)*BR_hhbbgg  
				elif coupling=='c2v' or coupling=='cv' : scaleToXS = eval_nnlo_xsec_ggF(1.)*BR_hhbbgg 
		if not options.unblind : obs   = scaleToXS*0.0 ## FIXME
		else : obs   = scaleToXS*vals[5][1] 
		m2s_t = scaleToXS*vals[0][1]
		m1s_t = scaleToXS*vals[1][1]
		exp   = scaleToXS*vals[2][1]
		p1s_t = scaleToXS*vals[3][1]
		p2s_t = scaleToXS*vals[4][1]
	
		## because the other code wants +/ sigma vars as deviations, without sign, from the centeal exp value...
		p2s = p2s_t - exp
		p1s = p1s_t - exp
		m2s = exp - m2s_t
		m1s = exp - m1s_t
		xval = coup
	#	print xval,exp	
		ptsList.append((xval, obs, exp, p2s, p1s, m1s, m2s))

ptsList.sort()
exp_list = []
obs_list = []
xval_list = []
for ipt, pt in enumerate(ptsList):
	xval = pt[0]
	obs  = pt[1]
	exp  = pt[2]
	p2s  = pt[3]
	p1s  = pt[4]
	m1s  = pt[5]
	m2s  = pt[6]

	grexp.SetPoint(ipt, xval, exp)
	#print xval,exp
	exp_list.append(exp)
	obs_list.append(obs)
	xval_list.append(xval)
	grobs.SetPoint(ipt, xval, obs)
	gr1sigma.SetPoint(ipt, xval, exp)
	gr2sigma.SetPoint(ipt, xval, exp)
	gr1sigma.SetPointError(ipt, 0,0,m1s,p1s)
	gr2sigma.SetPointError(ipt, 0,0,m2s,p2s)

exp_inter = interp1d(xval_list, exp_list, kind='cubic')
obs_inter = interp1d(xval_list, obs_list, kind='cubic')

##############Create functions from median expected and observed
#def graph2func(xval):
#   return gr.Eval(x[0])

######## set styles
grexp.SetMarkerStyle(24)
grexp.SetMarkerColor(4)
grexp.SetMarkerSize(0.8)
grexp.SetLineColor(ROOT.kBlue+2)
grexp.SetLineWidth(3)
grexp.SetLineStyle(2)
grexp.SetFillColor(0)

grobs.SetLineColor(1)
grobs.SetLineWidth(3)
grobs.SetMarkerColor(1)
grobs.SetMarkerStyle(20)
grobs.SetFillStyle(0)

gr1sigma.SetMarkerStyle(0)
gr1sigma.SetMarkerColor(3)
# gr1sigma.SetFillColor(ROOT.TColor.GetColor(0, 220, 60))
# gr1sigma.SetLineColor(ROOT.TColor.GetColor(0, 220, 60))
gr1sigma.SetFillColor(ROOT.kGreen+1)
gr1sigma.SetLineColor(ROOT.kGreen+1)
gr1sigma.SetFillStyle(1001)

# gr2sigma.SetName(tooLopOn[ic])
gr2sigma.SetMarkerStyle(0)
gr2sigma.SetMarkerColor(5)
# gr2sigma.SetFillColor(ROOT.TColor.GetColor(254, 234, 0))
# gr2sigma.SetLineColor(ROOT.TColor.GetColor(254, 234, 0))
gr2sigma.SetFillColor(ROOT.kOrange)
gr2sigma.SetLineColor(ROOT.kOrange)
gr2sigma.SetFillStyle(1001)

mg.Add(gr2sigma, "3")
mg.Add(gr1sigma, "3")
mg.Add(grexp, "L")
mg.Add(grobs, "L")

###########
legend = ROOT.TLegend(0,0,0,0)

legend.SetX1(0.17284)
legend.SetY1(0.630526)
# legend.SetX2(0.5)
legend.SetX2(0.520062)
#legend.SetY2(0.88)
legend.SetY2(0.896)


legend.SetFillColor(ROOT.kWhite)
legend.SetBorderSize(0)
# legend
legend.SetHeader('95% CL upper limits')
if options.unblind : legend.AddEntry(grobs,"Observed","l")
legend.AddEntry(grexp, "Median expected", "l")
legend.AddEntry(gr1sigma, "68% expected", "f")
legend.AddEntry(gr2sigma, "95% expected", "f")

fakePlot3 = ROOT.TGraphAsymmErrors()
fakePlot3.SetFillColor(ROOT.kRed)
fakePlot3.SetFillStyle(3001)
fakePlot3.SetLineColor(ROOT.kRed)
fakePlot3.SetLineWidth(3)
legend.AddEntry(fakePlot3, "Theoretical prediction", "lf")


##### text
# pt = ROOT.TPaveText(0.1663218,0.886316,0.3045977,0.978947,"brNDC")
pt = ROOT.TPaveText(0.1663218-0.02,0.886316,0.3045977-0.02,0.978947,"brNDC")
pt.SetBorderSize(0)
pt.SetTextAlign(12)
pt.SetTextFont(62)
pt.SetTextSize(0.05)
pt.SetFillColor(0)
pt.SetFillStyle(0)
# pt.AddText("CMS #font[52]{preliminary}" )
pt.AddText("CMS" )
# pt.AddText("#font[52]{preliminary}")
pt2 = ROOT.TPaveText(0.79,0.9066667,0.8997773,0.957037,"brNDC")
pt2.SetBorderSize(0)
pt2.SetFillColor(0)
pt2.SetTextSize(0.040)
pt2.SetTextFont(42)
pt2.SetFillStyle(0)
pt2.AddText(datalumi)

//pt4 = ROOT.TPaveText(0.4819196+0.036,0.7780357+0.015+0.02,0.9008929+0.036,0.8675595+0.015,"brNDC")
pt4 = ROOT.TPaveText(0.4819196+0.036,0.7780357+0.015+0.02,0.9008929+0.036,0.896,"brNDC")
pt4.SetTextAlign(12)
pt4.SetFillColor(ROOT.kWhite)
pt4.SetFillStyle(1001)
pt4.SetTextFont(42)
pt4.SetTextSize(0.05)
pt4.SetBorderSize(0)
pt4.SetTextAlign(32)
# pt4.AddText("bb #mu_{}#tau_{h} + bb e#tau_{h} + bb #tau_{h}#tau_{h}") 
# pt4.AddText("bb #tau_{#mu}#tau_{h} + bb #tau_{e}#tau_{h} + bb #tau_{h}#tau_{h}") 
#pt4.AddText("HH #rightarrow bbbb") 
pt4.AddText("HH#rightarrow#gamma#gammab#bar{b}") 

# offs = 0.020
# height = 0.05
# pt5 = ROOT.TPaveText(0.4819196+0.036+0.10,0.7780357+0.015-offs,0.9008929+0.036,0.7780357+0.015-offs+height,"brNDC")
# pt5.SetTextAlign(12)
# pt5.SetFillColor(ROOT.kWhite)
# pt5.SetFillStyle(1001)
# pt5.SetTextFont(42)
# pt5.SetTextSize(0.05)
# pt5.SetBorderSize(0)
# pt5.SetTextAlign(32)
# # pt5.AddText("bb #mu_{}#tau_{h} + bb e#tau_{h} + bb #tau_{h}#tau_{h}") 
# # pt5.AddText("bb #tau_{#mu}#tau_{h} + bb #tau_{e}#tau_{h} + bb #tau_{h}#tau_{h}") 
# pt5.AddText("#scale[0.8]{Combined channels}")

# txt_kt1 = ROOT.TLatex(30.5, 590.3, "k_{t} = 1")
# txt_kt1.SetTextAngle(48)
# txt_kt1.SetTextAlign(31)
# txt_kt1.SetTextSize(0.03)
# txt_kt1.SetTextFont(42)
# txt_kt1.SetTextColor(ROOT.kRed+1) #kGray+3
# txt_kt1.Draw()

# txt_kt2 = ROOT.TLatex(12.3, 750, "k_{t} = 2")
# txt_kt2.SetTextAngle(80)
# txt_kt2.SetTextAlign(31)
# txt_kt2.SetTextSize(0.03)
# txt_kt2.SetTextFont(42)
# txt_kt2.SetTextColor(ROOT.kRed+2) #kGray+3
# txt_kt2.Draw()


# ###### theory lines
theory_line = []
exp_line=[]
xval_line=[]
xmin=-20.4
xmax=31.4
if coupling=='kl' :
	xmin=-20.
	xmax=20.
if coupling=='c2v':
	xmin=-5
	xmax=7
if coupling=='cv':
	xmin=-4
	xmax=4

graph = ROOT.TGraph(options.vbfhhTheoryPrediction)
ci = ROOT.TColor.GetColor("#ff0000")
graph.SetLineColor(ci)
graph.SetLineWidth(2)
for k in range (0,graph.GetN()): 
	if options.whatToFloat=='r' : 
		if coupling=='kl' : theory_value  = eval_nnlo_xsec_ggF(graph.GetX()[k])*BR_hhbbgg + graph.GetY()[k]*1000.*BR_hhbbgg*qqHH_NNLO_kfactor
		elif coupling=='c2v' or coupling=='cv' :theory_value  = eval_nnlo_xsec_ggF(1.)*BR_hhbbgg + graph.GetY()[k]*1000.*BR_hhbbgg*qqHH_NNLO_kfactor
		graph.GetY()[k] = theory_value
		if (graph.GetX()[k]>=coup_min) and (graph.GetX()[k]<=coup_max) : theory_line.append(theory_value) 
	elif options.whatToFloat=='r_qqhh' : 
		if coupling=='kl' : theory_value  =  graph.GetY()[k]*1000.*BR_hhbbgg*qqHH_NNLO_kfactor
		elif coupling=='c2v' or coupling=='cv'  :theory_value  = graph.GetY()[k]*1000.*BR_hhbbgg*qqHH_NNLO_kfactor 
		graph.GetY()[k] = theory_value
		if (graph.GetX()[k]>=coup_min) and (graph.GetX()[k]<=coup_max) : theory_line.append(theory_value) 
	elif options.whatToFloat=='r_gghh' : 
		if coupling=='kl' : theory_value  =  eval_nnlo_xsec_ggF(graph.GetX()[k])*BR_hhbbgg
		elif coupling=='c2v'  or coupling=='cv' :theory_value  =  eval_nnlo_xsec_ggF(1.)*BR_hhbbgg
		graph.GetY()[k] = theory_value
		if (graph.GetX()[k]>=coup_min) and (graph.GetX()[k]<=coup_max) : theory_line.append(theory_value) 
	if (graph.GetX()[k]>=coup_min) and (graph.GetX()[k]<=coup_max) : xval_line.append(graph.GetX()[k])


## myFunc =  ROOT.TF1("myFunc","(2.09*[0]*[0]*[0]*[0] + 0.28*[0]*[0]*x*[0]*x*[0] -1.37*[0]*[0]*[0]*x*[0])*2.44185/[1]",xmin,xmax);
#myFunc = ROOT.TF1 ("myFunc", functionGF_kl_wrap, xmin, xmax, 1)
#if options.nlo : 
#	myFunc = ROOT.TF1 ("myFunc", nnlo_xsec_ggF_kl_wrap, xmin, xmax, 1)
#	y_theo_scale = BR_hhbbgg# already scaled to cross section
#myFunc.SetParameter(0, y_theo_scale) ### norm scale
#graph = ROOT.TGraph(myFunc);
#ci = ROOT.TColor.GetColor("#ff0000");
#graph.SetLineColor(ci);
#graph.SetLineWidth(2);
## graph.Draw("l");
#divider = 1000.
#nP = int((kl_max-kl_min)*divider)
#Graph_syst_Scale =  ROOT.TGraphAsymmErrors(nP)
#for i in range(nP) : 
#	x = kl_min+(i*1.)/divider
#	Graph_syst_Scale_x=(kl_min+(i*1.)/divider)
#	if options.nlo : Graph_syst_Scale_y=nnlo_xsec_ggF_kl_wrap([x], [y_theo_scale])
#	else :Graph_syst_Scale_y=functionGF_kl_wrap([x], [y_theo_scale])
#	theory_line.append(Graph_syst_Scale_y)
#	xval_line.append(x)
#	Graph_syst_Scale_x_err=(0)
#	if options.nlo :  
#		Graph_syst_Scale_y_errup    = nnlo_xsec_ggF_kl_wrap([x], [y_theo_scale])*0.045
#		Graph_syst_Scale_y_errdown  = nnlo_xsec_ggF_kl_wrap([x], [y_theo_scale])*0.064
#	else :  
#		Graph_syst_Scale_y_errup    = functionGF_kl_wrap([x], [y_theo_scale])*0.045
#		Graph_syst_Scale_y_errdown  = functionGF_kl_wrap([x], [y_theo_scale])*0.064
#	Graph_syst_Scale.SetPoint(i,Graph_syst_Scale_x,Graph_syst_Scale_y)
#	Graph_syst_Scale.SetPointError(i,Graph_syst_Scale_x_err,Graph_syst_Scale_x_err,Graph_syst_Scale_y_errup,Graph_syst_Scale_y_errdown)
#Graph_syst_Scale.SetLineColor(ROOT.kRed)
#Graph_syst_Scale.SetFillColor(ROOT.kRed)
#Graph_syst_Scale.SetFillStyle(3001)

exp_line = exp_inter(xval_line)
obs_line = obs_inter(xval_line)


print 'Expected Median and theory xsec'
idx = np.argwhere(np.diff(np.sign(exp_line-theory_line ))).flatten()
print np.array(xval_line)[idx], np.array(theory_line)[idx],np.array(exp_line)[idx]
if options.unblind:
	print 'Observed :'
	idx = np.argwhere(np.diff(np.sign(obs_line-theory_line ))).flatten()
	print np.array(xval_line)[idx], np.array(theory_line)[idx],np.array(obs_line)[idx]




hframe = ROOT.TH1F('hframe', '', 100, xmin, xmax)
if options.whatToFloat=='r' or options.whatToFloat=='r_gghh'  :
	hframe.SetMinimum(0.0)
	hframe.SetMaximum(2.5)
	if coupling == 'kl' : hframe.SetMaximum(3.0)
if options.whatToFloat=='r_qqhh' :
	ROOT.gPad.SetLogy()
	hframe.SetMinimum(0.0005)
	hframe.SetMaximum(10000) 

hframe.GetYaxis().SetTitleSize(0.047)
hframe.GetXaxis().SetTitleSize(0.055)
hframe.GetYaxis().SetLabelSize(0.045)
hframe.GetXaxis().SetLabelSize(0.045)
hframe.GetXaxis().SetLabelOffset(0.012)
hframe.GetYaxis().SetTitleOffset(1.2)
hframe.GetXaxis().SetTitleOffset(1.1)

if options.whatToFloat=='r' : hframe.GetYaxis().SetTitle("95% CL on #sigma HH #times BR(HH#rightarrow#gamma#gammab#bar{b})  [fb]")
elif options.whatToFloat=='r_qqhh' : hframe.GetYaxis().SetTitle("95% CL on #sigma qqHH #times BR(HH#rightarrow#gamma#gammab#bar{b})  [fb]")
elif options.whatToFloat=='r_gghh' : hframe.GetYaxis().SetTitle("95% CL on #sigma ggHH #times BR(HH#rightarrow#gamma#gammab#bar{b})  [fb]")
#hframe.GetYaxis().SetTitle("95% CL on #sigma (gg#rightarrowHH) #times BR(HH#rightarrow#gamma#gammab#bar{b})  [fb]")
if coupling=='kl' : hframe.GetXaxis().SetTitle("#kappa_{#lambda}=#lambda_{HHH}/#lambda_{SM}")
if coupling=='c2v' : hframe.GetXaxis().SetTitle("c_{2V}")
if coupling=='cv' : hframe.GetXaxis().SetTitle("c_{V}")

hframe.SetStats(0)
ROOT.gPad.SetTicky()
hframe.Draw()

# mg.Draw("pmc plc same")
gr2sigma.Draw("3same")
gr1sigma.Draw("3same")
grexp.Draw("Lsame")
if options.unblind : grobs.Draw("Lsame")

graph.Draw("l same")
#Graph_syst_Scale.Draw("e3 same");

pt.Draw()
pt2.Draw()
#redrawBorder()
c1.Update()
c1.RedrawAxis("g")
legend.Draw()
pt4.Draw()
# pt5.Draw()
c1.Update()
# raw_input()

c1.Print('%s/%s_scan_%s_to_%s_test3.pdf'%(options.outdir,coupling,options.outtag,options.whatToFloat), 'pdf')


