import pandas as pd
import math
import random
import numpy as np
import os
# import matplotlib.pyplot as plt


def resample():


    df = pd.read_csv('project/static/vessel.csv')
    
    csv_list = []
    for  i in os.listdir('project/static'):
      if 'vessel' in i:
        csv_list.append(i)
    
    
    def labeling(filename):
      labelist = []
      vessel=pd.read_csv(filename)
      vessel['t'] = pd.to_datetime(vessel.t)
      for i in range(0,len(vessel)):
          if vessel['sog'][i] < 0.5:
            labelist.append('Port')
          else:
            labelist.append('Route')
      vessel['label'] = labelist
    
      trip = []
      port_counter = 0
      route_counter = 0
      for i in range(0,len(vessel)):
        if vessel['label'][i] == 'Route' and vessel['label'][i-1] == 'Port':
          route_counter = route_counter + 1
        if vessel['label'][i] == 'Port':
          trip.append('Port')
        else:
          trip.append(route_counter)
      
      vessel['trip'] = trip
      vessel.to_csv('project/static/new.csv', index=False)
    
    for i in csv_list:
      labeling('project/static/vessel.csv')
    
    #-------------------------------------------------
    
    vessel = pd.read_csv('project/static/new.csv')
    
    the_trips = list(set(vessel['trip']))
    for i in range(0,len(the_trips)):
      if the_trips[i] != 'Port':
        the_trips[i] = int(the_trips[i])
      else:
        the_trips[i] = -10
    the_trips = sorted(the_trips)
    
    
    
    def resampler(vessel_trip):
      realset1 = vessel_trip[['t','latitude','longitude']]
      realset1= realset1.set_index('t')
      realset1.index = pd.to_datetime(realset1.index)
      #linear,polynomial,time recommended
      
      #sp = realset1.resample('1S').interpolate(method='polynomial', order=3)
      sp = realset1.resample('1S').interpolate(method='linear')
      
    #   sp1 = realset1.resample('1S').interpolate(method='pchip')
      sp = sp.dropna()
    #   sp1 = sp1.dropna()
      sp = sp.drop(sp.sample(len(sp)-len(realset1)).index) # arithmos grammwn pou thes na petakseis
    #   sp1 = sp1.drop(sp1.sample(len(sp1)-len(realset1)).index) # arithmos grammwn pou thes na petakseis
      return sp


    # from scipy.signal import savgol_filter
    vessel_new = pd.DataFrame(columns=['simt', 'fake_shipid', 'slon','slat','simcourse','simspeed'])
    vessel_old  = pd.DataFrame()
    for i in the_trips:
    # for i in (4,5):
      # try:
    # vessel_trip = vessel[vessel['trip'] == '111']
      vessel_trip = vessel[vessel['trip'] == str(i)]
      # print(i,len(vessel_trip))
      if len(vessel_trip) > 10:
        vessel_old = vessel_old.append(vessel_trip, ignore_index=True)
        sample1= resampler(vessel_trip)
        #savgol
        # sample1['longitude'] = savgol_filter(sample1['longitude'], 9, 3) # window size 51, polynomial order 3
        # sample1['latitude'] = savgol_filter(sample1['latitude'], 9, 3) # window size 51, polynomial order 3
        # sample1 = outliers_killer(vessel_trip,sample1)
        vessel_new = vessel_new.append(sample1, ignore_index=True)
    
    vessel_new[['longitude','latitude']].to_csv('project/static/pred_vessel.csv',index=False)