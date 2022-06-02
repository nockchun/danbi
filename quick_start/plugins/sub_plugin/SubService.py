import danbi as di

class SubService(di.IPlugin):
    def getInjectionKeys(self):
        return ["postgresql:connection"]

    def plug(self, app) -> None:
        print(f"'{self}' plugin pluged. {app}")
    
    def unplug(self) -> None:
        print(f"'{self}' plugin unpluged.")