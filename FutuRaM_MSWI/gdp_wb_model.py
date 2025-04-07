#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 14:43:26 2024

@author: marriyapillais
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#wb_gdp = pd.read_csv('data_downloads/API_NY/API_NY.GDP.PCAP.KD_DS2_en_csv_v2_120.csv', sep=',',skiprows=1, header=1)
#cyp_mlt_gdp=wb_gdp.loc[wb_gdp['Country Name'].isin(['Cyprus','Malta'])]


#%% Recalibrating WB model

#%%% Data extractions and Cleaning
# Getting MSW/cap data from oecd and extracting the required information
msw_oecd = pd.read_csv('data_downloads/msw_oecd.csv')
oecd_vars = ["REF_AREA","Reference area", "Measure","UNIT_MEASURE","TIME_PERIOD", "OBS_VALUE"]
msw_oecd = msw_oecd[oecd_vars]
msw_cap = msw_oecd.loc[msw_oecd["UNIT_MEASURE"]=='KG_PS']
msw_cap.drop(['Measure','UNIT_MEASURE'], axis = 'columns', inplace = True)
msw_cap.rename(columns={'TIME_PERIOD':'TIME','OBS_VALUE':'MSW/CAP'}, inplace = True)

#Dropping rows with country groups like OECD
cou_groups=['OECDE','OECDA','EU27_2020','OECDSO','OECD']
msw_cap= msw_cap.loc[~msw_cap['REF_AREA'].isin(cou_groups)]


#Getting GDP PPP 2015/cap
gdp_cap=pd.read_csv('data_downloads/OECD_gdp.csv')
gdp_cap=gdp_cap.loc[gdp_cap['VARIABLE']=='GDPVD_CAP']
gdp_cap=gdp_cap.loc[~gdp_cap['LOCATION'].isin(['G20', 'EA17', 'OECD', 'G20ADV', 'G20EME','OECDG20', 'G7M'])]
gdp_cap = gdp_cap[['LOCATION','TIME','Value']]
gdp_cap.rename(columns={'LOCATION':'REF_AREA','Value':'GDPCAP_USD'}, inplace = True)

#%%% Modelling
#Combining the two datasets
msw_gdp_cap = pd.merge(msw_cap, gdp_cap, on = ['TIME','REF_AREA'], how ='inner')
msw_gdp_cap.drop_duplicates(inplace=True)


#Calibrating the WB formula
def fit_fun(x,fit):
    #for the specified parameters, this function returns the log fit 
    return(fit[2]+fit[1]*np.log(x)+fit[0]*np.log(x)*np.log(x))

fit = np.polyfit(np.log(msw_gdp_cap['GDPCAP_USD']), msw_gdp_cap['MSW/CAP'], 2)
wb_fit = [29.43, -419.73 , 1647.41]
"""
Obtained fit: array([18.52534507, -176.90063059, 318.11762839])
WB fit: [29.43, -419.73 , 1647.41]
"""

def projections(reg_msw_data,reg_gdp_data, fit, base_year, column_names, proj_year):
    time, gdp_cap, msw_cap = column_names
    proxy_base = fit_fun(reg_gdp_data.loc[reg_gdp_data[time]==base_year][gdp_cap], fit).to_numpy()
    actual_base = reg_msw_data.loc[reg_msw_data[time]==base_year][msw_cap].to_numpy()
    proxies = fit_fun(reg_gdp_data.loc[reg_gdp_data[time].isin(np.arange(base_year+1,proj_year+1))][gdp_cap], fit)
    projections = proxies /proxy_base * actual_base
    return(projections)

#%%% Plotting Proxies and Projections

#Plot of projected waste generation

proj_data = pd.DataFrame(columns=['GDPCAP_USD','Projections'])
base_year = 2016

for region in msw_gdp_cap['REF_AREA'].unique():
    reg_data = msw_gdp_cap.loc[msw_gdp_cap['REF_AREA']==region]
    proxy_base = fit_fun(reg_data.loc[reg_data['TIME']==2016]['GDPCAP_USD'],fit).to_numpy()
    if proxy_base.size==0:
        #print(reg_data)
        #print(region)
        continue
    reg_data['Projections'] = projections(reg_data[['TIME','MSW/CAP']], reg_data[['TIME','GDPCAP_USD']], fit, 2016, ['TIME', 'GDPCAP_USD','MSW/CAP'], 2021)
    reg_data['WB_Projections'] = projections(reg_data[['TIME','MSW/CAP']], reg_data[['TIME','GDPCAP_USD']], wb_fit, 2016, ['TIME', 'GDPCAP_USD','MSW/CAP'], 2021)
    
    reg_data = reg_data.loc[reg_data['TIME'].isin(np.arange(2017,2022))]
    reg_data['Proxies'] = fit_fun(reg_data['GDPCAP_USD'],fit)
    reg_data['WB_Proxies'] = fit_fun(reg_data['GDPCAP_USD'], wb_fit)
    proj_data = pd.concat([proj_data, reg_data[['GDPCAP_USD','Projections','WB_Projections']]])

#plt.plot(msw_gdp_cap['GDPCAP_USD'],msw_gdp_cap['MSW/CAP'],'.',label ='Observed Data')
#plt.plot(msw_gdp_cap['GDPCAP_USD'], fit_fun(msw_gdp_cap['GDPCAP_USD'], fit), '.', label = 'Proxies (unscaled log regression)')
#plt.plot(msw_gdp_cap['GDPCAP_USD'], fit_fun(msw_gdp_cap['GDPCAP_USD'], wb_fit), '.', label = 'WB_Proxies (unscaled log regression)')
#plt.plot(proj_data['GDPCAP_USD'],proj_data['Projections'], '.', label = 'Projections for 2017 - 2021',color = 'brown')
#plt.plot(proj_data['GDPCAP_USD'],proj_data['WB_Projections'], '.', label = 'Projections for 2017 - 2021 using WB fit',color = 'black')
plt.scatter(msw_gdp_cap['GDPCAP_USD'],msw_gdp_cap['MSW/CAP'],label ='Observed Data', s = 8)
plt.scatter(msw_gdp_cap['GDPCAP_USD'], fit_fun(msw_gdp_cap['GDPCAP_USD'], fit), label = 'Proxies of recalibrated model', s=8)
plt.scatter(msw_gdp_cap['GDPCAP_USD'], fit_fun(msw_gdp_cap['GDPCAP_USD'], wb_fit), label = 'Proxies of World Bank model', s = 8)
plt.scatter(proj_data['GDPCAP_USD'],proj_data['Projections'],  label = 'Projections for 2017 - 2021 (recalibrated)',color = 'brown', s = 5)
plt.scatter(proj_data['GDPCAP_USD'],proj_data['WB_Projections'], label = 'Projections for 2017 - 2021 (World Bank)',color = 'black', s=5)
plt.xlabel('GDP per capita, USD at 2015 PPP')
plt.ylabel('MSW gen per Capita, KG/PS')
plt.title('Waste generation: Comparison of models and actual data')
plt.legend(loc="lower right", prop={'size': 7})
plt.show()







