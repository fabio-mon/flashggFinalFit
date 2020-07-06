#!/bin/python
import os,sys,copy,math
import json
from array import array
import ROOT as r
from optparse import OptionParser
from math import sqrt
from ROOT import gRandom, Double

#r.gStyle.SetPalette(1)
r.gStyle.SetOptStat(0)
r.gStyle.SetOptTitle(0)
r.gStyle.SetNumberContours(200)
r.gROOT.SetBatch(True)

def find_crossing(graph,value):
    crossing=[]
    Npoints = graph.GetN()
    graph.Sort()

    deltaNLL_values=graph.GetY()
    deltaNLL_values.SetSize(Npoints)
    a_deltaNLL = array('d',deltaNLL_values)  

    kl_values=graph.GetX()
    kl_values.SetSize(Npoints)  
    a_kl = array('d',kl_values) 

    x0=y0=x1=y1=0.
    x0=a_kl[0]
    y0=a_deltaNLL[0]
    for ipoint in range(1,Npoints):
        x1=a_kl[ipoint]
        y1=a_deltaNLL[ipoint]
#        print ipoint," ",x0," ",y0," ",x1," ",y1," "

        if((y0>value and y1<=value) or (y0<value and y1>=value)):
            x = (x1-x0)*(value-y0)/(y1-y0) + x0
            crossing.append(x)
#            print "found line crossing at ",x

        x0=x1
        y0=y1

    return crossing

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

    lumibox = r.TLatex  (0.9, 0.964+yoffset, "136.8 fb^{-1} (13 TeV)")
    lumibox.SetNDC()
    lumibox.SetTextAlign(31)
    lumibox.SetTextSize(extratextsize)
    lumibox.SetTextFont(lumitextfont)
    lumibox.SetTextColor(r.kBlack)

    # xpos  = 0.177
    xpos  = 0.137
    if cmstextinframe:
        ypos  = 0.94 ## inside the frame
    else:
        ypos  = 0.995  ## ouside the frame
    CMSbox = r.TLatex  (xpos, ypos+yoffset+0.01, "CMS")       
    CMSbox.SetNDC()
    CMSbox.SetTextSize(cmstextsize)
    CMSbox.SetTextFont(cmstextfont)
    CMSbox.SetTextColor(r.kBlack)
    CMSbox.SetTextAlign(13) ## inside the frame

    # simBox = r.TLatex  (xpos, ypos - 0.05+yoffset, "Simulation")
    simBox = r.TLatex  (xpos + 0.12, ypos+yoffset, "")
    simBox.SetNDC()
    simBox.SetTextSize(extratextsize)
    simBox.SetTextFont(extratextfont)
    simBox.SetTextColor(r.kBlack)
    simBox.SetTextAlign(13)

    channelLabel = r.TLatex  (0.6-0.05, 0.8, "HH #rightarrow #gamma#gammab#bar{b}")
    channelLabel.SetNDC()
    # channelLabel.SetTextAlign(31)
    channelLabel.SetTextSize(1.15*extratextsize)
    channelLabel.SetTextFont(lumitextfont)
    channelLabel.SetTextColor(r.kBlack)

    #channelLabel0 = r.TLatex  (0.6-0.05, 0.7, "Expected (#kappa_{#lambda} = 1)")
    channelLabel0 = r.TLatex  (0.2, 0.8, "Observed")
    channelLabel0.SetNDC()
    channelLabel0.SetTextSize(1.15*extratextsize)
    channelLabel0.SetTextFont(lumitextfont)
    channelLabel0.SetTextColor(r.kBlack)


    return [lumibox, CMSbox, simBox]#, channelLabel, channelLabel0]
    # lumibox.Draw()
    # CMSbox.Draw()
    # simBox.Draw()
    # channelLabel.Draw()


