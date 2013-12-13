#!usr/bin/python
import sys, getopt
import ROOT
from ROOT import TFile, TH1F, TCanvas, TPad
from ROOT import gROOT, gPad 
from ROOT import RooRealVar, RooDataHist, RooAddPdf, RooPlot, RooArgList, RooFit, RooGenericPdf
from setTDRStyle import setTDRStyle

applySub = False

opts, args = getopt.getopt(sys.argv[1:],'s:',['substructure='])

for opt, arg in opts:
  if opt in ('-s','--substructure'):
    applySub = arg

gROOT.Reset()
setTDRStyle()
gROOT.ForceStyle()
gROOT.SetStyle('tdrStyle')

if (applySub == True):
  filename = 'dijetHisto_data_signal_sub.root'
else:
  filename = 'dijetHisto_data_signal.root'

inf = TFile.Open(filename)
h   = inf.Get('h_mjj')

x = RooRealVar('mjj','mjj',900,4000)
NBINS = 62
p1 = RooRealVar('p1','p1',5,0,20)
p2 = RooRealVar('p2','p2',5,0,20)
p3 = RooRealVar('p3','p3',0.1,0,1)

model = RooGenericPdf('model','pow(1-@0/8000,@1)/pow(@0/8000,@2+@3*log(@0/8000))',RooArgList(x,p1,p2,p3))
roohist = RooDataHist('roohist','roohist',RooArgList(x),h)
res = model.fitTo(roohist)


can = TCanvas('can_Mjj_Data','can_Mjj_Data',900,600)
gPad.SetLogy() 
can.cd(1).SetBottomMargin(0.4);

frame1 = x.frame()
frame2 = x.frame();
roohist.plotOn(frame1,RooFit.Binning(NBINS))
model.plotOn(frame1)
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


#----- keep the GUI alive ------------
if __name__ == '__main__':
  rep = ''
  while not rep in ['q','Q']:
    rep = raw_input('enter "q" to quit: ')
    if 1 < len(rep):
      rep = rep[0]
