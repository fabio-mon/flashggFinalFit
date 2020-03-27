#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <map>

#include "boost/program_options.hpp"
#include "boost/lexical_cast.hpp"

#include "TFile.h"
#include "TMath.h"
#include "TLegend.h"
#include "TCanvas.h"
#include "RooPlot.h"
#include "RooWorkspace.h"
#include "RooDataSet.h"
#include "RooHist.h"
#include "RooAbsData.h"
#include "RooAbsPdf.h"
#include "RooArgSet.h"
#include "RooFitResult.h"
#include "RooMinuit.h"
#include "RooMinimizer.h"
#include "RooMsgService.h"
#include "RooDataHist.h"
#include "RooExtendPdf.h"
#include "RooProdPdf.h"
#include "TRandom3.h"
#include "TLatex.h"
#include "TMacro.h"
#include "TH1F.h"
#include "TH1I.h"
#include "TArrow.h"
#include "TKey.h"

#include "RooCategory.h"
#include "HiggsAnalysis/CombinedLimit/interface/RooMultiPdf.h"

#include "../interface/PdfModelBuilder.h"
#include <Math/PdfFuncMathCore.h>
#include <Math/ProbFunc.h>
#include <iomanip>
#include "boost/program_options.hpp"
#include "boost/algorithm/string/split.hpp"
#include "boost/algorithm/string/classification.hpp"
#include "boost/algorithm/string/predicate.hpp"

#include "../../tdrStyle/tdrstyle.C"
#include "../../tdrStyle/CMS_lumi.C"

using namespace std;
using namespace RooFit;
using namespace boost;

namespace po = program_options;

bool BLIND = false;
bool runFtestCheckWithToys=false;
int mgg_low =100;
int mgg_high =180;
//int mjj_low =70;
int mjj_low =90;
int mjj_high =190;
//int nBinsForMass = 4*(mgg_high-mgg_low);
int nBinsForMass = mgg_high-mgg_low;
//int nBinsForMass2 = (mjj_high-mjj_low);
int nBinsForMass2 = (mjj_high-mjj_low)/4.;

RooRealVar *intLumi_ = new RooRealVar("IntLumi","hacked int lumi", 1000.);

TRandom3 *RandomGen = new TRandom3();

RooAbsPdf* getPdf(PdfModelBuilder &pdfsModel, string type, int order, const char* ext=""){

  if (type=="Bernstein") return pdfsModel.getBernstein(Form("%s_bern%d",ext,order),order);
  else if (type=="Chebychev") return pdfsModel.getChebychev(Form("%s_cheb%d",ext,order),order);
  else if (type=="Exponential") return pdfsModel.getExponentialSingle(Form("%s_exp%d",ext,order),order);
  else if (type=="PowerLaw") return pdfsModel.getPowerLawSingle(Form("%s_pow%d",ext,order),order);
  else if (type=="Laurent") return pdfsModel.getLaurentSeries(Form("%s_lau%d",ext,order),order);
  else {
    cerr << "[ERROR] -- getPdf() -- type " << type << " not recognised." << endl;
    return NULL;
  }
}

void runFit(RooAbsPdf *pdf, RooDataSet *data, double *NLL, int *stat_t, int MaxTries){

  int ntries=0;
  RooArgSet *params_test = pdf->getParameters((const RooArgSet*)(0));
  //params_test->Print("v");
  int stat=1;
  double minnll=10e8;
  while (stat!=0){
    if (ntries>=MaxTries) break;
    RooFitResult *fitTest = pdf->fitTo(*data,RooFit::Save(1)
				       ,RooFit::Minimizer("Minuit2","minimize"),RooFit::SumW2Error(kTRUE)); //FIXME
    stat = fitTest->status();
    minnll = fitTest->minNll();
    if (stat!=0) params_test->assignValueOnly(fitTest->randomizePars());
    ntries++;
  }
  *stat_t = stat;
  *NLL = minnll;
}
double getProbabilityFtest(double chi2, int ndof,RooAbsPdf *pdfNull, RooAbsPdf *pdfTest, RooRealVar *mass, RooDataSet *data, std::string name){

  double prob_asym = TMath::Prob(chi2,ndof);
  if (!runFtestCheckWithToys) return prob_asym;

  int ndata = data->sumEntries();

  // fit the pdfs to the data and keep this fit Result (for randomizing)
  RooFitResult *fitNullData = pdfNull->fitTo(*data,RooFit::Save(1),RooFit::Strategy(1)
					     ,RooFit::Minimizer("Minuit2","minimize"),RooFit::SumW2Error(kTRUE),RooFit::PrintLevel(-1)); //FIXME
  RooFitResult *fitTestData = pdfTest->fitTo(*data,RooFit::Save(1),RooFit::Strategy(1)
					     ,RooFit::Minimizer("Minuit2","minimize"),RooFit::SumW2Error(kTRUE),RooFit::PrintLevel(-1)); //FIXME

  // Ok we want to check the distribution in toys then
  // Step 1, cache the parameters of each pdf so as not to upset anything
  RooArgSet *params_null = pdfNull->getParameters((const RooArgSet*)(0));
  RooArgSet preParams_null;
  params_null->snapshot(preParams_null);
  RooArgSet *params_test = pdfTest->getParameters((const RooArgSet*)(0));
  RooArgSet preParams_test;
  params_test->snapshot(preParams_test);

  int ntoys =5000;
  TCanvas *can = new TCanvas();
  can->SetLogy();
  TH1F toyhist(Form("toys_fTest_%s.pdf",pdfNull->GetName()),";Chi2;",60,-2,10);
  TH1I toyhistStatN(Form("Status_%s.pdf",pdfNull->GetName()),";FitStatus;",8,-4,4);
  TH1I toyhistStatT(Form("Status_%s.pdf",pdfTest->GetName()),";FitStatus;",8,-4,4);

  TGraph *gChi2 = new TGraph();
  gChi2->SetLineColor(kGreen+2);
  double w = toyhist.GetBinWidth(1);

  int ipoint=0;

  for (int b=0;b<toyhist.GetNbinsX();b++){
    double x = toyhist.GetBinCenter(b+1);
    if (x>0){
      gChi2->SetPoint(ipoint,x,(ROOT::Math::chisquared_pdf(x,ndof)));
      ipoint++;
    }
  }
  int npass =0; int nsuccesst =0;
  mass->setBins(nBinsForMass);
  for (int itoy = 0 ; itoy < ntoys ; itoy++){

    params_null->assignValueOnly(preParams_null);
    params_test->assignValueOnly(preParams_test);
    RooDataHist *binnedtoy = pdfNull->generateBinned(RooArgSet(*mass),ndata,0,1);

    int stat_n=1;
    int stat_t=1;
    int ntries = 0;
    double nllNull,nllTest;
    // Iterate on the fit
    int MaxTries = 2;
    while (stat_n!=0){
      if (ntries>=MaxTries) break;
      RooFitResult *fitNull = pdfNull->fitTo(*binnedtoy,RooFit::Save(1),RooFit::Strategy(1),RooFit::SumW2Error(kTRUE) //FIXME
					     ,RooFit::Minimizer("Minuit2","minimize"),RooFit::Minos(0),RooFit::Hesse(0),RooFit::PrintLevel(-1));
      //,RooFit::Optimize(0));

      nllNull = fitNull->minNll();
      stat_n = fitNull->status();
      if (stat_n!=0) params_null->assignValueOnly(fitNullData->randomizePars());
      ntries++;
    }

    ntries = 0;
    while (stat_t!=0){
      if (ntries>=MaxTries) break;
      RooFitResult *fitTest = pdfTest->fitTo(*binnedtoy,RooFit::Save(1),RooFit::Strategy(1),RooFit::SumW2Error(kTRUE) //FIXME
					     ,RooFit::Minimizer("Minuit2","minimize"),RooFit::Minos(0),RooFit::Hesse(0),RooFit::PrintLevel(-1));
      nllTest = fitTest->minNll();
      stat_t = fitTest->status();
      if (stat_t!=0) params_test->assignValueOnly(fitTestData->randomizePars());
      ntries++;
    }

    toyhistStatN.Fill(stat_n);
    toyhistStatT.Fill(stat_t);

    if (stat_t !=0 || stat_n !=0) continue;
    nsuccesst++;
    double chi2_t = 2*(nllNull-nllTest);
    if (chi2_t >= chi2) npass++;
    toyhist.Fill(chi2_t);
  }

  double prob=0;
  if (nsuccesst!=0)  prob = (double)npass / nsuccesst;
  toyhist.Scale(1./(w*toyhist.Integral()));
  toyhist.Draw();
  TArrow lData(chi2,toyhist.GetMaximum(),chi2,0);
  lData.SetLineWidth(2);
  lData.Draw();
  gChi2->Draw("L");
  TLatex *lat = new TLatex();
  lat->SetNDC();
  lat->SetTextFont(42);
  lat->DrawLatex(0.1,0.91,Form("Prob (asymptotic) = %.4f (%.4f)",prob,prob_asym));
  can->SaveAs(name.c_str());

  TCanvas *stas =new TCanvas();
  toyhistStatN.SetLineColor(2);
  toyhistStatT.SetLineColor(1);
  TLegend *leg = new TLegend(0.2,0.6,0.4,0.87); leg->SetFillColor(0);
  leg->SetTextFont(42);
  leg->AddEntry(&toyhistStatN,"Null Hyp","L");
  leg->AddEntry(&toyhistStatT,"Test Hyp","L");
  toyhistStatN.Draw();
  toyhistStatT.Draw("same");
  leg->Draw();
  stas->SaveAs(Form("%s_fitstatus.pdf",name.c_str()));
  //reassign params
  params_null->assignValueOnly(preParams_null);
  params_test->assignValueOnly(preParams_test);

  delete can; delete stas;
  delete gChi2;
  delete leg;
  delete lat;

  // Still return the asymptotic prob (usually its close to the toys one)
  return prob_asym;

}

