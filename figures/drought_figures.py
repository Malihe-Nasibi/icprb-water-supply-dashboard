"""
Drought figure module.

This file builds the Potomac Basin U.S. Drought Monitor map as a base64 PNG.
Boundary preparation and basin percentage calculations are handled in
data_fetching/drought.py.
"""

import io
import base64
from datetime import date
from functools import lru_cache

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

from config import USDM_CURRENT_GEOJSON_URL
from data_fetching.drought import (
    load_potomac_boundary_layers,
    calculate_usdm_basin_percentages
)


# Build Potomac Basin U.S. Drought Monitor map

@lru_cache(maxsize=4)
def build_potomac_usdm_map_src(cache_date):
    """
    Build a Potomac Basin U.S. Drought Monitor map and return it as a base64 PNG.

    This version keeps the large map plus the USDM intensity and basin-percentage
    panel, but removes organization logos and other organization-source graphics.
    """

    try:
        hucs, watershed = load_potomac_boundary_layers()
        usdm = gpd.read_file(USDM_CURRENT_GEOJSON_URL)

        if usdm.empty:
            raise ValueError("No USDM polygons were returned from the current USDM GeoJSON URL.")

        if usdm.crs is None:
            usdm = usdm.set_crs("EPSG:4326")

        if hucs.crs is None:
            hucs = hucs.set_crs("EPSG:4326")

        if watershed.crs is None:
            watershed = watershed.set_crs(hucs.crs)

        hucs = hucs.to_crs(usdm.crs)
        watershed = watershed.to_crs(usdm.crs)

        usdm = usdm.dropna(subset=["DM"]).copy()
        usdm["DM"] = usdm["DM"].astype(int)

        color_palette = {
            0: "#FFFF00",  # D0
            1: "#FCD37F",  # D1
            2: "#FFAA00",  # D2
            3: "#E60000",  # D3
            4: "#730000"   # D4
        }

        category_labels = {
            0: "D0 (Abnormally Dry)",
            1: "D1 (Moderate Drought)",
            2: "D2 (Severe Drought)",
            3: "D3 (Extreme Drought)",
            4: "D4 (Exceptional Drought)"
        }

        usdm["Plot_Color"] = usdm["DM"].map(color_palette).fillna("#FFFFFF")
        basin_percentages = calculate_usdm_basin_percentages(usdm, watershed)

        fig = plt.figure(figsize=(16, 8.6))
        ax = fig.add_axes([0.04, 0.08, 0.72, 0.83])
        info_ax = fig.add_axes([0.79, 0.12, 0.18, 0.74])
        info_ax.axis("off")

        usdm.plot(
            ax=ax,
            color=usdm["Plot_Color"],
            edgecolor="none",
            alpha=0.95
        )

        hucs.boundary.plot(
            ax=ax,
            edgecolor="lightgray",
            linewidth=0.65,
            alpha=0.95,
            zorder=4
        )

        watershed.boundary.plot(
            ax=ax,
            edgecolor="blue",
            linewidth=3.0,
            zorder=5
        )

        minx, miny, maxx, maxy = watershed.total_bounds
        ax.set_xlim(minx - 1.0, maxx + 1.0)
        ax.set_ylim(miny - 0.35, maxy + 0.35)

        ax.set_title(
            (
                "U.S. Drought Monitor Map for the Potomac Basin\n"
                f"Map retrieved: {date.today().strftime('%B %d, %Y')}"
            ),
            fontsize=18,
            fontweight="bold",
            pad=14
        )

        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.tick_params(labelsize=10)
        ax.grid(True, color="lightgray", alpha=0.45, linewidth=0.6)

        boundary_legend = [
            Line2D([0], [0], color="blue", lw=3.0, label="Potomac Basin"),
            Line2D([0], [0], color="lightgray", lw=3.0, label="Subbasins")
        ]

        ax.legend(
            handles=boundary_legend,
            title=None,
            loc="lower left",
            fontsize=12,
            frameon=True,
            facecolor="white",
            edgecolor="gray",
            framealpha=0.95,
            fancybox=False
        )

        # Right-side intensity legend
        info_ax.text(0.02, 0.96, "Intensity", fontsize=18, fontweight="bold", va="top")

        intensity_rows = [
            ("None", "#FFFFFF", "#cfcfcf"),
            (category_labels[0], color_palette[0], "#b5b5b5"),
            (category_labels[1], color_palette[1], "#b5b5b5"),
            (category_labels[2], color_palette[2], "#b5b5b5"),
            (category_labels[3], color_palette[3], "#b5b5b5"),
            (category_labels[4], color_palette[4], "#b5b5b5"),
            ("No Data", "#9E9E9E", "#9E9E9E")
        ]

        y = 0.88
        for label, fill_color, edge_color in intensity_rows:
            info_ax.add_patch(
                Rectangle(
                    (0.02, y - 0.024),
                    0.075,
                    0.035,
                    facecolor=fill_color,
                    edgecolor=edge_color,
                    linewidth=0.8,
                    transform=info_ax.transAxes
                )
            )
            info_ax.text(0.12, y - 0.006, label, fontsize=11.5, va="center")
            y -= 0.052

         # Basin percentage table
        table_rows = []

        nonzero_categories = [
            dm_value
            for dm_value, percent_value in basin_percentages.items()
            if percent_value > 0.05
        ]

        if nonzero_categories:
            max_category_to_show = min(max(nonzero_categories) + 1, 4)
        else:
            max_category_to_show = 0

        for dm_value in range(max_category_to_show + 1):
            percent_value = basin_percentages.get(dm_value, 0.0)

            if abs(percent_value) < 0.05:
                percent_text = "0%"
            elif percent_value < 1.0:
                percent_text = f"{percent_value:.1f}%"
            elif abs(percent_value - round(percent_value)) < 0.05:
                percent_text = f"{percent_value:.0f}%"
            else:
                percent_text = f"{percent_value:.1f}%"

            table_rows.append([f"D{dm_value}", percent_text])

        table = info_ax.table(
            cellText=table_rows,
            colLabels=["Category", "Basin"],
            cellLoc="center",
            loc="center",
            bbox=[0.00, 0.29, 1.00, 0.22]
        )
        
        table.auto_set_font_size(False)
        table.set_fontsize(10.5)
        
        for (row, col), cell in table.get_celld().items():
            cell.set_edgecolor("#333333")
            cell.set_linewidth(0.8)
        
            if row == 0:
                cell.set_facecolor("#D9D9D9")
                cell.get_text().set_fontweight("bold")
            elif col == 0:
                dm_text = cell.get_text().get_text()
        
                try:
                    dm_int = int(dm_text.replace("D", ""))
                    cell.set_facecolor(color_palette.get(dm_int, "white"))
                except Exception:
                    pass

        info_ax.text(
            0.02,
            0.20,
            "The Drought Monitor focuses on broad-scale conditions.\n"
            "Local conditions may vary. For more information on the\n"
            "Drought Monitor, go to droughtmonitor.unl.edu/About.aspx",
            fontsize=8.5,
            style="italic",
            va="top"
        )

        buffer = io.BytesIO()
        fig.savefig(buffer, format="png", dpi=155, bbox_inches="tight")
        plt.close(fig)

        buffer.seek(0)
        encoded = base64.b64encode(buffer.read()).decode("utf-8")

        return f"data:image/png;base64,{encoded}", None

    except Exception as e:
        return None, f"Potomac Basin drought map could not be created: {e}"