"""
NOAA/NWPS forecast data module.

This file downloads and prepares NOAA/NWPS observed and forecast stageflow
data. Forecast figure creation is handled separately in figures/forecast_figures.py.
"""

import requests
import pandas as pd
import numpy as np
from functools import lru_cache
from zoneinfo import ZoneInfo

from config import SITE_TIMEZONE


# Cache keys

def get_hourly_cache_key():
    """
    Used for forecast products because official forecast data can update
    more often than once per day.
    """
    return pd.Timestamp.now(tz=ZoneInfo(SITE_TIMEZONE)).strftime("%Y-%m-%d-%H")


# NOAA/NWPS official forecast data

def normalize_nwps_time(value):
    """
    Converts NWPS API timestamp to site local time without timezone info.
    The NOAA graph labels PORM2/BRKM2 in site time, which is Eastern time.
    """
    ts = pd.to_datetime(value, errors="coerce", utc=True)
    if pd.isna(ts):
        return pd.NaT
    return ts.tz_convert(SITE_TIMEZONE).tz_localize(None)


def find_first_key(dct, possible_keys):
    for key in possible_keys:
        if key in dct:
            return dct[key]
    return None


def numeric_or_nan(value):
    if isinstance(value, dict):
        value = find_first_key(value, ["value", "amount", "primary", "secondary"])
    return pd.to_numeric(value, errors="coerce")


def collect_stageflow_records(obj, series_type, inherited_meta=None):
    """
    Extracts stage and flow from NWPS stageflow observed/forecast JSON.
    This parser keeps observed and forecast separate by endpoint and assigns
    stage/flow using the primary/secondary metadata where available.
    """

    if inherited_meta is None:
        inherited_meta = {}

    records = []

    if isinstance(obj, dict):
        meta = inherited_meta.copy()

        for key in ["primaryName", "primaryUnits", "secondaryName", "secondaryUnits"]:
            if key in obj:
                meta[key] = obj[key]

        time_value = find_first_key(
            obj,
            ["validTime", "valid_time", "time", "dateTime", "datetime", "timestamp"]
        )

        has_primary = "primary" in obj
        has_secondary = "secondary" in obj

        if time_value is not None and (has_primary or has_secondary):
            stage_ft = np.nan
            flow_kcfs = np.nan

            primary_value = numeric_or_nan(obj.get("primary")) if has_primary else np.nan
            secondary_value = numeric_or_nan(obj.get("secondary")) if has_secondary else np.nan

            primary_name = str(meta.get("primaryName", "")).lower()
            primary_units = str(meta.get("primaryUnits", "")).lower()
            secondary_name = str(meta.get("secondaryName", "")).lower()
            secondary_units = str(meta.get("secondaryUnits", "")).lower()

            if not pd.isna(primary_value):
                if "stage" in primary_name or "gage" in primary_name or primary_units in ["ft", "feet"]:
                    stage_ft = float(primary_value)
                elif "flow" in primary_name or "discharge" in primary_name or "cfs" in primary_units:
                    if "kcfs" in primary_units:
                        flow_kcfs = float(primary_value)
                    else:
                        flow_kcfs = float(primary_value) / 1000.0

            if not pd.isna(secondary_value):
                if "stage" in secondary_name or "gage" in secondary_name or secondary_units in ["ft", "feet"]:
                    stage_ft = float(secondary_value)
                elif "flow" in secondary_name or "discharge" in secondary_name or "cfs" in secondary_units:
                    if "kcfs" in secondary_units:
                        flow_kcfs = float(secondary_value)
                    else:
                        flow_kcfs = float(secondary_value) / 1000.0

            if pd.isna(stage_ft) and not pd.isna(primary_value):
                stage_ft = float(primary_value)
            if pd.isna(flow_kcfs) and not pd.isna(secondary_value):
                flow_kcfs = float(secondary_value) if secondary_value < 100 else float(secondary_value) / 1000.0

            time_local = normalize_nwps_time(time_value)

            if not pd.isna(time_local) and not pd.isna(stage_ft):
                records.append({
                    "Time": time_local,
                    "Stage_ft": stage_ft,
                    "Flow_kcfs": flow_kcfs,
                    "Series": series_type
                })

        for value in obj.values():
            records.extend(collect_stageflow_records(value, series_type, meta))

    elif isinstance(obj, list):
        for item in obj:
            records.extend(collect_stageflow_records(item, series_type, inherited_meta))

    return records


@lru_cache(maxsize=16)
def fetch_nwps_stageflow_product_cached(gauge_id, product, cache_key):
    """
    Downloads a single NWPS stageflow product: observed or forecast.
    """

    url = f"https://api.water.noaa.gov/nwps/v1/gauges/{gauge_id}/stageflow/{product}"
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    data = response.json()

    series_type = "Observed" if product == "observed" else "Forecast"
    records = collect_stageflow_records(data, series_type)

    return records


@lru_cache(maxsize=16)
def fetch_nwps_gauge_metadata_cached(gauge_id, cache_key):
    """
    Downloads gauge metadata when available. This is used only for display labels.
    """

    url = f"https://api.water.noaa.gov/nwps/v1/gauges/{gauge_id}"
    response = requests.get(url, timeout=60)
    response.raise_for_status()

    return response.json()


def get_nwps_stageflow_dataframe(gauge_id):
    cache_key = get_hourly_cache_key()

    all_records = []
    all_records.extend(fetch_nwps_stageflow_product_cached(gauge_id, "observed", cache_key))
    all_records.extend(fetch_nwps_stageflow_product_cached(gauge_id, "forecast", cache_key))

    if not all_records:
        raise ValueError(f"No NWPS observed/forecast stageflow records were returned for {gauge_id}.")

    df = pd.DataFrame(all_records)
    df = df.dropna(subset=["Time", "Stage_ft"])
    df = df.drop_duplicates(subset=["Time", "Series"])
    df = df.sort_values("Time")

    return df


def get_nwps_forecast_issue_text(gauge_id):
    try:
        metadata = fetch_nwps_gauge_metadata_cached(gauge_id, get_hourly_cache_key())
        text_candidates = []

        def scan(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    key_lower = str(key).lower()
                    if "issue" in key_lower or "issued" in key_lower or "forecast" in key_lower:
                        if isinstance(value, str):
                            text_candidates.append(value)
                    scan(value)
            elif isinstance(obj, list):
                for item in obj:
                    scan(item)

        scan(metadata)

        if text_candidates:
            return text_candidates[0]

    except Exception:
        pass

    return None