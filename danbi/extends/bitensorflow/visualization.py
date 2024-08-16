import pandas as pd
from danbi.extends import bibokeh as bibo

def showLearningHistory(history, width: int = 1500, height: int = 400, legend: str = "bottm_left"):
    ylist = []
    keys = history.history.keys()
    for key in keys:
        if not key.startswith("val_"):
            validation = "val_"+key
            if validation in keys:
                ylist.append([key, "val_"+key])
            else:
                ylist.append([key])
            
    bibo.showPandas(
        pd.DataFrame(history.history), "index", ylist, "line", 1500, 400, True, "x", [2, 1],
        {"legend_location": legend}
    )