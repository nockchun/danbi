import pickle

def storePickle(data, file_path: str):
    with open(file_path, "wb") as f:
        pickle.dump(data, f)

def restorePickle(file_path: str):
    with open(file_path, "rb") as f:
        data = pickle.load(f)
    return data

