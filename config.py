# Basic settings

PARAMETER_CD = "00060"     # Discharge / streamflow, cubic feet per second
STAT_CD = "00003"          # Daily mean
QUERY_START = "1900-01-01"

GROUNDWATER_PARAMETER_CD = "72019"
GROUNDWATER_QUERY_START = "1980-01-01"

SITE_TIMEZONE = "America/New_York"

# Station lists

STATIONS = {
    "01646502": "Little Falls Pump Station",
    "01646500": "Little Falls",
    "01614500": "Conococheague Creek at Fairview, MD",
    "01643000": "Monocacy River at Jug Bridge Near Frederick, MD",
    "01636500": "Shenandoah River at Millville, WV",
    "01603000": "North Branch Potomac River Near Cumberland, MD"
}

GROUNDWATER_WELLS = {
    "VA41Q1":    "382150078424001",
    "VA51S7":    "383423077245901",
    "VA49V1":    "385607077381101",
    "VA52V2D":   "385638077220101",
    "VA46W175":  "390348078035501",
    "WVBer0445": "392725077582401",
    "MDMOEh20":  "390434076573002",
    "MDMOCc14":  "391314077224201",
    "MDWACi82":  "393402077434201",
    "MDWABe2":   "393638078001301",
}


# Drought and image URLs

USDM_CURRENT_MAP_URL = "https://droughtmonitor.unl.edu/data/png/current/current_usdm.png"
USDM_CURRENT_GEOJSON_URL = "https://droughtmonitor.unl.edu/data/json/usdm_current.json"

POTOMAC_BASIN_GEOJSON_FILE = "data/boundaries/potomac_basin.geojson"

POTOMAC_HUC8_GEOJSON_URL = (
    "https://hydro.nationalmap.gov/arcgis/rest/services/wbd/FeatureServer/4/query"
    "?where=HUC8%20LIKE%20%27020700%25%27"
    "&outFields=*"
    "&returnGeometry=true"
    "&f=geojson"
)

PRECIPITATION_IMAGES = [
    {
        "title": "24-hr Estimated Precipitation",
        "source": "Middle Atlantic River Forecast Center",
        "url": "https://www.weather.gov/images/marfc/mpe/past24.png"
    },
    {
        "title": "72-hr Precipitation Forecast",
        "source": "Middle Atlantic River Forecast Center",
        "url": "https://www.weather.gov/images/marfc/qpf_small/small_qpf_72hr_72.jpg"
    },
    {
        "title": "5-Day Total Precipitation",
        "source": "National Weather Service / Weather Prediction Center",
        "url": "https://www.wpc.ncep.noaa.gov/qpf/p120i.gif"
    },
    {
        "title": "7-Day Total Precipitation",
        "source": "National Weather Service / Weather Prediction Center",
        "url": "https://www.wpc.ncep.noaa.gov/qpf/p168i.gif"
    }
]

NOAA_OUTLOOK_IMAGES = [
    {
        "title": "30-Day Temperature Outlook",
        "source": "NOAA Climate Prediction Center",
        "url": "https://www.cpc.ncep.noaa.gov/products/predictions/30day/off15_temp.gif"
    },
    {
        "title": "30-Day Precipitation Outlook",
        "source": "NOAA Climate Prediction Center",
        "url": "https://www.cpc.ncep.noaa.gov/products/predictions/30day/off15_prcp.gif"
    }
]

# Flow forecast settings

FLOW_FORECAST_STATIONS = {
    "BRKM2": {
        "label": "Little Falls / BRKM2",
        "title": "Little Falls Flow Forecast",
        "subtitle": "Potomac River at Little Falls, MD — BRKM2",
        "description": "Forecast products for the Little Falls forecast point.",
        "nwps_gauge_id": "BRKM2"
    },
    "PORM2": {
        "label": "Point of Rocks / PORM2",
        "title": "Point of Rocks Flow Forecast",
        "subtitle": "Potomac River at Point of Rocks, MD — PORM2",
        "description": "Forecast products for the Point of Rocks forecast point.",
        "nwps_gauge_id": "PORM2"
    }
}

FLOW_FORECAST_MODELS = {
    "NAEFS": "NAEFS",
    "GEFS": "GEFS",
    "HEFS": "HEFS",
    "NWPS": "NOAA/NWPS Official Forecast"
}

FLOOD_STAGE_LEVELS = {
    "BRKM2": {
        "Action": 5.0,
        "Minor": 10.0,
        "Moderate": 12.0,
        "Major": 14.0
    },
    "PORM2": {
        "Action": 11.0,
        "Minor": 16.0,
        "Moderate": 20.0,
        "Major": 27.0
    }
}


# Reservoir settings

# Reservoir storage data file

RESERVOIR_DATA_FILE = "data/data_view.txt"

RESERVOIR_TREAT_ZERO_AS_MISSING = True

RESERVOIR_STORAGE_COLUMNS = {
    "WSSC - Patuxent reservoirs current usable storage (BG)": "Patuxent reservoirs",
    "WSSC - Little Reservoir current usable storage (BG)": "Little Reservoir",
    "FW - Occoquan Reservoir current usable storage (BG)": "Occoquan Reservoir",
    "USACE - Jennings Randolph Reservoir current usable storage (BG)": "Jennings Randolph current usable storage",
    "USACE - Jennings Randolph Reservoir water supply storage (BG)": "Jennings Randolph water supply storage",
    "USACE - Savage Reservoir current usable storage (BG)": "Savage Reservoir"
}

RESERVOIR_DEFAULT_COLUMN = "WSSC - Patuxent reservoirs current usable storage (BG)"


