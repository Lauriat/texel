#!/usr/bin/env python

import curses
from argparse import ArgumentParser

from .grid import Grid
from .styles import Styles
from .utils import read_spreadsheet, InvalidFileException


def run(scr, sheets, args):
    grid = Grid(
        scr,
        sheets,
        Styles(args.cellwidth, args.precision),
    )
    while grid.handle_press(scr.getch()):
        pass


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "file",
        help="Spreadsheet path (csv, xls, xlsx, xlsm, xlsb, odf, ods or odt)",
        metavar="FILE",
    )
    parser.add_argument(
        "-d",
        "--delimiter",
        help="Delimiter for csv files",
        metavar="DELIMITER",
        default=",",
    )
    parser.add_argument(
        "-c",
        "--cellwidth",
        help="Width of a cell",
        metavar="CELLWIDTH",
        type=int,
        default=10,
    )
    parser.add_argument(
        "-p",
        "--precision",
        help="Precision of floating point numbers",
        metavar="PRECISION",
        type=int,
        default=2,
    )
    parser.add_argument(
        "--fillna",
        help="Value to use to fill holes in the spreadsheet",
        metavar="FILLNA",
        default=None,
    )
    parser.add_argument(
        "--encoding",
        help="Encoding for CSV files",
        metavar="ENCODING",
        default="utf-8",
    )
    try:
        args = parser.parse_args()
        sheets = read_spreadsheet(args.file, args.delimiter, args.fillna, args.encoding)
    except InvalidFileException as e:
        print(e)
        exit()
    except TypeError as e:
        print(e)
        parser.print_usage()
        exit()
    except FileNotFoundError:
        print("Cannot find or open {}".format(args.file))
        exit()
    except ImportError as e:
        print(e)
        exit()
    curses.wrapper(run, sheets, args)
