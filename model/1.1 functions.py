import pandas as pd
from model.scenarios import get_dis_until2050, get_rcy_until2050
import numpy as np

def log_fit_fun(x,fit_params):
    """
    Compute the quadratic-log regression for given values of x.
    E.g. Fitted MSW per-capita for given values of GDP per-capita and regression coefficients.

    Parameters
    ----------
    x : array-like or float
        e.g. GDP per capita values.
    fit_params : list of float
        Regression coefficients [a, b, c] for the form:
        c + b * log(x) + a * (log(x) ** 2)

    Returns
    -------
    ndarray
        Fitted values.
    """

    return(fit_params[2]+fit_params[1]*np.log(x)+fit_params[0]*np.log(x)*np.log(x))

def logistic_fun(x, L, k, x0):
    """
    Evaluate a logistic function for the specified x values (e.g. years) and regression parameters.

    Parameters
    ----------
    x : array-like or float
        e.g Years or independent variable values.
    L : float
        Maximum curve value (upper bound).
    k : float
        Growth rate.
    x0 : float
        Inflection point.

    Returns
    -------
    ndarray
        Logistic curve values.
    """
    return L / (1 + np.exp(-k * (x - x0)))

#%%Function to estimate the future msw gen from the obtained fit function
def msw_gen_model(reg_msw_data,reg_gdp_data,  proj_year, fit = [18.52534507, -176.90063059, 318.11762839], base_year=2019, column_names=['TIME','GDPCAP_USD','MSW/CAP']):
    '''
    Project MSW generation by scaling a GDP-based proxy to observed base-year MSW per capita, based 
    on quadratic-log regression parameters for specified projection years.

    Parameters
    ----------
    reg_msw_data : pandas.DataFrame
        Regional MSW per-capita time-series data, keyed by year.
    reg_gdp_data : pandas.DataFrame
        Regional GDP per-capita times-series data, keyed by year.
    proj_year : int or list of int
        Year or years for projection.
    fit : sequence of float, optional
        Coefficients for the log-fit function. If not given, fit parameters 
        from the previously developed model are used: [18.52534507, -176.90063059, 318.11762839]
    base_year : int, optional
        Calibration year used to anchor the proxy to observed MSW per capita.
        Default is 2019.
    column_names : list of str, optional
        Column names in the dataframes: [time_col, gdp_col, msw_col]. 
        Default is ['TIME','GDPCAP_USD','MSW/CAP'].

    Returns
    -------
    ndarray
        Projected MSW per-capita values for the requested projection year(s).
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

    Estimate disposal or recycling share using a 3-parameter logistic curve.

    Parameters
    ----------
    params : array of float of size 3
        Logistic parameters [L, k, x0].
    years : array-like
        Years to evaluate.

    Returns
    -------
    ndarray
        Estimated disposal or recycling rates.
    '''
    return logistic_fun(years, params[0], params[1], params[2]) 

def estimate_incineration(params, years):
    """
    Estimate incineration share as the residual after disposal and recycling.

    Parameters
    ----------
    params : array of float of size 6
        Combined logistic parameters for disposal and recycling:
        [L_d, k_d, x0_d, L_r, k_r, x0_r].
    years : array-like
        Years to evaluate.

    Returns
    -------
    ndarray
        Estimated incineration rates.
    """
    D = model_D_R(params[:3], years)
    R = model_D_R(params[3:], years)
    I = 1 - D - R
    return I

def objective(params, years, inc_obs, dis_obs, rcy_obs):
    """
    Objective function to be minimized during parameter estimation for the model.
    It computes the sum of squared residuals between observed and estimated rates for disposal, recycling, and incineration.

    Parameters
    ----------
    params : array of float of size 6
        Combined logistic parameters for disposal and recycling:
        [L_d, k_d, x0_d, L_r, k_r, x0_r].
    years : array-like
        Years corresponding to observed rates.
    inc_obs : array-like
        Observed incineration rates.
    dis_obs : array-like
        Observed disposal rates.
    rcy_obs : array-like
        Observed recycling rates.

    Returns
    -------
    float
        Sum of squared residuals for estimations of all three treatment methods.
    """
    d = model_D_R(params[:3], years)
    r = model_D_R(params[3:], years)
    i = estimate_incineration(params, years)
    d_d = np.sum((d - dis_obs)**2)
    d_r = np.sum((r - rcy_obs)**2)
    d_i = np.sum((i - inc_obs)**2)
    return d_d + d_r + d_i

def con_1(params, years):
    """
    Constraint function enforcing disposal rate upper bound D < 1.

    """
    
    return (1-model_D_R(params[:3], years))
def con_2(params, years):
    """
    Constraint function enforcing recycling rate upper bound R < 1.

    """
    #constraint: R<1
    return (1-model_D_R(params[3:], years))
def con_3(params, years):
    """
    Constraint function enforcing incineration upper bound I < 1.
    """
    #constraint: I<1
    return (1-estimate_incineration(params, years))
def con_4(params, years):
   """
    Constraint function enforcing that disposal plus recycling remains below 1.

    Ensures the residual incineration share is less than 1.
    """
    #constraint: D+R<1
    return (1-model_D_R(params[:3], years)-model_D_R(params[3:], years))

#%% REC and CIR scenario estimations

