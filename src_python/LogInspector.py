#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Provides functions for reading in and plotting log files specific to the
current project.

When called straight from the command line it will open a file-navigator.
"""
__author__ = "Dennis van Gils"
__authoremail__ = "vangils.dennis@gmail.com"
__url__ = "https://github.com/Dennis-van-Gils/project-trachea-pressure-growth"
__date__ = "09-11-2022"
__version__ = "1.0"


from pathlib import Path
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt


class Log:
    """Structure that holds the timeseries data and additional information of a
    log file specific to the current project."""

    def __init__(self):
        self.filename = ""
        self.header_date = ""
        self.header_time = ""
        self.header_msg = [""]
        self.time = np.array([])
        self.pres = np.array([])


# ------------------------------------------------------------------------------
#   read_log
# ------------------------------------------------------------------------------


def read_log(filepath=None) -> Log:
    """Reads in a log file.

    Args:
        filepath (pathlib.Path, str):
            Path to the data file to open.

    Returns: instance of Log class
    """
    if isinstance(filepath, str):
        filepath = Path(filepath)

    if not isinstance(filepath, Path):
        raise Exception(
            "Wrong type passed to read_log(). "
            "Should be (str) or (pathlib.Path)."
        )

    if not filepath.is_file():
        raise Exception("File can not be found\n %s" % filepath.name)

    with filepath.open() as f:
        log = Log()

        # Scan the first lines for the start of the header and data sections
        MAX_LINES = 100  # Stop scanning after this number of lines
        str_header = []
        success = False
        for i_line in range(MAX_LINES):
            str_line = f.readline().strip()

            if str_line.upper() == "[HEADER]":
                # Simply skip
                pass
            elif str_line.upper() == "[DATA]":
                # Found data section. Exit loop.
                i_line_data = i_line
                success = True
                break
            else:
                # We must be in the header section now
                str_header.append(str_line)

        if not success:
            raise Exception(
                "Incorrect file format. Could not find [DATA] section."
            )

        # Read in all data columns including column names
        tmp_table = np.genfromtxt(
            filepath.name,
            delimiter="\t",
            names=True,
            skip_header=i_line_data + 2,
        )

        # Rebuild into a Matlab style 'struct'
        log.filename = filepath.name[0:-4]
        log.header_date = str_header[0]
        log.header_time = str_header[1]
        log.header_msg = str_header[2:]
        log.time = tmp_table["time"]
        log.pres = tmp_table["pres"]

    return log


# ------------------------------------------------------------------------------
#   plot_log
# ------------------------------------------------------------------------------

# Special characters
CHAR_PM = "\u00B1"
CHAR_DEG = "\u00B0"

# Colors
cm = (
    np.array(
        [
            [255, 255, 0],
            [252, 15, 192],
            [0, 255, 255],
            [255, 255, 255],
            [255, 127, 39],
            [0, 255, 0],
        ]
    )
    / 255
)


def plot_log(log: Log):
    # Lay-out
    mpl.style.use("dark_background")
    mpl.rcParams["font.size"] = 12
    # mpl.rcParams['font.weight'] = "bold"
    mpl.rcParams["axes.titlesize"] = 14
    mpl.rcParams["axes.labelsize"] = 14
    mpl.rcParams["axes.titleweight"] = "bold"
    mpl.rcParams["axes.formatter.useoffset"] = False
    # mpl.rcParams["axes.labelweight"] = "bold"
    mpl.rcParams["lines.linewidth"] = 2
    mpl.rcParams["grid.color"] = "0.25"

    fig1 = plt.figure(figsize=(16, 10), dpi=90)
    fig1.canvas.manager.set_window_title(log.filename)

    ax1 = fig1.add_subplot(1, 1, 1)

    # Plot pressure
    ax1.plot(log.time, log.pres, color=cm[1], label="Pressure")
    ax1.set_title(f"Pressure ({CHAR_PM} 0.02 mbar)")
    ax1.set_xlabel("time (s)")
    ax1.set_ylabel("pressure (mbar)")
    ax1.grid(True)

    # Finalize lay-out
    ax_w = 0.9
    ax_h = 0.8
    ax1.set_position([0.08, 0.06, ax_w, ax_h])

    # Save figure
    img_format = "png"
    fn_save = f"{log.filename}.{img_format}"
    plt.savefig(
        fn_save,
        dpi=90,
        orientation="portrait",
        format=img_format,
        transparent=False,
    )
    print(f"Saved image: {fn_save}")


# ------------------------------------------------------------------------------
#   Main
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    import os
    import sys
    import tkinter
    from tkinter import filedialog

    # Check for optional input arguments
    filename_supplied = False
    for arg in sys.argv[1:]:
        filename = arg
        filename_supplied = True

    root = tkinter.Tk()
    root.withdraw()  # Disable root window

    if not filename_supplied:
        filename = filedialog.askopenfilename(
            initialdir=os.getcwd(),
            title="Select data file",
            filetypes=(("text files", "*.txt"), ("all files", "*.*")),
        )
    if filename == "":
        sys.exit(0)

    root.destroy()  # Close file dialog

    print(f"Reading file: {filename}")
    plot_log(read_log(filename))
    plt.show()
