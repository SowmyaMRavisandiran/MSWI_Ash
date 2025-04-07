#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 20:30:39 2024

@author: marriyapillais
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


bau_data = pd.read_csv("data_saved/BAU_MSW.csv")
rec_data = pd.read_csv("data_saved/REC_MSW.csv")
cir_data = pd.read_csv("data_saved/CIR_MSW.csv")


reg_bau_data = bau_data.loc[bau_data['LOCATION']=='EU27+4']
reg_rec_data = rec_data.loc[rec_data['LOCATION']=='EU27+4']
reg_cir_data = cir_data.loc[cir_data['LOCATION']=='EU27+4']



#plotting time series of Landfill %
fig = plt.plot(reg_bau_data.loc[reg_bau_data['TIME']<=2021]['TIME'],reg_bau_data.loc[reg_bau_data['TIME']<=2021]['DIS%'],'o', label='Historic Landfill%', color = '#1f77b4')

x = np.arange(2010,2051)
plt.plot(x, reg_bau_data['DIS%'].loc[reg_bau_data['TIME'].isin(x)],'-',label = 'Landfill% Trend BAU', color = '#1f77b4')

plt.plot(reg_cir_data.loc[reg_cir_data['TIME']>=2022]['TIME'],reg_cir_data.loc[reg_cir_data['TIME']>=2022]['DIS%'],'--',label = 'Landfill% Trend CIR', color = '#1f77b4')

#Recycling %

#plotting time series of recycling %
plt.plot(reg_bau_data.loc[reg_bau_data['TIME']<=2021]['TIME'],reg_bau_data.loc[reg_bau_data['TIME']<=2021]['RCY%'],'o', label = 'Historic Recycling%', color='#ff7f0e')

x = np.arange(2010,2051)
plt.plot(x, reg_bau_data['RCY%'].loc[reg_bau_data['TIME'].isin(x)],'-',label = 'Recycling% Trend BAU', color = '#ff7f0e')

plt.plot(reg_cir_data.loc[reg_cir_data['TIME']>=2022]['TIME'],reg_cir_data.loc[reg_cir_data['TIME']>=2022]['RCY%'],'--',label = 'Recycling% Trend CIR', color = '#ff7f0e')

#plotting time series of incineration %
plt.plot(reg_bau_data.loc[reg_bau_data['TIME']<=2021]['TIME'],reg_bau_data.loc[reg_bau_data['TIME']<=2021]['INC%'], 'o', label = 'Historic Incineration%', color = '#2ca02c')
x = np.arange(2010,2051)
plt.plot(x, reg_bau_data['INC%'].loc[reg_bau_data['TIME'].isin(x)],'-',label = 'Incineration% Trend BAU', color = '#2ca02c')
   
plt.plot(reg_cir_data.loc[reg_cir_data['TIME']>=2022]['TIME'],reg_cir_data.loc[reg_cir_data['TIME']>=2022]['INC%'],'--',label = 'Incineration% Trend CIR', color = '#2ca02c')



plt.xlabel('Years')
plt.ylabel('Treatment %')
plt.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=2, prop={'size': 7})
plt.title('Trend Analysis of Treatment Methods: CIR Scenario')


plt.show()

#%%
#plotting time series of MSW GEN
fig = plt.plot(reg_bau_data.loc[reg_bau_data['TIME']<=2021]['TIME'],reg_bau_data.loc[reg_bau_data['TIME']<=2021]['MSW_GEN_T'],'o', label='Historic MSW Generated', color = '#575D90')

x = np.arange(2010,2051)
plt.plot(x, reg_bau_data['MSW_GEN_T'].loc[reg_bau_data['TIME'].isin(x)],'-',label = 'MSW GEN Trend BAU', color = '#575D90')

plt.plot(reg_cir_data.loc[reg_cir_data['TIME']>=2022]['TIME'],reg_cir_data.loc[reg_cir_data['TIME']>=2022]['MSW_GEN_T'],'--',label = 'MSW GEN Trend CIR', color = '#575D90')


plt.xlabel('Years')
plt.ylabel('MSW Generated in tonnes')
plt.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=2, prop={'size': 7})
plt.title('MSW Generation: CIR Scenario')


plt.show()

#%%%

