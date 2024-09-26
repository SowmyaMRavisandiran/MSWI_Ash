#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 16:26:56 2024

@author: marriyapillais
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from scipy.optimize import minimize, curve_fit, show_options
from functools import partial

eu_msw = pd.read_csv("data_saved/EU_MSW_Cleaned_Data.csv")
eu_msw = eu_msw[eu_msw['Country']!='EU27_2020']
eu27 = eu_msw.Country.unique()

eu_msw["INC%"] = eu_msw["DSP_I_RCV_E"]/eu_msw["TRT"]
eu_msw["TRT%"] = eu_msw["TRT"]/eu_msw["GEN"]
eu_msw["GEN%"] = eu_msw["GEN"]/eu_msw["GEN"]
eu_msw["DIS%"] = eu_msw["DSP_L_OTH"]/eu_msw["TRT"]
eu_msw["RCY%"] = eu_msw["RCY"]/eu_msw["TRT"]

#Dropping NaN values
eu_msw.dropna(subset=['INC%'], inplace=True)

#%% BAU SCENARIO

country_codes = pd.read_csv('data_saved/Country_Codes.csv')
missing_data = pd.read_csv('data_saved/Missing_data.csv')
eu_msw_cap = pd.read_csv('data_saved/EU_MSW_percap_Cleaned.csv')

#%% MSW GEN Projections
#%%% Missing Data to be filled in by BAU model

country_check = country_codes["NUTS_code"].iloc[:31]
missing_data_cap = []
for country in country_check:
    for year in np.arange(2010, 2022):
        if eu_msw_cap.loc[(eu_msw_cap["Country"]==country) & (eu_msw_cap["TIME_PERIOD"]==year)].empty:
            missing_data_cap.append([country,year])
            
missing_data_cap = pd.DataFrame(missing_data_cap, columns = ["Country", "TIME_PERIOD"])


#%%% Getting GDP/POP data and filling in gdp/pop for CYP and MLT
gdp = pd.read_csv('data_downloads/OECD_gdp.csv')
gdp = gdp[gdp["LOCATION"].isin(country_codes["NUTS_code"])]
pop= gdp.loc[(gdp["VARIABLE"]=='POP')& (gdp["Scenario"]=='Baseline')]
gdp_cap = gdp.loc[(gdp["VARIABLE"]=='GDPVD_CAP')& (gdp["Scenario"]=='Baseline')]
pop=pop[['LOCATION','VARIABLE','TIME','Value']].loc[pop['TIME'].isin(np.arange(2010,2051))]
#gdp_vd = gdp.loc[(gdp["VARIABLE"]=='GDPVD')& (gdp["Scenario"]=='Baseline')]

#%%%% Cyprus/Malta
#Getting WLD gdp growth rates and assuming that the same growth rates are followed by CYP and MLT
world_gdp_growth= pd.read_csv('data_downloads/oecd_gdp_world.csv')
gdp_cyp_mlt = pd.read_csv('data_downloads/oecd_gdp_cyp_mlt.csv')
pop_cyp_mlt = pd.read_csv('data_downloads/oecd_pop_cyp_mlt.csv')
pop_his_cm = pd.read_csv('data_downloads/oecd_pop_cyp_mlt_his.csv')
gdp_cyp_mlt = gdp_cyp_mlt[['REF_AREA','TIME_PERIOD','OBS_VALUE']]
pop_cyp_mlt=pop_cyp_mlt[['REF_AREA','TIME_PERIOD','OBS_VALUE']]
pop_his_cm=pop_his_cm[['REF_AREA','TIME_PERIOD','OBS_VALUE']]

#Cleaning data
gdp_cyp_mlt['OBS_VALUE']*=1e6
gdp_cyp_mlt.rename(columns={'TIME_PERIOD':'TIME', 'OBS_VALUE':'GDP_TOT_USD'},inplace = True)

world_gdp_growth.drop(["Flag Codes","FREQUENCY", "SUBJECT"], axis = 'columns', inplace = True)
world_gdp_growth['INDICATOR'] = 'GDPVD'
world_gdp_growth['Value']*=1e6
world_gdp_growth['MEASURE'] = 'USD'
world_gdp_growth = world_gdp_growth.loc[(world_gdp_growth['LOCATION']=='WLD') & (world_gdp_growth['TIME'].isin(np.arange(2010,2051)))]

#calculating growth rates for WLD
world_gdp_growth["GDP_Growth_Rate"] = world_gdp_growth['Value'].diff(periods=-1)/world_gdp_growth['Value']*100*-1
world_gdp_growth["GDP_Growth_Rate"]=world_gdp_growth["GDP_Growth_Rate"].shift(periods=1)

#Applying the growth rates for CYP and MLT to get gdp projections
gdp_cyp_mlt=gdp_cyp_mlt.pivot(index=['TIME'],columns='REF_AREA',values = 'GDP_TOT_USD').reset_index()

