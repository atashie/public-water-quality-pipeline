## R script created by Erin Urquhart on 10/2/2017. Pulls in daily ice tif files, bins them to weekly time step. Crops to CONUS extent. 
#### Keeps only ice and snow (data=3 &/or 4), creates spatial polygon shape file,
###  fills in holes (hole_chop.R) where ice lakes were to create one shapefile per week! Must re-run for each year


require(raster)
require(rgdal)
require(dplyr)
require(lubridate)

this_year <- 2022
t_init = Sys.time()

source("./OLCI_preprocessing/hole_chop.R")

#Input
input_files <- "./data/"
ice_dir <- paste0("./OLCI_preprocessing/input_ice_cover/",this_year)

#The shape files are assumed to be in input_files
l_conus <- "conus_boundary"

#Input/Output
ice_prelim_all <- "./OLCI_preprocessing/io_ice_cropped/"
ice_prelim <- paste0("./OLCI_preprocessing/io_ice_cropped/",this_year)
input_data<-paste0("./OLCI_preprocessing/input_OLCI/",this_year)

#Output
ice_out_all <- "./OLCI_preprocessing/ice_out/" 
ice_out<-paste0("./OLCI_preprocessing/ice_out/",this_year,"/") 
ice_shape_all <- "./OLCI_preprocessing/output_shapefiles/" 
ice_shape <- paste0("./OLCI_preprocessing/output_shapefiles/",this_year,"/") 

#Temporary
tmp_all <- "./tmp/"    #R write large temporary files when doing raster calculations
tmp_dir <- paste0("./tmp/",this_year,"/")

#Exit if input directories don't exist
if (!file.exists(input_files)) stop("Cannot find the main DATA directory for inputs and shapefiles.  Exiting.\n")
if (!file.exists(ice_dir)) stop("Cannot find the input_ice_cover directory for tiff inputs.  Exiting.\n")
if (!file.exists(input_data)) stop("Cannot find the main data directory for data files.  Exiting.\n")

#Check for all existing shapefiles
list_layers<-ogrListLayers(paste0(input_files,l_conus))
#Exit if nessessary shapefiles don't exist
if(! (l_conus %in% list_layers)) stop("The shapefile ", l_conus," does not exist in ",wd,"\n")

#Create output directories if they don't exist

if(!file.exists(tmp_all)){
    warning("Creating directory for all years temporary files in ",tmp_all,"\n")
    dir.create(tmp_all)
}

if(!file.exists(tmp_dir)){
    warning("Creating directory for temporary files in ",tmp_dir,"\n")
    dir.create(tmp_dir)
}

if(!file.exists(ice_prelim_all)){
    warning("Creating directory for all years masked ice tiffs in ",ice_prelim_all,"\n")
    dir.create(ice_prelim_all)
}

if(!file.exists(ice_prelim)){
    warning("Creating directory for masked ice tiffs in ",ice_prelim,"\n")
    dir.create(ice_prelim)
}

if(!file.exists(ice_shape_all)){
    warning("Creating directory for all years ice shapefiles in ",ice_shape_all,"\n")
    dir.create(ice_shape_all)
}

if(!file.exists(ice_shape)){
    warning("Creating directory for ice shapefiles in ",ice_shape,"\n")
    dir.create(ice_shape)
}

if(!file.exists(ice_out_all)){
  warning("Creating directory for all years ice weekly rasters in ",ice_out_all,"\n")
  dir.create(ice_out_all)
}

if(!file.exists(ice_out)){
  warning("Creating directory for ice weekly rasters in ",ice_out,"\n")
  dir.create(ice_out)
}

rasterOptions(tmpdir=tmp_dir)

conus <- readOGR(paste0(input_files,l_conus),layer=l_conus)

### Read in ice files
#Need to check these files too, and only use 'this_year'
reg_ex <- paste0("ims",this_year,"*_1km","*.tif")
fileNames<-c(list.files(ice_dir,pattern=glob2rx(reg_ex),full.names=FALSE,recursive=FALSE))
filePaths<-c(list.files(ice_dir,pattern=glob2rx(reg_ex),full.names=TRUE,recursive=FALSE))

rast.list_state<-list()
for(g in 1:length(fileNames)){
  
  # Print YYYYJJJ
  print(substring(fileNames[g],8,10))
  
  output<-paste0(paste0(ice_prelim,"/ice_imagesDAILY_masked"),substring(fileNames[g],4,10),"_trans.tif",sep="")
  
  if(file.exists(output)) {
    print('File exists - moving to next')
    next
  }
  
  cat("Time=",Sys.time()-t_init,"\n")
  rast.list_state<-raster(filePaths[g])
  SPtransSTATE<-projectRaster(rast.list_state,crs=crs(conus),res=4000)
  cat("Time after projectRaster=",Sys.time()-t_init,"\n")
  state_1<-crop(SPtransSTATE,conus,snap='in')
  cat("Time after crop=",Sys.time()-t_init,"\n")
  state<-mask(state_1,conus)
  cat("Time after mask=",Sys.time()-t_init,"\n")

  t2<-state
  t2[t2>3]<-3
  t2[t2<3]<-NA
  t2[t2==3]<-1
  cat("Time after pseudo-reclassify=",Sys.time()-t_init,"\n")


  writeRaster(t2,filename=output,format="GTiff",overwrite=TRUE)

}

### Read in ice files OLCI
#Use names from 'ice_dir' again, that has the proper year stamp in the character[4:7] place:
###read in olci files
fileNames<-c(list.files(input_data,pattern="*.tif",full.names=FALSE,recursive=FALSE))
filePaths<-c(list.files(input_data,pattern="*.tif",full.names=TRUE,recursive=FALSE))
#megan# dateST<-as.character(paste0(substr(fileNames,4,7),substr(fileNames,9,12),substr(fileNames,14,17),substr(fileNames,19,22)))
dateST <- as.character(substr(fileNames,2,15))
g<-unique(dateST) # OLCI dates formatted as YYYYJJJYYYYJJJ for each start/end date -- done in weeks

