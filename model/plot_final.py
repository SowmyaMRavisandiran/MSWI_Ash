#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 20:30:39 2024

@author: marriyapillais
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager
import seaborn as sns

bau_data = pd.read_csv("data/results/BAU_MSW.csv")
rec_data = pd.read_csv("data/results/REC_MSW.csv")
cir_data = pd.read_csv("data/results/CIR_MSW.csv")

#%%Treatment trends plot

region='EU27+4'

reg_bau_data = bau_data.loc[bau_data['LOCATION']==region]
reg_rec_data = rec_data.loc[rec_data['LOCATION']==region]
reg_cir_data = cir_data.loc[cir_data['LOCATION']==region]


font_FTR = font_manager.FontProperties(fname='/Users/marriyapillais/Desktop/msw_model/FutuRaM_MSWI/Cabin_font_FutuRaM.ttf')
font_FTR.set_size(14)  # Set to your desired font size
font_label=font_manager.FontProperties(fname='/Users/marriyapillais/Desktop/msw_model/FutuRaM_MSWI/Cabin_font_FutuRaM.ttf')
font_label.set_size(10)
font_title = font_manager.FontProperties(fname='/Users/marriyapillais/Desktop/msw_model/FutuRaM_MSWI/Cabin_font_FutuRaM.ttf')
font_title.set_size(16)


#plotting time series of Landfill %
fig = plt.plot(reg_bau_data.loc[reg_bau_data['TIME']<=2021]['TIME'],reg_bau_data.loc[reg_bau_data['TIME']<=2021]['DIS%']*100,'o', label='Historic Landfill%', color = '#6b1b62', alpha=0.9, markersize=6)
sns.set(style="whitegrid")
x = np.arange(2010,2051)
plt.plot(x, reg_bau_data['DIS%'].loc[reg_bau_data['TIME'].isin(x)]*100,'-',label = 'BAU Scenario Landfill%', color = '#6b1b62', alpha=0.9, linewidth=2.5)

plt.plot(reg_rec_data.loc[reg_rec_data['TIME']>=2022]['TIME'],reg_rec_data.loc[reg_rec_data['TIME']>=2022]['DIS%']*100,'--',label = 'Target Scenario Landfill%', color = '#6b1b62', alpha=0.7)

#Recycling %

#plotting time series of recycling %
plt.plot(reg_bau_data.loc[reg_bau_data['TIME']<=2021]['TIME'],reg_bau_data.loc[reg_bau_data['TIME']<=2021]['RCY%']*100,'^', label = 'Historic Recycling%', color='#166082', alpha=0.9, markersize=7)

x = np.arange(2010,2051)
plt.plot(x, reg_bau_data['RCY%'].loc[reg_bau_data['TIME'].isin(x)]*100,'-',label = 'BAU Scenario Recycling%', color = '#166082', alpha=0.9, linewidth=2.5)

plt.plot(reg_rec_data.loc[reg_rec_data['TIME']>=2022]['TIME'],reg_rec_data.loc[reg_rec_data['TIME']>=2022]['RCY%']*100,'--',label = 'Target Scenario Recycling%', color = '#166082', alpha=0.7)

#plotting time series of incineration %
plt.plot(reg_bau_data.loc[reg_bau_data['TIME']<=2021]['TIME'],reg_bau_data.loc[reg_bau_data['TIME']<=2021]['INC%']*100, 's', label = 'Historic Incineration%', color = '#af4910', alpha=0.9,  markersize=6)
x = np.arange(2010,2051)
plt.plot(x, reg_bau_data['INC%'].loc[reg_bau_data['TIME'].isin(x)]*100,'-',label = 'BAU Scenario Incineration%', color = '#af4910', alpha=0.7, linewidth=2.5)
   
plt.plot(reg_rec_data.loc[reg_rec_data['TIME']>=2022]['TIME'],reg_rec_data.loc[reg_rec_data['TIME']>=2022]['INC%']*100,'--',label = 'Target Scenario Incineration%', color = '#af4910', alpha=0.7)



