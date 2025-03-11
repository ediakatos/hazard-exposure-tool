# Hazard Processing Tool

This tool processes hazard-related data and outputs processed results in csv format for further visualisation. It is part of the hazard exposure workflow.

## Project Structure

The directory is organised as follows:

- **admin_data**  
  Contains administrative geographic data (GeoJSON files). These files serve as reference data for processing.

- **hazard_data**  
  Contains raw hazard data from various hazards:
  - **coastal_erosion**: Shapefile data.
  - **cyclone**: TIFF images.
  - **deforestation**: TIFF images.
  - **earthquake**: TIFF images.
  - **flood**: TIFF images.
  - **landslide**: TIFF images.

- **pop_data**  
  Contains raw population data (TIFF format).

- **prep_data**  
  Contains prepared data files that are used as input for processing.  
  **Note:** Before running the pipeline, create this directory if it doesn't exist.

- **output_data**  
  Contains processed CSV outputs for each hazard type.  
  **Note:** Before running the pipeline, create this directory if it doesn't exist.

- **src**  
  Contains the Python source code:
  - `compute_hazard.py` and `prepare_hazard_mask.py` are the main scripts.
  - **utils/**: Helper modules for data processing.

- **Makefile**, **pyproject.toml**, **poetry.toml**, and **poetry.lock**  
  Files for managing dependencies and running pipeline commands.

## Getting Started

1. **Install Dependencies**

   This project uses [Poetry](https://python-poetry.org/) for dependency management.  
   Run:
   ```sh
   poetry install
   ```

2. **Prepare Directories**

   Before running the processing pipeline, ensure that the following directories exist:
   - `prep_data`
   - `output_data`
   
   If they do not exist, create them by running:
   ```sh
   mkdir -p prep_data output_data
   ```

3. **Raw Data**

   The raw data is supplied from:
   - `admin_data`
   - `hazard_data`
   - `pop_data`

   Ensure that these directories contain the expected data files as shown in the project structure.

4. **Run the Pipeline**

   Use the provided Makefile to run the processing pipeline. For example, you might run:
   ```sh
   make pipeline
   ```

   This command processes the input files from `admin_data`, `hazard_data`, and `pop_data` and generates outputs in `output_data` (and intermediate files in `prep_data`).

## Contributing

Feel free to open issues or submit pull requests if you encounter any problems or have suggestions for improvements.

## License

This project is distributed under the terms of the [LICENSE](LICENSE) file.