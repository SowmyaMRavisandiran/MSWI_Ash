#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  9 13:15:18 2024

@author: marriyapillais
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


#%% BA, Boiler Ash and FA for 2021

#get the variables from the file (check previous code)
eu_msw = []
country_codes = []

#selecting data for 2021

eu_msw_2021 = eu_msw.loc[:,2021,:]
eu_msw_2021= eu_msw_2021[['GEN','DSP_I_RCV_E']]
eu_msw_2021 = eu_msw_2021.rename(columns = {'GEN':"MSW_Gen", "DSP_I_RCV_E":"MSW_WasteInc"})

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

eu_msw_2021["SLASH_bottomAshesWasteInc"] = eu_msw_2021['MSW_WasteInc']*0.25
eu_msw_2021["SLASH_flyAshesWasteInc"] = eu_msw_2021['MSW_WasteInc']*0.03
eu_msw_2021["SLASH_boilerAshesWasteInc"] = eu_msw_2021['MSW_WasteInc']*0.03

#creating output data structure

columns = ['Waste Stream', 'Country', 'Year', 'Scenario', 'Substance main parent',
           'Stock/Flow ID', 'Value', 'Unit', 'Data Quality', 'Reference', 'Remark 1',
           'Remark 2', 'Remark 3']

eu_msw_2021 = eu_msw_2021.reset_index()
eu_msw_2021= pd.melt(eu_msw_2021, id_vars=['geo','unit'], value_vars = ['MSW_Gen', 'MSW_WasteInc', 
                                'SLASH_bottomAshesWasteInc','SLASH_flyAshesWasteInc',
                                'SLASH_boilerAshesWasteInc'], var_name='Stock/Flow ID',
                                value_name='Value')

#Changing all values to tonnes
eu_msw_2021["Value"] *=1000
eu_msw_2021['unit'] = 't'
eu_msw_2021 = eu_msw_2021.rename(columns = {'unit':"Unit"})

#adding year, waste stream
eu_msw_2021['Year'] = 2021
eu_msw_2021['Waste Stream'] = 'SLASH'

#mapping countries to NUTS0 codes
nuts_0 = pd.read_csv("locationNUTS-0.csv")
country_codes["NUTS_code"] = country_codes.merge(nuts_0, left_on='Country',right_on='description', how = 'left')["code"]
eu_msw_2021["Country"] = eu_msw_2021.merge(country_codes, left_on='geo', right_on = "Code", how = 'left')["NUTS_code"]

#adding LowKey codes
subs_main_parent = {'SLASH_flyAshesWasteInc':'19 01 13','SLASH_bottomAshesWasteInc':'19 01 11',
                    'SLASH_boilerAshesWasteInc':'19 01 15'}
eu_msw_2021['Substance main parent'] = eu_msw_2021['Stock/Flow ID'].map(subs_main_parent)

#Rearrange columns
eu_msw_2021[['Scenario', 'Data Quality', 'Reference', 'Remark 1', 'Remark 2', 'Remark 3']] = np.nan
eu_msw_2021 = eu_msw_2021[columns]
eu_msw_2021.to_csv('Data_Structure_Task4.1_Task4.2.csv')


#%% Class for plotting - not in use


class reg_plot:
    def __init__(self, eu_data, title):
        self.eu27 = eu_data
        self.title = title
        
    
    def plot_tog(eu27, eu_msw, title):
        fig, axs = plt.subplots(8, 4, figsize=(20, 35))
        axs=axs.flatten()
        legend_handles = []
        legend_labels = ['Generation%', 'Treatment%','Incineration%','Disposal%','Recycling%']
        i=0
        for region in eu27:
            reg_data = eu_msw.loc[[region]]
        
            #getting the proportion of different treatment methods
            reg_data["ICN%"] = reg_data["DSP_I_RCV_E"]/reg_data["GEN"]
            reg_data["TRT%"] = reg_data["TRT"]/reg_data["GEN"]
            reg_data["GEN%"] = reg_data["GEN"]/reg_data["GEN"]
            reg_data["DIS%"] = reg_data["DSP_L_OTH"]/reg_data["GEN"]
            reg_data["RCY%"] = reg_data["RCY"]/reg_data["GEN"]
        
            #plotting time series of treatment %
        
            lines=axs[i].plot(reg_data.index.get_level_values("TIME_PERIOD").values,reg_data["GEN%"],color='black', linewidth=1)
            legend_handles.extend(lines)
            lines = axs[i].plot(reg_data.index.get_level_values("TIME_PERIOD").values,reg_data["TRT%"],color='red', linewidth=1)
            legend_handles.extend(lines)
            lines = axs[i].plot(reg_data.index.get_level_values("TIME_PERIOD").values,reg_data["ICN%"],color='blue', linewidth=1)
            legend_handles.extend(lines)
            lines = axs[i].plot(reg_data.index.get_level_values("TIME_PERIOD").values,reg_data["DIS%"],color='orchid', linewidth=1)
            legend_handles.extend(lines)
            lines = axs[i].plot(reg_data.index.get_level_values("TIME_PERIOD").values,reg_data["RCY%"],color='green', linewidth=1)
            legend_handles.extend(lines)
        
            #plt.xlabel('years')
            #plt.ylabel('Transfer coefficients')
            axs[i].set_title('Time Series of MSW treatment for ' + region)
            #plt.legend(loc="upper right", prop={'size': 8})
            #plt.show()
            i+=1
        
        # Add a common legend for the entire figure in the empty subplot
    
        legend_subplot = plt.subplot(8,4, 32)
        legend_subplot.axis('off')  
        legend_subplot.legend(legend_handles, legend_labels, loc='center', bbox_to_anchor=(0.5, 0.5), fontsize= 20)
        
        title = fig.suptitle(title, fontsize=30)
        title.set_position([0.5,0.95])
        plt.tight_layout(rect=[0, 0, 0.9, 0.95])
        
#%% Bulk flow file
#%%% Plotting trends of MSW generation for all regions

for region in eu27:
    reg_data = eu_msw.loc[[region]]
   
    plt.plot(reg_data.index.get_level_values("TIME_PERIOD").values,reg_data["GEN"],color='black', linewidth=1)
   
    plt.xlabel('years')
    plt.ylabel('MSW Generation in thousand tonnes')
    plt.title('Time Series of MSW treatment for ' + region)
    plt.savefig('./gen_plots/'+region+'.png',dpi='figure')
    plt.close()
#%%%%Creating one plot of all trends

def wb_fit(msw_data, gdp_data, base_year):
    #for the given gdp data, and base year, the function returns the corresponding 
    #projections of msw generation in the years for which gdp per cap is provided
    #following the world bank regression model
    fit = [29.43, -419.73 , 1647.41]
    x = gdp_data["Value"].values
    time = gdp_data["TIME"].values
    proxy_waste_gen = fit_fun(x,fit)
    proxy_waste_gen_base = fit_fun(gdp_data.loc[gdp_data["TIME"]==base_year]["Value"].values,fit)
    waste_gen_base = msw_data.loc[msw_data["TIME_PERIOD"]==base_year]["GEN"].values
    y = proxy_waste_gen/proxy_waste_gen_base * waste_gen_base
    predicted_msw_generation = pd.DataFrame({'TIME_PERIOD':time, 'GEN':y})
    return(predicted_msw_generation)

eu_msw = eu_msw[eu_msw['Country']!='EU27_2020']
eu27 = eu_msw.Country.unique()

fig, axs = plt.subplots(8, 4, figsize=(20, 35))
axs=axs.flatten()
legend_handles = []
legend_labels = ['MSW Generation', 'WB Model']