plt.xlabel('Years', fontproperties = font_FTR)
plt.ylabel('Treatment %', fontproperties = font_FTR)
plt.xticks(fontproperties = font_FTR)
plt.yticks(fontproperties = font_FTR)
plt.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=2, prop=font_label)
#plt.legend(loc="best", ncol=2, prop=font_label)
#plt.title('Trend Analysis of Treatment Methods BAU Scenario')
plt.title('Target Scenario of Treatment Methods, '+region, fontproperties=font_title)


#plt.savefig('plots/poster/Fig1_'+region+'_TRT.png',dpi=300, bbox_inches='tight')
plt.show()
plt.close()

#%%
#plotting time series of MSW GEN
fig_2 = plt.plot(reg_bau_data.loc[reg_bau_data['TIME']<=2021]['TIME'],reg_bau_data.loc[reg_bau_data['TIME']<=2021]['MSW_GEN_T'],'o', label='Historic MSW Generation', color = '#719a5f', alpha=0.9, markersize=6)

x = np.arange(2010,2051)
plt.plot(x, reg_bau_data['MSW_GEN_T'].loc[reg_bau_data['TIME'].isin(x)],'-',label = 'BAU Scenario MSW Genaration', color = '#719a5f', alpha=0.9)

#plt.plot(reg_cir_data.loc[reg_cir_data['TIME']>=2022]['TIME'],reg_cir_data.loc[reg_cir_data['TIME']>=2022]['MSW_GEN_T'],'--',label = 'MSW GEN Trend CIR', color = '#575D90')

plt.ylim(bottom=0)
plt.xlabel('Years', fontproperties=font_FTR)
plt.ylabel('MSW Generated (tonnes/year)', fontproperties=font_FTR)
plt.xticks(fontproperties=font_FTR)
plt.yticks(fontproperties=font_FTR)
plt.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=2, prop=font_label)
plt.title('Business-As-Usual Scenario of MSW Generation', fontproperties=font_title)

plt.savefig('plots/poster/Fig2_'+region+'_GEN.png',dpi=300, bbox_inches='tight')
plt.show()
plt.close()
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
ash_data = pd.read_csv('data/results/Data_Structure_Task4.1_Task4.2_all_scenarios.csv')
reg_bau_data = ash_data.loc[(ash_data['Country']==region)&((ash_data['Scenario']=='BAU')|(ash_data['Scenario']=='OBS'))]
reg_rec_data = ash_data.loc[(ash_data['Country']==region)&(ash_data['Scenario']=='REC')] 
reg_cir_data = ash_data.loc[(ash_data['Country']==region)&(ash_data['Scenario']=='CIR')]

x = np.arange(2010,2051)
fig = plt.plot(np.arange(2010,2022), reg_bau_data['Value'].loc[(reg_bau_data['Year'].isin(np.arange(2010,2022)))&(reg_bau_data['Substance main parent']=='19 01 11*')],'o',label = 'MSWI Bottom ash, Historic', color = '#166082', alpha=0.9, markersize=6)
plt.plot(x, reg_bau_data['Value'].loc[(reg_bau_data['Year'].isin(x))&(reg_bau_data['Substance main parent']=='19 01 11*')],'-',label = 'MSWI Bottom ash, BAU', color = '#166082', alpha=0.9)
plt.plot(reg_rec_data.loc[reg_rec_data['Year']>=2022]['Year'].unique(),reg_rec_data.loc[(reg_rec_data['Year']>=2022)&(reg_rec_data['Substance main parent']=='19 01 11*')]['Value'],'--',label = 'MSWI Bottom ash, Target', color = '#af4910', alpha=0.9)
#plt.plot(reg_cir_data.loc[reg_cir_data['Year']>=2022]['Year'].unique(),reg_cir_data.loc[(reg_cir_data['Year']>=2022)&(reg_cir_data['Substance main parent']=='19 01 11*')]['Value'],'--',label = 'Bottom ash CIR', color = '#210124')


