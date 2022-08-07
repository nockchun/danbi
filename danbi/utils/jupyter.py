import warnings, logging, os

def asClassMethod(clazz):
    def makeMethod(func):
        setattr(clazz, func.__name__, func)
    return makeMethod

def setWarningOff():
    warnings.filterwarnings("ignore")
    logging.getLogger("tensorflow").setLevel(logging.FATAL)
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
