import pandas as pd
import numpy as np
import rioxarray as rio
import xarray as xr

POPULATION_RASTER_PATH = './pop_data/sadc_pop_1km.tif'

HAZARD_RASTER_PATH = dict()
HAZARD_RASTER_PATH['flood'] = './hazard_data/flood/sadc_flood.tif' 
HAZARD_RASTER_PATH['earthquake'] = './hazard_data/earthquake/sadc_earthquake.tif' 
HAZARD_RASTER_PATH['landslide'] = './hazard_data/landslide/sadc_landslide.tif' 

HAZARD_PREP_PATH = dict()
HAZARD_PREP_PATH['flood'] = './prep_data/sadc_flood_prep.tif' 
HAZARD_PREP_PATH['earthquake'] = './prep_data/sadc_earthquake_prep.tif' 
HAZARD_PREP_PATH['landslide'] = './prep_data/sadc_landslide_prep.tif' 

HAZARD_THRESHOLD = dict()
HAZARD_THRESHOLD['flood'] = 0.0
#0.115g => acceleration corresponding to a strong perceived shaking (level VI in the Modified Mercalli intensity scale)
HAZARD_THRESHOLD['earthquake'] = 0.115 
#x = 3 => medium risk / x = 4 => high risk
HAZARD_THRESHOLD['landslide'] = 2.5


def compute_hazard_mask(hazard_raster: xr.core.dataarray.DataArray, 
    population_raster: xr.core.dataarray.DataArray, 
    hazard_threshold: float) -> xr.core.dataarray.DataArray:
    """
    Transform hazard raster into a hazard mask raster following the population grid (1 - exposed / 0 - not exposed)

    Args:
        hazard_raster (DataArray): Hazard raster
        population_raster (DataArray): Population raster
        hazard_threshold (float): Threshold to be used with the hazard raster to define exposed grid points

    Returns:
        DataArray: A raster following the population grid with a binary value of 1 when exposed to hazard following 
        the threshold and 0 otherwise
    """

    hazard_raster = hazard_raster.rio.reproject_match(population_raster)

    hazard_data = hazard_raster[0].values
    hazard_data = np.nan_to_num(hazard_data)
    hazard_data[hazard_data <= hazard_threshold] = 0
    hazard_data[hazard_data > hazard_threshold] = 1
    
    hazard_mask_raster = hazard_raster
    hazard_mask_raster.values = [hazard_data]    

    return(hazard_mask_raster)



def compute_population_exposure(hazard_mask_raster: xr.core.dataarray.DataArray, 
    population_raster: xr.core.dataarray.DataArray) -> xr.core.dataarray.DataArray:
    """
    Combine population and hazard mask rasters to compute exposed population raster. The value is the same as population
    if the grid is exposed and 0 otherwise

    Args:
        hazard_mask_raster (DataArray): Hazard binary mask raster 
        population_raster (DataArray): Population raster

    Returns:
        DataArray: A raster following the population grid with a value equal to the population
        if the grid is exposed and 0 otherwise
    """

    pop_hazard_array = np.multiply(population_raster[0].values,hazard_mask_raster[0].values)
    pop_exp_raster = hazard_mask_raster
    pop_exp_raster.values = [pop_hazard_array]
    pop_exp_raster = pop_exp_raster.rio.write_crs("epsg:4326")

    return(pop_exp_raster)

def main()-> None:
    """
    Main function to prepare hazard mask for each hazard type
    """

    for hazard in ['flood','earthquake','landslide']:

        hazard_raster = xr.open_dataarray(HAZARD_RASTER_PATH[hazard])
        population_raster = xr.open_dataarray(POPULATION_RASTER_PATH)

        hazard_mask_raster = compute_hazard_mask(hazard_raster, population_raster, HAZARD_THRESHOLD[hazard])
        population_exposure_raster = compute_population_exposure(hazard_mask_raster, population_raster)

        population_exposure_raster.rio.to_raster(HAZARD_PREP_PATH[hazard]) 

        print(hazard+' hazard prep completed')
    
    return("Hazard mask preparation complete!")

# if __name__ == "__main__":
#     main()


