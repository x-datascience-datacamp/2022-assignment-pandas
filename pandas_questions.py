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

# lounes guergous


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.read_csv("data/referendum.csv", delimiter=";")
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """

    regions = regions.rename(
        columns={
            "id": "id_reg",
            "code": "code_reg",
            "name": "name_reg",
            "slug": "slug_reg",
        }
    )
    departments = departments.rename(
        columns={
            "id": "id_dep",
            "region_code": "code_reg",
            "code": "code_dep",
            "name": "name_dep",
            "slug": "slug_dep",
        }
    )

    return pd.merge(
        regions[["code_reg", "name_reg"]],
        departments[["code_reg", "code_dep", "name_dep"]],
        on="code_reg",
    )


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum = referendum.drop(
        referendum[referendum["Department code"].str.startswith("Z")].index
    )
    referendum["Department code"] = referendum["Department code"].str.zfill(2)

    return pd.merge(
        referendum,
        regions_and_departments,
        left_on="Department code",
        right_on="code_dep",
        how="left",
    )


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """

    name_regions = referendum_and_areas[["code_reg", "name_reg"]]
    name_regions.set_index("code_reg", inplace=True)
    name_regions = name_regions.groupby(["code_reg"]).first()

    referendum_and_areas = referendum_and_areas[
        ["code_reg", "Registered", "Abstentions", "Null", "Choice A", "Choice B"]
    ]
    referendum_and_areas = referendum_and_areas.groupby(["code_reg"]).sum()

    return pd.merge(name_regions, referendum_and_areas, on="code_reg", how="right")


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """

    map = gpd.read_file("data/regions.geojson")

    referendum_result_by_regions = pd.merge(
        map, referendum_result_by_regions, left_on="code", right_on="code_reg"
    )
    referendum_result_by_regions = referendum_result_by_regions.drop(
        ["code", "nom"], axis=1
    )

    referendum_result_by_regions["ratio"] = referendum_result_by_regions["Choice A"] / (
        referendum_result_by_regions["Choice A"]
        + referendum_result_by_regions["Choice B"]
    )
    print(type(referendum_result_by_regions))
    referendum_result_by_regions.plot(column="ratio")
    print(type(gpd.GeoDataFrame(referendum_result_by_regions[["ratio",]])))
    return gpd.GeoDataFrame(referendum_result_by_regions)


map = gpd.read_file("data/regions.geojson")

if __name__ == "__main__":

    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(df_reg, df_dep)
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(referendum_and_areas)
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()