gdp_cyp_mlt = pd.merge(gdp_cyp_mlt,world_gdp_growth[['TIME','GDP_Growth_Rate']],how='outer',on='TIME')
for year in np.arange(2023,2051):
    gdp_cyp_mlt.loc[gdp_cyp_mlt['TIME']==year,'CYP']=gdp_cyp_mlt['CYP'].shift(1) * (1 + gdp_cyp_mlt['GDP_Growth_Rate']/100)
    gdp_cyp_mlt.loc[gdp_cyp_mlt['TIME']==year,'MLT']=gdp_cyp_mlt['MLT'].shift(1) * (1 + gdp_cyp_mlt['GDP_Growth_Rate']/100)

gdp_cyp_mlt['UNIT_MEASURE']='USD_PPP'
gdp_cyp_mlt.drop('GDP_Growth_Rate', axis='columns', inplace = True)
gdp_cyp_mlt = pd.melt(gdp_cyp_mlt,id_vars=['TIME', 'UNIT_MEASURE'],value_vars=['CYP','MLT'],var_name='REF_AREA',value_name='GDP_in_USD')

#using gdp and pop projections to get gdp/cap projections for CYP and MLT and appending the gdp projections file with estimated data


pop_cyp_mlt.rename(columns={'TIME_PERIOD':'TIME','OBS_VALUE':'POP'},inplace= True)
pop_cyp_mlt.drop(pop_cyp_mlt[pop_cyp_mlt['TIME'] == 2022].index, inplace = True)
pop_his_cm.rename(columns={'TIME_PERIOD':'TIME','OBS_VALUE':'POP'},inplace= True)


pop_cyp_mlt = pd.concat([pop_his_cm,pop_cyp_mlt],ignore_index=True)

gdp_cyp_mlt=pd.merge(gdp_cyp_mlt, pop_cyp_mlt,how = 'inner', on=['REF_AREA','TIME'])

gdp_cyp_mlt.drop('UNIT_MEASURE',axis='columns', inplace = True)
gdp_cyp_mlt['GDP_percap']=gdp_cyp_mlt['GDP_in_USD']/gdp_cyp_mlt['POP']

#%%%% Combining CYP and MLT with rest of the regions
#combining gdp_cap data of CYP, MLT with rest of the countries
gdp_cap=gdp_cap[['LOCATION','VARIABLE','TIME','Value']].loc[gdp_cap['TIME'].isin(np.arange(2010,2051))]
gdp_cap_cm = gdp_cyp_mlt[['REF_AREA','GDP_percap','TIME']]
gdp_cap_cm['VARIABLE']='GDPVD_CAP'
gdp_cap_cm.rename(columns={'REF_AREA':'LOCATION','GDP_percap':'Value'},inplace=True)
gdp_cap=pd.concat([gdp_cap,gdp_cap_cm],ignore_index=True)
gdp_cap.rename(columns = {'Value':'GDPVD_CAP'}, inplace = True)
gdp_cap.drop(['VARIABLE'], axis = 1, inplace = True)

#combining pop data
pop.rename(columns = {'Value':'POP'}, inplace = True)
pop.drop(['VARIABLE'], axis = 1, inplace = True)
pop_cyp_mlt.rename(columns={'REF_AREA':'LOCATION'}, inplace = True)
pop = pd.merge(pop, pop_cyp_mlt, how = 'outer', on = ['LOCATION', 'TIME', 'POP'])
pop = pop.loc[pop['TIME'].isin(np.arange(2010, 2051))]

#%%% Fits and fit function

def fit_fun(x,fit):
    #for the specified parameters, this function returns the log fit 
    return(fit[2]+fit[1]*np.log(x)+fit[0]*np.log(x)*np.log(x))

fit = np.load('msw_bau_model/fit_msw_projections.npy')
wb_fit = [29.43, -419.73 , 1647.41]
"""
Obtained fit: array([18.52534507, -176.90063059, 318.11762839])
WB fit: [29.43, -419.73 , 1647.41]
"""

def projections(reg_msw_data,reg_gdp_data, fit, base_year, column_names, proj_year):
    time, gdp_cap, msw_cap = column_names
    proxy_base = fit_fun(reg_gdp_data.loc[reg_gdp_data[time]==base_year][gdp_cap], fit).to_numpy()
    actual_base = reg_msw_data.loc[reg_msw_data[time]==base_year][msw_cap].to_numpy()
    if type(proj_year) == int:
        proxies = fit_fun(reg_gdp_data.loc[reg_gdp_data[time]==proj_year][gdp_cap], fit)
    else:
        proxies = fit_fun(reg_gdp_data.loc[reg_gdp_data[time].isin(proj_year)][gdp_cap], fit)
    projections = proxies /proxy_base * actual_base
    return(projections)

base_year = 2019


#%%% Filling in BAU data for MSW GEN

#%%%% creating dataframe
#creating a df with all data - msw, msw/cap, gdp/cap, pop, inc, inc%
bau_data = pd.merge(gdp_cap, pop, on = ['LOCATION', 'TIME'] , how = 'outer')

