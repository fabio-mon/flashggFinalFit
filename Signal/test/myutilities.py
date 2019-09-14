#!/usr/bin/python
import sys
import os
import ROOT
from ROOT import * 

#from https://stackoverflow.com/questions/18715688/find-common-substring-between-two-strings
def longestSubstringFinder(string1, string2):
    answer = ""
    len1, len2 = len(string1), len(string2)
    for i in range(len1):
        match = ""
        for j in range(len2):
            if (i + j < len1 and string1[i + j] == string2[j]):
                match += string2[j]
            else:
                if (len(match) > len(answer)): answer = match
                match = ""
    return answer

def inferprocessname(infilename,wsname="tagsDumper/cms_hgg_13TeV"):
    infile = TFile(infilename)
    ws = infile.Get(wsname)
    dataset_list = ws.allData()
    datasetname_list = []
    for dataset in dataset_list:
        ss=ostringstream()	
        dataset.printName(ss)
        datasetname_list.append(ss.str())

    match=datasetname_list[0]
    for idataset in range(1,len(datasetname_list)):
       match = longestSubstringFinder(match,datasetname_list[idataset])
    infile.Close()
    match = match[:-1]#remove '_' at the end of the string 
    return match
    
