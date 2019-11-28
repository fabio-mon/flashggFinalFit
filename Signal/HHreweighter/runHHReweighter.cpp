#include <iostream>
#include "TFile.h"
#include "TTree.h"
#include "TChain.h"
#include "TString.h"
#include "TH1F.h"
#include "TH2F.h"
#include "TDirectory.h"
#include "TLorentzVector.h"
#include <map>
#include <fstream>
#include "HHReweight5D.h"
#include <vector>
#include <boost/algorithm/string/replace.hpp>


using namespace std;

//c++ -lm -o runHH runHHReweighter.cpp HHReweight5D.cpp `root-config --glibs --cflags`
int main ()
{
	 int Nkl=51;
	 float klstep = 0.5;
    int Nkt=1;
	 float ktstep = 0.;
	 float klmin=-10;
	 float klmax=15;
	 float ktmin=1;
	 float ktmax=1;

	 TString s;
	 TString year = "2016";
    TString inMapFile   = "HHreweight_2016nodes_18092019.root" ;
//   TString inMapFile   = "HHreweight_2017nodes_08072019.root" ;
//    TString inMapFile   = "HHreweight_2018nodes_08072019.root" ;
	 TString addname = "_13TeV_125_13TeV_";
	 TString processName = "hh";
    TString inputDir = "/work/nchernya/DiHiggs/inputs/25_10_2019/trees/";
    TString outDir = "kl_kt_finebinning/";
	 TString filename = s.Format("output_%s_%s.root",processName.Data(),year.Data()); 

    string coeffFile  = "coefficientsByBin_extended_3M_costHHSim_19-4.txt";
    TString inHistoName = "allHHNodeMap2D";
    TFile* fHHDynamicRew = new TFile(inputDir+inMapFile);
    TH2* hhreweighterInputMap =  (TH2*) fHHDynamicRew->Get(inHistoName);
    HHReweight5D* hhreweighter;
    hhreweighter = new HHReweight5D(((string)inputDir).append(coeffFile), hhreweighterInputMap,inputDir);

	 TString cats[13] = {}; 
	 TString cats_names[13] = {}; 
	 const int NCATS=12;
	 const int NGENCATS=13;
	 for (int i=0;i<NCATS;i++){
		cats[i] = s.Format("DoubleHTag_%d",i);
		cats_names[i] = s.Format("DoubleHTag_%d",i);
	 }
	 cats[NGENCATS-1] = "NoTag_0";

	 float  mhh, cosTheta, weight, benchmark_reweight_SM, benchmark_reweight_box;
  
    TFile* fIn = TFile::Open(inputDir+filename);
	 TH1F *hMhh_kl10 = new TH1F("hMhh_kl5","hMhh_kl5",100,250,1000);/// only for a test
	 TDirectory* dirGen1 = fIn->GetDirectory("genDiphotonDumper");
	 TDirectory* dirGen2 = dirGen1->GetDirectory("trees");
    float sum_gen_w_SM= 0;
	 std::vector<float> sum_gen_w(Nkl*Nkt, 0.);
	 for (int cat=0;cat<NGENCATS;cat++){
    	TTree *ch_gen = (TTree*)dirGen2->Get(s.Format("%s%s%s%s",processName.Data(),year.Data(),addname.Data(),cats[cat].Data()));
      ch_gen->SetBranchAddress("benchmark_reweight_SM", &benchmark_reweight_SM);
      ch_gen->SetBranchAddress("benchmark_reweight_box", &benchmark_reweight_box);
	   ch_gen->SetBranchAddress("weight", &weight);	
		ch_gen->SetBranchAddress("absCosThetaStar_CS", &cosTheta);
      ch_gen->SetBranchAddress("mhh", &mhh);
    	for (int iEv = 0; iEv<ch_gen->GetEntries(); ++iEv){
    		ch_gen->GetEntry(iEv);
    		if ((iEv % 100000 == 0) && (iEv!=0)) cout << "Event: " << iEv << endl;
			sum_gen_w_SM += weight*hhreweighter->getWeight(1.,1., 0., 0., 0., mhh, cosTheta); 			
			for(int ikl=0; ikl<Nkl; ++ikl){
				float kl = klmin + ikl*klstep;
				for(int ikt=0; ikt<Nkt; ++ikt){
	  				float kt = ktmin + ikt*ktstep; 
					sum_gen_w[ikl+Nkl*ikt] += weight*hhreweighter->getWeight(kl, kt, 0., 0., 0., mhh, cosTheta);
               if (kl==10.) hMhh_kl10->Fill(mhh,weight*hhreweighter->getWeight(kl, kt, 0., 0., 0., mhh, cosTheta)); // for a test only	
				}
			}		
      }
    }



	 TDirectory* dir1 = fIn->GetDirectory("tagsDumper");
	 TDirectory* dir2 = dir1->GetDirectory("trees");
	 float sum_w_cats_SM[NCATS] = {0,0,0,0,0,0,0,0,0,0,0,0};
	 std::vector<vector<float>> sum_w_cats(Nkl*Nkt, vector<float>(NCATS,0.));
	 for (int cat=0;cat<NCATS;cat++){
	   TTree *ch_reco = (TTree*)dir2->Get(s.Format("%s%s%s%s",processName.Data(),year.Data(),addname.Data(),cats[cat].Data()));
      ch_reco->SetBranchAddress("benchmark_reweight_SM", &benchmark_reweight_SM);
      ch_reco->SetBranchAddress("benchmark_reweight_box", &benchmark_reweight_box);
    	ch_reco->SetBranchAddress("weight", &weight);
   	ch_reco->SetBranchAddress("genAbsCosThetaStar_CS", &cosTheta);
    	ch_reco->SetBranchAddress("genMhh", &mhh);
   	for (int iEv = 0; iEv<ch_reco->GetEntries(); ++iEv){
       	ch_reco->GetEntry(iEv);
        	if ((iEv % 100000 == 0)&& (iEv!=0)) cout << "Event: " << iEv << endl;
			sum_w_cats_SM[cat] += weight*hhreweighter->getWeight(1.,1., 0., 0., 0., mhh, cosTheta); 			
			for(int ikl=0; ikl<Nkl; ++ikl){
				float kl = klmin + ikl*klstep;
				for(int ikt=0; ikt<Nkt; ++ikt){
	  				float kt = ktmin + ikt*ktstep; 
    	 			sum_w_cats[ikl+Nkl*ikt][cat] += weight*hhreweighter->getWeight(kl, kt, 0., 0., 0., mhh, cosTheta);			
				}
			}		
    	}
 	 }

	//std::map<string, float> dictionary = {0};
	//dictionary[cats_names[cat]] = reweight_cat[cat];
	float reweight_cat_SM[NCATS] = {0,0,0,0,0,0,0,0,0,0,0,0};
	for (int cat=0;cat<NCATS;cat++){
		reweight_cat_SM[cat] = sum_w_cats_SM[cat]/sum_gen_w_SM;
	}

	for(int ikl=0; ikl<Nkl; ++ikl){
		float kl = klmin + ikl*klstep;
		for(int ikt=0; ikt<Nkt; ++ikt){
	  		float kt = ktmin + ikt*ktstep; 
	 		float reweight_cat[NCATS] = {0,0,0,0,0,0,0,0,0,0,0,0};
		//	cout<<" kl  "<<kl<<endl;

			ofstream out;
			std::string output_kl = boost::replace_all_copy(std::to_string(kl), ".", "d");
			output_kl = boost::replace_all_copy(output_kl, "-", "m");
			output_kl = boost::replace_all_copy(output_kl, "+", "p");
			std::string output_kt = boost::replace_all_copy(std::to_string(kt), ".", "d");
			output_kt = boost::replace_all_copy(output_kt, "-", "m");
			output_kt = boost::replace_all_copy(output_kt, "+", "p");
			string out_txt = (string)inputDir + (string)outDir +"/reweighting_"+(string)year+"_kl_"+output_kl+"_kt_"+output_kt+".txt";
			out.open(out_txt);

	 		for (int cat=0;cat<NCATS;cat++){
				reweight_cat[cat] = sum_w_cats[ikl+Nkl*ikt][cat]/sum_gen_w[ikl+Nkl*ikt];
				reweight_cat[cat] /= reweight_cat_SM[cat];
			//	cout<<reweight_cat[cat]<<endl;
				out<<reweight_cat[cat]<<endl;
	 		}
		}
	}
/*
	string outroot_txt = (string)inputDir + (string)outDir +"/reweighting_root_"+(string)year+"_kl_5.root";
	TFile *file = new TFile("output.root","NEW");
	hMhh_kl10->Draw();
	hMhh_kl10->Write();
	file->Write();
	file->Close();
*/
	fIn->Close();
}

