

# Config example: graphite chamber, high region, readout of 32 strips
cfg_GRAPHITE_HIGH = {

    "TDC_channels":         [4007, 4006, 4005, 4004, 4003, 4002, 4001, 4000, 4015, 4014, 4013, 4012, 4011, 4010, 4009, 4008, 4023, 4022, 4021, 4020, 4019, 4018, 4017, 4016, 4031, 4030, 4029, 4028, 4027, 4026, 4025, 4024],
    "TDC_strips":           [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32],
    "TDC_strips_mask":      [1, 2, 25, 26, 27, 28, 29, 30, 31, 32], # noisy strips...


    "muonTriggerWindow":    600,    # DAQ setting for efficiency scans
    "noiseTriggerWindow":   10000,  # DAQ setting for noise scans
    "timeWindowReject":     100,    # reject first 100 ns due to bad TDC data
    "muonWindowWidth":      3,      # amount of one-sided sigmas for the time window

    "stripArea":            45.75,  # active strip area in cm2
    
    "topGapName":           "GRAPHITE-TOP",
    "botGapName":           "GRAPHITE-BOT",

}

