
def AsClassMethod(clazz):
    def makeMethod(func):
        setattr(clazz, func.__name__, func)
    return makeMethod