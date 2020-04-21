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

# def getExpValue( kl,  yt): 
#     BR =1 
#     return (2.09*yt*yt*yt*yt +   0.28*yt*yt*kl*kl  -1.37*yt*yt*yt*kl)*2.44477/BR;


# def parseFile(filename, CL='50.0', exp=True):
#     f = open(filename)
#     matches = []
#     for line in f:
#         s = ('Expected %s%%: r <'%CL)
#         if not exp: s = 'Observed Limit: r <'

#         if not s in line:
#             continue
#         val = line.replace(s, '')
#         val = float(val)
#         matches.append(val)

#     if len(matches) == 0:
#         print "did not find any expected in file: " , filename, 'CL=', CL, 'exp?=', exp
#         return -1.0
#     else:
#         return matches[-1]

def getVals(fname):
	fIn = ROOT.TFile.Open(fname)
  	vals = []
	if fIn :
		tIn = fIn.Get('limit')
		if tIn.GetEntries() < 5:
			print "*** WARNING: cannot parse file", fname, "because nentries != 5"
			raise RuntimeError('cannot parse file')
		for i in range(0, tIn.GetEntries()):
			tIn.GetEntry(i)
			qe = tIn.quantileExpected
			lim = tIn.limit
			vals.append((qe,lim))
	else :
		for qe in [0.025,0.16,0.5,0.84,0.975,0.]:
			vals.append((qe,2.))
	return vals

def functionGF(kl, kt, c2, cg, c2g):
	# unused this can be extended to 5D coefficients; currently c2, cg, c2g are unused
	# return ( A1*pow(kt,4) + A3*pow(kt,2)*pow(kl,2) + A7*kl*pow(kt,3) );
	## 13 TeV
	A = [2.09078, 10.1517, 0.282307, 0.101205, 1.33191, -8.51168, -1.37309, 2.82636, 1.45767, -4.91761, -0.675197, 1.86189, 0.321422, -0.836276, -0.568156]

	def pow (base, exp):
		return base**exp
	
	val = A[0]*pow(kt,4) + A[1]*pow(c2,2) + (A[2]*pow(kt,2) + A[3]*pow(cg,2))*pow(kl,2) + A[4]*pow(c2g,2) + ( A[5]*c2 + A[6]*kt*kl )*pow(kt,2) + (A[7]*kt*kl + A[8]*cg*kl )*c2 + A[9]*c2*c2g + (A[10]*cg*kl + A[11]*c2g)*pow(kt,2)+ (A[12]*kl*cg + A[13]*c2g )*kt*kl + A[14]*cg*c2g*kl
	return val

def functionGF_kl_wrap (x,par):
	return par[0]*functionGF(x[0], 1., 0, 0, 0)


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
parser.add_option("--hhReweightDir",default='/work/nchernya/DiHiggs/inputs/18_02_2020/categorizedTrees/kl_kt_finebinning//',help="hh reweighting directory with all txt files" )
parser.add_option("--indir", help="Input directory ")
parser.add_option("--outdir", help="Output directory ")
parser.add_option("--outtag", help="Output tag ")
parser.add_option("--unblind", action="store_true",help="Observed is present or not ",default=False)
parser.add_option("--nlo", action="store_true",help="NLO samples (need to normalize to cross section) ",default=False)
(options,args)=parser.parse_args()
###########
###CREATE TAGS

datalumi = "136.8 fb^{-1} (13 TeV)"


c1 = ROOT.TCanvas("c1", "c1", 650, 500)
c1.SetFrameLineWidth(3)
c1.SetBottomMargin (0.15)
c1.SetRightMargin (0.05)
c1.SetLeftMargin (0.15)
c1.SetGridx()
c1.SetGridy()

mg = ROOT.TMultiGraph()


### signals are normalsed to 1fb already
scaleToXS = 1. # in fb for limit in xs of HH -> bbbb
y_theo_scale = 31.05*0.58*0.00227*2  #new most updated x-sec
BR_hhbbgg = 0.58*0.00227*2

