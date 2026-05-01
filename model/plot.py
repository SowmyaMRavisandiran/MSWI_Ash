#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 15 16:59:45 2024

@author: marriyapillais
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def get_region_data(data, region, column_name):
    return data.loc[data[column_name] == region]

def plot_trends_ax(ax, bau_data, scenarios, columns, historic_labels, bau_labels, colors, title, ylabel):
    for col_idx, (col, h_label, b_label, color) in enumerate(zip(columns, historic_labels, bau_labels, colors)):
        ax.plot(bau_data.loc[bau_data['TIME'] <= 2021]['TIME'],
                bau_data.loc[bau_data['TIME'] <= 2021][col],
                'o', label=h_label, color=color)

        x = np.arange(2010, 2051)
        ax.plot(x, bau_data[col].loc[bau_data['TIME'].isin(x)],
                '-', label=b_label, color=color)

        for scenario_data, scenario_labels, style in scenarios:
            ax.plot(scenario_data.loc[scenario_data['TIME'] >= 2022]['TIME'],
                    scenario_data.loc[scenario_data['TIME'] >= 2022][col],
                    style, label=scenario_labels[col_idx], color=color)

    ax.set_xlabel('Years')
    ax.set_ylabel(ylabel)
    ax.set_title(title)


def plot_countries_subplots(countries, bau_df, rec_df, cir_df, columns, historic_labels, bau_labels, colors, title_template, ylabel):
    n = len(countries)
    ncols = 2
    nrows = int(np.ceil(n / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(12, 4 * nrows), sharex=True, sharey=True)
    axes = axes.flatten()

    scenarios = [
        (rec_df, [f'{lab} REC' for lab in bau_labels], '--'),
        (cir_df, [f'{lab} CIR' for lab in bau_labels], '--')
    ]

    for ax, country in zip(axes, countries):
        bau_country = bau_df[bau_df['LOCATION'] == country]
        rec_country = rec_df[rec_df['LOCATION'] == country]
        cir_country = cir_df[cir_df['LOCATION'] == country]

        plot_trends_ax(ax, bau_country, scenarios, columns, historic_labels, bau_labels, colors,
                       title_template.format(country=country), ylabel)

        ax.legend(fontsize=7, loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2)

    for ax in axes[n:]:
        ax.axis('off')

    fig.tight_layout()
    plt.show()