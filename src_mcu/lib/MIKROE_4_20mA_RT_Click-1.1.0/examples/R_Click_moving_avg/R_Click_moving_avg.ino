/*
Example: Read out an R Click Board using an exponential moving average

https://github.com/Dennis-van-Gils/MIKROE_4_20mA_RT_Click
Dennis van Gils
22-07-2022
*/

#include <Arduino.h>

#include "MIKROE_4_20mA_RT_Click.h"

// The cable select pin of the R Click
const uint8_t PIN_R_CLICK = 5;

// Exponential moving average (EMA) parameters of the R Click readings
const uint32_t EMA_INTERVAL = 2000; // Desired oversampling interval [µs]
const float EMA_LP_FREQ = 10.;      // Low-pass filter cut-off frequency [Hz]

// Adjust the calibration parameters as needed
R_Click R_click(PIN_R_CLICK, RT_Click_Calibration{4.03, 19.93, 832, 3999});

void setup() {
  Serial.begin(9600);
  R_click.begin();
}

void loop() {
  uint32_t now = millis();
  static uint32_t tick = now;

  R_click.poll_EMA();

  // Report readings over serial every 1 sec
  if (now - tick > 1000) {
    tick = now;
    Serial.println(R_click.get_EMA_mA());
  }
}
