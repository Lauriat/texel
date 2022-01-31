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
        self.sheetId = 0
        self.sheetNames = list(self.sheets.keys())
        self.precision = precision
        self.fmtwidth = cellwidth
        self.cellwidth = self.fmtwidth + 1
        self.actions = self.arrow_actions()
        self.sep = "|"
        self.init()

    def init(self):
        self.x = 0
        self.y = 0
        self.screeny = 0
        self.screenx = 0
        self.xl = self.sheets[self.sheetNames[self.sheetId]]
        self.arr = self.xl.to_numpy()
        self.heigth, self.width = self.xl.shape
        self.idxwidth = int(math.log10(self.heigth) + 2)
        self.cols = utils.get_alphas(self.width)
        self.fmtstr = "{:>" + f"{self.fmtwidth}" + "}" + self.sep
        self.width_char = self.cellwidth * self.width + self.idxwidth
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
        self.x = (self.x + direction) % self.width
        if (self.x - self.screenx) >= self.scrwidth - 2:
            self.screenx = self.x - self.scrwidth + 2
        elif self.x < self.screenx:
            self.screenx = self.x

    def move_vertical(self, direction):
        self.y = (self.y + direction) % self.heigth
        if (self.y - self.screeny) >= self.scrheight - 3:
            self.screeny = self.y - (self.scrheight - 3) + 1
        elif self.y < self.screeny:
            self.screeny = self.y

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

    def draw(self):
        self.scr.clear()
        self.scrheight, self.fullwidth = self.scr.getmaxyx()
        self.scrwidth = math.ceil((self.fullwidth - self.idxwidth) / self.cellwidth)
        ww = min(self.width - self.screenx, self.scrwidth)
        header = (("{:" f"{self.fmtwidth}" + "}" + self.sep) * ww).format(
            *self.cols[self.screenx : self.screenx + ww]
        )
        self.scr.addstr(
            0, self.idxwidth, header, curses.A_UNDERLINE | curses.color_pair(3)
        )
        self.draw_grid()
        fw = "{:>" + f"{self.fullwidth}" + "}"
        selval = str(self.arr[self.y][self.x])
        self.scr.addstr(
            self.scrheight - 2,
            0,
            fw.format(selval),
            curses.A_UNDERLINE | curses.A_BOLD | curses.color_pair(4),
        )
        w = 0
        for i, sheet in enumerate(self.sheetNames):
            if i == self.sheetId:
                self.scr.addstr(
                    self.scrheight - 1,
                    w,
                    sheet,
                    curses.A_BOLD | curses.A_UNDERLINE | curses.color_pair(2),
                )
            else:
                self.scr.addstr(self.scrheight - 1, w, sheet, curses.color_pair(2))
            w += len(sheet) + 1

    def draw_grid(self):
        for row in range(min(self.heigth - self.screeny, self.scrheight - 3)):
            ee = "{:>" + f"{self.idxwidth}" + "}"
            self.scr.addstr(
                row + 1,
                0,
                ee.format(str(row + self.screeny + 1) + self.sep),
                curses.color_pair(3),
            )
            for col in range(min(self.width - self.screenx, self.scrwidth)):
                stringi = self.formatValue(
                    self.arr[row + self.screeny, col + self.screenx]
                )
                if (col + self.screenx == self.x) and (row + self.screeny == self.y):
                    self.scr.addstr(
                        row + 1,
                        col * self.cellwidth + self.idxwidth,
                        stringi,
                        curses.color_pair(1),
                    )
                else:
                    if row == self.scrheight - 4:
                        self.scr.addstr(
                            row + 1,
                            col * self.cellwidth + self.idxwidth,
                            stringi,
                            curses.A_UNDERLINE,
                        )
                    else:
                        self.scr.addstr(
                            row + 1,
                            col * self.cellwidth + self.idxwidth,
                            stringi,
                        )


def main(scr, sheets, args):
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(2, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
    grid = Grid(scr, sheets, args.precision, args.cellwidth)
    while True:
        key = scr.getch()
        if key == ord("q"):
            break
        grid.on_press(key)


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
    try:
        args = parser.parse_args()
        sheets = utils.read_spreadsheet(args.file, args.delimiter)
    except TypeError:
        parser.print_usage()
        exit()
    except FileNotFoundError:
        print("Cannot find or open {}".format(args.file))
        exit()
    curses.wrapper(main, sheets, args)