i=0
for region in eu27:
    reg_data = eu_msw.loc[eu_msw['Country']==region]
    
    
    #plotting time series of treatment %
    
    lines = axs[i].plot(reg_data["TIME_PERIOD"],reg_data["GEN"],'o', color='black', linewidth=1)
    legend_handles.extend(lines)
    year = np.arange(1995, 2051)
    gdp_data = gdp.loc[(gdp["LOCATION"]==country)&(gdp["TIME"].isin(year))]
    predict_msw = wb_fit(msw_data,gdp_data, base_year)
    #predict_msw = predict_msw.loc[predict_msw["TIME_PERIOD"]!=base_year]
    lines = axs[i].plot(year,predict_msw,'-', color='green', linewidth=1)
    legend_handles.extend(lines)
    #plt.xlabel('years')
    #plt.ylabel('Transfer coefficients')
    axs[i].set_title('Time Series of MSW Generation for ' + region)
    
    
    i+=1


# Add a common legend below the subplots
fig.subplots_adjust(bottom=0.05)
legend_subplot = fig.add_axes([0.1, 0.02, 0.8, 0.02])  
legend_subplot.axis('off')
legend_subplot.legend(legend_handles, legend_labels, loc='center', ncol=6, fontsize=15)

# Add a title for the entire figure
title = fig.suptitle('MSW Generation & WB  model', fontsize=30)
title.set_position([0.45, 0.95])
#title.set_y(0.95)
plt.show()



    
#%%% Plotting trends of treatment method for all regions

#saving separate plots  for each region
for region in eu27:
    reg_data = eu_msw.loc[[region]]
    
    #getting the proportion of different treatment methods
    reg_data["INC%"] = reg_data["DSP_I_RCV_E"]/reg_data["GEN"]
    reg_data["TRT%"] = reg_data["TRT"]/reg_data["GEN"]
    reg_data["GEN%"] = reg_data["GEN"]/reg_data["GEN"]
    reg_data["DIS%"] = reg_data["DSP_L_OTH"]/reg_data["GEN"]
    reg_data["RCY%"] = reg_data["RCY"]/reg_data["GEN"]
    
    #plotting time series of treatment %
    
    plt.plot(reg_data.index.get_level_values("TIME_PERIOD").values,reg_data["GEN%"],color='black', label='Generation%', linewidth=1)
    plt.plot(reg_data.index.get_level_values("TIME_PERIOD").values,reg_data["TRT%"],color='red', label='Treatment %', linewidth=1)
    plt.plot(reg_data.index.get_level_values("TIME_PERIOD").values,reg_data["INC%"],color='blue', label='Incineration %', linewidth=1)
    plt.plot(reg_data.index.get_level_values("TIME_PERIOD").values,reg_data["DIS%"],color='orchid', label='Disposal %', linewidth=1)
    plt.plot(reg_data.index.get_level_values("TIME_PERIOD").values,reg_data["RCY%"],color='green', label='Recycling %', linewidth=1)
    
    plt.xlabel('years')
    plt.ylabel('Transfer coefficients')
    plt.title('Time Series of MSW treatment for ' + region)
    plt.legend(loc="upper right", prop={'size': 8})
    plt.savefig('./treatment_plots/'+region+'.png',dpi='figure')
    plt.close()

""" #Creating one plot of all trends

fig, axs = plt.subplots(8, 4, figsize=(20, 35))
axs=axs.flatten()
legend_handles = []
legend_labels = ['Generation%', 'Treatment%','Incineration%','Disposal%','Recycling%']
i=0
for region in eu27:
    reg_data = eu_msw.loc[[region]]
    
    #getting the proportion of different treatment methods
    reg_data["ICN%"] = reg_data["DSP_I_RCV_E"]/reg_data["GEN"]
    reg_data["TRT%"] = reg_data["TRT"]/reg_data["GEN"]
    reg_data["GEN%"] = reg_data["GEN"]/reg_data["GEN"]
    reg_data["DIS%"] = reg_data["DSP_L_OTH"]/reg_data["GEN"]
    reg_data["RCY%"] = reg_data["RCY"]/reg_data["GEN"]
    
    #plotting time series of treatment %
    
    lines=axs[i].plot(reg_data.index.get_level_values("TIME_PERIOD").values,reg_data["GEN%"],color='black', linewidth=1)
    legend_handles.extend(lines)
    lines = axs[i].plot(reg_data.index.get_level_values("TIME_PERIOD").values,reg_data["TRT%"],color='red', linewidth=1)
    legend_handles.extend(lines)
    lines = axs[i].plot(reg_data.index.get_level_values("TIME_PERIOD").values,reg_data["ICN%"],color='blue', linewidth=1)
    legend_handles.extend(lines)
    lines = axs[i].plot(reg_data.index.get_level_values("TIME_PERIOD").values,reg_data["DIS%"],color='orchid', linewidth=1)
    legend_handles.extend(lines)
    lines = axs[i].plot(reg_data.index.get_level_values("TIME_PERIOD").values,reg_data["RCY%"],color='green', linewidth=1)
    legend_handles.extend(lines)
    
    #plt.xlabel('years')
    #plt.ylabel('Transfer coefficients')
    axs[i].set_title('Time Series of MSW treatment for ' + region)
    #plt.legend(loc="upper right", prop={'size': 8})
    #plt.show()
    i+=1
    
# Add a common legend for the entire figure in the empty subplot

legend_subplot = plt.subplot(8,4, 32)
legend_subplot.axis('off')  
legend_subplot.legend(legend_handles, legend_labels, loc='center', bbox_to_anchor=(0.5, 0.5), fontsize= 20)

title = fig.suptitle('Trends of MSW treatment method for EU 27+4 Countries', fontsize=30)
title.set_position([0.5,0.95])
plt.tight_layout(rect=[0, 0, 0.9, 0.95])
"""

#%%% Comparing Energy recovery and Incineration without energy recovery

#%%% World Bank fit and fit function
gdp = pd.read_csv('data_downloads/OECD_gdp.csv')
gdp = gdp[gdp["LOCATION"].isin(country_codes["NUTS_code"])]
pop= gdp.loc[(gdp["VARIABLE"]=='POP')& (gdp["Scenario"]=='Baseline')]
gdp = gdp.loc[(gdp["VARIABLE"]=='GDPVD_CAP')& (gdp["Scenario"]=='Baseline')]
base_year = 2016

def fit_fun(x,fit):
    #for the specified parameters, this function returns the log fit 
    return(fit[2]+fit[1]*np.log(x)+fit[0]*np.log(x)*np.log(x))

def wb_fit(msw_data, gdp_data, base_year):
    #for the given gdp data, and base year, the function returns the corresponding 
    #projections of msw generation in the years for which gdp per cap is provided
    #following the world bank regression model
    fit = [29.43, -419.73 , 1647.41]
    x = gdp_data["Value"].values
    time = gdp_data["TIME"].values
    proxy_waste_gen = fit_fun(x,fit)
    proxy_waste_gen_base = fit_fun(gdp_data.loc[gdp_data["TIME"]==base_year]["Value"].values,fit)
    waste_gen_base = msw_data.loc[msw_data["TIME_PERIOD"]==base_year]["GEN"].values
    y = proxy_waste_gen/proxy_waste_gen_base * waste_gen_base
    predicted_msw_generation = pd.DataFrame({'TIME_PERIOD':time, 'GEN':y})
    return(predicted_msw_generation)

# getting the projections of msw generated for the missing data in years 2020, 2021
filtered_rows = missing_data.loc[(missing_data['TIME_PERIOD']>=2020)]
filtered_rows['GEN'] = np.nan
base_year = 2016
for index, row in filtered_rows.iterrows():
    country = row['Country']
    year = row['TIME_PERIOD']
    msw_data = eu_msw.loc[eu_msw['Country']==country]
    gdp_data = gdp.loc[(gdp["LOCATION"]==country)&(gdp["TIME"].isin([base_year, year]))]
    predict_msw = wb_fit(msw_data,gdp_data, base_year)
    predict_msw = predict_msw.loc[predict_msw["TIME_PERIOD"]!=base_year]
    predict_msw['Country'] = country
    predict_msw['unit'] = 'THS_T'
    filtered_rows.loc[(filtered_rows['Country'] == country) & (filtered_rows['TIME_PERIOD'] == year), ['GEN']] = predict_msw['GEN'].values





