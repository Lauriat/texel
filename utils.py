import pandas as pd
from itertools import combinations, count


def read_spreadsheet(filename, delimiter, fillna):
    if filename.split(".")[-1] == "csv":
        sheetdict = {filename: pd.read_csv(filename, delimiter=delimiter, header=None)}
    else:
        sheetdict = pd.read_excel(filename, sheet_name=None, header=None)
    if fillna is not None:
        for key in sheetdict:
            sheetdict[key].fillna(fillna, inplace=True)
    return sheetdict


def get_alphas(n):
    alphaiter = get_alpha_iter()
    return [next(alphaiter) for _ in range(n)]


def get_alpha_iter():
    alpha = range(65, 91)
    for i in count(1):
        chars = combinations(alpha, i)
        for ch in chars:
            yield "".join(map(chr, ch))
