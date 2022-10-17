.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
.. image:: https://img.shields.io/badge/License-MIT-purple.svg
    :target: https://github.com/Dennis-van-Gils/project-project-diffusive-bubble-growth/blob/master/LICENSE.txt

Diffusive bubble growth
=======================
*A Physics of Fluids project.*

IN PROGRESS: Working proof of concept. Still have to updated comments, docstring
and neatify code here and there.

A pressure logger at 1 kHz for the human trachea project of Marco.

- Github: https://github.com/Dennis-van-Gils/project-project-diffusive-bubble-growth

.. image:: https://github.com/Dennis-van-Gils/project-diffusive-bubble-growth/blob/main/images/screenshot.png

Hardware
========
* Adafruit #3857: Adafruit Feather M4 Express - Featuring ATSAMD51 Cortex M4
* MIKROE 4-20 mA R Click (MIKROE-1387): 4-20 mA current loop receiver
* RS PRO #797-5018: Pressure Sensor, 0-10 bar, current output

Instructions
============
Download the `latest release <https://github.com/Dennis-van-Gils/project-diffusive-bubble-growth/releases/latest>`_
and unpack to a folder onto your drive.

Flashing the firmware
---------------------

Double click the reset button of the Feather while plugged into your PC. This
will mount a drive called `FEATHERBOOT`. Copy
`src_mcu/_build_Feather_M4/CURRENT.UF2 <https://github.com/Dennis-van-Gils/project-diffusive-bubble-growth/raw/main/src_mcu/_build_Feather_M4/CURRENT.UF2>`_
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
