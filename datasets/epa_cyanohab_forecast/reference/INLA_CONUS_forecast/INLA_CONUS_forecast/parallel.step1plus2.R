#### Script created by Erin A. Urquhart 11/20/2019
### script to read in weekly conus images, mask to just CONUS, then mask to just resolvable MERIS polygons
### Parallelized  latest update: 07/07/2020 (by Yadong Xu)
### Adapted to cyano_forecast by Hannah Ferriby and Natalie Reynolds (December 2022 and May 2023)

this_year = 2022
num.cores = as.numeric(Sys.getenv("SLURM_NTASKS"))
t_init = Sys.time()
c_1 = "L"

require(raster)
require(rgdal)
require(parallel)

rasterOptions(maxmemory = 1e+09)


### Extend raster class to add week or lake SeqNum for out-of-order parallel computation
RasterLayerNum <- setClass('RasterLayerNum',contains = 'RasterLayer', slots = c(seqnum = 'integer'))

### Functions formerly loops, invoked by mclapply

# mosaics <- mosaic.week.fxn <- function(week){
#   cat("Processing week ",week,"\n")
#   cat("Filename contains ",which_weeks[week],"\n")
#     
#   file_list<-c() #Need to define a column before using in loop
#   for(file in 1:length(fileNames)){
#     if(substring(fileNames[file],9,15)==which_weeks[week]){
#       file_list<-c(file_list,fileNames_full[file]) #Use full path to file names
#     }
#   }  
#   cat(length(file_list)," files will be used\n") #Is this always 9*6?
#     
#   rast_list <- lapply(file_list,raster) #Creates a list of rasters
#   
#   if (length(file_list)==1){
#     single<-rast_list
#     single <- RasterLayerNum(single, seqnum = week) #Add week number to object
#     rstack<-addLayer(rstack,single)
#   } else {
#     rast_list$fun<-mean  
#     rast_list$na.rm<-TRUE
#     mergeOUT<-do.call(mosaic,rast_list) #Mosaics together spatial tiles 
#     mergeOUT <- RasterLayerNum(mergeOUT, seqnum = week) #Add week number to object
#     names(mergeOUT)<-which_weeks[week]  
#     rstack<-addLayer(rstack,mergeOUT)   #Adds weekly data into a stack of all 52 weeks
#   }
# 
#   return(rstack)
#   #we can do clean up later...  rm(file_list)
# }  

mask.lake.fxn <- function(j) {
  cat(j,"of nlayers=",nlayers(lakes_mask),"\n")
  a<-lakes_mask [[j]]
  a[a==0]=0.5
  masked_test <- a * valid_pixels
  masked_test[masked_test<0]=NA
  masked_test[masked_test==0.5]=0

  g<-paste0(c_1,substr(names(lakes_mask[[j]]),2,8),sep="")
  outfile<-paste0(outdir,g,".CONUS_validpixels.tif")
  writeRaster(masked_test,filename=outfile,overwrite=TRUE)
  #print("Tiff created:",outfile,"\n")
  ot <- Sys.time() - t_init
  #print(ot)
} #end of layers loop j

#Inputs:
# In /work/CYANOHAB/RUN_DIR_FINAL/input_files
#     2 shape files, conus_boundary.shp and UpdatedLakes11_13.shp 
#     Where did these files come from?
#under the working directory ./input_OLCI 
# these files come from running "GetFiles"
# 1 tif per week, name is formatted (X and Y variable):
#     L20170012017007.L3m_7D_CYAN_CI_cyano_CYAN_CONUS_300m_X_Y.tif

#Define input data directories
input_files <- "./data/"
input_OLCI <- paste0("./OLCI_preprocessing/input_OLCI/",this_year)

#The datafiles are assumed to be in input_files
l_conus <- "conus_boundary"
l_MERIS <- "OLCI_resolvable_lakes_2022_09_08"
valid_pixels<- paste0(input_files,"invalidMixed.tif")

