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
import matplotlib.pyplot as plt
#####

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



scaleToXS = 1. # in fb for limit in xs of HH -> bbbb
y_theo_scale = 31.05*0.58*0.00227*2  #new most updated x-sec
BR_hhbbgg = 0.58*0.00227*2

x = np.linspace(-10,15,300)
nlo = eval_nnlo_xsec_ggF(x) * BR_hhbbgg
lo = functionGF(x,1., 0, 0, 0)*y_theo_scale
print x,nlo,lo 


fig = plt.figure()
#ax = fig.add_subplot(1, 1, 1)
#ax.spines['left'].set_position('center')
#ax.spines['bottom'].set_position('zero')
#ax.spines['right'].set_color('none')
#ax.spines['top'].set_color('none')
#ax.xaxis.set_ticks_position('bottom')
#ax.yaxis.set_ticks_position('left')
# plot the function
plt.plot(x,nlo, 'r',label='NLO')
plt.plot(x,lo, 'b',label='LO')
plt.xlabel('kl')
plt.ylabel('x-sec x BR [fb]')
plt.legend()
# show the plot
plt.savefig('nlo_lo.pdf')
