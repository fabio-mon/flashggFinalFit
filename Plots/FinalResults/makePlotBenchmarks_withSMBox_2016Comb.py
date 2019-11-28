from ROOT import *
import collections 
from optparse import OptionParser

gROOT.SetBatch(kTRUE)

def setBarWidth(gr, bw, isX = True):
    for ipt in range(0, gr.GetN()):
        if isX:
            gr.SetPointEXhigh(ipt, bw)
            gr.SetPointEXlow(ipt, bw)
        else:
            gr.SetPointEYhigh(ipt, bw)
            gr.SetPointEYlow(ipt, bw)


def parseFile(filename):
    f = open(filename)
    res = collections.OrderedDict()
    for l in f:
        l = l.strip()
        if not l: continue
        if 'BENCH' in l: continue
        ## BENCH                  EXP                  OBS,              +2sigma,              +1sigma,              -1sigma,           -2sigma
        tokens = l.split()
        bn  = int(tokens[0])
        print '... parsing benchmark', bn
        exp = float(tokens[1])
        obs = float(tokens[2])
        p2s = float(tokens[3])
        p1s = float(tokens[4])
        m1s = float(tokens[5])
        m2s = float(tokens[6])

        res[bn] = (exp, obs, p2s, p1s, m1s, m2s)
    f.close()
    return res


parser = OptionParser()
parser.add_option("--indir", help="Input directory ")
parser.add_option("--outdir", help="Output directory ")
parser.add_option("--outtag", help="Output tag ")
parser.add_option("--blind", help="Observed is present or not ",default=True)

(options,args)=parser.parse_args()

values = parseFile('%s/benchmarks_limits_%s.txt'%(options.indir,options.outtag))
thelabsize = 0.045

agrObs    = TGraphAsymmErrors()
agrExp    = TGraphAsymmErrors()
agr1sigma = TGraphAsymmErrors()
agr2sigma = TGraphAsymmErrors()

for ipt in range(0, 14):  #13 = 12 nodes + 13th SM point +14th box
    bn = ipt + 1
    agrExp.    SetPoint(agrExp.GetN(),    bn, values[bn][0])
    agr1sigma. SetPoint(agr1sigma.GetN(), bn, values[bn][0])
    agr2sigma. SetPoint(agr2sigma.GetN(), bn, values[bn][0])
    agrObs.    SetPoint(agrObs.GetN(),    bn, values[bn][1])

    agr2sigma.SetPointEYhigh(agr1sigma.GetN()-1, abs(values[bn][2] - values[bn][0]))
    agr1sigma.SetPointEYhigh(agr2sigma.GetN()-1, abs(values[bn][3] - values[bn][0]))

    agr1sigma.SetPointEYlow(agr2sigma.GetN()-1, abs(values[bn][4] - values[bn][0]))
    agr2sigma.SetPointEYlow(agr1sigma.GetN()-1, abs(values[bn][5] - values[bn][0]))

# # agrExp.SetPoint(agrExp.GetN(), agrExp.GetN()+1, more_exp[i])
# # agr1sigma.SetPoint(agr1sigma.GetN(), agr1sigma.GetN()+1, more_exp[i])
# # agr2sigma.SetPoint(agr2sigma.GetN(), agr2sigma.GetN()+1, more_exp[i])
# # agrObs.SetPoint(agrObs.GetN(), agrObs.GetN()+1, more_obs[i])


setBarWidth(agr1sigma, 0.3)
setBarWidth(agr2sigma, 0.3)
setBarWidth(agrExp, 0.0)
setBarWidth(agrExp, 0.0, isX=False)
# setBarWidth(agrObs, 0.0)

## make the plot
c1 = TCanvas("cc", "cc", 650, 500)
c1.SetLogy()
c1.cd()
c1.SetFrameLineWidth(3)
c1.SetBottomMargin (0.15)
c1.SetRightMargin (0.05)
c1.SetLeftMargin (0.15)

