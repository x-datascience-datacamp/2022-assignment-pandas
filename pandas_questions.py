"""Plotting referendum results in pandas.

In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using `geopandas`.
"""
import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    dir = "./data"
    referendum = pd.read_csv(f"{dir}/referendum.csv", delimiter=';',
                             on_bad_lines='skip')
    regions = pd.read_csv(f"{dir}/regions.csv",
                          on_bad_lines='skip')
    departments = pd.read_csv(f"{dir}/departments.csv", delimiter=',',
                              on_bad_lines='skip')

    return referendum, regions, departments


def merge_regions_and_departments(regions: pd.DataFrame,
                                  departments: pd.DataFrame):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions.columns = ['id', 'code_reg', 'name_reg', 'slug']
    departments.columns = ['id', 'code_reg', 'code_dep', 'name_dep', 'slug']
    dep = departments[['code_reg', 'code_dep', 'name_dep']]
    merged_reg_dep = pd.merge(regions[['code_reg', 'name_reg']],
                              dep,
                              on='code_reg', how='left')

    return merged_reg_dep


def merge_referendum_and_areas(referendum: pd.DataFrame,
                               regions_and_departments: pd.DataFrame):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum['Department code'] = referendum['Department code'].str.zfill(2)
    merged_ref_reg_dep = pd.merge(referendum, regions_and_departments,
                                  left_on='Department code',
                                  right_on='code_dep', how='inner')

    return merged_ref_reg_dep


def compute_referendum_result_by_regions(referendum_and_areas: pd.DataFrame):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    ref_area = referendum_and_areas
    codename = ["code_reg", "name_reg"]
    absolute_count = ref_area.groupby(codename).aggregate(np.sum).reset_index()
    absolute_count = absolute_count[['name_reg', 'Registered', 'Abstentions',
                                     'Null', 'Choice A', 'Choice B']]

    return absolute_count


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    reg_json = gpd.read_file("data/regions.geojson")
    ref_res_by_regions = referendum_result_by_regions
    ref_res_by_regions['nom'] = ref_res_by_regions['name_reg']
    ref_res_by_regions["ratio"] = (ref_res_by_regions["Choice A"] /
                                   (ref_res_by_regions["Choice A"] +
                                    ref_res_by_regions["Choice B"]))

    ref_map = gpd.GeoDataFrame(pd.merge(referendum_result_by_regions,
                                        reg_json, on='nom'))
    ref_map.plot("ratio")
    return ref_map


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
