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
    departments = pd.read_csv('./data/departments.csv')
    referendum = pd.read_csv('./data/referendum.csv', delimiter=";")
    regions = pd.read_csv('./data/regions.csv')
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions = regions.rename(columns={'id': 'id_reg', 'code': 'code_reg',
                                      'name': 'name_reg', 'slug': 'slug_reg'})
    departments = departments.rename(
        columns={'id': 'id_dep', 'region_code': 'code_reg',
                 'code': 'code_dep', 'name': 'name_dep',
                 'slug': 'slug_dep'})

    return pd.merge(regions[['code_reg', 'name_reg']],
                    departments[['code_reg', 'code_dep', 'name_dep']],
                    on='code_reg')


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum = referendum.drop(
        referendum[referendum["Department code"].str.startswith("Z")].index)
    referendum['Department code'] = referendum['Department code'].str.zfill(2)
    return pd.merge(referendum, regions_and_departments,
                    left_on='Department code', right_on='code_dep',
                    how='left')


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    ref_res_reg = (referendum_and_areas.groupby(
        ['code_reg', 'name_reg'])
        [['Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']]
        .sum().reset_index(level=['name_reg']))
    return ref_res_reg


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    df = gpd.read_file("data/regions.geojson")
    res = pd.merge(
        referendum_result_by_regions,
        df,
        how="left",
        left_on=["code_reg"],
        right_on=["code"],
    )
    res["ratio"] = res["Choice A"] \
        / (res["Choice A"] + res["Choice B"])
    gdf = gpd.GeoDataFrame(res)
    gdf.plot("ratio")
    return gdf


if __name__ == "__main__":
    ref, df_reg, df_dep = load_data()
    merge = merge_regions_and_departments(df_reg, df_dep)
    regions_and_departments = merge_regions_and_departments(df_reg, merge)
    print(regions_and_departments)
    referendum_and_areas = merge_referendum_and_areas(
        ref, regions_and_departments)
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas)
    print(referendum_results)
    plot_referendum_map(referendum_results)
    plt.show()
