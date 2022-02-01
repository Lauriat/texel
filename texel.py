#!/usr/bin/env python

import math
import curses
from functools import partial
import numpy as np
from numbers import Number
from enum import Enum, auto
from argparse import ArgumentParser

import utils


class Action(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()


class Coordinate:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def add(self, x, y):
        return Coordinate(self.x + x, self.y + y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class Styles:
    def __init__(self):
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(2, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
        self.bordercolor = curses.color_pair(3)
        self.sheets = curses.color_pair(2)
        self.sheet_selection = curses.A_BOLD | curses.A_UNDERLINE | curses.color_pair(2)
        self.header = curses.A_UNDERLINE | self.bordercolor
        self.lineno = self.bordercolor
        self.selection = curses.color_pair(1)
        self.footer = curses.A_UNDERLINE | curses.A_BOLD | curses.color_pair(4)


ARROWKEYS = {
    curses.KEY_UP: Action.UP,
    ord("k"): Action.UP,
    curses.KEY_DOWN: Action.DOWN,
    ord("j"): Action.DOWN,
    curses.KEY_LEFT: Action.LEFT,
    ord("h"): Action.LEFT,
    curses.KEY_RIGHT: Action.RIGHT,
    ord("l"): Action.RIGHT,
}


class Grid:
    def __init__(self, scr, sheets, precision, cellwidth):
        self.scr = scr
        self.sheets = sheets
        self.styles = Styles()
        self.sheetId = 0
        self.sheetNames = list(self.sheets.keys())
        self.precision = precision
        self.fmtwidth = cellwidth
        self.cellwidth = self.fmtwidth + 1
        self.actions = self.arrow_actions()
        self.sep = "|"
        self.init()

    def init(self):
        self.cursor = Coordinate(0, 0)
        self.screen = Coordinate(0, 0)
        self.xl = self.sheets[self.sheetNames[self.sheetId]]
        self.arr = self.xl.to_numpy()
        self.heigth, self.width = self.xl.shape
        self.lnwidth = int(math.log10(self.heigth) + 2)
        self.cols = utils.get_alphas(self.width)
        self.fmtstr = "{:>" + f"{self.fmtwidth}" + "}" + self.sep
        self.lnfmt = "{:>" + f"{self.lnwidth}" + "}"
        self.draw()

    def formatValue(self, x):
        if isinstance(x, Number):
            if not isinstance(x, (int, np.integer)):
                x = round(x, self.precision)
        x = str(x)
        if len(x) > self.fmtwidth:
            x = x[: self.fmtwidth - 3] + "..."
        return self.fmtstr.format(x)

    def arrow_actions(self):
        return {
            Action.UP: partial(self.move_vertical, -1),
            Action.DOWN: partial(self.move_vertical, 1),
            Action.LEFT: partial(self.move_horizontal, -1),
            Action.RIGHT: partial(self.move_horizontal, 1),
        }

    def move_horizontal(self, direction):
        self.cursor.x = (self.cursor.x + direction) % self.width
        if (self.cursor.x - self.screen.x) >= self.scrwidth - 2:
            self.screen.x = self.cursor.x - self.scrwidth + 2
        elif self.cursor.x < self.screen.x:
            self.screen.x = self.cursor.x

    def move_vertical(self, direction):
        self.cursor.y = (self.cursor.y + direction) % self.heigth
        if (self.cursor.y - self.screen.y) >= self.scrheight - 3:
            self.screen.y = self.cursor.y - (self.scrheight - 3) + 1
        elif self.cursor.y < self.screen.y:
            self.screen.y = self.cursor.y

    def on_press(self, key):
        if key in ARROWKEYS:
            self.actions[ARROWKEYS[key]]()
            self.draw()
        else:
            if len(self.sheetNames) > 1:
                if key == ord("\t"):
                    self.sheetId = (self.sheetId + 1) % len(self.sheetNames)
                    self.init()
                if key == 353:
                    self.sheetId = (self.sheetId - 1) % len(self.sheetNames)
                    self.init()

    def set_screen_variables(self):
        self.scrheight, self.fullwidth = self.scr.getmaxyx()
        self.scrwidth = math.ceil((self.fullwidth - self.lnwidth) / self.cellwidth)
        self.num_cols_in_screen = min(self.width - self.screen.x, self.scrwidth)
        self.num_rows_in_screen = min(self.heigth - self.screen.y, self.scrheight - 3)

    def draw_header(self):
        header = (
            ("{:" f"{self.fmtwidth}" + "}" + self.sep) * self.num_cols_in_screen
        ).format(*self.cols[self.screen.x : self.screen.x + self.num_cols_in_screen])
        self.scr.addstr(0, self.lnwidth, header, self.styles.header)

    def draw_grid(self):
        for row in range(self.num_rows_in_screen):
            self.scr.addstr(
                row + 1,
                0,
                self.lnfmt.format(str(row + self.screen.y + 1) + self.sep),
                self.styles.lineno,
            )
            for col in range(self.num_cols_in_screen):
                if (self.screen.add(col, row) == self.cursor):
                    style = self.styles.selection
                else:
                    style = (
                        curses.A_UNDERLINE
                        if (row == self.num_rows_in_screen - 1)
                        else curses.A_NORMAL
                    )
                self.scr.addstr(
                    row + 1,
                    col * self.cellwidth + self.lnwidth,
                    self.formatValue(
                        self.arr[row + self.screen.y, col + self.screen.x]
                    ),
                    style,
                )
        self.scr.addstr(row + 2, 0, " " * self.fullwidth, self.styles.lineno)

    def draw_sheets(self):
        sheetPos = 0
        for i, sheet in enumerate(self.sheetNames):
            if i == self.sheetId:
                self.scr.addstr(
                    self.scrheight - 1,
                    sheetPos,
                    sheet,
                    self.styles.sheet_selection,
                )
            else:
                self.scr.addstr(self.scrheight - 1, sheetPos, sheet, self.styles.sheets)
            sheetPos += len(sheet) + 1

    def draw_footer(self):
        self.scr.addstr(
            self.scrheight - 2,
            0,
            ("{:>" + f"{self.fullwidth}" + "}").format(
                str(self.arr[self.cursor.y, self.cursor.x])
            ),
            self.styles.footer,
        )

    def draw(self):
        self.scr.clear()
        self.set_screen_variables()
        self.draw_header()
        self.draw_grid()
        self.draw_footer()
        self.draw_sheets()


def main(scr, sheets, args):
    grid = Grid(scr, sheets, args.precision, args.cellwidth)
    key = scr.getch()
    while key != ord("q"):
        grid.on_press(key)
        key = scr.getch()


if __name__ == "__main__":
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
        help="Value to use to fill holes in the spreadsheets",
        metavar="FILLNA",
        default=None,
    )
    try:
        args = parser.parse_args()
        sheets = utils.read_spreadsheet(args.file, args.delimiter, args.fillna)
    except TypeError:
        parser.print_usage()
        exit()
    except FileNotFoundError:
        print("Cannot find or open {}".format(args.file))
        exit()
    curses.wrapper(main, sheets, args)
