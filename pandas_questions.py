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
    referendum = pd.read_csv("./data/referendum.csv", sep=';')
    regions = pd.read_csv("./data/regions.csv", sep=',')
    departments = pd.read_csv("./data/departments.csv", sep=',')
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    # Merge the regions and departments on the column "code" and "region_code"
    # respectively, and keep only the columns "code" and "name" from regions
    df = pd.merge(
        left=regions,
        right=departments,
        left_on="code",
        right_on="region_code",
        suffixes=("_reg", "_dep"),
    )[["code_reg", "name_reg", "code_dep", "name_dep"]]
    return df


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    # To avoid warning, make a copy of the dataframe
    df = referendum.copy()
    # Drop the lines relative to DOM-TOM-COM departments and abroad
    # i.e the departments with code starting with Z
    df = df[~df['Department code'].str.startswith('Z')]
    # Prevent the code with 1 2 3 4 instead of 01 02 03 04 to make a problem
    df['Department code'] = (df['Department code']
                             .str
                             .zfill(2))
    # Merge the referendum and regions_and_departments
    df = pd.merge(df,
                  regions_and_departments,
                  left_on='Department code',
                  right_on='code_dep')
    return df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    # Group by "code_reg" and "name_reg", then aggregate the sum of each field
    # set index as "code_reg" to avoid having two indexes due to group by
    df = (referendum_and_areas
          .groupby(by=["code_reg", "name_reg"], as_index=False)
          .agg({"Registered": "sum",
                "Abstentions": "sum",
                "Null": "sum",
                "Choice A": "sum",
                "Choice B": "sum"})
          .set_index("code_reg"))
    return df


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    # Load the geographic data with geopandas from regions.geojson
    regions = gpd.read_file("./data/regions.geojson").set_index("code")
    # Merge these info into referendum_result_by_regions doing a right join
    referendum_result_by_regions = (pd.merge(regions,
                                             referendum_result_by_regions,
                                             left_index=True,
                                             right_index=True,
                                             how="right"))
    # Compute the ratio
    referendum_result_by_regions["ratio"] = (
        referendum_result_by_regions["Choice A"]
        / (referendum_result_by_regions["Choice A"]
           + referendum_result_by_regions["Choice B"]))
    # Use the method GeoDataFrame.plot to display the result map
    referendum_result_by_regions.plot(column="ratio", legend=True)
    plt.plot()
    return referendum_result_by_regions


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