bau_data = pd.merge(bau_data, eu_msw[['Country','TIME_PERIOD','GEN', 'DSP_I_RCV_E', 'INC%']], how = 'left', left_on = ['LOCATION','TIME'], right_on=['Country','TIME_PERIOD'])
bau_data.drop(['Country','TIME_PERIOD'], axis = 1, inplace=True)
bau_data.rename(columns = {'GEN':'MSW_GEN_T', 'DSP_I_RCV_E':'INC_T'}, inplace = True)
bau_data['MSW_GEN_T']*=1e3
bau_data['INC_T']*=1e3

bau_data = pd.merge(bau_data, eu_msw_cap[['Country','TIME_PERIOD','GEN']], how = 'left', left_on = ['LOCATION','TIME'], right_on=['Country','TIME_PERIOD'])
bau_data.drop(['Country','TIME_PERIOD'], axis = 1, inplace=True)
bau_data.rename(columns = {'GEN':'MSW_GEN_CAP_KG/PS',}, inplace = True)
bau_data['WB_proj_mswcap'] = np.nan
bau_data['WB_proj_msw'] = np.nan

#%%%% Filling in missing_data using BAU model
# getting the projections of msw generated for the missing data in years 2020, 2021

for index, row in missing_data_cap.iterrows():
    country = row['Country']
    year = row['TIME_PERIOD']
    
    predict_msw = projections(bau_data[['TIME', 'MSW_GEN_CAP_KG/PS','LOCATION']].loc[(bau_data["LOCATION"]==country)], bau_data[['TIME', 'GDPVD_CAP','LOCATION']].loc[(bau_data["LOCATION"]==country)], fit, 2019,['TIME', 'GDPVD_CAP', 'MSW_GEN_CAP_KG/PS'], year).to_numpy()
    #wb_predict_msw = projections(bau_data[['TIME', 'MSW_GEN_CAP_KG/PS','LOCATION']].loc[(bau_data["LOCATION"]==country)], bau_data[['TIME', 'GDPVD_CAP','LOCATION']].loc[(bau_data["LOCATION"]==country)], wb_fit, 2019,['TIME', 'GDPVD_CAP', 'MSW_GEN_CAP_KG/PS'], year).to_numpy()
    
    
    #predict_msw = predict_msw.loc[predict_msw["TIME_PERIOD"]!=base_year]
    #predict_msw['Country'] = country
    #predict_msw['unit'] = 'THS_T'
    bau_data.loc[(bau_data['LOCATION'] == country) & (bau_data['TIME'] == year), ['MSW_GEN_CAP_KG/PS']] = predict_msw
    #bau_data.loc[(bau_data['LOCATION'] == country) & (bau_data['TIME'] == year), ['WB_proj_mswcap']] = wb_predict_msw
    bau_data.loc[(bau_data['LOCATION'] == country) & (bau_data['TIME'] == year), ['MSW_GEN_T']] = predict_msw * pop.loc[(pop['LOCATION'] == country) & (pop['TIME'] == year)]['POP'].to_numpy() /1e3
    #bau_data.loc[(bau_data['LOCATION'] == country) & (bau_data['TIME'] == year), ['WB_proj_msw']] = wb_predict_msw * pop.loc[(pop['LOCATION'] == country) & (pop['TIME'] == year)]['POP'].to_numpy() /1e3


#%%%% BAU projections for total MSW 

for region in bau_data['LOCATION'].unique():
    reg_data = bau_data.loc[bau_data['LOCATION']==region]
    bau_data.loc[(bau_data['LOCATION']==region)&(bau_data['TIME'].isin(np.arange(
        2022, 2051))),'MSW_GEN_CAP_KG/PS'] = projections(reg_data[['TIME','MSW_GEN_CAP_KG/PS']],reg_data[[
            'TIME','GDPVD_CAP']], fit, 2019, ['TIME','GDPVD_CAP', 'MSW_GEN_CAP_KG/PS'], np.arange(2022, 2051)) 
    bau_data.loc[(bau_data['LOCATION']==region)&(bau_data['TIME'].isin(np.arange(
        2022, 2051))),'MSW_GEN_T'] = bau_data['POP']*bau_data['MSW_GEN_CAP_KG/PS']/1e3
    
    # bau_data.loc[(bau_data['LOCATION']==region)&(bau_data['TIME'].isin(np.arange(
    #     2022, 2051))),'WB_proj_mswcap'] = projections(reg_data[['TIME','MSW_GEN_CAP_KG/PS']],reg_data[[
    #         'TIME','GDPVD_CAP']], wb_fit, 2019, ['TIME','GDPVD_CAP', 'MSW_GEN_CAP_KG/PS'], np.arange(2022, 2051)) 
    # bau_data.loc[(bau_data['LOCATION']==region)&(bau_data['TIME'].isin(np.arange(
    #     2022, 2051))),'WB_proj_msw'] = bau_data['POP']*bau_data['WB_proj_mswcap']/1e3

