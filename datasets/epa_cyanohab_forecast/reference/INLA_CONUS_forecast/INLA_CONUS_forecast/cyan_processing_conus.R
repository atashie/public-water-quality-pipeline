# This script is for scaling and extracting CI data
# Authors: Natalie Von Tress and Hannah Ferriby
# Date Created: 05/16/2022

# Set up workspace ----

# Clear environment
rm(list = ls(all = T))

library(tidyverse)
library(lubridate)
library(exactextractr)
library(sf)
library(terra)
library(future)
library(future.apply)
library(parallel)

t_init = Sys.time()


temp_dir <- './temp_files'
temp_create <- ifelse(!dir.exists(temp_dir),
                      dir.create(file.path(temp_dir),recursive = T),
                      F)
terraOptions(tempdir = temp_dir)

# Read in data ----

week_assignments <- read_csv('data/week_assignments.csv')

conus_lakes <- read_sf('data/OLCI_resolvable_lakes_2022_09_08/OLCI_resolvable_lakes_2022_09_08.shp')

files <- list.files(path = 'OLCI_preprocessing/output_masked_tif', full.names = TRUE, recursive = T)
# files <- files[str_which(files,"megan",negate = T)] # overwrite to exclude megan's files
# head(files);tail(files)

# CI_20221772022183_out.tif
tifNames <- files %>% str_extract('CI_[:digit:]{14}_out')
# head(tifNames);tail(tifNames)

# ci_brick <- rast(x = files) # REMOVE SUBSET ONCE CODE IS WORKING
# 
# mem_info(ci_brick)
# 
# ci_brick

# Check for pre-existing mean_cyan_conus and subset files and tifnames accordingly
if(file.exists('data/mean_cyan_conus.csv')){
  # Read in existing data
  mean_cyan_preexisting <- read_csv('data/mean_cyan_conus.csv')

  # Subset for images that have yet to be processed
  processed_scene_names <- mean_cyan_preexisting$scene_name
  unprocessed_sub <- (tifNames %in% processed_scene_names) == F

  files <- files[unprocessed_sub]
  tifNames <- tifNames[unprocessed_sub]


  if(length(files) == 0) {
    stopifnot(length(files) == 0)
  } #else {
  #   ci_brick <- ci_brick[[unprocessed_sub]]
  # }
}


if(length(files) == 0) {

  # Stop the code if there's nothing new to process ----

  ot <- Sys.time() - t_init
  print(ot)
  cat("No new images to process -- exiting the script")
  stopifnot(length(files) == 0)

} else {
  
  # Run the code if there are unprocessed images ----
 
  
  
  # crs(vect(conus_lakes))
  # crs(ci_brick)
  
  # ci_brick <- ci_brick %>% project(crs(vect(conus_lakes))) 
  
  
  # Write a function to calculate multiple metrics at once ----
  metrics <- function(x) {
    c(mean = mean(x,na.rm = T),
      median = median(x,na.rm = T),
      st_dev = sd(x, na.rm = T))
  }
  
  conus_lakes <- st_transform(conus_lakes,crs(rast(x = files[1])))
  
  make_extracted_tibble <- function(conus_lake) {
    
    ci_brick <- rast(x = files) # REMOVE SUBSET ONCE CODE IS WORKING
    
    conus_lakes %>% filter(COMID == conus_lake) -> lake
    
    exact_extract(ci_brick,lake)[[1]] %>%
      filter(coverage_fraction == 1) %>%
      dplyr::select(-coverage_fraction) %>%
      apply(MARGIN = 2,FUN = metrics) %>% t() %>%
      as_tibble(rownames = 'scene_name') %>%
      mutate(COMID = conus_lake) %>%
      return()
  }
  
  plan(multisession, workers = (detectCores() - 1))
  
  extracted_tibble <- future_lapply(conus_lakes$COMID,make_extracted_tibble) %>% bind_rows()
  
  plan(sequential)
  
  cat(str_c('\nFinished extracting values!'))
  
  
  summary(extracted_tibble)
  
  extracted_tibble
  
  # Pull dates from filenames ----
  dates <- rep(NA, length(tifNames))
  # dates_weekly_end <- rep(NA, length(tifNames))
  
  for(i in 1:length(tifNames)){
    # i <- 1
    dates[i] <- str_extract(tifNames[i],'[:digit:]{7}') %>% as.Date(format = '%Y%j')
    
    # dates_weekly_start[i] <- str_extract(dates,'^[:digit:]{7}') %>% as.Date(format = '%Y%j')
    
    # dates_weekly_end[i] <- str_extract(dates,'[:digit:]{7}$') %>% as.Date(format = '%Y%j')
  }
  
  dates <- as_date(dates)
  # dates_weekly_end <- as_date(dates_weekly_end)
  
  length(dates); head(dates); tail(dates)
  
  names_to_dates <- tibble(
    scene_name = tifNames,
    date = dates
  )
  
  
  # Extract data ----
 
  
  # Reshape
  extracted_tibble %>%
    # Pull image dates from layer names and create a year column
    left_join(names_to_dates) %>%
    # Assign weeks
    inner_join(week_assignments) %>%
    # Group data by COMID, week, and year
    group_by(COMID,year,week) %>%
    # Compute average value
    summarise(COMID = COMID,
              year = year,
              week = week,
              scene_name = scene_name,
              mean = mean,
              median = median,
              st_dev = st_dev,
              bloom = ifelse(median>=130,T,F)) %>% # 97 for 3 ug/L, 130 for 12 ug/L, 151 for 24 ug/L - subbing u for mu, so ug = micrograms
    distinct() -> mean_cyan
  
  if(exists('mean_cyan_preexisting') == T) {
    mean_cyan <- rbind(mean_cyan_preexisting,mean_cyan) %>% arrange(COMID,year,week)
  }
  
  print(mean_cyan)
  
  write_csv(mean_cyan,file = 'data/mean_cyan_conus.csv')
  
  cat('Wrote mean_cyan_conus.csv\n')
  ot <- Sys.time() - t_init
  print(ot)
}

# Delete terra temp files
unlink(temp_dir, recursive = TRUE, force = TRUE)