# #These are the files to be read in:
reg_ex <- paste0("*.tif")
filePathsI<-c(list.files(ice_prelim,pattern=glob2rx(reg_ex),full.names=TRUE,recursive=FALSE))
fileNamesI<-c(list.files(ice_prelim,pattern=glob2rx(reg_ex),full.names=FALSE,recursive=FALSE))
#print(fileNamesI)
year<-as.numeric(substr(fileNamesI,23,26))
this_year<-unique(year)

#L3 Throw an error if year is not equal to the input year
#if(year!=this_year){
 # stop("The year of the ice input files ",year," is not consistent with current year ",this_year," .")
#}

g3<-stack(filePathsI) # daily ice masks generated in previous loop


### weekly binning
date2<-as.numeric(substring(fileNamesI,27,29)) # Pulls Julian date from ICE PRELIM file names
date3<-sprintf("%03d",date2) # Formats the Julian dates into strings

# Rename for no apparent reason
state<-g3
namesWEEK<-names(state)

for (i in 1:length(g)){
  
  startD<-as.numeric(as.character(substr(g[i],5,7)))
  #startD <- as.numeric(substr(strftime(as.Date(paste0(substr(fileNames[i],4,7),substr(fileNames[i],9,12)),"%Y%m%d"),format = "%Y%j"),5,7))
  endD<-as.numeric(as.character(substr(g[i],12,14)))
  #endD <- as.numeric(substr(strftime(as.Date(paste0(substr(fileNames[i],14,17),substr(fileNames[i],19,22)),"%Y%m%d"),format = "%Y%j"),5,7))


  if (leap_year(this_year)==T) { # 2016 was a leap year --- would need to add code for 2020 as well
    if (startD>360){
      startD2=1
      date_grab<-c(unique(startD):366,sprintf("%03d",startD2:endD))
    } else {
      startD2=startD
      date_grab<-sprintf("%03d",startD2:endD)
    }
  } else {
    # print("it should be this year")
    if (startD>359){
      startD2=1
      date_grab<-c(unique(startD):365,sprintf("%03d",startD2:endD))
    } else {
      startD2=startD
      date_grab<-sprintf("%03d",startD2:endD)
    }
  }

  print(date_grab)  
  
  # Check to see whether file has already been generated -- SYYYYJJJYYYYJJJ_ice.shp
  output <- paste0(ice_shape,'S',this_year,first(date_grab),this_year,last(date_grab),'_ice.shp')
  if(file.exists(output)) {
    print('File exists - moving to next')
    next
  }
  
  result<-raster() # Initialize an empty raster
  for (l in 1:length(date_grab)){

    reg_ex2<-paste0(date_grab[l],"_trans",sep="")  #Just take the files for the current year
    
    ierr <- try(subset(state,grep(reg_ex2,namesWEEK,value=TRUE,fixed=TRUE)),TRUE)

    if(class(ierr) != "try-error"){ # if no error
      result1<-subset(state,grep(reg_ex2,namesWEEK,value=TRUE,fixed=TRUE))
    }else{ # if error
      reg_ex <- paste0(date_grab[l],"_trans",sep="")  #Will only throw an error if there is just one value (no 'dot')
      #result1<-subset(state,reg_ex2)
      print("inside try-error")  ##added by Yadong
      result1<-raster()
    }

    result<-stack(result,result1)
  }

  if(nlayers(result)>1){
    test<-calc(result,fun=max,na.rm=TRUE)
  }else{
    test<-result}

  output<-paste0("S",g[i],"_ice.tif",sep="")
  output2<-paste0(ice_out,"/",output,sep="")
  if(nlayers(test)>0){
    names(test)<-output
    writeRaster(test,filename = output2,format="GTiff",overwrite=T)

    ### Convert raster to spatial polygon
    #### read in "hole_chop.R" function to dissolve ice holes in polygon
    ### reproject file
    ll<-rasterToPolygons(test,dissolve=TRUE)
    cat("After rasterToPolygons, Time=",Sys.time()-t_init,"\n")
    gg<-hole_chop(ll)
    proj2<-crs(gg)
    cat("After proj2, Time=",Sys.time()-t_init,"\n")

    ### convert spatial polygon to spatial polygons data frame for new shapefile
    df <- data.frame(id = getSpPPolygonsIDSlots(gg))
    row.names(df) <- getSpPPolygonsIDSlots(gg)
    spdf <- SpatialPolygonsDataFrame(gg, data = df)
    cat("After SpatialPolygonsDataFrame, Time=",Sys.time()-t_init,"\n")
    proj4string(spdf) <- proj2
    spdf <- spTransform(spdf, proj2)
    #cat("After spTransform, Time=",Sys.time()-t_init,"\n")


    ## Write weekly ice shape file
    ### you will have to change the year prefix below!
    names1<-substr(names(test),1,19)
    output2<-paste0(names1,".shp")
    print(output2)
    writeOGR(spdf,layer="id",dsn=paste0(ice_shape,output2),driver="ESRI Shapefile",overwrite=TRUE)
    print("Shapefile Written")
  }
}

#Print out disk usage:
# cat("Disk usage, all:\n")
# system2("du",c("."))
# cat("Disk usage, tmp before delete:\n")
# system2("du",c("tmp"))

#Delete the temp directory
unlink(tmp_dir,recursive=TRUE,force=TRUE)
cat("End of script cyanoCONUS_ice_step3\n")
ot <- Sys.time() - t_init
print(ot)

