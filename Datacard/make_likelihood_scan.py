import ROOT
import numpy as np
from array import array

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



### a bit euristhic, but I notice that
### r is also saved in the output -> need to ask that it matches
### if the fit fails, the points *may* miss -> return None
def get_NLL(tree, r):
    dll = None
    for i in range (0, tree.GetEntries()):
        tree.GetEntry(i)
        if tree.mu_hh == r:
            dll = tree.deltaNLL
            break
    return dll


###
#inputDir = "/afs/cern.ch/user/f/fmonti/work/flashggFinalFit/CMSSW_7_4_7/src/flashggFinalFit/Datacard/cards/klscan_tthandhh/likelihood_out/"
inputDir = "/afs/cern.ch/user/f/fmonti/work/flashggFinalFit/CMSSW_7_4_7/src/flashggFinalFit/Datacard/cards/klscan_tthandhh_extended_fine/likelihood_out/"

Nkl   = 35
klmin = -6.25
klmax = 11.25
Nkt   = 21
ktmin = -2.1
ktmax =  2.1
'''
Nkl =   16
klmin = -5.5
klmax = 10.5
Nkt =    7
ktmin =  0.65
ktmax =  1.35
'''
deltaLL = {}
deltaLL_valid = {} ### just to get the minimum
goodfit = {}

# HH_kl_p_5d75

for ikl in range(0,Nkl):
    kl = klmin + (ikl+0.5)*(klmax-klmin)/Nkl
    deltaLL[kl] = {}
    deltaLL_valid[kl] = {}
    goodfit[kl] = {}
    for ikt in range(0,Nkt):
        kt = ktmin + (ikt+0.5)*(ktmax-ktmin)/Nkt;

        inputfilename_r0 = "%s/higgsCombinebbgg_result_r0_kl_%.3f_kt_%.3f.MultiDimFit.mH125.root"%(inputDir,kl,kt)
        inputfilename_r1 = "%s/higgsCombinebbgg_result_r1_kl_%.3f_kt_%.3f.MultiDimFit.mH125.root"%(inputDir,kl,kt)

        rootfile_r0 = ROOT.TFile.Open(inputfilename_r0)
        rootfile_r1 = ROOT.TFile.Open(inputfilename_r1)

        tree_r0 = rootfile_r0.Get('limit')
        tree_r1 = rootfile_r1.Get('limit')

        if(tree_r0==None or tree_r1==None):
            print "error file "+inputfilename_r0+" or "+inputfilename_r1+" are empty or do not exist"
            continue
        

        #tree_r0.GetEntry(1) ## for some reason, entry 0 is for r = 20
        #tree_r1.GetEntry(1) ## for some reason, entry 0 is for r = 20
        #dll_r0 = tree_r0.deltaNLL
        #dll_r1 = tree_r1.deltaNLL

        dll_r0 = get_NLL(tree_r0, 0)
        dll_r1 = get_NLL(tree_r1, 1)

        if not dll_r0 or not dll_r1:
            print "*** point ", kl, ' has an invalid fit, r=0 -> ', dll_r0, 'r=1 -> ', dll_r1, ' ... skipping'
            print "    >>> file r0 is "+inputfilename_r0
            print "    >>> file r1 is "+inputfilename_r1
            deltaLL[kl][kt] = None
            goodfit[kl][kt] = False
        else:
            dll = dll_r1 - dll_r0
            deltaLL[kl][kt] = dll
            goodfit[kl][kt] = True
            deltaLL_valid[kl][kt] = dll

### find the global minimun and scale everything
deltaLL_valid1D = {}
for ikl in range(0,Nkl):
    kl = klmin + (ikl+0.5)*(klmax-klmin)/Nkl
    deltaLL_valid1D [kl] = deltaLL_valid [kl] [1.]

deltaLL_valid1D_kt = {}
for ikt in range(0,Nkt):
    kt = ktmin + (ikt+0.5)*(ktmax-ktmin)/Nkt
    deltaLL_valid1D_kt [kt] = deltaLL_valid [1.] [kt]

print deltaLL_valid1D_kt

mmin2D = 999.
mmin1D = 999.
mmin1D_kt = 999.

for ikt in range(0,Nkt):
    kt = ktmin + (ikt+0.5)*(ktmax-ktmin)/Nkt;
    if(ikt==0):         mmin1D_kt = deltaLL_valid1D_kt[kt]
    else:               mmin1D_kt = min(mmin1D_kt,deltaLL_valid1D_kt [kt])

for ikl in range(0,Nkl):
    kl = klmin + (ikl+0.5)*(klmax-klmin)/Nkl
    if(ikl==0):         mmin1D = deltaLL_valid1D[kl]
    else:               mmin1D = min(mmin1D,deltaLL_valid1D[kl])
    for ikt in range(0,Nkt):
        kt = ktmin + (ikt+0.5)*(ktmax-ktmin)/Nkt;
        if(ikl==0 and ikt==0): mmin2D=deltaLL_valid[kl][kt]
        else:                  mmin2D = min(mmin2D,deltaLL_valid[kl][kt])

for ikt in range(0,Nkt):
    kt = ktmin + (ikt+0.5)*(ktmax-ktmin)/Nkt;
    deltaLL_valid1D_kt[kt] = 2*(deltaLL_valid1D_kt[kt]-mmin1D_kt)