double getGoodnessOfFit(RooRealVar *mass, RooAbsPdf *mpdf, RooDataSet *data, std::string name){

  double prob;
  int ntoys = 500;
  // Routine to calculate the goodness of fit.
  name+="_gofTest.pdf";
  RooRealVar norm("norm","norm",data->sumEntries(),0,10E6);
  //norm.removeRange();

  RooExtendPdf *pdf = new RooExtendPdf("ext","ext",*mpdf,norm);

  // get The Chi2 value from the data
  RooPlot *plot_chi2 = mass->frame();
  data->plotOn(plot_chi2,Binning(nBinsForMass),Name("data"));

  pdf->plotOn(plot_chi2,Name("pdf"));
  int np = pdf->getParameters(*data)->getSize();

  double chi2 = plot_chi2->chiSquare("pdf","data",np);
  std::cout << "[INFO] Calculating GOF for pdf " << pdf->GetName() << ", using " <<np << " fitted parameters" <<std::endl;

  // The first thing is to check if the number of entries in any bin is < 5
  // if so, we don't rely on asymptotic approximations

  if ((double)data->sumEntries()/nBinsForMass < 5 ){

    std::cout << "[INFO] Running toys for GOF test " << std::endl;
    // store pre-fit params
    RooArgSet *params = pdf->getParameters(*data);
    RooArgSet preParams;
    params->snapshot(preParams);
    int ndata = data->sumEntries();

    int npass =0;
    std::vector<double> toy_chi2;
    for (int itoy = 0 ; itoy < ntoys ; itoy++){
      //  std::cout << "[INFO] " <<Form("\t.. %.1f %% complete\r",100*float(itoy)/ntoys) << std::flush;
      params->assignValueOnly(preParams);
      int nToyEvents = RandomGen->Poisson(ndata);
      RooDataHist *binnedtoy = pdf->generateBinned(RooArgSet(*mass),nToyEvents,0,1);
      pdf->fitTo(*binnedtoy,RooFit::Minimizer("Minuit2","minimize"),RooFit::Minos(0),RooFit::Hesse(0),RooFit::PrintLevel(-1),RooFit::Strategy(0),RooFit::SumW2Error(kTRUE)); //FIXME

      RooPlot *plot_t = mass->frame();
      binnedtoy->plotOn(plot_t);
      pdf->plotOn(plot_t);//,RooFit::NormRange("fitdata_1,fitdata_2"));

      double chi2_t = plot_t->chiSquare(np);
      if( chi2_t>=chi2) npass++;
      toy_chi2.push_back(chi2_t*(nBinsForMass-np));
      delete plot_t;
    }
    std::cout << "[INFO] complete" << std::endl;
    prob = (double)npass / ntoys;

    TCanvas *can = new TCanvas();
    double medianChi2 = toy_chi2[(int)(((float)ntoys)/2)];
    double rms = TMath::Sqrt(medianChi2);

    TH1F toyhist(Form("gofTest_%s.pdf",pdf->GetName()),";Chi2;",50,medianChi2-5*rms,medianChi2+5*rms);
    for (std::vector<double>::iterator itx = toy_chi2.begin();itx!=toy_chi2.end();itx++){
      toyhist.Fill((*itx));
    }
    toyhist.Draw();

    TArrow lData(chi2*(nBinsForMass-np),toyhist.GetMaximum(),chi2*(nBinsForMass-np),0);
    lData.SetLineWidth(2);
    lData.Draw();
    can->SaveAs(name.c_str());

    // back to best fit
    params->assignValueOnly(preParams);
  } else {
    prob = TMath::Prob(chi2*(nBinsForMass-np),nBinsForMass-np);
  }
  std::cout << "[INFO] Chi2 in Observed =  " << chi2*(nBinsForMass-np) << std::endl;
  std::cout << "[INFO] p-value  =  " << prob << std::endl;
  delete pdf;
  return prob;

}

