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
        r"C:\Users\thoma\Desktop\DataCamp\2022-assignment-pandas\data\referendum.csv",
        sep=";",
    )
    regions = pd.read_csv(
        r"C:\Users\thoma\Desktop\DataCamp\2022-assignment-pandas\data\regions.csv",
        sep=",",
    )
    departments = pd.read_csv(
        r"C:\Users\thoma\Desktop\DataCamp\2022-assignment-pandas\data\departments.csv",
        sep=",",
    )

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    reg = regions[["code", "name"]]
    dep = departments[["region_code", "code", "name"]]
    data_frame_to_return = pd.DataFrame()
    data_frame_to_return[
        ["code_reg", "name_reg", "region_code", "code_dep", "name_dep"]
    ] = reg.merge(dep, how="inner", left_on="code", right_on="region_code")
    data_frame_to_return = data_frame_to_return.drop(columns=["region_code"])
    return data_frame_to_return


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.
    pass
    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum_new = referendum.drop(
        referendum[referendum["Department code"].str.startswith("Z")].index
    )
    referendum_new.loc[:, "Department code"] = referendum_new["Department code"].apply(
        lambda x: x.zfill(2)
    )
    to_return = regions_and_departments.merge(
        referendum_new, left_on="code_dep", right_on="Department code"
    )
    return to_return


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.
    pass
    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    df = referendum_and_areas.groupby(["code_reg", "name_reg"], as_index=False)
    df = df.aggregate(
        {
            "Registered": "sum",
            "Abstentions": "sum",
            "Null": "sum",
            "Choice A": "sum",
            "Choice B": "sum",
        }
    )
    df = df.set_index("code_reg")
    return df


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.
    pass
    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """

    data_path = "data"
    regions = gpd.read_file(f"{data_path}/regions.geojson")
    regions = regions.rename(columns={"code": "code_reg"})
    regions = regions.set_index("code_reg")
    df = pd.merge(
        regions, referendum_result_by_regions, left_index=True, right_index=True
    )
    df["ratio"] = df["Choice A"] / (df["Registered"] - df["Abstentions"] - df["Null"])
    df.plot(column="ratio", legend=True, cmap="OrRd")

    return df


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