gr2sigma = ROOT.TGraphAsymmErrors()
gr1sigma = ROOT.TGraphAsymmErrors()
grexp = ROOT.TGraph()
grobs = ROOT.TGraph()

ptsList = [] # (x, obs, exp, p2s, p1s, m1s, m2s)

### read the scan with normal width
kl_min =  0. 
kl_max = 0.
with open(options.hhReweightDir+"config.json","r") as rew_json:
  rew_dict = json.load(rew_json)
  kl_min = rew_dict['klmin'] 
  kl_max = rew_dict['klmax'] 
for ikl in range(0,rew_dict['Nkl']):
	kl = rew_dict['klmin'] + ikl*rew_dict["klstep"]	
	kl_str = ("{:.6f}".format(kl)).replace('.','d').replace('-','m') 
	for ikt in range(0,rew_dict['Nkt']):
		kt = rew_dict['ktmin'] + ikt*rew_dict['ktstep']
		kt_str = ("{:.6f}".format(kt)).replace('.','d').replace('-','m') 

		fname = options.indir + '/' + 'higgsCombine_kl_%s_kt_%s_%s.AsymptoticLimits.mH125.root'%(kl_str,kt_str,options.outtag)
		#fname = options.indir + '/' + 'higgsCombine_kl_%s_kt_%s.Asymptotic.mH125.root'%(kl_str,kt_str)
		vals  = getVals(fname)
		if options.nlo :  scaleToXS = eval_nnlo_xsec_ggF(kl)*BR_hhbbgg
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
		xval = kl
	#	print xval,exp	
		ptsList.append((xval, obs, exp, p2s, p1s, m1s, m2s))

# ### read the scan with finer width for more precision in the 0-8 region
# lambdasfiner = [0.1*x for x in range(0, 80)] # I am removing doubly counted points
# lambdasfiner.append(8.0)
# # print lambdasfiner
# for ipt in range(0, len(lambdasfiner)):
#     fName = 'cards_Combined_2017_04_19_1Dmorepts_lmr70//ggHH_bbtt{0}MT2/out_Asym_ggHH_bbtt{0}_noTH.log'.format(ipt+99900) # were produced form 99900 --> 0.0 to 99980 --> 8.0
#     obs   = 1000.*parseFile(fName, exp=False)
#     exp   = 1000.*parseFile(fName)
#     m1s_t = 1000.*parseFile(fName, CL='16.0')
#     p1s_t = 1000.*parseFile(fName, CL='84.0')
#     m2s_t = 1000.*parseFile(fName, CL=' 2.5')
#     p2s_t = 1000.*parseFile(fName, CL='97.5')
#     ## because the other code wants +/ sigma vars as deviations, without sign, from the centeal exp value...
#     p2s = p2s_t - exp
#     p1s = p1s_t - exp
#     m2s = exp - m2s_t
#     m1s = exp - m1s_t
#     xval = lambdasfiner[ipt]

#     ptsList.append((xval, obs, exp, p2s, p1s, m1s, m2s))


# grexp.SetPoint(ipt, xval, exp)
# grobs.SetPoint(ipt, xval, obs)
# gr1sigma.SetPoint(ipt, xval, exp)
# gr2sigma.SetPoint(ipt, xval, exp)
# gr1sigma.SetPointError(ipt, 0,0,m1s,p1s)
# gr2sigma.SetPointError(ipt, 0,0,m2s,p2s)
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
# mg.SetMinimum(0)
# mg.SetMaximum(1000)
# mg.Draw("A pmc plc")

# mg.GetYaxis().SetTitleSize(0.047)
# mg.GetXaxis().SetTitleSize(0.055)
# mg.GetYaxis().SetLabelSize(0.045)
# mg.GetXaxis().SetLabelSize(0.045)
# mg.GetXaxis().SetLabelOffset(0.012)
# mg.GetYaxis().SetTitleOffset(1.2)
# mg.GetXaxis().SetTitleOffset(1.1)

