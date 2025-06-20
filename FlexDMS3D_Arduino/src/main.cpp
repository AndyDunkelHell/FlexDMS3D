#include <Arduino.h>
#include <SoftwareSerial.h>
#include <Wire.h>
#include "CommandHandler.h"
#include <AceRoutine.h>

CommandHandler<10, 90, 15> SerialCommandHandler;
using namespace ace_routine;

bool print_val = false;
int val = 0;
/*
  Oversampling Example for a Small Signal
  ---------------------------------------
  Reads from analog pin (A0), performs 16-sample averaging,
  and prints the resulting measurement over Serial.
*/

const int SENSOR_PIN = A0;
const int OVERSAMPLING_FACTOR = 16;
const float ADC_MAX_COUNTS = 1023.0;  // For 10-bit ADC on Arduino UNO
const float V_REF = 5;            // Reference voltage for ADC


// Smoothing factor for the IIR filter.
// 0.9 = "smooth" (slow response), 0.1 = "less smooth" (faster response).
float alpha = 0.9;  

// We'll keep track of the filtered value across loop iterations
float filteredVoltage = 0.0;  
bool init_limits = false;
float Rbot;
float Rtop;

COROUTINE(sendPos){
  COROUTINE_LOOP(){  
    if (print_val){
      //val = analogRead(SENSOR_PIN);  // read the input pin
      long sum = 0;
    
      // Collect multiple samples
      for (int i = 0; i < OVERSAMPLING_FACTOR; i++) {
        int adcValue = analogRead(SENSOR_PIN);
        sum += adcValue;
      }
      
      // Compute the average
      float averageReading = sum / (float)OVERSAMPLING_FACTOR;

      // Convert ADC counts to voltage (if needed)
      float out_voltage = (averageReading / ADC_MAX_COUNTS) * V_REF;
      float out_voltage_gain = -((out_voltage) - 1.65)/1.213;

      // 3) LOW-PASS FILTER
      // filteredVoltage[n] = alpha * filteredVoltage[n-1] + (1 - alpha) * voltage
      filteredVoltage = alpha * filteredVoltage + (1.0 - alpha) * out_voltage_gain;
      

      //float out_voltage= val * 0.004887585533;
      float voltage_diff= filteredVoltage;
      float R = 43;
      float Rx = R*(((0.61*voltage_diff) + 1)/(1-(0.61*voltage_diff)));

      if (!init_limits){
        init_limits = true;
        Rtop = Rx + 5;
        Rbot = Rx - 5;
      }

      if(out_voltage != 0){
      char buffer[64];
      char s_voltage[10];
      char s_diff[10];  
      char s_Rx[10];
      char s_Rtop[10];
      char s_Rbot[10];

      dtostrf(out_voltage, 9, 6, s_voltage);
      dtostrf(voltage_diff, 9, 6, s_diff);
      dtostrf(Rx, 4, 2, s_Rx);
      dtostrf(Rtop, 2, 0, s_Rtop);
      dtostrf(Rbot, 2, 0, s_Rbot);
      sprintf(buffer, "%s,%s,%s,2,-2,%s,%s", s_voltage, s_diff, s_Rx, s_Rbot, s_Rtop);
      Serial.println(buffer);          
      }
    }
    COROUTINE_DELAY(10);
  }
}

void conn(CommandParameter &parameters){

  Serial.print(F("Connection confirmed and started reading vals")); // When Connected Return to Python initiating the Motors
  print_val = true; 
}

void stop_send(CommandParameter &parameters){
  Serial.print(F("STOP"));
  print_val = false; 
}

void setup() {
  Serial.begin(250000);

  SerialCommandHandler.AddCommand(F("connect"), conn);\
  SerialCommandHandler.AddCommand(F("stop"), stop_send);


}

void loop() {

  SerialCommandHandler.Process();
  sendPos.runCoroutine();

  // if (print_val){
  //   val = analogRead(A0);  // read the input pin
  //   Serial.println(val);          // debug value
  // } 
}

