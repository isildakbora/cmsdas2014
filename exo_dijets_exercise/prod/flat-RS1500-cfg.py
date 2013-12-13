import FWCore.ParameterSet.Config as cms 
process = cms.Process('myprocess')
process.load('FWCore.MessageService.MessageLogger_cfi')

process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
process.GlobalTag.globaltag = 'START53_V27::All'

process.TFileService=cms.Service("TFileService",fileName=cms.string('dijetTree.root'))
##-------------------- Define the source  ----------------------------
process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(-1))

from CMGTools.Production.datasetToSource import *
process.source = datasetToSource('CMS','/RSGravitonToWW_kMpl01_M-1500_Tune23_8TeV-herwigpp/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM','*.root')

#############   Format MessageLogger #################
process.MessageLogger.cerr.FwkReport.reportEvery = 1000

process.load('KKousour.CMGAnalysis.PAT_ca8jets_simple_cff')

##-------------------- User analyzer  --------------------------------
process.dijets     = cms.EDAnalyzer('DijetTreeProducer',
  jets             = cms.InputTag('patJetsCA8CHSwithNsub'),
  jetsPruned       = cms.InputTag('patJetsCA8CHSpruned'),
  met              = cms.InputTag('pfMet'),
  vtx              = cms.InputTag('goodOfflinePrimaryVertices'),
  mjjMin           = cms.double(0),
  ptMin            = cms.double(20),
  ## MC ########################################
  pu               = cms.untracked.InputTag('addPileupInfo'),
  ## trigger ###################################
  triggerAlias     = cms.vstring('Fat','PFHT650','PFNoPUHT650','HT750','HT550'),
  triggerSelection = cms.vstring(
    'HLT_FatDiPFJetMass750_DR1p1_Deta1p5_v*',
    'HLT_PFHT650_v*',
    'HLT_PFNoPUHT650_v*',
    'HLT_HT750_v*',  
    'HLT_HT550_v*'
  ),
  triggerConfiguration = cms.PSet(
    hltResults            = cms.InputTag('TriggerResults','','HLT'),
    l1tResults            = cms.InputTag(''),
    daqPartitions         = cms.uint32(1),
    l1tIgnoreMask         = cms.bool(False),
    l1techIgnorePrescales = cms.bool(False),
    throw                 = cms.bool(False)
  )
)
process.p = cms.Path(process.ca8Jets * process.dijets)