# mg.GetYaxis().SetTitle("95% CL on #sigma #times #bf{#it{#Beta}}(HH#rightarrow bb#tau#tau) [fb]")
# mg.GetXaxis().SetTitle("k_{#lambda}/k_{t}")

###########
legend = ROOT.TLegend(0,0,0,0)
# legend.SetX1(0.17)
# legend.SetY1(0.69)
# legend.SetX2(0.466)
# legend.SetY2(0.362-0.171+0.69)          

legend.SetX1(0.17284)
legend.SetY1(0.630526)
# legend.SetX2(0.5)
legend.SetX2(0.520062)
legend.SetY2(0.88)


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

pt4 = ROOT.TPaveText(0.4819196+0.036,0.7780357+0.015+0.02,0.9008929+0.036,0.8675595+0.015,"brNDC")
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
# xmin=-20.4
# xmax=31.4
theory_line = []
exp_line=[]
xval_line=[]
xmin=-20.4
xmax=31.4
yt=1
BR = 1
# myFunc =  ROOT.TF1("myFunc","(2.09*[0]*[0]*[0]*[0] + 0.28*[0]*[0]*x*[0]*x*[0] -1.37*[0]*[0]*[0]*x*[0])*2.44185/[1]",xmin,xmax);
myFunc = ROOT.TF1 ("myFunc", functionGF_kl_wrap, xmin, xmax, 1)
if options.nlo : 
	myFunc = ROOT.TF1 ("myFunc", nnlo_xsec_ggF_kl_wrap, xmin, xmax, 1)
	y_theo_scale = BR_hhbbgg# already scaled to cross section
myFunc.SetParameter(0, y_theo_scale) ### norm scale
graph = ROOT.TGraph(myFunc);
ci = ROOT.TColor.GetColor("#ff0000");
graph.SetLineColor(ci);
graph.SetLineWidth(2);
# graph.Draw("l");
divider = 1000.
nP = int((kl_max-kl_min)*divider)
Graph_syst_Scale =  ROOT.TGraphAsymmErrors(nP)
for i in range(nP) : 
	x = kl_min+(i*1.)/divider
	Graph_syst_Scale_x=(kl_min+(i*1.)/divider)
	if options.nlo : Graph_syst_Scale_y=nnlo_xsec_ggF_kl_wrap([x], [y_theo_scale])
	else :Graph_syst_Scale_y=functionGF_kl_wrap([x], [y_theo_scale])
	theory_line.append(Graph_syst_Scale_y)
	xval_line.append(x)
	Graph_syst_Scale_x_err=(0)
	if options.nlo :  
		Graph_syst_Scale_y_errup    = nnlo_xsec_ggF_kl_wrap([x], [y_theo_scale])*0.045
		Graph_syst_Scale_y_errdown  = nnlo_xsec_ggF_kl_wrap([x], [y_theo_scale])*0.064
	else :  
		Graph_syst_Scale_y_errup    = functionGF_kl_wrap([x], [y_theo_scale])*0.045
		Graph_syst_Scale_y_errdown  = functionGF_kl_wrap([x], [y_theo_scale])*0.064
	Graph_syst_Scale.SetPoint(i,Graph_syst_Scale_x,Graph_syst_Scale_y)
	Graph_syst_Scale.SetPointError(i,Graph_syst_Scale_x_err,Graph_syst_Scale_x_err,Graph_syst_Scale_y_errup,Graph_syst_Scale_y_errdown)
Graph_syst_Scale.SetLineColor(ROOT.kRed)
Graph_syst_Scale.SetFillColor(ROOT.kRed)
Graph_syst_Scale.SetFillStyle(3001)
exp_line = exp_inter(xval_line)
obs_line = obs_inter(xval_line)

print 'Expected Median and theory xsec'
for ipt in range(0,grexp.GetN()):
   x = ROOT.Double(0)
   y = ROOT.Double(0)
   grexp.GetPoint(ipt, x, y)