x = np.arange(2010,2051)
fig = plt.plot(x, reg_bau_data['MSW_GEN_T'].loc[reg_bau_data['TIME'].isin(x)],'-',label = 'MSW Generated Trend BAU', color = '#310D20')
plt.plot(reg_rec_data.loc[reg_rec_data['TIME']>=2022]['TIME'],reg_rec_data.loc[reg_rec_data['TIME']>=2022]['MSW_GEN_T'],'--',label = 'MSW Generated Trend REC', color = '#310D20')
plt.plot(reg_cir_data.loc[reg_cir_data['TIME']>=2022]['TIME'],reg_cir_data.loc[reg_cir_data['TIME']>=2022]['MSW_GEN_T'],'--',label = 'MSW Generated Trend CIR', color = '#310D20')


plt.plot(x, reg_bau_data['INC_T'].loc[reg_bau_data['TIME'].isin(x)],'-',label = 'MSW Incinerated Trend BAU', color = '#225560')
plt.plot(reg_rec_data.loc[reg_rec_data['TIME']>=2022]['TIME'],reg_rec_data.loc[reg_rec_data['TIME']>=2022]['INC_T'],'--',label = 'MSW Incinerated Trend REC', color = '#225560')
plt.plot(reg_cir_data.loc[reg_cir_data['TIME']>=2022]['TIME'],reg_cir_data.loc[reg_cir_data['TIME']>=2022]['INC_T'],'--',label = 'MSW Incinerated Trend CIR', color = '#225560')


plt.xlabel('Years')
plt.ylabel('Trends of MSW Gen and INC in tonnes')
plt.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=2, prop={'size': 7})
plt.title('Trend Analysis of MSW Generation and Incineration')


plt.show()

#%%
ash_data = pd.read_csv('data_saved/Data_Structure_Task4.1_Task4.2_all_scenarios.csv')
reg_bau_data = ash_data.loc[(ash_data['Country']=='EU27+4')&((ash_data['Scenario']=='BAU')|(ash_data['Scenario']=='OBS'))]
reg_rec_data = ash_data.loc[(ash_data['Country']=='EU27+4')&(ash_data['Scenario']=='REC')] 
reg_cir_data = ash_data.loc[(ash_data['Country']=='EU27+4')&(ash_data['Scenario']=='CIR')]

x = np.arange(2010,2051)
fig = plt.plot(x, reg_bau_data['Value'].loc[(reg_bau_data['Year'].isin(x))&(reg_bau_data['Substance main parent']=='19 01 11*')],'-',label = 'Bottom ash BAU', color = '#210124')
plt.plot(reg_rec_data.loc[reg_rec_data['Year']>=2022]['Year'].unique(),reg_rec_data.loc[(reg_rec_data['Year']>=2022)&(reg_rec_data['Substance main parent']=='19 01 11*')]['Value'],'--',label = 'Bottom ash REC', color = '#210124')
plt.plot(reg_cir_data.loc[reg_cir_data['Year']>=2022]['Year'].unique(),reg_cir_data.loc[(reg_cir_data['Year']>=2022)&(reg_cir_data['Substance main parent']=='19 01 11*')]['Value'],'--',label = 'Bottom ash CIR', color = '#210124')


plt.plot(x, reg_bau_data['Value'].loc[(reg_bau_data['Year'].isin(x))&(reg_bau_data['Substance main parent']=='19 01 13*')],'-',label = 'Fly ash BAU', color = '#750D37')
plt.plot(reg_rec_data.loc[reg_rec_data['Year']>=2022]['Year'].unique(),reg_rec_data.loc[(reg_rec_data['Year']>=2022)&(reg_rec_data['Substance main parent']=='19 01 13*')]['Value'],'--',label = 'Fly ash REC', color = '#750D37')
plt.plot(reg_cir_data.loc[reg_cir_data['Year']>=2022]['Year'].unique(),reg_cir_data.loc[(reg_cir_data['Year']>=2022)&(reg_cir_data['Substance main parent']=='19 01 13*')]['Value'],'--',label = 'Fly ash CIR', color = '#750D37')


plt.xlabel('Years')
plt.ylabel('MSW Inc Ash in tonnes')
plt.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=2, prop={'size': 7})
plt.title('Trend Analysis of MSW Incineration Ash')


plt.show()