#Define output directories
tmp_all <- "./tmp/" 
tmp_dir <- paste0("./tmp/",this_year,"/")    #R write large temporary files when doing raster calculations
outdir_all <- "./OLCI_preprocessing/output_CONUS_masked/" #Files generated from this script for all years will be here
outdir <- paste0("./OLCI_preprocessing/output_CONUS_masked/",this_year,"/") #Files generated from this script will be here

#Exit if input directories don't exist
if (!file.exists(input_files)) stop("Cannot find the main DATA directory for inputs and shapefiles.  Exiting.\n")
if (!file.exists(input_OLCI)) stop("Cannot find the OLCI directory for tiff inputs.  Exiting.\n")

# #Check for all existing shapefiles and datafiles
# list_layers<- lapply(list.files(input_files,recursive = T,full.names = T),ogrListLayers())
# #Exit if nessessary files don't exist
# if(! (l_conus %in% list_layers)) stop("The shapefile ", l_conus," does not exist in ",input_files,"\n")
# if(! (l_MERIS %in% list_layers)) stop("The shapefile ",l_MERIS," does not exist in ",input_files,"\n")
# #if (!file.exists(valid_pixels)) stop("The file ",valid_pixels," does not exist.\n")


#Create output directories if they don't exist

if(!file.exists(tmp_all)){
  warning("Creating directory for all years temporary files in ",tmp_all,"\n")
  dir.create(tmp_all)
}

if(!file.exists(tmp_dir)){
  warning("Creating directory for temporary files in ",tmp_dir,"\n")
  dir.create(tmp_dir)
}

if(!file.exists(outdir_all)){
    warning("Creating directory for all years output files in ",outdir_all,"\n")
    dir.create(outdir_all)
}

if(!file.exists(outdir)){
  warning("Creating directory for output files in ",outdir,"\n")
  dir.create(outdir)
}

rasterOptions(tmpdir=tmp_dir)

############### read in spatial polygon and shape files needed for state and TILE cropping ############

#L3 readOGR is from the package rgdal, Read OGR vector maps into Spatial objects
##conus_low <-readOGR(input_files,layer=l_conus)      #L3 (directory,layer name) is the way of calling readOGR for a shape file 
##conus <- spTransform(conus_low, CRS=CRS("+init=epsg:5070")) #same as original conus
conus<-readOGR(paste0(input_files,l_conus),layer=l_conus)      #L3 (directory,layer name) is the way of calling readOGR for a shape file 
lakes<-readOGR(paste0(input_files,l_MERIS),layer=l_MERIS)

###### read in .tif files #########

valid_pixels <- raster(valid_pixels)

#Assumes we already checked these files
### FOR ENTIRE CONUS
# create raster list with raw tifs for each time step

#"L" for 2017:  reg_ex <- paste0("L",YYYY,"*.tif")  #Just take the files for the current year
#c_1=L for OLCI and c_1=M for MERIS
reg_ex <- paste0("*.tif")
fileNames<-c(list.files(input_OLCI,pattern=glob2rx(reg_ex),full.names=FALSE,recursive=FALSE))     #This just has file names (full.names=FALSE)
fileNames_full<-c(list.files(input_OLCI,pattern=glob2rx(reg_ex),full.names=TRUE,recursive=FALSE)) #This also has path to files (full.names=TRUE)

#Find number of weeks- we should have already warned them if there are less than 52 weeks
#megan# week_string1 <- as.Date(paste0(substring(fileNames,14,17), substring(fileNames,19,22)),"%Y%m%d") #YYddd (2 digit year, and ending day out of 365...data is weekly)
#megan# week_string <- paste0(substring(fileNames,14,17),strftime(week_string1, format = "%j"))
week_string <- substring(fileNames,9,15)
which_weeks<-unique(week_string)        
n_weeks<-length(which_weeks)            

#rstack <- stack()  #Initializing rstack as a stack before using in loop

### loop through weekly tif files and MOSAIC all tiles together to form one CONUS weekly tif
#mosaics <- mclapply(1:n_weeks, mosaic.week.fxn, mc.cores = num.cores)

