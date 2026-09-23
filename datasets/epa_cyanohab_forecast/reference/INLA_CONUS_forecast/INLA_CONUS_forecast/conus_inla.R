# INLA conus model set up for Atmos
# Author: Natalie Reynolds
# Initial date: 11-17-22

# To restart R: CTRL + SHIFT + fn + F10

# Set up ws ----

# Clear environment
rm(list = ls(all = T))
t_init = Sys.time()

# load("/work/HAB4CAST/cyano_forecast/inla_exports/2023-06-07/workspace.RData")

# Set seed
set.seed(1234)

# Libraries
library(tidyverse)
library(INLA) 
library(inlabru)
library(ROCR)
library(caret)
library(RColorBrewer)
library(ggpubr)
library(colorspace)
library(lubridate)
library(grid)
library(gridExtra)
library(cowplot)

source('data/HighstatLibV10.R')

# Spatial libraries
library(sf)
library(ggspatial) # For plotting

# set cutoff denominator
denom <- 50

# Create save location for figures ----
figures_folder <- './inla_exports/'
export_fp <- str_c(figures_folder,Sys.Date(),'/')

if(!file.exists(figures_folder)){
  warning("Creating directory for exported figures in ", figures_folder, "\n")
  dir.create(figures_folder)
}

if(!file.exists(export_fp)){
  warning("Creating sub-directory for exported figures in ", export_fp, "\n")
  dir.create(export_fp)
}

# Read in data ----
# Compiled data
compiled_data <- read_csv('data/compiled_data.csv')

week_assignments <- read_csv('data/week_assignments.csv') %>%
  group_by(week,year) %>%
  mutate(date = min(date),
         month = month(date)) %>% dplyr::select(-date) %>% distinct()
week_assignments %>% filter(year == 2021) %>% group_by(month) %>% mutate(Week = min(week)) %>% dplyr::select(-week) %>% distinct()-> weeks

# Spatial data ----
## Lake shapefiles - Albers projection, done in shapefile preparation in ArcGIS Pro
conus_lakes <- read_sf('data/OLCI_resolvable_lakes_2022_09_08/OLCI_resolvable_lakes_2022_09_08.shp') %>% mutate(COMID = as.numeric(COMID))

st_crs(conus_lakes)

## CONUS boundary
not_conus <- c("VI","HI","AK","MP","PR","GU","AS")

states_bound <- read_sf('data/cb_2019_us_state_500k/cb_2019_us_state_500k.shp') %>% filter(!STUSPS %in% not_conus) %>%
  st_transform(st_crs(conus_lakes))

conus_bound <- st_union(states_bound)

# Prep the input data ----
## Weeks are defined to match the Time column in compiled data, YYYYWW

first_week <- 201701
mid_week <- 202101
final_week <- 202152

input <-
  compiled_data %>%

  # Fill Wtemp data
  group_by(COMID) %>%
  arrange(COMID,Time) %>%
  mutate(Cyano_adjusted = lead(Cyano),
         Bloom_adjusted = as.numeric(lead(Bloom)),
         Wtemp_adjusted = ifelse(Wtemp < 0, NA, Wtemp)) %>%
  fill(Wtemp_adjusted) %>%
  ungroup() %>%

  # Keep only data that falls within the wtemp data
  filter(Time >= first_week & Time <= final_week) %>%

  # Set aside prediction data
  mutate(subset = ifelse(Time >= mid_week & Time <= final_week, # Should be final_week
                         'prediction', NA)) %>%

  # Pre-process Bloom data
  filter(!is.na(subset) | (!is.na(Bloom_adjusted) & is.na(subset))) %>%

  # Partitions data into 80% training, validation, and final week for prediction
  mutate(
    # Create a row number column for ifelse statement
    row = row_number(),
    # Start by setting all max times (YYYYWW) to prediction
    subset = ifelse(Time >= mid_week & Time <= final_week, # Should be final_week
                    'prediction',
                    # For data not in prediction, sample 80% for training data
                    ifelse(row %in% sample(which(Time != max(Time)),
                                           floor(0.7*length(which(Time != max(Time))))),
                           'training',
                           # Remaining data is reserved as validation data
                           'validation'))) %>%

  # Scale continuous predictor variables
  mutate(
    Atemp = scale(Atemp)[,1],
    Wtemp = scale(Wtemp)[,1],
    Wtemp_adjusted = scale(Wtemp_adjusted)[,1],
    Precip = scale(Precip)[,1],
    Area = scale(Area)[,1],
    dMean = scale(dMean)[,1],
    dMax = scale(dMax)[,1],
    subset = factor(subset, levels = c('training', 'validation', 'prediction'), ordered = T)
  ) %>% arrange(subset,COMID,Time) %>% dplyr::select(-Atemp) # Atemp removed from model because it was colinear with Wtemp_adjusted

summary(input)

# Calculate the median chlorophyll concentration above the cutoff
input %>% filter(Bloom_adjusted == 1) %>% summarize(med_dn = median(Cyano_adjusted),
                                                    med_ci = (10^((3/250)*med_dn - 4.2)),
                                                    med_chl =med_ci*6620 - 3.07)

# Examine Variance Inflation Factor
corvif((dplyr::select(
  input,
  # Atemp, # Atemp removed from model because it was colinear with Wtemp_adjusted
  Wtemp_adjusted,Precip,
  Area,dMean,
  Week,LONG,LAT)))

# Fit initial INLA model ----
# Set up parameters for time function -- an autoregressive model of order 1 (AR1)
hyprior <- list(theta1 = list(prior="pc.prec", param=c(0.5, 0.05)),
                theta2 = list(prior="pc.cor1", param=c(0.1, 0.9)))

# Pull centroids
centroids <- input %>% dplyr::select(COMID,LAT,LONG) %>% distinct()

loc <- cbind(input$LONG,input$LAT)

# Build mesh
max_edge <- diff(range(loc[,1]))/15

## Buffer lakes to ensure more are within the mesh boundary -- experiments to determine buffer size run on 12/20/22
lakes_buffer <- st_buffer(st_union(conus_lakes), 2000)

(mesh <- inla.mesh.2d(loc = loc,
                      boundary = sf::as_Spatial(lakes_buffer),
                      max.edge = max_edge*c(1,2),
                      offset = max_edge*c(1,2),
                      cutoff = max_edge/denom # Results in ~6km mesh edge cutoff, experiments recorded 11/17
))$n # Prints out number of mesh nodes after fitting mesh

# A matrix
a_matrix <- inla.spde.make.A(mesh,loc)
## nrow = mesh$n and ncol = nrow(loc) -- essentially tells us which vertex each observation falls on

# Index
index <- inla.spde.make.index('s',mesh$n)

# SPDE model
spde <- inla.spde2.matern(mesh)

# Generate data stacks
stack <- inla.stack(
  data = list(Bloom_adjusted = c(pull(filter(input,
                                             subset == 'training'),Bloom_adjusted),
                                 rep(NA,nrow(filter(input,
                                                    subset != 'training'))))),
  A = list(a_matrix,1),
  effects = list(index,
                 list(data.frame(dplyr::select(
                   input,
                   # Atemp,
                   Wtemp_adjusted,Precip,
                   Area,dMean,dMax,
                   Week,LONG,LAT))))
)

# Run the inla model - NOTE - REMOVED ATEMP
formula4 <- Bloom_adjusted ~ -1 + Wtemp_adjusted + Precip + Area + dMean + f(Week, model = 'ar1', hyper = hyprior, constr = T) + f(s, model = spde)

results4 <- inla(formula4,
                 family = 'binomial',
                 control.family = list(link = 'logit'),
                 data = inla.stack.data(stack),
                 control.predictor = list(
                   A = inla.stack.A(stack),
                   compute = T, link = 1 # compute = T enables the fitted.values calculation, link = 1
                 ),
                 control.inla = list(int.strategy = 'eb'),
                 verbose = F,
                 control.compute = list(dic = T,cpo = T))

