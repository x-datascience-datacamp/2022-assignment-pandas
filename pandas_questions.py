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
    referendum = pd.DataFrame(pd.read_csv('data/referendum.csv', sep=';',))
    regions = pd.DataFrame(pd.read_csv('data/regions.csv', sep=','))
    departments = pd.DataFrame(pd.read_csv('data/departments.csv', sep=','))

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions.rename(columns={'code': 'code_reg', 'name': 'name_reg'},
                   inplace=True)
    departments.rename(columns={'code': 'code_dep', 'name': 'name_dep',
                                'region_code': 'code_reg'}, inplace=True)
    data = pd.merge(regions, departments, on='code_reg', how='left')
    return data[['code_reg', 'name_reg', 'code_dep', 'name_dep']]


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum['Department code'] = referendum.apply(
        lambda x: tidy_id(x['Department code']), axis=1)
    print(referendum['Department code'])
    referendum.rename(columns={'Department code': 'code_dep'}, inplace=True)
    data = pd.merge(referendum, regions_and_departments,
                    on='code_dep', how='right')
    data['Department code'] = data['code_dep']
    return data.dropna(axis=0)


def tidy_id(r):

    if (str(r) in {'1', '2', '3', '4', '5', '6', '7', '8', '9'}):
        return '0'+str(r)
    else:
        return str(r)


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    data = pd.DataFrame(referendum_and_areas[['code_reg',
                                              'name_reg',
                                              'Registered',
                                              'Abstentions',
                                              'Null',
                                              'Choice A',
                                              'Choice B']])
    data = data.groupby(['code_reg', 'name_reg']).sum()
    data = data.reset_index(['code_reg', 'name_reg'])
    data = data.set_index('code_reg')
    return data


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo_data = gpd.GeoDataFrame(gpd.read_file('data/regions.geojson'))
    geo_data.rename(columns={'nom': 'name_reg'}, inplace=True)
    data = pd.merge(geo_data, referendum_result_by_regions, on='name_reg')

    gpd.GeoDataFrame.plot(data['Choice A']/(data['Choice A']+data['Choice B']))
    data['ratio'] = data.apply(lambda x: ratio(int(x['Choice A']),
                                               int(x['Choice B'])), axis=1)

    return gpd.GeoDataFrame(data)


def ratio(Choice_A, Choice_B):
    return Choice_A/(Choice_A + Choice_B)


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
