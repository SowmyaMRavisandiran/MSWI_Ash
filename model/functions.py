import pandas as pd
import numpy as np

def log_fit_fun(x,fit_params):
    #for the specified parameters, this function returns the y values for each value x
    return(fit_params[2]+fit_params[1]*np.log(x)+fit_params[0]*np.log(x)*np.log(x))