#plt.plot(x, reg_bau_data['Value'].loc[(reg_bau_data['Year'].isin(x))&(reg_bau_data['Substance main parent']=='19 01 13*')],'-',label = 'Fly ash BAU', color = '#750D37')
#plt.plot(reg_rec_data.loc[reg_rec_data['Year']>=2022]['Year'].unique(),reg_rec_data.loc[(reg_rec_data['Year']>=2022)&(reg_rec_data['Substance main parent']=='19 01 13*')]['Value'],'--',label = 'Fly ash REC', color = '#750D37')
#plt.plot(reg_cir_data.loc[reg_cir_data['Year']>=2022]['Year'].unique(),reg_cir_data.loc[(reg_cir_data['Year']>=2022)&(reg_cir_data['Substance main parent']=='19 01 13*')]['Value'],'--',label = 'Fly ash CIR', color = '#750D37')

plt.ylim(bottom=0)
plt.xlabel('Years', fontproperties=font_FTR)
plt.ylabel('MSWI Bottom Ash (tonnes/year)', fontproperties=font_FTR)
plt.xticks(fontproperties=font_FTR)
plt.yticks(fontproperties=font_FTR)
plt.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2, prop=font_label)
plt.title('Target Scenario for MSW Incineration Ash', fontproperties=font_title)

plt.savefig('plots/poster/Fig4_'+region+'_BA.png',dpi=300, bbox_inches='tight')
plt.show()

#%%

import geopandas as gpd
import matplotlib.pyplot as plt

# Load a built-in map of countries
world = gpd.read_file('/Users/marriyapillais/Desktop/msw_model/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp')
world.loc[world['ADMIN']=='France', 'ISO_A3'] = 'FRA'
world.loc[world['ADMIN']=='Northern Cyprus', 'ISO_A3'] = 'CYP'
world.loc[world['ADMIN']=='Norway', 'ISO_A3'] = 'NOR'

# Define groups by ISO3 codes
blue = ['AUT','BEL','CZE','DNK','FIN','FRA','HUN','IRL','LUX',
        'NLD','POL','PRT','ESP','SWE','CHE','GBR','BGR','HRV',
        'EST','LVA','LTU']
grey = ['DEU','ITA','SVN']
orange = ['GRC','ISL','SVK','ROU','CYP']

# Add color column
world['color'] = 'lightgrey'  # background default
world.loc[world.ISO_A3.isin(blue),  'color'] = '#166082'
world.loc[world.ISO_A3.isin(grey),  'color'] = '#6b1b62' 
world.loc[world.ISO_A3.isin(orange),'color'] = '#af4910'

# Plot map
# fig, ax = plt.subplots(1, 1, figsize=(10, 8))
# world.plot(ax=ax, color=world['color'], edgecolor='black', linewidth=0.5)

# # Focus on Europe
# ax.set_xlim(-25, 35)
# ax.set_ylim(34, 72)
# ax.axis('off')
# ax.set_title('EU27+4: Country Color Map', fontsize=16)

# plt.show()

world['geometry'] = world['geometry'].simplify(tolerance=0.05, preserve_topology=True)

# Plot setup
fig, ax = plt.subplots(figsize=(10, 8), facecolor='white')

# Draw landmasses
world.plot(ax=ax, color=world['color'], edgecolor='white', linewidth=0.4)

# Focus on Europe=[]
ax.set_xlim(-25, 35)
ax.set_ylim(34, 72)
ax.axis('off')

# Custom legend
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='#166082', edgecolor='white', label='Decrease Incineration% to meet Target'),
    Patch(facecolor='#6b1b62', edgecolor='white', label='BAU Meets Target'),
    Patch(facecolor='#af4910', edgecolor='white', label='Increase Incineration% to meet Target'),
]
ax.legend(handles=legend_elements, loc="upper center", bbox_to_anchor=(0.5, -0.01), frameon=False, prop=font_label)