idx = np.argwhere(np.diff(np.sign(exp_line-theory_line ))).flatten()
print np.array(xval_line)[idx], np.array(theory_line)[idx],np.array(exp_line)[idx]
print 'Observed :'
idx = np.argwhere(np.diff(np.sign(obs_line-theory_line ))).flatten()
print np.array(xval_line)[idx], np.array(theory_line)[idx],np.array(obs_line)[idx]

# ytbis = 2
# # Graph_syst_Scale2 =  ROOT.TGraphAsymmErrors(nP)
# Graph_syst_Scale2 =  ROOT.TGraphAsymmErrors()
# for i in range(nP) : 
#     # print Graph_syst_Scale2.GetN(), i
#     Graph_syst_Scale2_x=(xmin+(i*1.)/10.)
#     Graph_syst_Scale2_y=(getExpValue(2*(xmin+(i*1.)/10.),ytbis))
#     # if Graph_syst_Scale2_y > 800:
#     if Graph_syst_Scale2_x > 10.9 or Graph_syst_Scale2_x < -5.3:
#         continue
#     # print i
#     Graph_syst_Scale2_x_err=(0)
#     Graph_syst_Scale2_y_errup=(  (2.09*ytbis*ytbis*ytbis*ytbis+0.28*ytbis*ytbis*2*(xmin+(i*1.)/10.)*2*(xmin+(i*1.)/10.)-1.37*ytbis*ytbis*ytbis*2*(xmin+(i*1.)/10.))*2.44185*0.053/BR)
#     Graph_syst_Scale2_y_errdown=((2.09*ytbis*ytbis*ytbis*ytbis+0.28*ytbis*ytbis*2*(xmin+(i*1.)/10.)*2*(xmin+(i*1.)/10.)-1.37*ytbis*ytbis*ytbis*2*(xmin+(i*1.)/10.))*2.44185*0.067/BR)
#     Graph_syst_Scale2.SetPoint(Graph_syst_Scale2.GetN(),Graph_syst_Scale2_x,Graph_syst_Scale2_y)
#     Graph_syst_Scale2.SetPointError(Graph_syst_Scale2.GetN()-1,Graph_syst_Scale2_x_err,Graph_syst_Scale2_x_err,Graph_syst_Scale2_y_errup,Graph_syst_Scale2_y_errdown)
# Graph_syst_Scale2.SetLineColor(ROOT.kRed+2)
# Graph_syst_Scale2.SetFillColor(ROOT.kRed+2)
# Graph_syst_Scale2.SetFillStyle(3001)
# myFunc.SetParameter(0,ytbis); 
# myFunc.SetParameter(1,BR); 
# myFunc.SetNpx(200)
# graph2 = ROOT.TGraph(myFunc);
# for ipt in reversed(range(0, graph2.GetN())):
#     x = ROOT.Double(0)
#     y = ROOT.Double(0)
#     graph2.GetPoint(ipt, x, y)
#     if x >= 10.9 or x < -5.3    :
#         graph2.RemovePoint(ipt)

# graph2.SetLineColor(ROOT.kRed+1);
# graph2.SetLineWidth(2);


hframe = ROOT.TH1F('hframe', '', 100, -20, 20)
hframe.SetMinimum(0.0)
hframe.SetMaximum(3.)

hframe.GetYaxis().SetTitleSize(0.047)
hframe.GetXaxis().SetTitleSize(0.055)
hframe.GetYaxis().SetLabelSize(0.045)
hframe.GetXaxis().SetLabelSize(0.045)
hframe.GetXaxis().SetLabelOffset(0.012)
hframe.GetYaxis().SetTitleOffset(1.2)
hframe.GetXaxis().SetTitleOffset(1.1)

