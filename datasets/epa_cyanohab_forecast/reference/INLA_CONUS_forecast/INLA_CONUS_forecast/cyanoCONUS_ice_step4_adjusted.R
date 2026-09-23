require(raster)
require(rgdal)

this_year <- 2022
t_init = Sys.time()
c_1 = "L"

#Input/Output
tmp_dir <- paste0("./tmp/",this_year,"/")
datadir <- paste0("./OLCI_preprocessing/output_CONUS_masked/",this_year)
outdir_all <- "./OLCI_preprocessing/output_masked_tif/"
outdir_year <- paste0(outdir_all,as.character(this_year),"/")

#My shapefiles are correct
shp_dir <- paste0("./OLCI_preprocessing/output_shapefiles/",this_year,"/")

#Exit if input directories don't exist
if (!file.exists(datadir)){
cat("Cannot find the main DATA directory for inputs.  Exiting.\n")
q()
return
}
if (!file.exists(shp_dir)){
cat("Cannot find the imagery directory for shapefile inputs.  Exiting.\n")
q()
return
}

#Create output directories if they don't exist
if(!file.exists(tmp_dir)){
    cat("Creating directory for temporary files, tmp_dir\n")
    dir.create(tmp_dir)
}
if(!file.exists(outdir_all)){
    cat("Creating directory for masked tif output files, output\n")
    dir.create(outdir_all)
}

if(!file.exists(outdir_year)){
    cat("Creating directory for masked tif output files, output\n")
    dir.create(outdir_year)
}

rasterOptions(tmpdir=tmp_dir)


############### CYANO DATA #############
fileNames<-c(list.files(datadir,pattern=paste('validpixels.tif',sep=""),full.names=FALSE,recursive=FALSE)) # outputs from steps1/2

sub<-substring(fileNames,2,5)       #9-12 is the 4 digit year
which_years<-unique(sub)       #Which years are files for?
if(length(which_years)!=1) warning("There is more than one year of data in the output_CONUS_masked directory.  The only year to be used will be ",this_year)
#L3 Throw an error if year is not equal to the input year
#if(which_years!=this_year){
# stop("The year of the ice input files ",year," is not consistent with current year ",this_year," .")
#}

day <- substring(fileNames,6,8) #Day of week, should start at >= 1 , and add 7's for each week
day2<-unique(day)

n_files_mp <- length(day2) # Number of files for the year

#################### ICE ###########
reg_ex <- paste0("*.shp")  #Just take the files for the current year
ice1<-c(list.files(shp_dir,pattern=glob2rx(reg_ex),full.names=FALSE,recursive=FALSE)) # Lists ice shapefiles, not including filepath
head(ice1)

ice2<-c(list.files(shp_dir,pattern=glob2rx(reg_ex),full.names=TRUE,recursive=FALSE)) # Lists ice shapefiles, including filepath
day_ice<-as.character(substr(ice1,13,15))

n_files_ice <- length(day_ice)  #Number of files, should be 52 (put in error checking)

for (j in 1:n_files_ice){
  print(j)
  
  outputname<-substring(ice1[j],2,15)
  output<-paste0(outdir_year,"CI_",outputname,"_out.tif",sep="")
  
  if(file.exists(output)) {
    print('File exists - moving to next')
    next
  }
  
  cat("Time at j =",j," loop for ice masking =",Sys.time()-t_init,"\n")

  layerN<-substring(ice1[j],1,19)

  ice<-readOGR(shp_dir,layer=layerN)

  end_of_week<-substr(ice1[j],9,15)

  reg_ex <- paste0(c_1,end_of_week,"*.tif")  #Just take the files for the current year
  # print(reg_ex)
  reg_ex2 <- paste0(c_1,strftime(as.Date(end_of_week,"%Y%j"),format = "%Y%j"),"*.tif")
  filePaths<-c(list.files(datadir,pattern=glob2rx(reg_ex2),full.names=TRUE,recursive=FALSE)) #This also has path to files
  # print(filePaths)

  if(length(filePaths)==0){
    cat("There is no valid pixel output ",reg_ex2," to match the shape file ",layerN,"\n")
    cat("Skipping j =",j," in loop over shapefiles.\n")
    next
  }

  cat("The ice shapefile used will be ",layerN," and the tif file will be ",filePaths,"\n")

  data<-raster(filePaths)
  data<-reclassify(data,c(253,Inf,NA))
  print("after reclassify to NA") 
  ot <- Sys.time() - t_init
  print(ot)

  outputMASKED <- mask(data,ice,inverse=T)

  # Should be 'CI_2017123120180106_out.tif' CI_YYYYJJJYYYYJJJ_out.tif -- currently 'CI_20161222016128_icout.tif' CI_YYYYJJJYYYYJJJ_icout.tif
  writeRaster(outputMASKED,filename=output,format="GTiff",overwrite=T)
  
  print(paste0(outputname,' written'))

}  #end loop over weeks
# 
# 
# #Print out disk usage:
# cat("Disk usage, all:\n")
# system2("du",c("."))
# cat("Disk usage, tmp before delete:\n")
# system2("du",c("tmp"))

#Delete the temp directory
unlink(tmp_dir,recursive=TRUE,force=TRUE)

cat("End of script cyanoCONUS_ice_step4\n")
ot <- Sys.time() - t_init
print(ot)

