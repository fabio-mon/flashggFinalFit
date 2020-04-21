//g++ -Wall -o fggMergeWorkspaces.exe `root-config --cflags --glibs` -L $ROOTSYS/lib -lRooFitCore -lFoam -lMinuit -lMathMore fggMergeWorkspaces.cpp
// ROOT includes
#include "TROOT.h"
#include "TCanvas.h"
#include "TH1F.h"
#include "TH2F.h"
#include "TF1.h"
#include "TAxis.h"
#include "TString.h"
#include "TMath.h"
#include "TMatrixDSym.h"
#include "TMatrixD.h"
#include "TVectorD.h"
#include "TKey.h"
#include "TFile.h"
#include "TDirectory.h"
#include "TDirectoryFile.h"
#include "TChain.h"
#include "TList.h"
#include "TObject.h"
#include "TTree.h"
#include "TROOT.h"
#include "TSystem.h"

// RooFit includes
#include "RooDataHist.h"
#include "RooDataSet.h"
#include "RooRealVar.h"
#include "RooConstVar.h"
#include "RooFormulaVar.h"
#include "RooPlot.h"
#include "RooAddPdf.h"
#include "RooFitResult.h"
#include "RooArgSet.h"
#include "RooArgList.h"
#include "RooAddPdf.h"
#include "RooGlobalFunc.h"
#include "RooCmdArg.h"

// RooStats includes
#include "RooWorkspace.h"

// standard includes
#include <cmath>
#include <ctime>
#include <iostream>
#include <fstream>
#include <map>
#include <unordered_map>
#include <set>
#include <vector>
#include <iomanip>
#include <string>
#include <sstream>
#include <algorithm>
#include <iterator>

using namespace std;

vector<string>* GetListOfDatasets(RooWorkspace *ws)
{
  vector<string> *datasetnames = new vector<string>;
  auto datasets = ws->allData();
  for(auto category : datasets)
  {
    ostringstream ss;
    category->printName(ss);
    datasetnames->push_back( ss.str() );
  }
  return datasetnames;
}

int main( int argc, char *argv[] )
{
  //parse input
  std::vector<string> inputlist;
  std::string outputfilename = argv[1];
  for( int f = 2; f < argc; f++ ) 
    inputlist.push_back( argv[f] );

  //get category names list
  TFile  *inFile_forinit = new TFile(inputlist.at(0).c_str(),"READ");
  RooWorkspace *ws_forinit = (RooWorkspace*)inFile_forinit->Get("tagsDumper/cms_hgg_13TeV");
  vector<string> *datasetnames = GetListOfDatasets(ws_forinit);
  inFile_forinit->Close();
  if(ws_forinit)
    delete ws_forinit;

  string NoTag_category="";
  cout<<"List of categories:"<<endl;
  for(auto datasetname : *datasetnames)
  {
    cout<<"\t"<<datasetname<<endl;
    if(datasetname.find("NoTag") != string::npos)
      NoTag_category=datasetname;
  }

  system( Form("cp %s %s",inputlist.at(0).c_str(),outputfilename.c_str()) );

  if(NoTag_category!="")
  {
    cout<<"removing notag category"<<endl;
    TFile *outfile = new TFile(outputfilename.c_str(),"UPDATE");
    outfile->cd("tagsDumper");
    RooWorkspace *w_out = (RooWorkspace*)outfile->Get("tagsDumper/cms_hgg_13TeV");
    RooDataSet* notag_dataset = (RooDataSet*)w_out->data(NoTag_category.c_str());
    w_out->RecursiveRemove(notag_dataset);

    outfile->cd("tagsDumper");
    w_out->Write(w_out->GetName(),TObject::kOverwrite);
    outfile->Close();
    if(w_out)
      delete w_out;
  }
    
  //merge the inputs    
  for(unsigned ifile=1; ifile<inputlist.size(); ++ifile)
  {
    TFile  *inFile = new TFile(inputlist.at(ifile).c_str(),"READ");
    RooWorkspace *w_in = (RooWorkspace*)inFile->Get("tagsDumper/cms_hgg_13TeV");
    vector<string> *indatasetnames = GetListOfDatasets(w_in);    
    inFile->Close();
    if(w_in)
      delete w_in;

    for(auto indatasetname : *indatasetnames)
    {
      cout<<"doing dataset "<<indatasetname<<endl;
      TFile *outfile = new TFile(outputfilename.c_str(),"UPDATE");
      outfile->cd("tagsDumper");
      RooWorkspace *w_out = (RooWorkspace*)outfile->Get("tagsDumper/cms_hgg_13TeV");
      TFile  *inFile = new TFile(inputlist.at(ifile).c_str(),"READ");
      RooWorkspace *w_in = (RooWorkspace*)inFile->Get("tagsDumper/cms_hgg_13TeV");
      if(std::find(datasetnames->begin(), datasetnames->end(), indatasetname) != datasetnames->end())
	((RooDataSet*)w_out->data(indatasetname.c_str()))->append( *((RooDataSet*)(w_in->data(indatasetname.c_str()))) );
      else
	w_out->import( *((RooDataSet*)(w_in->data(indatasetname.c_str()))) );

      inFile->Close();
      outfile->cd("tagsDumper");
      w_out->Write(w_out->GetName(),TObject::kOverwrite);
      outfile->Close();
      if(w_in)
	delete w_in;
      if(w_out)
	delete w_out;
    }
  }


}


