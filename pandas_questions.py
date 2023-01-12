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
    res = pd.merge(
        regions[['code', 'name']],
        departments[['region_code', 'code', 'name']],
        left_on='code', right_on='region_code', how='left')
    res = res.drop('region_code', axis=1)
    res.columns = ['code_reg', 'name_reg', 'code_dep', 'name_dep']

    return res


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    not_metropole = [
        'Guadeloupe', 'Martinique', 'Guyane', 'La Réunion',
        'Mayotte', "Collectivités d'Outre-Mer"]
    code_not_metropole = ['ZA', 'ZB', 'ZC', 'ZD', 'ZM',
                          'ZN', 'ZP', 'ZS', 'ZW', 'ZX', 'ZZ']

    for i in range(1, 10):
        regions_and_departments.loc[regions_and_departments[
            'code_dep'] == ("0" + str(i)), 'code_dep'] = str(i)

    rad_metropole = regions_and_departments[
        -(regions_and_departments['name_reg'].isin(not_metropole))
        ]
    referendum = referendum[
        - referendum['Department code'].isin(code_not_metropole)
        ]

    res = pd.merge(rad_metropole, referendum,
                   left_on='code_dep', right_on='Department code', how='left')
    return res


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    referendum_and_areas = referendum_and_areas[['code_reg',
                                                 'name_reg',
                                                 'Registered', 'Abstentions',
                                                 'Null', 'Choice A',
                                                 'Choice B']]
    referendum_and_areas = referendum_and_areas.set_index('code_reg')

    index_ = referendum_and_areas['name_reg'].unique()
    res = referendum_and_areas.groupby('code_reg').sum()
    res.insert(0, 'name_reg', index_)
    return res


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.
    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """

    geo_reg = gpd.read_file("data/regions.geojson")
    geo_reg = geo_reg[~geo_reg["code"].str.startswith("0")]

    geo_reg = pd.merge(geo_reg, referendum_result_by_regions,
                       how="left", left_on="code", right_on="code_reg")
    geo_reg = geo_reg.drop(columns=["nom"])

    geo_reg["ratio"] = geo_reg["Choice A"] \
        / (geo_reg["Choice A"] + geo_reg["Choice B"])

    geo_reg.plot(column="ratio", legend=True, cmap="viridis")
    plt.title("Referendum results: A-ratio per region")
    return gpd.GeoDataFrame(geo_reg)


if __name__ == "__main__":

    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(
        df_reg, df_dep
    )
    print(regions_and_departments)
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()
