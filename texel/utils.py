from functools import lru_cache
from itertools import combinations, count
from typing import Any, Dict, List, Generator

from .reader import SpreadsheetReader, InvalidFileException

import numpy as np
import pyperclip

HELP = (
    "ARROWS / hjkl - Move",
    "<TAB> <SHIFT-TAB> / n <SHIFT n> - Switch sheet",
    "v - Visual/selection mode",
    "<ESC> - Exit visual/selection mode",
    "c / y - Copy selected cell(s)",
    "q - Exit",
    "? - Show this message",
)


def read_spreadsheet(
    filename: str, delimiter: str, fillna: Any, encoding: str
) -> Dict[str, np.ndarray]:
    return SpreadsheetReader(filename, delimiter, fillna, encoding).read()


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
