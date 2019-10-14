#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
df = pd.read_csv("NYPD_Complaint_Data_Historic.csv", low_memory=False)


# In[2]:


df.head()


# In[4]:


df = df[~((df['CMPLNT_FR_DT'].isnull()) |(df['CMPLNT_FR_TM'].isnull()))]


# In[5]:


df.info()


# In[6]:


def DTTM(dt,tm):
    return dt + ' ' + tm


# In[7]:


result = []
for dt, tm in zip(df['CMPLNT_FR_DT'], df['CMPLNT_FR_TM']):
    result.append(DTTM(dt,tm))


# In[8]:


df['CMPLNT_FR'] = result


# In[9]:


#Convert string data to datetime object
import datetime
df['CMPLNT_FR'] = df['CMPLNT_FR'].apply(lambda x:datetime.datetime.strptime(x,'%m/%d/%Y %H:%M:%S'))


# In[10]:


#Get weekday and hour from date
df['day_of_week'] = df['CMPLNT_FR'].apply(lambda x: x.isoweekday())
df['hour'] = df['CMPLNT_FR'].apply(lambda x: x.hour)


# In[11]:


get_ipython().run_line_magic('matplotlib', 'inline')
import matplotlib.pyplot as plt
import seaborn as sns
plt.style.use('seaborn')


# In[154]:


#Changes in the number of crimes at different times of the day
plt.xticks(range(0,24))
df.groupby(['hour']).size().plot(kind="line",figsize=(12,6))


# In[13]:


#Changes in the number of crimes at different day of the week
df.groupby(['day_of_week']).size().plot(kind="line",figsize=(12,6))


# In[14]:


labels = list(df['BORO_NM'].unique())
sizes = df[~df['BORO_NM'].isnull()].groupby(['BORO_NM']).size()
explode = (0.05,0.05,0.05,0.05,0.05)
 
plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, pctdistance=0.85, explode = explode)

centre_circle = plt.Circle((0,0),0.70,fc='white')
fig = plt.gcf()
fig.gca().add_artist(centre_circle)
plt.tight_layout()
plt.show()


# In[15]:


df.groupby(['day_of_week', 'hour']).size().unstack().plot(kind="bar",figsize=(24,24))


# In[16]:


df.info()


# In[144]:


def createZoneTable(zone_factor,westlimit=-74.2635, southlimit=40.4856, eastlimit=-73.7526, northlimit=40.9596):
    zone_table = list()
    #Your code goes here
    logi = (eastlimit - westlimit) / zone_factor
    lati = (northlimit - southlimit) / zone_factor
    i = 0
    j = 0
    for lat in range(zone_factor):
        westlimit = -74.2635
        j = 0
        for log in range(zone_factor):
            lola = [[westlimit,southlimit],[westlimit+logi,southlimit],[westlimit+logi,southlimit+lati],[westlimit,southlimit+lati],[westlimit,southlimit]]
            zone = ((str(i)+"_"+str(j)),lola)
            zone_table.append(zone)
            j += 1
            westlimit += logi
        southlimit+= lati
        i += 1
    return zone_table


# In[145]:


def createGeoJsonObject(zone_table):
    zone_data_dict = dict()
    zone_data_dict['type'] = 'FeatureCollection'
    zone_data_dict_features = list()
    zone_data_dict['features'] = zone_data_dict_features
    
    #Your code goes here
    for i in range(len(zone_table)):
        subzone = dict()
        subzone["geometry"] = {'coordinates': [zone_table[i][1]], 'type': 'Polygon'}
        subzone["properties"] = {'zone_id': zone_table[i][0]}
        subzone["type"] = 'Feature'
        zone_data_dict_features.append(subzone)   
    
    return zone_data_dict


# In[146]:


#Sat Zone factor to 30
zone_table = createZoneTable(30)


# In[147]:


def get_zone(lat,lon,zone_table):
    
    #Your code goes here
    for i in range(len(zone_table)):
        while (lon > zone_table[i][1][0][0]) & (lon < zone_table[i][1][1][0]) & (lat > zone_table[i][1][1][1]) & (lat < zone_table[i][1][2][1]):
            return zone_table[i][0]
            break


# In[148]:


df['zone'] = df.apply(lambda x:get_zone(x["Latitude"],x["Longitude"],zone_table),axis=1)


# In[149]:


zones = df[~df['zone'].isnull()].groupby('zone')
counts = pd.DataFrame(zones.size())
counts.rename(columns={0:"counts"},inplace=True)
counts.reset_index(level=0,inplace=True)


# In[150]:


counts.head()


# In[151]:


import folium
new_map = folium.Map(location = [40.4856, -74.2635],zoom_start=10)
new_map.choropleth(geo_data=createGeoJsonObject(zone_table), data=counts,
             columns=['zone','counts'],
             key_on='feature.properties.zone_id',
             fill_color='RdYlGn', fill_opacity=0.7, line_opacity=0.8,
             legend_name='Distribution of Client')


# In[155]:


new_map.save('new_map.html')


# In[152]:


new_map