def fixemptybins(histo2D):
    print "in function fixemptybins" 
    xbinwidth = histo2D.GetXaxis().GetBinWidth(1)
    ybinwidth = histo2D.GetYaxis().GetBinWidth(1)
    for xbin in range(1,histo2D.GetXaxis().GetNbins()+1):
        x = histo2D.GetXaxis().GetBinCenter(xbin)
        for ybin in range(1,histo2D.GetYaxis().GetNbins()+1):
            y = histo2D.GetYaxis().GetBinCenter(ybin)
            ibin = histo2D.FindBin(x,y)
            if histo2D.GetBinEntries(ibin)==0:
                print "found empty bin at %f,%f"%(x,y)
                ibinxp1 = histo2D.FindBin(x+xbinwidth,y)
                ibinxm1 = histo2D.FindBin(x-xbinwidth,y)
                ibinyp1 = histo2D.FindBin(x,y+ybinwidth)
                ibinym1 = histo2D.FindBin(x,y-ybinwidth)
#                avg=0.
#                if histo2D.GetBinEntries(ibinxm1)!=0 and histo2D.GetBinEntries(ibinxp1)!=0 and histo2D.GetBinEntries(ibinym1)!=0 and histo2D.GetBinEntries(ibinyp1)!=0:
#                    avg = (histo2D.GetBinContent(ibinxm1)+histo2D.GetBinContent(ibinxp1)+histo2D.GetBinContent(ibinym1)+histo2D.GetBinContent(ibinyp1))/4.
 
                xavg=0.
                yavg=0.
                avg=0.
                if histo2D.GetBinEntries(ibinxm1)!=0 and histo2D.GetBinEntries(ibinxp1)!=0:
                    xavg = 0.5*(histo2D.GetBinContent(ibinxm1) + histo2D.GetBinContent(ibinxp1))
                if histo2D.GetBinEntries(ibinym1)!=0 and histo2D.GetBinEntries(ibinyp1)!=0:
                    yavg = 0.5*(histo2D.GetBinContent(ibinym1) + histo2D.GetBinContent(ibinyp1))
                if xavg!=0 and yavg!=0:
                    avg = 0.5*(xavg+yavg)
                elif xavg!=0:
                    avg = xavg
                elif yavg!=0:
                    avg = yavg
 
                if avg!=0:
                    histo2D.SetBinContent(ibin,avg)
                    histo2D.SetBinEntries(ibin,1)
                    print "fixed with value %f!"%avg
                else: 
                    print "can't fix this bin !!!"


parser = OptionParser()
parser.add_option("--infilename_2Dscan",               default="",         help="Input file(s) for 2D scan")
parser.add_option("--infilename_obs",                  default="",         help="Input file(s) with observed result")
parser.add_option("--infilename_exp",                  default="",         help="Input file(s) with expected result")
parser.add_option("--outdir",                          default="plots/", help="Output dir for plots")
parser.add_option("--Npoints_2Dscan",    type="int",   default=10000,      help="Number of points for 2D scan")
parser.add_option("--klmin",             type="float", default=-3.,         help="kl min")
parser.add_option("--klmax",             type="float", default=3.,         help="kl max")
parser.add_option("--ktmin",             type="float", default=-2.,         help="kt min")
parser.add_option("--ktmax",             type="float", default=2.,         help="kt max")
(options,args)=parser.parse_args()

klmin = options.klmin
klmax = options.klmax
ktmin = options.ktmin
ktmax = options.ktmax

outfile = r.TFile("%s/likelihood_scans.root"%options.outdir,"RECREATE")
outfile.cd()

