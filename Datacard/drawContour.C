void drawContour(string infilename, string label="")
{
  TFile* infile = new TFile(infilename.c_str(),"READ");
  TTree* intree = (TTree*) infile->Get("limit");
  TCanvas *c = new TCanvas("def","def",600,600);
  int Npoints = intree->Draw("mu_hh:mu_tth","","");
  TGraph* contour68 = new TGraph(Npoints,intree->GetV2(),intree->GetV1());
  contour68->SetMarkerStyle(20);
  contour68->SetTitle("68% C.L. contour");
  TCanvas *c1 = new TCanvas("plot","plot",600,600);
  c1->cd();
  c1->SetGridx();
  c1->SetGridy();
  contour68->Draw("AP");
  contour68->GetXaxis()->SetLimits(0.,2.2);
  contour68->GetXaxis()->SetTitle("#mu_{ttH}");
  contour68->GetYaxis()->SetRangeUser(0.,2.2);
  contour68->GetYaxis()->SetTitle("#mu_{HH}");
  c1->Update();
}

void drawContour(string infilename68, string infilename95, string label="")
{
  gStyle->SetOptTitle(0);
  TFile* infile68 = new TFile(infilename68.c_str(),"READ");
  TTree* intree68 = (TTree*) infile68->Get("limit");
  TCanvas *c = new TCanvas("def","def",600,600);
  int Npoints68 = intree68->Draw("mu_hh:mu_tth","","");
  TGraph* contour68 = new TGraph(Npoints68,intree68->GetV2(),intree68->GetV1());
  contour68->SetFillStyle(0);
  contour68->SetMarkerStyle(20);
  contour68->SetTitle("68% C.L. contour");

  TFile* infile95 = new TFile(infilename95.c_str(),"READ");
  TTree* intree95 = (TTree*) infile95->Get("limit");
  c->cd();
  int Npoints95 = intree95->Draw("mu_hh:mu_tth","","");
  TGraph* contour95 = new TGraph(Npoints95,intree95->GetV2(),intree95->GetV1());
  contour95->SetMarkerStyle(20);
  contour95->SetFillStyle(0);
  contour95->SetMarkerColor(kRed);
  contour95->SetTitle("95% C.L. contour");

  TCanvas *c1 = new TCanvas("plot","plot",600,600);
  c1->cd();
  c1->SetGridx();
  c1->SetGridy();
  contour68->Draw("AP");
  contour68->GetXaxis()->SetLimits(0.,3);
  contour68->GetXaxis()->SetTitle("#mu_{ttH}");
  contour68->GetYaxis()->SetRangeUser(0.,3);
  contour68->GetYaxis()->SetTitle("#mu_{HH}");

  contour95->Draw("P SAME");
  c1->BuildLegend();

  TLatex title;
  title.SetNDC();
  title.DrawLatex(0.1,0.95,label.c_str());
  c1->Update();
}
