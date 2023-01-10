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
    referendum = pd.DataFrame({})
    regions = pd.DataFrame({})
    departments = pd.DataFrame({})
    
    """
    Example
    
    regions = pd.DataFrame({'code_reg': [1, 2, 3], 'name_reg': ['Region 1', 'Region 2', 'Region 3']})
    departments = pd.DataFrame({'code_dep': [101, 102, 103, 201, 202], 'name_dep': ['Department 101', 
                                                                                'Department 102', 
                                                                                'Department 103', 
                                                                                'Department 201', 
                                                                                'Department 202'], 
                                                                                'code_reg': [1, 1, 2, 2, 3]})
                                                                                
    referendum = pd.DataFrame({'code_dep': [101, 102, 103, 201, 202], 'votes': [1000, 2000, 3000, 4000, 5000]})
    """
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    # Merge the dataframes
    result = pd.merge(regions, departments, on='code_reg')

    # reorder column
    result = result[['code_reg','name_reg','code_dep','name_dep']]

    return pd.DataFrame({})


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    # merge the dataframe
    result = pd.merge(referendum, regions_and_departments, on='code_dep')

    # drop the unwanted rows
    result = result[~result.DOM_TOM_COM]
    result = result[~result.French_abroad]

    # drop unwanted columns
    result = result.drop(columns=['DOM_TOM_COM','French_abroad'])

    return result


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    # group by code_reg
    result = referendum_and_areas.groupby(['code_reg', 'name_reg']).sum()
    result.reset_index(inplace=True)
    result.set_index('code_reg', inplace=True)

    return result


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    # Load the geographic data
    regions = gpd.read_file('regions.geojson')
    
    # Merging the two DataFrames
    result = pd.merge(regions,referendum_result_by_regions, left_on = 'name_reg',right_on='name_reg')
    
    # adding ratio column
    result['ratio'] = result['Choice A'] / (result['Choice A'] + result['Choice B'] + result['Abstentions'] + result['Null'])

    return result


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
