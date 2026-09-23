# cyano_forecast
Updated INLA cyanobacteria forecast repository. 

This repository contains all code used in the INLA cyanobacteria study. It does not, however, include inpute files due to file size limitations. All input files are publicallly available for free download.  

Code and general workflow:  
1. Week assignments  
  a. generate_week_assignments_tibble.R  
    - Purpose: Generates a csv of dates in our study period with the week of the year it falls on. This was done to correspond with the CyAN data week numbers, wherein the first week of each year begins on the first Sunday of each year and counts until the first Sunday of the following year.  
    - Sbatch file: generate_week_assignments.sbatch  
2. Lake morphology  
  a. lake_morpho_code.R  
    - Purpose: Calculates lake morphology data for INLA model  
    - Sbatch file: lake_morpho.sbatch  
    - __NOTE__: While I configured this code so it _could_ run on atmos, it consistently fails on a different lake each time. Therefore, this code needs to be run on a local machine.  
3. CyAN data  
  a. parallel.step1plus2.R  
     - Purpose: Crops OLCI cyan images to conus boundary and masks out values that aren't resolvable lakes. Residual code exists in the file to mosaic individual cyan tiles, but this isn't necessary anymore. I've also recoded it so that the code is in the main working directory, OLCI_preprocessing-specific files remain in the OLCI_preprocessing subdirectory, and more generalized files are in the data directory. This helps prevent mix-ups with the resolvable lakes shapefile, etc.   
     - Sbatch file: step2plus2.sbatch  
     
     b. cyanoCONUS_ice_step3_adjusted.R  
     - Purpose: Creates weekly ice masks as tifs and shapefiles and fills any holes within the mask. Also crops the mask to the CONUS boundary. As a side note, I don't think all the inputs are actually used in the code. h
     - Sbatch file: step3_adjusted.sbatch  
     
     c. cyanoCONUS_ice_step4_adjusted.R  
      - Purpose: Applies the ice mask (generated in step 3) to the OLCI images that were masked for mixed pixels (in step 1/2).  
      - Sbatch file: step4_adjusted.sbatch  
      
      d. cyan_processing_conus.R   
      - Purpose: Calculates the mean, median, and standard deviation of cyan values for each week and each lake in our dataset.  
      - Sbatch file: cyan_processing.sbatch  
        
4. Ice data  
  a. generate_ice_tibble.R  
    - Purpose: Generates a csv file detailing which lakes overlapped with the ice mask for our entire study period. This is later used in compile_data.R to replace missing bloom values with "no bloom," which creates a more balanced dataset for training the INLA model, especially in winter months.  
    - Sbatch file: generate_ice_tibble.sbatch  
5. PRISM data  
  a. prism_download.R  
    - Purpose: Automatically downloads daily PRISM air temperature and precipitation data for our study period.
    - Sbatch file: prism_download.sbatch  
    
    b. prism_processing_conus.R  
    - Purpose: Calculates weekly mean air temp and precipitation for each lake for the duration of our study period.  
    - Sbatch file: prism_download.sbatch  
    
6. Water temp data  
  a. See https://github.com/bschaeff/SW_Model; this repository is used to generate __rf_pred_temp_2016_2022_for_inla.csv__ for this analysis.  
7. Data compilation  
  a. compile_data.R  
    - Purpose: Join all datasets together for INLA model. Final column names were selected to match the column names Mark Myer used in his INLA code.  
    - Sbatch file: compile_data.sbatch  
8. INLA model  
  a. conus_inla.R
     - Purpose: Run the INLA model and generate all model outputs (figures, tables, uncertainty analysis, etc) for INLA paper.
     - Sbatch file: conus_inla.sbatch
