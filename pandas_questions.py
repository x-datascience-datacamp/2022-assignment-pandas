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
    referendum = pd.read_csv('./data/referendum.csv', sep=";")
    regions = pd.read_csv('./data/regions.csv', sep=",")
    departments = pd.read_csv('./data/departments.csv', sep=",")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """

    merged_data = departments.merge(
        regions,
        how='left',
        left_on=['region_code'],
        right_on=['code'],
        suffixes=['_dep', '_reg']
    )
    return merged_data[['code_reg', 'name_reg', 'code_dep', 'name_dep']]


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    r_a_d = regions_and_departments[
        regions_and_departments['code_reg'] != "COM"
    ]
    r_a_d['code_reg'] = r_a_d['code_reg'].astype(int)
    r_a_d['code_dep'] = [c[1] if c[0] == '0' else c for c in r_a_d['code_dep']]
    data = referendum.merge(
        r_a_d,
        how='inner',
        left_on='Department code',
        right_on='code_dep')
    data = data[data['Department name'] != "FRANCAIS DE L'ETRANGER"]
    return data


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """

    data = referendum_and_areas[[
        'code_reg',
        'name_reg',
        'Registered',
        'Abstentions',
        'Null',
        'Choice A',
        'Choice B']]
    data = data.groupby(['code_reg', 'name_reg']).apply(
        lambda x: x.abs().sum()).reset_index()
    data.index = data['code_reg']
    data = data.drop(['code_reg'], axis=1)
    return data


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """

    gd = gpd.read_file('./data/regions.geojson')
    gd = gd.merge(
        referendum_result_by_regions,
        how='inner',
        left_on='nom',
        right_on='name_reg'
    )
    gd['ratio'] = gd['Choice A'] / (gd['Choice A'] + gd['Choice B'])
    gd.plot("ratio", cmap="Blues")
    return gd


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
