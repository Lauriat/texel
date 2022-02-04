#!/usr/bin/env python

import curses
from argparse import ArgumentParser

from .grid import Grid
from .keys import Keys
from .styles import Styles
from .utils import read_spreadsheet


def run(scr, sheets, args):
    grid = Grid(
        scr,
        sheets,
        Styles(args.cellwidth, args.precision),
    )
    key = scr.getch()
    while key != Keys.QUIT:
        grid.on_press(key)
        key = scr.getch()


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
        default=None,
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
    try:
        args = parser.parse_args()
        sheets = read_spreadsheet(args.file, args.delimiter, args.fillna)
    except TypeError:
        parser.print_usage()
        exit()
    except FileNotFoundError:
        print("Cannot find or open {}".format(args.file))
        exit()
    curses.wrapper(run, sheets, args)