#%%% Plots for comparing two models

fig, axs = plt.subplots(8, 4, figsize=(20, 35))
axs=axs.flatten()
legend_handles = []
legend_labels = ['Historic MSW Generated (tonnes)','BAU projections for MSW (tonnes) - adjusted']

i=0
for region in bau_data["LOCATION"].unique():
    
    reg_data = bau_data.loc[bau_data['LOCATION']==region]
    
    #plotting historic data
    x = np.arange(2010,2022)
    y = reg_data["MSW_GEN_T"].loc[reg_data["TIME"].isin(x)]
    lines = axs[i].plot(x,y,'o', label='Historic MSW Generated (tonnes)')
    legend_handles.extend(lines)

    #plotting BAU projections of adjusted formula
    x = np.arange(2022,2051)
    y = reg_data["MSW_GEN_T"].loc[reg_data["TIME"].isin(x)]
    lines = axs[i].plot(x,y,'-', label = 'BAU projections for MSW (tonnes) - adjusted')
    legend_handles.extend(lines)

    #plotting BAU projections of old formula
    #x = np.arange(2022,2051)
    #y = reg_data["WB_proj_msw"].loc[reg_data["TIME"].isin(x)]
    #lines = axs[i].plot(x,y,'-', label = 'BAU projections for MSW (tonnes) - WB formula')

    
    axs[i].set_title('Projection of total MSW generated for ' + region)
    i+=1
    
# Adjust layout to make space for legend and heading
plt.tight_layout(rect=[0, 0, 0.9, 0.93])

# Set axis labels for subplots
for ax in axs:
    ax.set_xlabel('Years')
    ax.set_ylabel('MSW generated (in tonnes)')

# Add a common legend in the empty subplot
legend_subplot = plt.subplot(8,4, 32) 
legend_subplot.axis('off')
legend_subplot.legend(legend_handles, legend_labels, loc='center', fontsize=12)

# Add a title for the entire figure
title = fig.suptitle('BAU projections of MSW generated, base year 2019', fontsize=30)
title.set_position([0.45, 0.95])
#title.set_y(0.95)
plt.show()

#%% S-fit for INC %

def logistic_fun(x, L, k, x0):
    return L / (1 + np.exp(-k * (x - x0)))

def I(x, params_D, params_R):
    D = logistic_fun(x, params_D[0], params_D[1], params_D[2])
    R = logistic_fun(x, params_R[0], params_R[1], params_R[2])
    I = 1 - D - R
    return I

#%%% S-fit using minimize and constraints on params

def objective(params, years, inc_obs, dis_obs, rcy_obs):
    d = logistic_fun(years, params[0],params[1],params[2])
    r = logistic_fun(years, params[3],params[4],params[5])
    i = I(years, params[0:3], params[3:])
    d_d = np.sum((d - dis_obs)**2)
    d_r = np.sum((r - rcy_obs)**2)
    d_i = np.sum((i - inc_obs)**2)
    return d_d + d_r + d_i

def D(params, years):
    return logistic_fun(years, params[0], params[1], params[2])
def R(params, years):
    return logistic_fun(years, params[3], params[4], params[5])
def I_con(params,years):
    return I(years, params[0:3], params[3:])
    
def con_1(params, years):
    #constraint: D<1
    return (1-logistic_fun(years,params[0], params[1], params[2]))
def con_2(params, years):
    #constraint: R<1
    return (1-logistic_fun(years,params[3], params[4], params[5]))
def con_3(params, years):
    #constraint: I<1
    return (1-I(years, params[0:3], params[3:]))
def con_4(params, years):
    #constraint: D+R<1
    return (1-logistic_fun(years,params[3], params[4], params[5])-logistic_fun(years,params[0], params[1], params[2]))


#%%% Getting INC% for all countries and the corresponding inc quantities

for region in bau_data['LOCATION'].unique():
    reg_data = eu_msw.loc[eu_msw['Country']==region]
    
    #For GRC it is from 2020, IRL from 20221 and others from 2022
    #to calibrate this model, we are using data from all years
    years = np.arange(reg_data.iloc[0]["TIME_PERIOD"], 2051)
    
    initial_params = [reg_data.iloc[0]["DIS%"], -1, reg_data.iloc[0]["TIME_PERIOD"], reg_data.iloc[0]["RCY%"], 1, reg_data.iloc[0]["TIME_PERIOD"]]
    bounds = [(-np.inf, np.inf), (-np.inf, 0), (-np.inf, np.inf),(-np.inf, 1),(0, np.inf),(-np.inf, np.inf)]
    
    cons = [{'type': 'ineq', 'fun': partial(con_4, years=years)}
            ]
    
    years = reg_data["TIME_PERIOD"].to_numpy()
    results = minimize(objective, initial_params, args=(years, reg_data["INC%"].to_numpy(),reg_data["DIS%"].to_numpy(),reg_data["RCY%"].to_numpy()), bounds = bounds, constraints=cons, options ={ 'maxfev': 10000})
    
    # Extract the fitted parameters
    params = results.x
    params_D = params[0:3]
    params_R = params[3:]
    
    
    if region == 'GRC':
        start_year = 2020
    elif region == 'IRL':
        start_year = 2021
    else:
        start_year = 2022
    
    bau_data.loc[(bau_data['LOCATION']==region)&(bau_data['TIME'].isin(np.arange(
        start_year, 2051))),'INC%'] = I(np.arange(start_year, 2051), params_D, params_R)
    
    bau_data.loc[(bau_data['LOCATION']==region)&(bau_data['TIME'].isin(np.arange(
        start_year, 2051))),'INC_T'] = bau_data["INC%"]*bau_data['MSW_GEN_T']
            