plt.title('BAU Difference from Targets',   fontproperties = font_title)
plt.tight_layout()
plt.savefig('eu27_plus4_smooth.png', dpi=300, bbox_inches='tight')
plt.show()

#%%

#Add path for these
sf_cmp = pd.read_csv("SLASH_SF_cmp_version20.csv")
rm = pd.read_csv("SLASH_RM_cmp_version11.csv")


sf_cmp_msw = rm[(rm['Layer 1'].isin(['19 01 11*', '19 01 13*']))&(rm['Layer 4'].notna())]


msw_rm  = sf_cmp_msw[sf_cmp_msw['Stock/Flow ID']=='SLASH_2RM_bottomAshesWasteInc']
msw_rm = msw_rm[(msw_rm['Year'].isin([2021,2050]))&(msw_rm['Scenario'].isin(['OBS','BAU','REC']))]

sf_cmp_msw = sf_cmp_msw[(sf_cmp_msw['Year'].isin([2021,2050]))&(sf_cmp_msw['Scenario'].isin(['OBS','BAU','REC']))&(sf_cmp_msw['Stock/Flow ID']!='SLASH_2RM_bottomAshesWasteInc')]

sf_cmp_msw=sf_cmp_msw.groupby(
    by =['Waste Stream', 'Location', 'Year', 'Scenario',
             'Layer 4',  'Unit'], as_index=False
    )['Value'].sum()

sf_cmp_msw.loc[sf_cmp_msw['Scenario']=='REC', 'Scenario']='Target'
msw_rm.loc[msw_rm['Scenario']=='REC', 'Scenario']='Target'


criticality = pd.read_csv('/Users/marriyapillais/Desktop/SLASH/plug-in code and data/visuals/Criticality_criteria.csv')
criticality=criticality[(criticality['Layer 1'].isna())&
                        (criticality['Layer 2'].isna())&
                        (criticality['Layer 3'].isna())&
                        (criticality['Layer 4'].notna())]
# Set up the plot
plt.figure(figsize=(12, 6))

custom_colors = {
    'OBS': '#6b1b62',
    'BAU': '#166082',
    'Target': '#af4910'
}

scenario_order = ['OBS', 'BAU', 'Target']  # Adjust to match your Scenario column exactly

# Filter the data first
filtered_df = sf_cmp_msw[
    (sf_cmp_msw['Value'] >= 10) &
    ((sf_cmp_msw['Layer 4'].isin(criticality['Layer 4']))|
     (sf_cmp_msw['Layer 4']=='Fe'))
]

#filtered_df = msw_rm

# Step 1: Compute Layer 4 order by total value (or a specific scenario if you prefer)
layer_order = (
    filtered_df.groupby('Layer 4')['Value']
    .sum()
    .sort_values(ascending=False)
    .index
)
# Plot with seaborn: x = Layer 4, hue = Scenario_Year

sns.barplot(
    data=filtered_df,
    x='Layer 4',
    y='Value',
    hue='Scenario',
    palette=custom_colors,    # Your custom palette
    order=layer_order,        # x-axis order
    hue_order=scenario_order, # consistent scenario bar order
    alpha=0.9
)
sns.set(style="whitegrid")
# Improve layout
plt.xlabel('Element', fontproperties=font_FTR)
plt.ylabel('Value (tonnes/year)', fontproperties=font_FTR)
plt.yscale('log')
plt.title('Volume of Elements in MSWI Ash', fontproperties=font_title)
#plt.title('Recoverability of Elements in MSWI Ash', fontproperties=font_title)
plt.xticks(fontproperties=font_FTR)
plt.yticks(fontproperties=font_FTR)
plt.tight_layout()
plt.legend(title='Scenario', prop=font_label)

# Show plot


plt.savefig('plots/poster/Fig5_'+region+'_cmp.png',dpi=300, bbox_inches='tight')

plt.show()






