# This script is for determining when each conus lake is in the ice mask
# Authors: Natalie Von Tress and Hannah Ferriby
# Date Created: 05/16/2022

# Set up workspace ----

# Clear environment
rm(list = ls(all = T))

# Load packages
library(tidyverse)
library(lubridate)
library(sf)
library(future)
library(future.apply)
library(parallel)

t_init = Sys.time()

# Set working directory
# wd <- '/work/HAB4CAST/data_processing/'
# setwd(wd)

# Read in datasets ----

# Lakes
conus_lakes <- read_sf('data/OLCI_resolvable_lakes_2022_09_08/OLCI_resolvable_lakes_2022_09_08.shp') # %>% st_buffer(dist = -300)

head(conus_lakes)

# Week assignments 
week_assignments <- read_csv('data/week_assignments.csv')

head(week_assignments)

# Ice masks
## Directory location 
ice_dir <- 'OLCI_preprocessing/output_shapefiles/'

## List files
ice_mask_files <- list.files(ice_dir,recursive = T)

## Remove megan files and keep only files with .shp file type
ice_mask_files <- (ice_mask_files[str_which(ice_mask_files,pattern = '^2[:graph:]*shp$')])

head(ice_mask_files)

# Create tibble ----

make_mask_tibble <- function(ice_mask_file) {
  mask <- read_sf(str_c(ice_dir,ice_mask_file)) %>% st_transform(st_crs(conus_lakes))
  
  st_intersects(conus_lakes,mask,sparse = F) %>% cbind(conus_lakes) %>% rename(masked = ".") %>% 
    dplyr::select(COMID, masked) %>% mutate(file = ice_mask_file) %>% as_tibble %>% return()
}

plan(multisession,
     workers = (detectCores() - 1))

mask_tibble <- future_lapply(ice_mask_files,make_mask_tibble) %>% bind_rows() %>% arrange(COMID,file)

plan(sequential)

mask_tibble %>%
  mutate(
    jday = str_extract(file,'[:digit:]{7}'),
    date = as.Date(jday, format = '%Y%j')
  ) %>%
  left_join(week_assignments) %>%
  dplyr::select(COMID, masked, week, year) -> mask_tibble

summary(mask_tibble)
head(mask_tibble)
tail(mask_tibble)

write_csv(mask_tibble,'data/weekly_ice_tibble.csv')