if options.infilename_obs != "" :
    ''' compare observed with expected result '''
    c = r.TCanvas('c', 'c', 600, 600)
    c.SetFrameLineWidth(3)
    c.SetBottomMargin(0.13)
    c.SetLeftMargin(0.13)
    #c.SetRightMargin(0.13)
    c.SetGridx()    
    c.SetGridy()    

    obsfile = r.TFile(options.infilename_obs,"READ")
    contour68_obs = obsfile.Get("contour68")
    contour95_obs = obsfile.Get("contour95")
    Bestfit_obs   = obsfile.Get("Bestfit")

    SMpoint=r.TGraph()
    SMpoint.SetPoint(0,1.,1.)
    SMpoint.SetMarkerStyle(29)
    SMpoint.SetMarkerSize(2)
    SMpoint.SetMarkerColor(r.kGreen+2)
   
    SMprediction0 = r.TF1("SMprediction0","TMath::Sqrt([0]*x)",0.,klmax)
    SMprediction1 = r.TF1("SMprediction1","-TMath::Sqrt([0]*x)",0.,klmax)
    SMprediction0.SetParameters(1,1)
    SMprediction1.SetParameters(1,1)
    SMprediction0.SetNpx(10000)
    SMprediction1.SetNpx(10000)
    SMprediction0.SetLineColor(r.kGreen+2)
    SMprediction1.SetLineColor(r.kGreen+2)

 
    contour68_obs.SetLineColor(r.kBlue+1)
    contour68_obs.SetLineStyle(1)
    contour95_obs.SetLineColor(r.kBlue+1)
    contour95_obs.SetLineStyle(3)
    Bestfit_obs.SetMarkerColor(1)
    Bestfit_obs.SetMarkerStyle(33)

    
    #contour68_obs.GetXaxis().SetTitle("#kappa_{#lambda}")
    contour68_obs.GetXaxis().SetTitle("c_{2V}")
    contour68_obs.GetYaxis().SetTitle("c_{V}")
    contour68_obs.GetXaxis().SetTitleSize(0.05)
    contour68_obs.GetYaxis().SetTitleSize(0.05)
    contour68_obs.GetXaxis().SetTitleOffset(1.25)
    contour68_obs.GetYaxis().SetTitleOffset(1.25)

    legend_2D = r.TLegend(0.15,0.15,0.5,0.4)
    legend_2D.SetBorderSize(0)
    legend_2D.SetFillStyle(-1)
    legend_2D.SetTextFont(42)
    legend_2D.SetTextSize(0.03)
    legend_2D.AddEntry(SMpoint,"SM","P")
    legend_2D.AddEntry(SMprediction0,"SM c_{2V}=c_{V}^{2}","L")
    #legend_2D.AddEntry(Bestfit_obs,"Best fit HH cat.","P")
    legend_2D.AddEntry(contour68_obs,"68%C.L.","L")
    legend_2D.AddEntry(contour95_obs,"95%C.L.","L")
    
    contour68_obs.Draw("cont3")
    contour95_obs.Draw("cont3 SAME")
    SMpoint.Draw("P SAME")
    SMprediction0.Draw("L SAME")
    SMprediction1.Draw("L SAME")
    #Bestfit_obs.Draw("P SAME")

    legend_2D.Draw()
    et = extra_texts()
    for t in et: t.Draw()
    c.Print("%s/compare_2Dscan.pdf"%options.outdir)
    c.Print("%s/compare_2Dscan.png"%options.outdir)
    c.SaveAs("%s/compare_2Dscan.root"%options.outdir)