for region in eu27:
    reg_data = eu_msw.loc[[region]]
    
    #getting the proportion of different treatment methods
    reg_data["INC%"] = reg_data["DSP_I"]/reg_data["DSP_I_RCV_E"]
    reg_data["RCV_E%"] = reg_data["RCV_E"]/reg_data["DSP_I_RCV_E"]
    
    
    #plotting time series of treatment %
    
    plt.plot(reg_data.index.get_level_values("TIME_PERIOD").values,reg_data["INC%"],color='black', label='Incineration without Energy Recovery%', linewidth=1)
    plt.plot(reg_data.index.get_level_values("TIME_PERIOD").values,reg_data["RCV_E%"],color='green', label='Energy Recovery %', linewidth=1)

   
    plt.xlabel('years')
    plt.ylabel('Proportion of total Incineration')
    plt.title('Incineration with and without Energy Recovery for ' + region)
    plt.legend(loc="upper right", prop={'size': 8})
    plt.savefig('./energy_recovery_plots/'+region+'.png',dpi='figure')
    #plt.show()
    plt.close()

                     





#%% Projections file: Log fit
#%%% Defining functions for log fit
def fit_fun(x,fit):
    #for the specified parameters, this function returns the log fit 
    return(fit[1]+fit[0]*np.log(x))
    
def L(params, years):   
    return(params[0]+params[1]*np.log(years))

def L_fut(params, years):
    l = params[0]+params[1]*np.log(years)
    return np.clip(l,0,1)    
    #return(params[0]+params[1]*np.log(years))

def R(params, years): 
    return (params[2] + params[3] * np.log(years))

def R_fut(params, years):
    r = params[2]+params[3]*np.log(years)
    return np.clip(r,0,1) 
    

def I(params, years):
    return (1 - L(params, years) - R(params, years))

def I_fut(params, years):
    i = 1 - L_fut(params, years) - R_fut(params, years)
    return np.clip(i,0,1)
    #return (1 - L_fut(params, years) - R_fut(params, years))

def con_1(params, years):
    return (1-L(params,years))
def con_2(params, years):
    return (1-R(params,years))
def con_3(params, years):
    return (0.65-I(params,years))

def objective(params, years, inc_obs, dis_obs, rcy_obs):
    l = L(params,years)
    r = R(params, years)
    i = I(params, years)
    d_l = np.sum((l - dis_obs)**2)
    d_r = np.sum((r - rcy_obs)**2)
    d_i = np.sum((i - inc_obs)**2)
    return d_l + d_r + d_i


def initial_param(reg_data):
    t_1 = reg_data.iloc[0]["TIME_PERIOD"]
    t_2 = reg_data.iloc[-1]["TIME_PERIOD"]
    dis_1 = reg_data.iloc[0]["DIS%"]
    dis_2 = reg_data.iloc[-1]["DIS%"]
    rcy_1 = reg_data.iloc[0]["RCY%"]
    rcy_2 = reg_data.iloc[-1]["RCY%"]
    initial_params = [0,0,0,0]
    initial_params[1] = (dis_2 - dis_1)/(t_2-t_1)
    initial_params[0] = dis_1 - initial_params[1]*t_1
    initial_params[3] = (rcy_2 - rcy_1)/(t_2-t_1)
    initial_params[2] = rcy_1 - initial_params[3]*t_1
    return initial_params


#%%%% Plotting for regions separately

for region in eu27:
    reg_data = eu_msw.loc[eu_msw["Country"]==region]
    initial_params = initial_param(reg_data)
    #years = np.arange(1995,2051)
    years = reg_data["TIME_PERIOD"].to_numpy()
    
    cons = [{'type': 'ineq', 'fun': partial(L, years=years)},
            {'type': 'ineq', 'fun': partial(R, years=years)},
            {'type': 'ineq', 'fun': partial(I, years=years)},
            {'type': 'ineq', 'fun': partial(con_1, years=years)},
            {'type': 'ineq', 'fun': partial(con_2, years=years)},
            {'type': 'ineq', 'fun': partial(con_3, years=years)}
            ]
    #years = reg_data["TIME_PERIOD"].to_numpy()
    result = minimize(objective, initial_params, args=(years, reg_data["INC%"].to_numpy(),reg_data["DIS%"].to_numpy(),reg_data["RCY%"].to_numpy()), constraints=cons)
    optimized_params = result.x
    
    x = reg_data["TIME_PERIOD"]
    y = reg_data["DIS%"]
    fig = plt.scatter(x,y,label = 'Landfill%')
    x = np.arange(1995,2051)
    plt.plot(x, L_fut(optimized_params, x),'-',label = 'Landfill % Trend')
    
    x = reg_data["TIME_PERIOD"]
    y = reg_data["RCY%"]
    plt.scatter(x,y,label = 'Recyling%')
    x = np.arange(1995,2051)
    plt.plot(x, R_fut(optimized_params, x),'-',label = 'Recycling % Trend')
  
    
    x = reg_data["TIME_PERIOD"]
    y = reg_data["INC%"]
    plt.scatter(x,y,label = 'Incineration%')
    x = np.arange(1995,2051)
    plt.plot(x, I_fut(optimized_params, x),'-',label = 'Incineration % Trend')
  
    
    plt.xlabel('Year')
    plt.ylabel('Treatment %')
    plt.title('Future Landfill % ' + region)
    plt.legend(loc="upper right", prop={'size': 8})
    plt.show()
    #plt.savefig('./landfill_projections/'+region+'.png',dpi='figure')

#%%%% One plot for all regions

fig, axs = plt.subplots(8, 4, figsize=(20, 35))
axs=axs.flatten()
legend_handles = []
legend_labels = ['Landfill%','Landfill% Trend', 'Recycling%', 'Recycling% Trend', 'Incineration%','Incineration% Trend']

i=0
for region in eu27:
    reg_data = eu_msw.loc[eu_msw['Country']==region]
    
    
    #running the minimize function
    initial_params = initial_param(reg_data)
    #years = np.arange(1995,2051)
    years = reg_data["TIME_PERIOD"].to_numpy()
    cons = [{'type': 'ineq', 'fun': partial(L, years=years)},
            {'type': 'ineq', 'fun': partial(R, years=years)},
            {'type': 'ineq', 'fun': partial(I, years=years)},
            {'type': 'ineq', 'fun': partial(con_1, years=years)},
            {'type': 'ineq', 'fun': partial(con_2, years=years)},
            {'type': 'ineq', 'fun': partial(con_3, years=years)}
            ]
    #years = reg_data["TIME_PERIOD"].to_numpy()
    result = minimize(objective, initial_params, args=(years, reg_data["INC%"].to_numpy(),reg_data["DIS%"].to_numpy(),reg_data["RCY%"].to_numpy()), constraints=cons)
    optimized_params = result.x
    
    
    #plotting time series of Landfill %
    x = reg_data["TIME_PERIOD"]
    y = reg_data["DIS%"]
    lines = axs[i].plot(x,y,'o', label='Landfill%', color = '#1f77b4')
    legend_handles.extend(lines)
    x = np.arange(1995,2051)
    lines = axs[i].plot(x, L_fut(optimized_params, x),'-',label = 'Landfill% Trend', color = '#1f77b4')
    legend_handles.extend(lines)
    
    #plotting time series of recycling %
    x = reg_data["TIME_PERIOD"]
    y = reg_data["RCY%"]
    lines = axs[i].plot(x,y,'o', label = 'Recycling%', color='#ff7f0e')
    legend_handles.extend(lines)
    x = np.arange(1995,2051)
    lines = axs[i].plot(x, R_fut(optimized_params, x),'-',label = 'Recycling% Trend',  color='#ff7f0e')
    legend_handles.extend(lines)
    
    #plotting time series of recycling %
    x = reg_data["TIME_PERIOD"]
    y = reg_data["INC%"]
    lines = axs[i].plot(x,y, 'o', label = 'Incineration%', color = '#2ca02c')
    legend_handles.extend(lines)
    x = np.arange(1995,2051)
    lines = axs[i].plot(x, I_fut(optimized_params, x),'-',label = 'Incineration% Trend', color = '#2ca02c')
    legend_handles.extend(lines)
    
    axs[i].set_title('Projection of treatment method for ' + region)
    i+=1