print 
print deltaLL_valid1D_kt

for ikl in range(0,Nkl):
    kl = klmin + (ikl+0.5)*(klmax-klmin)/Nkl
    deltaLL_valid1D[kl] = 2*(deltaLL_valid1D[kl]-mmin1D)
    for ikt in range(0,Nkt):
        kt = ktmin + (ikt+0.5)*(ktmax-ktmin)/Nkt;
        deltaLL_valid[kl][kt] = 2*(deltaLL_valid[kl][kt]-mmin2D)

gr2D = ROOT.TH2F("deltaLL 2D scan","deltaLL 2D scan",Nkl,klmin,klmax,Nkt,ktmin,ktmax)
gr = ROOT.TGraph()
gr_kt = ROOT.TGraph()

for ikt in range(0,Nkt):
    kt = ktmin + (ikt+0.5)*(ktmax-ktmin)/Nkt;
    if goodfit[1.][kt]:
        print "setting point "+str(gr_kt.GetN())+" "+str(kt)+" "+str(deltaLL_valid1D_kt[kt])
        gr_kt.SetPoint(gr_kt.GetN(), kt,deltaLL_valid1D_kt[kt])

for ikl in range(0,Nkl):
    kl = klmin + (ikl+0.5)*(klmax-klmin)/Nkl
    if goodfit[kl][1.]:     gr.SetPoint(gr.GetN(), kl, deltaLL_valid1D[kl])    
    for ikt in range(0,Nkt):
        kt = ktmin + (ikt+0.5)*(ktmax-ktmin)/Nkt;
        #print "doing point (kl,kt)=(%.3f,%.3f)"%(kl, kt) 
        if goodfit[kl][kt]: gr2D.SetBinContent(gr2D.FindBin(kl,kt), deltaLL_valid[kl][kt])


gr_kt.SetMarkerStyle(8)
gr_kt.SetMarkerSize(0.8)

gr.SetMarkerStyle(8)
gr.SetMarkerSize(0.8)

### now make the plot
c0 = ROOT.TCanvas('c0', 'c0', 600, 600)
c0.SetFrameLineWidth(3)
c0.SetBottomMargin(0.13)
c0.SetLeftMargin(0.13)
c0.SetRightMargin(0.13)
c0.SetFrameLineWidth(3)
c0.SetBottomMargin(0.13)
c0.SetLeftMargin(0.13)    
gr2D.GetXaxis().SetTitle("k_{#lambda}")
gr2D.GetYaxis().SetTitle("k_{t}")
gr2D.GetZaxis().SetTitle("-2#Deltaln(L)'")
gr2D.DrawCopy("COLZ")
#draw 1 and 2 sigma contours
contours = array('d',[2.3,5.99])
gr2D.SetContour(2,contours);
gr2D.SetLineColor(2);
gr2D.SetLineWidth(2);
gr2D.Draw("cont3 same");
c0.Print("%s/klambda_kt_scan.pdf"%inputDir)
c0.Print("%s/klambda_kt_scan.png"%inputDir)

c1 = ROOT.TCanvas('c1', 'c1', 600, 600)
c1.SetFrameLineWidth(3)
c1.SetBottomMargin(0.13)
c1.SetLeftMargin(0.13)

xmin = -6
xmax = 11
ymax = 10
frame = ROOT.TH1D('frame', ';k_{#lambda};-2#Deltaln(L)', 100, xmin, xmax)
frame.SetMinimum(0)
frame.SetMaximum(ymax)
frame.GetXaxis().SetTitleSize(0.05)
frame.GetYaxis().SetTitleSize(0.05)
frame.GetXaxis().SetTitleOffset(1.25)
frame.GetYaxis().SetTitleOffset(1.25)
frame.Draw()
gr.Draw('PLsame')


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
legend.AddEntry(gr,"Combined","L")
legend.Draw("same")

c1.Print('%s/klambda_scan.png'%inputDir)
c1.Print('%s/klambda_scan.png'%inputDir)


c2 = ROOT.TCanvas('c2', 'c2', 600, 600)
#c2.SetFrameLineWidth(3)
#c2.SetBottomMargin(0.13)
#c2.SetLeftMargin(0.13)

xmin = -0.65
xmax = 1.35
ymax = 10
#frame_kt = ROOT.TH1D('frame_kt', ';k_{t};-2#Deltaln(L)', 100, xmin, xmax)
#frame_kt.SetMinimum(0)
#Frame_kt.SetMaximum(ymax)
#frame_kt.GetXaxis().SetTitleSize(0.05)
#frame_kt.GetYaxis().SetTitleSize(0.05)
#frame_kt.GetXaxis().SetTitleOffset(1.25)
#frame_kt.GetYaxis().SetTitleOffset(1.25)
#frame_kt.Draw()
gr_kt.Draw('PLsame')


### lines
#sigmas = [1,1.96]
#CL = [68,95]
#lines = []
#for s in sigmas:
#    l = ROOT.TLine(xmin, s*s, xmax, s*s)
#    l.SetLineStyle(7)
#    l.SetLineWidth(1)
#    l.SetLineColor(ROOT.kGray+2)
#    lines.append(l)
#for l in lines: l.Draw()

#et = extra_texts()
#for t in et: t.Draw()

c2.Print('%s/kt_scan.png'%inputDir)
c2.Print('%s/kt_scan.png'%inputDir)
