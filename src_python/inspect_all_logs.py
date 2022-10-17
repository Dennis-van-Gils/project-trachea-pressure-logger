#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Scan for all log files in the current folder. Those that are missing a plot
figure will be processed. Useful tool for quick inspection.
"""
__author__ = "Dennis van Gils"
__authoremail__ = "vangils.dennis@gmail.com"
__url__ = "https://github.com/Dennis-van-Gils/project-diffusive-bubble-growth"
__date__ = "14-10-2022"
__version__ = "1.0"

import os
import re
from LogInspector import read_log, plot_log

if __name__ == "__main__":
    my_path = os.getcwd()
    file_list = [
        f
        for f in os.listdir(my_path)
        if os.path.isfile(os.path.join(my_path, f))
    ]

    for filename in file_list:
        # Look for files matching: ######_###### [+any extra chars] .txt
        p = re.compile("\d{6}_\d{6}(.*?)\.(txt|TXT)$")
        if p.match(filename):
            # Found a matching file
            # Now check if the same filename exists ending with .png
            filename_png = filename[0:-4] + ".png"

            if not os.path.isfile(filename_png):
                # Figure does not yet exists. Create.
                print(f"Reading file: {filename}")
                log = read_log(filename)
                plot_log(log)