summary(results4)

time_i <- Sys.time() # time_i indicates intermediate model times
print(time_i - t_init)


# Set up for loop to iterate final year ----
results_i <- results4

time_seq <- seq(mid_week,final_week,1)
data_i <- list(Bloom_adjusted = c(pull(filter(input,
                                              subset == 'training'),Bloom_adjusted),
                                  rep(NA,nrow(filter(input,
                                                     subset != 'training')))))

prediction_response <- rep(NA,nrow(filter(input,subset == 'prediction')))
prediction_sd <- rep(NA,nrow(filter(input,subset == 'prediction')))

for(i in 1:length(time_seq)){

  # Set up row numbers --
  # row_sub refers to row numbers in the overall dataset (regardless of subset), and
  # pred_row_sub refers to row numbers specifically within the prediction subset

  row_sub <- which(input$Time == time_seq[i])
  pred_row_sub <- which(filter(input, subset == 'prediction')$Time == time_seq[i])

  # Store results
  prediction_response[pred_row_sub] <- results_i$summary.fitted.values$mean[row_sub]
  prediction_sd[pred_row_sub] <- results_i$summary.fitted.values$sd[row_sub]

  # Refit model--
  # Create data stack
  data_i$Bloom_adjusted[row_sub] <- input$Bloom_adjusted[row_sub]

  stack_i <- inla.stack(
    data = data_i,
    A = list(a_matrix,1),
    effects = list(index,
                   list(data.frame(dplyr::select(
                     input,
                     Wtemp_adjusted,Precip,
                     Area,dMean,dMax,
                     Week,LONG,LAT))))
  )

  results_i <- inla(formula4,
                    family = 'binomial',
                    control.family = list(link = 'logit'),
                    data = inla.stack.data(stack_i),
                    control.predictor = list(
                      A = inla.stack.A(stack),
                      compute = T, link = 1 # compute = T enables the fitted.values calculation, link = 1
                    ),
                    control.inla = list(int.strategy = 'eb'),
                    verbose = F,
                    control.compute = list(dic = T,cpo = T),
                    control.mode = list(result = results_i,restart = T))

  print(Sys.time() - time_i)
  time_i <- Sys.time()

}

summary(results_i)

# Model results ----
# Pull mean predictions
responses <- results4$summary.fitted.values$mean[1:nrow(input)]

## VALIDATION
# Subset mean responses for validation (aka validation) data only
validation_responses <- responses[which(input$subset == 'validation')]

# Pull corresponding validation observations
validation_observations <- input %>% filter(subset == 'validation') %>% pull(Bloom_adjusted)

validation_roc_instance <- prediction(validation_responses,validation_observations)

validation_roc_performance_instance <- performance(validation_roc_instance, measure = 'tpr', x.measure = 'fpr')

# View prediction response
summary(prediction_response)
# Formerly: Pull prediction response:
# prediction_response <- responses[which(input$subset == 'prediction' & !is.na(input$Bloom_adjusted))] # Now populated in for loop

# Pull corresponding observations
prediction_observations <- input %>% filter(subset == 'prediction' & !is.na(Bloom_adjusted)) %>% pull(Bloom_adjusted)
prediction_response_na_omit <- prediction_response[which(!is.na(filter(input,subset == 'prediction')$Bloom_adjusted))]

optimize_cutoff <- function(performance, value) {
  cut_index <- mapply(FUN = function(x, y, p){
    d <- (x - 0)^2 + (y - 1)^2
    index <- which(d == min(d))
    c(sensitivity = y[[index]], # tpr
      specificity = 1-x[[index]], #tnr
      cutoff = p[[index]])},
    # The '@' operator is used to access data in S4 class objects (e.g. the performance instances)
    performance@x.values, # tpr
    performance@y.values, # tnr
    value@cutoffs
  )
}

cutoff <- optimize_cutoff(validation_roc_performance_instance,
                          validation_roc_instance) # Cutoff value is cutoff[3]

generate_cm <- function(responses, observations) {
  tibble(
    response = factor(responses >= cutoff[3],
                      levels = c(T,F), ordered = T),
    observed = factor(observations, levels = c(1,0),
                      labels = c(T,F), ordered = T)
  ) %>% table() %>% return()
}

generate_stats <- function(responses, observations) {
  cm <- generate_cm(responses = responses, observations = observations)

  roc_instance <- prediction(responses,observations)

  auc <- performance(roc_instance, measure = 'auc')

  stats <- confusionMatrix(cm)

  tibble(
    AUC = auc@y.values[[1]],
    Sensitivity = stats$byClass[1],
    Specificity = stats$byClass[2],
    Accuracy = stats$overall[1],
    Precision = cm[1,1]/(cm[1,1] + cm[1,2]),
    Prevalance = (cm[1,1] + cm[2,1])/sum(cm),
    `False Omission Rate` = cm[2,1]/(cm[2,1] + cm[2,2]),
    `F1 Score` = (2*cm[1,1])/(2*cm[1,1] + cm[1,2] + cm[2,1]),
    Kappa = stats$overall[2],
    `Brier Score` = mean((responses - observations)^2)
    ) %>% t() %>% return()
}

print(cutoff[[3]])

### VALIDATION RESULTS
val_cm <- generate_cm(responses = validation_responses,observations = validation_observations)
print(val_cm)

val_stats <- generate_stats(responses = validation_responses,
                            observations = validation_observations)
print(val_stats)

### PREDICTION RESULTS
pred_cm <- generate_cm(responses = prediction_response_na_omit,observations = prediction_observations)
print(pred_cm)

pred_stats <- generate_stats(responses = prediction_response_na_omit,observations = prediction_observations)
print(pred_stats)

# Previously:
generate_stats(responses[which(input$subset == 'prediction' & !is.na(input$Bloom_adjusted))],prediction_observations)

# Generate export data ----
tibble(
  COMID = input$COMID,
  Time = input$Time,
  observed_med_cyan = input$Cyano,
  observed_bloom = input$Bloom_adjusted,
  response_prob = c(results4$summary.fitted.values$mean[which(input$subset != 'prediction')],
                    prediction_response),
  response_sd = c(results4$summary.fitted.values$sd[which(input$subset != 'prediction')],
                  prediction_sd),
  response_bloom = ifelse(response_prob >= cutoff[3],
                          1,0),
  class = factor(ifelse(response_bloom == 0 & observed_bloom == 0, 'TN',
                        ifelse(response_bloom == 0 & observed_bloom == 1, 'FN',
                               ifelse(response_bloom == 1 & observed_bloom == 1, 'TP',
                                      ifelse(response_bloom == 1 & observed_bloom == 0, 'FP',NA))))), # NA's should equal the number of missing values in input$Bloom_adjusted
  subset = input$subset
) %>%
  mutate(class = factor(class, levels = c('TP','FP','TN','FN'),
                        # labels = c('True positive','False positive',
                        #            'True negative','False negative'),
                        ordered = T),
         subset = factor(subset,
                         levels = c('training','validation','prediction'),
                         labels = c('Training', 'Validation', 'Prediction'),
                         ordered = T)) -> export_csv

summary(export_csv)
write_csv(export_csv, str_c(export_fp,'results.csv'))

# Tables from paper ----

## Table 1 ## Posterior estimates (mean, St. Dev., quantiles) for fixed effects. ----

results_i$summary.fixed[,1:5] %>% round(digits = 2) %>%
  rename(Mean = mean,
         `St. Dev` = sd,
         `0.025` = `0.025quant`,
         `0.5` = `0.5quant`,
         `0.975` = `0.975quant`
  ) -> table_1

