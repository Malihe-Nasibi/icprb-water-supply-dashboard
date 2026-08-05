"""
Drought data module.

This file downloads and prepares Potomac HUC8 boundary layers and calculates
U.S. Drought Monitor drought-category percentages for the Potomac Basin.
"""

from functools import lru_cache

import geopandas as gpd

from config import POTOMAC_HUC8_GEOJSON_URL
from data_fetching.streamflow_usgs import get_daily_cache_key


# Geometry helpers

def _clean_geometry(gdf):
    """Remove empty geometries and repair invalid geometries when possible."""

    if gdf is None or gdf.empty:
        return gdf

    gdf = gdf.dropna(subset=["geometry"]).copy()
    gdf = gdf[~gdf.geometry.is_empty].copy()

    try:
        gdf["geometry"] = gdf.geometry.buffer(0)
    except Exception:
        pass

    return gdf


def _standardize_huc8_columns(hucs):
    """Make HUC8 column names consistent across WBD web services."""

    hucs = hucs.copy()
    columns_lower = {col.lower(): col for col in hucs.columns}

    if "HUC8" not in hucs.columns:
        if "huc8" in columns_lower:
            hucs["HUC8"] = hucs[columns_lower["huc8"]]
        elif "huc" in columns_lower:
            hucs["HUC8"] = hucs[columns_lower["huc"]]
        elif "name" in columns_lower:
            hucs["HUC8"] = hucs[columns_lower["name"]]
        else:
            hucs["HUC8"] = "Potomac HUC8"

    if "NAME" not in hucs.columns:
        if "name" in columns_lower:
            hucs["NAME"] = hucs[columns_lower["name"]]
        elif "gnis_name" in columns_lower:
            hucs["NAME"] = hucs[columns_lower["gnis_name"]]
        else:
            hucs["NAME"] = hucs["HUC8"].astype(str)

    return hucs


# Basin percentage calculation

def calculate_usdm_basin_percentages(usdm_gdf, watershed_gdf):
    """
    Estimate percent of the Potomac Basin area in each USDM drought category.

    Areas are calculated in EPSG:5070 to avoid using geographic degrees as area.
    Values are returned as percentages of total basin area.
    """

    percentages = {dm: 0.0 for dm in range(5)}

    try:
        watershed_area = watershed_gdf.to_crs("EPSG:5070").dissolve()
        usdm_area = usdm_gdf[["DM", "geometry"]].to_crs("EPSG:5070").copy()

        total_area = watershed_area.geometry.area.sum()

        if total_area <= 0:
            return percentages

        clipped = usdm_area.overlay(watershed_area[["geometry"]], how="intersection")

        if clipped.empty:
            return percentages

        clipped["Area"] = clipped.geometry.area

        for dm_value, area_value in clipped.groupby("DM")["Area"].sum().items():
            try:
                dm_int = int(dm_value)
            except Exception:
                continue

            if dm_int in percentages:
                percentages[dm_int] = (area_value / total_area) * 100.0

        return percentages

    except Exception:
        return percentages


# Potomac Basin boundary layers

@lru_cache(maxsize=4)
def load_potomac_boundary_layers_cached(cache_date):
    """
    Download and prepare Potomac Basin HUC8 boundary layers from the USGS WBD
    web service.
    """

    hucs = gpd.read_file(POTOMAC_HUC8_GEOJSON_URL)

    if hucs.empty:
        raise ValueError("No Potomac HUC8 boundaries were returned from the WBD web service.")

    hucs = _standardize_huc8_columns(hucs)
    hucs = _clean_geometry(hucs)

    if hucs.crs is None:
        hucs = hucs.set_crs("EPSG:4326")

    # The URL should already filter to HUC8 codes starting with 020700, but
    # this second filter as a safety check if the service query behavior changes.
    hucs["HUC8"] = hucs["HUC8"].astype(str)
    hucs = hucs[hucs["HUC8"].str.startswith("020700")].copy()

    if hucs.empty:
        raise ValueError("The WBD layer downloaded, but no HUC8 codes starting with 020700 were found.")

    watershed = hucs.dissolve()
    watershed = watershed.reset_index(drop=True)
    watershed["Name"] = "Potomac Basin"

    print(f"Downloaded Potomac boundary layers from web. Cache date: {cache_date}")

    return hucs, watershed


def load_potomac_boundary_layers():
    cache_date = get_daily_cache_key()
    hucs, watershed = load_potomac_boundary_layers_cached(cache_date)
    return hucs.copy(), watershed.copy()