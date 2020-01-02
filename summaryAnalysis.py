
import sys, os, glob, shutil, json, math, re, random
import ROOT
import analyzer as an
import config 

ROOT.gROOT.SetBatch()
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptTitle(0)

def drawAux(c):
    
    textLeft = ROOT.TLatex()
    textLeft.SetTextFont(42)
    textLeft.SetTextSize(0.04)
    textLeft.SetNDC()
    textLeft.DrawLatex(c.GetLeftMargin(), 0.96, "#bf{CMS} 904,#scale[0.75]{ #it{Preliminary}}")
        
    textRight = ROOT.TLatex()
    textRight.SetNDC()
    textRight.SetTextFont(42)
    textRight.SetTextSize(0.04)
    textRight.SetTextAlign(31)
    #textRight.DrawLatex(1.0-c.GetRightMargin(), 0.96, "S%d" % (scanid))
    
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

    cfg = config.cfg_CMS_FEB_904
    outputdir = "summaryResults"
    xMin = 6600
    xMax = 8000
    thrsEffScans = [347, 359, 353] # 200, 210, 220
    thrsnoiseScans = [355, 360, 354] # 200, 210, 220
    
    thrsMv = [200, 210, 220]
    thrsQ = [x*1.0/1.5 for x in thrsMv]
    colors = [ROOT.kBlue, ROOT.kRed, ROOT.kBlack]
    
    
    ### EFFICIENCY PLOT
    graphs_eff = [] # store all efficiency TGraps

    g_thrs_WP = ROOT.TGraphErrors()
    g_thrs_cls = ROOT.TGraphErrors()
    g_thrs_cmp = ROOT.TGraphErrors()
    g_thrs_noise = ROOT.TGraphErrors()

    for i,thrs in enumerate(thrsMv):

        tag = "CMS_FEB_efficiency"
        dir = "data/efficiency_%dmV" % (thrs)
        tagdir = "%s/%s" % (dir, tag)
        
        g_eff = ROOT.TGraphErrors()
        #g_eff = makeGraphDefault("eff_thrs_%d" % thrsMv[i], "HV_{eff} (V)", "Efficiency (%)")
    
    
        for j,CAENFile in enumerate(glob.glob("%s/*CAEN.root" % dir)):

            HVPoint = int(os.path.basename(CAENFile).split("_")[1][2:])
            dir__ = "%s/HV%s/" % (tagdir, HVPoint)
            
            CAEN = ROOT.TFile(CAENFile)
            HV = CAEN.Get("HVeff_%s" % cfg['topGapName']).GetMean()
            if HV < 20: HV = CAEN.Get("HVeff_%s" % cfg['botGapName']).GetMean()
            
            with open("%s/output.json" % (dir__)) as f_in: analyzerResults = json.load(f_in)
            analyzerResults = analyzerResults['output_parameters']
            
            g_eff.SetPoint(j, HV, 100.*analyzerResults['efficiencyMuon'])
            g_eff.SetPointError(j, 0, 100.*analyzerResults['efficiencyMuon_err'])
            
        graphs_eff.append(g_eff) 
        
        
        with open("%s/results.json" % (tagdir)) as f_in: analyzerResults = json.load(f_in)
        
        g_thrs_WP.SetPoint(i, thrsMv[i], analyzerResults['workingPoint_raw'])
        g_thrs_WP.SetPointError(i, 0, analyzerResults['workingPoint_err'])
        
        g_thrs_cls.SetPoint(i, thrsMv[i], analyzerResults['muonCLS'])
        g_thrs_cls.SetPointError(i, 0, analyzerResults['muonCLS_err'])
        
        g_thrs_cmp.SetPoint(i, thrsMv[i], analyzerResults['muonCMP'])
        g_thrs_cmp.SetPointError(i, 0, analyzerResults['muonCMP_err'])
        
        
    
    for i,thrs in enumerate(thrsMv):

        tag = "CMS_FEB_noise"
        dir = "data/noise_%dmV" % (thrs)
        tagdir = "%s/%s" % (dir, tag)
        dir__ = "%s/HV%s/" % (tagdir, 1)
        
        with open("%s/output.json" % (dir__)) as f_in: analyzerResults = json.load(f_in)
        analyzerResults = analyzerResults['output_parameters']

        g_thrs_noise.SetPoint(i, thrsMv[i], analyzerResults['noiseRate'])
        #g_thrs_noise.SetPointError(i, 0, analyzerResults['muonCMP_err'])
        


    
    # do ploting and fitting
    c = ROOT.TCanvas("c1", "c1", 800, 800)
    c.SetLeftMargin(0.12)
    c.SetRightMargin(0.05)
    c.SetTopMargin(0.05)
    c.SetBottomMargin(0.1)
    c.Clear()
    
    params = ROOT.TLatex()
    params.SetTextFont(42)
    params.SetTextSize(0.04)
    params.SetNDC()
    

    ############################
    # efficiency curves
    ############################  
    for i,g in enumerate(graphs_eff):
        
        g = setGraphStyle(g, "HV_{eff} (V)", "Efficiency (%)")
        g.GetYaxis().SetRangeUser(0,100)
        g.GetXaxis().SetRangeUser(xMin, xMax)
        g.SetLineWidth(2)
        g.SetLineColor(colors[i])
        g.SetMarkerStyle(20)
        g.SetMarkerColor(colors[i])
        if i == 0: g.Draw("AP")
        else: g.Draw("P SAME")
        
        sigmoid = ROOT.TF1("sigmoid","[0]/(1+exp([1]*([2]-x)))", xMin, xMax)
        sigmoid.SetParName(0,"#epsilon_{max}");
        sigmoid.SetParName(1,"#lambda");
        sigmoid.SetParName(2,"HV_{50%}");
        sigmoid.SetParameter(0, 0.98); 
        sigmoid.SetParameter(1, 0.011); 
        sigmoid.SetParameter(2, 6700);   
        sigmoid.SetLineColor(colors[i])

        g.Fit("sigmoid")
        emax = sigmoid.GetParameter(0)
        lam = sigmoid.GetParameter(1)
        hv50 = sigmoid.GetParameter(2)

        WP = (math.log(19)/lam + hv50 + 150)
        
        params.DrawLatex(0.52, 0.5-i*0.12, "#bf{#color[%s]{V_{thrs} = %d mV #approx %d fC}}" % (colors[i], thrsMv[i], thrsQ[i]))
        params.DrawLatex(0.52, 0.45-i*0.12, "#color[%s]{WP = %d V (%.1f %%)}" % (colors[i], WP, sigmoid.Eval(WP)))
        
    params.DrawLatex(0.15, 0.9, "#bf{CMS Front-End electronics}")
    params.DrawLatex(0.15, 0.85, "1.4 mm")
    drawAux(c)
    
    c.SaveAs("%s/muonEfficiency.png" % outputdir)
    c.SaveAs("%s/muonEfficiency.pdf" % outputdir)        
    c.SaveAs("%s/muonEfficiency.C" % outputdir)      
    

        
    ############################
    # working point
    ############################  
    c.Clear()
    g_thrs_WP = setGraphStyle(g_thrs_WP, "V_{thrs} (mV)", "Working Point (V)")
    #g_thrs_WP.GetYaxis().SetRangeUser(0,15)
    g_thrs_WP.GetXaxis().SetRangeUser(0.9*min(thrsMv), 1.1*max(thrsMv))
    g_thrs_WP.Draw("AP")
    params.DrawLatex(0.15, 0.9, "#bf{CMS Front-End electronics}")
    params.DrawLatex(0.15, 0.85, "1.4 mm")
    drawAux(c)
    c.SaveAs("%s/thrs_WP.png" % outputdir)
    c.SaveAs("%s/thrs_WP.pdf" % outputdir)   
    c.SaveAs("%s/thrs_WP.C" % outputdir)     
    
    
    ############################
    # cluster size
    ############################  
    c.Clear()
    g_thrs_cls = setGraphStyle(g_thrs_cls, "V_{thrs} (mV)", "Muon cluster size")
    g_thrs_cls.GetYaxis().SetRangeUser(0,4)
    g_thrs_cls.GetXaxis().SetRangeUser(0.9*min(thrsMv), 1.1*max(thrsMv))
    g_thrs_cls.Draw("AP")
    params.DrawLatex(0.15, 0.9, "#bf{CMS Front-End electronics}")
    params.DrawLatex(0.15, 0.85, "1.4 mm")
    drawAux(c)
    c.SaveAs("%s/thrs_CLS.png" % outputdir)
    c.SaveAs("%s/thrs_CLS.pdf" % outputdir) 
    c.SaveAs("%s/thrs_CLS.C" % outputdir) 
    
    
    ############################
    # cluster multiplicity
    ############################ 
    c.Clear()
    g_thrs_cmp = setGraphStyle(g_thrs_cmp, "V_{thrs} (mV)", "Muon cluster multiplicity")
    g_thrs_cmp.GetYaxis().SetRangeUser(0,2)
    g_thrs_cmp.GetXaxis().SetRangeUser(0.9*min(thrsMv), 1.1*max(thrsMv))
    g_thrs_cmp.Draw("AP")
    params.DrawLatex(0.15, 0.9, "#bf{CMS Front-End electronics}")
    params.DrawLatex(0.15, 0.85, "1.4 mm")
    drawAux(c)
    c.SaveAs("%s/thrs_CMP.png" % outputdir)
    c.SaveAs("%s/thrs_CMP.pdf" % outputdir) 
    c.SaveAs("%s/thrs_CMP.C" % outputdir)
    
    
    ############################
    # noise
    ############################ 
    c.Clear()
    g_thrs_noise = setGraphStyle(g_thrs_noise, "V_{thrs} (mV)", "Noise rate (Hz/cm^{2})")
    g_thrs_noise.GetYaxis().SetRangeUser(0,1)
    g_thrs_noise.GetXaxis().SetRangeUser(0.9*min(thrsMv), 1.1*max(thrsMv))
    g_thrs_noise.Draw("AP")
    params.DrawLatex(0.15, 0.9, "#bf{CMS Front-End electronics}")
    params.DrawLatex(0.15, 0.85, "1.4 mm")
    drawAux(c)
    c.SaveAs("%s/thrs_noiseRate.png" % outputdir)
    c.SaveAs("%s/thrs_noiseRate.pdf" % outputdir) 
    c.SaveAs("%s/thrs_noiseRate.C" % outputdir) 
  