agrExp.SetTitle("Expected CLs")
agrExp.SetMarkerStyle(24)
agrExp.SetMarkerColor(4)
agrExp.SetMarkerSize(0.8)
agrExp.SetLineColor(4)
agrExp.SetLineStyle(2)
agrExp.SetFillColor(0)

agr1sigma.SetTitle("Expected #pm 1#sigma")
agr1sigma.SetMarkerStyle(0)
agr1sigma.SetMarkerColor(3)
# agr1sigma.SetFillColor(TColor.GetColor(0, 220, 60))
# agr1sigma.SetLineColor(TColor.GetColor(0, 220, 60))
agr1sigma.SetFillColor(kGreen+1)
agr1sigma.SetLineColor(kGreen+1)
agr1sigma.SetFillStyle(1001)

# agr2sigma.SetName(channels[ic])
# agr2sigma.SetTitle("Expected #pm 2#sigma")
agr1sigma.SetMarkerStyle(0)
agr2sigma.SetMarkerColor(5)
agr2sigma.SetFillColor(TColor.GetColor(254, 234, 0))
agr2sigma.SetLineColor(TColor.GetColor(254, 234, 0))
agr2sigma.SetFillStyle(1001)

agr2sigma.GetYaxis().SetTitleSize(0.047)
agr2sigma.GetXaxis().SetTitleSize(0.055)
agr2sigma.GetYaxis().SetLabelSize(0.045)
# agr2sigma.GetXaxis().SetLabelSize(0.045) ## wil draw by hand...
agr2sigma.GetXaxis().SetLabelSize(0.0)
agr2sigma.GetXaxis().SetLabelOffset(0.012)
agr2sigma.GetYaxis().SetTitleOffset(1.15)
agr2sigma.GetXaxis().SetTitleOffset(1.1)
agr2sigma.SetFillColor(kOrange)
agr2sigma.SetLineColor(kOrange)

# agr2sigma.GetYaxis().SetRangeUser(0.01*scale,1000*scale)
# agr2sigma.GetYaxis().SetRangeUser(1.0,4000)
# agr2sigma.GetYaxis().SetRangeUser(1.0,2000)
# agr2sigma.GetYaxis().SetNdivisions(10)

# agr2sigma.GetXaxis().SetRangeUser(250,900)
# agr2sigma.GetYaxis().SetTitle("95% CL on #sigma #times #bf{#it{#Beta}}(HH#rightarrow bb#tau#tau) [fb]")
# agr2sigma.GetXaxis().SetTitle("Shape benchmark")

####### the frame
hframe = TH1F("hframe", ";Shape benchmark;95% CL on #sigma (gg#rightarrowHH) #times BR(HH#rightarrow#gamma#gammab#bar{b})  [fb]", 15, 0.01, 14.99)
hframe.SetStats(0)
# hframe.SetMinimum(1.0)
# hframe.SetMaximum(5000)
hframe.SetMinimum(0.01)
hframe.SetMaximum(30)
#hframe.GetYaxis().SetTitleSize(0.047)
hframe.GetYaxis().SetTitleSize(0.045)
hframe.GetXaxis().SetTitleSize(0.055)
hframe.GetYaxis().SetLabelSize(thelabsize)
# hframe.GetXaxis().SetLabelSize(0.045)
hframe.GetXaxis().SetLabelSize(0.00) # do by hand
hframe.GetXaxis().SetLabelOffset(0.012)
#hframe.GetYaxis().SetTitleOffset(1.15)
hframe.GetYaxis().SetTitleOffset(1.3)
hframe.GetXaxis().SetTitleOffset(1.1)

# hframe.GetXaxis().SetBinLabel(13, "a")
ttext_label = TLatex()
ttext_label.SetTextFont(42)
ttext_label.SetTextSize(thelabsize)
ttext_label.SetNDC(False)
# ttext_label.SetFillColor(kWhite)