#hframe.GetYaxis().SetTitle("95% CL on #sigma #times #bf{#it{#Beta}}(HH#rightarrow bbbb) [fb]")
#hframe.GetYaxis().SetTitle("95% CL on #sigma_{ggF}(pp#rightarrowHH) [fb]")
hframe.GetYaxis().SetTitle("95% CL on #sigma (gg#rightarrowHH) #times BR(HH#rightarrow#gamma#gammab#bar{b})  [fb]")
hframe.GetXaxis().SetTitle("#kappa_{#lambda}=#lambda_{HHH}/#lambda_{SM}")

hframe.SetStats(0)
ROOT.gPad.SetTicky()
hframe.Draw()

# mg.Draw("pmc plc same")
gr2sigma.Draw("3same")
gr1sigma.Draw("3same")
grexp.Draw("Lsame")
grobs.Draw("Lsame")

graph.Draw("l same")
Graph_syst_Scale.Draw("e3 same");
# graph2.Draw("l same")
# Graph_syst_Scale2.Draw("e3 same");

pt.Draw()
pt2.Draw()
# pt4.Draw()
# txt_kt1.Draw()
# txt_kt2.Draw()
redrawBorder()
c1.Update()
c1.RedrawAxis("g")
legend.Draw()
pt4.Draw()
# pt5.Draw()
c1.Update()
# raw_input()

c1.Print('%s/klambda_scan_%s.pdf'%(options.outdir,options.outtag), 'pdf')


# smXS = 33.53*0.073
# for ipt in range(0, grobs.GetN()):
#     ptx = ROOT.Double(0.0)
#     pty = ROOT.Double(0.0)
#     grobs.GetPoint(ipt, x, y)
#     if x == 1.0:
#         print 'OBS LIMIT W.R.T. SM: ', y/(smXS), 'limit in fb:' , y


# for ipt in range(0, grexp.GetN()):
#     ptx = ROOT.Double(0.0)
#     pty = ROOT.Double(0.0)
#     grexp.GetPoint(ipt, x, y)
#     if x == 1.0:
#         print 'EXP LIMIT W.R.T. SM: ', y/(smXS), 'limit in fb:' , y

# if False:
#     print "OBS GRAPH"
#     grobs.Print()
#     print '\nEXP GRAPH'
#     grexp.Print()
#     print '\nEXP +2sigma'
#     gr2sigma.Print()
#     print '\nEXP +1sigma'
#     gr1sigma.Print()


# c1.Print("combined_klktscan_band.pdf", 'pdf')
# # for m in masses :
# #     fileLocation = "cards_"+channels[c]+"_"+folder+"/"+app+str(m)+catstring+"/higgsCombine"+app+str(m)+"_forLim_noTH.Asymptotic.mH"+str(m)+".root"
# #     if plotByCategory :
# #         fileLocation = "cards_Combined_"+folder+"/"+app+str(m)+tooLopOn[c]+"/higgsCombine"+app+str(m)+"_forLim_noTH.Asymptotic.mH"+str(m)+".root"
# #     if not os.path.isfile(fileLocation) : 
# #         print "FILE NOT FOUND: " , fileLocation
# #         continue
# #     if benchmark<0 : pointNumbers.append(m)
# #     fin = TFile.Open(fileLocation)
# #     tree = fin.Get("limit")
# #     if not tree :
# #         print "MALEDETTO TREE", fileLocation, fin, tree
# #         gAll.SetPoint(gAll.GetN(),m-offsetX,-1)
# #         g95[c].SetPoint(g95[c].GetN(),m-offsetX,-1)
# #         gObs.SetPoint(gObs.GetN(),m-offsetX,-1) 

