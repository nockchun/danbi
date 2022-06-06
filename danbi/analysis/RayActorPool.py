try:
    import pandas as pd
    import ray

    class RayActorPool:
        def __init__(self, ActorClass: ray.actor.ActorClass, amount: int):
            actors = [ActorClass.remote() for _ in range(amount)]
            self._actor_pool = ray.util.ActorPool(actors)
        
        def get(self, method_name: str, batch_vals: list):
            results = self._actor_pool.map(lambda a, v: getattr(a, method_name).remote(*v), batch_vals)
            
            return [x for x in results]
        
        def getPandas(self, method_name: str, batch_vals: list, columns: list):
            results = self.get(method_name, batch_vals)
            
            return pd.DataFrame(results, columns=columns)
except:
    ...