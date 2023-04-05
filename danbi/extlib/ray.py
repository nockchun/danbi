from typing import List, Callable
import psutil
import pandas as pd
import ray

class RayActorPool:
    """Deploy as many actors as the number of mounts to ray cluster and create a pool manager for manage them.
    """
    def __init__(self, ActorClass: ray.actor.ActorClass, amount: int):
        """Deploy as many actors as the number of mounts to ray cluster and create a pool manager for manage them.

        Args:
            ActorClass (ray.actor.ActorClass): ray's actor class.
            amount (int): amount of actors. in general, use only the number of cpu cores. 
        """
        actors = [ActorClass.remote() for _ in range(amount)]
        self._actor_pool = ray.util.ActorPool(actors)
    
    def get(self, method_name: str, batch_vals: list) -> list:
        """Run at ray cluster with registered actor.

        Args:
            method_name (str): actor's method name of string what you want to run.
            batch_vals (list): data list for multi actors.

        Returns:
            list: Results of processing by multiple actors with the input data list.
        """
        results = self._actor_pool.map(lambda a, v: getattr(a, method_name).remote(*v), batch_vals)
        
        return [x for x in results]
    
    def getPandas(self, method_name: str, batch_vals: list, columns: list, dropna: bool = False) -> pd.DataFrame:
        """It's same as get(). but the result is pandas DataFrame.

        Args:
            method_name (str): actor's method name of string what you want to run.
            batch_vals (list): data list for multi actors.
            columns (list): results column names.
            dropna (bool, optional): Except when there is None among the results. Defaults to False.

        Returns:
            pd.DataFrame: Results of processing by multiple actors with the input data list.
        """
        results = self.get(method_name, batch_vals)
        df = pd.DataFrame(results, columns=columns)
        
        return df.dropna() if dropna else df


def rayTaskRun(func_ray: Callable, vals: List, func_callback: Callable = None, chunk: int = None, vervos: bool = True):
    if chunk is None:
        chunk = int(psutil.cpu_count() * 0.9)
    
    ray_refs = []
    cnt_total = len(vals)
    for idx, val in enumerate(vals):
        if vervos:
            print(f"{idx+1}/{cnt_total} ({round((idx+1)/cnt_total*100)}%)", end="\r")
        if isinstance(val, (list, tuple)):
            ray_refs.append(func_ray.remote(*val))
        else:
            ray_refs.append(func_ray.remote(val))
        if idx % chunk == 0:
            while len(ray_refs) > int(chunk * 0.5):
                done_id, ray_refs = ray.wait(ray_refs)
                if func_callback:
                    func_callback(*ray.get(done_id)[0])
    while len(ray_refs):
        done_id, ray_refs = ray.wait(ray_refs)
        if func_callback:
            func_callback(*ray.get(done_id)[0])