#mosaic_tiles <- stack(mosaics)

mosaic_tiles<-stack(fileNames_full)
names(mosaic_tiles) <- week_string

cat(names(mosaic_tiles))
ot <- Sys.time() - t_init
cat("Completed mosaic. ", ot, "\n")

#L3 Writing for debugging only
#cat("Description of mosaic_tiles\n")
#cat(str(mosaic_tiles, max.level=8),"\n")
#mclapply(1:nlayers(mosaic_tiles),
#	function(d){ writeRaster(mosaic_tiles[[d]],
#	filename=paste0("./DEBUG/debug.",d,".mosaic_tiles.tif"),
#	format="GTiff",overwrite=TRUE)
#	}, mc.cores = num.cores)

################################################################################################
### reproject and change extent to CONUS
#crop_to_conus <-crop(mosaic_tiles,extent(conus)) #Crop the files according to the conus boundary
crops <- mclapply(1:nlayers(mosaic_tiles),
                  crops <- function(week){
                    cropped <- crop(mosaic_tiles[[week]],extent(conus))
                    return(cropped)
                    }, mc.cores = num.cores)

crop_to_conus <- stack(crops)

cat(names(crop_to_conus))
ot <- Sys.time() - t_init
cat("Completed Crop. ", ot, "\n")

#L3 Writing for debugging only
#cat("Description of crop_to_conus\n")
#cat(str(crop_to_conus, max.level=8),"\n")
#mclapply(1:nlayers(crop_to_conus),
#	function(d){ writeRaster(crop_to_conus[[d]],
#	filename=paste0("./DEBUG/debug.",d,".crop_to_conus.tif"),
#	format="GTiff",overwrite=TRUE)
#	}, mc.cores = num.cores)

###### mask satellite imagery with CONUS boundary shapefile 
### write out raster brick for each year
l<-spTransform(conus,crs(mosaic_tiles))
mask_crop_to_conus<-mask(crop_to_conus,l)
cat(names(mask_crop_to_conus))

ot <- Sys.time() - t_init
cat("Completed Mask. ", ot, "\n")

#L3 Writing for debugging only
#cat("Description of mask_crop_to_conus\n")
#cat(str(mask_crop_to_conus, max.level=8),"\n")
#mclapply(1:nlayers(mask_crop_to_conus),
#	function(d){ writeRaster(mask_crop_to_conus[[d]],
#	filename=paste0("./DEBUG/debug.",d,".mask_crop_to_conus.tif"),
#	format="GTiff",overwrite=TRUE)
#	}, mc.cores = num.cores)

### mask land and only preserve lake polygons ~1865 lakes
SPtrans_lakes <- spTransform(lakes,crs(mask_crop_to_conus))
ot <- Sys.time() - t_init
cat("Transformed Polygons. ", ot, "\n")

#L3 Writing for debugging only
#cat("Description of SPtrans_lakess\n")
#cat(str(SPtrans_lakes, max.level=8),"\n")
#for(d in 1:nlayers(SPtrans_lakes)){
#  writeOGR(SPtrans_lakes,layer="SPtrans_lakes",dsn="./DEBUG",driver="ESRI Shapefile",overwrite=TRUE)
#}

lakes_mask <- mask(mask_crop_to_conus,SPtrans_lakes)

ot <- Sys.time() - t_init
cat("Completed Lakes Mask. ", ot, "\n")

###### REMOVE mixed land-water edge pixels and invalid pixels from polygons
mclapply(1:nlayers(lakes_mask), mask.lake.fxn, mc.cores = num.cores)


cat("end year",this_year,"\n") 
ot <- Sys.time() - t_init
cat(ot)

#Print out disk usage:
#cat("Disk usage, all:\n")
#system2("du",c("."))
#cat("Disk usage, tmp before delete:\n")
#system2("du",c("tmp"))

#Delete the temp directory
unlink(tmp_dir,recursive=TRUE,force=TRUE)

cat("End of script\n")
ot <- Sys.time() - t_init
cat(ot)