if options.infilename_2Dscan != "":
    c0 = r.TCanvas('c0', 'c0', 600, 600)
    c0.SetFrameLineWidth(3)
    c0.SetBottomMargin(0.13)
    c0.SetLeftMargin(0.13)
    c0.SetRightMargin(0.13)
    c0.SetFrameLineWidth(3)
    c0.SetBottomMargin(0.13)
    c0.SetLeftMargin(0.13)    
    c0.SetGridx()    
    c0.SetGridy()    
    inchain = r.TChain("limit","limit")
    for infilename in options.infilename_2Dscan.split(","):
        inchain.Add(infilename)
    Npoints = int(sqrt(options.Npoints_2Dscan))
    inchain.Draw("CV:C2V","quantileExpected == -1","P same")

    best_fit = r.TGraph(r.gROOT.FindObject("Graph"))
    best_fit.SetName("Bestfit")
    best_fit.SetTitle("Bestfit")
    best_fit.SetMarkerSize(2)
    best_fit.SetMarkerStyle(33)
    inchain.Draw("2*deltaNLL:CV:C2V>>likelihood_vs_kl_kt(%i,%f,%f,%i,%f,%f)"%(Npoints,klmin,klmax,Npoints,ktmin,ktmax),
                     "2*deltaNLL<50",
                     "prof colz goff")
    inchain.Draw("2*deltaNLL:CV:C2V>>likelihood_vs_kl_kt_contour(%i,%f,%f,%i,%f,%f)"%(Npoints,klmin,klmax,Npoints,ktmin,ktmax),
                     "",
                     "prof colz goff")

    likelihood_vs_kl_kt = r.TProfile2D(r.gDirectory.Get("likelihood_vs_kl_kt"))
    fixemptybins(likelihood_vs_kl_kt)
    likelihood_vs_kl_kt.GetYaxis().SetTitle("c_{V}")
    likelihood_vs_kl_kt.GetXaxis().SetTitle("c_{2V}")
    likelihood_vs_kl_kt.GetZaxis().SetTitle("-2#Deltaln(L)'")
    likelihood_vs_kl_kt.GetZaxis().SetRangeUser(0.,50.)
    ###################################################
    #likelihood_vs_kl_kt.GetYaxis().SetRangeUser(0.65,1.35)
    #likelihood_vs_kl_kt.GetXaxis().SetRangeUser(-10,15)
    ###################################################
    likelihood_vs_kl_kt.Draw("COLZ")

    likelihood_vs_kl_kt_contour = r.TProfile2D(r.gDirectory.Get("likelihood_vs_kl_kt_contour"))
    fixemptybins(likelihood_vs_kl_kt_contour)
    #draw 1 and 2 sigma contours
    contours =  array('d',[2.3,5.99])
    contour68 = array('d',[2.3])
    contour95 = array('d',[5.99])

    outfile.cd()
    best_fit.Write()

    outfile.cd()
    likelihood_vs_kl_kt_contour68 = r.TProfile2D(likelihood_vs_kl_kt_contour)
    likelihood_vs_kl_kt_contour68.SetName("contour68")
    likelihood_vs_kl_kt_contour68.SetTitle("contour68")
    likelihood_vs_kl_kt_contour68.SetContour(1,contour68);
    likelihood_vs_kl_kt_contour68.SetLineWidth(2);
    likelihood_vs_kl_kt_contour68.SetLineStyle(1);
    likelihood_vs_kl_kt_contour68.Write()

    outfile.cd()
    likelihood_vs_kl_kt_contour95 = r.TProfile2D(likelihood_vs_kl_kt_contour)
    likelihood_vs_kl_kt_contour95.SetName("contour95")
    likelihood_vs_kl_kt_contour95.SetTitle("contour95")
    likelihood_vs_kl_kt_contour95.SetContour(1,contour95);
    likelihood_vs_kl_kt_contour95.SetLineWidth(2);
    likelihood_vs_kl_kt_contour95.SetLineStyle(7);
    likelihood_vs_kl_kt_contour95.Write()

    likelihood_vs_kl_kt_contour.SetContour(2,contours);
    likelihood_vs_kl_kt_contour.SetLineColor(2);
    likelihood_vs_kl_kt_contour.SetLineWidth(2);
    likelihood_vs_kl_kt_contour.Draw("cont3 same");
    best_fit.Draw("p same")
    et = extra_texts()
    for t in et: t.Draw()

    box = r.TBox()
    box.SetFillStyle(1001)
    box.SetFillColor(16)
    box.SetLineColor(16)
    #box.DrawBox(klmin,ktmin,klmax,-1.35) 
    #box.DrawBox(klmin,-0.65,klmax,0.65)
    #box.DrawBox(klmin,1.35,klmax,ktmax)  
    #box.DrawBox(klmin+0.1,-2.1,klmax-0.1,-1.35) 
    #box.DrawBox(klmin+0.1,-0.65,klmax-0.1,0.65)
    #box.DrawBox(klmin+0.1,1.35,klmax-0.1,2.1)  

    c0.Print("%s/likelihood_2Dscan.pdf"%options.outdir)
    c0.Print("%s/likelihood_2Dscan.png"%options.outdir)
    c0.SaveAs("%s/likelihood_2Dscan_canvas.root"%options.outdir)
    outfile.cd()
    likelihood_vs_kl_kt.Write()

outfile.Close()
