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
import os


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.read_csv(os.path.join("data", "referendum.csv"), sep=";")
    regions = pd.read_csv(os.path.join("data", "regions.csv"))
    departments = pd.read_csv(os.path.join("data", "departments.csv"))

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    columns_regions = {
        "code": "code_reg",
        "name": "name_reg",
    }
    regions = regions.rename(columns=columns_regions)
    print(regions.head())
    columns_departments = {
        "code": "code_dep",
        "region_code": "code_reg",
        "name": "name_dep",
    }

    departments = departments.rename(columns=columns_departments)
    print(departments.head())
    df_merge = regions.merge(departments, on="code_reg", how="inner")
    return df_merge[["code_reg", "name_reg", "code_dep", "name_dep"]]


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum["Department code"] = referendum["Department code"].apply(
        lambda element: element.zfill(2)
    )
    df_merge = referendum.merge(
        regions_and_departments,
        left_on="Department code",
        right_on="code_dep",
        how="inner",
    )
    return df_merge


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    df_group = referendum_and_areas.groupby("name_reg")[
        ["Registered", "Abstentions", "Null", "Choice A", "Choice B"]
    ].sum()
    df_group = df_group.reset_index()
    return df_group


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    df_geo_regions = gpd.read_file(os.path.join("data", "regions.geojson"))
    df_geo_regions = df_geo_regions.rename(
        columns={"code": "code_reg", "nom": "name_reg"}
    )
    df_final = referendum_result_by_regions.merge(
        df_geo_regions[["name_reg", "geometry"]], on="name_reg", how="inner"
    )

    df_final = gpd.GeoDataFrame(df_final)
    df_final["ratio"] = df_final["Choice A"] / (
        df_final["Choice A"] + df_final["Choice B"]
    )  # +df_final['Null'])
    df_final.plot("ratio")
    return df_final  # [['ratio','geometry']]


if __name__ == "__main__":

    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(df_reg, df_dep)
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()
