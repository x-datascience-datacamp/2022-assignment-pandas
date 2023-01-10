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
    referendum = pd.read_csv(
        "data/referendum.csv",
        sep=";",
    )
    regions = pd.read_csv("data/regions.csv", sep=",")
    departments = pd.read_csv("data/departments.csv", sep=",")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    df_merged = pd.merge(
        regions, departments, left_on="code", right_on="region_code", how="left"
    )
    df_merged.drop(["id_x", "code_x", "slug_x", "slug_y", "id_y"] \ 
    , axis=1, inplace=True)
    df_merged.rename(
        columns={
            "name_x": "name_reg",
            "name_y": "name_dep",
            "region_code": "code_reg",
            "code_y": "code_dep",
        },
        inplace=True,
    )

    return df_merged


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum["Department code"] = referendum["Department code"].apply(
        lambda x: x.zfill(2)
    )
    df_merged = pd.merge(
        regions_and_departments,
        referendum,
        left_on="code_dep",
        right_on="Department code",
        how="inner",
    )

    return df_merged


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    df_return = (
        referendum_and_areas.groupby(["name_reg", "code_reg"], as_index=False)
        .agg(
            {
                "Registered": "sum",
                "Abstentions": "sum",
                "Null": "sum",
                "Choice A": "sum",
                "Choice B": "sum",
            }
        )
        .set_index("code_reg")
    )

    return df_return


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo_data = gpd.read_file("data/regions.geojson")
    geo_referendum = pd.merge(
        geo_data,
        referendum_result_by_regions,
        left_on="code",
        right_on="code_reg",
        how="inner",
    )
    geo_referendum["ratio"] = geo_referendum["Choice A"] / (
        geo_referendum["Registered"]
        - geo_referendum["Abstentions"]
        - geo_referendum["Null"]
    )
    geo_referendum.plot(
        column="ratio",
        legend=True,
        legend_kwds={"label": "Ratio A", "orientation": "horizontal"},
    )

    return geo_referendum


if __name__ == "__main__":

    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(df_reg, df_dep)
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions( \
        referendum_and_areas)
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()
