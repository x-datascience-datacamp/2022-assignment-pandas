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
    referendum = pd.DataFrame(pd.read_csv('data/referendum.csv', sep=';'))
    regions = pd.DataFrame(pd.read_csv('data/regions.csv', sep=','))
    departments = pd.DataFrame(pd.read_csv('data/departments.csv', sep=','))

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions = regions.rename(columns={'id': 'id', 'code': 'code_reg',
                                      'name': 'name_reg', 'slug': 'slug'})
    departments = departments.rename(columns={'id': 'id',
                                              'region_code': 'code_reg',
                                              'code': 'code_dep',
                                              'name': 'name_dep',
                                              'slug': 'slug'})
    reg_dep = pd.merge(regions[['code_reg', 'name_reg']],
                       departments[['code_reg', 'code_dep', 'name_dep']],
                       on='code_reg')

    return pd.DataFrame(reg_dep)


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    reg_dep = regions_and_departments
    for i in range(len(reg_dep)):
        if reg_dep['code_dep'].iloc[i][0] == '0':
            reg_dep['code_dep'].iloc[i] = reg_dep['code_dep'].iloc[i][1:]
    reg_dep['Department code'] = reg_dep['code_dep']
    reg_dep_ref = pd.merge(reg_dep, referendum, on='Department code')
    reg_dep_ref = reg_dep_ref.dropna()
    return pd.DataFrame(reg_dep_ref)


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
    data['ratio'] = data.apply(lambda x:
                               int(x['Choice A'])/(int(x['Choice A']) +
                                                   int(x['Choice B'])), axis=1)

    return gpd.GeoDataFrame(data)


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