void plot(RooRealVar *mass, RooAbsPdf *pdf, RooDataSet *data, string name,vector<string> flashggCats_, int status, double *prob, int proj=1){

  // Chi2 taken from full range fit
  RooPlot *plot_chi2 = mass->frame();
  data->plotOn(plot_chi2,Binning(nBinsForMass));
  pdf->plotOn(plot_chi2);

  int np = pdf->getParameters(*data)->getSize()+1; //Because this pdf has no extend
  double chi2 = plot_chi2->chiSquare(np);

  *prob = getGoodnessOfFit(mass,pdf,data,name);
  RooPlot *plot = mass->frame();
  if(proj==1){
    mass->setRange("unblindReg_1",mgg_low,115);
    mass->setRange("unblindReg_2",135,mgg_high);
    if (BLIND) {
      data->plotOn(plot,Binning(nBinsForMass),CutRange("unblindReg_1"));
      data->plotOn(plot,Binning(nBinsForMass),CutRange("unblindReg_2"));
      data->plotOn(plot,Binning(nBinsForMass),Invisible());
    }
    else data->plotOn(plot,Binning(nBinsForMass));
  }
  if(proj==2){
    mass->setRange("unblindReg_3",mjj_low,105);
    mass->setRange("unblindReg_4",145,mjj_high);
    if (BLIND) {
      data->plotOn(plot,Binning(nBinsForMass2),CutRange("unblindReg_3"));
      data->plotOn(plot,Binning(nBinsForMass2),CutRange("unblindReg_4"));
      data->plotOn(plot,Binning(nBinsForMass2),Invisible());
    }
    else data->plotOn(plot,Binning(nBinsForMass2));
  }
   
  TCanvas *canv = new TCanvas();
  pdf->plotOn(plot);//,RooFit::NormRange("fitdata_1,fitdata_2"));
  pdf->paramOn(plot,RooFit::Layout(0.34,0.96,0.89),RooFit::Format("NEA",AutoPrecision(1)));
  if (BLIND) plot->SetMinimum(0.0001);
  plot->SetTitle("");
  plot->Draw();
  TLatex *lat = new TLatex();
  lat->SetNDC();
  lat->SetTextFont(42);
  lat->DrawLatex(0.1,0.92,Form("#chi^{2} = %.3f, Prob = %.2f, Fit Status = %d ",chi2*(nBinsForMass-np),*prob,status));
  canv->SaveAs(name.c_str());

  //plot_chi2->Draw();
  //canv->SaveAs((name+"debug").c_str());

  delete canv;
  delete lat;
}
void plot(RooRealVar *mass, RooMultiPdf *pdfs, RooCategory *catIndex, RooDataSet *data, string name, vector<string> flashggCats_, int cat, int bestFitPdf=-1, int proj=1){

  TCanvas *canv = new TCanvas(Form("canvas_%d",proj),Form("canvas_%d",proj));
  TPad *pad1 = new TPad(Form("pad1_%d",proj),Form("pad1_%d",proj),0,0.25,1,1);
  TPad *pad2 = new TPad(Form("pad2_%d",proj),Form("pad2_%d",proj),0,0,1,0.35);
  pad1->SetBottomMargin(0.18);
  pad2->SetTopMargin(0.00001);
  //pad2->SetBottomMargin(0.25);
  pad2->SetBottomMargin(0.3);
  pad1->Draw();
  pad2->Draw();
  pad1->cd();


  int color[14] = {kBlue,kRed,kMagenta,kGreen+1,kOrange+7,kAzure+10,kBlack,kBlue,kRed,kMagenta,kGreen+1,kOrange+7,kAzure+10,kBlack};
  TLegend *leg = new TLegend(0.5,0.55,0.92,0.88);
  leg->SetFillColor(0);
  leg->SetLineColor(1);
  RooPlot *plot = mass->frame();

  if(proj==1){
    mass->setRange("unblindReg_1",mgg_low,115);
    mass->setRange("unblindReg_2",135,mgg_high);
    if (BLIND) {
      data->plotOn(plot,Binning(nBinsForMass),CutRange("unblindReg_1"),LineColor(kWhite),MarkerColor(kWhite));
      data->plotOn(plot,Binning(nBinsForMass),CutRange("unblindReg_2"),LineColor(kWhite),MarkerColor(kWhite));
      data->plotOn(plot,Binning(nBinsForMass),Invisible(),LineColor(kWhite),MarkerColor(kWhite));
    }
    else data->plotOn(plot,Binning(nBinsForMass));
  }
  if(proj==2){
    mass->setRange("unblindReg_3",mjj_low,105);
    mass->setRange("unblindReg_4",145,mjj_high);
    if (BLIND) {
     // data->plotOn(plot,Binning(nBinsForMass2),CutRange("unblindReg_3,unblindReg_4"));
      data->plotOn(plot,Binning(nBinsForMass2),CutRange("unblindReg_3"),LineColor(kWhite),MarkerColor(kWhite));
      data->plotOn(plot,Binning(nBinsForMass2),CutRange("unblindReg_4"),LineColor(kWhite),MarkerColor(kWhite));
      data->plotOn(plot,Binning(nBinsForMass2),Invisible(),LineColor(kWhite),MarkerColor(kWhite));
    }
    else data->plotOn(plot,Binning(nBinsForMass2));
  }

  vector<string> pdfNameSplit;
  string bestFitFuncNameOtherProj; 
  for (int icat=0;icat<catIndex->numTypes();icat++){
    if (bestFitPdf==icat) {
      //split in mgg and mjj func by splitting in _.
      string currentPdfName(pdfs->getCurrentPdf()->GetName());
      split(pdfNameSplit,currentPdfName,boost::is_any_of("_"));
      if (proj==1) bestFitFuncNameOtherProj = pdfNameSplit[2]; //first is Mgg, then is Mjj
      if (proj==2) bestFitFuncNameOtherProj = pdfNameSplit[1];
    } 
  }
  cout<<"Best fit name : "<<bestFitFuncNameOtherProj<<endl;
  RooHist *plotdata = (RooHist*)plot->getObject(plot->numItems()-1);
  int npoints = plotdata->GetN();
  TGraphAsymmErrors *hdata  = new TGraphAsymmErrors(npoints);

  int currentIndex = catIndex->getIndex();
 // TObject *datLeg = plot->getObject(int(plot->numItems())-1);
 // leg->AddEntry(datLeg,Form("Data - %s",flashggCats_[cat].c_str()),"LEP");
  leg->AddEntry(hdata,Form("Data - %s",flashggCats_[cat].c_str()),"LEP");
  int style=1;
  RooAbsPdf *pdf;
  RooCurve *nomBkgCurve;
  int bestcol= -1;
  int pdfToConsiderCounter=0;
  for (int icat=0;icat<catIndex->numTypes();icat++){
    int col;
    if (pdfToConsiderCounter<=6) col=color[pdfToConsiderCounter];
    else if(pdfToConsiderCounter<=13){
      col=color[pdfToConsiderCounter]; 
      style++;
    } else { 
      col=kBlack; 
      style++; 
    }
    catIndex->setIndex(icat);
    pdfs->getCurrentPdf()->fitTo(*data,RooFit::Minos(0),RooFit::Minimizer("Minuit2","minimize"),RooFit::SumW2Error(kTRUE)); //FIXME
    string currentPdfName(pdfs->getCurrentPdf()->GetName());
    split(pdfNameSplit,currentPdfName,boost::is_any_of("_"));
    string currentFuncNameOtherProj; 
    if (proj==1) currentFuncNameOtherProj = pdfNameSplit[2]; //first is Mgg, then is Mjj
    if (proj==2) currentFuncNameOtherProj = pdfNameSplit[1]; //first is Mgg, then is Mjj
    if (currentFuncNameOtherProj==bestFitFuncNameOtherProj) {
      pdfs->getCurrentPdf()->plotOn(plot,LineColor(col),LineStyle(style));//,RooFit::NormRange("fitdata_1,fitdata_2"));
      pdfToConsiderCounter+=1;
    }
    TObject *pdfLeg = plot->getObject(int(plot->numItems()-1));
    std::string ext = "";
    if (bestFitPdf==icat) {
      ext=" (Best Fit Pdf) ";
      pdf= pdfs->getCurrentPdf();
      nomBkgCurve = (RooCurve*)plot->getObject(plot->numItems()-1);
      bestcol = col;
    }
    if (currentFuncNameOtherProj==bestFitFuncNameOtherProj)  leg->AddEntry(pdfLeg,Form("%s%s",pdfs->getCurrentPdf()->GetName(),ext.c_str()),"L");
  }
  plot->SetTitle(Form("Category %s",flashggCats_[cat].c_str()));
  if (BLIND) plot->SetMinimum(0.0001);
  plot->GetXaxis()->SetLabelSize(0.0);
  plot->Draw();
  leg->Draw("same");
  CMS_lumi( canv, 0, 0);
  ///start extra bit for ratio plot///
  TH1D *hbplottmp;
  double xtmp,ytmp;//
  int point =0;
  TGraphAsymmErrors *hdatasub = new TGraphAsymmErrors(npoints);
  //hdatasub->SetMarkerSize(defmarkersize);
  for (int ipoint=0; ipoint<npoints; ++ipoint) {
    //double bkgval = hbplottmp->GetBinContent(ipoint+1);
    plotdata->GetPoint(ipoint, xtmp,ytmp);
    double bkgval = nomBkgCurve->interpolate(xtmp);
    if (BLIND && proj==1) {
      if ((xtmp > 115 ) && ( xtmp < 135) ) continue;
    }
    if (BLIND && proj==2) {
      if ((xtmp > 105 ) && ( xtmp < 145) ) continue;
    }
	
    //	std::cout << "[INFO] plotdata->Integral() " <<  plotdata->Integral() << " ( bins " << npoints  << ") hbkgplots[i]->Integral() " << hbplottmp->Integral() << " (bins " << hbplottmp->GetNbinsX() << std::endl;
    double errhi = plotdata->GetErrorYhigh(ipoint);
    double errlow = plotdata->GetErrorYlow(ipoint);

    //std::cout << "[INFO]  Channel " << name  << " errhi " << errhi << " errlow " << errlow  << std::endl;
    //	std::cout << "[INFO] Channel  " << name << " setting point " << point <<" : xtmp "<< xtmp << "  ytmp " << ytmp << " bkgval  " << bkgval << " ytmp-bkgval " << ytmp-bkgval << std::endl;
    bool drawZeroBins_ =1;
    if (!drawZeroBins_) if(fabs(ytmp)<1e-5) continue;
    hdatasub->SetPoint(point,xtmp,ytmp-bkgval);
    hdatasub->SetPointError(point,0.,0.,errlow,errhi );
    hdata->SetPoint(point,xtmp,ytmp);
    hdata->SetPointError(point,0.,0.,errlow,errhi );
    point++;
  }
  pad2->cd();
  TH1 *hdummy;
  if(proj==1) hdummy = new TH1D("hdummyweight","",nBinsForMass,mgg_low,mgg_high);
  if(proj==2) hdummy = new TH1D("hdummyweight","",nBinsForMass2,mjj_low,mjj_high);   

  hdummy->SetMaximum(hdatasub->GetHistogram()->GetMaximum()+1);
  hdummy->SetMinimum(hdatasub->GetHistogram()->GetMinimum()-1);
  hdummy->GetYaxis()->SetTitle("data - best fit PDF");
  hdummy->GetYaxis()->SetTitleSize(0.11);
  hdummy->GetYaxis()->SetTitleOffset(0.4);
  hdummy->GetYaxis()->SetLabelSize(0.07);
  hdummy->GetXaxis()->SetLabelSize(0.1);
  if(proj==1){
    hdummy->GetXaxis()->SetTitle("m_{#gamma#gamma} (GeV)");
  } else {
    hdummy->GetXaxis()->SetTitle("m_{jj} (GeV)");
  }
  hdummy->GetXaxis()->SetTitleSize(0.12);
  hdummy->Draw("HIST");
  hdummy->GetYaxis()->SetNdivisions(808);

  TLine *line3;
  if(proj==1) line3 = new TLine(mgg_low,0.,mgg_high,0.);
  if(proj==2) line3 = new TLine(mjj_low,0.,mjj_high,0.);   
  line3->SetLineColor(bestcol);
  //line3->SetLineStyle(kDashed);
  line3->SetLineWidth(5.0);
  line3->Draw();
  hdatasub->Draw("PESAME");
  pad1->cd();
  if (BLIND) hdata->Draw("PESAME");
  // enf extra bit for ratio plot///
  canv->SaveAs(Form("%s.pdf",name.c_str()));
  canv->SaveAs(Form("%s.jpg",name.c_str()));
  catIndex->setIndex(currentIndex);
  delete canv;
}

