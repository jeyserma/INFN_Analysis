

# Config example: graphite chamber, high region, readout of 32 strips
cfg_CMS_FEB_904 = {

    "TDC_channels":         [3048, 3049, 3050, 3051, 3052, 3053, 3054, 3055],
    "TDC_strips":           [1, 2, 3, 4, 5, 6, 7, 8],
    "TDC_strips_mask":      [8],

    "muonTriggerWindow":    600,    # DAQ setting for efficiency scans
    "noiseTriggerWindow":   10000,  # DAQ setting for noise scans
    "timeWindowReject":     100,    # reject first 100 ns due to bad TDC data
    "muonWindowWidth":      3,      # amount of one-sided sigmas for the time window
    

    "stripArea":            135.351, # active strip area in cm2
    
    "topGapName":           "INFN-TOP",
    "botGapName":           "INFN-BOT",

}

