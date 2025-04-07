#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 17 15:40:19 2024

@author: marriyapillais
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from scipy.optimize import minimize, curve_fit, show_options
from functools import partial

#bau_data = pd.read_csv("data_saved/BAU_MSW.csv", index_col = 0)
parameter = pd.read_csv("data_saved/parameters.csv")
bau_data = pd.read_csv("data_saved/BAU_MSW_updated.csv", index_col = 0)
#parameter = pd.read_csv("data_saved/parameters_updated.csv")

#%% Data structure

bau_data["Scenario"] = "BAU"  
bau_data.loc[bau_data["TIME"] <= 2021, "Scenario"] = "OBS"

#bau_data.drop(columns = ["GDPVD_CAP","POP","MSW_GEN_CAP_KG/PS"], inplace= True)
bau_data.reset_index(drop=True, inplace= True)
rec_data = bau_data.loc[bau_data["TIME"]>=2022].copy()
rec_data['Scenario']='REC'

#%% Function to check 


def value_at_2035(bau_data, treatment_method):
    return (bau_data[treatment_method].loc[(bau_data["TIME"]==2035)].values[0])
    
def get_rcy_until2050(bau_data):
    rec_rcy_data = pd.DataFrame(columns = ['TIME','RCY%'])
    dif_from_bau = (0.65-value_at_2035(bau_data,'RCY%'))/value_at_2035(bau_data,'RCY%')
    differences_from_2021 = pd.DataFrame({'TIME':np.arange(2021,2036),'Difference':  np.linspace(0, dif_from_bau, 15)}) #15=2035-2021+1
    print(differences_from_2021)
    #Get the REC data for RCY between 2021 and 2035
    rec_rcy_data['TIME'] = np.arange(2021,2051)
    rec_rcy_data['RCY%']= bau_data["RCY%"].loc[bau_data['TIME'].isin(np.arange(2021,2036))].reset_index(drop=True) * (1+differences_from_2021['Difference'])
    
    #Get the REC data for RCY between 2036 and 2050 
    rec_rcy_data.loc[rec_rcy_data['TIME'].isin(np.arange(2036, 2051)),'RCY%']= rec_rcy_data['RCY%'].loc[rec_rcy_data['TIME']==2035].values[0]
    
    
    return rec_rcy_data

def get_dis_until2050(bau_data):
    rec_dis_data = pd.DataFrame(columns = ['TIME','DIS%'])
    dif_from_bau = (value_at_2035(bau_data,'DIS%')-0.1)/value_at_2035(bau_data,'DIS%')
    differences_from_2021 = pd.DataFrame({'TIME':np.arange(2021,2036),'Difference':  np.linspace(0, dif_from_bau, 15)}) #15=2035-2021+1
    print(differences_from_2021)
    #Get the REC data for RCY between 2021 and 2035
    rec_dis_data['TIME'] = np.arange(2021,2051)
    rec_dis_data['DIS%'] = bau_data['DIS%'].loc[bau_data['TIME'].isin(np.arange(2021,2036))].reset_index(drop=True) * (1-differences_from_2021['Difference'])
    
    #Get the REC data for DIS between 2036 and 2050 
    rec_dis_data.loc[rec_dis_data['TIME'].isin(np.arange(2036, 2051)),'DIS%']= rec_dis_data['DIS%'].loc[rec_dis_data['TIME']==2035].values[0]
   
    return rec_dis_data

def check_bau_rcy(bau_data):
    if value_at_2035(bau_data,'RCY%')>= 0.65:
        rec_rcy = bau_data[['TIME','RCY%']].loc[bau_data['TIME'].isin(np.arange(2021,2051))]
        print('BAU')
    
    else:
        rec_rcy = get_rcy_until2050(bau_data)
        #print(rec_rcy)
    rec_rcy.reset_index(drop = True, inplace = True)   
    return rec_rcy

def check_bau_dis(bau_data):
    if value_at_2035(bau_data,'DIS%')<= 0.1:
        rec_dis = bau_data[['TIME','DIS%']].loc[bau_data['TIME'].isin(np.arange(2021,2051))]
        print('BAU')
    
    else:
       rec_dis = get_dis_until2050(bau_data)
       #print(rec_dis)
    rec_dis.reset_index(drop = True, inplace = True)
    return rec_dis

