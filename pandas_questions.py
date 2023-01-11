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
    referendum = pd.DataFrame(pd.read_csv('data/referendum.csv', sep = ';', error_bad_lines = False))
    regions = pd.DataFrame(pd.read_csv('data/regions.csv'))
    departments = pd.DataFrame(pd.read_csv('data/departments.csv'))

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    merge_regions_and_departments = pd.merge(regions, departments, left_on = 'code', right_on = 'region_code', suffixes = ('_reg', '_dep'))
    return merge_regions_and_departments[['code_reg', 'name_reg', 'code_dep', 'name_dep']]


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum_and_areas = pd.merge(referendum, regions_and_departments, left_on = 'Department code', right_on = 'code_dep')
    return referendum_and_areas[ ~ referendum_and_areas['Department code'].str.startswith('Z') ]


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    referendum_result_by_regions = referendum_and_areas.groupby(['code_reg', 'name_reg']).aggregate(sum).drop(columns = 'Town code')
    return referendum_result_by_regions.reset_index('name_reg')


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    coordinates = gpd.read_file('data/regions.geojson')
    referendum_result_by_regions_coordinates = referendum_result_by_regions.merge(coordinates, left_on = 'code_reg', right_on = 'code').drop(columns = 'nom')
    referendum_result_by_regions_coordinates['ratio'] = referendum_result_by_regions_coordinates['Choice A'] / (referendum_result_by_regions_coordinates['Null']+referendum_result_by_regions_coordinates['Choice A'] + referendum_result_by_regions_coordinates['Choice B'])
    geo_df = gpd.GeoDataFrame(referendum_result_by_regions_coordinates)
    geo_df.plot('ratio', legend = True, figsize = (15, 10), cmap = 'Reds')
    plt.title('Choice A rate per region in France')
    return geo_df


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