# Converted to probabilities:
# table_1 <- round(exp(results_i$summary.fixed[,1:5])/(1+ exp(results_i$summary.fixed[,1:5])),digits = 2) %>% 
#   rename(Mean = mean,
#          `St. Dev` = sd,
#          `0.025` = `0.025quant`,
#          `0.5` = `0.5quant`,
#          `0.975` = `0.975quant`
#          ) %>%
#   # Overwrite standard deviation with correct calculations
#   mutate(
#     `St. Dev` = (`0.975` - `0.5`)/2
#   )
# 
# print(table_1)  

# # Visualize
# results_i$marginals.fixed[[1]] %>% as_tibble() %>% mutate(var = results_i$names.fixed[1]) %>%
#   rbind(results_i$marginals.fixed[[2]] %>% as_tibble() %>% mutate(var = results_i$names.fixed[2])) %>%
#   rbind(results_i$marginals.fixed[[3]] %>% as_tibble() %>% mutate(var = results_i$names.fixed[3])) %>%
#   rbind(results_i$marginals.fixed[[4]] %>% as_tibble() %>% mutate(var = results_i$names.fixed[4])) %>%
#   ggplot() +
#   geom_line(aes(x = x,y = y)) +
#   facet_wrap(~var, scales = 'free')
# 
# # Transform then visualize
# results_i$marginals.fixed[[1]] %>% as_tibble() %>% mutate(var = results_i$names.fixed[1]) %>%
#   rbind(results_i$marginals.fixed[[2]] %>% as_tibble() %>% mutate(var = results_i$names.fixed[2])) %>%
#   rbind(results_i$marginals.fixed[[3]] %>% as_tibble() %>% mutate(var = results_i$names.fixed[3])) %>%
#   rbind(results_i$marginals.fixed[[4]] %>% as_tibble() %>% mutate(var = results_i$names.fixed[4])) %>%
#   mutate(x = exp(x)/(1+exp(x))) %>%
#   ggplot() + 
#   geom_line(aes(x = x,y = y)) + 
#   facet_wrap(~var, scales = 'free_y') +
#   scale_x_continuous(limits = c(0,1))

# Previously:
results4$summary.fixed[,1:5] %>% format(digits = 1) %>%
  rename(Mean = mean,
         `St. Dev` = sd,
         `0.025` = `0.025quant`,
         `0.5` = `0.5quant`,
         `0.975` = `0.975quant`
  )


## Table 2 ## Posterior estimates (mean, St. Dev., quantiles) for random effects. ----

## Compute values for Table 4 in manuscript ##

## Spatial range and variance
results_i_spatial <- inla.spde2.result(results_i,'s',spde)

## Range
mean_range <- inla.emarginal(function(x) x, results_i_spatial$marginals.range.nominal[[1]])
mean_range_2 <- inla.emarginal(function(x) x^2, results_i_spatial$marginals.range.nominal[[1]])
stdev_range <- sqrt(mean_range_2 - mean_range^2)
ci_range <- inla.qmarginal(c(0.025, 0.5, 0.975), results_i_spatial$marginals.range.nominal[[1]])

mean_variance <- inla.emarginal(function(x) x, results_i_spatial$marginals.variance.nominal[[1]])
mean_variance_2 <- inla.emarginal(function(x) x^2, results_i_spatial$marginals.variance.nominal[[1]])
stdev_variance <- sqrt(mean_variance_2 - mean_variance^2)
ci_variance <- inla.qmarginal(c(0.025, 0.5, 0.975), results_i_spatial$marginals.variance.nominal[[1]])

# Compute the variance for the AR1 component 'temporal variance'
ar1_variance <- inla.tmarginal(function(x) (1/x), results_i$marginals.hy[[1]])
mean_ar1_variance <- inla.emarginal(function(x) x, ar1_variance)
mean_ar1_variance_2 <- inla.emarginal(function(x) x^2, ar1_variance)
stdev_mean_ar1_variance <- sqrt(mean_ar1_variance_2 - mean_ar1_variance ^2)
ci_ar1_variance <- inla.qmarginal(c(0.025,0.5,0.975),ar1_variance)

# Pull the AR1 parameter
ar1 <- inla.tmarginal(function(x) x, results_i$marginals.hyperpar[[2]])
mean_ar1 <-  inla.emarginal(function(x) x, ar1)
mean_ar1_2 <- inla.emarginal(function(x) x^2, ar1)
stdev_mean_ar1 <- sqrt(mean_ar1_2 - mean_ar1^2)
ci_ar1 <- inla.qmarginal(c(0.025,0.5,0.975), ar1)

# Set up a summary table // Table 4 in the manuscript
table_2 <- tibble(
  Mean = c(mean_ar1_variance,mean_variance,mean_range,mean_ar1),
  `St. Dev.` = c(stdev_mean_ar1_variance,stdev_variance,stdev_range,stdev_mean_ar1),
  `0.025` = c(ci_ar1_variance[1],ci_variance[1],ci_range[1],ci_ar1[1]),
  `0.5` = c(ci_ar1_variance[2],ci_variance[2],ci_range[2],ci_ar1[2]),
  `0.975` = c(ci_ar1_variance[3],ci_variance[3],ci_range[3],ci_ar1[3])
) %>% as.data.frame() %>% format(digits = 2, scientific = F, bigmark = ',')
rownames(table_2) <- c("Temporal variance",
                       "Spatial Variance (m)",
                       "Spatial Correlation Range, rho (m)",
                       "AR(1) parameter, alpha")

print(table_2)

## Tables 3 and 4 are confusion matrices ## ----

## Table 5 ## Results of the statistical evaluation metrics obtained using the cutoff point ----

table_5 <- val_stats %>% cbind(pred_stats) %>% as.data.frame() %>%
  rename(
         `Validation dataset` = V1,
         `Prediction dataset` = V2) %>% format(digits = 2)
print(table_5)

# Figures from paper ----

## Figure 1 ## Choropleth map of the number of high-risk bloom weeks in CONUS lakes from 2017 through 2021. ----

input %>%
  group_by(COMID) %>%
  summarise(
    n = sum(Bloom_adjusted, na.rm = T),
    LAT = LAT,
    LONG = LONG) %>% distinct() %>%
  arrange(n) %>%
  ggplot()+
  geom_sf(data = states_bound,fill = 'white', lwd = .25, color = 'gray70') +
  geom_sf(data = conus_bound,fill = 'transparent',lwd = .25) +
  geom_point(aes(x = LONG, y = LAT, fill = n, color = n),
             alpha = .7, shape = 21, size = 1) +
  scale_fill_gradientn(name = 'Number of\nbloom weeks',
                       colors = brewer.pal(n = 9, name = 'BuGn'),
                       ) +
  scale_color_gradientn(name = 'Number of\nbloom weeks',
                        colors = darken(brewer.pal(n = 9, name = 'BuGn'),0.3)
  ) +
  annotation_scale(width_hint = .1) +
  annotation_north_arrow(style = north_arrow_minimal,
                         height = unit(1.3,'cm'),
                         pad_y = unit(1.8,'line'),
                         pad_x = unit(-.12,'in')) +
  xlab('Longitude') + ylab("Latitude") +
  theme_bw() +
  theme(text = element_text(size = 12,),
        legend.title = element_text(size = 10),
        axis.text.x = element_text(angle = 45,hjust = 1)) +
  guides(color = 'none') -> figure_1

input %>%
  group_by(COMID) %>%
  summarise(
    n = sum(Bloom_adjusted, na.rm = T),
    LAT = LAT,
    LONG = LONG) %>% distinct() %>%
  arrange(n) %>% write.csv(str_c(export_fp,'values_1.csv'))

figure_1

ggsave(
  str_c(export_fp,'figure_1.jpg'),
  figure_1,
  height = 4,
  width = 6.5,
  units = 'in',
  dpi = 600
)


