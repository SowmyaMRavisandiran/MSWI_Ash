#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 15 11:08:24 2023

@author: marriyapillais
"""

import pandas as pd

#reading eurostat data for Netherlands
nl_msw_data = pd.read_csv("env_wasmun_page_linear_NL.csv")
#removing columns that are not needed
nl_msw_data.drop(["DATAFLOW","LAST UPDATE","freq","OBS_FLAG"],axis = 'columns',inplace = True)

units = nl_msw_data["unit"].unique()
wst_oper = nl_msw_data["wst_oper"].unique()
time_period = nl_msw_data["TIME_PERIOD"].unique() 

#creating separate dataframes for tonnes and kg/cap for the year 2021
nl_msw_percap_2021 = nl_msw_data.loc[(nl_msw_data["unit"]==units[0])&(nl_msw_data["TIME_PERIOD"]==2021)]
nl_msw_tonnes_2021 = nl_msw_data.loc[(nl_msw_data["unit"]==units[1])&(nl_msw_data["TIME_PERIOD"]==2021)]

inc_code = "DSP_I_RCV_E"

#create data frame with quantities of incineration and BA/FA

ba_perc = 25 
fa_perc = 3 

nl_inc_2021 = nl_msw_tonnes_2021.loc[(nl_msw_tonnes_2021["wst_oper"]==inc_code)]
nl_inc_2021['Bottom Ash'] = nl_inc_2021["OBS_VALUE"] * ba_perc / 100
nl_inc_2021['Fly Ash'] = nl_inc_2021["OBS_VALUE"] * fa_perc / 100


#time series of MSW generation for NL

nl_msw_tonnes = nl_msw_data.loc[(nl_msw_data["unit"]==units[1])]

#Note: pivoting the table loses the following columns: unit, geo

nl_msw_tonnes = nl_msw_tonnes.pivot(index='TIME_PERIOD', columns='wst_oper', values='OBS_VALUE')
nl_msw_tonnes["ICN%"] = nl_msw_tonnes[inc_code]/nl_msw_tonnes["GEN"]
nl_msw_tonnes["TRT%"] = nl_msw_tonnes["TRT"]/nl_msw_tonnes["GEN"]
nl_msw_tonnes["GEN%"] = nl_msw_tonnes["GEN"]/nl_msw_tonnes["GEN"]
nl_msw_tonnes["DIS%"] = nl_msw_tonnes["DSP_L_OTH"]/nl_msw_tonnes["GEN"]
nl_msw_tonnes["RCY%"] = nl_msw_tonnes["RCY"]/nl_msw_tonnes["GEN"]
#plotting time series of incineration %
import matplotlib.pyplot as plt

plt.plot(nl_msw_tonnes.index.values,nl_msw_tonnes["GEN%"],color='black', label='Generation%', linewidth=1)
plt.plot(nl_msw_tonnes.index.values,nl_msw_tonnes["TRT%"],color='red', label='Treatment %', linewidth=1)
plt.plot(nl_msw_tonnes.index.values,nl_msw_tonnes["ICN%"],color='blue', label='Incineration %', linewidth=1)
plt.plot(nl_msw_tonnes.index.values,nl_msw_tonnes["DIS%"],color='orchid', label='Disposal %', linewidth=1)
plt.plot(nl_msw_tonnes.index.values,nl_msw_tonnes["RCY%"],color='green', label='Recycling %', linewidth=1)

plt.xlabel('years')
plt.ylabel('Transfer coefficients')
plt.title('Time Series of Proportion of Treatment Methods')
plt.legend(loc="upper right", prop={'size': 8})
plt.show()


nl_msw_tonnes["SUM"] = nl_msw_tonnes[inc_code]+nl_msw_tonnes["DSP_L_OTH"]+nl_msw_tonnes["RCY"]
#stacked plot of treatment methods
plt.plot([],[],color='palegoldenrod', label='Incineration', linewidth=3)
plt.plot([],[],color='powderblue', label='Recycling', linewidth=3)
plt.plot([],[],color='orchid', label='Other Disposal', linewidth=3)
plt.stackplot(nl_msw_tonnes.index.values, nl_msw_tonnes[inc_code], nl_msw_tonnes["RCY"], nl_msw_tonnes["DSP_L_OTH"], colors=['palegoldenrod','powderblue','orchid'])

plt.xlabel('years')
plt.ylabel('Transfer coefficients')
plt.title('Time Series of Treatment methods')
plt.legend(loc="lower right", prop={'size': 8})
plt.show()