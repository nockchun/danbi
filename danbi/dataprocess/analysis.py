import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

model_linear = LinearRegression()
def anaRegressionTrend(data, outlier_rate=0.1, span=0):
    global model_linear

    # 선형회귀 계산
    size_data = len(data)
    time = np.arange(size_data).reshape(-1, 1)
    model_linear.fit(time, data)
    slope = model_linear.coef_[0] # 기울기
    intercept = model_linear.intercept_ # 절편
    trend = model_linear.predict(np.arange(size_data+span).reshape(-1, 1))

    # 상한 & 하한 선 계산
    series_diff = pd.Series(data - trend[:size_data])
    lower = series_diff[series_diff <= series_diff.quantile(outlier_rate)].abs().mean()
    upper = series_diff[series_diff >= series_diff.quantile(1- outlier_rate)].abs().mean()
    median = upper if upper < lower else lower

    upper_intercept = intercept + median
    lower_intercept = intercept - median
    
    # 상위 10%, 하위 10% 라인 계산
    trend_upper = (slope * np.arange(size_data+span).reshape(-1, 1) + upper_intercept).flatten()
    trend_lower = (slope * np.arange(size_data+span).reshape(-1, 1) + lower_intercept).flatten()

    return slope, intercept, trend, trend_upper, trend_lower