#%%% S-fit: One plot for all regions

fig, axs = plt.subplots(8, 4, figsize=(20, 35))
axs=axs.flatten()
legend_handles = []
legend_labels = ['Historic Landfill%','Landfill% Trend', 'Historic Recycling%', 'Recycling% Trend', 'Historic Incineration%','Incineration% Trend']

i=0
for region in eu27:
    reg_data = eu_msw.loc[eu_msw['Country']==region]
    years = np.arange(reg_data.iloc[0]["TIME_PERIOD"], 2051)
    
    initial_params = [reg_data.iloc[0]["DIS%"], -1, reg_data.iloc[0]["TIME_PERIOD"], reg_data.iloc[0]["RCY%"], 1, reg_data.iloc[0]["TIME_PERIOD"]]
    bounds = [(-np.inf, np.inf), (-np.inf, 0), (-np.inf, np.inf),(-np.inf, 1),(0, np.inf),(-np.inf, np.inf)]
    
    cons = [{'type': 'ineq', 'fun': partial(con_4, years=years)}
            ]
    
    years = reg_data["TIME_PERIOD"].to_numpy()
    results = minimize(objective, initial_params, args=(years, reg_data["INC%"].to_numpy(),reg_data["DIS%"].to_numpy(),reg_data["RCY%"].to_numpy()), bounds = bounds, constraints=cons, options ={ 'maxfev': 10000})
    
    # Extract the fitted parameters
    params = results.x
    params_D = params[0:3]
    params_R = params[3:]
    
    #Landfill%
    L_fit, k_fit, x0_fit = params_D
    
    #plotting time series of Landfill %
    x = reg_data["TIME_PERIOD"]
    y = reg_data["DIS%"]
    lines = axs[i].plot(x,y,'o', label='Historic Landfill%', color = '#1f77b4')
    legend_handles.extend(lines)
    x = np.arange(reg_data.iloc[0]["TIME_PERIOD"],2051)
    lines = axs[i].plot(x, logistic_fun(x, L_fit, k_fit, x0_fit),'-',label = 'Landfill% Trend', color = '#1f77b4')
    legend_handles.extend(lines)
    
    #Recycling %
    # Extract the fitted parameters
    L_fit, k_fit, x0_fit = params_R
    
    #plotting time series of recycling %
    x = reg_data["TIME_PERIOD"]
    y = reg_data["RCY%"]
    lines = axs[i].plot(x,y,'o', label = 'Historic Recycling%', color='#ff7f0e')
    legend_handles.extend(lines)
    x = np.arange(reg_data.iloc[0]["TIME_PERIOD"],2051)
    lines = axs[i].plot(x, logistic_fun(x, L_fit, k_fit, x0_fit),'-',label = 'Recycling% Trend',  color='#ff7f0e')
    legend_handles.extend(lines)
    
    #plotting time series of recycling %
    x = reg_data["TIME_PERIOD"]
    y = reg_data["INC%"]
    lines = axs[i].plot(x,y, 'o', label = 'Historic Incineration%', color = '#2ca02c')
    legend_handles.extend(lines)
    x = np.arange(reg_data.iloc[0]["TIME_PERIOD"],2051)
    lines = axs[i].plot(x, I(x, params_D, params_R),'-',label = 'Incineration% Trend', color = '#2ca02c')
    legend_handles.extend(lines)
    
    axs[i].set_title('Projection of treatment method for ' + region)
    i+=1
    #print(region,' ', params_D, ' ', params_R, '/n')

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
title = fig.suptitle('Trend Analysis of Incineration %', fontsize=30)
title.set_position([0.45, 0.95])
#title.set_y(0.95)
plt.show()

#%%% EU27+4

#%%%% EU 27+4 data
#MSW Generated

countries_to_group = bau_data["LOCATION"].unique()
df_filtered = bau_data[bau_data['LOCATION'].isin(countries_to_group)]
df_filtered.drop(['WB_proj_mswcap','WB_proj_msw','GDPVD_CAP','INC%', 'MSW_GEN_CAP_KG/PS','POP'],axis = 'columns', inplace = True)
# Create a new row for 'EU 27+4' by summing values for specified countries
df_filtered = df_filtered.groupby(['TIME'], as_index=False).sum()

