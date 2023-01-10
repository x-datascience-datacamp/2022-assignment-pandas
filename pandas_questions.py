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
    df_result = pd.merge(
                            regions[['code', 'name']],
                            departments[['region_code', 'code', 'name']],
                            left_on='code',
                            right_on='region_code',
                            how='left',
                            suffixes=('_reg', '_dep'),
                       )

    df_result = df_result.drop(['region_code'], axis=1)

    return df_result


def merge_referendum_and_areas(referendum, regions_and_departments):

    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum['Department code'] = referendum['Department code']\
        .apply(lambda x: x.zfill(2))
    df_result = pd.merge(
                            referendum,
                            regions_and_departments,
                            left_on='Department code',
                            right_on='code_dep',
                            how='inner',
                        )
    return df_result


def compute_referendum_result_by_regions(referendum_and_areas):

    df_result = referendum_and_areas.groupby(['code_reg', 'name_reg'])\
        .agg('sum')[['Registered', 'Abstentions',
                     'Null', 'Choice A', 'Choice B']]\
        .reset_index('name_reg')
    return df_result


def plot_referendum_map(referendum_result_by_regions):

    df_gpd = gpd.read_file('./data/regions.geojson')
    df = pd.merge(
                referendum_result_by_regions,
                df_gpd,
                left_on='code_reg',
                right_on='code',
                how='left',
                )
    df['ratio'] = df['Choice A']/(df['Choice A'] + df['Choice B'])
    geo_df = gpd.GeoDataFrame(df)
    geo_df.plot(column='ratio')

    return geo_df


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
