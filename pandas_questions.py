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
import unidecode


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.read_csv('data/referendum.csv')
    regions = pd.read_csv('data/regions.csv')
    departments = pd.read_csv('data/departments.csv', sep=';')
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    a = regions[['code', 'name']].rename(columns={
        'code': 'code_reg', 'name': 'name_reg'})
    b = departments[['region_code', 'code', 'name']].rename(columns={
        'region_code': 'code_reg', 'code': 'code_dep', 'name': 'name_dep'})
    df_merged = pd.merge(a, b, on='code_reg')
    return df_merged


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    d = regions_and_departments[
        regions_and_departments['code_reg'].apply(lambda x: x.isnumeric())]
    d = d[d['code_reg'].apply(lambda x: 11 <= float(x) <= 94)]
    d['name_dep'] = d['name_dep'].apply(
        lambda x: unidecode.unidecode(x).upper()).unique()
    d['name_dep'] = d['name_dep'].str.replace(r'\W', '', regex=True)
    c = referendum.rename(columns={
        'Department code': 'code_dep', 'Department name': 'name_dep'})
    c['name_dep'] = c['name_dep'].str.replace(r'\W', '', regex=True)

    return pd.merge(d, c, on=["code_dep", "name_dep"])


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    grouped = referendum_and_areas.groupby(['name_reg', 'code_reg']).sum()
    return grouped.reset_index('name_reg').drop(columns={'Town code'})


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    gdf = gpd.read_file("data/regions.geojson")
    gdf = gdf.rename(columns={'code': 'code_reg', 'nom': 'name_reg'})
    f = pd.merge(referendum_result_by_regions, gdf, on=[
        "code_reg", "name_reg"]).set_index('code_reg')
    f['ratio'] = f['Choice A'] / f[
        ['Abstentions', 'Null', 'Choice A', 'Choice B']].sum(axis=1)
    f = gpd.GeoDataFrame(f)
    f.plot('ratio')

    return f


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
