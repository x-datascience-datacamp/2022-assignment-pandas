"""Plotting r ress in pandas.

In short, we want to make beautiful map to report ress of a r. In
some way, we would like to depict ress with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using `geopandas`.
"""
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def load_data():
    """Load data from the CSV files r/regions/departments."""
    r = pd.read_csv('data/referendum.csv', sep=';')
    regions = pd.read_csv('data/regions.csv')
    departments = pd.read_csv('data/departments.csv')
    return r, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions = regions.rename(columns={'code': 'region_code'})
    merged_df = pd.merge(departments, regions, on='region_code', how='left')
    df = merged_df.rename(
        columns={
            'region_code': 'code_reg',
            'code': 'code_dep',
            'name_x': 'name_dep',
            'name_y': 'name_reg'
            })
    df = df[['code_reg', 'name_reg', 'code_dep', 'name_dep']]
    return df


def standardize_dep_code(code):
    if (code == '2A') | (code == '2B'):
        return code
    return '0' + str(int(code))


def merge_referendum_and_areas(r, r_d):
    """Merge r and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    r = r.drop(r[r['Department code'].str.startswith('Z')].index)
    r['Department code'] = r['Department code'].map(standardize_dep_code)

    r_d = r_d.drop(
        r_d[r_d['code_reg'].isin(['DOM', '01', '02', '03', '04', '06'])].index
        )
    r_d['code_dep'] = r_d['code_dep'].map(standardize_dep_code)

    res_df = pd.merge(
        r_d,
        r,
        left_on='code_dep',
        right_on='Department code',
        how='right'
        )
    return res_df


def compute_referendum_result_by_regions(r_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    r_and_areas = r_and_areas.groupby(
        ['code_reg', 'name_reg'], as_index=False).sum()
    r_and_areas = r_and_areas.set_index(
        ['code_reg']).drop(columns=['Town code'])
    return r_and_areas


def plot_referendum_map(r_res_by_regions):
    """Plot a map with the ress from the r.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `r_res_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the res map. The ress
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the ress.
    """
    geo_region = gpd.read_file('data/regions.geojson')
    geo_region = geo_region.rename(columns={'code': 'code_reg'})

    r_res_by_regions = r_res_by_regions.reset_index()
    denom = (r_res_by_regions['Choice A'] + r_res_by_regions['Choice B'])
    r_res_by_regions['ratio'] = r_res_by_regions['Choice A'] / denom
    r_res_by_regions = r_res_by_regions[['code_reg', 'ratio']]

    res_df = pd.merge(
        geo_region,
        r_res_by_regions,
        on='code_reg',
        how='left'
        ).rename(columns={'nom': 'name_reg'})
    return res_df


if __name__ == "__main__":

    r, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(
        df_reg, df_dep
    )
    r_and_areas = merge_referendum_and_areas(
        r, regions_and_departments
    )
    r_ress = compute_referendum_result_by_regions(
        r_and_areas
    )
    print(r_ress)

    plot_referendum_map(r_ress)
    plt.show()
