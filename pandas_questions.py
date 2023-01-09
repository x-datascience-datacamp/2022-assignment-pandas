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
    '''Load data from the CSV files referundum/regions/departments.'''
    referendum = pd.read_csv('data/referendum.csv', sep=';')
    regions = pd.read_csv('data/regions.csv', sep=',')
    departments = pd.read_csv('data/departments.csv', sep=',')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    '''Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    '''
    regions_temp = regions.rename(
        columns={'name': 'name_reg', 'code': 'code_reg'})
    departments_temp = departments.rename(
        columns={'name': 'name_dep', 'region_code': 'code_reg',
                 'code': 'code_dep'})

    regions_temp.drop(columns=['slug', 'id'], axis='columns', inplace=True)
    departments_temp.drop(columns=['slug', 'id'], axis='columns', inplace=True)

    df = pd.merge(regions_temp, departments_temp, on='code_reg', how='right')

    return df


def merge_referendum_and_areas(referendum, regions_and_departments):
    '''Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    '''

    referendum_temp = referendum[referendum['Department name']
                                 != "FRANCAIS DE L'ETRANGER"]
    # del when department code starts with 'Z' for DOM-TOM
    referendum_temp = \
        referendum_temp[~referendum_temp['Department code'].str.startswith(
            'Z')]

    # Change format to prevent issues in the merge
    regions_and_departments['code_dep'] = \
        regions_and_departments['code_dep'].apply(
            lambda x: x[1:] if x.startswith('0') else x)

    df = pd.merge(referendum_temp, regions_and_departments,
                  left_on='Department code', right_on='code_dep', how='left')

    return df


def compute_referendum_result_by_regions(referendum_and_areas):
    '''Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    '''

    reg_result = referendum_and_areas.drop(columns=['code_dep', 'Town code',
                                                    'Town name', 'name_dep',
                                                    'code_reg'],
                                           axis='columns')
    reg_result = reg_result.groupby(
        ['name_reg']).sum().reset_index()

    return reg_result


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """

    regions_geojson = gpd.read_file('data/regions.geojson')
    regions_geojson = regions_geojson.rename(columns={'nom': 'name_reg'})
    map_geojson = regions_geojson.merge(referendum_result_by_regions,
                                        on='name_reg')

    map_geojson['ratio'] = (map_geojson['Choice A']
                            / (map_geojson['Choice A']
                               + map_geojson['Choice B']))

    map_geojson['percentage'] = map_geojson['ratio'] * 100
    map_geojson.plot(column='percentage', legend=True)
    plt.title("Percentage of vote for choice A")

    return map_geojson


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
