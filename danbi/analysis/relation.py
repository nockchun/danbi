import numpy as np

def anaCorrelation(df, positive=0.8, negative=0.8, method="spearman", once=True, no_rate=False, group_result=False):
    if group_result:
        no_rate = True
        
    corr_pos = {}
    corr_neg = {}
    
    df_corr = df.corr(method=method)
    df_corr.reset_index(drop=True, inplace=True)
    columns = df_corr.columns
    
    df_pos = df_corr.where(df_corr >= positive)
    df_neg = df_corr.where(df_corr <= -negative)
    for item, result in [(df_pos, corr_pos), (df_neg, corr_neg)]:
        for idx, row in item.iterrows():
            if once:
                have_corrs = row[idx+1:].dropna()
            else:
                row.pop(columns[idx])
                have_corrs = row.dropna()
            if len(have_corrs) > 0:
                have_corr = np.array(list(have_corrs.items()))
                if no_rate:
                    result[columns[idx]] = have_corr[:,0].tolist()
                else:
                    result[columns[idx]] = have_corr
    
    if group_result:
        group_pos = []
        group_neg = []
        for item, result in [(corr_pos, group_pos), (corr_neg, group_neg)]:
            for key, value in item.items():
                value.append(key)
                set_data = set(value)
                is_update = False
                for corr_set in result:
                    if len(corr_set & set_data) > 0:
                        corr_set.update(set_data)
                        is_update = True
                        break
                if not is_update:
                    result.append(set_data)
        return group_pos, group_neg
    
    return corr_pos, corr_neg

def anaCorrelationFuture(df, positive=0.8, negative=0.8, targets=[], method="pearson", future=0, once=True):
    corr_pos = {}
    corr_neg = {}
    cols = df.columns.tolist()
    for idx, col in enumerate(cols):
        print(f"Analysis {idx+1}/{len(cols)}{' '*50}", end="\r")
        if (len(targets) > 0) and (col not in targets):
            continue
        col_others = cols[:idx] + cols[idx+1:]
        df[col_others] = df[col_others].shift(-future)
        df_corr = df.corr(method=method)
        if once:
            series = df_corr[col].iloc[idx+1:]
        else:
            series = df_corr[df_corr[col] < 1.0][col]
        
        series_pos = series[series > positive]
        if len(series_pos.index) > 0:
            corr_pos[col] = series_pos.index.tolist()
        series_neg = series[series  < -negative]
        if len(series_neg.index) > 0:
            corr_neg[col] = series_neg.index.tolist()
        
        df[col_others] = df[col_others].shift(future)
    
    return corr_pos, corr_neg