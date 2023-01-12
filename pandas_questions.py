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
    regions = pd.read_csv("data/regions.csv", sep=',')
    departments = pd.read_csv("data/departments.csv", sep=",")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions = regions.rename(
        columns={'name': 'name_reg',
                 'code': 'code_reg'})

    departments = departments.rename(
        columns={'name': 'name_dep',
                 'region_code': 'code_reg',
                 'code': 'code_dep'})

    regions_departments = pd.merge(regions, departments, on='code_reg')
    regions_departments = regions_departments[['code_reg',
                                               'name_reg',
                                               'code_dep',
                                               'name_dep']]

    return regions_departments


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum['Department code'] = referendum['Department code']\
        .apply(lambda x: x.zfill(2))

    referendum_areas = pd.merge(
        referendum,
        regions_and_departments,
        left_on='Department code',
        right_on='code_dep'
    )
    referendum_areas.drop(columns=['code_dep', 'name_dep'])  # Doublon

    return referendum_areas


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    count = referendum_and_areas.groupby(['name_reg', 'code_reg'])[
        'name_reg',
        'Registered',
        'Abstentions',
        'Null',
        'Choice A',
        'Choice B'].sum()

    count.reset_index('name_reg', inplace=True)

    return count


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    dt_geopand = gpd.read_file('data/regions.geojson').set_index("code")
    dt_geopand = dt_geopand.join(referendum_result_by_regions, how="right")
    dt_geopand["ratio"] = dt_geopand["Choice A"] / \
        (dt_geopand["Choice A"] + dt_geopand["Choice B"])
    dt_geopand.plot("ratio")
    dt_geopand.rename({'nom': 'name_reg'})

    return dt_geopand


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
