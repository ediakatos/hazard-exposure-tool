# hazard-exposure-tool

Disaster risk assessment is crucial for effective preparedness and response.


### Setup

clone repository

```bash
git clone git@github.com:mapaction/hazard-visualisation-tool.git
```

## install dependencies

```bash
cd hazard-visualisation-tool
poetry install --no-root
```

## to run backend
```bash
flask --app app run
```

### Data

##### Flood

Sources used:

The map depicts flood prone areas at global scale for flood events with 100-year return period. Resolution is 30 arcseconds (approx. 1km). Cell values indicate water depth (in m). The map can be used to assess flood exposure and risk of population and assets. NOTE: this dataset is based on JRC elaborations and is not an official flood hazard map (for details and limitations please refer to related publications).

[Flood hazard map of the World - 100-year return period](https://data.jrc.ec.europa.eu/dataset/jrc-floods-floodmapgl_rp100y-tif#dataaccess)

##### Lebanon

[Lebanon - Population Counts](https://data.humdata.org/dataset/worldpop-population-counts-for-lebanon)

https://data.humdata.org/dataset/cod-ab-lbn


##### HDX API

:book: [Docs](https://hdx-hapi.readthedocs.io/en/latest/)

:book: [API](https://hapi.humdata.org/docs#/Utility/get_encoded_identifier_api_v1_encode_identifier_get)

:gear: [HXLStandard/libhxl-python](https://github.com/HXLStandard/libhxl-python)

:package: [libhxl](https://pypi.org/project/libhxl/)
