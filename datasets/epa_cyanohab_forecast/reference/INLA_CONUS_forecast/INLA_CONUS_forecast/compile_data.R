# This code is to join the PRISM, CyAN, and lake morphology data
# Author: Natalie Von Tress
# Date created: 6/3/22

# Clear workspace
rm(list = ls())

# Load libraries
library(tidyverse)
library(lubridate)
library(sf)

# Set working directory
# wd <- '/work/HAB4CAST/data_processing/'
# wd <- '~/cyan_forecasting/cyano_forecast'
# setwd(wd)

# Read in data ----
# Need: Lake morphology, ARD, PRISM, and CyAN processed outputs

week_assignments <- read_csv('data/week_assignments.csv')

# crs(rast('data/OLCI_preprocessing/output_masked_tif/2016/CI_20161222016128_out.tif')) == crs(vect(ard_tiles))
# 
# crs(rast('data/conus_ard_data/LC08_CU_001006_20211216_20211226_02_QA_PIXEL.TIF')) == crs(rast('data/OLCI_preprocessing/output_masked_tif/2016/CI_20161222016128_out.tif'))
# 
# crs(vect(st_read('data/CONUS_C2_ARD_grid/conus_c2_ard_grid.shp'))) == crs(rast('data/conus_ard_data/LC08_CU_001006_20211216_20211226_02_QA_PIXEL.TIF'))

conus_lakes <- read_sf('data/OLCI_resolvable_lakes_2022_09_08/OLCI_resolvable_lakes_2022_09_08.shp') %>% mutate(COMID = as.numeric(COMID))
conus_lake_morpho <- read_csv('data/conus_lake_morpho.csv') #%>% 
  # rename(COMID = comid)
mean_cyan <- read_csv('data/mean_cyan_conus.csv') %>% arrange(COMID,year,week)  # NOTE - we're actually using the median, not the mean. Both are recorded in the csv.
mean_prism <- read_csv('data/mean_prism_conus.csv') %>% arrange(COMID,year,week) 
mean_wtemp <- read_csv('data/rf_pred_temp_2016_2022_for_inla.csv') %>% 
  left_join(week_assignments) %>%
  mutate(t = rf_temp + 273.15) %>%
  group_by(COMID,year,week) %>%
  summarise(COMID = COMID,
            year = year,
            week = week,
            mean_wtemp_k = mean(t,na.rm = T)) %>%
  # Drop repeated rows
  distinct() %>%
  arrange(COMID,year,week) 

# Process data and join ----
# Columns needed: COMID, Time (YYYYWW), Cyano (cell density), Atemp (deg_c), Wtemp (deg_c -- currently K), Precip (in), area (m2), dMean (m), dMax (m), Year, Week, LONG, LAT, Bloom (logical)

# Tidy lake morpho data
conus_lakes %>% 
  mutate(centroid = st_centroid(geometry),
         LONG = st_coordinates(centroid)[,1],
         LAT = st_coordinates(centroid)[,2]) %>%
  inner_join(conus_lake_morpho, by = 'COMID') %>% 
  dplyr::select(COMID,lake_sa,lake_max_depth,lake_mean_depth,LONG,LAT) %>%
  rename(dMean = lake_mean_depth,
         dMax = lake_max_depth,
         Area = lake_sa) -> lakes_data


# Handle cyan data - replace NA blooms with 0 if ice cover
weekly_ice_tibble <- read_csv('data/weekly_ice_tibble.csv')
mean_cyan_ice <- mean_cyan %>% left_join(weekly_ice_tibble) %>% mutate(bloom = ifelse(is.na(bloom) & masked == T, F, bloom))


# mean_prism start 2016 01 end 2022 31
# mean_wtemp start 2016 01 end 2022 17 -- dated info now that it's from the RF model
# mean_cyan start 2016 18 end 2022 28

mean_prism %>% full_join(mean_wtemp) %>% full_join(mean_cyan_ice) %>% full_join(lakes_data) -> joined_data # need to right join lake to avoid a row of NAs 

joined_data %>% 
  rename(Year = year,
         Week = week,
         Cyano = median,
         Bloom = bloom,
         Atemp = mean_atemp,
         Wtemp = mean_wtemp_k,
         Precip = mean_precip) %>%
  mutate(Time = as.numeric(str_c(as.character(Year),
                      ifelse(nchar(Week) == 2, as.character(Week), str_c('0',as.character(Week))))),
         Wtemp = Wtemp - 273.15) %>% 
  dplyr::select(COMID,Time,Cyano,Atemp,Wtemp,Precip,Area,dMean,dMax,Year,Week,LONG,LAT,Bloom) -> compiled_data

write_csv(compiled_data,'data/compiled_data.csv')

## Examine w temp data


summary(compiled_data)

