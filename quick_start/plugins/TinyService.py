import danbi as di

class TinyService(di.IPlugin):
    def getInjectionKeys(self):
        return ["flask:app"]

    def plug(self, app) -> None:
        print(f"'{self}' plugin pluged. {app}")
    
    def unplug(self) -> None:
        print(f"'{self}' plugin unpluged..")