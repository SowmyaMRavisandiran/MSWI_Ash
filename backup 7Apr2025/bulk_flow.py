#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 19 15:25:43 2023

@author: marriyapillais
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#Reading MSW data downloaded from Eurostat
msw_data = pd.read_csv("data_downloads/env_wasmun_linear.csv")
country_codes = pd.read_csv("data_saved/country_codes.csv")

#changes for coutnry codes are not needed since the updated file is saved
#nuts_0 = pd.read_csv("data_downloads/locationNUTS-0.csv")


#Fixing code for Romania in the file
#country_codes.loc[country_codes["Country"]=='Romania',"Code"] = 'RO'

#List of EU27+4 regions that are under study
eu27 = country_codes["Code"].values

units = msw_data["unit"].unique()
wst_oper = msw_data["wst_oper"].unique()

"""
Breakdown of Waste Management Operations:

RECYCLING:    
RCY = RCY_M+RCY_C_D+RCY_PRP_REU

INCINERATION:
DSP_I_RCV_E = RCV_E+ DSP_I

ALL TREATMENT
TRT = DSP_I_RCV_E + DSP_L_OTH + RCY
"""

time_period = msw_data["TIME_PERIOD"].unique() 

#Selecting data with E27 regions 

#eu_msw = msw_data.loc[(msw_data["geo"].isin(eu27) & (msw_data["unit"]==units[1]))]
eu_msw = msw_data.loc[(msw_data["geo"].isin(eu27))]
eu_msw.drop(["DATAFLOW","LAST UPDATE","freq","OBS_FLAG"],axis = 'columns', inplace = True)

#pivoting table to perform calculations
eu_msw = eu_msw.pivot(index=['geo','TIME_PERIOD','unit'], columns='wst_oper', values='OBS_VALUE')

#mapping country code to 3-letter codes
eu_msw = eu_msw.reset_index()
#country_codes["NUTS_code"] = country_codes.merge(nuts_0, left_on='Country',right_on='description', how = 'left')["code"]
#country_codes.loc[country_codes["NUTS_code"].isna(), "NUTS_code"] = 'EU27_2020'
eu_msw["Country"] = eu_msw.merge(country_codes, left_on='geo', right_on = "Code", how = 'left')["NUTS_code"]
eu_msw.drop(['geo'], axis = 'columns', inplace = True)

#%% OBS SCENARIO

#%%% Data Cleaning - Removing NaNs 

nan_count = eu_msw.isna().sum()

#Cleaning Prepare for Reuse columns
eu_msw.loc[eu_msw['PRP_REU'].isna(),'PRP_REU'] = 0
    
#Cleaning Energy recovery and Incineration data
"""

- If one of the values of DSP_I and RCV_E is NaN, then it is assumed to be zero and 
  DSP_I_RCV_E is a summation of DSP_I, RSV_E.
- If all three are zero, then if the volume for other treatment methods add up to
  volume of treatment, then everything is zero

"""

#Changing NaN values when one of DSP_I, RCV_E is NaN: 
eu_msw.loc[(eu_msw['DSP_I'].isna()) & (eu_msw['RCV_E'].notna()), 'DSP_I']=0
eu_msw.loc[(eu_msw['RCV_E'].isna()) & (eu_msw['DSP_I'].notna()), 'RCV_E']=0
eu_msw['DSP_I_RCV_E']=np.where((eu_msw['DSP_I_RCV_E'].isna()) & (eu_msw['DSP_I'].notna()) &
                            (eu_msw['RCV_E'].notna()), eu_msw[['DSP_I','RCV_E']].sum(axis=1),
                            eu_msw['DSP_I_RCV_E']) 

"""
#  If we want to retain NaN values as NaN, can follow the steps below to replace the steps above:

# fill in the sum of DSP_I and RCV_E when one of them is NaN

eu_msw['DSP_I_RCV_E']=np.where((eu_msw['DSP_I_RCV_E'].isna())& ((eu_msw['DSP_I'].notna()) |
                            (eu_msw['RCV_E'].notna())), eu_msw[['DSP_I','RCV_E']].sum(axis=1),
                            eu_msw['DSP_I_RCV_E']) 

"""

