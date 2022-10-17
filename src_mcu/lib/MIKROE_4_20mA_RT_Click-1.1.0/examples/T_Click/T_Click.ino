/*
Example: Set the output current of a T Click Board

https://github.com/Dennis-van-Gils/MIKROE_4_20mA_RT_Click
Dennis van Gils
22-07-2022
*/

#include <Arduino.h>

#include "MIKROE_4_20mA_RT_Click.h"

// The cable select pin of the T Click
const uint8_t PIN_T_CLICK = 6;

// Adjust the calibration parameters as needed
T_Click T_click(PIN_T_CLICK, RT_Click_Calibration{4.02, 19.99, 800, 3980});

void setup() {
  Serial.begin(9600);
  T_click.begin();
  T_click.set_mA(12.);
}

void loop() {}