df_filtered['LOCATION'] = 'EU27+4'

#%%%% Plots for EU 27+4
x = np.arange(2010,2022)
y = df_filtered["MSW_GEN_T"].loc[df_filtered["TIME"].isin(x)]
fig = plt.plot(x,y,'o', label='Historic MSW Generated (tonnes)')

#plotting BAU projections of adjusted formula
x = np.arange(2022,2051)
y = df_filtered["MSW_GEN_T"].loc[df_filtered["TIME"].isin(x)]
plt.plot(x,y,'-', label = 'BAU projections for MSW (tonnes)')

plt.xlabel('Years')
plt.ylabel('MSW Generated (in tonnes)')
plt.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=2, prop={'size': 7})
plt.title('BAU Projections of Total MSW Generated in EU27+4')
plt.show()

#Incineration %

eu_data = eu_msw.loc[eu_msw['Country']=="EU27+4"]
years = np.arange(eu_data.iloc[0]["TIME_PERIOD"], 2051)

initial_params = [eu_data.iloc[0]["DIS%"], -1, eu_data.iloc[0]["TIME_PERIOD"], eu_data.iloc[0]["RCY%"], 1, eu_data.iloc[0]["TIME_PERIOD"]]
bounds = [(-np.inf, np.inf), (-np.inf, 0), (-np.inf, np.inf),(-np.inf, 1),(0, np.inf),(-np.inf, np.inf)]

cons = [{'type': 'ineq', 'fun': partial(con_4, years=years)}
        ]

years = eu_data["TIME_PERIOD"].to_numpy()
results = minimize(objective, initial_params, args=(years, eu_data["INC%"].to_numpy(),eu_data["DIS%"].to_numpy(),eu_data["RCY%"].to_numpy()), bounds = bounds, constraints=cons, options ={ 'maxfev': 10000})

# Extract the fitted parameters
params = results.x
params_D = params[0:3]
params_R = params[3:]

#Landfill%
L_fit, k_fit, x0_fit = params_D

#plotting time series of Landfill %
x = eu_data["TIME_PERIOD"]
y = eu_data["DIS%"]
fig = plt.plot(x,y,'o', label='Historic Landfill%', color = '#1f77b4')
x = np.arange(eu_data.iloc[0]["TIME_PERIOD"],2051)
plt.plot(x, logistic_fun(x, L_fit, k_fit, x0_fit),'-',label = 'Landfill% Trend', color = '#1f77b4')


#Recycling %
# Extract the fitted parameters
L_fit, k_fit, x0_fit = params_R

#plotting time series of recycling %
x = eu_data["TIME_PERIOD"]
y = eu_data["RCY%"]
plt.plot(x,y,'o', label = 'Historic Recycling%', color='#ff7f0e')
x = np.arange(reg_data.iloc[0]["TIME_PERIOD"],2051)
plt.plot(x, logistic_fun(x, L_fit, k_fit, x0_fit),'-',label = 'Recycling% Trend',  color='#ff7f0e')

#plotting time series of recycling %
x = eu_data["TIME_PERIOD"]
y = eu_data["INC%"]
plt.plot(x,y, 'o', label = 'Historic Incineration%', color = '#2ca02c')

x = np.arange(reg_data.iloc[0]["TIME_PERIOD"],2051)
plt.plot(x, I(x, params_D, params_R),'-',label = 'Incineration% Trend', color = '#2ca02c')
plt.xlabel('Years')
plt.ylabel('Treatment %')
plt.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=2, prop={'size': 7})
plt.title('Trend Analysis of Treatment Methods')


#print(region,' ', params_D, ' ', params_R, '/n')




#%% Getting the outputs for ash in the required data structure

#%%% adding EU27+4

#Dropping WB columns
#bau_data.drop(['WB_proj_mswcap', 'WB_proj_msw'], axis = 'columns', inplace = True)

ash_data = pd.concat([bau_data[df_filtered.columns],df_filtered],ignore_index = True)

#%%% Getting ash quantities

ash_data["SLASH_bottomAshesWasteInc"] = ash_data['INC_T']*0.28
ash_data["SLASH_flyAshesWasteInc"] = ash_data['INC_T']*0.03
#eu_msw_his["SLASH_boilerAshesWasteInc"] = eu_msw_his['MSW_WasteInc']*0.03
ash_data.drop(['MSW_GEN_T','INC_T'], axis = 'columns', inplace = True)
ash_data.rename(columns= {'TIME':'Year','LOCATION':'Country'},inplace=  True)

#%%% reformatting into output structure

columns = ['Waste Stream', 'Country', 'Year', 'Scenario', 'Substance main parent',
           'Stock/Flow ID', 'Value', 'Unit', 'Data Quality', 'Reference', 'Remark 1',
           'Remark 2', 'Remark 3']


