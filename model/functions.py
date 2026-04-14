import pandas as pd
import numpy as np

def log_fit_fun(x,fit_params):
    #for the specified parameters, this function returns the y values for each value x
    return(fit_params[2]+fit_params[1]*np.log(x)+fit_params[0]*np.log(x)*np.log(x))

def logistic_fun(x, L, k, x0):
    return L / (1 + np.exp(-k * (x - x0)))

#%%Function to estimate the future msw gen from the obtained fit function
def msw_gen_model(reg_msw_data,reg_gdp_data,  proj_year, fit = [18.52534507, -176.90063059, 318.11762839], base_year=2019, column_names=['TIME','GDPCAP_USD','MSW/CAP']):
    '''
    Given fit parameters, and base year for model, this function estimates proxy and projected values of 
    MSW generation for the specified projection year(s)
    reg_msw_dat: dataframe with MSW per capita data for the region of interest
    reg_gdp_data: dataframe with GDP per capita  data for the region of interest
    proj_year: year(s) for which projections are to be made. Can be a single year (int) or a list of years (list of ints)
    fit: parameters of the fit function
    base_year: base year for calibrating the model
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

#%% Constrained logistic model for estimating disposal, reyccling and incineration rates

def model_D_R(params, years):
    '''
    Given parameters and years, this function estimates the disposal or recycling rates for the specified years
    params: list containing the 3 parameters of the logistic function for either disposal or recycling
    years: years for which the estimates are to be made
    '''
    return logistic_fun(years, params[0], params[1], params[2]) 

def estimate_incineration(params, years):
    D = model_D_R(params[:3], years)
    R = model_D_R(params[3:], years)
    I = 1 - D - R
    return I

def objective(params, years, inc_obs, dis_obs, rcy_obs):
    d = model_D_R(params[:3], years)
    r = model_D_R(params[3:], years)
    i = estimate_incineration(params, years)
    d_d = np.sum((d - dis_obs)**2)
    d_r = np.sum((r - rcy_obs)**2)
    d_i = np.sum((i - inc_obs)**2)
    return d_d + d_r + d_i

def con_1(params, years):
    #constraint: D<1
    return (1-model_D_R(params[:3], years))
def con_2(params, years):
    #constraint: R<1
    return (1-model_D_R(params[3:], years))
def con_3(params, years):
    #constraint: I<1
    return (1-estimate_incineration(params, years))
def con_4(params, years):
    #constraint: D+R<1
    return (1-model_D_R(params[:3], years)-model_D_R(params[3:], years))