"""
#The following entries are changed with the conditions checked below. so this step does not affect the 
# fact that Other_recovery column is not present in eurostat data 



a = np.where((eu_msw['DSP_I_RCV_E'].isna()) & (eu_msw['RCY'].notna())
                                      & (eu_msw['DSP_L_OTH'].notna()) & 
                                      (eu_msw['DSP_L_OTH']+eu_msw['RCY']==eu_msw['TRT']))
check = eu_msw.iloc[a]

b = np.where((eu_msw['DSP_I_RCV_E'].notna()) & (eu_msw['RCY'].isna())
                                      & (eu_msw['DSP_L_OTH'].notna()) & 
                                      (eu_msw['DSP_L_OTH']+eu_msw['DSP_I_RCV_E']==eu_msw['TRT']))
check_2 = eu_msw.iloc[b]
"""
#When all three are NaN, Checking if the volumes of other treatment methods add 
#up, and changing NaN

eu_msw['DSP_I']=np.where((eu_msw['DSP_I_RCV_E'].isna()) & (eu_msw['RCY'].notna())
                                      & (eu_msw['DSP_L_OTH'].notna()) & 
                                      (eu_msw['DSP_L_OTH']+eu_msw['RCY']==eu_msw['TRT']),
                                       0, eu_msw['DSP_I'])
eu_msw['RCV_E']=np.where((eu_msw['DSP_I_RCV_E'].isna()) & (eu_msw['RCY'].notna())
                                      & (eu_msw['DSP_L_OTH'].notna()) & 
                                      (eu_msw['DSP_L_OTH']+eu_msw['RCY']==eu_msw['TRT']),
                                       0, eu_msw['RCV_E'])
eu_msw['DSP_I_RCV_E']=np.where((eu_msw['DSP_I_RCV_E'].isna()) & (eu_msw['RCY'].notna())
                                      & (eu_msw['DSP_L_OTH'].notna()) & 
                                      (eu_msw['DSP_L_OTH']+eu_msw['RCY']==eu_msw['TRT']),
                                       0, eu_msw['DSP_I_RCV_E'])

#Cleaning Recycling data

#Similar to incineration, changing NaN when one of the two recycling processes is NaN
eu_msw.loc[(eu_msw['RCY_C_D'].isna()) & (eu_msw['RCY_M'].notna()), 'RCY_C_D']=0
eu_msw.loc[(eu_msw['RCY_M'].isna()) & (eu_msw['RCY_C_D'].notna()), 'RCY_M']=0
eu_msw['RCY']=np.where((eu_msw['RCY'].isna()) & (eu_msw['RCY_C_D'].notna()) &
                            (eu_msw['RCY_M'].notna()), eu_msw[['RCY_C_D','RCY_M']].sum(axis=1),
                            eu_msw['RCY']) 

"""
#  If we want to retain NaN values as NaN, can follow the steps below to replace the 3 steps above:

# fill in the sum of RCY_C_D and RCY_M when one of them is NaN

eu_msw['RCY']=np.where((eu_msw['RCY'].isna())& ((eu_msw['RCY_C_D'].notna()) |
                            (eu_msw['RCY_M'].notna())), eu_msw[['RCY_C_D','RCY_M']].sum(axis=1),
                            eu_msw['RCY']) 

"""

#When all three are NaN, Checking if the volumes of other treatment methods add 
#up, and changing NaN

eu_msw['RCY_M']=np.where((eu_msw['RCY'].isna()) & (eu_msw['DSP_I_RCV_E'].notna())
                                      & (eu_msw['DSP_L_OTH'].notna()) & 
                                      (eu_msw['DSP_L_OTH']+eu_msw['DSP_I_RCV_E']==eu_msw['TRT']),
                                       0, eu_msw['RCY_M'])
eu_msw['RCY_C_D']=np.where((eu_msw['DSP_I_RCV_E'].notna()) & (eu_msw['RCY'].isna())
                                      & (eu_msw['DSP_L_OTH'].notna()) & 
                                      (eu_msw['DSP_L_OTH']+eu_msw['DSP_I_RCV_E']==eu_msw['TRT']),
                                       0, eu_msw['RCY_C_D'])
eu_msw['RCY']=np.where((eu_msw['DSP_I_RCV_E'].notna()) & (eu_msw['RCY'].isna())
                                      & (eu_msw['DSP_L_OTH'].notna()) & 
                                      (eu_msw['DSP_L_OTH']+eu_msw['DSP_I_RCV_E']==eu_msw['TRT']),
                                       0, eu_msw['RCY'])


