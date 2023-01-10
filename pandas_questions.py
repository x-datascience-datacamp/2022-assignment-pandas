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
    newData = (
        pd.merge(
            left=departments,
            right=regions,
            left_on="region_code",
            right_on="code",
            how="left",
        )
    )[["region_code", "name_y", "code_x", "name_x"]]
    newData.columns = ["code_reg", "name_reg", "code_dep", "name_dep"]
    return newData


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    regions_and_departments["code_dep"] = regions_and_departments[
        "code_dep"].apply(
        lambda x: supprimer0(x)
    )
    newData = pd.merge(
        left=referendum,
        right=regions_and_departments,
        left_on="Department code",
        right_on="code_dep",
    )

    return newData


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    new = referendum_and_areas.groupby("code_reg").sum()[
        ["Registered", "Abstentions", "Null", "Choice A", "Choice B"]
    ]
    new.reset_index("code_reg")

    newData = pd.merge(
        left=new,
        right=referendum_and_areas[["name_reg", "code_reg"]].drop_duplicates(),
        on="code_reg",
        how="left",
        )[["name_reg", "Registered", "Abstentions",
           "Null", "Choice A", "Choice B"]]
    return newData


def supprimer0(x):
    """Aide plot_referendum_map."""
    if x[0] == "0":
        return x[1:]
    return x


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    mapi = gpd.read_file("data/regions.geojson")
    print(referendum_result_by_regions.columns)
    new = pd.merge(
        left=referendum_result_by_regions,
        right=mapi,
        left_on="name_reg",
        right_on="nom",
        how="left",
    )[
        [
            "Registered",
            "Abstentions",
            "Null",
            "Choice A",
            "Choice B",
            "name_reg",
            "code",
            "nom",
            "geometry",
        ]
    ]

    new.columns = [
        "Registered",
        "Abstentions",
        "Null",
        "Choice A",
        "Choice B",
        "name_reg",
        "code_reg",
        "nom",
        "geometry",
    ]
    new["ratio"] = new["Choice A"] / (new["Choice A"] + new["Choice B"])
    new = gpd.GeoDataFrame(new)
    new.plot("ratio")

    return gpd.GeoDataFrame(new)


if __name__ == "__main__":

    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(df_reg, df_dep)
    referendum_and_areas = merge_referendum_and_areas(
        referendum,
        regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas)
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()
