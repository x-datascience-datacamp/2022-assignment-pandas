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
    regions = pd.read_csv("data/regions.csv", sep=",")
    departments = pd.read_csv("data/departments.csv", sep=",")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    temp = pd.merge(regions[["code", "name"]].rename(
                    columns={"code": "region_code"}),
                    departments[["region_code", "code", "name"]],
                    on="region_code",
                    how="right")
    temp.rename(columns={"region_code": "code_reg",
                "name_x": "name_reg", "code": "code_dep",
                         "name_y": "name_dep"}, inplace=True)
    return temp


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    drop_dep_code = ['ZA', 'ZB', 'ZC', 'ZD', 'ZM', 'ZN', 'ZP', 'ZS',
                     'ZW', 'ZX', 'ZZ']
    new_ref = referendum[~referendum["Department code"].isin(drop_dep_code)]
    temp = new_ref["Department code"].str.len() == 1
    new_ref["Department code"].loc[temp] = ('0'
                                            + new_ref
                                            ["Department code"].loc[temp])
    temp = pd.merge(new_ref,
                    regions_and_departments.rename(
                        columns={"code_dep": "Department code"}),
                    on="Department code", how="left")
    temp["code_dep"] = temp.loc[:, "Department code"]
    return temp


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """

    temp = referendum_and_areas.groupby(["code_reg", "name_reg"])
    temp = temp["Registered", "Abstentions",
                "Null", "Choice A", "Choice B"].sum()
    temp.reset_index(inplace=True)
    temp.set_index("code_reg", inplace=True)
    return temp


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """

    gdf = gpd.read_file("data/regions.geojson")
    temp = pd.merge(referendum_result_by_regions,
                    gdf.rename(
                        columns={"code": "code_reg"})
                    [["code_reg", "geometry"]],
                    on="code_reg", how="left")
    temp.set_index("code_reg", inplace=True)
    temp["ratio"] = temp["Choice A"]/(temp["Choice A"]+temp["Choice B"])
    temp = gpd.GeoDataFrame(temp).set_geometry("geometry")
    temp.plot("ratio", legend=True)
    return gpd.GeoDataFrame(temp[["geometry", "name_reg", "ratio"]])


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
