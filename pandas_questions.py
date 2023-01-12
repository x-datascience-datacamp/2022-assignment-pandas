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


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.read_csv("data/referendum.csv", sep=";")
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    dep = departments.copy()
    reg = regions.copy()
    dep.rename(columns={
        'code': 'code_dep', 'region_code': 'code_reg', 'name': 'name_dep'
        },
        inplace=True)
    reg.rename(columns={'code': 'code_reg', 'name': 'name_reg'}, inplace=True)
    meg = pd.merge(reg, dep, on='code_reg')[[
        'code_reg', 'name_reg', 'code_dep', 'name_dep'
    ]]
    return meg


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.
    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """

    ref = referendum.copy()
    ref['code_dep'] = ref['Department code']
    ref = ref.iloc[:36565, :]
    for i in range(ref.shape[0]):
        if ref.iloc[i, 9].isdigit() and int(ref.iloc[i, 9]) < 10:
            ref.iloc[i, 9] = '0'+ref.iloc[i, 9]

    meg = pd.merge(ref, regions_and_departments, on='code_dep')[[
        'Department code', 'Department name', 'Town code', 'Town name',
        'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B',
        'code_dep', 'code_reg', 'name_reg', 'name_dep'
    ]]
    return meg


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.
    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """

    ref_by_reg = referendum_and_areas.groupby('name_reg')[[
        'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']].sum()
    ref_by_reg = ref_by_reg.reset_index('name_reg')
    return ref_by_reg


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo = gpd.read_file('data/regions.geojson')
    geo = geo.copy()
    geo.rename(columns={'nom': 'name_reg'}, inplace=True)
    meg = pd.merge(referendum_result_by_regions, geo, on='name_reg')
    meg = gpd.GeoDataFrame(meg)
    meg.plot(column='Choice A', legend=True)
    meg['ratio'] = meg['Choice A']/(meg['Choice A'] + meg['Choice B'])
    return meg


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
