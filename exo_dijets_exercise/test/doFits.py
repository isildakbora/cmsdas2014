#!usr/bin/python
import sys, getopt
import ROOT
from ROOT import TFile, TH1F, TCanvas, TPad
from ROOT import gROOT, gPad 
from ROOT import RooRealVar, RooDataHist, RooAddPdf, RooPlot, RooArgList, RooArgSet,  RooBernstein, RooCBShape, RooAddPdf, RooFit, RooGenericPdf, RooWorkspace
from setTDRStyle import setTDRStyle

import optparse
usage = "usage: %prog [options]"
parser = optparse.OptionParser(usage)
parser.add_option("-s","--fitSig",action="store_true",default=False,dest="fitSig")
parser.add_option("-d","--fitDat",action="store_true",default=False,dest="fitDat")
parser.add_option("-m","--mass",action="store",type="int",dest="mass",default=0)
(options, args) = parser.parse_args()

mass = options.mass
fitSig = options.fitSig
fitDat = options.fitDat

#opts, args = getopt.getopt(sys.argv[1:],'m:s:d',['mass=','figSig=','fitDat='])
#
#for opt, arg in opts:
#  if opt in ('-m','--mass'):
#    mass = arg
#  if opt in ('-s','--fitSig'):
#    fitSig = True
#  if opt in ('-d','--fitDat'):
#    fitDat = True
    
gROOT.Reset()
setTDRStyle()
gROOT.ForceStyle()
gROOT.SetStyle('tdrStyle')

# -----------------------------------------
# get histograms
filenameSig = 'dijetHisto_RS'+str(mass)+'_signal.root'
filenameDat = 'dijetHisto_data_signal.root'

infSig = TFile.Open(filenameSig)
hSig   = infSig.Get('h_mjj')
hSig.Rebin(20)

infDat = TFile.Open(filenameDat)
hDat   = infDat.Get('h_mjj')
#hDat.Rebin(20)

# -----------------------------------------
# define observable
x = RooRealVar('mjj','mjj',900,4500)

if fitSig: 

    # define parameters for signal fit
    m = RooRealVar('mean','mean',float(mass),float(mass)-200,float(mass)+200)
    s = RooRealVar('sigma','sigma',0.1*float(mass),0,10000)
    a = RooRealVar('alpha','alpha',1,-10,10)
    n = RooRealVar('n','n',1,0,100)
    sig = RooCBShape('sig','sig',x,m,s,a,n)        

    p  = RooRealVar('p','p',1,0,5)
    x0 = RooRealVar('x0','x0',1000,100,5000)

    bkg = RooGenericPdf('bkg','1/(exp(pow(@0/@1,@2))+1)',RooArgList(x,x0,p))

    fsig= RooRealVar('fsig','fsig',0.5,0.,1.)
    signal = RooAddPdf('signal','signal',sig,bkg,fsig)

    # -----------------------------------------
    # fit signal
    canS = TCanvas('can_Mjj'+str(mass),'can_Mjj'+str(mass),900,600)
    hSig.Draw()
    gPad.SetLogy() 

    roohistSig = RooDataHist('roohist','roohist',RooArgList(x),hSig)

    signal.fitTo(roohistSig)
    frame = x.frame()
    roohistSig.plotOn(frame)
    signal.plotOn(frame)
    signal.plotOn(frame,RooFit.Components('bkg'),RooFit.LineColor(ROOT.kRed),RooFit.LineWidth(2),RooFit.LineStyle(ROOT.kDashed))
    frame.Draw('same')


if fitDat: 

    # -----------------------------------------
    # define parameters for background
    NBINS = 180
    p1 = RooRealVar('p1','p1',7,0,10)
    p2 = RooRealVar('p2','p2',5,0,10)
    p3 = RooRealVar('p3','p3',0.1,0,5)

    background = RooGenericPdf('background','(pow(1-@0/8000,@1)/pow(@0/8000,@2+@3*log(@0/8000)))',RooArgList(x,p1,p2,p3))
    roohistBkg = RooDataHist('roohist','roohist',RooArgList(x),hDat)
    res = background.fitTo(roohistBkg)

    # -----------------------------------------
    # plot background
    canB = TCanvas('can_Mjj_Data','can_Mjj_Data',900,600)
    gPad.SetLogy() 
    canB.cd(1).SetBottomMargin(0.4);

    frame1 = x.frame()
    frame2 = x.frame();
    roohistBkg.plotOn(frame1,RooFit.Binning(NBINS))
    background.plotOn(frame1)
    hpull = frame1.pullHist();
    frame2.addPlotable(hpull,'p');

    frame1.SetMinimum(0.5)
    frame1.GetXaxis().SetTitle('')
    frame1.GetXaxis().SetLabelSize(0.0)
    frame1.GetYaxis().SetTickLength(0.06)
    frame1.Draw()

    pad = TPad('pad','pad',0.,0.,1.,1.);
    pad.SetTopMargin(0.6);
    pad.SetFillColor(0);
    pad.SetFillStyle(0);
    pad.Draw();
    pad.cd(0);
    frame2.SetMinimum(-5)
    frame2.SetMaximum(5)
    frame2.GetYaxis().SetNdivisions(505)
    frame2.GetXaxis().SetTitleOffset(0.9)
    frame2.GetYaxis().SetTitleOffset(0.8)
    frame2.GetYaxis().SetTickLength(0.06)
    frame2.GetYaxis().SetTitleSize(0.05)
    frame2.GetYaxis().SetLabelSize(0.03)
    frame2.GetYaxis().SetTitle('(Data-Fit)/Error')
    frame2.GetXaxis().SetTitle('m_{jj} (GeV)')
    frame2.Draw();


if fitSig and fitDat:
    
    # -----------------------------------------
    # write everything to a workspace to make a datacard
    w = RooWorkspace('w','workspace')
    getattr(w,'import')(signal)
    getattr(w,'import')(background)
    getattr(w,'import')(roohistBkg,RooFit.Rename("data_obs"))  
    w.Print()
    w.writeToFile('RS'+str(mass)+'_workspace.root')
    
    # -----------------------------------------
    # write a datacard
    LUMI = 19.7;
    signalCrossSection = 0.004083e3;
    signalEfficiency = 0.2941;
    ExpectedSignalRate = signalCrossSection*LUMI*signalEfficiency;
    # ... to be continued ...

#----- keep the GUI alive ------------
if __name__ == '__main__':
  rep = ''
  while not rep in ['q','Q']:
    rep = raw_input('enter "q" to quit: ')
    if 1 < len(rep):
      rep = rep[0]
