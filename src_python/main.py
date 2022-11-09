#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A pressure logger for Marco de Paoli's trachea tube.
"""
__author__ = "Dennis van Gils"
__authoremail__ = "vangils.dennis@gmail.com"
__url__ = "https://github.com/Dennis-van-Gils/project-trachea-pressure-logger"
__date__ = "09-11-2022"
__version__ = "1.0"
print(__url__)
# pylint: disable=bare-except, broad-except, unnecessary-lambda

import os
import sys

# Constants
DAQ_INTERVAL_MS = 1  # [ms] Expected, not ground truth.
CHART_INTERVAL_MS = 10  # [ms]
CHART_HISTORY_TIME = 1800  # [s]

# Global flags
TRY_USING_OPENGL = True
DEBUG = False  # Show debug info in terminal?

# Mechanism to support both PyQt and PySide
# -----------------------------------------

PYQT5 = "PyQt5"
PYQT6 = "PyQt6"
PYSIDE2 = "PySide2"
PYSIDE6 = "PySide6"
QT_LIB_ORDER = [PYQT5, PYSIDE2, PYSIDE6, PYQT6]
QT_LIB = os.getenv("PYQTGRAPH_QT_LIB")

# Parse optional cli argument to enfore a QT_LIB
# cli example: python benchmark.py pyside6
if len(sys.argv) > 1:
    arg1 = str(sys.argv[1]).upper()
    for i, lib in enumerate(QT_LIB_ORDER):
        if arg1 == lib.upper():
            QT_LIB = lib
            break

# pylint: disable=import-error, no-name-in-module, c-extension-no-member
if QT_LIB is None:
    for lib in QT_LIB_ORDER:
        if lib in sys.modules:
            QT_LIB = lib
            break

if QT_LIB is None:
    for lib in QT_LIB_ORDER:
        try:
            __import__(lib)
            QT_LIB = lib
            break
        except ImportError:
            pass

if QT_LIB is None:
    this_file = __file__.split(os.sep)[-1]
    raise Exception(
        f"{this_file} requires PyQt5, PyQt6, PySide2 or PySide6; "
        "none of these packages could be imported."
    )

# fmt: off
if QT_LIB == PYQT5:
    from PyQt5 import QtCore, QtGui, QtWidgets as QtWid    # type: ignore
    from PyQt5.QtCore import pyqtSlot as Slot              # type: ignore
elif QT_LIB == PYQT6:
    from PyQt6 import QtCore, QtGui, QtWidgets as QtWid    # type: ignore
    from PyQt6.QtCore import pyqtSlot as Slot              # type: ignore
elif QT_LIB == PYSIDE2:
    from PySide2 import QtCore, QtGui, QtWidgets as QtWid  # type: ignore
    from PySide2.QtCore import Slot                        # type: ignore
elif QT_LIB == PYSIDE6:
    from PySide6 import QtCore, QtGui, QtWidgets as QtWid  # type: ignore
    from PySide6.QtCore import Slot                        # type: ignore
# fmt: on

QT_VERSION = (
    QtCore.QT_VERSION_STR if QT_LIB in (PYQT5, PYQT6) else QtCore.__version__
)

# pylint: enable=import-error, no-name-in-module, c-extension-no-member
# \end[Mechanism to support both PyQt and PySide]
# -----------------------------------------------

import numpy as np
import pyqtgraph as pg

print(f"{QT_LIB:9s} {QT_VERSION}")
print(f"PyQtGraph {pg.__version__}")

import dvg_pyqt_controls as controls
from dvg_debug_functions import tprint, dprint, print_fancy_traceback as pft
from dvg_pyqt_filelogger import FileLogger
from dvg_pyqtgraph_threadsafe import (
    HistoryChartCurve,
    LegendSelect,
    PlotManager,
)

from dvg_devices.Arduino_protocol_serial import Arduino
from dvg_qdeviceio import QDeviceIO, DAQ_TRIGGER

if TRY_USING_OPENGL:
    try:
        import OpenGL.GL as gl  # pylint: disable=unused-import
        from OpenGL.version import __version__ as gl_version
    except:
        print("PyOpenGL  not found")
        print("To install: `conda install pyopengl` or `pip install pyopengl`")
    else:
        print(f"PyOpenGL  {gl_version}")
        pg.setConfigOptions(useOpenGL=True)
        pg.setConfigOptions(antialias=True)
        pg.setConfigOptions(enableExperimental=True)
else:
    print("PyOpenGL  disabled")

# Global pyqtgraph configuration
# pg.setConfigOptions(leftButtonPan=False)
pg.setConfigOption("background", controls.COLOR_GRAPH_BG)
pg.setConfigOption("foreground", controls.COLOR_GRAPH_FG)


def get_current_date_time():
    cur_date_time = QtCore.QDateTime.currentDateTime()
    return (
        cur_date_time.toString("dd-MM-yyyy"),  # Date
        cur_date_time.toString("HH:mm:ss"),  # Time
        cur_date_time.toString("yyMMdd_HHmmss"),  # Reverse notation date-time
    )


# ------------------------------------------------------------------------------
#   State
# ------------------------------------------------------------------------------


class State(object):
    """Reflects the actual readings of the Arduino. There should only be one
    instance of the State class.
    """

    def __init__(self):
        self.time = np.nan  # [s]
        self.pres = np.nan  # [mbar]


state = State()

# ------------------------------------------------------------------------------
#   MainWindow
# ------------------------------------------------------------------------------


class MainWindow(QtWid.QWidget):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)

        self.setWindowTitle("Trachea pressure logger")
        self.setGeometry(350, 60, 1200, 900)
        self.setStyleSheet(
            controls.SS_TEXTBOX_READ_ONLY
            + controls.SS_GROUP
            + controls.SS_HOVER
        )

        # -------------------------
        #   Top frame
        # -------------------------

        # Left box
        self.qlbl_update_counter = QtWid.QLabel("0")
        self.qlbl_DAQ_rate = QtWid.QLabel("DAQ: nan Hz")
        self.qlbl_DAQ_rate.setStyleSheet("QLabel {min-width: 7em}")
        self.qlbl_recording_time = QtWid.QLabel()

        vbox_left = QtWid.QVBoxLayout()
        vbox_left.addWidget(self.qlbl_update_counter, stretch=0)
        vbox_left.addStretch(1)
        vbox_left.addWidget(self.qlbl_recording_time, stretch=0)
        vbox_left.addWidget(self.qlbl_DAQ_rate, stretch=0)

        # Middle box
        self.qlbl_title = QtWid.QLabel(
            "Trachea pressure logger",
            font=QtGui.QFont("Palatino", 14, weight=QtGui.QFont.Weight.Bold),
        )
        self.qlbl_title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.qlbl_cur_date_time = QtWid.QLabel("00-00-0000    00:00:00")
        self.qlbl_cur_date_time.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignCenter
        )
        self.qpbt_record = controls.create_Toggle_button(
            "Click to start recording to file"
        )
        self.qpbt_record.clicked.connect(lambda state: logger.record(state))

        vbox_middle = QtWid.QVBoxLayout()
        vbox_middle.addWidget(self.qlbl_title)
        vbox_middle.addWidget(self.qlbl_cur_date_time)
        vbox_middle.addWidget(self.qpbt_record)

        # Right box
        p = {
            "alignment": QtCore.Qt.AlignmentFlag.AlignRight
            | QtCore.Qt.AlignmentFlag.AlignVCenter
        }
        self.qpbt_exit = QtWid.QPushButton("Exit", minimumHeight=30)
        self.qpbt_exit.clicked.connect(self.close)
        self.qlbl_GitHub = QtWid.QLabel(
            f'<a href="{__url__}">GitHub source</a>', **p
        )
        self.qlbl_GitHub.setTextFormat(QtCore.Qt.TextFormat.RichText)
        self.qlbl_GitHub.setTextInteractionFlags(
            QtCore.Qt.TextInteractionFlag.TextBrowserInteraction
        )
        self.qlbl_GitHub.setOpenExternalLinks(True)

        vbox_right = QtWid.QVBoxLayout(spacing=4)
        vbox_right.addWidget(self.qpbt_exit, stretch=0)
        vbox_right.addStretch(1)
        vbox_right.addWidget(QtWid.QLabel(__author__, **p))
        vbox_right.addWidget(self.qlbl_GitHub)
        vbox_right.addWidget(QtWid.QLabel(f"v{__version__}", **p))

        # Round up top frame
        hbox_top = QtWid.QHBoxLayout()
        hbox_top.addLayout(vbox_left, stretch=0)
        hbox_top.addStretch(1)
        hbox_top.addLayout(vbox_middle, stretch=0)
        hbox_top.addStretch(1)
        hbox_top.addLayout(vbox_right, stretch=0)

        # -------------------------
        #   Bottom frame
        # -------------------------

        #  Charts
        # -------------------------

        self.gw = pg.GraphicsLayoutWidget()

        # Plot: Pressure
        p = {
            "color": controls.COLOR_GRAPH_FG.name(),
            "font-size": "12pt",
            "font-family": "Helvetica",
        }
        self.pi_pres = self.gw.addPlot(row=1, col=0)
        self.pi_pres.setLabel("left", text="pressure (mbar)", **p)

        self.plots = [self.pi_pres]
        for plot in self.plots:
            plot.setClipToView(True)
            plot.showGrid(x=1, y=1)
            plot.setLabel("bottom", text="history (s)", **p)
            plot.setMenuEnabled(True)
            plot.enableAutoRange(axis=pg.ViewBox.XAxis, enable=False)
            plot.enableAutoRange(axis=pg.ViewBox.YAxis, enable=True)
            plot.setAutoVisible(y=True)
            plot.setRange(xRange=[-CHART_HISTORY_TIME, 0])

        # Curves
        capacity = round(CHART_HISTORY_TIME * 1e3 / DAQ_INTERVAL_MS)
        PEN_02 = pg.mkPen(color=[252, 15, 192], width=3)

        self.tscurve_pres = HistoryChartCurve(
            capacity=capacity,
            linked_curve=self.pi_pres.plot(pen=PEN_02, name="Pressure"),
        )
        self.tscurves = [self.tscurve_pres]

        #  Group `Readings`
        # -------------------------

        legend = LegendSelect(
            linked_curves=self.tscurves, hide_toggle_button=True
        )

        p = {
            "readOnly": True,
            "alignment": QtCore.Qt.AlignmentFlag.AlignRight,
            "maximumWidth": 54,
        }
        self.qlin_temp = QtWid.QLineEdit(**p)
        self.qlin_pres = QtWid.QLineEdit(**p)

        # fmt: off
        legend.grid.setHorizontalSpacing(6)
        legend.grid.addWidget(self.qlin_pres               , 0, 2)
        legend.grid.addWidget(QtWid.QLabel("± 0.02 mbar"), 0, 3)
        # fmt: on

        qgrp_readings = QtWid.QGroupBox("Readings")
        qgrp_readings.setLayout(legend.grid)

        #  Group 'Log comments'
        # -------------------------

        self.qtxt_comments = QtWid.QTextEdit()
        grid = QtWid.QGridLayout()
        grid.addWidget(self.qtxt_comments, 0, 0)

        qgrp_comments = QtWid.QGroupBox("Log comments")
        qgrp_comments.setLayout(grid)

        #  Group 'Charts'
        # -------------------------

        self.plot_manager = PlotManager(parent=self)
        self.plot_manager.add_autorange_buttons(linked_plots=self.plots)
        self.plot_manager.add_preset_buttons(
            linked_plots=self.plots,
            linked_curves=self.tscurves,
            presets=[
                {
                    "button_label": "00:30",
                    "x_axis_label": "history (sec)",
                    "x_axis_divisor": 1,
                    "x_axis_range": (-30, 0),
                },
                {
                    "button_label": "01:00",
                    "x_axis_label": "history (sec)",
                    "x_axis_divisor": 1,
                    "x_axis_range": (-60, 0),
                },
                {
                    "button_label": "10:00",
                    "x_axis_label": "history (min)",
                    "x_axis_divisor": 60,
                    "x_axis_range": (-10, 0),
                },
                {
                    "button_label": "30:00",
                    "x_axis_label": "history (min)",
                    "x_axis_divisor": 60,
                    "x_axis_range": (-30, 0),
                },
            ],
        )
        self.plot_manager.add_clear_button(linked_curves=self.tscurves)
        self.plot_manager.perform_preset(1)

        qgrp_chart = QtWid.QGroupBox("Charts")
        qgrp_chart.setLayout(self.plot_manager.grid)

        vbox = QtWid.QVBoxLayout()
        vbox.addWidget(qgrp_readings)
        vbox.addWidget(qgrp_comments)
        vbox.addWidget(qgrp_chart, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)
        vbox.addStretch()

        # Round up bottom frame
        hbox_bot = QtWid.QHBoxLayout()
        hbox_bot.addWidget(self.gw, 1)
        hbox_bot.addLayout(vbox, 0)

        # -------------------------
        #   Round up full window
        # -------------------------

        vbox = QtWid.QVBoxLayout(self)
        vbox.addLayout(hbox_top, stretch=0)
        vbox.addSpacerItem(QtWid.QSpacerItem(0, 10))
        vbox.addLayout(hbox_bot, stretch=1)

    # --------------------------------------------------------------------------
    #   Handle controls
    # --------------------------------------------------------------------------

    @Slot()
    def update_GUI(self):
        str_cur_date, str_cur_time, _ = get_current_date_time()
        self.qlbl_cur_date_time.setText(f"{str_cur_date}    {str_cur_time}")
        self.qlbl_update_counter.setText(f"{ard_qdev.update_counter_DAQ:d}")
        self.qlbl_DAQ_rate.setText(
            f"DAQ: {ard_qdev.obtained_DAQ_rate_Hz:.1f} Hz"
        )
        self.qlbl_recording_time.setText(
            f"REC: {logger.pretty_elapsed()}" if logger.is_recording() else ""
        )
        self.qlin_pres.setText(f"{state.pres:.2f}")

    @Slot()
    def update_chart(self):
        if DEBUG:
            tprint("update_chart")

        for tscurve in self.tscurves:
            tscurve.update()


# ------------------------------------------------------------------------------
#   Program termination routines
# ------------------------------------------------------------------------------


def stop_running():
    app.processEvents()
    ard_qdev.quit()
    logger.close()

    print("Stopping timers................ ", end="")
    timer_GUI.stop()
    timer_charts.stop()
    print("done.")


@Slot()
def notify_connection_lost():
    stop_running()

    window.qlbl_title.setText("! ! !    LOST CONNECTION    ! ! !")
    str_cur_date, str_cur_time, _ = get_current_date_time()
    str_msg = f"{str_cur_date} {str_cur_time}\nLost connection to Arduino."
    print(f"\nCRITICAL ERROR @ {str_msg}")
    reply = QtWid.QMessageBox.warning(
        window, "CRITICAL ERROR", str_msg, QtWid.QMessageBox.StandardButton.Ok
    )

    if reply == QtWid.QMessageBox.StandardButton.Ok:
        pass  # Leave the GUI open for read-only inspection by the user


@Slot()
def about_to_quit():
    print("\nAbout to quit")
    stop_running()
    ard.close()


# ------------------------------------------------------------------------------
#   Your Arduino update function
# ------------------------------------------------------------------------------


def DAQ_function():
    # Date-time keeping
    str_cur_date, str_cur_time, str_cur_datetime = get_current_date_time()

    # Listen to the Arduino for sensor readings send out over serial
    success, reply = ard.readline()
    # dprint(reply)

    if not (success):
        dprint(
            "'%s' reports IOError @ %s %s"
            % (ard.name, str_cur_date, str_cur_time)
        )
        return False

    # Parse readings into separate state variables
    try:
        split_reply = (reply.strip()).split("\t")
        state.time = float(split_reply[0]) / 1000
        state.pres = float(split_reply[1])
    except Exception as err:
        pft(err, 3)
        dprint(f"'{ard.name}' reports IOError @ {str_cur_date} {str_cur_time}")
        return False

    # Add readings to chart histories
    window.tscurve_pres.appendData(state.time, state.pres)

    # Logging to file
    logger.update(filepath=str_cur_datetime + ".txt", mode="w")

    # Return success
    return True


# ------------------------------------------------------------------------------
#   File logger
# ------------------------------------------------------------------------------


def write_header_to_log():
    str_cur_date, str_cur_time, _ = get_current_date_time()
    logger.write("[HEADER]\n")
    logger.write(str_cur_date + "\n")
    logger.write(str_cur_time + "\n")
    logger.write(window.qtxt_comments.toPlainText())
    logger.write("\n\n[DATA]\n")
    logger.write("[s]\t[±0.02 mbar]\n")
    logger.write("time\tpres\n")


def write_data_to_log():
    logger.write(f"{logger.elapsed():.3f}\t{state.pres:.2f}\n")


# ------------------------------------------------------------------------------
#   Main
# ------------------------------------------------------------------------------

if __name__ == "__main__":

    # Connect to: Arduino
    ard = Arduino(name="Ard", connect_to_specific_ID="Trachea pressure logger")
    ard.serial_settings["baudrate"] = 115200
    ard.auto_connect(filepath_last_known_port="config/port_Arduino.txt")

    if not (ard.is_alive):
        print("\nCheck connection and try resetting the Arduino.")
        print("Exiting...\n")
        sys.exit(0)

    ard.write("on\n")  # TODO: make nicer

    # Create application and main window
    QtCore.QThread.currentThread().setObjectName("MAIN")  # For DEBUG info
    app = QtWid.QApplication(sys.argv)
    app.setFont(QtGui.QFont("Arial", 9))
    app.aboutToQuit.connect(about_to_quit)
    window = MainWindow()

    # Set up multi-threaded communication: Arduino
    ard_qdev = QDeviceIO(ard)
    ard_qdev.create_worker_DAQ(
        DAQ_trigger=DAQ_TRIGGER.CONTINUOUS,
        DAQ_function=DAQ_function,
        critical_not_alive_count=3,
        debug=DEBUG,
    )
    ard_qdev.signal_DAQ_updated.connect(window.update_GUI)
    ard_qdev.signal_connection_lost.connect(notify_connection_lost)

    # File logger
    logger = FileLogger(
        write_header_function=write_header_to_log,
        write_data_function=write_data_to_log,
    )
    logger.signal_recording_started.connect(
        lambda filepath: window.qpbt_record.setText(
            f"Recording to file: {filepath}"
        )
    )
    logger.signal_recording_stopped.connect(
        lambda: window.qpbt_record.setText("Click to start recording to file")
    )

    # Timers
    timer_GUI = QtCore.QTimer()
    timer_GUI.timeout.connect(window.update_GUI)
    timer_GUI.start(100)

    timer_charts = QtCore.QTimer()
    timer_charts.timeout.connect(window.update_chart)
    timer_charts.start(CHART_INTERVAL_MS)

    # Start threads
    ard_qdev.start()  # NOTE: The DAQ worker thread starts up in a paused state
    ard_qdev.unpause_DAQ()  # Start listening continuously to the Arduino

    # Start the main GUI event loop
    window.show()
    if QT_LIB in (PYQT5, PYSIDE2):
        sys.exit(app.exec_())
    else:
        sys.exit(app.exec())
