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
    referendum = pd.read_csv("data/referendum.csv", sep=';')
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions_names = dict(zip(regions["code"], regions["name"]))
    merged_df = pd.concat([departments['region_code'], departments['region_code'].apply(lambda x: regions_names[x]),
                           departments['code'], departments['name']], axis=1)
    merged_df.columns = ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    return merged_df


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    regions_names = dict(zip(regions_and_departments["code_dep"], regions_and_departments["name_reg"]))
    department_names = dict(zip(regions_and_departments["code_dep"], regions_and_departments["name_dep"]))
    regions_codes = dict(zip(regions_and_departments["code_dep"], regions_and_departments["code_reg"]))
    referendum = referendum[~referendum["Department code"].str.contains("Z")]
    merged_df = pd.concat([referendum, referendum["Department code"].str.zfill(2).rename('code_dep'),
                           referendum["Department code"].apply(lambda x: regions_codes[x.zfill(2)]).rename('code_reg'),
                           referendum["Department code"].apply(lambda x: regions_names[x.zfill(2)]).rename('name_reg'),
                           referendum["Department code"].apply(lambda x: department_names[x.zfill(2)]).rename(
                               'name_dep')],
                          axis=1)
    return merged_df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    regions_names = dict(zip(referendum_and_areas["code_reg"], referendum_and_areas["name_reg"]))
    temp_df = referendum_and_areas.groupby(["code_reg"], as_index=False).sum().drop(["Town code"], axis=1)
    final_df = pd.concat([temp_df["code_reg"].apply(lambda x: regions_names[x]).rename('name_reg'), temp_df],
                         axis=1).set_index('code_reg')
    return final_df


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    df = gpd.read_file('data/regions.geojson')
    final_df = pd.merge(df, referendum_result_by_regions, left_on='code', right_on='code_reg')
    final_df['ratio'] = final_df['Choice A'] / (final_df['Choice A'] + final_df['Choice B'])
    final_df.plot('ratio', legend=True)
    return final_df


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
