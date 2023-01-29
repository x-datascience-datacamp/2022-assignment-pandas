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
    referendum = pd.read_csv('data/referendum.csv', sep =';')
    regions = pd.read_csv('data/regions.csv', sep = ',')
    departments = pd.read_csv('data/departments.csv', sep =',')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    df_test = pd.merge(departments,
                  regions,
                  how='left',
                  left_on='region_code',
                  right_on='code',
                  suffixes=('_dep', '_reg'))
    df_final = df_test[['code_reg', 'name_reg', 'code_dep', 'name_dep']]

    return df_final


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum['Department code'] = referendum['Department code'].astype(str).str.zfill(2)
    df_final = pd.merge(referendum,
                  regions_and_departments,
                  how='inner',
                  left_on='Department code',
                  right_on='code_dep')


    return df_final


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.
    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    df_test = referendum_and_areas[['code_reg',
                               'name_reg',
                               'Registered',
                               'Abstentions',
                               'Null',
                               'Choice A',
                               'Choice B']]
    df_grouped = df_test.groupby(['code_reg','name_reg']).sum()
    df_grouped = df_grouped.reset_index(level='name_reg')
    return df_grouped


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    # Load the geographic data
    regions = gpd.read_file("data/regions.geojson")

    merged = pd.merge(referendum_result_by_regions,
                      regions,
                      how ='left',
                      left_on="code_reg",
                      right_on='code')

    # Calculate the ratio of 'Choice A' votes over total expressed ballots
    merged["ratio"] = merged["Choice A"] / (merged["Choice A"] + merged["Choice B"])
    geo_df = gpd.GeoDataFrame(merged,geometry = merged.geometry)
    # Plot the results
    _,ax_fig = plt.subplots(figsize = (10,10))
    geo_df.plot(column = 'ratio', ax = ax_fig, cmap = 'rainbow',
            legend = True, legend_kwds={'shrink': 0.3},
            markersize = 10)
    ax_fig.set_title('Ratio of Choice A')
    # Return the merged GeoDataFrame with the 'ratio' column
    return geo_df


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
