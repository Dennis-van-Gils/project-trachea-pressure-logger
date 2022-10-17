/*
Example: An R Click and a T Click Board placed in a single current loop.

Every 10 seconds the T Click output current will cycle through 4, 12 and 20 mA.
The R Click will perform an exponential moving average on its oversampled
readings and report over serial every second.

https://github.com/Dennis-van-Gils/MIKROE_4_20mA_RT_Click
Dennis van Gils
22-07-2022
*/

#include <Arduino.h>

#include "MIKROE_4_20mA_RT_Click.h"

// Cable select pins
const uint8_t PIN_R_CLICK = 5;
const uint8_t PIN_T_CLICK = 6;

// Exponential moving average (EMA) parameters of the R Click readings
const uint32_t EMA_INTERVAL = 2000; // Desired oversampling interval [µs]
const float EMA_LP_FREQ = 10.;      // Low-pass filter cut-off frequency [Hz]

// Adjust the calibration parameters as needed
R_Click R_click(PIN_R_CLICK, RT_Click_Calibration{4.03, 19.93, 832, 3999},
                EMA_INTERVAL, EMA_LP_FREQ);
T_Click T_click(PIN_T_CLICK, RT_Click_Calibration{4.02, 19.99, 800, 3980});

void setup() {
  Serial.begin(9600);
  R_click.begin();
  T_click.begin();
}

void loop() {
  uint32_t now = millis();
  static uint32_t tick = now;
  static uint32_t tock = now;
  static uint8_t mA_out = 4;

  if (R_click.poll_EMA()) {
    // DEBUG: Show obtained oversampling interval
    // Serial.println(R_click.get_EMA_obtained_interval());
  }

  // Cycle through the output currents [4, 12, 20] mA, every 10 sec
  if (now - tock > 10000) {
    tock = now;

    if (mA_out == 4) {
      mA_out = 12;
    } else if (mA_out == 12) {
      mA_out = 20;
    } else {
      mA_out = 4;
    }
    T_click.set_mA(mA_out);
  }

  // Report readings over serial every 1 sec
  if (now - tick > 1000) {
    tick = now;

    Serial.print("T click: ");
    Serial.printf("%4u", T_click.get_last_set_bitval());
    Serial.print('\t');
    Serial.printf("%2u", mA_out);
    Serial.print("   |   R click: ");
    Serial.printf("%4u", (uint16_t)round(R_click.get_EMA_bitval()));
    Serial.print('\t');
    Serial.print(R_click.get_EMA_mA(), 2);
    Serial.print('\n');
  }
}