# Adjust layout to make space for legend and heading
plt.tight_layout(rect=[0, 0, 0.9, 0.93])

# Set axis labels for subplots
for ax in axs:
    ax.set_xlabel('Years')
    ax.set_ylabel('Treatment %')

# Add a common legend below the subplots
fig.subplots_adjust(bottom=0.05)
legend_subplot = fig.add_axes([0.1, 0.02, 0.8, 0.02])  
legend_subplot.axis('off')
legend_subplot.legend(legend_handles, legend_labels, loc='center', ncol=6, fontsize=15)

# Add a title for the entire figure
title = fig.suptitle('Method III: Constrained Regression for 1995-2021, degree 1, constrain for future', fontsize=30)
title.set_position([0.45, 0.95])
#title.set_y(0.95)
plt.show()
    

#%%% Plots for historic trends of Treatment %
#saving separate plots  for each region
for region in eu27:
    reg_data = eu_msw.loc[eu_msw["Country"]==region]
    
    #plotting time series of treatment %
    
    plt.plot(reg_data["TIME_PERIOD"],reg_data["GEN%"],color='black', label='Generation%', linewidth=1)
    plt.plot(reg_data["TIME_PERIOD"],reg_data["TRT%"],color='red', label='Treatment %', linewidth=1)
    plt.plot(reg_data["TIME_PERIOD"],reg_data["INC%"],color='blue', label='Incineration %', linewidth=1)
    plt.plot(reg_data["TIME_PERIOD"],reg_data["DIS%"],color='orchid', label='Disposal %', linewidth=1)
    plt.plot(reg_data["TIME_PERIOD"],reg_data["RCY%"],color='green', label='Recycling %', linewidth=1)
    
    plt.xlabel('years')
    plt.ylabel('Transfer coefficients')
    plt.title('Time Series of MSW treatment for ' + region)
    plt.legend(loc="upper right", prop={'size': 8})
    plt.show()
    #plt.savefig('./treatment_plots/'+region+'.png',dpi='figure')
    #plt.close()

""" #Creating one plot of all trends

fig, axs = plt.subplots(8, 4, figsize=(20, 35))
axs=axs.flatten()
legend_handles = []
legend_labels = ['Generation%', 'Treatment%','Incineration%','Disposal%','Recycling%']
i=0
for region in eu27:
    reg_data = eu_msw.loc[[region]]
    
    
    #plotting time series of treatment %
    
    lines=axs[i].plot(reg_data["TIME_PERIOD"].values,reg_data["GEN%"],color='black', linewidth=1)
    legend_handles.extend(lines)
    lines = axs[i].plot(reg_data["TIME_PERIOD"].values,reg_data["TRT%"],color='red', linewidth=1)
    legend_handles.extend(lines)
    lines = axs[i].plot(reg_data["TIME_PERIOD"].values,reg_data["ICN%"],color='blue', linewidth=1)
    legend_handles.extend(lines)
    lines = axs[i].plot(reg_data["TIME_PERIOD"].values,reg_data["DIS%"],color='orchid', linewidth=1)
    legend_handles.extend(lines)
    lines = axs[i].plot(reg_data["TIME_PERIOD"].values,reg_data["RCY%"],color='green', linewidth=1)
    legend_handles.extend(lines)
    
    #plt.xlabel('years')
    #plt.ylabel('Transfer coefficients')
    axs[i].set_title('Time Series of MSW treatment for ' + region)
    #plt.legend(loc="upper right", prop={'size': 8})
    #plt.show()
    i+=1
    
# Add a common legend for the entire figure in the empty subplot

legend_subplot = plt.subplot(8,4, 32)
legend_subplot.axis('off')  
legend_subplot.legend(legend_handles, legend_labels, loc='center', bbox_to_anchor=(0.5, 0.5), fontsize= 20)

title = fig.suptitle('Trends of MSW treatment method for EU 27+4 Countries', fontsize=30)
title.set_position([0.5,0.95])
plt.tight_layout(rect=[0, 0, 0.9, 0.95])
"""


#%%% S fit using curve fit

"""
Note:
    curve_fit function is used to perform trend analysis by optimizing the logistic 
    function to fit the historic data of INC%, RCY% and DIS%. The following two 
    sections of code perform the optimization and plotting fo rthe EU regions separately
    and together in one plot, respectively. 
    
    maxfev is set to 10000
    
    
    initial params are set using the first data point - and the plot is made form the first data point - this fixes the issue with HRV
    in the first run, no bounds are set - this leads to RCY% for SVK blowing to >1
    in the second run bounds are set for L2 to be <1. This solves the issue for SVK. But the issue with EST remains
    in the third run bound are also set for k2 to be >0. This forces the RCY% trend curve to be increasing always. This siolves the issue with EST. The issue with INC% <0 for some past values remains.
    
"""

#%%%% For regions separately

for region in eu27:
    reg_data = eu_msw.loc[eu_msw["Country"]==region]
    years = reg_data["TIME_PERIOD"].to_numpy()
    
    
    #Landfill%
    initial_guess = [reg_data.iloc[0]["DIS%"], -1, reg_data.iloc[0]["TIME_PERIOD"]]  # Initial guess for parameters L, k, x0
    params_D, covariance_D = curve_fit(logistic_fun, years, reg_data["DIS%"], p0=initial_guess, maxfev = 10000)
    # Extract the fitted parameters
    L_fit, k_fit, x0_fit = params_D
    
    x = reg_data["TIME_PERIOD"]
    y = reg_data["DIS%"]
    fig = plt.scatter(x,y,label = 'Landfill%')
    x = np.arange(reg_data.iloc[0]["TIME_PERIOD"],2051)
    plt.plot(x, logistic_fun(x, L_fit, k_fit, x0_fit),'-',label = 'Landfill % Trend')
    
    
    #Recycling %
    initial_guess = [reg_data.iloc[0]["RCY%"], 1, reg_data.iloc[0]["TIME_PERIOD"]]  # Initial guess for parameters L, k, x0
    params_R, covariance_R = curve_fit(logistic_fun, years, reg_data["RCY%"], p0=initial_guess,  maxfev = 10000,  bounds = ([-np.inf, 0, -np.inf],[1,np.inf, np.inf]))
    # Extract the fitted parameters
    L_fit, k_fit, x0_fit = params_R
    
    x = reg_data["TIME_PERIOD"]
    y = reg_data["RCY%"]
    plt.scatter(x,y,label = 'Recyling%')
    x = np.arange(reg_data.iloc[0]["TIME_PERIOD"],2051)
    plt.plot(x, logistic_fun(x, L_fit, k_fit, x0_fit),'-',label = 'Recycling % Trend')
  
    #Incineration%
    x = reg_data["TIME_PERIOD"]
    y = reg_data["INC%"]
    plt.scatter(x,y,label = 'Incineration%')
    x = np.arange(reg_data.iloc[0]["TIME_PERIOD"],2051)
    plt.plot(x, I(x, params_D, params_R),'-',label = 'Incineration % Trend')
  
    
    plt.xlabel('Year')
    plt.ylabel('Treatment %')
    plt.title('Future Treatment % ' + region)
    plt.legend(loc="upper right", prop={'size': 8})
    plt.show()
    print(region,' ', params_D, ' ', params_R, '/n')

#%%%% Curve-fit: One plot for all regions

fig, axs = plt.subplots(8, 4, figsize=(20, 35))
axs=axs.flatten()
legend_handles = []
legend_labels = ['Landfill%','Landfill% Trend', 'Recycling%', 'Recycling% Trend', 'Incineration%','Incineration% Trend']

