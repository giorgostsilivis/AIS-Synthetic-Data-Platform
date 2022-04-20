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




def kinematic():
  filename='project/static/new.csv'
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
      vessel.to_csv(filename, index=False)

  labeling(filename)
  vessel=pd.read_csv(filename)
  the_trips = list(set(vessel['trip']))
  for i in range(0,len(the_trips)):
    if the_trips[i] != 'Port':
      the_trips[i] = int(the_trips[i])
    else:
      the_trips[i] = -10
  the_trips = sorted(the_trips)

  def fake_traj(vessel_trip):
    # sample1 = vessel_trip
    # sample1 = sample1.reset_index(drop = True)
    # WGS --> UTM
    import utm
    import numpy as np
    
    sample1 = vessel_trip
    sample1 = sample1.reset_index(drop = True)
    
    sample1['X'] = np.nan #easting
    sample1['Y'] = np.nan #northing
    sample1['zone1'] = np.nan
    sample1['zone2'] = np.nan
    for u in range(0,len(sample1)):
      uu = utm.from_latlon(sample1["latitude"][u], sample1["longitude"][u])
      sample1['X'][u] = uu[0]
      sample1['Y'][u] = uu[1]
      sample1['zone1'][u] = uu[2]
      sample1['zone2'][u] = uu[3]
  
    # Mock time
    import random
    from datetime import datetime, timedelta
    
    a = sample1['t']
    b = pd.to_datetime(a)
    b = b.reset_index(drop = True)
    simt = b
    for i in range (0, len(b)-1):
      j = b[i+1] - b[i]
      simt[i] = b[i] + timedelta(seconds = int(random.uniform(0,j.seconds)))
    #epeidh to kanei ana trip vgazei oti na nai to time se olh thn troxia... gia auto ekana tis 2 grammes comment apo katw
    # simt = simt + timedelta(minutes = int(random.uniform(-480,480)))
    # simt = simt + timedelta(days = int(random.uniform(-45,45)))
    
    dtime = []
    for i in range (1, len(simt)):
      k = simt[i] - simt[i-1]
      dtime.append(k.seconds)
    
    dtime.append(0)
    sample1['simt'] = simt
    sample1['dt'] = dtime
    
    #speed
    import math
    for i in range(0,len(sample1.sog)):
      if math.isnan(sample1.sog[i]): 
        continue
      else:
        sample1.sog[i] = sample1.sog[i] * 0.51 #knots to m/s
  
    #slon,slat
    #ta sin,cos pane anapoda epeidh einai azimouthia fi = p/2 - theta
    sample1['simX'] = sample1.X + sample1.sog.interpolate(method= 'linear',limit_direction='both')*np.sin(np.radians(sample1.cog.interpolate(method= 'linear',limit_direction='both')))*sample1.dt
    sample1['simY'] = sample1.Y + sample1.sog.interpolate(method= 'linear',limit_direction='both')*np.cos(np.radians(sample1.cog.interpolate(method= 'linear',limit_direction='both')))*sample1.dt 
    sample1['slon'] = np.nan
    sample1['slat'] = np.nan
    # sample1['slon'], sample1['slat'] = pp(sample1['simX'].values, sample1['simY'].values, inverse=True)
    for i in range(0,len(sample1)):
      u = (sample1['simX'][i],sample1['simY'][i],sample1['zone1'][i],sample1['zone2'][i])
      sample1['slon'][i], sample1['slat'][i] = utm.to_latlon(*u)[1],utm.to_latlon(*u)[0]
    
    #simspeed
    sample1['simspeed'] = sample1.sog
    for i in range(0,len(sample1.sog)):
      if sample1['sog'][i] == 0:
        sample1['simspeed'][i] = sample1.sog[i]
      elif math.isnan(sample1.sog[i]):
        sample1.simspeed[i] = math.nan
      else:
        sample1.simspeed[i] = abs(int(sample1.sog[i] * 1.96) + 0.1*int(random.uniform(-3,3)))
    
    #angles
    from geographiclib.geodesic import Geodesic
    ...
    def get_bearing(lat1, lat2, long1, long2):
        brng = Geodesic.WGS84.Inverse(lat1, long1, lat2, long2)['azi1']
        return brng
    
    sample1['simcourse'] = sample1['cog']
    for i in range(0,len(sample1.cog)-1):
      if math.isnan(sample1.cog[i]):
        continue
      else:
        # parakatwv o typos apo to arthro tou Giannh doulepse kala alla se orismenes grammes apexei arketa
        # xi = math.cos(sample1.slat[i]) * math.sin(sample1.slon[i]-sample1.slon[i-1])
        # yi = math.cos(sample1.slat[i-1])*math.sin(sample1.slat[i]) - math.sin(sample1.slat[i-1])*math.cos(sample1.slat[i])*math.cos(sample1.slon[i]-sample1.slon[i-1])
        # sample1.simcourse[i] = np.rad2deg(math.atan2(xi,yi))
        # sample1.simcourse[i] = round(sample1.course[i] + int(random.uniform(-2,2)),1)
        #calc bearing angle
    
        
        sample1['simcourse'][i] = get_bearing(sample1['slat'][i],sample1['slat'][i+1],sample1['slon'][i],sample1['slon'][i+1])
    sample1['simcourse'][len(sample1['cog'])-1] = sample1['simcourse'][len(sample1['cog'])-2]
    
    #id
    from faker import Faker
    faker = Faker()
    #id
    sample1['fake_shipid'] = faker.uuid4()
    
    #final drop
    sample1 = sample1.replace([np.inf, -np.inf], np.nan)
    # sample1 = sample1.drop(columns=['heading','course','speed','lon','lat','X','Y','simX','simY','dt','t','shipid'])
    sample1 = sample1[['simt','fake_shipid','slon','slat','simcourse','simspeed']]
    
    # #final drop
    # sample1 = sample1.replace([np.inf, -np.inf], np.nan)
    # sample1 = sample1.drop(columns=['heading','course','speed','lon','lat','X','Y','simX','simY','dt','t','shipid'])
    # sample1 = sample1[['simt','fake_shipid','slon','slat','simheading','simcourse','simspeed','shiptype','destination']]
  
    return sample1
  

  def outliers_killer(vessel_trip,sample1):
    lat_max = vessel_trip['latitude'].max()
    lat_min = vessel_trip['latitude'].min()
    lon_max = vessel_trip['longitude'].max()
    lon_min = vessel_trip['longitude'].min()
    for i in range(1,len(sample1)):
      if sample1['slat'][i] < lat_min:
        sample1['slat'][i] = sample1['slat'][i-1]
      elif sample1['slat'][i] > lat_max:
        sample1['slat'][i] = sample1['slat'][i-1]
      if sample1['slon'][i] < lon_min:
        sample1['slon'][i] = sample1['slon'][i-1]
      elif sample1['slon'][i] > lon_max:
        sample1['slon'][i] = sample1['slon'][i-1]
    return sample1

  from scipy.signal import savgol_filter
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
      sample1= fake_traj(vessel_trip)
      #savgol
      sample1['slon'] = savgol_filter(sample1['slon'], 9, 3) # window size 51, polynomial order 3
      sample1['slat'] = savgol_filter(sample1['slat'], 9, 3) # window size 51, polynomial order 3
      sample1 = outliers_killer(vessel_trip,sample1)
      vessel_new = vessel_new.append(sample1, ignore_index=True)
    # except:
    #   print(i)
  #id
  from faker import Faker
  faker = Faker()
  #id
  vessel_new['fake_shipid'] = faker.uuid4()
  vessel_new[['slon','slat']].to_csv('project/static/kin_pred_vessel.csv',index=False)

