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
    referendum = pd.read_csv('data/referendum.csv', sep=';')
    regions = pd.read_csv('data/regions.csv')
    departments = pd.read_csv('data/departments.csv')
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions = pd.DataFrame(regions)
    departments = pd.DataFrame(departments)

    regions = regions.rename(columns={'code': 'code_reg', 'name':
                                      'name_reg', 'slug': 'region_slug'})
    departments = departments.rename(columns={'region_code': 'code_reg',
                                              'code': 'code_dep',
                                              'name': 'name_dep',
                                              'slug': 'dep_slug'})

    merged_df = pd.merge(regions, departments, on='code_reg', how='inner')
    merged_df = merged_df[['code_reg', 'name_reg', 'code_dep', 'name_dep']]
    return merged_df


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum_copy = referendum.copy()
    for i in range(10):
        referendum_copy['Department code'].replace(str(i),
                                                   '0'+str(i),
                                                   inplace=True)
    referendum_copy['code_dep'] = referendum_copy['Department code']
    referendum_copy = referendum_copy.iloc[:36565, :]
    merged_df = pd.merge(referendum_copy,
                         regions_and_departments,
                         on='code_dep')[['Department code', 'Department name',
                                         'Town code', 'Town name',
                                         'Registered', 'Abstentions',
                                         'Null', 'Choice A',
                                         'Choice B', 'code_dep',
                                         'code_reg', 'name_reg',
                                         'name_dep']]
    return merged_df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    df = referendum_and_areas.groupby(['code_reg']).sum()
    df = df[['Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']]
    regions = referendum_and_areas[['name_reg', 'code_reg']]
    regions = regions.groupby(['code_reg']).first()
    df_merged = pd.merge(df, regions, on='code_reg')
    return df_merged


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geographic_data = gpd.read_file("data/regions.geojson")
    df_merged = pd.merge(referendum_result_by_regions,
                         geographic_data,
                         left_index=True,
                         right_on="code",
                         how="left")
    df_merged["ratio"] = df_merged["Choice A"] / (df_merged["Choice A"] +
                                                  df_merged["Choice B"])
    df_merged = gpd.GeoDataFrame(df_merged)
    df_merged.plot(column="ratio")
    return df_merged


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
