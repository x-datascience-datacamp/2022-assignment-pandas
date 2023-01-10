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
    regions = pd.read_csv("data/regions.csv", sep=',')
    departments = pd.read_csv("data/departments.csv", sep=',')
    referendum = pd.read_csv("data/referendum.csv", sep=';')
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):

    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions = pd.DataFrame(regions).rename(
        columns={'code': 'code_reg', 'name': 'name_reg'})

    departments = pd.DataFrame(departments).rename(
        columns={'code': 'code_dep', 'name': 'name_dep'})

    regions_and_departments = pd.merge(
        regions[['code_reg', 'name_reg']],
        departments[['code_dep', 'name_dep', 'region_code']],
        left_on='code_reg', right_on='region_code', how='left')

    regions_and_departments = \
        regions_and_departments.drop(columns='region_code')
    return regions_and_departments


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum['Department code'] = referendum['Department code'].str.zfill(2)
    rlt = pd.merge(referendum[[
        'Department code', 'Department name', 'Town code', 'Town name',
        'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']],
        regions_and_departments[
            ['code_reg', 'name_reg', 'code_dep', 'name_dep']],
        left_on='Department code', right_on='code_dep')
    referendum_and_areas = rlt[['Department code', 'Department name',
                                'Town code', 'Town name',
                                'Registered', 'Abstentions', 'Null',
                                'Choice A', 'Choice B',
                                'code_dep', 'code_reg',
                                'name_reg', 'name_dep']]
    return referendum_and_areas


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    print(referendum_and_areas.columns)
    referendum_result_by_regions = referendum_and_areas.groupby('code_reg')[
        'name_reg', 'Registered', 'Abstentions',
        'Null', 'Choice A', 'Choice B'].sum()
    referendum_and_areas = referendum_and_areas[['code_reg', 'name_reg']]
    referendum_and_areas = referendum_and_areas.drop_duplicates(
        keep='first', inplace=False)
    referendum_result_by_regions = pd.merge(referendum_result_by_regions,
                                            referendum_and_areas,
                                            on='code_reg',
                                            how='right')
    referendum_result_by_regions = \
        referendum_result_by_regions[['name_reg',
                                      'Registered', 'Abstentions',
                                      'Null', 'Choice A', 'Choice B']]
    return referendum_result_by_regions


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    regions_carte = gpd.read_file("data/regions.geojson")
    referendum_result_by_regions["ratio"] = \
        (referendum_result_by_regions['Choice A']
            / (referendum_result_by_regions['Choice B']
                + referendum_result_by_regions['Choice A']))
    referendum_result_by_regions = pd.merge(regions_carte,
                                            referendum_result_by_regions
                                            [['name_reg', 'ratio']],
                                            left_on='nom',
                                            right_on='name_reg',
                                            how='left')
    referendum_result_by_regions = referendum_result_by_regions.drop(
        'nom', axis=1)
    return referendum_result_by_regions


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