agrExp.SetMarkerSize(1.3)

agrObs.SetMarkerStyle(8)
# agrObs.SetMarkerSize(0.8)
agrObs.SetMarkerSize(1.3)
agrObs.SetLineWidth(2)

hframe.GetYaxis().SetNdivisions(20)
hframe.GetXaxis().SetNdivisions(20)
hframe.Draw()
agr2sigma.Draw("E2same")
agr1sigma.Draw("E2SAME")
agrExp.Draw("PSAME")
if not options.blind:
    agrObs.Draw("PESAME")

######################

legend = TLegend()# cNice[ic].BuildLegend()
# legend.SetFillStyle(0)
# legend.SetLineColor(0)
legend.SetLineColor(kWhite)
legend.SetBorderSize(0)
# legend.SetX1(0.164)
# legend.SetY1(0.1992373-0.03)
# legend.SetX2(0.56)
# legend.SetY2(0.39-0.03)
# legend.SetX1(0.1825)
# legend.SetY1(0.17)
# legend.SetX2(0.4125)
# legend.SetY2(0.36)

# legend.SetX1(0.177469)
# legend.SetY1(0.183158)
# legend.SetX2(0.506173)
# legend.SetY2(0.421053)

# legend.SetX1(0.177469)
# legend.SetY1(0.183158)
# legend.SetX2(0.946173)
# legend.SetY2(0.331053)

legend.SetX1(0.179012)
legend.SetY1(0.187368)
legend.SetX2(0.689815)
legend.SetY2(0.334737)

legend.SetNColumns(2)
#legend.SetHeader('95% CL upper limits', 'c')
legend.SetHeader('95% CL upper limits')
if not options.blind : legend.AddEntry(agrObs, "Observed", "p")
legend.AddEntry(agr1sigma, "68% expected", "f")
legend.AddEntry(agrExp, "Median expected", "p")
legend.AddEntry(agr2sigma, "95% expected", "f")
c1.SetLogy()
c1.SetGridy(1)
c1.SetGridx(1)

# pt = TPaveText(0.1663218,0.7966102,0.3045977,0.8898305,"brNDC")
pt = TPaveText(0.1663218-0.02,0.886316,0.3045977-0.02,0.978947,"brNDC")
pt.SetBorderSize(0)
pt.SetTextAlign(12)
pt.SetTextFont(62)
pt.SetTextSize(0.05)
pt.SetFillColor(0)
pt.SetFillStyle(0)
#pt.AddText("CMS #font[52]{Supplementary}" )
pt.AddText("CMS #font[52]{Preliminary}" )

off1bis = 0.065
off1bisx = 0.015
pt1Bis = TPaveText(0.1663218-0.02+off1bisx,0.886316-off1bis,0.3045977-0.02+off1bisx,0.978947-off1bis,"brNDC")
pt1Bis.SetBorderSize(0)
pt1Bis.SetTextAlign(12)
pt1Bis.SetTextFont(42)
pt1Bis.SetTextSize(0.04)
pt1Bis.SetFillColor(kWhite)
pt1Bis.SetFillStyle(0)
#pt1Bis.AddText("arXiv:XXXX.XXXXX" )


# boxBand = TLegend(0.17284, 0.791579, 0.929012, 0.894737)
boxBand = TLegend(0.17284, 0.790, 0.929012, 0.894737)
boxBand.SetFillColor(kWhite)
boxBand.SetBorderSize(0)

# pt.AddText("#font[52]{preliminary}")
pt2 = TPaveText(0.79,0.9066667,0.8997773,0.957037,"brNDC")
pt2.SetBorderSize(0)
pt2.SetFillColor(0)
pt2.SetTextSize(0.040)
pt2.SetTextFont(42)
pt2.SetFillStyle(0)
#pt2.AddText("35.9 fb^{-1} (13 TeV)")
pt2.AddText("136.8 fb^{-1} (13 TeV)")