# #         continue
# #     high=0
# #     low=0
# #     limit = 0
# #     obs = 0
# #     errX = 0.38
# #     if benchmark == 1 : 
# #         offsetX = -1
# #         errX = 0.15
# #     for entry in tree :
# #         if tree.quantileExpected < 0 :
# #             obs = tree.limit*scale
# #         elif tree.quantileExpected == 0.5 : 
# #             limit = tree.limit*scale
# #         elif tree.quantileExpected > 0.83 and tree.quantileExpected < 0.85 : 
# #             high = tree.limit*scale
# #         elif tree.quantileExpected > 0.15 and tree.quantileExpected < 0.17: 
# #             low = tree.limit*scale 
# #         elif tree.quantileExpected > 0.024 and tree.quantileExpected < 0.026 : 
# #             low95 = tree.limit*scale
# #         elif tree.quantileExpected > 0.974 and tree.quantileExpected < 0.976 : 
# #             high95 = tree.limit*scale

# #     if limit>0 : #and limit < 50 : 
# #         if m == 750 and limit > 900 :
# #             limit = limit/100
# #             obs = obs/100
# #             high = high/100
# #             high95=high95/100
# #             low = low/100
# #             low95=low95/100
# #         gAll.SetPoint(gAll.GetN(),m-offsetX,limit)
# #         gAll.SetPointError(gAll.GetN()-1,0+errX,0+errX,limit-low,high-limit)
# #         g95[c].SetPoint(g95[c].GetN(),m-offsetX,limit)
# #         g95[c].SetPointError(g95[c].GetN()-1,0+errX,0+errX,limit-low95,high95-limit)
# #         gObs.SetPoint(gObs.GetN(),m-offsetX,obs)    


# ##### print a YAML format for HepDATA
# print "\n\nHEP DATA - x variable"
# for ipt in range(0, grexp.GetN()):
#     x_exp = ROOT.Double(0.0)
#     y_exp = ROOT.Double(0.0)

#     x_obs = ROOT.Double(0.0)
#     y_obs = ROOT.Double(0.0)

#     grexp.GetPoint(ipt, x_exp, y_exp)
#     grobs.GetPoint(ipt, x_obs, y_obs)
#     ey_p2s = gr2sigma.GetErrorYhigh(ipt)
#     ey_p1s = gr1sigma.GetErrorYhigh(ipt)
#     ey_m1s = gr1sigma.GetErrorYlow(ipt)
#     ey_m2s = gr2sigma.GetErrorYlow(ipt)
#     print "- value: %f" % x_exp

# print "\n\nHEP DATA - exp"
# for ipt in range(0, grexp.GetN()):
#     x_exp = ROOT.Double(0.0)
#     y_exp = ROOT.Double(0.0)

#     x_obs = ROOT.Double(0.0)
#     y_obs = ROOT.Double(0.0)

#     grexp.GetPoint(ipt, x_exp, y_exp)
#     grobs.GetPoint(ipt, x_obs, y_obs)
#     ey_p2s = gr2sigma.GetErrorYhigh(ipt)
#     ey_p1s = gr1sigma.GetErrorYhigh(ipt)
#     ey_m1s = gr1sigma.GetErrorYlow(ipt)
#     ey_m2s = gr2sigma.GetErrorYlow(ipt)
#     print "- value: %f" % y_exp
#     print "  errors:"
#     print "  - asymerror: {minus: %f,  plus: %f,  label: '1 sigma'}" % (ey_m1s, ey_p1s)
#     print "  - asymerror: {minus: %f,  plus: %f,  label: '2 sigma'}" % (ey_m2s, ey_p2s)

# print "\n\nHEP DATA - obs"
# for ipt in range(0, grexp.GetN()):
#     x_exp = ROOT.Double(0.0)
#     y_exp = ROOT.Double(0.0)

#     x_obs = ROOT.Double(0.0)
#     y_obs = ROOT.Double(0.0)

#     grexp.GetPoint(ipt, x_exp, y_exp)
#     grobs.GetPoint(ipt, x_obs, y_obs)
#     ey_p2s = gr2sigma.GetErrorYhigh(ipt)
#     ey_p1s = gr1sigma.GetErrorYhigh(ipt)
#     ey_m1s = gr1sigma.GetErrorYlow(ipt)
#     ey_m2s = gr2sigma.GetErrorYlow(ipt)
#     print "- value: %f" % y_obs
