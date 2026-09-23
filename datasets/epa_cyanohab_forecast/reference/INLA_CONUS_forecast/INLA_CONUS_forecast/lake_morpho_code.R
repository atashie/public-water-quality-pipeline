#Calculating lake morphology data from the lakemorpho package

#Written by Hannah Ferriby & Jeff Hollister
#Date updated 9/7/2022

# wd <- "/work/HAB4CAST/data_processing/data"
# setwd(wd)

# Load libraries ----
library(tidyverse)
library(sf)
library(lakemorpho)
library(elevatr)

# Read in data ----
#all_data_conus <- read_csv("lake_morpho_conus_allvariables.csv")
conus_lakes <- st_read("data/OLCI_resolvable_lakes_2022_09_08/OLCI_resolvable_lakes_2022_09_08.shp")

# Create lake morpho df ----
lake_morpho <- data.frame()
for(i in 1:nrow(conus_lakes)){
  
  print(i); print(conus_lakes$COMID[i])
  
  lake_m_topo <- lakeSurroundTopo(
    inLake = sf::as_Spatial(conus_lakes[i,]),
    reso = 100
  )
  
  elev <- get_elev_raster(
    lake_m_topo$surround,
    z = 10, #https://github.com/tilezen/joerd/blob/master/docs/data-sources.md#what-is-the-ground-resolution
    prj = NULL,
    src = "aws",
    verbose = T,
    neg_to_na = T,
    clip = "locations"
  )
  
  lake_m_topo <- lakeSurroundTopo(
    inLake = sf::as_Spatial(conus_lakes[i,]),
    inElev = elev
  )
  
  lake_shoreline <- lakeShorelineLength(lake_m_topo)
  lake_sa <- lakeSurfaceArea(lake_m_topo)
  lake_max_depth <- lakeMaxDepth(lake_m_topo)
  lake_mean_depth <- lakeMeanDepth(lake_m_topo, zmax = lake_max_depth)
  lake_morpho <- rbind(lake_morpho, data.frame(COMID = conus_lakes[i,]$COMID,
                                               lake_shoreline,
                                               lake_sa,
                                               lake_max_depth,
                                               lake_mean_depth))
}

summary(lake_morpho)

## Additional Lake Morpho processing -- added by Natalie Reynolds on 5/31/2023 ----
hydro_lakes <- read_sf('data/HydroLAKES_polys_v10_shp/HydroLAKES_polys_v10_shp/HydroLAKES_polys_v10.shp') %>% st_transform(st_crs(conus_lakes)) %>% filter(Country == 'United States of America') 

summary(hydro_lakes)

hydro_lakes %>% st_intersects(conus_lakes, sparse = T) -> intersects

# Add COMID
hydro_lakes %>% mutate(COMID = NA) -> hydro_lakes 

for(i in 1:nrow(hydro_lakes)){
  hydro_lakes$COMID[i] <- ifelse(identical(intersects[[i]], integer(0)),NA,conus_lakes$COMID[intersects[[i]]])
}

hydro_lakes %>% filter(!is.na(COMID)) %>% as_tibble() %>% dplyr::select(-geometry) -> hydro_lakes_data

# lake_morpho %>% filter(lake_mean_depth == 0) %>% pull(COMID) -> comid_sub
# 
# hydro_lakes_data %>% filter(COMID %in% comid_sub) %>% group_by(COMID) %>% count() %>% filter(n > 1) -> comid_sub_2
# 
# hydro_lakes %>% filter(COMID %in% comid_sub_2$COMID) %>% View()

hydro_lakes_data %>% group_by(COMID) %>% summarize(total_area = sum(Lake_area)) %>% ungroup() %>% left_join(hydro_lakes_data) %>% 
  mutate(area_fraction = Lake_area/total_area,
         weighted_depth = area_fraction*Depth_avg) %>%
  group_by(COMID) %>% summarize(weighted_depth_avg = sum(weighted_depth)) -> depths

lake_morpho %>% rename(depth_original = lake_mean_depth) %>% mutate(lake_mean_depth = NA) -> lake_morpho

for(i in 1:nrow(lake_morpho)) {
  if(lake_morpho$depth_original[i] > 0) {
    lake_morpho$lake_mean_depth[i] <- lake_morpho$depth_original[i]
  } else if(lake_morpho$depth_original[i] == 0 & lake_morpho$COMID[i] %in% depths$COMID) {
    lake_morpho$lake_mean_depth[i] <- filter(depths, COMID == lake_morpho$COMID[i])$weighted_depth_avg
  } else {lake_morpho$lake_mean_depth[i] <- NA}
}

# Save lake morpho csv ----
#lake_morpho <- lake_morpho %>% rename("COMID" = "comid")
write_csv(lake_morpho, "data/conus_lake_morpho.csv")

# Save workspace
save.image("~/cyano_forecast/data/lake_morpho_workspace.RData")
