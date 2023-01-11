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
    referendum = pd.read_csv("data/referendum.csv", delimiter=';')
    regions = pd.read_csv('data/regions.csv')
    departments = pd.read_csv('data/departments.csv')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    merged_data = pd.merge(regions[['code', 'name']],departments[['region_code', 'code', 'name']],how='right' \
        ,left_on='code', right_on='region_code', suffixes=['_reg', '_dep'])

    return merged_data.drop(columns=['region_code'])


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    regions_and_departments['code_dep'] = regions_and_departments['code_dep'].apply(lambda x: x[1:] if x[0]=='0' else x)
    referendum = referendum[referendum['Department code'].str.len()<3]
    referendum = referendum[referendum['Department name'] != "FRANCAIS DE L'ETRANGER"]
    merged_data = pd.merge(referendum, regions_and_departments, how = 'left', left_on='Department code', right_on='code_dep')
    merged_data = merged_data.dropna()
    return merged_data


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    df = referendum_and_areas[['name_reg','code_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']]
    df = df.groupby(['code_reg','name_reg']).agg(sum)
    df = df.reset_index()
    df = df.set_index('code_reg')
    
    return df


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geodata = gpd.read_file('data/regions.geojson')
    data_geometry = pd.merge(left = geodata, right = referendum_result_by_regions , right_on = 'code_reg', left_on = 'code', how = 'left')
    data_geometry['ratio'] = data_geometry['Choice A']/(data_geometry['Registered']-(data_geometry['Abstentions']+data_geometry['Null']))
    data_geometry.plot(column='ratio')

    return data_geometry


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