#%%% Check for missing data
#Check for missing data
country_check = country_codes["NUTS_code"].iloc[:31]
missing_data = []
for country in country_check:
    for year in np.arange(2010, 2022):
        if eu_msw.loc[(eu_msw["Country"]==country) & (eu_msw["TIME_PERIOD"]==year)].empty:
            missing_data.append([country,year])
            
missing_data = pd.DataFrame(missing_data, columns = ["Country", "TIME_PERIOD"])


#%%% OECD data comparison

#Loading OECD MSW data and selecting relevant countries, treatment methods, variables, and units of measure
oecd_msw = pd.read_csv("data_downloads/msw_oecd.csv")
oecd_units = oecd_msw["Unit of measure"].unique()
oecd_msw = oecd_msw.loc[oecd_msw["Unit of measure"].isin(oecd_units[1:3])]
oecd_msw = oecd_msw.loc[oecd_msw["REF_AREA"].isin(country_codes["NUTS_code"])]
measure = ['Total waste generated',
          'Material recovery (Recycling + Composting)', 'Composting',
          'Recycling', 'Other recovery',
          'Incineration without energy recovery', 'Memo: total incineration',
          'Landfill', 'Disposal operations',
          'Other disposal', 'Recovery operations',
          'Amounts designated for treatment operations',
          'Incineration with energy recovery']
oecd_msw = oecd_msw.loc[oecd_msw["Measure"].isin(measure)]
oecd_vars = ["REF_AREA","Reference area", "Measure","UNIT_MEASURE", "Unit of measure","TIME_PERIOD", "OBS_VALUE","UNIT_MULT"]
oecd_msw = oecd_msw[oecd_vars]

oecd_msw_percap = oecd_msw.loc[oecd_msw["UNIT_MEASURE"]=='KG_PS'] 
oecd_msw_tonnes = oecd_msw.loc[oecd_msw["UNIT_MEASURE"]=='T'] 

oecd_msw_tonnes = oecd_msw_tonnes.pivot(index=["REF_AREA","Reference area","UNIT_MEASURE", "Unit of measure","TIME_PERIOD","UNIT_MULT"], columns=['Measure'], values='OBS_VALUE')
oecd_msw_tonnes = oecd_msw_tonnes.reset_index()

#oecd_check = oecd_msw_tonnes.loc[(oecd_msw_tonnes["Other recovery"].notna())&(oecd_msw_tonnes["Other recovery"]!=0)&(oecd_msw_tonnes["Memo: total incineration"]==0)]
oecd_msw_percap = oecd_msw_percap.pivot(index=["REF_AREA","Reference area","UNIT_MEASURE", "Unit of measure","TIME_PERIOD","UNIT_MULT"], columns=['Measure'], values='OBS_VALUE')
oecd_msw_percap = oecd_msw_percap.reset_index()


#%%% Getting Missing Data for UK from OECD data

#Getting the values for UK

oecd_uk = oecd_msw_tonnes.loc[(oecd_msw_tonnes["REF_AREA"]=='GBR')&(oecd_msw_tonnes["TIME_PERIOD"].isin(time_period))]
oecd_uk_cap = oecd_msw_percap.loc[(oecd_msw_percap["REF_AREA"]=='GBR')&(oecd_msw_percap["TIME_PERIOD"].isin(time_period))]

# columns to drop : 'Recovery operations', 'Other recovery','Disposal operations','Other disposal'
map_trt = {'Total waste generated':'GEN',
          'Material recovery (Recycling + Composting)':'RCY', 
          'Composting' : 'RCY_C_D',
          'Recycling': 'RCY_M',
          'Incineration without energy recovery': 'DSP_I', 
          'Memo: total incineration': 'DSP_I_RCV_E',
          'Landfill':'DSP_L_OTH', 
          'Amounts designated for treatment operations': 'TRT',
          'Incineration with energy recovery': 'RCV_E'}

oecd_uk.drop(['Recovery operations', 'Other recovery','Disposal operations','Other disposal', "Unit of measure", "UNIT_MULT", "Reference area"], axis = 'columns', inplace = True)
oecd_uk = oecd_uk.rename(columns = map_trt)
oecd_uk = oecd_uk.rename(columns = {"REF_AREA":'Country',"UNIT_MEASURE":'unit'})
oecd_uk["unit"]='THS_T'
#Prepare for reuse
oecd_uk["PRP_REU"] = 0