## Figure 2 ## Mean AR (1) temporal trend corresponding to week of year across all study years and lakes. The shaded area represents the 95% credible interval ----
weekvalues_4 <- tibble(
  week = results_i$summary.random$Week$ID,
  mean_lo = results_i$summary.random$Week$mean,
  lower_lo = results_i$summary.random$Week$`0.025quant`,
  upper_lo = results_i$summary.random$Week$`0.975quant`,
  mean_prob = NA,
  lower_prob = NA,
  upper_prob = NA
)

# Populate probability column
weekvalues_4[,5:7] <- exp(weekvalues_4[2:4])/(1 + exp(weekvalues_4[2:4]))

weekvalues_4 %>% write.csv(str_c(export_fp,'values_2.csv'))

ggplot(weekvalues_4) +
  geom_line(aes(y = mean_lo, x = week), size = .75, color = 'black') +
  geom_ribbon(aes(ymin = lower_lo, ymax = upper_lo, x = week), alpha = 0.3, fill = 'gray50') +
  # geom_hline(yintercept = 0, lty = 3) +
  scale_x_continuous(name = 'Month',
                     breaks = weeks$Week,labels = weeks$month,
                     expand = expansion(0,0)) +
  # scale_x_continuous(name = "Week",
  #                    breaks = seq(0,48,12),limits = c(1,52),
  #                    expand = expansion(0,0)) +
  scale_y_continuous(name = 'Log Odds') +
  theme_bw() +
  theme(text = element_text(size = 10),
        panel.grid.minor = element_blank()) -> figure_2

figure_2

ggsave(
  str_c(export_fp,'figure_2.jpg'),
  figure_2,
  height = 5,
  width = 5,
  units = 'in',
  dpi = 600
)


## Figure 3 ## Mean of spatial random effect mapped across lakes in CONUS. Lakes with relatively higher log-odds of a high-risk cyanobacterial bloom are indicated with warm colors, while cool colors represent lakes with relatively lower log-odds of high-risk blooms. ----

# Projector object (need for coordinates)
grid_projector <- inla.mesh.projector(
  mesh = mesh,
  loc = unique(loc)
)

# Attach the values to the coordinates
grid_proj <- inla.mesh.project(
  projector = grid_projector,
  field = results_i$summary.random[['s']][['mean']]
) %>% as.matrix()

# Join data for plotting
plot_data <- tibble(
  LONG = grid_projector$loc[,1],
  LAT = grid_projector$loc[,2],
  field_val = grid_proj[,1]
) %>%
  merge(centroids) %>%
  merge(dplyr::select(conus_lakes,COMID,geometry))

# Plot // Figure 3 in manuscript
plot_data %>% as_tibble() %>%
  arrange(field_val) %>%
  # mutate(field_val = ordered(cut(exp(field_val)/(1 + exp(field_val)),breaks = seq(0,1,0.2)), levels = c('(0.8,1]','(0.6,0.8]','(0.4,0.6]','(0.2,0.4]','(0,0.2]'))) %>%
  ggplot()+
  geom_sf(data = states_bound,fill = 'white', lwd = .25, color = 'gray70') +
  geom_sf(data = conus_bound,fill = 'transparent',lwd = .25) +
  geom_point(aes(x = LONG, y = LAT, fill = field_val,  color = field_val),
             alpha = .8, shape = 21, size = 1) +
  scale_fill_gradientn(name = 'Log Odds',
                    colors = c("#4f718f","#856898","#c57b93",
                               "#faa594","#ffff8f"),
                    limits = c(-15,10)) +
  scale_color_gradientn(name = 'Log Odds',
                     colors = darken(c("#4f718f","#856898","#c57b93",
                                       "#faa594","#ffff8f"),0.3),
                     limits = c(-15,10)) +
  annotation_scale(width_hint = .1) +
  annotation_north_arrow(style = north_arrow_minimal,
                         height = unit(1.3,'cm'),
                         pad_y = unit(1.8,'line'),
                         pad_x = unit(-.12,'in')) +
  guides(color = 'none') +
  xlab('Longitude') + ylab("Latitude") +
  theme_bw() +
  theme(legend.title = element_text(size = 10),
        text = element_text(size = 10),
        axis.text.x = element_text(angle = 45,hjust = 1))  -> figure_3

figure_3

plot_data %>% as_tibble() %>%
  arrange(field_val) %>%
  # mutate(field_val_cut = ordered(cut(exp(field_val)/(1 + exp(field_val)),breaks = seq(0,1,0.2)), levels = c('(0.8,1]','(0.6,0.8]','(0.4,0.6]','(0.2,0.4]','(0,0.2]'))) %>% 
  dplyr::select(-geometry) %>%
  write.csv(str_c(export_fp,'values_3.csv'))

ggsave(
  str_c(export_fp,'figure_3.jpg'),
  figure_3,
  height = 4,
  width = 6.5,
  units = 'in',
  dpi = 600
)

## Figure 4 ## Map of mean (A) and standard deviation (B) of probability of exceedance of high-risk bloom event for the prediction week. ----

plot_data_pred_prob <- tibble(
  COMID = input$COMID[which(input$subset == 'prediction')],
  Week = input$Week[which(input$subset == 'prediction')],
  LONG = input$LONG[which(input$subset == 'prediction')],
  LAT = input$LAT[which(input$subset == 'prediction')],
  probability = prediction_response
) %>% left_join(dplyr::select(conus_lakes,COMID,geometry)) %>%  right_join(weeks)

plot_data_pred_prob %>% dplyr::select(-geometry) %>% write.csv(str_c(export_fp,'values_4.csv'))

tibble(
  COMID = input$COMID[which(input$subset == 'prediction')],
  Week = input$Week[which(input$subset == 'prediction')],
  LONG = input$LONG[which(input$subset == 'prediction')],
  LAT = input$LAT[which(input$subset == 'prediction')],
  probability = prediction_response
) %>% write.csv(str_c(export_fp,'values_4_all_weeks.csv'))

plot_data_st_dev <- tibble(
  COMID = input$COMID[which(input$subset == 'prediction')],
  Week = input$Week[which(input$subset == 'prediction')],
  LONG = input$LONG[which(input$subset == 'prediction')],
  LAT = input$LAT[which(input$subset == 'prediction')],
  st_dev =  prediction_sd
) %>% left_join(dplyr::select(conus_lakes,COMID,geometry))  %>% right_join(weeks)

plot_data_st_dev %>% dplyr::select(-geometry) %>% write.csv(str_c(export_fp,'values_s2.csv'))

# Plot
figure_4 <- ggplot()+
  geom_sf(data = states_bound,fill = 'white', lwd = .25, color = 'gray70') +
  geom_sf(data = conus_bound,fill = 'transparent',lwd = .25) +
  geom_point(data = arrange(plot_data_pred_prob,probability),
             aes(x = LONG, y= LAT,  fill = probability, color = probability),
             alpha = .7, shape = 21, size = .7) +
  scale_fill_gradientn(limit = c(0,1),
                       name = 'Mean probability\nof bloom',
                       colors = c("#4f718f","#856898","#c57b93",
                                  "#faa594","#ffff8f"),
                       breaks = seq(0,1,.2)
  ) +
  scale_color_gradientn(name = 'Mean probability\nof bloom',
                        colors = darken(c("#4f718f","#856898","#c57b93",
                                          "#faa594","#ffff8f"),0.3),
                        limit = c(0,1),
                        breaks = seq(0,1,.2)
  ) +
  facet_wrap(~factor(month,levels = 1:12, ordered= T, labels = month.name),ncol = 3)+
  annotation_scale(width_hint = 0.09,
                   pad_x = unit(0.1,'cm'),
                   pad_y = unit(0.1,'cm'),
                   text_pad = unit(0.1, "cm"),
                   height = unit(0.2,'cm'),
                   data = tibble(month = 10)) +
  annotation_north_arrow(aes(location = 'br'),
                         data = tibble(month = 10),
                         height = unit(.8,'cm'),
                         pad_y = unit(0.1,'cm'),
                         pad_x = unit(-0.17,'in'),
                         style = north_arrow_minimal(text_size = 8)) +
  ylab('Latitude') +
  xlab('Longitude') +
  theme_bw() +
  theme(text = element_text(size = 10),
        # legend.title = element_text(size = 8),
        legend.position = 'bottom',
        legend.text = element_text(angle = 45,hjust = 1),
        legend.title = element_text(vjust = 1),
        axis.text.x = element_text(angle = 45,hjust = 1),
        # axis.title.y = element_blank(),
        strip.background = element_rect(fill = 'white'),
        strip.text = element_text(margin = margin(t = 2, r = 0,
                                                  b = 2, l = 0, unit = "pt"))) +
  guides(color = 'none')