def get_inc_until2050(bau_rcy,bau_dis):
    rec_inc_data = pd.DataFrame(columns = ['TIME','INC%'])
    rec_inc_data["TIME"]= np.arange(2021,2051)
    rec_inc_data['INC%'] = 1 - bau_rcy['RCY%'] - bau_dis['DIS%']
    return rec_inc_data

#%%

# bau_msw = pd.read_csv("data_saved/EU_MSW_Cleaned_Data.csv")
# bau_msw['Balance'] = bau_msw['TRT'] - bau_msw['DSP_I_RCV_E'] - bau_msw['DSP_L_OTH'] - bau_msw['RCY']
# bau_msw['Balance%'] = bau_msw['Balance']/bau_msw['TRT']*100

# bau_msw_check = bau_msw.loc[(bau_msw['Balance%']>=5)&(bau_msw['TIME_PERIOD'].isin(np.arange(2010,2022)))]

#%%Plotting 

fig, axs = plt.subplots(8, 4, figsize=(20, 35))
axs=axs.flatten()
legend_handles = []
#legend_labels = ['Historic Landfill%','Landfill% Trend BAU','Landfill fit target','Landfill% Trend REC', 'Historic Recycling%', 'Recycling% Trend BAU', 'Recycling fit target','Recycling% Trend REC','Historic Incineration%','Incineration% Trend BAU', 'Incineration fit target','Incineration% Trend REC']
legend_labels = ['Historic Landfill%','Landfill% Trend BAU','Landfill% Trend REC', 'Historic Recycling%', 'Recycling% Trend BAU', 'Recycling% Trend REC','Historic Incineration%','Incineration% Trend BAU', 'Incineration% Trend REC']

i=0
rec_data = rec_data.set_index(['LOCATION','TIME'])
for region in bau_data['LOCATION'].unique():
    #print(region)
    
    reg_bau_data = bau_data.loc[bau_data['LOCATION']==region]
    #print(reg_bau_data)
    
    rec_rcy = check_bau_rcy(reg_bau_data)

    rec_dis = check_bau_dis(reg_bau_data)

    rec_inc = get_inc_until2050(rec_rcy, rec_dis)
    
    
    reg_rec_data = pd.DataFrame({'TIME':np.arange(2021,2051),'RCY%':rec_rcy['RCY%'],'DIS%':rec_dis['DIS%'],'INC%':rec_inc['INC%']})
    reg_rec_data['LOCATION'] = region
    
    
    #print(reg_rec_data)
    
    #plotting time series of Landfill %
    lines = axs[i].plot(reg_bau_data.loc[reg_bau_data['TIME']<=2021]['TIME'],reg_bau_data.loc[reg_bau_data['TIME']<=2021]['DIS%'],'o', label='Historic Landfill%', color = '#1f77b4')
    legend_handles.extend(lines)
    x = np.arange(2010,2051)
    lines = axs[i].plot(x, reg_bau_data['DIS%'].loc[reg_bau_data['TIME'].isin(x)],'-',label = 'Landfill% Trend BAU', color = '#1f77b4')
    legend_handles.extend(lines)
       
    lines = axs[i].plot(reg_rec_data.loc[reg_rec_data['TIME']>=2022]['TIME'],reg_rec_data.loc[reg_rec_data['TIME']>=2022]['DIS%'],'--',label = 'Landfill% Trend REC', color = '#1f77b4')
    legend_handles.extend(lines)
    
    #Recycling %
    
    #plotting time series of recycling %
    lines = axs[i].plot(reg_bau_data.loc[reg_bau_data['TIME']<=2021]['TIME'],reg_bau_data.loc[reg_bau_data['TIME']<=2021]['RCY%'],'o', label = 'Historic Recycling%', color='#ff7f0e')
    legend_handles.extend(lines)
    x = np.arange(2010,2051)
    lines = axs[i].plot(x, reg_bau_data['RCY%'].loc[reg_bau_data['TIME'].isin(x)],'-',label = 'Recycling% Trend BAU', color = '#ff7f0e')
    legend_handles.extend(lines)
    lines = axs[i].plot(reg_rec_data.loc[reg_rec_data['TIME']>=2022]['TIME'],reg_rec_data.loc[reg_rec_data['TIME']>=2022]['RCY%'],'--',label = 'Recycling% Trend REC', color = '#ff7f0e')
    legend_handles.extend(lines)
    
    #plotting time series of incineration %
    lines = axs[i].plot(reg_bau_data.loc[reg_bau_data['TIME']<=2021]['TIME'],reg_bau_data.loc[reg_bau_data['TIME']<=2021]['INC%'], 'o', label = 'Historic Incineration%', color = '#2ca02c')
    legend_handles.extend(lines)
    x = np.arange(2010,2051)
    lines = axs[i].plot(x, reg_bau_data['INC%'].loc[reg_bau_data['TIME'].isin(x)],'-',label = 'Incineration% Trend BAU', color = '#2ca02c')
    legend_handles.extend(lines)
       
    lines = axs[i].plot(reg_rec_data.loc[reg_rec_data['TIME']>=2022]['TIME'],reg_rec_data.loc[reg_rec_data['TIME']>=2022]['INC%'],'--',label = 'Incineration% Trend REC', color = '#2ca02c')
    legend_handles.extend(lines)
    

    axs[i].set_title(region)
    
    
    #Update rec_data
    reg_rec_data = reg_rec_data.set_index(['LOCATION','TIME'])
    columns_to_update = ['RCY%', 'DIS%', 'INC%']
    rec_data.update(reg_rec_data[columns_to_update])


    i+=1

