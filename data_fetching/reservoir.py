"""
Reservoir data module.

This file reads and prepares the local reservoir storage data file.
"""

import os
from functools import lru_cache

import numpy as np
import pandas as pd

from config import (
    RESERVOIR_DATA_FILE,
    RESERVOIR_TREAT_ZERO_AS_MISSING,
    RESERVOIR_STORAGE_COLUMNS
)


# Reservoir storage data

def get_reservoir_data_file():
    candidates = [
        RESERVOIR_DATA_FILE,
        os.path.join("data", "reservoir_storage.txt"),
        os.path.join("data", "data_view.txt")
    ]

    for file_path in candidates:
        if file_path and os.path.exists(file_path):
            return file_path

    return RESERVOIR_DATA_FILE


@lru_cache(maxsize=8)
def load_reservoir_storage_cached(file_path, modified_time):
    df = pd.read_csv(file_path, skipinitialspace=True)
    df.columns = [col.strip() for col in df.columns]

    if "Date" not in df.columns:
        raise ValueError("Reservoir storage file must include a Date column.")

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"]).copy()
    df = df.sort_values("Date")

    available_columns = []

    for column in RESERVOIR_STORAGE_COLUMNS:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

            if RESERVOIR_TREAT_ZERO_AS_MISSING:
                df.loc[df[column] == 0, column] = np.nan

            available_columns.append(column)

    if not available_columns:
        raise ValueError("No expected reservoir storage columns were found in the file.")

    print(f"Reservoir storage data loaded from {file_path}. Modified time: {modified_time}")

    return df


def load_reservoir_storage():
    file_path = get_reservoir_data_file()

    if not os.path.exists(file_path):
        raise FileNotFoundError(
            "Reservoir storage file was not found. Put data_view.txt in the data folder, "
            "or update RESERVOIR_DATA_FILE in config.py. Current path: "
            f"{file_path}"
        )

    modified_time = os.path.getmtime(file_path)
    return load_reservoir_storage_cached(file_path, modified_time).copy()


def get_available_reservoir_columns(df):
    return [column for column in RESERVOIR_STORAGE_COLUMNS if column in df.columns]