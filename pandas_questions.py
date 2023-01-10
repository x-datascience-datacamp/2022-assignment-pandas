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
    df = regions[["code", "name"]].merge(departments[
        ["region_code", "code", "name"]], left_on=["code"],
        right_on=["region_code"], how='right')
    df = df.drop('region_code', axis=1)
    df.columns = ['code_reg', 'name_reg', 'code_dep', 'name_dep']

    return pd.DataFrame(df)


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    i = referendum.index[referendum["Department code"] == "ZA"].tolist()[0]
    df = referendum.iloc[:i]
    i1 = regions_and_departments.index[
        regions_and_departments["code_reg"] == "COM"].tolist()[0]
    df1 = regions_and_departments.iloc[:i1]
    df1.loc[:9, "code_dep"][:9] = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]

    df = df.merge(
        df1, left_on=["Department code"],
        right_on=["code_dep"], how='right')

    df = pd.DataFrame.reindex(
        df, columns=[
            'Department code', 'Department name',
            'Town code', 'Town name', 'Registered',
            'Abstentions', 'Null', 'Choice A', 'Choice B',
            'code_dep', 'code_reg', 'name_reg', 'name_dep'])
    df.drop(df.tail(5).index, inplace=True)

    return df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    df1 = pd.DataFrame(
        referendum_and_areas.groupby(by=['code_reg', 'name_reg']).sum())
    df1 = df1.drop(['Town code'], axis=1)
    df1.reset_index(inplace=True, level=['name_reg'])
    return pd.DataFrame(df1)


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """

    df_reg = gpd.read_file('data/regions.geojson')
    df_reg = df_reg.drop(index=range(9, 14))
    df = referendum_result_by_regions

    df = df.merge(df_reg, left_on=["code_reg"], right_on=["code"], how='right')

    df['ratio'] = df['Choice A'] / (df['Choice A'] + df['Choice B'])
    df = gpd.GeoDataFrame(df)

    fig, ax = plt.subplots(1, 1)
    df.plot(column='ratio', ax=ax, legend=True)

    return df


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
