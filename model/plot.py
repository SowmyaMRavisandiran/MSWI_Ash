#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 15 16:59:45 2024

@author: marriyapillais
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
file_name = "Data_Structure_Task4.1_Task4.2_BAU.csv"


ash_data = pd.read_csv(file_name)

country_codes = pd.read_csv('data_saved/Country_Codes.csv')

ash_data_obs = ash_data.loc[ash_data["Scenario"]=='OBS']
obs_ba = ash_data_obs.loc[ash_data_obs["Substance main parent"]=='19 01 11*']

# Plotting
plt.figure(figsize=(10, 6))

for index,row in country_codes[:-1].iterrows():
    data = obs_ba.loc[obs_ba['Country']==row['NUTS_code']]

    plt.plot(data['Year'], data['Value'], label= row['Country'])

plt.xlabel('Year')
plt.ylabel('Ash Quantities in tonnes')
plt.title('Incineration Bottom Ash Quantities by Country')
plt.legend(loc='upper left', bbox_to_anchor=(1.05, 1), title="Countries", ncol=2, fontsize='small')
plt.grid(True)

# Adjust layout to make room for the legend
plt.tight_layout(rect=[0, 0, 0.85, 1])

plt.show()


plt.figure(figsize=(10, 6))
eu_data = ash_data.loc[(ash_data['Country']=='EU27+4')]
for i in ash_data['Stock/Flow ID'].unique():
    data = eu_data.loc[eu_data['Stock/Flow ID']==i]

    plt.plot(data['Year'], data['Value'], label= i)

plt.xlabel('Year')
plt.ylabel('Ash Quantities in tonnes')
plt.title('Projections of Ash quantities for EU27+4 (BAU)')
plt.legend(loc='center right', title="Ash Type")

# Adjust layout to make room for the legend
plt.tight_layout(rect=[0, 0, 0.85, 1])

plt.show()
