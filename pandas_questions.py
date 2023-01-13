"""Plotting referendum results in pandas.

In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using `geopandas`.
"""
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.read_csv('data/referendum.csv', sep=";")
    regions = pd.read_csv('data/regions.csv')
    departments = pd.read_csv('data/departments.csv')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions.rename(columns={"code": "region_code", "name": "name_reg"},
                   inplace=True)
    df = pd.merge(regions, departments,
                  how='inner',
                  on=["region_code"])
    df = df[["region_code", "name_reg", "code", "name"]]
    df.rename(columns={"region_code": "code_reg", "code": "code_dep",
                       "name": "name_dep"},
              inplace=True)
    return df


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    regions_and_departments["code_dep"].replace(
        ['01', '02', '03', '04', '05', '06', '07', '08', '09'],
        ['1', '2', '3', '4', '5', '6', '7', '8', '9'],
        inplace=True)
    df = pd.merge(regions_and_departments,
                  referendum,
                  left_on="code_dep",
                  right_on="Department code")
    df.replace(["COM", "TOM", "DOM", "CollectivitÃ©s d'Outre-Mer"],
               np.nan, inplace=True)
    df.dropna(axis=0, inplace=True)
    return df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    df = referendum_and_areas[[
        'code_reg',
        'name_reg',
        'Registered',
        'Abstentions',
        'Null',
        'Choice A',
        'Choice B'
        ]]
    dff = referendum_and_areas[['code_reg', 'name_reg']].drop_duplicates()
    dff.set_index(keys=["code_reg"], inplace=True)
    df = df.groupby(['code_reg']).sum()
    df = pd.merge(df, dff, how='left', left_index=True, right_index=True)
    return df


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    gr = gpd.read_file('data/regions.geojson')
    gr.rename(columns={"code": "code_reg"}, inplace=True)
    gr.set_index(keys=["code_reg"], inplace=True)
    df = pd.merge(referendum_result_by_regions, gr,
                  how='inner', left_index=True, right_index=True)
    df["ratio"] = df["Choice A"]/(df["Choice A"]+df["Choice B"])
    data = gpd.GeoDataFrame(df)
    data.plot("ratio", legend=True, cmap="Blues")
    return data


if __name__ == "__main__":

    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(
        df_reg, df_dep
    )
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()
