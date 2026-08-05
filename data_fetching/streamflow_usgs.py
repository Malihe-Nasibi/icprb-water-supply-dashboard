import requests
import pandas as pd
from datetime import date
from functools import lru_cache

from config import PARAMETER_CD, STAT_CD, QUERY_START


# Cache keys

def get_daily_cache_key():
    return date.today().strftime("%Y-%m-%d")


# Function to download USGS daily streamflow data

def get_usgs_daily_flow(site_id, start_date, end_date):

    url = "https://waterservices.usgs.gov/nwis/dv/"

    params = {
        "format": "json",
        "sites": site_id,
        "parameterCd": PARAMETER_CD,
        "statCd": STAT_CD,
        "startDT": start_date,
        "endDT": end_date,
        "siteStatus": "all"
    }

    response = requests.get(url, params=params, timeout=60)
    response.raise_for_status()

    data = response.json()
    time_series = data["value"]["timeSeries"]

    if len(time_series) == 0:
        return pd.DataFrame(columns=["Date", "Flow_cfs"])

    values = time_series[0]["values"][0]["value"]

    records = []
    for item in values:
        try:
            records.append({
                "Date": item["dateTime"][:10],
                "Flow_cfs": float(item["value"])
            })
        except Exception:
            continue

    df = pd.DataFrame(records)

    if df.empty:
        return pd.DataFrame(columns=["Date", "Flow_cfs"])

    df["Date"] = pd.to_datetime(df["Date"])

    return df


# Load and prepare streamflow record

@lru_cache(maxsize=16)
def load_station_record_cached(site_id, cache_date):

    query_end = date.today().strftime("%Y-%m-%d")

    df_all = get_usgs_daily_flow(
        site_id=site_id,
        start_date=QUERY_START,
        end_date=query_end
    )

    if df_all.empty:
        raise ValueError(f"No USGS daily flow data were returned for station {site_id}.")

    df_all = df_all.dropna(subset=["Flow_cfs"])
    df_all = df_all[df_all["Flow_cfs"] > 0].copy()

    if df_all.empty:
        raise ValueError(f"No positive flow values were returned for station {site_id}.")

    df_all = df_all.sort_values("Date")

    df_all["Flow_7Day_cfs"] = (
        df_all["Flow_cfs"]
        .rolling(window=7, min_periods=7)
        .mean()
    )

    df_all["Year"] = df_all["Date"].dt.year
    df_all["Month_Day"] = df_all["Date"].dt.strftime("%m-%d")

    df_all = df_all[df_all["Month_Day"] != "02-29"].copy()

    # 2001 is only a dummy non-leap plotting year used to place Month-Day
    # values on a Jan-Dec x-axis.
    df_all["Plot_Date"] = pd.to_datetime("2001-" + df_all["Month_Day"])

    print(f"USGS data loaded for station {site_id}. Cache date: {cache_date}")

    return df_all


def load_station_record(site_id):
    cache_date = get_daily_cache_key()
    return load_station_record_cached(site_id, cache_date).copy()