# pt4 = TPaveText(0.4819196,0.7780357+0.012,0.9008929,0.8675595+0.01+0.012,"brNDC")
# pt4 = TPaveText(0.4819196,0.67,0.9008929,0.77,"brNDC")
pt4 = TPaveText(0.534,0.79,0.93,0.88,"brNDC")
pt4.SetTextAlign(12)
pt4.SetFillColor(kWhite)
pt4.SetFillStyle(1001)
pt4.SetTextFont(42)
pt4.SetTextSize(0.05)
pt4.SetBorderSize(0)
pt4.SetTextAlign(32)
# pt4.AddText(channelsName[ic]) 
#pt4.AddText("HH combination") 
pt4.AddText("HH#rightarrow#gamma#gammab#bar{b}") 
# if ic == 3 : pt4.AddText("#scale[0.8]{Combined channels}")
pt.Draw()
pt2.Draw()
# pt4.Draw()

# c1.SetTickx()
c1.SetTicky()
c1.Update()
c1.RedrawAxis();
c1.Update()
c1.RedrawAxis("g");
legend.Draw()
c1.Update()
boxBand.Draw()
pt1Bis.Draw()

#ymin_labels = 0.13
ymin_labels = 0.006
for ival in range(0, 12):
    if ival < 9: ttext_label.DrawLatex(0.85+ival, ymin_labels, str(ival+1))
    else: ttext_label.DrawLatex(0.85+ival-0.15, ymin_labels, str(ival+1))
# ttext_label.DrawLatex(0.8+12-0.3, ymin_labels, 'k_{#lambda}=0')
# ttext_label.DrawLatex(0.8+13, ymin_labels, 'SM')
ttext_label.DrawLatex(0.8+12-0.2, ymin_labels, 'SM')
ttext_label.DrawLatex(0.8+13-0.1, ymin_labels, 'k_{#lambda}=0')

# ymin_labels = 0.01
# for ival in range(0, 12):
#     if ival < 9: ttext_label.DrawLatex(0.85+ival, ymin_labels, str(ival+1))
#     else: ttext_label.DrawLatex(0.85+ival-0.15, ymin_labels, str(ival+1))
# # ttext_label.DrawLatex(0.8+12-0.3, ymin_labels, 'k_{#lambda}=0')
# # ttext_label.DrawLatex(0.8+13, ymin_labels, 'SM')
# ttext_label.DrawLatex(0.8+12-0.2, ymin_labels, 'SM')
# ttext_label.DrawLatex(0.8+13-0.1, ymin_labels, 'k_{#lambda}=0')



pt4.Draw()
c1.Update()
raw_input()

c1.Print('%s/benchmark_plot_%s.pdf'%(options.outdir,options.outtag), 'pdf')

#### print a text table
print "%10s %20s %20s, %20s, %20s, %20s, %20s" % ("BENCH", "EXP" , "OBS", "+2sigma", "+1sigma", "-1sigma", "-2sigma")
for ipt in range(0, agrExp.GetN()):
    x_exp = Double(0.0)
    y_exp = Double(0.0)

    x_obs = Double(0.0)
    y_obs = Double(0.0)

    agrExp.GetPoint(ipt, x_exp, y_exp)
    agrObs.GetPoint(ipt, x_obs, y_obs)

    y_p2s = y_exp + agr2sigma.GetErrorYhigh(ipt)
    y_p1s = y_exp + agr1sigma.GetErrorYhigh(ipt)
    y_m1s = y_exp - agr1sigma.GetErrorYlow(ipt)
    y_m2s = y_exp - agr2sigma.GetErrorYlow(ipt)


    print "{: >10} {: >20} {: >20} {: >20} {: >20} {: >20} {: >20}".format (str(ipt), y_exp, y_obs, y_p2s, y_p1s, y_m1s, y_m2s)

