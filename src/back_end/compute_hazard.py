
import geopandas as gpd
import pandas as pd
import numpy as np
import rasterio
from rasterstats import zonal_stats


from src.utils.raster_aux_tools import compute_zonal_stat, compute_hazard_population_exposure

POPULATION_RASTER_PATH = './pop_data/sadc_pop_1km.tif'
ADMIN_VECTOR_PATH = './admin_data/sadc_adm1.geojson'

HAZARD_INPUT_PATH = dict()
HAZARD_INPUT_PATH['flood'] = './prep_data/sadc_flood_prep.tif' 
HAZARD_INPUT_PATH['earthquake'] = './prep_data/sadc_earthquake_prep.tif' 
HAZARD_INPUT_PATH['landslide'] = './prep_data/sadc_landslide_prep.tif' 
HAZARD_INPUT_PATH['cyclone'] = './hazard_data/cyclone/STORM_FIXED_RETURN_PERIODS_SI_100_YR_RP.tif'
HAZARD_INPUT_PATH['coastal_erosion'] = './hazard_data/coastal_erosion/sadc_coastal_erosion.shp'
HAZARD_INPUT_PATH['deforestation'] = dict()
HAZARD_INPUT_PATH['deforestation']['loss'] = './hazard_data/deforestation/sadc_lossyear.tif'
HAZARD_INPUT_PATH['deforestation']['cover'] = './hazard_data/deforestation/sadc_treecover.tif'

HAZARD_OUTPUT_PATH = dict()
HAZARD_OUTPUT_PATH['flood'] = './output_data/flood.csv'
HAZARD_OUTPUT_PATH['earthquake'] = './output_data/earthquake.csv'
HAZARD_OUTPUT_PATH['landslide'] = './output_data/landslide.csv'
HAZARD_OUTPUT_PATH['cyclone'] = './output_data/cyclone.csv'
HAZARD_OUTPUT_PATH['coastal_erosion'] = './output_data/coastal_erosion.csv'
HAZARD_OUTPUT_PATH['deforestation'] = './output_data/deforestation.csv'


def process_flood(admin_df: gpd.geodataframe.GeoDataFrame,
    pop_raster: rasterio.io.DatasetReader) -> pd.core.frame.DataFrame:
    """
    Compute Hazard level for Flood through exposed population.

    Args: 
        admin_df (GeoDataFrame): Administrative or other boundaries used for aggregation
        pop_raster (DatasetReader): Population raster

    Returns:
        DataFrame: DataFrame containing admin codes and names, total population, population exposed and ratio of exposure.
    """
    pop_exp_raster = rasterio.open(HAZARD_INPUT_PATH['flood'])
    df = compute_hazard_population_exposure(admin_df, pop_raster, pop_exp_raster)
    return(df)


def process_earthquake(admin_df: gpd.geodataframe.GeoDataFrame, 
    pop_raster: rasterio.io.DatasetReader) -> pd.core.frame.DataFrame:
    """
    Compute Hazard level for Earthquake through exposed population.

    Args: 
        admin_df (GeoDataFrame): Administrative or other boundaries used for aggregation
        pop_raster (DatasetReader): Population raster

    Returns:
        DataFrame: DataFrame containing admin codes and names, total population, population exposed and ratio of exposure.
    """
    pop_exp_raster = rasterio.open(HAZARD_INPUT_PATH['earthquake'])
    df = compute_hazard_population_exposure(admin_df, pop_raster, pop_exp_raster)
    return(df)


def process_landslide(admin_df: gpd.geodataframe.GeoDataFrame, 
    pop_raster: rasterio.io.DatasetReader) -> pd.core.frame.DataFrame:
    """
    Compute Hazard level for Landslide through exposed population.

    Args: 
        admin_df (GeoDataFrame): Administrative or other boundaries used for aggregation
        pop_raster (DatasetReader): Population raster

    Returns:
        DataFrame: DataFrame containing admin codes and names, total population, population exposed and ratio of exposure.
    """    
    pop_exp_raster = rasterio.open(HAZARD_INPUT_PATH['landslide'])
    df = compute_hazard_population_exposure(admin_df, pop_raster, pop_exp_raster)
    return(df)




def process_deforestation(admin_df: gpd.geodataframe.GeoDataFrame) -> pd.core.frame.DataFrame:
    """
    Compute Hazard level for Deforestation through ratio between treecover loss and initial treecover.

    Args: 
        admin_df (GeoDataFrame): Administrative or other boundaries used for aggregation

    Returns:
        DataFrame: DataFrame containing admin codes and names, tree cover, loss and deforestation ratio
    """
    df = admin_df.drop(columns = 'geometry').copy()
    hazard_threshold = 0

    hazard_raster = rasterio.open(HAZARD_INPUT_PATH['deforestation']['loss'])
    hazard_data = np.nan_to_num(hazard_raster.read(1))
    hazard_data[hazard_data <= hazard_threshold] = 0
    hazard_data[hazard_data > hazard_threshold] = 1
    df['loss'] = compute_zonal_stat(hazard_data, hazard_raster.transform, admin_df, agg = 'sum')

    hazard_raster = rasterio.open(HAZARD_INPUT_PATH['deforestation']['cover'])
    hazard_data = np.nan_to_num(hazard_raster.read(1))
    hazard_data[hazard_data <= hazard_threshold] = 0
    hazard_data[hazard_data > hazard_threshold] = 1
    df['cover'] = compute_zonal_stat(hazard_data, hazard_raster.transform, admin_df, agg = 'sum')

    df['deforestation'] = df['loss']/df['cover']
    
    return df


