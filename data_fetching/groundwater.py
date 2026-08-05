"""
Groundwater data module.

This file downloads and prepares USGS groundwater observations.
"""

import requests
import pandas as pd
from datetime import date
from functools import lru_cache

from config import GROUNDWATER_WELLS, GROUNDWATER_PARAMETER_CD, GROUNDWATER_QUERY_START
from data_fetching.streamflow_usgs import get_daily_cache_key


# Groundwater data download

def fetch_groundwater_daily(site_no, start_date, end_date):
    """
    Fetch daily groundwater depth-to-water data from USGS NWIS daily values.
    Parameter 72019 = depth to water level, feet below land surface.
    """

    url = "https://waterservices.usgs.gov/nwis/dv/"

    params = {
        "format": "json",
        "sites": site_no,
        "parameterCd": GROUNDWATER_PARAMETER_CD,
        "startDT": start_date,
        "endDT": end_date,
        "siteStatus": "all"
    }

    response = requests.get(url, params=params, timeout=60)
    response.raise_for_status()

    data = response.json()
    time_series = data["value"]["timeSeries"]

    if len(time_series) == 0:
        return pd.DataFrame(columns=["Date", "Depth_ft"])

    values = time_series[0]["values"][0]["value"]

    records = []
    for item in values:
        try:
            records.append({
                "Date": item["dateTime"][:10],
                "Depth_ft": float(item["value"])
            })
        except Exception:
            continue

    df = pd.DataFrame(records)

    if df.empty:
        return pd.DataFrame(columns=["Date", "Depth_ft"])

    df["Date"] = pd.to_datetime(df["Date"])

    return df.dropna(subset=["Date", "Depth_ft"]).sort_values("Date")


def fetch_groundwater_discrete(site_no, start_date, end_date):
    """
    Fetch discrete groundwater field measurements from USGS OGC API.
    Used only when daily values are not available.
    """

    all_records = []

    url = (
        "https://api.waterdata.usgs.gov/ogcapi/v0/collections/"
        "field-measurements/items"
        f"?monitoring_location_id=USGS-{site_no}"
        f"&parameter_code={GROUNDWATER_PARAMETER_CD}"
        f"&time={start_date}T00:00:00Z/{end_date}T23:59:59Z"
        "&limit=10000&f=json"
    )

    while url:
        response = requests.get(url, timeout=60)

        if response.status_code != 200 or not response.text.strip():
            break

        data = response.json()
        features = data.get("features", [])

        if not features:
            break

        for feature in features:
            properties = feature.get("properties", {})

            try:
                all_records.append({
                    "Date": pd.to_datetime(properties.get("time", "")[:10]),
                    "Depth_ft": pd.to_numeric(properties.get("value"), errors="coerce")
                })
            except Exception:
                continue

        links = data.get("links", [])
        next_url = next((link["href"] for link in links if link.get("rel") == "next"), None)
        url = next_url

    if not all_records:
        return pd.DataFrame(columns=["Date", "Depth_ft"])

    df = pd.DataFrame(all_records)
    df = df.dropna(subset=["Date", "Depth_ft"]).sort_values("Date")

    return df


@lru_cache(maxsize=32)
def load_groundwater_record_cached(well_name, cache_date):

    if well_name not in GROUNDWATER_WELLS:
        raise ValueError(f"Groundwater well {well_name} is not in the well list.")

    site_no = GROUNDWATER_WELLS[well_name]
    query_end = date.today().strftime("%Y-%m-%d")

    df = fetch_groundwater_daily(
        site_no=site_no,
        start_date=GROUNDWATER_QUERY_START,
        end_date=query_end
    )
    source_type = "daily"

    if df.empty:
        df = fetch_groundwater_discrete(
            site_no=site_no,
            start_date=GROUNDWATER_QUERY_START,
            end_date=query_end
        )
        source_type = "discrete"

    if df.empty:
        raise ValueError(f"No groundwater data were returned for well {well_name} ({site_no}).")

    df = df[df["Depth_ft"] > 0].copy()
    df = df.sort_values("Date")
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month

    print(
        f"Groundwater data loaded for {well_name} ({site_no}). "
        f"Source: {source_type}. Records: {len(df)}. Cache date: {cache_date}"
    )

    return df, source_type


def load_groundwater_record(well_name):
    cache_date = get_daily_cache_key()
    df, source_type = load_groundwater_record_cached(well_name, cache_date)
    return df.copy(), source_type