void plot(RooRealVar *mass, map<string,RooAbsPdf*> pdfs, RooDataSet *data, string name, vector<string> flashggCats_, int cat, int bestFitPdf=-1, int proj = 1){

  int color[7] = {kBlue,kRed,kMagenta,kGreen+1,kOrange+7,kAzure+10,kBlack};
  TCanvas *canv = new TCanvas();
  TLegend *leg = new TLegend(0.6,0.65,0.88,0.88);
  leg->SetFillColor(0);
  leg->SetLineColor(0);
  RooPlot *plot = mass->frame();
  if(proj==1){
    mass->setRange("unblindReg_1",mgg_low,115);
    mass->setRange("unblindReg_2",135,mgg_high);
    if (BLIND) {
      data->plotOn(plot,Binning(nBinsForMass),CutRange("unblindReg_1"));
      data->plotOn(plot,Binning(nBinsForMass),CutRange("unblindReg_2"));
      data->plotOn(plot,Binning(nBinsForMass),Invisible());
    }
    else data->plotOn(plot,Binning(nBinsForMass));
  }
  if(proj==2){
    mass->setRange("unblindReg_1",mjj_low,105);
    mass->setRange("unblindReg_2",145,mjj_high);
    if (BLIND) {
      data->plotOn(plot,Binning(nBinsForMass2),CutRange("unblindReg_1"));
      data->plotOn(plot,Binning(nBinsForMass2),CutRange("unblindReg_2"));
      data->plotOn(plot,Binning(nBinsForMass2),Invisible());
    }
    else data->plotOn(plot,Binning(nBinsForMass2));      
  }
  TObject *datLeg = plot->getObject(int(plot->numItems()-1));
  if(flashggCats_.size() >0){
    leg->AddEntry(datLeg,Form("Data - %s",flashggCats_[cat].c_str()),"LEP");
  } else {
    leg->AddEntry(datLeg,Form("Data - %d",cat),"LEP");
  }
  int i=0;
  int style=1;
  cout<< Form(" INFO Catergory %d ",cat)<<endl;
  for (map<string,RooAbsPdf*>::iterator it=pdfs.begin(); it!=pdfs.end(); it++){
    int col;
    if (i<=6) col=color[i];
    else {col=kBlack; style++;}
    it->second->plotOn(plot,LineColor(col),LineStyle(style));//,RooFit::NormRange("fitdata_1,fitdata_2"));
    TObject *pdfLeg = plot->getObject(int(plot->numItems()-1));
    std::string ext = "";
    if (bestFitPdf==i) ext=" (Best Fit Pdf) ";
    leg->AddEntry(pdfLeg,Form("%s%s",it->first.c_str(),ext.c_str()),"L");

    int np = (it->second)->getParameters(*data)->getSize()+1; //Because this pdf has no extend
    double chi2 = plot->chiSquare(np);
    int numBins = 0;
    if (proj==1) numBins = nBinsForMass;
    if (proj==2) numBins = nBinsForMass2;
    double prob = TMath::Prob(chi2*(numBins-np),numBins-np);
    // double *prob;
    // *prob = getGoodnessOfFit(mass,(it->second),data,name);
    // cout<< Form("reduced #chi^{2} = %.3f, #chi^{2} = %.3f, Prob = %.2f",chi2,chi2*(nBinsForMass-np),*prob)<<endl;
    // cout<< Form(" INFO projection = %d  %s %s #chi^{2} = %.3f, reduced #chi^{2} = %.3f, prob = %.7f",proj,it->first.c_str(),ext.c_str(),chi2*(numBins-np),chi2,prob)<<endl;
    string proj_str = "Mjj";
    if (proj==1)  proj_str= "Mgg";
    cout<< Form(" INFO : Projection = %s, %s %s, #chi^{2} = %.3f",proj_str.c_str(),it->first.c_str(),ext.c_str(),chi2)<<endl;

    i++;
  }
  plot->SetTitle(Form(" %s",flashggCats_[cat].c_str()));
  if (BLIND) plot->SetMinimum(0.0001);
  plot->Draw();
  leg->Draw("same");
  CMS_lumi( canv, 0, 0);
  canv->SaveAs(Form("%s.pdf",name.c_str()));
  canv->SaveAs(Form("%s.jpg",name.c_str()));
  delete canv;
}

void transferMacros(TFile *inFile, TFile *outFile){

  TIter next(inFile->GetListOfKeys());
  TKey *key;
  while ((key = (TKey*)next())){
    if (string(key->ReadObj()->ClassName())=="TMacro") {
      //cout << key->ReadObj()->ClassName() << " : " << key->GetName() << endl;
      TMacro *macro = (TMacro*)inFile->Get(key->GetName());
      outFile->cd();
      macro->Write();
    }
  }
}
int getBestFitFunction(RooMultiPdf *bkg, RooDataSet *data, RooCategory *cat, bool silent=false){


  double global_minNll = 1E10;
  int best_index = 0;
  int number_of_indeces = cat->numTypes();

  RooArgSet snap,clean;
  RooArgSet *params = bkg->getParameters((const RooArgSet*)0);
  params->remove(*cat);
  params->snapshot(snap);
  params->snapshot(clean);
  if (!silent) {
    //params->Print("V");
  }

  //bkg->setDirtyInhibit(1);
  //RooAbsReal *nllm = bkg->createNLL(*data);
  //RooMinimizer minim(*nllm);
  //minim.setStrategy(1);

  for (int id=0;id<number_of_indeces;id++){
    params->assignValueOnly(clean);
    cat->setIndex(id);

    //RooAbsReal *nllm = bkg->getCurrentPdf()->createNLL(*data);

    if (!silent) {
      /*
       * std::cout << "BEFORE  MAKING FIT" << std::endl;
       * params->Print("V");
       * std::cout << "-----------------------" << std::endl;
       * */
    }

    //minim.minimize("Minuit2","minimize");
    double minNll=0; //(nllm->getVal())+bkg->getCorrection();
    int fitStatus=1;
    runFit(bkg->getCurrentPdf(),data,&minNll,&fitStatus,/*max iterations*/3);
    // Add the penalty

    minNll=minNll+bkg->getCorrection();

    if (!silent) {
      /*
       * std::cout << "After Minimization ------------------  " <<std::endl;
       * std::cout << bkg->getCurrentPdf()->GetName() << " " << minNll <<std::endl;
       * bkg->Print("v");
       * bkg->getCurrentPdf()->getParameters(*data)->Print("V");
       * std::cout << " ------------------------------------  " << std::endl;
       *
       * params->Print("V");
       * */
      std::cout << "[INFO] AFTER FITTING" << std::endl;
      std::cout << "[INFO] Function was " << bkg->getCurrentPdf()->GetName() <<std::endl;
      std::cout << "[INFO] Correction Applied is " << bkg->getCorrection() <<std::endl;
      std::cout << "[INFO] NLL + c = " <<  minNll << std::endl;
      std::cout << "-----------------------" << std::endl;
    }

    if (minNll < global_minNll){
      global_minNll = minNll;
      snap.assignValueOnly(*params);
      best_index=id;
    }
  }
  cat->setIndex(best_index);
  params->assignValueOnly(snap);

  if (!silent) {
    std::cout << "[INFO] Best fit Function -- " << bkg->getCurrentPdf()->GetName() << " " << cat->getIndex() <<std::endl;
    //bkg->getCurrentPdf()->getParameters(*data)->Print("v");
  }
  return best_index;
}

