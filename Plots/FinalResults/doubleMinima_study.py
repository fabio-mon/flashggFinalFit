import os,sys,copy,math
import numpy as np
import shutil
import json
import ROOT as r
from optparse import OptionParser
from ROOT import TCanvas,TGraph,TLegend
from array import array


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



parser = OptionParser()
parser.add_option("-y","--years", default='2018',help="years to consider")
parser.add_option("-c","--cats",default="DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11")
parser.add_option("--hhReweightDir",default='/work/nchernya/DiHiggs/inputs/18_02_2020/categorizedTrees/kl_kt_finebinning/',help="hh reweighting directory with all txt files" )
parser.add_option("--outdir", help="Output directory ")
parser.add_option("--outtag", help="Output tag ")
(options,args)=parser.parse_args()

years = options.years.split(',')
cats = options.cats.split(',')

kl_dependency = {}
kl_fit = {}
for cat in cats:
  kl_dependency[cat] = {}
  kl_fit[cat] = {}
  for year in years :
    kl_dependency[cat][year]={} 
    kl_dependency[cat][year]['kl']=[]
    kl_dependency[cat][year]['yeild_change']=[]


with open(options.hhReweightDir+"config.json","r") as rew_json:
  rew_dict = json.load(rew_json)
for ikl in range(0,rew_dict['Nkl']):
   kl = rew_dict['klmin'] + ikl*rew_dict['klstep']
   kl_str = ("{:.6f}".format(kl)).replace('.','d').replace('-','m') 
   for ikt in range(0,rew_dict['Nkt']):
      kt = rew_dict['ktmin'] + ikt*rew_dict['ktstep']
      kt_str = ("{:.6f}".format(kt)).replace('.','d').replace('-','m') 

      for year in years:
        rew_values = [] #for 12 cats
        with open(options.hhReweightDir+"reweighting_%s_kl_%s_kt_%s.txt"%(year,kl_str,kt_str),"r") as rew_values_file:
          for line in rew_values_file.readlines():
            rew_values.append(float(line.strip()))
        for cat_num,c in enumerate(cats):
             rew = rew_values[cat_num]
             kl_dependency[c][year]['kl'].append(kl)
             kl_dependency[c][year]['yeild_change'].append(rew)


xmin=-20.4
xmax=31.4
y_theo_scale = 31.05*0.58*0.00227*2  #new most updated x-sec
myFunc = r.TF1 ("myFunc", functionGF_kl_wrap, xmin, xmax, 1)
myFunc.SetParameter(0, y_theo_scale) ### norm scale

year=years[0]
c1 = TCanvas("c","",900,300)
c1.Divide(3,1)
colors = [r.kBlue-6,r.kGreen+1,r.kOrange+0,r.kRed+0]  #reverse order
cat_map = {}
cat_map['MVA0'] = 'DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3'
cat_map['MVA1'] = 'DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7'
cat_map['MVA2'] = 'DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11'
maximum = [2,6,8]
mx_map = 'MX<385(GeV),385<MX<510(GeV),510<MX<600(GeV),MX>600(GeV),MX<330(GeV),330<MX<360(GeV),360<MX<540(GeV),MX>540(GeV),MX<330(GeV),330<MX<375(GeV),375<MX<585(GeV),MX>585(GeV)'.split(',')
for mva_cat,mva in enumerate('MVA0,MVA1,MVA2'.split(',')):
  c1.cd(mva_cat+1)
  graphs = []
  legend = TLegend(0.3,0.65,0.55,0.9)
  legend.SetBorderSize(0)
  legend.SetFillStyle(-1)
  legend.SetTextFont(42)
  legend.SetTextSize(0.04)
  #for cat_num,c in enumerate(cats):
  for c_map_num,cat in enumerate(reversed(cat_map[mva].split(','))):
    c = cat#real category 
    n = len(kl_dependency[c][year]['kl'])
    kl_array, rew_array = array( 'd' ), array( 'd' )
    for i in range(0,n):
      kl_array.append(kl_dependency[c][year]['kl'][i])
      #yield_ratio = kl_dependency[c][year]['yeild_change'][i]*myFunc.Eval(kl_array[i])/y_theo_scale
      yield_ratio = kl_dependency[c][year]['yeild_change'][i]*myFunc.Eval(kl_array[i])
      rew_array.append(yield_ratio)
    gr = TGraph( n, kl_array, rew_array )
    if c_map_num==0 : gr.SetTitle(mva)
    gr.SetMarkerStyle(20+c_map_num)
    gr.SetMarkerSize(0.6)
    gr.SetMarkerColor(colors[c_map_num])
    gr.GetHistogram().SetMaximum(maximum[mva_cat])          
    gr.GetXaxis().SetTitle( '#kappa_{#lambda}=#lambda_{HHH}/#lambda_{SM}' )
    gr.GetYaxis().SetTitle( 'Signal yields' )
    gr.GetXaxis().SetTitleSize(0.047)
    if c_map_num==0 : gr.Draw("AP")
    else : gr.Draw('Psame')
    r.gDirectory.Append(gr)
    graphs.append(gr)
    legend.AddEntry(gr,cat.replace("DoubleHTag_","CAT ")+', '+mx_map[int(cat[-1])],"P")
  legend.Draw("same")
  r.gDirectory.Append(legend)
c1.Update()
c1.Draw()
out_name = '%s/yeilds_ratio_kl_xsec_%s_study'%(options.outdir,options.outtag)
c1.Print( out_name+'.pdf','pdf')