figure_4

ggsave(str_c(export_fp,'figure_4.jpg'), # if you put the legend on the left, save as height = 5, width = 6.5
       figure_4,
       height = 7,
       width = 6.5,
       units = 'in',
       dpi = 600,
       bg="white")


## Figure 5 ## Box plots of prediction mean and standard deviation for TP, FP, TN, FN breakdown ----

# Print quartiles
export_csv %>% filter(subset == 'Prediction' & !is.na(class)) %>% group_by(class) %>%
  summarise(values = quantile(response_prob),
            quantile = seq(0,1,0.25)) %>% write_csv(str_c(export_fp, 'values_5.csv'))

figure_5 <- ggarrange(
  export_csv %>%
    filter(!is.na(class), subset == 'Prediction') %>%
    ggplot() +
    geom_boxplot(aes(x = class,y = response_prob)) +
    geom_hline(yintercept = cutoff[3],color = 'gray40', linetype = 'longdash') +
    geom_text(data = (export_csv %>%
                        filter(!is.na(class), subset == 'Prediction') %>%
                        group_by(class) %>% count() %>%
                        mutate(n = str_c('(',formatC(n,format="d", big.mark=","),')'))),
              mapping = aes(x = class, y = 1, label = n, vjust = -0.75), size = 3) +
    # facet_wrap(~subset) +
    labs(x = 'Class',
         y = 'Response Probability') +
    theme_bw(),

  export_csv %>%
    filter(!is.na(class), subset == 'Prediction') %>%
    ggplot() +
    geom_boxplot(aes(x = class,y = response_sd)) +
    # geom_text(data = (export_csv %>%
    #                     filter(!is.na(class), subset == 'Prediction') %>%
    #                     group_by(class) %>% count() %>%
    #                     mutate(n = str_c('n = ',formatC(n,format="d", big.mark=",")))),
    #           mapping = aes(x = class, y = max(export_csv %>%
    #                                              filter(!is.na(class), subset == 'Prediction') %>%
    #                                              pull(response_sd)), label = n, vjust = -0.75),
    #           size = 3) +
    # facet_wrap(~subset) +
    labs(x = 'Class',
         y = 'Response Standard Deviation') +
    theme_bw(),
  ncol = 2)

figure_5

ggsave(str_c(export_fp,'figure_5.jpg'),
       figure_5,
       height = 5,
       width = 6.5,
       units = 'in',
       dpi = 600)

## Figure 6 ## Temporal line plots, showing the breakdown of model results and metrics over time. ----
# Temporal plo0ts - grayscale
plot_6a <-
  export_csv %>%
  filter(!is.na(class),
         subset == 'Prediction') %>%
  mutate(facet = 'Model Results') %>%
  mutate(week = as.numeric(str_sub(as.character(Time),5,6))) %>%
  group_by(facet,week,subset,class) %>%
  count() %>%
  left_join(week_assignments %>% filter(year == 2021)) %>%
  ggplot() +
  geom_line(aes(x = week,y = n, color = class, linetype = class), lwd = .4) +
  # facet_wrap(~subset,scales = 'free_y',nrow = 1) +
  facet_wrap(~facet) +
  scale_color_manual(values = c('black','black','gray60','gray60'),
                     name = 'Linetypes:',
                     breaks = c('TP','FP','TN','FN'),
                     labels = c('True positive',
                                'False positive',
                                'True negative',
                                'False negative')) +
  scale_linetype_manual(values = c('solid','41','solid','41','42'),
                        name = 'Linetypes:',
                        breaks = c('TP','FP','TN','FN'),
                        labels = c('True positive',
                                   'False positive',
                                   'True negative',
                                   'False negative')) +
  scale_x_continuous(breaks = weeks$Week,labels = weeks$month) +
  scale_y_continuous(limits = c(0,3000)) +
  labs(x = 'Month', y = 'Number of model results') +
  coord_cartesian(xlim = c(1,52),expand = F) +
  theme_bw() +
  theme(strip.background = element_rect(fill="white"),
        text = element_text(size = 10),
        legend.title = element_text(size = 8),
        legend.position = c(1,1),
        legend.justification = c('right','top'),
        legend.background = element_rect(color = 'gray20', size = .5),
        legend.text = element_text(size = 8),
        legend.key.height = unit(0.18,'in'),
        panel.grid.minor = element_blank())

export_csv %>%
  filter(!is.na(class),
         subset == 'Prediction') %>%
  mutate(facet = 'Model Results') %>%
  mutate(week = as.numeric(str_sub(as.character(Time),5,6))) %>%
  group_by(facet,week,subset,class) %>%
  count() %>%
  left_join(week_assignments %>% filter(year == 2021)) %>%
  write_csv(str_c(export_fp,'values_6a.csv'))

plot_6b <- export_csv %>%
  filter(!is.na(class), subset == "Prediction") %>%
  mutate(week = as.numeric(str_sub(as.character(Time),5,6))) %>%
  group_by(week,subset,class) %>%
  count() %>%
  pivot_wider(names_from = class, values_from = n) %>%
  mutate(Accuracy = (TP + TN)/(TP + TN + FP + FN)*100,
         Precision = TP/(TP + FP)*100,
         Sensitivity = TP/(TP + FN)*100,
         Specificity = TN/(TN + FP)*100) %>%
  dplyr::select(-TP,-FP,-TN,-FN) %>%
  pivot_longer(cols = c(Accuracy, Precision, Sensitivity, Specificity), names_to = 'Metric', values_to = 'n') %>%
  left_join(week_assignments %>% filter(year == 2021)) %>% # filter for 2017 bc it's the only year with 53 weeks
  ggplot() +
  geom_line(aes(x = week,y = n), lwd = .4, color = 'gray30', linetype = '42') +
  facet_wrap(~Metric,nrow = 2) +
  scale_y_continuous(limits = c(20,100), breaks = seq(20,100,20)) +
  scale_x_continuous(breaks = weeks$Week,labels = weeks$month) +
  labs(x = 'Month', y = 'Percent (%)') +
  coord_cartesian(xlim = c(1,52),expand = F) +
  theme_bw() +
  theme(strip.background = element_rect(fill="white"),
        text = element_text(size = 10),
        legend.title = element_text(size = 10),
        panel.grid.minor = element_blank())

export_csv %>%
  filter(!is.na(class), subset == "Prediction") %>%
  mutate(week = as.numeric(str_sub(as.character(Time),5,6))) %>%
  group_by(week,subset,class) %>%
  count() %>%
  pivot_wider(names_from = class, values_from = n) %>%
  mutate(Accuracy = (TP + TN)/(TP + TN + FP + FN)*100,
         Precision = TP/(TP + FP)*100,
         Sensitivity = TP/(TP + FN)*100,
         Specificity = TN/(TN + FP)*100) %>%
  dplyr::select(-TP,-FP,-TN,-FN) %>%
  pivot_longer(cols = c(Accuracy, Precision, Sensitivity, Specificity), names_to = 'Metric', values_to = 'n') %>%
  left_join(week_assignments %>% filter(year == 2021)) %>%
  write.csv(str_c(export_fp,'values_6b.csv'))