void BkgMultiModelFitAllOrders(TString OutputFileName, std::string jsonForEnvelope,RooWorkspace *_w,
			       int Ncat,  vector<map<string,int> > choices_mgg, vector<map<string,int> > choices_mjj,
			       vector<string> functionClasses, map<string,string> namingMap,
			       int _fitStrategy,bool isFlashgg_,bool isData_,int isbbggLimits_,
			       vector<string> flashggCats_, std::string ext, std::string outDir)
{
  std::vector<RooDataSet*> data(Ncat,nullptr);
  RooWorkspace *wBias;

  wBias = new RooWorkspace("multipdf","multipdf");
  //   int _fitStrategy=2; // Only 2D for start
   
  RooRealVar *mgg,*mjj;
  if(isFlashgg_ && isData_){
    mgg = _w->var("CMS_hgg_mass");
    // if(_fitStrategy==2) mjj = _w->var("CMS_hjj_mass");
    //  else mjj = new RooRealVar("CMS_hjj_mass","CMS_hjj_mass",mjj_low,mjj_high);
    if(_fitStrategy==2) mjj = _w->var("Mjj");
    else mjj = new RooRealVar("CMS_hjj_mass","CMS_hjj_mass",mjj_low,mjj_high);
  }
  else if(isbbggLimits_){
    mgg = _w->var("mgg");
    mjj = _w->var("mjj");
  }

 
  mgg->setRange("BkgFitRange",mgg_low,mgg_high);
  if(_fitStrategy==2) mjj->setRange("BkgFitRange",mjj_low,mjj_high);
  RooArgSet *obsset = new RooArgSet();
  obsset->add(*mgg);
  if(_fitStrategy==2) obsset->add(*mjj);
  if(_fitStrategy==1)
    mgg->setBins(nBinsForMass);
  if(_fitStrategy==2){
    mgg->setBins(100);
    mjj->setBins(100);
  }
  RooFitResult* fitresults = new RooFitResult();
  PdfModelBuilder pdfsModel;
  pdfsModel.setObsVar(mgg);
  PdfModelBuilder pdfsModel_1;
  pdfsModel_1.setObsVar(mjj);
   
  RooAbsPdf* mggBkgTmp = nullptr;
  RooAbsPdf* mjjBkgTmp = nullptr;
  RooProdPdf* BkgProdPdf = nullptr;
  RooExtendPdf* BkgExtPdf = nullptr;
   

  // add label for pdf according to function
  int NumOfFunc = functionClasses.size();
  const char *label[NumOfFunc] = {"Ber", "Exp", "Pow"};
  //   for(int i=0;i<NumOfFunc;i++){
  //      label[i] = (namingMap.find(functionClasses[i])).c_str();
  //   }
  int func_ordmgg[Ncat][NumOfFunc];
  int func_ordmjj[Ncat][NumOfFunc];
  bool allorders[Ncat];
  for(int i=0;i<Ncat;i++) allorders[i]=false;
  ifstream  jFile(jsonForEnvelope.c_str());
  std::vector<TString> EnvFunc[Ncat];
  if(!jFile.good()){
    cout<<"[WARNING]: Can't open envelope json file "<<jsonForEnvelope.c_str()<<endl;
    for(int c=0;c<Ncat;c++){
      map<string,int> choices_mgg_cat = choices_mgg[c];
      map<string,int> choices_mjj_cat = choices_mjj[c];
      for(int i=0;i<NumOfFunc;i++){
	func_ordmgg[c][i] = choices_mgg_cat.find(functionClasses[i])->second;
	func_ordmjj[c][i] = choices_mjj_cat.find(functionClasses[i])->second;
	allorders[c] = true;
      }
    }
  }
  else{
    cout<<"[INFO]: Produce MultiPdf according to this json file - "<<jsonForEnvelope.c_str()<<endl;
    int cat; char funcs[500]; char line[500];
    jFile.getline(line,500);
    for(int c=0;c<Ncat;c++){
      jFile.getline(line,500);
      cat=-1; strcpy(funcs, "");
      sscanf(line,"cat%d: %d %d %d %d %d %d %s",&cat,&(func_ordmgg[c][0]),&(func_ordmgg[c][1]),&(func_ordmgg[c][2]),&(func_ordmjj[c][0]),&(func_ordmjj[c][1]),&(func_ordmjj[c][2]),funcs);
	 
      TString st_funcs(funcs);
      TObjArray *tx = st_funcs.Tokenize(",");
      if(tx->GetEntries()>0){
	for (Int_t i = 0; i < tx->GetEntries(); i++) EnvFunc[cat].push_back(  ((TObjString *)(tx->At(i)))->String() );
      }
      else
	allorders[c] = true;
      delete tx;
	 
      // printf("cat %d:\n ",cat);
      // printf("%d %d %d %d %d %d\n",func_ordmgg[c][0],func_ordmgg[c][1],func_ordmgg[c][2],func_ordmjj[c][0],func_ordmjj[c][1],func_ordmjj[c][2]);
      //cout<<func_ordmgg[c][0]<<"  "<<func_ordmgg[c][1]<<"  "<<func_ordmgg[c][2]<<"  "<<func_ordmjj[c][0]<<"  "<<func_ordmjj[c][1]<<"  "<<func_ordmjj[c][2]<<"  "<<endl;
      //	 for(unsigned k=0; k<EnvFunc[c].size(); k++){
      //	    cout<<EnvFunc[c][k]<<"  ";
      //	    //printf("%s  \n",EnvFunc[c][k].Data());
      //	    if(k>4) break;
      //	 }
      //	 cout<<endl;
	 
    }
      
  }

   
  for (int c = 0; c < Ncat; ++c) { // to each category

    string catname;
    if (isData_) {
      catname = Form("%s",flashggCats_[c].c_str());
      data[c] = (RooDataSet*)_w->data(Form("Data_13TeV_%s",catname.c_str()));
    }
    else if(isbbggLimits_){
      catname = Form("cat%d",c);
      data[c] = (RooDataSet*)_w->data(Form("data_obs_%s",catname.c_str()));
    }
    else{
      catname = Form("%s",flashggCats_[c].c_str());
      data[c] = (RooDataSet*)_w->data(Form("data_mass_%s",catname.c_str()));
    }
    cout<<"\n"<<"----------------------"<<endl;   
    cout<<"[INFO] Category "<<catname.c_str()<<":"<<endl;
    cout<<"[INFO] "<<mgg->GetName()<<": ";
    for(int mggfunc=0;mggfunc<NumOfFunc;mggfunc++)
      cout<<functionClasses[mggfunc]<<"-"<<func_ordmgg[c][mggfunc]<<" , ";
    cout<<endl;
    if(_fitStrategy == 2){
      cout<<"[INFO] "<<mjj->GetName()<<": ";
      for(int mjjfunc=0;mjjfunc<NumOfFunc;mjjfunc++)
	cout<<functionClasses[mjjfunc]<<"-"<<func_ordmjj[c][mjjfunc]<<" , ";
      cout<<endl;
    }

    RooRealVar norm(TString::Format("roomultipdf_%s_norm",flashggCats_[c].c_str()),"Number of background events",0,10000);
    RooArgList mypdfs;
      
    for(int mggfunc=0;mggfunc<NumOfFunc;mggfunc++){
      for(int mggfunc_ord=1; mggfunc_ord<=func_ordmgg[c][mggfunc]; mggfunc_ord++){
	    
	if(mggfunc>0 && mggfunc_ord%2==0) continue; // only odd orders are allowed for Exp and Pow
	    
	for(int mjjfunc=0;mjjfunc<NumOfFunc;mjjfunc++){
	  for(int mjjfunc_ord=1; mjjfunc_ord<=func_ordmjj[c][mjjfunc]; mjjfunc_ord++){

	    if(_fitStrategy == 1 && !(mjjfunc==0 && mjjfunc_ord==1)) continue;
	    if(mjjfunc>0 && mjjfunc_ord%2==0)  continue;

	    bool stoploop=true;
	    if(EnvFunc[c].size()>0){
	      for(unsigned k=0; k<EnvFunc[c].size(); k++){
		TString s1,s2;
		if(_fitStrategy == 2){
		  s1 = TString::Format("%s%d_%s%d",label[mggfunc],mggfunc_ord,label[mjjfunc],mjjfunc_ord);
		  s2 = EnvFunc[c][k];
		}
		else if(_fitStrategy == 1){
		  s1 = TString::Format("%s%d",label[mggfunc],mggfunc_ord);
		  s2 = EnvFunc[c][k]; s2 = s2(0,s2.First("_"));
		}
			
		if( s1==s2 || allorders[c])
		  stoploop=false;
			
	      }
	    }
	    else{
	      stoploop=false;
	    }

	    if(stoploop) continue;

       bool gofPass_mgg=true;
       bool gofPass_mjj=true;
		  
	    //  printf("%s%d_%s%d_cat%d\n",label[mggfunc],mggfunc_ord,label[mjjfunc],mjjfunc_ord,c);
	    if(_fitStrategy == 2){
	      mggBkgTmp = getPdf(pdfsModel,functionClasses[mggfunc],mggfunc_ord, TString::Format("bkg_mgg_for%s%d_%s",label[mjjfunc],mjjfunc_ord,flashggCats_[c].c_str()));
	      mjjBkgTmp = getPdf(pdfsModel_1,functionClasses[mjjfunc],mjjfunc_ord, TString::Format("bkg_mjj_for%s%d_%s",label[mggfunc],mggfunc_ord,flashggCats_[c].c_str()));

		   double gofProbMgg =0; 
		   double gofProbMjj =0; 
/*		   int fitStatus=0;
         int proj=1;
			plot(mgg,mggBkgTmp,data[c],Form("%s/%s%d_mgg_gof_%s.pdf",outDir.c_str(),label[mggfunc],mggfunc_ord,flashggCats_[c].c_str()),flashggCats_,fitStatus,&gofProbMgg,proj);
			if (! ((gofProbMgg > 0.05) || (mggfunc_ord == func_ordmgg[c][mggfunc]) )){   // Good looking fit or one of our regular truth functions
              gofPass_mgg=false;
         }
         proj=2;
			plot(mjj,mjjBkgTmp,data[c],Form("%s/%s%d_mjj_gof_%s.pdf",outDir.c_str(),label[mjjfunc],mjjfunc_ord,flashggCats_[c].c_str()),flashggCats_,fitStatus,&gofProbMjj,proj);
			if (! ((gofProbMjj > 0.05) || (mjjfunc_ord == func_ordmjj[c][mjjfunc]) )){   // Good looking fit or one of our regular truth functions
              gofPass_mjj=false;
         }
         cout<<"INFO Mjj : "<<Form("%s%d %s",label[mjjfunc],mjjfunc_ord,flashggCats_[c].c_str())<<"  "<<gofProbMjj<<"  "<<gofPass_mjj<<endl;
         cout<<"INFO Mgg : "<<Form("%s%d %s",label[mggfunc],mggfunc_ord,flashggCats_[c].c_str())<<"  "<<gofProbMgg<<"  "<<gofPass_mgg<<endl;
*/
	      BkgProdPdf = new RooProdPdf(TString::Format("pdf_%s%d_%s%d_%s",label[mggfunc],mggfunc_ord,label[mjjfunc],mjjfunc_ord,flashggCats_[c].c_str()), "", RooArgList(*mggBkgTmp, *mjjBkgTmp));
	      BkgExtPdf = new RooExtendPdf(TString::Format("ext_pdf_%s%d_%s%d_%s",label[mggfunc],mggfunc_ord,label[mjjfunc],mjjfunc_ord,flashggCats_[c].c_str()),"", *BkgProdPdf,norm);
	    }
	    else if(_fitStrategy == 1){
	      mggBkgTmp = getPdf(pdfsModel,functionClasses[mggfunc],mggfunc_ord, TString::Format("bkg_mgg_%s",flashggCats_[c].c_str()));
	      BkgExtPdf = new RooExtendPdf(TString::Format("ext_pdf_%s%d_%s",label[mggfunc],mggfunc_ord,flashggCats_[c].c_str()),"", *mggBkgTmp,norm);
	    }
	    RooArgSet *params_test = BkgExtPdf->getParameters(obsset);
	    int ntries = 0;

	    int stat = 1;
	    while (stat!=0 && ntries < 100){
		     
	      fitresults = BkgExtPdf->fitTo(*data[c], Strategy(2),Minos(kFALSE), Range("BkgFitRange"), Save(kTRUE),PrintLevel(-1));
	      stat = fitresults->status();
	      if (stat!=0) params_test->assignValueOnly(fitresults->randomizePars());
	      ntries++;
	    }
	    if(stat!=0){
	      printf("Warning::Fit of background function pdf_%s%d_%s%d_%s is failed\n",label[mggfunc],mggfunc_ord,label[mjjfunc],mjjfunc_ord,flashggCats_[c].c_str());
	    }
	    if(_fitStrategy == 2)
         if ((gofPass_mgg) && (gofPass_mjj)) mypdfs.add(*BkgProdPdf);
	    else if(_fitStrategy == 1)
	      mypdfs.add(*mggBkgTmp);
	  }
	}
      }
    }
      
    if(mypdfs.getSize() == 0){
      printf("[ERROR] BkgMultiModelFitAllOrders: There are no functions in RooMultiPdf for cat %d\n",c);
      printf("Production of workspace with RooMultiPdf was aborted\n");
      return;
    }
      
    RooCategory category(TString::Format("pdf_index_%s",flashggCats_[c].c_str()),"Index of Pdf which is active");
    RooMultiPdf multipdf(TString::Format("roomultipdf_%s",flashggCats_[c].c_str()),"All Pdfs",category,mypdfs);

    if(isFlashgg_==1){
      category.SetName(Form("pdfindex_%s_%s",flashggCats_[c].c_str(),ext.c_str()) );
      multipdf.SetName(Form("CMS_hgg_%s_%s_bkgshape",flashggCats_[c].c_str(),ext.c_str()));
      norm.SetName( Form("CMS_hgg_%s_%s_bkgshape_norm",catname.c_str(),ext.c_str()) );
      norm.setVal(data[c]->sumEntries());
      norm.setRange(0,3*data[c]->sumEntries());
    }
      
    int bestFitPdfIndex = getBestFitFunction(&multipdf,data[c],&category,1);
    category.setIndex(bestFitPdfIndex);
    std::cout << "[INFO] Created MultiPdf " << multipdf.GetName() << ", in Category " << c << " with a total of " << category.numTypes() << " pdfs"<< std::endl;
    //      mypdfs.Print();
    std::cout << "[INFO] Best Fit Pdf = " << bestFitPdfIndex << ", " << mypdfs.at(bestFitPdfIndex)->GetName() << std::endl;
      
    wBias->import(category);
    wBias->import(norm);
    wBias->import(multipdf);
    wBias->import(*data[c]);

    plot(mgg,&multipdf,&category,data[c],Form("%s/multipdf_mass_%s",outDir.c_str(),flashggCats_[c].c_str()),flashggCats_,c,bestFitPdfIndex,1);
    plot(mjj,&multipdf,&category,data[c],Form("%s/multipdf_mass2_%s",outDir.c_str(),flashggCats_[c].c_str()),flashggCats_,c,bestFitPdfIndex,2);
      
    if(isFlashgg_==1 && _fitStrategy == 1){
      RooDataHist dataBinned(Form("roohist_data_mass_%s",flashggCats_[c].c_str()),"data",*mgg,*data[c]);
      wBias->import(dataBinned);
    }
      
  }
  RooRealVar *intL;
  RooRealVar *sqrts;
  if (isFlashgg_){
    intL  = intLumi_;
    sqrts = (RooRealVar*)_w->var("SqrtS");
    if (!sqrts){ sqrts = new RooRealVar("SqrtS","SqrtS",13); }
  } else if(isbbggLimits_){
    intL = new RooRealVar("IntLumi","IntLumi",77.4); //FIXME
    sqrts = new RooRealVar("SqrtS","SqrtS",13); //FIXME
  }else {
    intL  = intLumi_;
    sqrts = (RooRealVar*)_w->var("Sqrts");
  }
  wBias->import(*intL);
  wBias->import(*sqrts);
   
  //   if (_verbLvl>1) std::cout << "[BkgMultiPDFModelFit] Finish cat loop " << std::endl;
  //      wBias->Print("v");
  TString filename;
  if(OutputFileName=="")
    filename="./ws_TEST.root";
  else
    filename = OutputFileName;
   
  TFile * tFile = new TFile(filename.Data(), "RECREATE");
  tFile->cd();
  wBias->Write();
  tFile->Close();
   
}