i=0
for region in eu27:
    reg_data = eu_msw.loc[eu_msw['Country']==region]
    years = reg_data["TIME_PERIOD"].to_numpy()

    #Landfill%
    initial_guess = [reg_data.iloc[0]["DIS%"], -1, reg_data.iloc[0]["TIME_PERIOD"]]  # Initial guess for parameters L, k, x0
    params_D, covariance_D = curve_fit(logistic_fun, years, reg_data["DIS%"], p0=initial_guess, maxfev = 10000)
    
    
    # Extract the fitted parameters
    L_fit, k_fit, x0_fit = params_D
    
    #plotting time series of Landfill#
    x = reg_data["TIME_PERIOD"]
    y = reg_data["DIS%"]
    lines = axs[i].plot(x,y,'o', label='Landfill%', color = '#1f77b4')
    legend_handles.extend(lines)
    x = np.arange(reg_data.iloc[0]["TIME_PERIOD"],2051)
    
    lines = axs[i].plot(x, logistic_fun(x, L_fit, k_fit, x0_fit),'-',label = 'Landfill% Trend', color = '#1f77b4')
    legend_handles.extend(lines)
    
    #Recycling %
    initial_guess = [reg_data.iloc[0]["RCY%"], 1,reg_data.iloc[0]["TIME_PERIOD"]]  # Initial guess for parameters L, k, x0
    params_R, covariance_R = curve_fit(logistic_fun, years, reg_data["RCY%"], p0=initial_guess,  maxfev = 10000, bounds = ([-np.inf, 0, -np.inf],[1,np.inf, np.inf]))
    # Extract the fitted parameters
    L_fit, k_fit, x0_fit = params_R
    
    #plotting time series of recycling %
    x = reg_data["TIME_PERIOD"]
    y = reg_data["RCY%"]
    lines = axs[i].plot(x,y,'o', label = 'Recycling%', color='#ff7f0e')
    legend_handles.extend(lines)
    x = np.arange(reg_data.iloc[0]["TIME_PERIOD"],2051)
    lines = axs[i].plot(x, logistic_fun(x, L_fit, k_fit, x0_fit),'-',label = 'Recycling% Trend',  color='#ff7f0e')
    legend_handles.extend(lines)
    
    #plotting time series of recycling %
    x = reg_data["TIME_PERIOD"]
    y = reg_data["INC%"]
    lines = axs[i].plot(x,y, 'o', label = 'Incineration%', color = '#2ca02c')
    legend_handles.extend(lines)
    x = np.arange(reg_data.iloc[0]["TIME_PERIOD"],2051)
    lines = axs[i].plot(x, I(x, params_D, params_R),'-',label = 'Incineration% Trend', color = '#2ca02c')
    legend_handles.extend(lines)
    
    axs[i].set_title('Projections of treatment method for ' + region)
    print(region,' ', params_D, ' ', params_R, '/n')
    i+=1

# Adjust layout to make space for legend and heading
plt.tight_layout(rect=[0, 0, 0.9, 0.93])

# Set axis labels for subplots
for ax in axs:
    ax.set_xlabel('Years')
    ax.set_ylabel('Treatment %')

# Add a common legend below the subplots
fig.subplots_adjust(bottom=0.05)
legend_subplot = fig.add_axes([0.1, 0.02, 0.8, 0.02])  
legend_subplot.axis('off')
legend_subplot.legend(legend_handles, legend_labels, loc='center', ncol=6, fontsize=15)

# Add a title for the entire figure
title = fig.suptitle('Logistic Regression of Treatment methods', fontsize=30)
title.set_position([0.45, 0.95])
#title.set_y(0.95)
plt.show()


#%%% Sfit - minimization with constraints, Plotting for regions separately

for region in eu27:
    reg_data = eu_msw.loc[eu_msw["Country"]==region]
    years = reg_data["TIME_PERIOD"].to_numpy()
    initial_params = [2*reg_data.iloc[0]["DIS%"], -1, reg_data.iloc[0]["TIME_PERIOD"], 2*reg_data.iloc[0]["RCY%"], 1, reg_data.iloc[0]["TIME_PERIOD"]]
    
    cons = [{'type': 'ineq', 'fun': partial(D, years=years)},
            {'type': 'ineq', 'fun': partial(R, years=years)},
            {'type': 'ineq', 'fun': partial(I_con, years=years)},
            {'type': 'ineq', 'fun': partial(con_1, years=years)},
            {'type': 'ineq', 'fun': partial(con_2, years=years)},
            {'type': 'ineq', 'fun': partial(con_3, years=years)}
            ]
    
    
    results = minimize(objective, initial_params, args=(years, reg_data["INC%"].to_numpy(),reg_data["DIS%"].to_numpy(),reg_data["RCY%"].to_numpy()), constraints=cons, options ={ 'maxfev': 10000})
    
    # Extract the fitted parameters
    params = results.x
    params_D = params[0:3]
    params_R = params[3:]
    
    #Landfill%
    L_fit, k_fit, x0_fit = params_D
    
    x = reg_data["TIME_PERIOD"]
    y = reg_data["DIS%"]
    fig = plt.scatter(x,y,label = 'Landfill%')
    x = np.arange(1995,2051)
    plt.plot(x, logistic_fun(x, L_fit, k_fit, x0_fit),'-',label = 'Landfill % Trend')
    
    
    #Recycling %
    # Extract the fitted parameters
    L_fit, k_fit, x0_fit = params_R
    
    x = reg_data["TIME_PERIOD"]
    y = reg_data["RCY%"]
    plt.scatter(x,y,label = 'Recyling%')
    x = np.arange(1995,2051)
    plt.plot(x, logistic_fun(x, L_fit, k_fit, x0_fit),'-',label = 'Recycling % Trend')
  
    #Incineration%
    x = reg_data["TIME_PERIOD"]
    y = reg_data["INC%"]
    plt.scatter(x,y,label = 'Incineration%')
    x = np.arange(1995,2051)
    plt.plot(x, I(x, params_D, params_R),'-',label = 'Incineration % Trend')
  
    
    plt.xlabel('Year')
    plt.ylabel('Treatment %')
    plt.title('Future Treatment % ' + region)
    plt.legend(loc="upper right", prop={'size': 8})
    plt.show()
    print(region,' ', params_D, ' ', params_R, '/n')
#%%% S-fit using minimize and constraint for D+R < 1

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
    return (1-logistic_fun(years,params[0], params[1], params[2]) - logistic_fun(years,params[3], params[4], params[5]))


#%%%% Plotting for regions separately

for region in eu27:
    reg_data = eu_msw.loc[eu_msw["Country"]==region]
    years = reg_data["TIME_PERIOD"].to_numpy()
    initial_params = [2*reg_data.iloc[0]["DIS%"], -1, reg_data.iloc[0]["TIME_PERIOD"], 2*reg_data.iloc[0]["RCY%"], 1, reg_data.iloc[0]["TIME_PERIOD"]]
    
    cons = [{'type': 'ineq', 'fun': partial(D, years=years)},
            {'type': 'ineq', 'fun': partial(R, years=years)},
            {'type': 'ineq', 'fun': partial(I_con, years=years)},
            {'type': 'ineq', 'fun': partial(con_1, years=years)}
            ]
    
    
    results = minimize(objective, initial_params, args=(years, reg_data["INC%"].to_numpy(),reg_data["DIS%"].to_numpy(),reg_data["RCY%"].to_numpy()), constraints=cons, options ={ 'maxfev': 10000})
    
    # Extract the fitted parameters
    params = results.x
    params_D = params[0:3]
    params_R = params[3:]
    
    #Landfill%
    L_fit, k_fit, x0_fit = params_D
    
    x = reg_data["TIME_PERIOD"]
    y = reg_data["DIS%"]
    fig = plt.scatter(x,y,label = 'Landfill%')
    x = np.arange(1995,2051)
    plt.plot(x, logistic_fun(x, L_fit, k_fit, x0_fit),'-',label = 'Landfill % Trend')
    
    
    #Recycling %
    # Extract the fitted parameters
    L_fit, k_fit, x0_fit = params_R
    
    x = reg_data["TIME_PERIOD"]
    y = reg_data["RCY%"]
    plt.scatter(x,y,label = 'Recyling%')
    x = np.arange(1995,2051)
    plt.plot(x, logistic_fun(x, L_fit, k_fit, x0_fit),'-',label = 'Recycling % Trend')
  
    #Incineration%
    x = reg_data["TIME_PERIOD"]
    y = reg_data["INC%"]
    plt.scatter(x,y,label = 'Incineration%')
    x = np.arange(1995,2051)
    plt.plot(x, I(x, params_D, params_R),'-',label = 'Incineration % Trend')
  
    
    plt.xlabel('Year')
    plt.ylabel('Treatment %')
    plt.title('Future Treatment % ' + region)
    plt.legend(loc="upper right", prop={'size': 8})
    plt.show()
    print(region,' ', params_D, ' ', params_R, '/n')

