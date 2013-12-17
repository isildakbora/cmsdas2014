#!usr/bin/python
import sys, getopt
import ROOT
from ROOT import TFile, TH1F, THStack, TCanvas, TMath, gROOT, gPad
from setTDRStyle import setTDRStyle

var    = ''
xmin   = 0.0
xmax   = 0.0
rebin  = 1
xtitle = ''
logy   = True

opts, args = getopt.getopt(sys.argv[1:],'v:x:y:r:t:l:',['var=','xmin=','xmax=','rebin=','xtitle=','logy='])

for opt, arg in opts:
  if opt in ('-v','--var'):
    var = arg
  elif opt in ('-x','--xmin'):
    xmin = float(arg)
  elif opt in ('-y','--xmax'):
    xmax = float(arg)
  elif opt in ('-r','--rebin'):
    rebin = int(arg)
  elif opt in ('-t','--xtitle'):
    xtitle = arg
  elif opt in ('-l','--logy'):
    logy = arg

gROOT.Reset()
setTDRStyle()
gROOT.ForceStyle()
gROOT.SetStyle('tdrStyle')

fileNames = ['QCD500','QCD1000','RS2000','data']
xsections = [8426.,204.,4.083e-3,1.]
colorF    = [ROOT.kBlue-9,ROOT.kBlue-8,ROOT.kWhite,ROOT.kBlack]
colorL    = [ROOT.kBlack,ROOT.kBlack,ROOT.kRed,ROOT.kBlack]
hist      = []
LUMI      = 19700.
#---- open the files --------------------
i_f = 0
for f in fileNames:
  inf = TFile('dijetHisto_'+f+'_signal.root')
  print inf.GetName()
  
  Nev = inf.Get('TriggerPass').GetBinContent(1)
  wt = 1.0
  if i_f < 3:
    wt = LUMI*xsections[i_f]/Nev
  
  h = inf.Get('h_'+var)
  h.Scale(wt)
  h.Rebin(rebin)
  h.SetDirectory(0)
  h.SetFillColor(colorF[i_f])
  h.SetLineColor(colorL[i_f])
  h.SetMarkerColor(colorL[i_f])
  hist.append(h)
   
  i_f += 1

NQCD = hist[0].Integral()+hist[1].Integral()
NDAT = hist[3].Integral()
kFactor = NDAT/NQCD
print kFactor

hist[0].Scale(kFactor)
hist[1].Scale(kFactor)

histQCD = hist[0].Clone('histQCD')
histQCD.Add(hist[1])

hsQCD = THStack('QCD','QCD')

hsQCD.Add(hist[0])
hsQCD.Add(hist[1])

#----- Drawing -----------------------
can = TCanvas('can_'+var,'can_'+var,900,600)
if logy:
  gPad.SetLogy()
hAux = hist[3].Clone('aux')
hAux.Reset()
hAux.GetXaxis().SetRangeUser(xmin,xmax)
hAux.GetXaxis().SetTitle(xtitle)
hAux.SetMaximum(1.2*TMath.Max(hist[3].GetBinContent(hist[3].GetMaximumBin()),histQCD.GetBinContent(histQCD.GetMaximumBin())))
hAux.SetMinimum(0.01)
hAux.Draw()
hsQCD.Draw('same hist')
hist[3].Draw('same E')
hist[2].Draw('same hist')
gPad.RedrawAxis()
    
#----- keep the GUI alive ------------
if __name__ == '__main__':
  rep = ''
  while not rep in ['q','Q']:
    rep = raw_input('enter "q" to quit: ')
    if 1 < len(rep):
      rep = rep[0]
