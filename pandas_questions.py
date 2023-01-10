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
    """Load data from the CSV files referendum/regions/departments."""
    referendum = pd.read_csv('data/referendum.csv', sep=';')
    regions = pd.read_csv('data/regions.csv')
    departments = pd.read_csv('data/departments.csv')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """

    merged_df = pd.merge(departments, regions, right_on='code', left_on='region_code', how='left')
    df =  merged_df.rename(columns={'region_code': 'code_reg', 'code_x': 'code_dep', 'name_x': 'name_dep', 'name_y':'name_reg'})
    df = df[['code_reg', 'name_reg', 'code_dep', 'name_dep']]
    return df


def standardize_dep_code(code):
    if (code == '2A') | (code == '2B'):
        return code
    
    else: 
        return '0' + str(int(code))

def merge_referendum_and_areas(referendum, r_d):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum = referendum.drop(referendum[referendum['Department code'].str.startswith('Z')].index)
    referendum['Department code'] = referendum['Department code'].map(standardize_dep_code)

    r_d = r_d.drop(r_d[r_d['code_reg'].isin(['DOM', '01', '02', '03', '04', '06'])].index)
    r_d['code_dep'] = r_d['code_dep'].map(standardize_dep_code)

    res_df = pd.merge(r_d, referendum, left_on='code_dep', right_on='Department code', how='right')
    return res_df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    referendum_and_areas = referendum_and_areas.groupby(['code_reg', 'name_reg'], as_index=False).sum()
    referendum_and_areas = referendum_and_areas.set_index(['code_reg']).drop(columns=['Town code'])
    return referendum_and_areas


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo_region = gpd.read_file('data/regions.geojson')
    geo_region = geo_region.rename(
        columns={'code':'code_reg'}
        )

    referendum_result_by_regions = referendum_result_by_regions.reset_index()
    referendum_result_by_regions['ratio'] =  referendum_result_by_regions['Choice A'] / (referendum_result_by_regions['Choice A'] + referendum_result_by_regions['Choice B'])
    referendum_result_by_regions = referendum_result_by_regions[['code_reg', 'ratio']] 

    res_df = pd.merge(geo_region, referendum_result_by_regions, on='code_reg', how='left').rename(columns={'nom':'name_reg'})  
    return res_df


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