#%%%% S-fit: One plot for all regions

fig, axs = plt.subplots(8, 4, figsize=(20, 35))
axs=axs.flatten()
legend_handles = []
legend_labels = ['Landfill%','Landfill% Trend', 'Recycling%', 'Recycling% Trend', 'Incineration%','Incineration% Trend']

i=0
for region in eu27:
    reg_data = eu_msw.loc[eu_msw['Country']==region]
    
    #years = reg_data["TIME_PERIOD"].to_numpy()
    
    initial_params = [2*reg_data.iloc[0]["DIS%"], -1, reg_data.iloc[0]["TIME_PERIOD"], 2*reg_data.iloc[0]["RCY%"], 1, reg_data.iloc[0]["TIME_PERIOD"]]
    
    years = np.arange(1995,2051)
    cons = [{'type': 'ineq', 'fun': partial(D, years=years)},
            {'type': 'ineq', 'fun': partial(R, years=years)},
            {'type': 'ineq', 'fun': partial(I_con, years=years)},
            {'type': 'ineq', 'fun': partial(con_1, years=years)},
            ]
    
    years = reg_data["TIME_PERIOD"].to_numpy()
    
    results = minimize(objective, initial_params, args=(years, reg_data["INC%"].to_numpy(),reg_data["DIS%"].to_numpy(),reg_data["RCY%"].to_numpy()), constraints=cons, options ={ 'maxfev': 10000})
    
    # Extract the fitted parameters
    params = results.x
    params_D = params[0:3]
    params_R = params[3:]
    
    #Landfill%
    L_fit, k_fit, x0_fit = params_D
    
    #plotting time series of Landfill %
    x = reg_data["TIME_PERIOD"]
    y = reg_data["DIS%"]
    lines = axs[i].plot(x,y,'o', label='Landfill%', color = '#1f77b4')
    legend_handles.extend(lines)
    x = np.arange(1995,2051)
    lines = axs[i].plot(x, logistic_fun(x, L_fit, k_fit, x0_fit),'-',label = 'Landfill% Trend', color = '#1f77b4')
    legend_handles.extend(lines)
    
    #Recycling %
    # Extract the fitted parameters
    L_fit, k_fit, x0_fit = params_R
    
    #plotting time series of recycling %
    x = reg_data["TIME_PERIOD"]
    y = reg_data["RCY%"]
    lines = axs[i].plot(x,y,'o', label = 'Recycling%', color='#ff7f0e')
    legend_handles.extend(lines)
    x = np.arange(1995,2051)
    lines = axs[i].plot(x, logistic_fun(x, L_fit, k_fit, x0_fit),'-',label = 'Recycling% Trend',  color='#ff7f0e')
    legend_handles.extend(lines)
    
    #plotting time series of recycling %
    x = reg_data["TIME_PERIOD"]
    y = reg_data["INC%"]
    lines = axs[i].plot(x,y, 'o', label = 'Incineration%', color = '#2ca02c')
    legend_handles.extend(lines)
    x = np.arange(1995,2051)
    lines = axs[i].plot(x, I(x, params_D, params_R),'-',label = 'Incineration% Trend', color = '#2ca02c')
    legend_handles.extend(lines)
    
    axs[i].set_title('Projection of treatment method for ' + region)
    i+=1

# Adjust layout to make space for legend and heading
plt.tight_layout(rect=[0, 0, 0.9, 0.93])

# Set axis labels for subplots
for ax in axs:
    ax.set_xlabel('Years')
    ax.set_ylabel('Treatment %')

# Add a common legend below the subplots
fig.subplots_adjust(bottom=0.05)
legend_subplot = fig.add_axes([0.1, 0.02, 0.8, 0.02])  
legend_subplot.axis('off')
legend_subplot.legend(legend_handles, legend_labels, loc='center', ncol=6, fontsize=15)

# Add a title for the entire figure
title = fig.suptitle('Logistic regression: Minimization with constraints', fontsize=30)
title.set_position([0.45, 0.95])
#title.set_y(0.95)
plt.show()

#%% Scenarios

def value_at_2035(bau_data, treatment_method):
    return (bau_data[treatment_method].loc[(bau_data["TIME"]==2035)].values[0])
    
def option_1_rcy(bau_data):
    rec_rcy_data = pd.DataFrame(columns = ['TIME','RCY%'])
    dif_from_bau = (0.65-value_at_2035(bau_data,'RCY%'))/value_at_2035(bau_data,'RCY%')
    differences_from_2021 = pd.DataFrame({'TIME':np.arange(2021,2036),'Difference':  np.linspace(0, dif_from_bau, 15)}) #15=2035-2021+1
    print(differences_from_2021)
    #Get the REC data for RCY between 2021 and 2035
    rec_rcy_data['TIME'] = np.arange(2021,2036)
    rec_rcy_data['RCY%']= bau_data["RCY%"].loc[bau_data['TIME'].isin(np.arange(2021,2036))].reset_index(drop=True) * (1+differences_from_2021['Difference'])
    
    return rec_rcy_data

def option_1_dis(bau_data):
    rec_dis_data = pd.DataFrame(columns = ['TIME','DIS%'])
    dif_from_bau = (value_at_2035(bau_data,'DIS%')-0.1)/value_at_2035(bau_data,'DIS%')
    differences_from_2021 = pd.DataFrame({'TIME':np.arange(2021,2036),'Difference':  np.linspace(0, dif_from_bau, 15)}) #15=2035-2021+1
    print(differences_from_2021)
    #Get the REC data for RCY between 2021 and 2035
    rec_dis_data['TIME'] = np.arange(2021,2036)
    rec_dis_data['DIS%'] = bau_data['DIS%'].loc[bau_data['TIME'].isin(np.arange(2021,2036))].reset_index(drop=True) * (1-differences_from_2021['Difference'])
    
    return rec_dis_data

def get_rcy_until_2035(bau_data, option):
    if value_at_2035(bau_data,'RCY%')>= 0.65:
        rec_rcy = bau_data[['TIME','RCY%']].loc[bau_data['TIME'].isin(np.arange(2021,2036))]
        print('BAU')
    
    else:
        if option=='Option1':
            print('Option1')
            rec_rcy = option_1_rcy(bau_data)
    rec_rcy.reset_index(drop = True, inplace = True)   
    return rec_rcy

def get_dis_until_2035(bau_data, option):
    if value_at_2035(bau_data,'DIS%')<= 0.1:
        rec_dis = bau_data[['TIME','DIS%']].loc[bau_data['TIME'].isin(np.arange(2021,2036))]
        print('BAU')
    
    else:
        if option == 'Option1':
            print('Option1')
            rec_dis = option_1_dis(bau_data)
    rec_dis.reset_index(drop = True, inplace = True)
    return rec_dis

def get_inc_until_2035(bau_rcy,bau_dis):
    rec_inc_data = pd.DataFrame(columns = ['TIME','INC%'])
    rec_inc_data["TIME"]= np.arange(2021,2036)
    rec_inc_data['INC%'] = 1 - bau_rcy['RCY%'] - bau_dis['DIS%']
    print(rec_inc_data)
    return rec_inc_data

