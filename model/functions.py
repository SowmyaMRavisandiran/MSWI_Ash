import pandas as pd
import numpy as np

def log_fit_fun(x,fit_params):
    #for the specified parameters, this function returns the y values for each value x
    return(fit_params[2]+fit_params[1]*np.log(x)+fit_params[0]*np.log(x)*np.log(x))


#Function to estimate the future msw gen from the obtained fit function
def msw_gen_model(reg_msw_data,reg_gdp_data, fit, base_year, proj_year, column_names=['TIME','GDPCAP_USD','MSW/CAP']):
    '''
    Given fit parameters, and base year for model, this function estimates proxy and projected values of 
    MSW generation for the specified projection year(s)
    reg_msw_dat: dataframe with MSW per capita data for the region of interest
    reg_gdp_data: dataframe with GDP per capita  data for the region of interest
    fit: parameters of the fit function
    base_year: base year for calibrating the model
    proj_year: year(s) for which projections are to be made. Can be a single year (int) or a list of years (list of ints)
    column_names: names of the columns in the dataframes for time, gdp per capita and msw per capita respectively.
    '''
    time, gdp_cap, msw_cap = column_names
    proxy_base = log_fit_fun(reg_gdp_data.loc[reg_gdp_data[time]==base_year][gdp_cap], fit).to_numpy()
    actual_base = reg_msw_data.loc[reg_msw_data[time]==base_year][msw_cap].to_numpy()
    if type(proj_year) == int:
        proxies = log_fit_fun(reg_gdp_data.loc[reg_gdp_data[time]==proj_year][gdp_cap], fit)
    else:
        proxies = log_fit_fun(reg_gdp_data.loc[reg_gdp_data[time].isin(proj_year)][gdp_cap], fit)
    projections = proxies /proxy_base * actual_base
    return(projections)

