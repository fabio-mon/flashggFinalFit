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
parser.add_option("-y","--years", default='2016,2017,2018',help="years to consider")
parser.add_option("-c","--cats",default="DoubleHTag_0,DoubleHTag_1,DoubleHTag_2,DoubleHTag_3,DoubleHTag_4,DoubleHTag_5,DoubleHTag_6,DoubleHTag_7,DoubleHTag_8,DoubleHTag_9,DoubleHTag_10,DoubleHTag_11")
parser.add_option("--hhReweightDir",default='/work/nchernya/DiHiggs/inputs/25_10_2019/trees/kl_kt_finebinning/',help="hh reweighting directory with all txt files" )
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


c1 = TCanvas("c","",1200,900)
c1.Divide(4,3)
colors=[2,4,r.kGreen+2]
for cat_num,c in enumerate(cats):
  c1.cd(cat_num+1)
  graphs = []
  legend = TLegend(0.3,0.55,0.55,0.85)
  legend.SetBorderSize(0)
  legend.SetFillStyle(-1)
  legend.SetTextFont(42)
  legend.SetTextSize(0.07)
  fit = r.TF1("fit_%s"%c,"[0]*x*x+[1]*x+[2]",-30,30)
  fit.SetLineColor(r.kOrange)
  for y_num,year in enumerate(years) :
    n = len(kl_dependency[c][year]['kl'])
    kl_array, rew_array = array( 'd' ), array( 'd' )
    for i in range(0,n):
      kl_array.append(kl_dependency[c][year]['kl'][i])
      #yield_ratio = kl_dependency[c][year]['yeild_change'][i]*myFunc.Eval(kl_array[i])/y_theo_scale
      yield_ratio = kl_dependency[c][year]['yeild_change'][i]*myFunc.Eval(kl_array[i])
      rew_array.append(yield_ratio)
    gr = TGraph( n, kl_array, rew_array )
    if y_num==0 : gr.SetTitle(c)
    gr.SetMarkerStyle(21+y_num)
    gr.SetMarkerColor(colors[y_num])
    gr.GetXaxis().SetTitle( '#kappa_{#lambda}=#lambda_{HHH}/#lambda_{SM}' )
    gr.GetYaxis().SetTitle( 'yields scaling' )
    gr.GetXaxis().SetTitleSize(0.047)
    gr.GetYaxis().SetTitleSize(0.047)
    if y_num==0 : gr.Draw("AP")
    else : gr.Draw('Psame')
    r.gDirectory.Append(gr)
    graphs.append(gr)
    legend.AddEntry(gr,year,"P")
    if year=='2018':
       gr.Fit("fit_%s"%c)
       kl_fit[c]['p0'] = fit.GetParameter(0) 
       kl_fit[c]['p1'] = fit.GetParameter(1) 
       kl_fit[c]['p2'] = fit.GetParameter(2) 
  legend.AddEntry(fit,"Fit ax^{2}+bx+c","L")
  legend.Draw("same")
  r.gDirectory.Append(legend)
  r.gDirectory.Append(fit)
c1.Update()
c1.Draw()
out_name = '%s/yeilds_ratio_kl_xsec_%s'%(options.outdir,options.outtag)
c1.Print( out_name+'.pdf','pdf')

with open(out_name+"_fitparams.json","w") as fit_json:
  json.dump(kl_fit,fit_json)