def get_rcy_until_2050(bau_data, option, params):
    if value_at_2035(bau_data,'RCY%')>= 0.65:
        rec_rcy = bau_data[['TIME','RCY%']].loc[bau_data['TIME'].isin(np.arange(2021,2051))]
        print('BAU')
    
    else:
        if option=='Option1':
            print('Option1')
            rec_rcy = option_1_rcy(bau_data)
        elif option=='Option2':
            print("Option2")
            data_at_2021, data_at_2035 = option_2_rcy(bau_data)
            print(data_at_2021, data_at_2035)
            new_parameter=params.copy()

            new_parameter["L2"]*=1.1
            
            new_parameter["x02"], new_parameter["k2"] = x0_k_option2(new_parameter["L2"].values[0], data_at_2021, data_at_2035)
            print(new_parameter)
            years = np.arange(2021,2051)
            rcy_data=R(new_parameter.values[0],years)
            rec_rcy = pd.DataFrame({'TIME':years,'RCY%':rcy_data})
        elif option=='Option3':
            data_at_2021, data_at_2035 = option_2_rcy(bau_data)
            
            new_parameter=params.copy()

            new_parameter["k2"]*=1.1
            print(new_parameter)
            new_parameter["x02"], new_parameter["L2"] = x0_L_option3(new_parameter["k2"].values[0], data_at_2021, data_at_2035)
            years = np.arange(2021,2051)
            rcy_data=R(new_parameter.values[0],years)
            rec_rcy = pd.DataFrame({'TIME':years,'RCY%':rcy_data})
    rec_rcy.reset_index(drop = True, inplace = True)   
    return rec_rcy

def get_dis_until_2050(bau_data, option, params):
    if value_at_2035(bau_data,'DIS%')<= 0.1:
        rec_dis = bau_data[['TIME','DIS%']].loc[bau_data['TIME'].isin(np.arange(2021,2051))]
        print('BAU')
    
    else:
        if option == 'Option1':
            print('Option1')
            
            rec_dis = option_1_dis(bau_data)
        elif option=='Option2':
            print("Option2")
            data_at_2021, data_at_2035 = option_2_dis(bau_data)
            
            new_parameter=params.copy()

            new_parameter["L1"]*=1.1
            
            new_parameter["x01"], new_parameter["k1"] = x0_k_option2(new_parameter["L1"].values[0], data_at_2021, data_at_2035)
            print(new_parameter)
            years = np.arange(2021,2051)
            dis_data=D(new_parameter.values[0],years)
            rec_dis = pd.DataFrame({'TIME':years,'DIS%':dis_data})
        elif option=='Option3':
            data_at_2021, data_at_2035 = option_2_dis(bau_data)
            
            new_parameter=params.copy()

            new_parameter["k1"]*=1.1
            print(new_parameter)
            
            new_parameter["x01"], new_parameter["L1"] = x0_L_option3(new_parameter["k1"].values[0], data_at_2021, data_at_2035)
            years = np.arange(2021,2051)
            dis_data=D(new_parameter.values[0],years)
            rec_dis = pd.DataFrame({'TIME':years,'RCY%':dis_data})
    rec_dis.reset_index(drop = True, inplace = True)
    return rec_dis

def get_inc_until_2050(rcy,dis):
    rec_inc_data = pd.DataFrame(columns = ['TIME','INC%'])
    rec_inc_data["TIME"]= np.arange(2021,2051)
    rec_inc_data['INC%'] = 1 - rcy['RCY%'] - dis['DIS%']
   #print(rec_inc_data)
    return rec_inc_data

def get_model(rec_rcy_data,rec_dis_data,rec_inc_data):
    reg_data = pd.merge(pd.merge(rec_rcy_data,rec_dis_data,on='TIME'),rec_inc_data,on='TIME')
    params = get_fit_R_D(reg_data)
    years = np.arange(2021,2051)
    rec_dis = D(params,years)
    rec_rcy=R(params,years)
    rec_inc=I(years,params)
    rec_data = pd.DataFrame({'TIME':years,'RCY%':rec_rcy,'DIS%':rec_dis,'INC%':rec_inc})
    
    return rec_data
#%% Options 2 and 3: Changing parameters and getting new fit

#Option 2: changing the amplitude parameter L
#Option 3: Changing the curvature parameter k

def option_2_dis(bau_data):
    data_at_2021 = (2021, bau_data['DIS%'].loc[(bau_data["TIME"]==2021)].values[0])
    data_at_2035 = (2035, 0.10)
    return (data_at_2021, data_at_2035)

def option_2_rcy(bau_data):
    data_at_2021 = (2021, bau_data['RCY%'].loc[(bau_data["TIME"]==2021)].values[0])
    data_at_2035 = (2035, 0.65)
    return (data_at_2021, data_at_2035)


def x0_k_option2(L, a, b):
    ax, ay = a
    bx, by = b
    print('CHECK', L/by-1)
    print('CHECK',L/ay-1)
    x0 = (ax*np.log((L/by)-1)-bx*np.log((L/ay)-1))/(np.log((L/by)-1)-np.log((L/ay)-1))
    k = (np.log((L/ay)-1)-np.log((L/by)-1))/(bx-ax)
    print(x0,k)
    return x0, k

def x0_L_option3(k, a, b):
    ax, ay = a
    bx, by = b
    x0 = np.log((by-ay)/(ay*np.exp(-k*ax)-by*np.exp(-k*bx)))/k
    L = ay*(1+np.exp(-k(ax-x0)))
    return x0, L

#%%Plotting 
option = 'Option3'   #options 1, 2 and 3
fig, axs = plt.subplots(8, 4, figsize=(20, 35))
axs=axs.flatten()
legend_handles = []
#legend_labels = ['Historic Landfill%','Landfill% Trend BAU','Landfill fit target','Landfill% Trend REC', 'Historic Recycling%', 'Recycling% Trend BAU', 'Recycling fit target','Recycling% Trend REC','Historic Incineration%','Incineration% Trend BAU', 'Incineration fit target','Incineration% Trend REC']
legend_labels = ['Historic Landfill%','Landfill% Trend BAU','Landfill% Trend REC', 'Historic Recycling%', 'Recycling% Trend BAU', 'Recycling% Trend REC','Historic Incineration%','Incineration% Trend BAU', 'Incineration% Trend REC']