def process_cyclone(admin_df: gpd.geodataframe.GeoDataFrame) -> pd.core.frame.DataFrame:
    """
    Compute Hazard level for Cyclone through maximum speed for a fixed return period.

    Args: 
        admin_df (GeoDataFrame): Administrative or other boundaries used for aggregation

    Returns:
        DataFrame: DataFrame containing admin codes, names and maximum wind speed
    """
    

    df = admin_df.drop(columns = 'geometry').copy()

    hazard_raster = rasterio.open(HAZARD_INPUT_PATH['cyclone'])
    hazard_data = hazard_raster.read(1)  
    df['max_speed'] = compute_zonal_stat(hazard_data, hazard_raster.transform, admin_df, agg = 'max')

    return df


def process_coastal_erosion(admin_df: gpd.geodataframe.GeoDataFrame, adm_col: str) -> pd.core.frame.DataFrame:
    """
    Compute Hazard level for Coastal Erosion through mean erosion ratio over coastline

    Args: 
        admin_df (GeoDataFrame): Administrative or other boundaries used for aggregation
        adm_col (str): name of admin level column to be used for aggregation

    Returns:
        DataFrame: DataFrame containing admin codes, names and erosion rate
    """
    
    hazard_df = gpd.read_file(HAZARD_INPUT_PATH['coastal_erosion'])

    admin_df.geometry = admin_df.geometry.buffer(0.01)
    
    hazard_df = hazard_df[['rate_time','geometry']]
    merge_df = gpd.sjoin(admin_df,hazard_df)
    merge_df = merge_df.groupby([adm_col])['rate_time'].mean().reset_index()
    
    df = admin_df.merge(merge_df, on = adm_col, how = 'left')
    df = df.drop(columns = 'geometry')

    return df



def export_dataset(df: pd.core.frame.DataFrame, hazard: str):
    """
    Compute Hazard level for Coastal Erosion through mean erosion ratio over coastline

    Args: 
        df (DataFrame): DataFrame containing admin codes, names and hazard level
        hazard (str): name of the hazard being computed

    Returns:

    """

    if 'adm2_src' in  df.columns:
        df.sort_values(by = ['adm1_src', 'adm2_src'], inplace = True)

    df.to_csv(HAZARD_OUTPUT_PATH[hazard])
    print(HAZARD_OUTPUT_PATH[hazard])

    return

def run_analysis(hazard_type: str) -> pd.core.frame.DataFrame:
    """
    Run hazard analysis for a specific hazard type.
    Loads the population raster and admin boundaries, processes the hazard,
    and returns the computed DataFrame.
    """
    pop_raster = rasterio.open(POPULATION_RASTER_PATH)
    admin_df = gpd.read_file(ADMIN_VECTOR_PATH)

    adm_complete_list = ['adm0_src', 'adm0_name', 'adm1_src', 'adm1_name', 'adm2_src', 'adm2_name']
    adm_list = [col for col in adm_complete_list if col in admin_df.columns]
    adm_list.append('geometry')
    admin_df = admin_df[adm_list]

    if hazard_type == 'flood':
        df = process_flood(admin_df, pop_raster)
    elif hazard_type == 'earthquake':
        df = process_earthquake(admin_df, pop_raster)
    elif hazard_type == 'landslide':
        df = process_landslide(admin_df, pop_raster)
    elif hazard_type == 'deforestation':
        df = process_deforestation(admin_df)
    elif hazard_type == 'cyclone':
        df = process_cyclone(admin_df)
    elif hazard_type == 'coastal_erosion':
        if 'adm2_src' in admin_df.columns:
            adm_col = 'adm2_src'
        elif 'adm1_src' in admin_df.columns:
            adm_col = 'adm1_src'
        else:
            adm_col = 'adm0_src'
        df = process_coastal_erosion(admin_df, adm_col)
    else:
        raise ValueError(f"Unknown hazard type: {hazard_type}")
    
    return df

def main():

    #####################################
    pop_raster = rasterio.open(POPULATION_RASTER_PATH)
    admin_df = gpd.read_file(ADMIN_VECTOR_PATH)

    #####################################
    adm_complete_list = ['adm0_src','adm0_name','adm1_src','adm1_name','adm2_src','adm2_name']
    adm_list = []
    for adm_col in adm_complete_list:
        if adm_col in admin_df.columns:
            adm_list.append(adm_col)

    adm_list.append('geometry')
    admin_df = admin_df[adm_list]

    #####################################
    df = process_flood(admin_df, pop_raster)
    export_dataset(df, 'flood')

    #####################################
    df = process_earthquake(admin_df, pop_raster)
    export_dataset(df, 'earthquake')

    #####################################
    df = process_landslide(admin_df, pop_raster)
    export_dataset(df, 'landslide')

    #####################################
    df = process_deforestation(admin_df)
    export_dataset(df, 'deforestation')

    #####################################
    df = process_cyclone(admin_df)
    export_dataset(df, 'cyclone')

    #####################################
    if 'adm2_src' in admin_df.columns:
        adm_col = 'adm2_src'
    elif 'adm1_src' in admin_df.columns:
        adm_col = 'adm1_src'
    else:
        adm_col = 'adm0_src'

    df = process_coastal_erosion(admin_df, adm_col)
    export_dataset(df, 'coastal_erosion')



    
# if __name__ == "__main__":
#     main()