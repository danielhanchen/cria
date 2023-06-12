"""
    Copyright Daniel Han-Chen
    Inspired from https://docs.python.org/3/library/concurrent.futures.html
"""

__all__ = [
    "multithreading",
    "multiprocessing",
]

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from concurrent.futures import as_completed as As_Completed
from tqdm import tqdm as ProgressBar
from typing import Callable, Sequence
from psutil import cpu_count as CPU_COUNT
from random import shuffle as RANDOM_SHUFFLE
N_CPUS = CPU_COUNT(logical = False)
del CPU_COUNT

def multithreading(download : Callable,
                   process  : Callable,
                   data     : Sequence) -> Sequence:
    """
        Used mainly for IO bound tasks, like downloading files.
    """
    n = len(data)
    all_datas = [None]*n
    with ProgressBar(total = n) as progress_bar, ThreadPoolExecutor(N_CPUS*5) as executor:
        futures = { executor.submit(download, *x) : k for k, x in enumerate(data) }
        iterator = As_Completed(futures)
        for future in iterator:
            try:
                all_datas[futures[future]] = process(*future.result())
                progress_bar.update(1)
            except Exception as error:
                executor.shutdown(wait = False, cancel_futures = True)
                raise RuntimeError(repr(error))
        pass
    pass
    return all_datas
pass

def Caller(function):
    def _call(index, data): return index, function(data)
    return _call
pass

def multiprocessing(process  : Callable,
                    data     : Sequence) -> Sequence:
    """
        Used mainly for compute bound tasks.
    """
    n = len(data)
    all_datas = [None]*n
    process = Caller(process)
    data = list(enumerate(data))
    RANDOM_SHUFFLE(data) # Must shuffle to counteract imbalanced datasets

    with ProgressBar(total = n) as progress_bar, ProcessPoolExecutor(N_CPUS) as executor:
        iterator = executor.map(process, data, chunksize = max(n // N_CPUS, 1))
        for (index, result) in iterator:
            all_datas[index] = result
            progress_bar.update(1)
        pass
    pass
    return all_datas
pass
