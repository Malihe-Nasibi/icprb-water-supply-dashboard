"""
Drought data module.

This file loads the local Potomac Basin boundary and calculates
U.S. Drought Monitor drought-category percentages for the Potomac Basin.
"""

import os
from functools import lru_cache

import geopandas as gpd

from config import POTOMAC_BASIN_GEOJSON_FILE


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
def load_potomac_boundary_layers_cached(boundary_file, modified_time):
    """
    Load the local Potomac Basin boundary file.

    The same basin geometry is returned twice so the existing drought-map
    plotting code can continue to receive both a subbasin layer and a full
    watershed layer.
    """

    if not os.path.exists(boundary_file):
        raise FileNotFoundError(f"Missing Potomac Basin boundary file: {boundary_file}")

    basin_gdf = gpd.read_file(boundary_file)
    basin_gdf = _clean_geometry(basin_gdf)

    if basin_gdf.crs is None:
        basin_gdf = basin_gdf.set_crs("EPSG:4326")

    watershed_gdf = basin_gdf.dissolve().reset_index(drop=True)
    watershed_gdf = _clean_geometry(watershed_gdf)

    # huc8_gdf is kept for compatibility with the current plotting function.
    # With the local basin file, it represents the basin boundary layer.
    huc8_gdf = watershed_gdf.copy()

    return huc8_gdf, watershed_gdf


def load_potomac_boundary_layers():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    boundary_file = os.path.join(project_root, POTOMAC_BASIN_GEOJSON_FILE)

    modified_time = os.path.getmtime(boundary_file)

    return load_potomac_boundary_layers_cached(boundary_file, modified_time)
