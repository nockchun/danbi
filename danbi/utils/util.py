import pickle
import bz2

def storePickle(data, file_path: str):
    with bz2.open(file_path, "wb") as f:
        pickle.dump(data, f)

def restorePickle(file_path: str, default: any = {}):
    try:
        with bz2.open(file_path, "rb") as f:
            data = pickle.load(f)
    except:
        data = default
    return data