ash_data= pd.melt(ash_data, id_vars=['Country','Year'], value_vars = ['SLASH_bottomAshesWasteInc',
                                'SLASH_flyAshesWasteInc'],var_name='Stock/Flow ID', value_name='Value')

#Changing all values to tonnes

ash_data['Unit'] = 't'

#adding  waste stream
ash_data['Waste Stream'] = 'SLASH'

#adding LowKey codes
subs_main_parent = {'SLASH_flyAshesWasteInc':'19 01 13*','SLASH_bottomAshesWasteInc':'19 01 11*',
                    'SLASH_boilerAshesWasteInc':'19 01 15*'}
ash_data['Substance main parent'] = ash_data['Stock/Flow ID'].map(subs_main_parent)

#Rearrange columns

ash_data['Scenario'] = np.where(ash_data['Year'] <= 2021, 'OBS', 'BAU')
ash_data[['Reference']] = np.nan
ash_data[['Remark 2']] = np.nan

ash_data.loc[(ash_data["Country"]=='GBR')&(ash_data['Year']<=2021),['Remark 1']] = 'Estimated from OECD MSW incineration quantities'
conditions = (((ash_data["Country"]=='DNK')&(ash_data["Year"]==2010)) | ((ash_data["Country"]=='IRL')&(ash_data["Year"]==2013)) | ((ash_data["Country"]=='IRL')&(ash_data["Year"]==2015)) | ((ash_data["Country"]=='ISL')&(ash_data["Year"]==2019)))
ash_data.loc[conditions,['Remark 1']]='Missing data, estimated from Eurostat MSW incineration quantities of neighbouring years '
ash_data.loc[(ash_data["Country"]!='GBR') & (ash_data['Year']<=2021) & ~conditions,['Remark 1']]='Estimated from Eurostat MSW incineration quantities'

#remarlk for bau scenario
conditions = (((ash_data["Country"]=='IRL')&(ash_data["Year"]==2021)) | ((ash_data["Country"]=='GRC')&(ash_data["Year"]==2020))| ((ash_data["Country"]=='GRC')&(ash_data["Year"]==2021)))
ash_data.loc[(ash_data['Scenario']=='BAU') | conditions,['Remark 1']] = 'Estimated from models - Check Reference'

ash_data[['Remark 3']] = 'Sowmya Ravisandiran'


ash_data.loc[ash_data['Year'] <= 2021,['Data Quality']] = 2
ash_data.loc[ash_data['Year'] > 2035,['Data Quality']] = 4
ash_data.loc[(ash_data['Year'] > 2021)&(ash_data['Year']<=2035),['Data Quality']] = 3

ash_data = ash_data[columns]

#eu_msw_his.drop(eu_msw_his.loc[eu_msw_his["Country"]=='EU27_2020'].index, inplace = True)


ash_data.to_csv('Data_Structure_Task4.1_Task4.2_BAU.csv', index = False)



#%% Checking trade balances

eu_msw["Balance"] = eu_msw["GEN"]-eu_msw["TRT"]

balance = eu_msw.groupby(by=["TIME_PERIOD"]).sum()

balance = eu_msw.loc[eu_msw["Country"]!='EU27+4']

balance = balance.groupby(by=["TIME_PERIOD","unit"])[['Balance','GEN','TRT','DSP_I_RCV_E','DSP_L_OTH','RCY']].sum()
balance = balance.reset_index()
balance = balance.loc[balance["TIME_PERIOD"]>=2001]

trade = pd.read_excel('data_downloads/Waste_shipment_data_imports_exports.xlsx', header = 8) 

trade=trade.loc[trade["General Basel Convention code -Y code"].isin(["Y18","Y46","Y47"])]
trade = trade[['Year', 'Import/export', 'Country reporting', 'Country Category',
        'Quantity in tonnes', 'To or from country', 'To or from country category',
       'Disposal and recovery code', 'General Basel Convention code -Y code']]


a = trade.groupby(by = ['Year','Import/export'])['Quantity in tonnes'].sum().reset_index()
a=pd.pivot(a,index = 'Year',columns = 'Import/export',values = 'Quantity in tonnes').reset_index()
a["Trade_Balance"]=a["Export"]-a["Import"]
a['Trade_Balance']*=1e-3
a["Export"]*=1e-3
a["Import"]*=1e-3

b = pd.merge(balance, a[["Year",'Trade_Balance']], how = 'inner', left_on = "TIME_PERIOD", right_on = "Year")

b["% covered in trade data"] = b['Trade_Balance']/b['Balance']
b['% traded wrt gen'] = b["Balance"]/b["GEN"]


trade_msw = b[["TIME_PERIOD","unit","Balance","Trade_Balance","GEN","% covered in trade data","% traded wrt gen"]]



#GEN vs TRT

test = eu_msw[['TIME_PERIOD', 'unit', 'DSP_I_RCV_E', 'DSP_L_OTH', 'GEN',
       'RCY','TRT', 'Country', 'INC%','TRT%', 'Balance']].loc[eu_msw["TIME_PERIOD"]>=2010]