# Reset index 
rec_data = rec_data.reset_index()

# Adjust layout to make space for legend and heading
plt.tight_layout(rect=[0, 0, 0.9, 0.93])

# Set axis labels for subplots
for ax in axs:
    ax.set_xlabel('Years')
    ax.set_ylabel('Treatment %')

# Add a common legend below the subplots
fig.subplots_adjust(bottom=0.05)
legend_subplot = fig.add_axes([0.1, 0.02, 0.7, 0.02])  
legend_subplot.axis('off')
legend_subplot.legend(legend_handles, legend_labels, loc='center', ncol=6, fontsize=15)

# Add a title for the entire figure
title = fig.suptitle('REC scenario', fontsize=30)
title.set_position([0.45, 0.95])
#title.set_y(0.95)
plt.show()

#%%
rec_data["INC_T"] = rec_data['MSW_GEN_T']*rec_data['INC%']
#rec_data.to_csv("data_saved/REC_MSW.csv")
    
#%% CIR scenario

def cir_msw_total(bau_data):
    msw_total_data = pd.DataFrame(columns = ['TIME','MSW_GEN_T'])
    dif_from_bau = 0.1
    differences_from_2021 = pd.DataFrame({'TIME':np.arange(2021,2051),'Difference':  np.linspace(0, dif_from_bau, 30)}) #30=2050-2021+1
    
    msw_total_data['TIME'] = np.arange(2021,2051)
    msw_total_data['MSW_GEN_T']= bau_data["MSW_GEN_T"].loc[bau_data['TIME'].isin(np.arange(2021,2051))].reset_index(drop=True) * (1-differences_from_2021['Difference'])

    
    return msw_total_data

cir_data = rec_data.copy()
cir_data['Scenario']='CIR'
cir_data = cir_data.set_index(['LOCATION','TIME'])

for region in rec_data["LOCATION"].unique():
    msw_new = cir_msw_total(bau_data.loc[bau_data['LOCATION']==region])
    msw_new['LOCATION'] = region
    print(msw_new)
    
    msw_new = msw_new.set_index(['LOCATION','TIME'])
    cir_data.update(msw_new['MSW_GEN_T'])

cir_data = cir_data.reset_index()
cir_data["INC_T"] = cir_data['MSW_GEN_T']*cir_data['INC%']
#cir_data.to_csv("data_saved/CIR_MSW.csv")

#%%Ash data for REC, CIR and BAU

