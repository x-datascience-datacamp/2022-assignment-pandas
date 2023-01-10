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
    df = pd.merge(
        departments[["code", "name", "region_code"]],
        regions[["code", "name"]],
        how="left",
        left_on=["region_code"],
        right_on=["code"],
    )

    df = df[["region_code", "name_y", "code_x", "name_x"]]

    df.columns = ["code_reg", "name_reg", "code_dep", "name_dep"]

    df = df.dropna()

    return df


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    dom1 = ["ZA", "ZB", "ZC", "ZD", "ZM",
            "ZN", "ZP", "ZS", "ZW", "ZX", "ZZ"]

    df_dom1 = referendum["Department code"].isin(dom1)
    ref = referendum.drop(
        referendum[df_dom1].index, inplace=False
    )

    reg_and_dep = regions_and_departments.drop(
        regions_and_departments[
            regions_and_departments["code_dep"].isin(
                [
                    "971",
                    "972",
                    "973",
                    "974",
                    "976",
                    "975",
                    "977",
                    "978",
                    "984",
                    "986",
                    "987",
                    "988",
                    "989",
                ]
            )
        ].index,
        inplace=False,
    )
    reg_and_dep["code_dep"][:9] = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]

    df = pd.merge(
        ref, reg_and_dep, how="left",
        left_on=["Department code"],
        right_on=["code_dep"]
    )
    df = df.dropna()

    return df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    df_comp = (
        referendum_and_areas[
            ["code_reg", "Registered",
             "Abstentions", "Null",
             "Choice A", "Choice B"]
        ]
        .groupby(by=["code_reg"])
        .sum()
    )

    df_comp["name_reg"] = referendum_and_areas.sort_values(by=["code_reg"])[
        "name_reg"
    ].unique()

    df_comp = df_comp[
        ["name_reg", "Registered",
         "Abstentions", "Null",
         "Choice A", "Choice B"]
    ]

    df_comp = df_comp.dropna()

    return df_comp


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo_df = gpd.read_file("data/regions.geojson")

    map_df = pd.merge(
        referendum_result_by_regions,
        geo_df[["nom", "geometry"]],
        how="left",
        left_on=["name_reg"],
        right_on=["nom"],
    )

    df_abs = map_df["Choice B"] + map_df["Choice A"]

    map_df["ratio"] = map_df["Choice A"] / df_abs

    gdf = gpd.GeoDataFrame(map_df, geometry=map_df["geometry"])

    gdf = gdf.dropna()

    gdf.plot(column="ratio")

    return gdf


if __name__ == "__main__":

    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(df_reg, df_dep)
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()