oecd_uk_cap.drop([ "Unit of measure", "UNIT_MULT", "Reference area"], axis = 'columns', inplace = True)
oecd_uk_cap = oecd_uk_cap.rename(columns = map_trt)
oecd_uk_cap = oecd_uk_cap.rename(columns = {"REF_AREA":'Country',"UNIT_MEASURE":'unit'})
oecd_uk_cap["unit"]='KG_HAB'
#Prepare for reuse
oecd_uk_cap["PRP_REU"] = 0



#%%%%Checking difference between OECD and Eurostat for UK
a = eu_msw[eu_msw['Country']=='GBR']
a = a[["DSP_I_RCV_E","TIME_PERIOD"]]
a = a[a["TIME_PERIOD"].isin([2011,2012,2013,2014,2015,2016,2017,2018])]
a = a["DSP_I_RCV_E"].to_numpy()
b = oecd_uk[oecd_uk["TIME_PERIOD"].isin([2011,2012,2013,2014,2015,2016,2017,2018])]
b = b[["DSP_I_RCV_E","TIME_PERIOD"]]
b = b["DSP_I_RCV_E"].to_numpy()
c = (a-b)/b*100

#%%% Separating per cap data and total volume data

eu_msw_cap = eu_msw.loc[eu_msw["unit"] == units[0]]

#selecting bulk values of msw
eu_msw = eu_msw.loc[eu_msw["unit"] == units[1]]

#%%% Filling in missing data by interpolation when the neighbouring years are available
missing_data['unit'] = 'THS_T'

eu_msw = pd.concat([eu_msw,missing_data.loc[(missing_data['TIME_PERIOD']<2020)&(missing_data['Country']!='GBR')]])
eu_msw.sort_values(by=['Country', 'TIME_PERIOD'], inplace = True, ignore_index = True)

"""
for the rows with nan, which are not GRC or HRV (since they have some missing values), use interpolate to fill in data 
"""
excluded_countries = ['GRC', 'HRV']
interpolate_df = eu_msw[~eu_msw["Country"].isin(excluded_countries)].copy()
interpolate_df = interpolate_df.interpolate()
eu_msw.update(interpolate_df, overwrite = False)

#doing the same for per cap


country_check = country_codes["NUTS_code"].iloc[:31]
missing_data_cap = []
for country in country_check:
    for year in np.arange(2010, 2022):
        if eu_msw_cap.loc[(eu_msw_cap["Country"]==country) & (eu_msw_cap["TIME_PERIOD"]==year)].empty:
            missing_data_cap.append([country,year])
            
missing_data_cap = pd.DataFrame(missing_data_cap, columns = ["Country", "TIME_PERIOD"])


eu_msw_cap = pd.concat([eu_msw_cap,missing_data_cap.loc[(missing_data_cap['TIME_PERIOD']<2020)&(missing_data_cap['Country']!='GBR')]])
eu_msw_cap.sort_values(by=['Country', 'TIME_PERIOD'], inplace = True, ignore_index = True)

"""
for the rows with nan, which are not GRC or HRV (since they have some missing values), use interpolate to fill in data 
"""
excluded_countries = ['GRC', 'HRV']
interpolate_df = eu_msw_cap[~eu_msw_cap["Country"].isin(excluded_countries)].copy()
interpolate_df = interpolate_df.interpolate()
eu_msw_cap.update(interpolate_df, overwrite = False)



#%%% Adding EU27+4 for total msw quantities and getting per cap data separately

# adding missing values for UK from OECD data
eu_msw = pd.concat([eu_msw[eu_msw["Country"]!='GBR'],oecd_uk], ignore_index = True)

#countries_to_group = ['EU27_2020', 'GBR', 'ISL', 'NOR', 'CHE']
#summing all countries instead of using EU27_2020

countries_to_group = country_codes["NUTS_code"][:-1].to_list()
df_filtered = eu_msw[eu_msw['Country'].isin(countries_to_group)]

# Create a new row for 'EU 27+4' by summing values for specified countries
df_filtered = df_filtered.groupby(['TIME_PERIOD', 'unit'], as_index=False).sum()

df_filtered['Country'] = 'EU27+4'
df_filtered = df_filtered[~df_filtered['TIME_PERIOD'].isin([2020,2021])]

eu_msw = pd.concat([eu_msw, df_filtered], ignore_index=True)

eu_msw.to_csv("EU_MSW_Cleaned_Data.csv")