ggarrange(plot_6a, plot_6b,
          ncol = 2,
          widths = c(3,4)) -> figure_6

figure_6

ggsave(
  str_c(export_fp,'figure_6.jpg'),
  figure_6,
  height = 5.5,
  width = 6.5,
  units = 'in',
  bg = 'white',
  dpi = 600
)

# Format summary output file ----

ggarrange(

  ggarrange(
    ggparagraph(paste(
      str_c('Model run date: ',Sys.Date()),
      'Mesh information:',
      str_c(' - Max edge: ',round(max_edge/1000, digits = 2), ' km'),
      str_c(' - Cutoff:   ', round(max_edge/denom/1000, digits = 1),' km'),
      str_c(' - ', mesh$n,' nodes'), sep = '\n'
    ),
    lineheight = 1.5,size = 11) +
      theme(plot.margin = unit(c(t = 0.25, r = 0, b = 1, l = 0.25),"in")),

    ggparagraph(paste(' \n',' \n',str_c('Model cutoff:',as.character(round(cutoff[3],3)),sep = ' ')),
                lineheight = 2,size = 11, face = 'bold'),
    ncol = 2, widths = c(5.5,3.0)),


  ggtexttable(table_1, theme = ttheme('light')) %>%
    tab_add_title(text = 'Table 1. Posterior estimates for fixed effects.'),

  ggtexttable(table_2, theme = ttheme('light')) %>%
    tab_add_title(text = 'Table 2. Posterior estimates for random effects'),

  ggarrange(
    ggarrange(ggtexttable(val_cm, theme = ttheme('light')) %>%
                tab_add_title(text = 'Table 3. Validation\nconfusion matrix'),
              ggtexttable(pred_cm, theme = ttheme('light')) %>%
                tab_add_title(text = 'Table 4. Prediction\nconfusion matrix'),
              ncol = 1),
    ggtexttable(table_5, theme = ttheme('light')) %>%
      tab_add_title(text = 'Table 5. Performance metrics'),
    ncol = 2, widths = c(0.4,0.6)
  ),

  ncol = 1,
  heights = c(2,2.5,2.25,4.25),
  align = 'v')

ggsave(
  str_c(export_fp,'summary.pdf'),
  height = 11,
  width = 8.5,
  units = 'in'
)

# Supplemental Figures ----

## Figure S1 ## Mesh figure ----
# Mesh plot - major work in progress
# Rewrite gg function with developmental version from inlabru github, rewrote linewidth as lwd to get it working
# https://github.com/inlabru-org/inlabru/blob/devel/R/ggplot.R 
gg.inla.mesh <- function(data,
                         color = NULL,
                         alpha = NULL,
                         edge.color = "grey",
                         edge.lwd = 0.25,
                         interior = TRUE,
                         int.color = "blue",
                         int.lwd = 0.5,
                         exterior = TRUE,
                         ext.color = "black",
                         ext.lwd = 1,
                         crs = NULL,
                         mask = NULL,
                         nx = 500, ny = 500,
                         ...) {
  requireNamespace("INLA")
  requireNamespace("ggplot2")
  if (is.null(color) && ("colour" %in% names(list(...)))) {
    color <- list(...)[["colour"]]
  }
  if (!is.null(color)) {
    px <- pixels(data, nx = nx, ny = ny)
    A <- INLA::inla.spde.make.A(data, px)
    px$color <- as.vector(A %*% color)
    if (!is.null(alpha)) {
      px$alpha <- as.vector(A %*% alpha)
      gg <- gg(px, mask = mask, alpha = "alpha")
    } else {
      gg <- gg(px, mask = mask)
    }
    
    return(gg)
  }
  
  if (data$manifold == "S2") {
    stop("Geom not implemented for spherical meshes (manifold = S2)")
  }
  if (!is.null(crs)) {
    data <- fm_transform(data, crs = crs)
  }
  
  df <- rbind(
    data.frame(a = data$loc[data$graph$tv[, 1], c(1, 2)], b = data$loc[data$graph$tv[, 2], c(1, 2)]),
    data.frame(a = data$loc[data$graph$tv[, 2], c(1, 2)], b = data$loc[data$graph$tv[, 3], c(1, 2)]),
    data.frame(a = data$loc[data$graph$tv[, 1], c(1, 2)], b = data$loc[data$graph$tv[, 3], c(1, 2)])
  )
  
  colnames(df) <- c("x", "y", "xend", "yend")
  mp <- ggplot2::aes(x = .data$x, y = .data$y, xend = .data$xend, yend = .data$yend)
  msh <- ggplot2::geom_segment(data = df, mapping = mp, color = edge.color, lwd = edge.lwd)
  
  # Outer boundary
  if (exterior) {
    df <- data.frame(
      data$loc[data$segm$bnd$idx[, 1], 1:2],
      data$loc[data$segm$bnd$idx[, 2], 1:2]
    )
    colnames(df) <- c("x", "y", "xend", "yend")
    bnd <- ggplot2::geom_segment(data = df, mapping = mp, color = ext.color, lwd = ext.lwd)
  } else {
    bnd <- NULL
  }
  
  if (interior) {
    # Interior boundary
    df <- data.frame(
      data$loc[data$segm$int$idx[, 1], 1:2],
      data$loc[data$segm$int$idx[, 2], 1:2]
    )
    colnames(df) <- c("x", "y", "xend", "yend")
    if (nrow(df) == 0) {
      int <- NULL
    } else {
      int <- ggplot2::geom_segment(data = df, mapping = mp, color = int.color, lwd = int.lwd)
    }
  } else {
    int <- NULL
  }
  
  # Return combined geomes
  c(msh, bnd, int)
}

figure_s1 <- ggplot()+
  geom_sf(data = conus_bound, color = 'transparent',fill = 'gray90') +
  # geom_sf(data = lakes_buffer,color = "red", fill = "transparent") +
  gg(
    mesh,
    color = NULL,
    alpha = NULL,
    edge.color = "grey62",
    edge.lwd = 0.15,
    interior = TRUE,
    int.color = "blue",
    int.lwd = 0.25,
    exterior = TRUE,
    ext.color = "black",
    ext.lwd = 0.25,
    crs = NULL,
    mask = NULL) +
  annotation_scale(width_hint = .1) +
  annotation_north_arrow(style = north_arrow_minimal,
                         height = unit(1.3,'cm'),
                         pad_y = unit(1.8,'line'),
                         pad_x = unit(-.12,'in')) +
  xlab('Longitude') + ylab("Latitude") +
  theme_bw() +
  theme(text = element_text(size = 12,),
        legend.title = element_text(size = 10),
        axis.text.x = element_text(angle = 45,hjust = 1)) +
  guides(color = 'none')

figure_s1

ggsave(str_c(export_fp,'figure_s1.jpg'),
       figure_s1,
       height = 4,
       width = 6.5,
       units = 'in',
       dpi = 600,
       bg="white")

## Figure S2 ## Standard deviation map ----
# THIS CODE IS NOT CURRENTLY BEING USED IN THE MANUSCRIPT. IT GENERATES THE STANDARD DEVIATION PLOT THAT CORRESPONDS WTIH THE ABOVE PLOT. DO NOT DELETE THIS CODE!