def value_at_2035(bau_data, treatment_method):
    """
    Return the BAU treatment share for a specific method in 2035.

    Parameters
    ----------
    bau_data : pandas.DataFrame
        BAU scenario data containing a TIME column and treatment share columns.
    treatment_method : str
        Column name for the treatment method, e.g. 'RCY%' or 'DIS%'.

    Returns
    -------
    float
        The value of the treatment method in 2035.
    """
    return (bau_data[treatment_method].loc[(bau_data["TIME"]==2035)].values[0])


def diff_from_2021(bau_data, treatment_method, limit):
    """
    Compute the linear change factors from 2021 to 2035 for the selected treatment method.

    For recycling, the target is 65% in 2035. For disposal, the target is 10% in 2035.

    Parameters
    ----------
    bau_data : pandas.DataFrame
        BAU scenario data containing TIME and treatment method values.
    treatment_method : str
        Column name for the treatment method, either 'RCY%' or 'DIS%'.
    limit : float
        Target value for the treatment method in 2035 (e.g. 0.65 for recycling, 0.1 for disposal).
    Returns
    -------
    pandas.DataFrame
        DataFrame with TIME from 2021 to 2035 and the proportional Difference factor.
    """
    
    dif_from_bau = (limit - value_at_2035(bau_data, treatment_method)) / value_at_2035(bau_data, treatment_method)
    differences_from_2021 = pd.DataFrame({'TIME': np.arange(2021, 2036), 'Difference': np.linspace(0, dif_from_bau, 15)})
    return differences_from_2021


def get_treatment_until2050(bau_data, treatment_method, limit):
    """
    Build an adjusted treatment trajectory through 2050 when the 2035 target is not met in BAU.

    Between 2021 and 2035, values are scaled from BAU using the linear phasing factors.
    After 2035, values remain constant at the 2035 adjusted level through 2050.

    Parameters
    ----------
    bau_data : pandas.DataFrame
        BAU scenario data containing TIME and treatment method values.
    treatment_method : str
        Column name for the treatment method, either 'RCY%' or 'DIS%'.
    limit : float
        Target value for the treatment method in 2035 (e.g. 0.65 for recycling, 0.1 for disposal).
    Returns
    -------
    pandas.DataFrame
        DataFrame with TIME from 2021 to 2050 and the adjusted treatment values.
    """
    rec_data = pd.DataFrame(columns=['TIME', treatment_method])
    differences_from_2021 = diff_from_2021(bau_data, treatment_method, limit)
    rec_data['TIME'] = np.arange(2021, 2051)
    rec_data[treatment_method] = bau_data[treatment_method].loc[bau_data['TIME'].isin(np.arange(2021, 2036))].reset_index(drop=True) * (1 + differences_from_2021['Difference'])
    rec_data.loc[rec_data['TIME'].isin(np.arange(2036, 2051)), treatment_method] = rec_data.loc[rec_data['TIME'] == 2035, treatment_method].values[0]
    return rec_data


def check_value_at_2035(bau_data, treatment_method, limit):
    """
    Check whether the BAU value in 2035 already meets the policy target.

    Parameters
    ----------
    bau_data : pandas.DataFrame
        BAU scenario data containing TIME and treatment method values.
    treatment_method : str
        Column name for the treatment method, either 'RCY%' or 'DIS%'.
    limit : float
        Target value for the treatment method in 2035 (e.g. 0.65 for recycling, 0.1 for disposal).
    Returns
    -------
    bool
        True when BAU already meets or exceeds the target for recycling, or falls below the target for disposal.
    """
    if treatment_method == 'RCY%':
        condition = value_at_2035(bau_data, treatment_method) >= limit
    elif treatment_method == 'DIS%':
        condition = value_at_2035(bau_data, treatment_method) <= limit
    return condition


def get_rec_data(bau_data, treatment_method, limit, rec_data=[]):
    """
    Return the scenario data for the requested treatment method over 2021-2050.

    If the BAU path already meets the 2035 target, the BAU series is returned unchanged.
    Otherwise, an adjusted trajectory is generated through 2050.

    Parameters
    ----------
    bau_data : pandas.DataFrame
        BAU scenario data containing TIME and treatment method values.
    treatment_method : str
        Column name for the treatment method, either 'RCY%' or 'DIS%'.
    limit : float
        Target value for the treatment method in 2035 (e.g. 0.65 for recycling, 0.1 for disposal).
    Returns
    -------
    pandas.DataFrame
        DataFrame with TIME from 2021 to 2050 and the selected treatment method values.
    """
    condition = check_value_at_2035(bau_data, treatment_method, limit)
    if treatment_method != 'INC%':
        if condition:
            rec_data = bau_data[['TIME', treatment_method]].loc[bau_data['TIME'].isin(np.arange(2021, 2051))]
        else:
            rec_data = get_treatment_until2050(bau_data, treatment_method, limit)
            rec_data.reset_index(drop=True, inplace=True)
    elif treatment_method == 'INC%':
            if rec_data==[]:
                print("Error: Recycling and disposal data needed to compute the incineration trajectory.")
                break
            else:
            rec_data = pd.DataFrame(columns = ['TIME','INC%'])
            rec_data["TIME"]= np.arange(2021,2051)
            rec_data['INC%'] = 1 - bau_data['RCY%'] - bau_data['DIS%']
    return rec_data