# adding missing values for UK from OECD data
eu_msw_cap = pd.concat([eu_msw_cap[eu_msw_cap["Country"]!='GBR'],oecd_uk_cap], ignore_index = True)

eu_msw_cap.to_csv("EU_MSW_percap_Cleaned.csv",index = False)

#%%% getting BA/FA for all historic years required for the data structure

            
eu_msw_his = eu_msw.loc[eu_msw["TIME_PERIOD"].isin(np.arange(2010,2022))]
eu_msw_his= eu_msw_his[['GEN','DSP_I_RCV_E','TIME_PERIOD','unit','Country']]
eu_msw_his = eu_msw_his.rename(columns = {'GEN':"MSW_Gen", "DSP_I_RCV_E":"MSW_WasteInc"})  #this step is not needed



#estimating ash quantities
"""
From BAT document:
    BA = 150-350 kg/t -> 15-35 % wt/wt
    Boiler ash = 20-40 kg/t -> 2-4% wt/wt
    FA = 15-60 -> 1.5-6 % wt/wt
    
    
    CODES:
        SLASH_flyAshesWasteInc
        SLASH_bottomAshesWasteInc
"""

eu_msw_his["SLASH_bottomAshesWasteInc"] = eu_msw_his['MSW_WasteInc']*0.28
eu_msw_his["SLASH_flyAshesWasteInc"] = eu_msw_his['MSW_WasteInc']*0.03
#eu_msw_his["SLASH_boilerAshesWasteInc"] = eu_msw_his['MSW_WasteInc']*0.03
eu_msw_his.drop(['MSW_Gen','MSW_WasteInc'], axis = 'columns', inplace = True)

#%%% creating output data structure

columns = ['Waste Stream', 'Country', 'Year', 'Scenario', 'Substance main parent',
           'Stock/Flow ID', 'Value', 'Unit', 'Data Quality', 'Reference', 'Remark 1',
           'Remark 2', 'Remark 3']


eu_msw_his= pd.melt(eu_msw_his, id_vars=['Country','unit','TIME_PERIOD'], value_vars = ['SLASH_bottomAshesWasteInc',
                                'SLASH_flyAshesWasteInc'],var_name='Stock/Flow ID', value_name='Value')

#Changing all values to tonnes
eu_msw_his["Value"] *=1000
eu_msw_his['unit'] = 't'
eu_msw_his = eu_msw_his.rename(columns = {'unit':"Unit"})

#adding year, waste stream
eu_msw_his = eu_msw_his.rename(columns = {'TIME_PERIOD':'Year'})
eu_msw_his['Waste Stream'] = 'SLASH'

#adding LowKey codes
subs_main_parent = {'SLASH_flyAshesWasteInc':'19 01 13','SLASH_bottomAshesWasteInc':'19 01 11',
                    'SLASH_boilerAshesWasteInc':'19 01 15'}
eu_msw_his['Substance main parent'] = eu_msw_his['Stock/Flow ID'].map(subs_main_parent)

#Rearrange columns

eu_msw_his[['Scenario']] = 'OBS'
eu_msw_his[['Reference']] = np.nan
eu_msw_his[['Remark 2']] = np.nan

eu_msw_his.loc[eu_msw_his["Country"]=='GBR',['Remark 1']] = 'Estimated from OECD MSW incineration quantities'
conditions = (((eu_msw_his["Country"]=='DNK')&(eu_msw_his["Year"]==2010)) | ((eu_msw_his["Country"]=='IRL')&(eu_msw_his["Year"]==2013)) | ((eu_msw_his["Country"]=='IRL')&(eu_msw_his["Year"]==2015)) | ((eu_msw_his["Country"]=='ISL')&(eu_msw_his["Year"]==2019)))
eu_msw_his.loc[conditions,['Remark 1']]='Missing data, estimated from Eurostat MSW incineration quantities of neighbouring years '
eu_msw_his.loc[(eu_msw_his["Country"]!='GBR')& ~conditions,['Remark 1']]='Estimated from Eurostat MSW incineration quantities'
eu_msw_his[['Remark 3']] = 'Sowmya Ravisandiran'
eu_msw_his[['Data Quality']] = 2
eu_msw_his = eu_msw_his[columns]
eu_msw_his.drop(eu_msw_his.loc[eu_msw_his["Country"]=='EU27_2020'].index, inplace = True)
eu_msw_his.to_csv('Data_Structure_Task4.1_Task4.2.csv')

















