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
    referendum = pd.read_csv("data/referendum.csv", delimiter=";")
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    merged = pd.merge(regions, departments, left_on='code',
                      right_on='region_code', how='right')
    merged = merged.rename(columns={'region_code': 'code_reg',
                                    'name_x': 'name_reg', 'code_y': 'code_dep',
                                    'name_y': 'name_dep'})
    merged = merged[['code_reg', 'name_reg', 'code_dep', 'name_dep']]
    return merged


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    # filling the department code at 2 digits
    referendum["Department code"] = referendum["Department code"] \
        .apply(lambda x: x.zfill(2))
    # selecting only the metropolitan region (not begining with 'Z')
    referendum = referendum[~referendum["Department code"].str.startswith('Z')]
    df = regions_and_departments.merge(referendum,
                                       how="left",
                                       left_on="code_dep",
                                       right_on="Department code")
    df = df[df["code_dep"].str.len() == 2]
    return df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by 'code_reg' and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    df = referendum_and_areas.drop(["Department code", "Town code",
                                    "Town name"], axis=1)
    df = df.rename(columns={'Region Name': 'name_reg'})
    df = df.groupby(by=["name_reg", "code_reg"],
                    as_index=False).agg({"Registered": "sum",
                                        "Abstentions": "sum", "Null": "sum",
                                         "Choice A": "sum",
                                         "Choice B": "sum"})
    df = df.set_index('code_reg')
    return df


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from 'regions.geojson'.
    * Merge these info into 'referendum_result_by_regions'.
    * Use the method 'GeoDataFrame.plot' to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    # loading the geographic data
    geo_reg = gpd.read_file("data/regions.geojson")
    geo_reg = geo_reg[~geo_reg["code"].str.startswith("0")]
    # merging data
    geo_reg = pd.merge(geo_reg, referendum_result_by_regions,
                       how="left", left_on="code", right_on="code_reg")
    geo_reg = geo_reg.drop(columns=["nom"])
    # computing a "A_ratio" column into geo_reg
    geo_reg["ratio"] = geo_reg["Choice A"] \
        / (geo_reg["Choice A"] + geo_reg["Choice B"])
    # plotting the map
    geo_reg.plot(column="ratio", legend=True, cmap="viridis")
    plt.title("Referendum results: A-ratio per region")
    return gpd.GeoDataFrame(geo_reg)


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
