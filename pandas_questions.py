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
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    dfr = regions.rename(columns={'code':
                                  'region_code'})[['region_code', 'name']]
    dfp = departments[['region_code', 'code', 'name']]
    df_merge = pd.merge(dfp, dfr, on='region_code', suffixes=['_dep',
                                                              '_reg'])
    df_merge = df_merge[['region_code', 'name_reg', 'code', 'name_dep']]
    df_merge = df_merge.rename(columns={'region_code':
                                        'code_reg', 'code': 'code_dep'})
    return df_merge


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    ref = referendum.rename(columns={'Department code': 'code_dep'})
    ref_filtered = ref[~ref['code_dep'].str.isalpha()]
    ref_filtered["Department code"] = ref_filtered.iloc[:, 0]
    filters = regions_and_departments['code_dep']
    filters = filters[regions_and_departments['code_dep'].str.startswith('0')]
    for i, el in enumerate(filters.values):
        filters.values[i] = el.replace("0", "")
    regions_and_departments['code_dep'][
        regions_and_departments['code_dep'].str.startswith('0')] = filters
    merged = pd.merge(regions_and_departments, ref_filtered, on='code_dep')
    res = merged[['Department code',
                  'Department name',
                  'Town code',
                  'Town name',
                  'Registered', 'Abstentions', 'Null',
                  'Choice A', 'Choice B',
                  'code_dep', 'code_reg', 'name_reg', 'name_dep']]
    return res


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    res = referendum_and_areas.set_index("code_reg")[['name_reg',
                                                      'Registered',
                                                      'Abstentions',
                                                      'Null',
                                                      'Choice A',
                                                      'Choice B'
                                                      ]].groupby(
        "name_reg").sum()
    res = res.reset_index()
    return res


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    file = gpd.read_file("data/regions.geojson")
    file.columns = ['code', 'name_reg', 'geometry']
    gdf = pd.merge(file, referendum_result_by_regions, on="name_reg")
    gdf["ratio"] = gdf["Choice A"] / (gdf["Choice A"] + gdf["Choice B"])
    gdf.plot("ratio")
    return gdf


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
