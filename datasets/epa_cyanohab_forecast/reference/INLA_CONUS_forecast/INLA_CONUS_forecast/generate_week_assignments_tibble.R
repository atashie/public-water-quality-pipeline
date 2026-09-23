# This script is a reference for how I generated the week assignments tibbles used throughout the workflow
# I'm setting this aside for future reference forif/when we expand the model past 2019
# Author: Natalie Von Tress
# Date created: 5/16/22

# Load packages
library(tidyverse)
library(lubridate)
library(MESS)

# From Blake: The NASA weekly start the first Sunday of the calendar year and run Sunday to Saturday. 
# Assign week numbers to dates
tibble(
  # Starting with the first Sunday of 2016 
  date = seq(as.Date("2016-01-03"),as.Date("2022-12-31"),by="1 day"), 
  # Pull the week day from the date
  wday = wday(date),
  # Create a "trigger" based on whether the date is the first Sunday of the year
  week_count_start = ifelse(month(date) == 1 & day(date) < 8 & wday == 1, 1, 0),
  # Assign groups based on the trigger
  group = cumsum(week_count_start),
  # Assign weeks, set to reset every "triggered" day
  week = ave(x = wday,group,
             FUN = function(x) cumsumbinning(x,threshold = sum(1:7)))
) %>% 
  mutate(year = as.numeric(as.character(factor(group,levels = min(group):max(group),labels = min(year(date)):max(year(date)))))) %>%
  dplyr::select(date,year,week) -> week_assignments

write_csv(week_assignments,'data/week_assignments.csv')