figure_s2 <- ggplot()+
  geom_sf(data = states_bound,fill = 'white', lwd = .25, color = 'gray70') +
  geom_sf(data = conus_bound,fill = 'transparent',lwd = .25) +
  geom_point(data = arrange(plot_data_st_dev,st_dev),
             aes(x = LONG, y= LAT, fill = st_dev, color = st_dev),
             alpha = .7, shape = 21, size = .7) +
  scale_fill_gradientn(name = 'Standard deviation\nof probability',
                       colors = c("#4f718f","#856898","#c57b93",
                                  # "#eb8394",
                                  "#faa594","#ffff8f"),
                       limits = c(0,round(max(plot_data_st_dev$st_dev) + 0.004,digits = 2)), # The 0.004 is to ensure it rounds up
                       breaks = seq(0,round(max(plot_data_st_dev$st_dev) + 0.004,digits = 2),length.out = 5),
                       label = format(seq(0,round(max(plot_data_st_dev$st_dev) + 0.004,digits = 1),length.out = 5),digits = 3)
  ) +
  scale_color_gradientn(name = 'Standard deviation\nof probability',
                        colors =  darken(c("#4f718f","#856898","#c57b93",
                                           # "#eb8394",
                                           "#faa594","#ffff8f"),0.3),
                        limits = c(0,round(max(plot_data_st_dev$st_dev) + 0.004,digits = 2)),
                        breaks = seq(0,round(max(plot_data_st_dev$st_dev) + 0.004,digits = 1),length.out = 5)
  ) +
  facet_wrap(~factor(month,levels = 1:12, ordered= T, labels = month.name),ncol = 3)+
  annotation_scale(width_hint = 0.09,
                   pad_x = unit(0.1,'cm'),
                   pad_y = unit(0.1,'cm'),
                   text_pad = unit(0.1, "cm"),
                   height = unit(0.2,'cm'),
                   data = tibble(month = 10)) +
  annotation_north_arrow(aes(location = 'br'),
                         data = tibble(month = 10),
                         height = unit(.8,'cm'),
                         pad_y = unit(0.1,'cm'),
                         pad_x = unit(-0.17,'in'),
                         style = north_arrow_minimal(text_size = 8)) +
  ylab('Latitude') +
  xlab('Longitude') +
  theme_bw() +
  theme(text = element_text(size = 10),
        # legend.title = element_text(size = 8),
        legend.position = 'bottom',
        legend.text = element_text(angle = 45,hjust = 1),
        legend.title = element_text(vjust = 1),
        axis.text.x = element_text(angle = 45,hjust = 1),
        # axis.title.y = element_blank(),
        strip.background = element_rect(fill = 'white'),
        strip.text = element_text(margin = margin(t = 2, r = 0,
                                                  b = 2, l = 0, unit = "pt"))) +
  guides(color = 'none')

figure_s2

ggsave(str_c(export_fp,'figure_s2.jpg'),
       figure_s2,
       height = 7,
       width = 6.5,
       units = 'in',
       dpi = 600,
       bg="white")

## Figure S3 ## Prevalance plot ----

export_csv %>%
  filter(!is.na(class), subset == "Prediction") %>%
  mutate(week = as.numeric(str_sub(as.character(Time),5,6))) %>%
  group_by(week,subset,class) %>%
  count() %>%
  pivot_wider(names_from = class, values_from = n) %>%
  mutate(Prevalance = (TP + FN)/(TP + FP + TN + FN)*100) %>%
  dplyr::select(-TP,-FP,-TN,-FN) %>%
  # pivot_longer(cols = c(Accuracy, Precision, Sensitivity, Specificity), names_to = 'Metric', values_to = 'n') %>%
  left_join(week_assignments %>% filter(year == 2021)) %>% 
  ggplot() +
  geom_line(aes(x = week,y = Prevalance), lwd = .4, color = 'gray30') +
  # facet_wrap(~Metric,nrow = 2) +
  scale_y_continuous(limits = c(0,40), breaks = seq(0,40,10)) +
  scale_x_continuous(breaks = weeks$Week,labels = weeks$month) +
  labs(x = 'Month', y = 'Prevalance (%)') +
  coord_cartesian(xlim = c(1,52),expand = F) +
  theme_bw() +
  theme(strip.background = element_rect(fill="white"),
        text = element_text(size = 10),
        panel.grid.minor = element_blank())


ggsave(
  str_c(export_fp,'figure_s3.jpg'),
  height = 5,
  width = 5,
  units = 'in',
  dpi = 600
)

## Figure S4 ## Ratings curve ----
# for some reason this doesn't seem to work

# Set up plot
plot.new()
plot(validation_roc_performance_instance,colorize = F, lty = 1, cex.lab = 1.2, xlim = c(0,1), ylim = c(0,1), xaxs="i", yaxs="i")
points(x = 1.01 - cutoff[2], y = cutoff[1], cex = 2, pch = 20, col = 'black')
abline(a=0,b=1)
roc_plot <- recordPlot()
plot.new()

gg_roc_plot <- ggdraw(roc_plot)

ggsave(str_c(export_fp,'figure_s4.jpg'),
       gg_roc_plot,
       height = 5,
       width = 5,
       units = 'in',
       dpi = 600)

# T tests ----

# Training dataset
t.test(
  filter(export_csv, subset == 'Training', class == 'TP')$response_prob,
  filter(export_csv, subset == 'Training', class == 'FP')$response_prob
) # p-value < 2.2e-16

t.test(
  filter(export_csv, subset == 'Training', class == 'TN')$response_prob,
  filter(export_csv, subset == 'Training', class == 'FN')$response_prob
) # p-value < 2.2e-16

# Validation dataset
t.test(
  filter(export_csv, subset == 'Validation', class == 'TP')$response_prob,
  filter(export_csv, subset == 'Validation', class == 'FP')$response_prob
) # p-value < 2.2e-16

t.test(
  filter(export_csv, subset == 'Validation', class == 'TN')$response_prob,
  filter(export_csv, subset == 'Validation', class == 'FN')$response_prob
) # p-value < 2.2e-16

# Prediction dataset
t.test(
  filter(export_csv, subset == 'Prediction', class == 'TP')$response_prob,
  filter(export_csv, subset == 'Prediction', class == 'FP')$response_prob
) # p-value < 2.2e-16

t.test(
  filter(export_csv, subset == 'Prediction', class == 'TN')$response_prob,
  filter(export_csv, subset == 'Prediction', class == 'FN')$response_prob
) # p-value < 2.2e-16

# Uncertainty analysis ----

## Prep CI data ----
## Pull input observations for prediction dataset
dn_observations <- input %>% filter(subset == 'prediction' & !is.na(Bloom_adjusted)) %>% pull(Cyano_adjusted)

## Write a function to convert DNs to CIcyano values
scale_dns <- function(dn) {
  ifelse(dn == 0,
         0,
         (10^((3/250)*dn - 4.2))) %>% return()
}

## Convert DNs to CIcyano
ci_observations <- scale_dns(dn_observations)

## Check work
summary(dn_observations); summary(ci_observations)

## Calculate bloom threshold for CIcyano
bloom_threshold <- scale_dns(97)

## Introduce uncertainty ----

## Write a function to add uncertainty to the ci_observations
add_uncertainty <- function(uncertainty_increments){
  
  jumbled_observations <- rep(NA,length(ci_observations))
  
  uncertainty <- rnorm(length(which(ci_observations > 0)), 0, 0.0001*uncertainty_increments)
  
  j <- 1
  
  for(i in 1:length(ci_observations)) {
    
    if(is.na(ci_observations[i]) & is.na(prediction_observations[i])) {
      jumbled_observations[i] <- NA 
    } else if(is.na(ci_observations[i]) & !is.na(prediction_observations[i])) {
      jumbled_observations[i] <- 0 # These observations are coded as 'no bloom' because they overlap with the snow/ice mask
    } else if(ci_observations[i] == 0) {
      jumbled_observations[i] <- 0 # These are 0 because there is no bloom in the imagery
    } else {
      jumbled_observations[i] <- ci_observations[i] + uncertainty[j]
      
      j <- j + 1
    }
  }
  
  as.numeric(ifelse(jumbled_observations >= bloom_threshold, T, F)) %>% return()
  
}

