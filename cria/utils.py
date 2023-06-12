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

def multithreading(download : Callable,
                   process  : Callable,
                   data     : Sequence) -> Sequence:
    """
        Used mainly for IO bound tasks, like downloading files.
    """
    n = len(data)
    all_datas = [None]*n
    with ProgressBar(total = n) as progress_bar, ThreadPoolExecutor() as executor:
        futures = { executor.submit(download, *x) : k for k, x in enumerate(data) }
        for future in As_Completed(futures):
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

def multiprocessing(process  : Callable,
                    data     : Sequence) -> Sequence:
    """
        Used mainly for compute bound tasks.
    """
    n = len(data)
    all_datas = [None]*n
    with ProgressBar(total = n) as progress_bar, ProcessPoolExecutor() as executor:
        futures = { executor.submit(process, *x) : k for k, x in enumerate(data) }
        for future in As_Completed(futures):
            try:
                all_datas[futures[future]] = future.result()
                progress_bar.update(1)
            except Exception as error:
                executor.shutdown(wait = False, cancel_futures = True)
                raise RuntimeError(repr(error))
        pass
    pass
    return all_datas
pass
