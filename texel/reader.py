import ast
import csv
import os
from numbers import Number
from typing import Any, Dict, Union


import numpy as np
from openpyxl import load_workbook as load_excel
from odf.opendocument import load as load_odf
from odf.table import Table, TableCell, TableRow

try:
    import pandas as pd
    PANDAS = True
except ModuleNotFoundError:
    PANDAS = False

EXCEL_FORMATS = ("xlsx", "xlsm", "xltx", "xltm")
ODF_FORMATS = ("odf", "odt", "ods")
PANDAS_FORMATS = ("xls", "xlsb")
SUPPORTED_FORMATS = ("csv", *ODF_FORMATS, *EXCEL_FORMATS, *PANDAS_FORMATS)


class InvalidFileException(Exception):
    pass


class SpreadsheetReader:
    def __init__(self, filename: str, delimiter: str, fillna: Any, encoding: str):
        self.filename = filename
        self.delimiter = delimiter
        self.fillna = fillna
        self.encoding = encoding
        self.ft = self.filename.split(".")[-1]

    def read(self) -> Dict[str, np.ndarray]:
        self._validate()
        if self.ft in EXCEL_FORMATS:
            sheetdict = self._read_excel()
        elif self.ft in ODF_FORMATS:
            sheetdict = self._read_odf()
        elif self.ft in PANDAS_FORMATS:
            sheetdict = self._read_pandas()
        else:
            sheetdict = self._read_csv()
        if self.fillna is not None:
            for key in sheetdict:
                sheetdict[key][sheetdict[key] == np.nan] = self.fillna
        return sheetdict

    def _read_pandas(self):
        if not PANDAS:
            raise ImportError(
                f"Optional dependency 'pandas' required for filetype '{self.ft}'\n"
                + "Install with pip install pandas"
            )
        wb = pd.read_excel(self.filename, sheet_name=None, header=None)
        wb = {key: val.to_numpy() for key, val in wb.items()}
        return wb

    def _validate(self):
        self._check_exists()
        self._check_format()

    def _check_format(self):
        if self.ft not in SUPPORTED_FORMATS:
            raise InvalidFileException(
                f"Invalid file format ({self.ft})\n"
                + f"Supported formats are: {', '.join(SUPPORTED_FORMATS)}"
            )

    def _check_exists(self):
        if not os.path.exists(self.filename):
            raise FileNotFoundError()

    def _parse_cell(self, value: Union[str, Number, TableCell]) -> Union[str, Number]:
        if isinstance(value, Number):
            return value
        if value is None:
            return np.nan
        value = str(value).strip()
        if len(value) > 0:
            try:
                return ast.literal_eval(value)
            except (SyntaxError, ValueError):
                return value
        return np.nan

    def _parse_odfcell(self, cell: TableCell):
        if cell.getAttribute("valuetype") != "string":
            cell = cell.getAttribute("value")
        return self._parse_cell(cell)

    def _read_csv(self):
        lines = []
        with open(self.filename, encoding=self.encoding) as csvfile:
            for line in csv.reader(csvfile, delimiter=self.delimiter):
                lines.append(list(map(self._parse_cell, line)))
        return {self.filename: self._to_array(lines)}

    def _read_excel(self):
        sheets = {}
        wb = load_excel(filename=self.filename, data_only=True)
        for sheet in wb.sheetnames:
            lines = [[self._parse_cell(e.value) for e in row] for row in wb[sheet].rows]
            sheets[sheet] = self._to_array(lines)
        return sheets

    def _read_odf(self):
        sheets = {}
        wb = load_odf(self.filename)
        for sheet in wb.getElementsByType(Table):
            rows = [
                list(map(self._parse_odfcell, row.getElementsByType(TableCell)))
                for row in sheet.getElementsByType(TableRow)
            ]
            sheets[sheet.getAttribute("name")] = self._to_array(rows)
        return sheets

    def _to_array(self, lines):
        shape = len(lines), max(map(len, lines))
        arr = np.zeros(shape, dtype=object)
        arr[:] = np.nan
        for i, line in enumerate(lines):
            arr[i, : len(line)] = line
        return arr