jumbled_1 <- sapply(rep(1,1000), add_uncertainty)
jumbled_2 <- sapply(rep(2,1000), add_uncertainty)
jumbled_4 <- sapply(rep(4,1000), add_uncertainty)
jumbled_8 <- sapply(rep(8,1000), add_uncertainty)
jumbled_16 <- sapply(rep(16,1000), add_uncertainty)

## Table S1 ## Summarize the number of observations changed ----
tibble(
  `Uncertainty introduced` = c(1,2,4,8,16)*0.0001,
  `Number of observations altered` = c(
    length(which(jumbled_1 != prediction_observations)),
    length(which(jumbled_2 != prediction_observations)),
    length(which(jumbled_4 != prediction_observations)),
    length(which(jumbled_8 != prediction_observations)),
    length(which(jumbled_16 != prediction_observations))
  )
) %>%
  mutate(`Percent of observations altered` = round(`Number of observations altered`/length(jumbled_1)*100, digits = 3)) -> table_s1

## Table S2 ## Generate confusion matrices ----
prediction_matrix <- matrix(rep(prediction_response_na_omit,1000),ncol = 1000)

cbind(generate_cm(responses = prediction_response_na_omit,observations = prediction_observations),
      generate_cm(prediction_matrix,jumbled_1)/1000,
      generate_cm(prediction_matrix,jumbled_2)/1000,
      generate_cm(prediction_matrix,jumbled_4)/1000,
      generate_cm(prediction_matrix,jumbled_8)/1000,
      generate_cm(prediction_matrix,jumbled_16)/1000) -> table_s2

## Table S3 ## Generate performance statistics ----

generate_stats(responses = prediction_response_na_omit,observations = prediction_observations) %>%
  as.data.frame() %>%
  rownames_to_column() %>%
  rename(Metric = rowname,
         "Unadjusted" = V1) %>%
  full_join(generate_stats(prediction_matrix,jumbled_1) %>%
              as.data.frame() %>%
              rownames_to_column() %>%
              rename(Metric = rowname,
                     "St. Dev. = 0.0001" = V1)) %>%
  full_join(
    generate_stats(prediction_matrix,jumbled_2) %>%
      as.data.frame() %>%
      rownames_to_column() %>%
      rename(Metric = rowname,
             "St. Dev. = 0.0002" = V1)
  ) %>%
  full_join(
    generate_stats(prediction_matrix,jumbled_4) %>%
      as.data.frame() %>%
      rownames_to_column() %>%
      rename(Metric = rowname,
             "St. Dev. = 0.0004" = V1)
  ) %>%
  full_join(
    generate_stats(prediction_matrix,jumbled_8) %>%
      as.data.frame() %>%
      rownames_to_column() %>%
      rename(Metric = rowname,
             "St. Dev. = 0.0008" = V1)
  ) %>%
  full_join(
    generate_stats(prediction_matrix,jumbled_16) %>%
      as.data.frame() %>%
      rownames_to_column() %>%
      rename(Metric = rowname,
             "St. Dev. = 0.0016" = V1)
  ) -> table_s3

table_s3[,2:7] <- round(table_s3[,2:7], digits = 3)

## Save results as PDF ----
# Format Table S2, confusion matrices
tab_body_up <- tableGrob(rbind(table_s2[,1:6], rep('',6)), theme = ttheme('light', base_size = 8))
tab_body_dn <- tableGrob(table_s2[,7:12], theme = ttheme('light', base_size = 8))
tab_header_up <- tableGrob(table_s2[,1:3], rows = NULL,cols = c('Unadjusted',
                                                             'St. Dev. = 0.0001',
                                                             'St. Dev. = 0.0002'),
                                                             # 'St. Dev. = 0.0004',
                                                             # 'St. Dev. = 0.0008',
                                                             # 'St. Dev. = 0.0016'),
                        theme = ttheme_minimal(base_size = 8))
tab_header_dn <- tableGrob(table_s2[,4:6], rows = NULL,cols = c(# 'Unadjusted',
                                                                # 'St. Dev. = 0.0001',
                                                                # 'St. Dev. = 0.0002',
                                                                'St. Dev. = 0.0004',
                                                                'St. Dev. = 0.0008',
                                                                'St. Dev. = 0.0016'),
                           theme = ttheme_minimal(base_size = 8))

tab_up <- gtable_combine(tab_header_up[1,], tab_body_up, along=2)
tab_up$widths <- rep(max(tab_up$widths), length(tab_up$widths))

tab_dn <- gtable_combine(tab_header_dn[1,], tab_body_dn, along=2)
tab_dn$widths <- rep(max(tab_up$widths), length(tab_up$widths))

tab_up$layout[1:3 , c("l", "r")] <- list(seq(2,6,2),seq(3,7,2))
tab_dn$layout[1:3 , c("l", "r")] <- list(seq(2,6,2),seq(3,7,2))

tab <- gtable_combine(tab_up,tab_dn, along = 2)

# Visualize
# grid.newpage()
# grid.draw(tab %>%
#             tab_add_hline(at.row = c(2,4,7,tab_nrow(tab))) %>%
#             table_cell_bg(row = c(3:4,8:9), column = c(2:3,6:7),
#                           fill="gray95", color = 'gray95'))

# Arrange tables
ggarrange(
  ggparagraph(paste(
    str_c('Model run date: ',Sys.Date()),
    str_c("\nThe prediction dataset, containing the final year's CIcyano observations, were adjusted according to N(0,uncertainty), with uncertainty equal to: 0.0001, 0.0002, 0.0004, 0.0008, and 0.0016. Each uncertainty threshold was applied to generate 1000 adjusted prediction datasets each. Resulting values were then converted back to bloom/no bloom according the the bloom threshold (DN = 97, the CIcyano equivalent to the WHO level-1 health alert for cyanoHABs).The number of changed values for each uncertainty dataset were totaled. Averaged confusion matrices and summary statistics were also presented.")),
  lineheight = 1.5,size = 11) +
    theme(plot.margin = unit(c(t = 0.5, r = 0, b = 1, l = 0.5),"in")),
  
  ggtexttable(table_s1, theme = ttheme('light', base_size = 8))%>%
    tab_add_title(text = 'Table S1. Number and percent of observations changed with uncertainty.', size = 11),

  ggdraw(ggplot() + theme_minimal()) +
    # draw_grob(tab %>%
    #             tab_add_hline(at.row = c(2,tab_nrow(tab))) %>%
    #             table_cell_bg(row = 3:4, column = c(2:3,6:7,10:11),
    #                           fill="gray95", color = 'gray95')),
    draw_grob(tab %>%
                tab_add_hline(at.row = c(2,4,7,tab_nrow(tab))) %>%
                table_cell_bg(row = c(3:4,8:9), column = c(2:3,6:7),
                              fill="gray95", color = 'gray95') %>%
                tab_add_title(text = 'Table S2. Confusion matrices from uncertainty analysis.', size = 11)),
  
  ggtexttable(table_s3, theme = ttheme('light', base_size = 8)) %>%
    tab_add_title(text = 'Table S3. Summary statistics from uncertainty analysis.', size = 11),
  
  ncol = 1,
  heights = c(2,2,2.5,2.25),
  align = 'v')

ggsave(
  str_c(export_fp,'uncertainty.pdf'),
  height = 11,
  width = 8.5,
  units = 'in'
)


# Wrap it up ----
#### end
ot <- Sys.time() - t_init
print(ot)

unlink(tempdir(),recursive = T)

# Save workspace
save.image(str_c(export_fp,'workspace.RData'))