test = test.loc[test["TRT%"]!=1]


test_5yrs = eu_msw[['TIME_PERIOD', 'unit', 'DSP_I_RCV_E', 'DSP_L_OTH', 'GEN',
                    'RCY','TRT', 'Country', 'INC%','TRT%', 'Balance']].loc[eu_msw["TIME_PERIOD"]>=2017]


test_2yrs = eu_msw[['TIME_PERIOD', 'unit', 'DSP_I_RCV_E', 'DSP_L_OTH', 'GEN',
                    'RCY','TRT', 'Country', 'INC%','TRT%', 'Balance']].loc[eu_msw["TIME_PERIOD"]>=2020]




#%% Analysis of balance

eu_msw["balance %"] = eu_msw['Balance']/eu_msw['GEN']
eu_msw['balance_inc%']= eu_msw['balance %']*eu_msw['INC%']
eu_msw['balance_rcy%']= eu_msw['balance %']*eu_msw['RCY%']
eu_msw['balance_dis%']= eu_msw['balance %']*eu_msw['DIS%']
eu_msw['Balance/TRT'] = eu_msw['Balance']/eu_msw['TRT']

eu_msw_5years = eu_msw.loc[eu_msw["TIME_PERIOD"]>=2017]


eu_filtered = eu_msw_5years[eu_msw_5years["Country"].isin(countries_to_group)]
eu_filtered = eu_filtered[['TIME_PERIOD', 'unit', 'DSP_I_RCV_E', 'DSP_L_OTH', 'GEN', 'RCY', 'TRT',
       'Country', 'INC%', 'TRT%', 'GEN%', 'DIS%', 'RCY%', 'Balance']]

eu_filtered['inc%*bal']=eu_filtered['INC%']*eu_filtered['Balance']
eu_filtered['rcy%*bal']=eu_filtered['RCY%']*eu_filtered['Balance']
eu_filtered['dis%*bal']=eu_filtered['DIS%']*eu_filtered['Balance']

eu_filtered = eu_filtered[['TIME_PERIOD', 'unit', 'DSP_I_RCV_E', 'DSP_L_OTH', 'GEN', 'RCY', 'TRT',
       'Country', 'inc%*bal', 'dis%*bal', 'rcy%*bal', 'Balance']]

eu_filtered = eu_filtered.groupby(["TIME_PERIOD"],as_index=False).sum()

eu_filtered['unit']='THS_T'

eu_filtered['Country']='EU27+4'

eu_filtered['inc%*bal/gen']=eu_filtered['inc%*bal']/eu_filtered['GEN'] 
eu_filtered['rcy%*bal/gen']=eu_filtered['rcy%*bal']/eu_filtered['GEN']
eu_filtered['dis%*bal/gen']=eu_filtered['dis%*bal']/eu_filtered['GEN']

#%% Example analysis for PRT, SWE

prt_data = eu_msw.loc[eu_msw['Country']=='PRT']
swe_data = eu_msw.loc[eu_msw['Country']=='SWE']

prt_data.drop(columns = ['DSP_I','RCV_E','PRP_REU','RCY_C_D','RCY_M'],inplace = True)
swe_data.drop(columns = ['DSP_I','RCV_E','PRP_REU','RCY_C_D','RCY_M'],inplace = True)


prt_trade = trade.loc[trade['Country reporting']=='Portugal']


a = prt_trade.groupby(['Year', 'Import/export', 'Country reporting', 'Country Category','General Basel Convention code -Y code'],as_index=False)['Quantity in tonnes'].sum()
a = a.loc[a['General Basel Convention code -Y code']=='Y46']


class TradeAnalysis:
    """
    self.data 
    Type: pandas DataFrame
    Contains: columns ['Year', 'Import/export', 'Country reporting', 'Country Category',
            'Quantity in tonnes', 'To or from country', 'To or from country category',
           'Disposal and recovery code', 'General Basel Convention code -Y code', 'European List of Waste code',
           'Detailed Basel Convention code or OECD decison code', 'Hazardousness',
           'Basis for classification to hazardous and non-hazardous',
           'UN hazardous code properties which render the waste hazardous',
           'Country of transit stated by a code', 'Notes']
    """
    
    def __init__(self, country_name, data):
        self.country_name = country_name
        self.data = data
        
    def total_trade_quantity(self):
        self.data
        

    def total_export_value(self):
        return sum(self.export_data.values())

    def total_import_value(self):
        return sum(self.import_data.values())

    def trade_balance(self):
        return self.total_export_value() - self.total_import_value()

    def top_export_products(self, num_products=5):
        sorted_exports = sorted(self.export_data.items(), key=lambda x: x[1], reverse=True)
        return sorted_exports[:num_products]

    def top_import_products(self, num_products=5):
        sorted_imports = sorted(self.import_data.items(), key=lambda x: x[1], reverse=True)
        return sorted_imports[:num_products]


















