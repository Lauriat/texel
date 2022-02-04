from itertools import combinations, count
from functools import lru_cache
import pyperclip
import pandas as pd
import numpy as np

from typing import Any, Dict, List, Generator


def read_spreadsheet(
    filename: str, delimiter: str, fillna: Any
) -> Dict[str, pd.DataFrame]:
    if filename.split(".")[-1] == "csv":
        sheetdict = {filename: pd.read_csv(filename, delimiter=delimiter, header=None)}
    else:
        sheetdict = pd.read_excel(filename, sheet_name=None, header=None)
    if fillna is not None:
        for key in sheetdict:
            sheetdict[key].fillna(fillna, inplace=True)
    return sheetdict


@lru_cache()
def get_alphas(n: int) -> List[str]:
    alphaiter = get_alpha_iter()
    return [next(alphaiter) for _ in range(n)]


def copy(obj: Any):
    if isinstance(obj, np.ndarray):
        string = array_to_string(obj)
    else:
        string = str(obj)
    pyperclip.copy(string)


def get_alpha_iter() -> Generator[str, None, None]:
    alpha = range(65, 91)
    for i in count(1):
        chars = combinations(alpha, i)
        for ch in chars:
            yield "".join(map(chr, ch))


def array_to_string(mat: np.ndarray) -> str:
    return "\n".join(",".join(map(str, e)) for e in mat)
