
import sys,os,glob,shutil,json,math,re
import ROOT
import analyzer as an
import config 


def drawAux(c, aux_right):
    
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
    textRight.DrawLatex(1.0-c.GetRightMargin(), 0.96, aux_right)
    
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
    tag = "INFN_clusterStudy"
    
    ## config: specify the configuration containing the mapping and strip dimensions (see config.py)
    cfg = config.cfg_GRAPHITE_HIGH
    
    ## HVPoint: HVpoint considered to perform the cluster study
    HVPoint = 6
    
    ## dir: ROOT directory of all raw data files 
    dir = "."
    

    ##############################################################################################
    outputdir = "%s/%s/" % (dir, tag)
    #if os.path.exists(outputdir): shutil.rmtree(outputdir) # delete output dir, if exists
    if not os.path.exists(outputdir):os.makedirs(outputdir) # make output dir

    saveDir = outputdir + "HV%d/" % HVPoint
    if not os.path.exists(saveDir): os.makedirs(saveDir)
   
    
    g_cls = ROOT.TGraphErrors()
    g_cmp = ROOT.TGraphErrors()
    
    times = [0, 0.2, 0.4, 0.6, 0.8, 1, 2, 3, 5, 10, 15, 20]
    times = [0, 2, 4, 6, 8, 10, 15, 20, 25]
    
    # get the scan ID from the ROOT file
    files = glob.glob("%s/*CAEN.root" % dir)
    if len(files) == 0: sys.exit("No ROOT files in directory") 
    scanid = int(re.findall(r'\d+', files[0])[0])
    
    analyzer = an.Analyzer(dir, saveDir, scanid, HVPoint, "efficiency")
    analyzer.loadConfig(cfg)
    analyzer.setVerbose(1)
    analyzer.timeProfile()
    analyzer.stripProfile()

    maxY = -999
    analyzer.setVerbose(0) # turn off plotting
    for i,t in enumerate(times):
    
        cls, cmp = analyzer.clusterization(t)
        g_cls.SetPoint(i, t, cls)
        g_cmp.SetPoint(i, t, cmp)
        if cls > maxY: maxY = cls
        if cmp > maxY: maxY = cmp
        
        

        
    # do plotting and fitting
    c = ROOT.TCanvas("c1", "c1", 800, 800)
    c.SetLeftMargin(0.12)
    c.SetRightMargin(0.05)
    c.SetTopMargin(0.05)
    c.SetBottomMargin(0.1)
    
    leg = ROOT.TLegend(0.2, 0.85, 0.8, 0.95)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0) #1001
    leg.SetFillColor(0)
    leg.SetNColumns(2)
    
    c.Clear()
    #c.SetLogy()
    g_cmp = setGraphStyle(g_cmp, "Clusterization #DeltaT (ns)", "Clusterization outcome")
    g_cls = setGraphStyle(g_cls, "Clusterization #DeltaT (ns)", "Clusterization outcome")
    
    g_cmp.GetYaxis().SetRangeUser(1, 1.1*maxY)
    g_cmp.GetXaxis().SetRangeUser(min(times), max(times))
    g_cmp.Draw("ALP")
    g_cmp.SetLineColor(ROOT.kRed)
    g_cmp.SetMarkerColor(ROOT.kRed)
    g_cls.Draw("SAME LP")
    
    leg.AddEntry(g_cmp, "Cluster multiplicity", "LP")
    leg.AddEntry(g_cls, "Cluster size", "LP")
    leg.Draw("SAME")

    drawAux(c, "S%d/HV%d" % (scanid, HVPoint))
    c.SaveAs("%s/clusterTime_muon.png" % (outputdir))
    c.SaveAs("%s/clusterTime_muon.pdf" % (outputdir))
    
        
        
        
    
