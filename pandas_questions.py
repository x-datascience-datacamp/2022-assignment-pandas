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
    data_path = 'data'
    referendum = pd.read_csv(f'{data_path}/referendum.csv', sep=';')
    regions = pd.read_csv(f'{data_path}/regions.csv', sep=',')
    departments = pd.read_csv(f'{data_path}/departments.csv', sep=',')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    df = pd.merge(regions, departments, left_on='code', right_on='region_code')
    df = df.drop(['code_x', 'id_x', 'slug_x', 'slug_y', 'id_y'], axis=1)
    df = df.rename(columns={'region_code': 'code_reg', 'name_x': 'name_reg',
                            'code_y': 'code_dep', 'name_y': 'name_dep'})

    return df


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    df = referendum[~referendum['Department code'].str.startswith('Z')].copy()
    df.loc[:, 'Department code'] = df['Department code'].apply(
        lambda x: x.zfill(2))
    df = pd.merge(df, regions_and_departments,
                  left_on='Department code', right_on='code_dep')

    return df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    df = referendum_and_areas.groupby(['code_reg', 'name_reg'], as_index=False)
    df = df.aggregate({'Registered': 'sum', 'Abstentions': 'sum',
                       'Null': 'sum', 'Choice A': 'sum', 'Choice B': 'sum'})
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
    data_path = 'data'
    regions = gpd.read_file(f'{data_path}/regions.geojson')
    regions = regions.rename(columns={'code': 'code_reg'})
    regions = regions.set_index('code_reg')
    df = pd.merge(regions, referendum_result_by_regions,
                  left_index=True, right_index=True)
    df['ratio'] = (df['Choice A'] /
                   (df['Registered'] - df['Abstentions'] - df['Null']))
    df.plot(column='ratio', legend=True, cmap='OrRd')

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
