import danbi as di

class TinyService(di.IPlugin):
    def plug(self) -> None:
        print(f"'{self}' plugin pluged.")
    
    def unplug(self) -> None:
        print(f"'{self}' plugin unpluged..")