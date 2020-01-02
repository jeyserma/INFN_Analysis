
import sys, os, glob, shutil, json, math, re, random
import ROOT
import analyzer as an
import config 

ROOT.gROOT.SetBatch()
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptTitle(0)

def atoi(text):
    return int(text) if text.isdigit() else text
def natural_keys(text):
    return [ atoi(c) for c in re.split('(\d+)',text) ]


def drawAux(c):
    
    textLeft = ROOT.TLatex()
    textLeft.SetTextFont(42)
    textLeft.SetTextSize(0.04)
    textLeft.SetNDC()
    textLeft.DrawLatex(c.GetLeftMargin(), 0.96, "#bf{CMS} 904,#scale[0.75]{ #it{Work in progress}}")
        
    textRight = ROOT.TLatex()
    textRight.SetNDC()
    textRight.SetTextFont(42)
    textRight.SetTextSize(0.04)
    textRight.SetTextAlign(31)
    textRight.DrawLatex(1.0-c.GetRightMargin(), 0.96, "S%d" % (scanid))
    
def setGraphStyle(g, xlabel, ylabel):

    g.SetLineWidth(2)
    g.SetLineColor(ROOT.kBlue)
    g.SetMarkerStyle(20)
    g.SetMarkerColor(ROOT.kBlue)
    g.GetXaxis().SetTitle(xlabel)
    g.GetYaxis().SetTitle(ylabel)
    g.GetYaxis().SetTitleOffset(1.8)
    g.GetYaxis().SetLabelOffset(2.0*g.GetYaxis().GetLabelOffset())
    g.GetXaxis().SetTitleOffset(1.2)
    g.GetXaxis().SetLabelOffset(2.0*g.GetXaxis().GetLabelOffset())
        
    return g


if __name__ == "__main__":

    ## tag: all the plots and results will be saved in a directory with its tagname
    tag = "INFN_noise"
    
    ## config: specify the configuration containing the mapping and strip dimensions (see config.py)
    cfg = config.cfg_GRAPHITE_HIGH
    
    ## dir: ROOT directory of all raw data files 
    dir = "."
    
    ## xMin, xMax: typical voltage range for the analysis 
    xMin, xMax = 6000, 8000
    

    
    ##############################################################################################
    outputdir = "%s/%s/" % (dir, tag)
    #if os.path.exists(outputdir): shutil.rmtree(outputdir) # delete output dir, if exists
    if not os.path.exists(outputdir):os.makedirs(outputdir) # make output dir
    
    
    HVeff = [] # storage of HV eff points
    out = {}
    
    # prepare TGraphs
    g_iMon_BOT = ROOT.TGraphErrors()
    g_iMon_TOP = ROOT.TGraphErrors()
    g_noise = ROOT.TGraphErrors()


    iMonMax = -999

    
    # get the scan ID from the ROOT file
    files = glob.glob("%s/*CAEN.root" % dir)
    if len(files) == 0: sys.exit("No ROOT files in directory") 
    scanid = int(re.findall(r'\d+', files[0])[0])
    
    # get all ROOT files in the dir
    files.sort(key=natural_keys) # sort on file name, i.e. according to HV points
    for i,CAENFile in enumerate(files):
        
        HVPoint = int(os.path.basename(CAENFile).split("_")[1][2:])
        print "Analyze HV point %d " % HVPoint
        
        
        saveDir = outputdir + "HV%d/" % HVPoint
        if not os.path.exists(saveDir): os.makedirs(saveDir)

        
        analyzer = an.Analyzer(dir, saveDir, scanid, HVPoint, "noise")
        analyzer.loadConfig(cfg)
        analyzer.setVerbose(1)    
        analyzer.timeStripProfile2D()
        analyzer.timeProfile()
        analyzer.stripProfile()
        #analyzer.eventDisplay(-1)
        analyzer.write()
        
        # load CAEN for HV and currents
        CAEN = ROOT.TFile(CAENFile)
        current_TOP = CAEN.Get("Imon_%s" % cfg['topGapName']).GetMean()
        current_BOT = CAEN.Get("Imon_%s" % cfg['botGapName']).GetMean()
        HV = CAEN.Get("HVeff_%s" % cfg['topGapName']).GetMean()
        if HV < 20: HV = CAEN.Get("HVeff_%s" % cfg['botGapName']).GetMean()
        HVeff.append(HV)
        
        if HV > xMax: xMax = HV
        if HV < xMin: xMin = HV
        
        CAEN.Close()
        
        # load analyzer results
        with open("%s/output.json" % (saveDir)) as f_in: analyzerResults = json.load(f_in)
        analyzerResults = analyzerResults['output_parameters']
        

        if current_BOT > iMonMax: iMonMax = current_BOT
        if current_TOP > iMonMax: iMonMax = current_TOP
        g_iMon_BOT.SetPoint(i, HV, current_BOT)
        g_iMon_TOP.SetPoint(i, HV, current_TOP)

        g_noise.SetPoint(i, HV, analyzerResults['noiseRate'])

        

    # do plotting and fitting
    c = ROOT.TCanvas("c1", "c1", 800, 800)
    c.SetLeftMargin(0.12)
    c.SetRightMargin(0.05)
    c.SetTopMargin(0.05)
    c.SetBottomMargin(0.1)
    
    params = ROOT.TLatex()
    params.SetTextFont(42)
    params.SetTextSize(0.03)
    params.SetNDC()
    
    
    ############################
    # gap currents
    ############################
    c.Clear()
    g_iMon_BOT = setGraphStyle(g_iMon_BOT, "HV_{eff} (V)", "Current (#muA)")
    g_iMon_TOP = setGraphStyle(g_iMon_TOP, "HV_{eff} (V)", "Current (#muA)")

    g_iMon_BOT.Draw("ALP")
    g_iMon_BOT.GetYaxis().SetRangeUser(0, 1.1*iMonMax)
    
    g_iMon_TOP.SetLineColor(ROOT.kRed)
    g_iMon_TOP.SetMarkerColor(ROOT.kRed)
    g_iMon_TOP.Draw("SAME LP")
    
    params.DrawLatex(0.16, 0.9, "#color[4]{Current top gap}")
    params.DrawLatex(0.16, 0.85, "#color[2]{Current bottom gap}")

    drawAux(c)
    c.SaveAs("%s/gapCurrents.png" % outputdir)
    c.SaveAs("%s/gapCurrents.pdf" % outputdir)

    


    ############################
    # mean noise rate
    ############################    
    c.Clear()
    g_noise = setGraphStyle(g_noise, "HV_{eff} (V)", "Mean noise rate (Hz/cm^{2})")
    g_noise.Draw("ALP")
    drawAux(c)
    c.SaveAs("%s/meanNoiseRate.png" % outputdir)
    c.SaveAs("%s/meanNoiseRate.pdf" % outputdir) 
    
    
    
    