i=0
for region in bau_data['LOCATION'].unique():
    print(region)
    reg_bau_data = bau_data.loc[bau_data['LOCATION']==region]
    params = parameter.loc[parameter['LOCATION']==region]
    params.drop(columns = 'LOCATION', inplace = True)
    
    #Option1
    
    # rec_dis_until_2035 = get_dis_until_2035(reg_bau_data,option)
    # print(rec_dis_until_2035)
    # rec_rcy_until_2035 = get_rcy_until_2035(reg_bau_data,option)
    # print(rec_rcy_until_2035)
    # rec_inc_until_2035 = get_inc_until_2035(rec_rcy_until_2035, rec_dis_until_2035)
    # reg_rec_data = get_model(rec_rcy_until_2035,rec_dis_until_2035,rec_inc_until_2035)
    # print(reg_rec_data)
    
    #option 2
    rec_rcy = get_rcy_until_2050(reg_bau_data,option, params)
    #print(rec_rcy)
    rec_dis = get_dis_until_2050(reg_bau_data,option, params)
    #print(rec_dis)
    
    rec_inc = get_inc_until_2050(rec_rcy, rec_dis)
    reg_rec_data = pd.DataFrame({'TIME':np.arange(2021,2051),'RCY%':rec_rcy['RCY%'],'DIS%':rec_dis['DIS%'],'INC%':rec_inc['INC%']})
    #print(reg_rec_data)
    
    #plotting time series of Landfill %
    lines = axs[i].plot(reg_bau_data.loc[reg_bau_data['TIME']<=2021]['TIME'],reg_bau_data.loc[reg_bau_data['TIME']<=2021]['DIS%'],'o', label='Historic Landfill%', color = '#1f77b4')
    legend_handles.extend(lines)
    x = np.arange(2010,2051)
    lines = axs[i].plot(x, reg_bau_data['DIS%'].loc[reg_bau_data['TIME'].isin(x)],'-',label = 'Landfill% Trend BAU', color = '#1f77b4')
    legend_handles.extend(lines)
    
    #Option 1
    # lines = axs[i].plot(rec_dis_until_2035['TIME'], rec_dis_until_2035['DIS%'],'o',label = 'Landfill% fit target', color = 'black')
    # legend_handles.extend(lines)
    
    lines = axs[i].plot(reg_rec_data['TIME'],reg_rec_data['DIS%'],'--',label = 'Landfill% Trend REC', color = '#1f77b4')
    legend_handles.extend(lines)
    
    #Recycling %
    
    #plotting time series of recycling %
    lines = axs[i].plot(reg_bau_data.loc[reg_bau_data['TIME']<=2021]['TIME'],reg_bau_data.loc[reg_bau_data['TIME']<=2021]['RCY%'],'o', label = 'Historic Recycling%', color='#ff7f0e')
    legend_handles.extend(lines)
    x = np.arange(2010,2051)
    lines = axs[i].plot(x, reg_bau_data['RCY%'].loc[reg_bau_data['TIME'].isin(x)],'-',label = 'Recycling% Trend BAU', color = '#ff7f0e')
    legend_handles.extend(lines)
    
    
    #Option 1
    # lines = axs[i].plot(rec_rcy_until_2035['TIME'], rec_rcy_until_2035['RCY%'],'o',label = 'Recycling% fit target', color = 'black')
    # legend_handles.extend(lines)
    
    lines = axs[i].plot(reg_rec_data['TIME'],reg_rec_data['RCY%'],'--',label = 'Recycling% Trend REC', color = '#ff7f0e')
    legend_handles.extend(lines)
    
    #plotting time series of incineration %
    lines = axs[i].plot(reg_bau_data.loc[reg_bau_data['TIME']<=2021]['TIME'],reg_bau_data.loc[reg_bau_data['TIME']<=2021]['INC%'], 'o', label = 'Historic Incineration%', color = '#2ca02c')
    legend_handles.extend(lines)
    x = np.arange(2010,2051)
    lines = axs[i].plot(x, reg_bau_data['INC%'].loc[reg_bau_data['TIME'].isin(x)],'-',label = 'Incineration% Trend BAU', color = '#2ca02c')
    legend_handles.extend(lines)
    
    #Option 1
    # lines = axs[i].plot(rec_inc_until_2035['TIME'], rec_inc_until_2035['INC%'],'o',label = 'Incineration% fit target', color = 'black')
    # legend_handles.extend(lines)
    
    lines = axs[i].plot(reg_rec_data['TIME'],reg_rec_data['INC%'],'--',label = 'Incineration% Trend REC', color = '#2ca02c')
    legend_handles.extend(lines)
    

    axs[i].set_title(region)
    i+=1

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
title = fig.suptitle('REC scenario: Option 2', fontsize=30)
title.set_position([0.45, 0.95])
#title.set_y(0.95)
plt.show()
    

#%% Case 1: Increase L2 by 10% (amplitude of RCY)


new_parameter=parameter.copy()

new_parameter["L2"]*=1.1


#%% Case 2: Increase k2 by 10% (curvature of RCY)

new_parameter=parameter.copy()

new_parameter["k2"]*=1.1

#%% Case 3: Decrease L1 by 10% (amplitude of DIS)

new_parameter=parameter.copy()

new_parameter["L1"]*=0.9

#%% Case 4: Increase k1 by 10% (curvature of DIS)

new_parameter=parameter.copy()

new_parameter["k1"]*=1.1

#%% Case 5: Decrease L1 and increase L2 by 10% (amplitude of DIS, RCY)

new_parameter=parameter.copy()

new_parameter["L1"]*=0.9
new_parameter['L2']*=1.1


#%% Case 6: Increase k1 and k2 by 10% (curvature of DIS)

new_parameter=parameter.copy()

new_parameter["k1"]*=1.1
new_parameter["k2"]*=1.1

#%% Getting INC% for all countries and the corresponding inc quantities

# for region in rec_data['LOCATION'].unique():
#     params = new_parameter.loc[new_parameter["LOCATION"]==region][['L1','k1','x01','L2','k2','x02']].values[0]
    
#     rec_data.loc[(rec_data['LOCATION']==region)&(rec_data['TIME'].isin(np.arange(
#         2022, 2051))),'INC%'] = I(np.arange(2022, 2051), params)
    
#     rec_data.loc[(rec_data['LOCATION']==region)&(rec_data['TIME'].isin(np.arange(
#         2022, 2051))),'DIS%'] = D(params, np.arange(2022, 2051))
    
#     rec_data.loc[(rec_data['LOCATION']==region)&(rec_data['TIME'].isin(np.arange(
#         2022, 2051))),'RCY%'] = R(params, np.arange(2022, 2051))
    
#     rec_data.loc[(rec_data['LOCATION']==region)&(rec_data['TIME'].isin(np.arange(
#         2022, 2051))),'INC_T'] = rec_data["INC%"]*rec_data['MSW_GEN_T']
            

#%% S-fit: One plot for all regions

fig, axs = plt.subplots(8, 4, figsize=(20, 35))
axs=axs.flatten()
legend_handles = []
legend_labels = ['Historic Landfill%','Landfill% Trend BAU','Landfill% Trend REC', 'Historic Recycling%', 'Recycling% Trend BAU', 'Recycling% Trend REC','Historic Incineration%','Incineration% Trend BAU', 'Incineration% Trend REC']

i=0
for region in bau_data['LOCATION'].unique():
    reg_bau_data = bau_data.loc[bau_data['LOCATION']==region]
    #reg_rec_data = rec_data.loc[rec_data['LOCATION']==region]
    
    params = parameter.loc[parameter["LOCATION"]==region][['L1','k1','x01','L2','k2','x02']].values[0]
    new_params = new_parameter.loc[new_parameter["LOCATION"]==region][['L1','k1','x01','L2','k2','x02']].values[0]
    
    
    #plotting time series of Landfill %
    lines = axs[i].plot(reg_bau_data.loc[reg_bau_data['TIME']<=2021]['TIME'],reg_bau_data.loc[reg_bau_data['TIME']<=2021]['DIS%'],'o', label='Historic Landfill%', color = '#1f77b4')
    legend_handles.extend(lines)
    x = np.arange(2010,2051)
    lines = axs[i].plot(x, D(params, x),'-',label = 'Landfill% Trend BAU', color = '#1f77b4')
    legend_handles.extend(lines)
    
    lines = axs[i].plot(x, D(new_params,x),'--',label = 'Landfill% Trend REC', color = '#1f77b4')
    legend_handles.extend(lines)
    
    #Recycling %
    
    #plotting time series of recycling %
    lines = axs[i].plot(reg_bau_data.loc[reg_bau_data['TIME']<=2021]['TIME'],reg_bau_data.loc[reg_bau_data['TIME']<=2021]['RCY%'],'o', label = 'Historic Recycling%', color='#ff7f0e')
    legend_handles.extend(lines)
    x = np.arange(2010,2051)
    lines = axs[i].plot(x, R(params,x),'-',label = 'Recycling% Trend BAU',  color='#ff7f0e')
    legend_handles.extend(lines)
    
    lines = axs[i].plot(x, R(new_params,x),'--',label = 'Recycling% Trend REC', color = '#ff7f0e')
    legend_handles.extend(lines)
    
    #plotting time series of incineration %
    lines = axs[i].plot(reg_bau_data.loc[reg_bau_data['TIME']<=2021]['TIME'],reg_bau_data.loc[reg_bau_data['TIME']<=2021]['INC%'], 'o', label = 'Historic Incineration%', color = '#2ca02c')
    legend_handles.extend(lines)
    x = np.arange(2010,2051)
    lines = axs[i].plot(x, I(x, params),'-',label = 'Incineration% Trend BAU', color = '#2ca02c')
    legend_handles.extend(lines)
    
    lines = axs[i].plot(x, I(x, new_params),'--',label = 'Incineration% Trend REC', color = '#2ca02c')
    legend_handles.extend(lines)
    
    axs[i].set_title(region)
    i+=1

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
title = fig.suptitle('REC scenario- Case 6: Increase k1 and k2', fontsize=30)
title.set_position([0.45, 0.95])
#title.set_y(0.95)
plt.show()



