.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
.. image:: https://img.shields.io/badge/License-MIT-purple.svg
    :target: https://github.com/Dennis-van-Gils/project-project-trachea-pressure-logger/blob/master/LICENSE.txt

Diffusive bubble growth
=======================
*A Physics of Fluids project.*

A pressure logger at 1 kHz for the human trachea project of Marco de Paoli.

- Github: https://github.com/Dennis-van-Gils/project-trachea-pressure-logger

.. image:: https://github.com/Dennis-van-Gils/project-trachea-pressure-logger/blob/main/images/screenshot.png

Hardware
========
* Adafruit #3857: Adafruit Feather M4 Express - Featuring ATSAMD51 Cortex M4
* MIKROE 4-20 mA R Click (MIKROE-1387): 4-20 mA current loop receiver
* Omega PX2300: Pressure Sensor, differential wet-wet +/- 0.067 bar, current output, 0.25 FS accuracy

Pinout
======

==========        =======
Feather M4        R Click
----------        -------
3V                3.3V
GND               GND
D5                CS
MI                SDO
SCK               SCK
==========        =======

Instructions
============
Download the `latest release <https://github.com/Dennis-van-Gils/project-trachea-pressure-logger/releases/latest>`_
and unpack to a folder onto your drive.

Flashing the firmware
---------------------

Double click the reset button of the Feather while plugged into your PC. This
will mount a drive called `FEATHERBOOT`. Copy
`src_mcu/_build_Feather_M4/CURRENT.UF2 <https://github.com/Dennis-van-Gils/project-trachea-pressure-logger/raw/main/src_mcu/_build_Feather_M4/CURRENT.UF2>`_
onto the Featherboot drive. It will restart automatically with the new
firmware.

Running the application
-----------------------

| Preferred distribution: Anaconda full or Miniconda

    * `Anaconda <https://www.anaconda.com>`_
    * `Miniconda <https://docs.conda.io/en/latest/miniconda.html>`_

Open `Anaconda Prompt` and navigate to the unpacked folder. Run the following to
install the necessary packages: ::

   cd src_python
   conda create -n py39 python=3.9
   conda activate py39
   pip install -r requirements.txt

Now you can run the application.
In Anaconda prompt:

::

    conda activate py39
    ipython main.py


LED status lights
=================

* Solid blue: Booting and setting up
* Solid green: Ready for communication
* Flashing green: Sensor data is being send over USB
