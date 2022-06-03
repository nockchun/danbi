import danbi as di

class SubService(di.IPlugin):
    def plug(self) -> None:
        print(f"'{self}' plugin pluged.")
    
    def unplug(self) -> None:
        print(f"'{self}' plugin unpluged.")