ash_data = pd.concat([bau_data,pd.concat([rec_data,cir_data],ignore_index = True)], ignore_index = True)

ash_data["SLASH_bottomAshesWasteInc"] = ash_data['INC_T']*0.28
ash_data["SLASH_flyAshesWasteInc"] = ash_data['INC_T']*0.03
#eu_msw_his["SLASH_boilerAshesWasteInc"] = eu_msw_his['MSW_WasteInc']*0.03
ash_data.drop(['MSW_GEN_T','INC_T'], axis = 'columns', inplace = True)
ash_data.drop(['DIS%','RCY%','INC%'], axis = 'columns', inplace = True)
ash_data.rename(columns= {'TIME':'Year','LOCATION':'Country'},inplace=  True)

#%%% reformatting into output structure

columns = ['Waste Stream', 'Country', 'Year', 'Scenario', 'Substance main parent',
           'Stock/Flow ID', 'Value', 'Unit', 'Data Quality', 'Reference', 'Remark 1',
           'Remark 2', 'Remark 3']


ash_data= pd.melt(ash_data, id_vars=['Country','Year','Scenario'], value_vars = ['SLASH_bottomAshesWasteInc',
                                'SLASH_flyAshesWasteInc'],var_name='Stock/Flow ID', value_name='Value')

#Changing all values to tonnes

ash_data['Unit'] = 't'

#adding  waste stream
ash_data['Waste Stream'] = 'SLASH'

#adding LowKey codes
subs_main_parent = {'SLASH_flyAshesWasteInc':'19 01 13*','SLASH_bottomAshesWasteInc':'19 01 11*'}
                    #'SLASH_boilerAshesWasteInc':'19 01 15*'}
ash_data['Substance main parent'] = ash_data['Stock/Flow ID'].map(subs_main_parent)

#Rearrange columns

#ash_data['Scenario'] = np.where(ash_data['Year'] <= 2021, 'OBS', 'BAU')
ash_data[['Reference']] = np.nan
ash_data[['Remark 2']] = np.nan

ash_data.loc[(ash_data["Country"]=='GBR')&(ash_data['Year']<=2021),['Remark 1']] = 'Estimated from OECD MSW incineration quantities'
conditions = (((ash_data["Country"]=='DNK')&(ash_data["Year"]==2010)) | ((ash_data["Country"]=='IRL')&(ash_data["Year"]==2013)) | ((ash_data["Country"]=='IRL')&(ash_data["Year"]==2015)) | ((ash_data["Country"]=='ISL')&(ash_data["Year"]==2019)))
ash_data.loc[conditions,['Remark 1']]='Missing data, estimated from Eurostat MSW incineration quantities of neighbouring years '
ash_data.loc[(ash_data["Country"]!='GBR') & (ash_data['Year']<=2021) & ~conditions,['Remark 1']]='Estimated from Eurostat MSW incineration quantities'

#remarlk for bau scenario
conditions = (((ash_data["Country"]=='IRL')&(ash_data["Year"]==2021)) | ((ash_data["Country"]=='GRC')&(ash_data["Year"]==2020))| ((ash_data["Country"]=='GRC')&(ash_data["Year"]==2021)))
ash_data.loc[(ash_data['Scenario']=='BAU') | conditions,['Remark 1']] = 'Estimated from models - Check Reference'
ash_data.loc[(ash_data['Scenario']=='CIR') | (ash_data['Scenario']=='REC'),['Remark 1']] = 'Estimated from models - Check Reference'

ash_data[['Remark 3']] = 'Sowmya Ravisandiran'


ash_data.loc[ash_data['Year'] <= 2021,['Data Quality']] = 2
ash_data.loc[ash_data['Year'] > 2035,['Data Quality']] = 4
ash_data.loc[(ash_data['Year'] > 2021)&(ash_data['Year']<=2035),['Data Quality']] = 3

ash_data = ash_data[columns]

#eu_msw_his.drop(eu_msw_his.loc[eu_msw_his["Country"]=='EU27_2020'].index, inplace = True)


ash_data.to_csv('Data_Structure_Task4.1_Task4.2_all_scenarios.csv', index = False)

















