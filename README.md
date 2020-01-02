# INFN_Analysis
Analysis package for the INFN electronics at 904/GIF++ laboratories

The master branch contains the simple analysis tool used for cosmic/noise studies. An example run is added with all relevant files. Other branches contain specific analyzers for GIF++, 2D analysis, etc.

Contents:

 - [Configuration file](#configuration-file)
 - [Analyzer class](#analyzer-class)
 - [Analyze an efficiency run](#analyze-an-efficiency-run)
 - [Analyze a noise run](#analyze-a-noise-run)
 - [Muon clusterization study](#muon-clusterization-study)
 



# Configuration file
 The config.py file contains the information of strips, TDC mapping, gap names etc. It should closely follow the hardware configuration and the WebDCS settings. An overview of the settings is given below:
 
  - TDC_channels: list of TDC channels connected to the strips
  - TDC_strips: list of TDC strips (ordered), one-to-one relation with TDC_channels
  - TDC_strips_mask: list of strips to be masked (dead or noisy)
  - muonTriggerWindow = 600: DAQ setting for efficiency scans
  - noiseTriggerWindow = 10000: DAQ setting for noise scans
  - timeWindowReject = 100: reject first 100 ns due to bad TDC data
  - muonWindowWidth = 3: amount of one-sided sigmas for the time window
  - stripArea: active strip area in cm2
  - topGapName: top gap name, as given in the WebDCS
  - topGapName: bottom gap name, as given in the WebDCS

# Analyzer class
 This analyzer.py class contains all the basic functionalities to analyze one single HVpoint. The analyzer is initialized by:
 
    import analyzer as an
    analyzer = an.Analyzer(dir, saveDir, scanid, HVPoint, mode)
    analyzer.setVerbose(1) # verbosity, set to 1
    
    
 with dir = the directory where the ROOT files are stored, saveDir a directory where all the output will be saved, scanid the scan ID number, HVPoint the current point to be analyzed and mode = efficieny/noise. A configuration from config.py (e.g. cfg_GRAPHITE_HIGH) is loaded as follows:
 
    import config 
    analyzer.loadConfig(config.cfg_GRAPHITE_HIGH)
    
Next, a set of analysis routines are called to perform the entire analysis (efficiency or noise). First, the time windows are determined using the function   
    
    analyzer.timeProfile(267, 9) # args: peakMean (ns), peakWidth (ns); NO FIT
    analyzer.timeProfile() # w/o arguments the peakMean/peakWidth are determined by Gaussian fit
    
When no argument is given, as Gaussian fit is performed over the time profile to search the mean and width of the time peak. The muon time window is then determined as a given amount of sigmas (= muonWindowWidth)  around the mean fitted value. In cases where statistics is limited (e.g. at low voltages with low efficieny), the fit might fail and return non-physical time windows. Therefore, it is possible prescribe the mean/width of the peak as arguments to the timeProfile() function. One can then e.g. obtain the mean/width from a high HV point by means of a Gaussian fit, and then use these parameters as argument for the analyzer. Usually, when the trigger is not changed, the mean/widht values are more or less constant.

A full 2D dump of the events can be obtained using:
    
    analyzer.timeStripProfile2D() 
    
The hit profiles are plotted using the stripProfile() function:

    analyzer.stripProfile()
    
 For both efficiency/noise runs, it plots all the hits recorded by the TDC channels (taking into account the masked strips). For efficiency runs, it plots the muon hit profile defined as all the hits inside the muon window. For noise runs, it calculates the noise rate and noise rate profiles.  
 
Muon clusterization can be performed calling the following function:

    analyzer.clusterization(10, 4, 16) # args: nominal/up/down clusterization time constraint (ns)
  
Three arguments are given: nominal/up/down time constraints. The clusterization is performed by grouping hits (per event) widh adjacent strips and within a given time interval. The time interval typically is 10 ns when using a conventional CAEN TDC (see clusterStudy.py). In order to estimate the error on the cluster size/multiplicity, an up/down variation is performed by altering the time constraints around the nominal value. The masked strips are taken into account for the efficiency calculation.

Muon efficiency is calculated by calling:
        
    analyzer.efficiency()
    
It calculates the muon efficiency (using hits in the muon time window only) and the absolute efficiency (using all the hits, also outside the muon time window). The masked strips are taken into account for the efficiency calculation.
        
In order to plot single events, the function eventDisplay(n) is written:

    analyzer.eventDisplay(10) # args: amount of events to be plotted (randomly). -1: all events
        
If n=-1, all events are plotted, if n>0 only the first n events are plotted.
        
All the input and output parameters are stored in a JSON file when calling:

    analyzer.write() 


# Analyze an efficiency run
 The script analyzeEfficiencyRun.py performs an efficiency analysis with muon clusterization. The core analyzer is called for each HVpoint, and the currents, efficiency, cluster size and multiplicity are plotted as function of the HV. A Sigmoid fit is performed over the efficiency curve to extract the WP and all other relevant parameters. All parameters are stored in a JSON file.
 
 In order to run multiple analyses (e.g. with different time windows, different clusterization paramaters), a tag must be given. All the data are then stored in a directory with the tag name.
 
 HOW TO USE:
 
 - download an efficiency run from the WebDCS, and extract the files to a directory;
 - adapt config.py, if necessary (or add a new config);
 - open analyzeEfficiencyRun.py, change the tag and config;
 - go to the extracted directory, and run the analyzeEfficiencyRun.py script.
 
 
# Analyze a noise run
 The script analyzeNoiseRun.py performes an noise analysis. The core analyzer is called for each HVpoint, and the currents and noise rates are plotted as function of the HV. All parameters are stored in a JSON file.
 
 In order to run multiple analyses (e.g. with different time windows, different clusterization paramaters), a tag must be given. All the data are then stored in a directory with the tag name.
 
 HOW TO USE:
 
 - download a noise run from the WebDCS, and extract the files to a directory;
 - adapt config.py, if necessary (or add a new config);
 - open analyzeNoiseRun.py, change the tag and config;
 - go to the extracted directory, and run the analyzeNoiseRun.py script.
 

# Muon clusterization study
In order to know the clusterization timing values, a script has been written which performs the clusterization for several time constraints. The muon cluster size (CLS) and multiplicity (CMP) is then plotted as function of the time constraint. The CLS should reach a plateau value around 10 ns.
 
 HOW TO USE:
 
 - download an efficiency run from the WebDCS, and extract the files to a directory;
 - adapt config.py, if necessary (or add a new config);
 - open clusterStudy.py, change the tag and config and specify the HVpoint at which the study must be performed (typically WP)
 - go to the extracted directory, and run the clusterStudy.py script.
