"""
    Copyright Daniel Han-Chen
    Inspired from https://docs.python.org/3/library/concurrent.futures.html

    Pathos interestingly works inside interative modes, and does NOT
    need if __name__ == "__main__" to work!
"""

__all__ = [
    "multithreading",
    "multiprocessing",
]

from typing import Callable, Sequence
from tqdm import tqdm as ProgressBar
from psutil import cpu_count as CPU_COUNT
N_CPUS = CPU_COUNT(logical = True)
del CPU_COUNT
from inspect import signature

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed as As_Completed

def multithreading(download : Callable,
                   process  : Callable,
                   data     : Sequence) -> Sequence:
    """
        Used mainly for IO bound tasks, like downloading files.
    """
    DOWNLOAD_SINGULAR = len(signature(download).parameters) == 1
    PROCESS_SINGULAR  = len(signature(process ).parameters) == 1
    n = len(data)
    if n == 0: return []
    if n == 1:
        x = download(data[0]) if DOWNLOAD_SINGULAR else download(*data[0])
        return [ process(x) if PROCESS_SINGULAR else process(*x) ]
    pass

    all_datas = [None]*n
    with ProgressBar(total = n) as progress, ThreadPoolExecutor(N_CPUS*5) as executor:

        if DOWNLOAD_SINGULAR:
            futures = { executor.submit(download,  x) : k for k, x in enumerate(data) }
        else:
            futures = { executor.submit(download, *x) : k for k, x in enumerate(data) }
        pass

        for future in As_Completed(futures):
            try:
                result = future.result()
                result = process(result) if PROCESS_SINGULAR else process(*result)
                all_datas[futures[future]] = result
                progress.update(1)
            except Exception as error:
                executor.shutdown(wait = False, cancel_futures = True)
                raise RuntimeError(repr(error))
        pass
    pass
    return all_datas
pass


from pathos.pools import ProcessPool

def multiprocessing(process  : Callable,
                    data     : Sequence) -> Sequence:
    """
        Used mainly for compute bound tasks.
    """
    PROCESS_SINGULAR = len(signature(process).parameters) == 1
    n = len(data)
    if n == 0: return []
    if n == 1:
        x = data[0]
        return [ process(x) if PROCESS_SINGULAR else process(*x) ]
    pass

    first_item = data[0]
    # CHUNKSIZE = max(len(data) // N_CPUS, 1)

    pool = ProcessPool(nodes = N_CPUS)
    if PROCESS_SINGULAR:
        all_datas = pool.imap(process, data, chunksize = 1)
    else:
        n_parameters = len(first_item)
        data = [[x[p] for x in data] for p in range(n_parameters)]
        all_datas = pool.imap(process, *data, chunksize = 1)
    pass
    all_datas = list(ProgressBar(all_datas, total = n))
    return all_datas
pass