int main(int argc, char* argv[]){

  setTDRStyle();
  writeExtraText = true;       // if extra text
  extraText  = "Preliminary";  // default extra text is "Preliminary"
  lumi_8TeV  = "19.1 fb^{-1}"; // default is "19.7 fb^{-1}"
  lumi_7TeV  = "4.9 fb^{-1}";  // default is "5.1 fb^{-1}"
  lumi_sqrtS = "13 TeV";       // used with iPeriod = 0, e.g. for simulation-only plots (default is an empty string)
  int year_ = 2016;
  //int year_ = 2017;

  string fileName;
  int ncats;
  int singleCategory;
  string datfile;
  string outDir;
  string outfilename;
  bool is2011=false;
  bool verbose=false;
  bool saveMultiPdf=false;
  int isFlashgg_ =1;    int FitStrategy_ =2;
  string flashggCatsStr_;
  vector<string> flashggCats_;
  bool isData_ =0;     bool isbbggLimits_ =0;
  std::string jsonForEnvelope_ = "";
   
  po::options_description desc("Allowed options");
  desc.add_options()
    ("help,h",                                                                                  "Show help")
    ("infilename,i", po::value<string>(&fileName),                                              "In file name")
    ("ncats,c", po::value<int>(&ncats)->default_value(5),                                       "Number of categories")
    ("singleCat", po::value<int>(&singleCategory)->default_value(-1),                           "Run A single Category")
    ("datfile,d", po::value<string>(&datfile)->default_value("dat/fTest.dat"),                  "Right results to datfile for BiasStudy")
    ("outDir,D", po::value<string>(&outDir)->default_value("plots/fTest"),                      "Out directory for plots")
    ("saveMultiPdf", po::value<string>(&outfilename),         "Save a MultiPdf model with the appropriate pdfs")
    ("runFtestCheckWithToys", "When running the F-test, use toys to calculate pvals (and make plots) ")
    ("is2011",                                                                                  "Run 2011 config")
    ("is2012",                                                                                  "Run 2012 config")
    ("unblind",          "Dont blind plots")
    ("isFlashgg",  po::value<int>(&isFlashgg_)->default_value(1),              "Use Flashgg output ")
    ("FitStrategy",  po::value<int>(&FitStrategy_)->default_value(2),              "1D or 2D ")		 
    ("isbbggLimits",  po::value<bool>(&isbbggLimits_)->default_value(0),              "Use bbggLimit output ")
    ("isData",  po::value<bool>(&isData_)->default_value(0),              "Use Data not MC ")
    ("flashggCats,f", po::value<string>(&flashggCatsStr_)->default_value("UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,UntaggedTag_4,VBFTag_0,VBFTag_1,VBFTag_2,TTHHadronicTag,TTHLeptonicTag,VHHadronicTag,VHTightTag,VHLooseTag,VHEtTag"),       "Flashgg category names to consider")
    ("jsonForEnvelope", po::value<string>(&jsonForEnvelope_)->default_value(""),       "Json file for envelope")		     
    ("year", po::value<int>(&year_)->default_value(2016),       "Dataset year")
    ("verbose,v",                                                               "Run with more output")
    ;
  po::variables_map vm;
  po::store(po::parse_command_line(argc,argv,desc),vm);
  po::notify(vm);
  if (vm.count("help")) { cout << desc << endl; exit(1); }
  if (vm.count("is2011")) is2011=true;
  if (vm.count("unblind")) BLIND=false;
  saveMultiPdf = vm.count("saveMultiPdf");
  bool isjsonForEnvelope = false;
  if (vm.count("jsonForEnvelope")) isjsonForEnvelope=true;
   
  if (vm.count("verbose")) verbose=true;
  if (vm.count("runFtestCheckWithToys")) runFtestCheckWithToys=true;

  if (!verbose) {
    RooMsgService::instance().setGlobalKillBelow(RooFit::ERROR);
    RooMsgService::instance().setSilentMode(true);
    gErrorIgnoreLevel=kWarning;
  }
  split(flashggCats_,flashggCatsStr_,boost::is_any_of(","));

  int startingCategory=0;
  if (singleCategory >-1){
    ncats=singleCategory+1;
    startingCategory=singleCategory;
  }
  if (isFlashgg_==1){

    ncats= flashggCats_.size();

  }

  if(verbose) std::cout << "[INFO] SaveMultiPdf? " << saveMultiPdf << std::endl;
  TFile *outputfile;
  RooWorkspace *outputws;

  //   if (saveMultiPdf){
  //      outputfile = new TFile(outfilename.c_str(),"RECREATE");
  //      outputws = new RooWorkspace(); outputws->SetName("multipdf");
  //   }
   
  system(Form("mkdir -p %s",outDir.c_str()));
  TFile *inFile = TFile::Open(fileName.c_str());
  RooWorkspace *inWS;
  if(isFlashgg_){
    if (isData_){
      inWS = (RooWorkspace*)inFile->Get("tagsDumper/cms_hgg_13TeV");
    } else {
      inWS = (RooWorkspace*)inFile->Get("cms_hgg_workspace");
    }
  }
  else if(isbbggLimits_){
    inWS = (RooWorkspace*)inFile->Get("w_all");
  }
  else {
    inWS = (RooWorkspace*)inFile->Get("cms_hgg_workspace");//FIXME
  }
  if (verbose) std::cout << "[INFO]  inWS open " << inWS << std::endl;
  if (saveMultiPdf){
    transferMacros(inFile,outputfile);

  }

  vector<string> functionClasses;
  functionClasses.push_back("Bernstein");
  functionClasses.push_back("Exponential");
  functionClasses.push_back("PowerLaw");
  //   functionClasses.push_back("Laurent");
  map<string,string> namingMap;
  namingMap.insert(pair<string,string>("Bernstein","Ber"));
  namingMap.insert(pair<string,string>("Exponential","Exp"));
  namingMap.insert(pair<string,string>("PowerLaw","Pow"));
  //   namingMap.insert(pair<string,string>("Laurent","lau"));

  // store results here

  FILE *resFile ;
  if  (singleCategory >-1) resFile = fopen(Form("%s/fTestResults_%s.txt",outDir.c_str(),flashggCats_[singleCategory].c_str()),"w");
  else resFile = fopen(Form("%s/fTestResults.txt",outDir.c_str()),"w");
  vector<map<string,int> > choices_vec;
  vector<map<string,int> > choices_vec2;
  //   vector<map<string,std::vector<int> > > choices_envelope_vec;
  //   vector<map<string,RooAbsPdf*> > pdfs_vec;

  PdfModelBuilder pdfsModel,pdfsModel2;
  RooRealVar *mass,*mass2=nullptr;
  if(isbbggLimits_){
    mass = (RooRealVar*)inWS->var("mgg");
    if(FitStrategy_==2) mass2 = (RooRealVar*)inWS->var("mjj"); 
  }
  else{
    mass = (RooRealVar*)inWS->var("CMS_hgg_mass"); //FIXME
    //if(FitStrategy_==2) mass2 = (RooRealVar*)inWS->var("CMS_hjj_mass"); //FIXME
    if(FitStrategy_==2) mass2 = (RooRealVar*)inWS->var("Mjj"); //FIXME
  }
  if(FitStrategy_!=2) mass2 = mass;
  std:: cout << "[INFO] Got masses from ws " << mass;
  if(FitStrategy_==2) std::cout << " and "<< mass2;
  std::cout<< std::endl;
   
  pdfsModel.setObsVar(mass);
  if(FitStrategy_==2)   pdfsModel2.setObsVar(mass2);   
  double upperEnvThreshold = 0.1; // upper threshold on delta(chi2) to include function in envelope (looser than truth function)

  fprintf(resFile,"Truth Model & d.o.f & $\\Delta NLL_{N+1}$ & $p(\\chi^{2}>\\chi^{2}_{(N\\rightarrow N+1)})$ \\\\\n");
  fprintf(resFile,"\\hline\n");

  std::string ext = is2011 ? "7TeV" : "8TeV";
  //if (isFlashgg_) ext = "13TeV";
  //FIXME trying to remove duplicated names for 2016+2017 combination
  if (isFlashgg_) ext = Form("13TeV_%d",year_);
  ext = "13TeV"; //FIXME
  cout<<"start loop"<<endl;
  for (int cat=0; cat<ncats; cat++){

    map<string,int> choices;
    map<string,RooAbsPdf*> pdfs;
    map<string,int> choices2;
    map<string,RooAbsPdf*> pdfs2;

    string catname;
    if (isFlashgg_){
      catname = Form("%s",flashggCats_[cat].c_str());
    } else {
      catname = Form("cat%d",cat);
    }
    RooDataSet *dataFull;
    RooDataSet *dataFull0;
    if (isData_) {
      dataFull = (RooDataSet*)inWS->data(Form("Data_13TeV_%s",catname.c_str()));
      /*dataFull= (RooDataSet*) dataFull0->emptyClone();
       *     for (int i =0 ; i < dataFull0->numEntries() ; i++){
       *     double m = dataFull0->get(i)->getRealValue("CMS_hgg_mass");
       *     //if (m <(mgg_low+0.01) or m > (mgg_high-0.01))
       *     if (m==mgg_low){
       *     std::cout << "dataset mass m="<< m << std::endl;
       *     continue;
       *     }
       *     dataFull->add(*dataFull0->get(),1.0);
       *     }*/
      if (verbose) std::cout << "[INFO] opened data for  "  << Form("Data_%s",catname.c_str()) <<" - " << dataFull <<std::endl;
    }
    else if(isbbggLimits_){
      dataFull = (RooDataSet*)inWS->data(Form("data_obs_%s",catname.c_str()));
      if (verbose) std::cout << "[INFO] opened data for  "  << Form("data_obs_%s",catname.c_str()) <<" - " << dataFull <<std::endl;
    }
    else
      {dataFull = (RooDataSet*)inWS->data(Form("data_mass_%s",catname.c_str()));
	if (verbose) std::cout << "[INFO] opened data for  "  << Form("data_mass_%s",catname.c_str()) <<" - " << dataFull <<std::endl;
      }


    mass->setBins(nBinsForMass);
    RooDataSet *data;
    //RooDataHist thisdataBinned(Form("roohist_data_mass_%s",flashggCats_[cat].c_str()),"data",*mass,*dataFull);
    //RooDataSet *data = (RooDataSet*)&thisdataBinned;
    string thisdataBinned_name;

    if ( isFlashgg_){
      thisdataBinned_name =Form("roohist_data_mass_%s",flashggCats_[cat].c_str());
      //RooDataHist thisdataBinned(Form("roohist_data_mass_%s",flashggCats_[cat].c_str()),"data",*mass,*dataFull);
      //data = (RooDataSet*)&thisdataBinned;
      //std::cout << "debug " << thisdataBinned.GetName() << std::endl;

      //RooDataSet *data = (RooDataSet*)dataFull;
    } else {
      thisdataBinned_name= Form("roohist_data_mass_cat%d",cat);
      //RooDataSet *data = (RooDataSet*)dataFull;
    }
    RooDataHist thisdataBinned(thisdataBinned_name.c_str(),"data",*mass,*dataFull);
    data = (RooDataSet*)&thisdataBinned;
    RooDataSet *data2 = nullptr;
    if(FitStrategy_==2)
      mass2->setBins(nBinsForMass2);
    string thisdataBinned_name2;
      
    if ( isFlashgg_){
      thisdataBinned_name2 =Form("roohist_data_mass2_%s",flashggCats_[cat].c_str());
    } else {
      thisdataBinned_name2= Form("roohist_data_mass2_cat%d",cat);
    }
    RooDataHist thisdataBinned2(thisdataBinned_name2.c_str(),"data2",*mass2,*dataFull);
    data2 = (RooDataSet*)&thisdataBinned2;


    fprintf(resFile,"\\multicolumn{4}{|c|}{\\textbf{Category %d}} \\\\\n",cat);
    fprintf(resFile,"\\hline\n");

    double MinimimNLLSoFar=1e10;
    int simplebestFitPdfIndex = 0;
    int proj = 1;
    // Standard F-Test to find the truth functions for 1st mass
    for (vector<string>::iterator funcType=functionClasses.begin();
	 funcType!=functionClasses.end(); funcType++){

      double thisNll=0.; double prevNll=0.; double chi2=0.; double prob=0.;
      int order=1; int prev_order=0; int cache_order=0;

      RooAbsPdf *prev_pdf=NULL;
      RooAbsPdf *cache_pdf=NULL;
      std::vector<int> pdforders;

      int counter =0;
      while (prob<0.05 && order < 7){ //FIXME
	RooAbsPdf *bkgPdf = getPdf(pdfsModel,*funcType,order,Form("ftest_pdf_%d_%s",cat,ext.c_str()));
	if (!bkgPdf){
	  // assume this order is not allowed
	  order++;
	}
	else {

	  //RooFitResult *fitRes = bkgPdf->fitTo(*data,Save(true),RooFit::Minimizer("Minuit2","minimize"));
	  int fitStatus = 0;
	  //thisNll = fitRes->minNll();
	  bkgPdf->Print();
	  runFit(bkgPdf,data,&thisNll,&fitStatus,/*max iterations*/3);//bkgPdf->fitTo(*data,Save(true),RooFit::Minimizer("Minuit2","minimize"));
	  if (fitStatus!=0) std::cout << "[WARNING] Warning -- Fit status for " << bkgPdf->GetName() << " at " << fitStatus <<std::endl;

	  chi2 = 2.*(prevNll-thisNll);
	  if (chi2<0. && order>1) chi2=0.;
	  if (prev_pdf!=NULL){
	    prob = getProbabilityFtest(chi2,order-prev_order,prev_pdf,bkgPdf,mass,data
				       ,Form("%s/Ftest_from_%s%d_%s.pdf",outDir.c_str(),funcType->c_str(),order,flashggCats_[cat].c_str()));
	    std::cout << "[INFO]  F-test Prob(chi2>chi2(data)) == " << prob << std::endl;
	  } else {
	    prob = 0;
	  }
	  double gofProb=0;
	  // otherwise we get it later ...
	  if (!saveMultiPdf) plot(mass,bkgPdf,data,Form("%s/%s%d_%s.pdf",outDir.c_str(),funcType->c_str(),order,flashggCats_[cat].c_str()),flashggCats_,fitStatus,&gofProb,proj);
	  cout << "[INFO]\t " << *funcType << " " << order << " " << prevNll << " " << thisNll << " " << chi2 << " " << prob << endl;
	  //fprintf(resFile,"%15s && %d && %10.2f && %10.2f && %10.2f \\\\\n",funcType->c_str(),order,thisNll,chi2,prob);
	  prevNll=thisNll;
	  cache_order=prev_order;
	  cache_pdf=prev_pdf;
	  prev_order=order;
	  prev_pdf=bkgPdf;
	  order++;
	}
	counter++;
      }

      fprintf(resFile,"%15s & %d & %5.2f & %5.2f \\\\\n",funcType->c_str(),cache_order+1,chi2,prob);
      choices.insert(pair<string,int>(*funcType,cache_order));
      pdfs.insert(pair<string,RooAbsPdf*>(Form("%s%d",funcType->c_str(),cache_order),cache_pdf));

      int truthOrder = cache_order;

    }
    choices_vec.push_back(choices);
    plot(mass,pdfs,data,Form("%s/truths_mass_%s",outDir.c_str(),flashggCats_[cat].c_str()),flashggCats_,cat,-1,proj);

    if(FitStrategy_==2) {
      proj=2;	 
      // Standard F-Test to find the truth functions for 2nd mass
      for (vector<string>::iterator funcType=functionClasses.begin();
	   funcType!=functionClasses.end(); funcType++){

	double thisNll=0.; double prevNll=0.; double chi2=0.; double prob=0.;
	int order=1; int prev_order=0; int cache_order=0;

	RooAbsPdf *prev_pdf=NULL;
	RooAbsPdf *cache_pdf=NULL;
	std::vector<int> pdforders;

	int counter =0;
	//while (prob<0.05){
	while (prob<0.05 && order < 7){ //FIXME
	  RooAbsPdf *bkgPdf = getPdf(pdfsModel2,*funcType,order,Form("ftest_pdf2_%d_%s",cat,ext.c_str()));
	  if (!bkgPdf){
	    // assume this order is not allowed
	    order++;
	  }
	  else {

	    //RooFitResult *fitRes = bkgPdf->fitTo(*data,Save(true),RooFit::Minimizer("Minuit2","minimize"));
	    int fitStatus = 0;
	    //thisNll = fitRes->minNll();
	    bkgPdf->Print();
	    runFit(bkgPdf,data2,&thisNll,&fitStatus,/*max iterations*/3);//bkgPdf->fitTo(*data,Save(true),RooFit::Minimizer("Minuit2","minimize"));
	    if (fitStatus!=0) std::cout << "[WARNING] Warning -- Fit status for " << bkgPdf->GetName() << " at " << fitStatus <<std::endl;

	    chi2 = 2.*(prevNll-thisNll);
	    if (chi2<0. && order>1) chi2=0.;
	    if (prev_pdf!=NULL){
	      prob = getProbabilityFtest(chi2,order-prev_order,prev_pdf,bkgPdf,mass2,data2
					 ,Form("%s/Ftest2_from_%s%d_%s.pdf",outDir.c_str(),funcType->c_str(),order,flashggCats_[cat].c_str()));
	      std::cout << "[INFO]  F-test Prob(chi2>chi2(data)) == " << prob << std::endl;
	    } else {
	      prob = 0;
	    }
	    double gofProb=0;
	    // otherwise we get it later ...
	    if (!saveMultiPdf) plot(mass2,bkgPdf,data2,Form("%s/%s%d_2_%s.pdf",outDir.c_str(),funcType->c_str(),order,flashggCats_[cat].c_str()),flashggCats_,fitStatus,&gofProb,proj);
	    cout << "[INFO]\t " << *funcType << " " << order << " " << prevNll << " " << thisNll << " " << chi2 << " " << prob << endl;
	    //fprintf(resFile,"%15s && %d && %10.2f && %10.2f && %10.2f \\\\\n",funcType->c_str(),order,thisNll,chi2,prob);
	    prevNll=thisNll;
	    cache_order=prev_order;
	    cache_pdf=prev_pdf;
	    prev_order=order;
	    prev_pdf=bkgPdf;
	    order++;
	  }
	  counter++;
	}

	fprintf(resFile,"%15s & %d & %5.2f & %5.2f \\\\\n",funcType->c_str(),cache_order+1,chi2,prob);
	choices2.insert(pair<string,int>(*funcType,cache_order));
	pdfs2.insert(pair<string,RooAbsPdf*>(Form("%s%d",funcType->c_str(),cache_order),cache_pdf));

	int truthOrder = cache_order;

      }
      choices_vec2.push_back(choices2);
      plot(mass2,pdfs2,data2,Form("%s/truths_mass2_%s",outDir.c_str(),flashggCats_[cat].c_str()),flashggCats_,cat,-1,proj);
    }
    else{
      for (vector<string>::iterator funcType=functionClasses.begin();
	   funcType!=functionClasses.end(); funcType++)
	choices2.insert(pair<string,int>(*funcType,7));
      choices_vec2.push_back(choices2);
    }
  }

   
  if (saveMultiPdf){
    BkgMultiModelFitAllOrders(outfilename, jsonForEnvelope_,inWS,
			      ncats, choices_vec, choices_vec2,
			      functionClasses, namingMap,
			      FitStrategy_,isFlashgg_,isData_,isbbggLimits_,
			      flashggCats_, ext, outDir);
  }


  return 0;
}
