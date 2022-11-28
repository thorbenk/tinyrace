#include "FastLED.h"
#include "LiquidCrystal_I2C.h"
#include "Button2.h"

#define NUM_LEDS 16
#define LANE_LEDS 8

CRGB leds[NUM_LEDS];

// PINS
const int lane_sensors[2][2] = {{A0, A1}, {A2, A3}};
const int lane_sensor_thresh[2][2] = {{10, 10}, {10, 10}};
constexpr int neopixels_data_pin = 4;
constexpr int reset_button_pin = 12;


unsigned long lane_micros[2][2];
bool lane_passed[2][2];
int lane_values[2][2];
unsigned int iters[2];
unsigned long last_led_update;
uint8_t led_number;

LiquidCrystal_I2C lcd(0x27, 16, 2);

constexpr float TO_METER_PER_SECOND = 0.08 * 1E6;
constexpr float TO_KMH = 0.08 * 1E6 * 3.6;
constexpr float TO_KMH_UNSCALED = 0.08 * 1E6 * 3.6 * 64;

Button2 resetButton;

//#define DEBUG_RACE
#define DEBUG_UPDATE

void full_reset() {
    for (uint8_t lane = 0; lane < 2; ++lane) {
      for (uint8_t pos = 0; pos < 2; ++pos) {
        lane_micros[lane][pos] = 0;
        lane_values[lane][pos] = 0;
        lane_passed[lane][pos] = false;
      }
      iters[lane] = 0;
    }
    last_led_update = 0;
    led_number = 0;
}

void setup() {
    pinMode(LED_BUILTIN, OUTPUT);
    for (uint8_t lane = 0; lane < 2; ++lane) {
      for (uint8_t pos = 0; pos < 2; ++pos) {
        pinMode(lane_sensors[lane][pos], INPUT);
      }
    }

#if 1
    FastLED.addLeds<WS2812, neopixels_data_pin, GRB>(leds, NUM_LEDS);
    FastLED.setMaxRefreshRate(0);

    lcd.init();
    lcd.backlight();
    
    lcd.setCursor(0, 0);
    lcd.print("Jannis'");
    lcd.setCursor(0,1);
    lcd.print("Hotwheels Rennen");
#endif    

    full_reset();

    resetButton.begin(reset_button_pin, INPUT, false);
 
    Serial.begin(9600);
    while (!Serial) {;}

    Serial.println("setup done");
}

void debug_race() {
  for (uint8_t lane = 0; lane < 2; ++lane) {
      for (uint8_t pos = 0; pos < 2; ++pos) {
        lane_values[lane][pos] = analogRead(lane_sensors[lane][pos]);
      }
  }
  
  Serial.print("Lane A: V1: ");
  Serial.print(lane_values[0][0]);
  Serial.print(", V2: ");
  Serial.print(lane_values[0][1]);

  Serial.print(" | Lane B: V1: ");
  Serial.print(lane_values[1][0]);
  Serial.print(", V2: ");
  Serial.println(lane_values[1][1]);

  //Serial.println(resetButton.clickToString(resetButton.wait()));
  
  delay(50);
}

void loop() {
#ifdef DEBUG_RACE
  debug_race();
#else

    if (last_led_update + 1000 < millis()) {
      unsigned long start_update = micros();
      for(uint8_t lane = 0; lane < 2; ++lane) {
      for (uint8_t i = 0; i < LANE_LEDS; ++i) {
#ifdef PATTERN_1
       if (i == led_number)
          leds[LANE_LEDS*lane + i] = (lane == 0) ? CRGB(4,0,0) : CRGB(0,4,0);
        else
          leds[LANE_LEDS*lane + i] = (lane == 0) ? CRGB(0,0,4) : CRGB(4,4,0);
#else
        if (i % 2 == led_number)
          leds[LANE_LEDS*lane + i] = (lane == 0) ? CRGB(4,0,0) : CRGB(0,4,0);
        else
          leds[LANE_LEDS*lane + i] = (lane == 0) ? CRGB(0,4,0) : CRGB(0,0,4);
#endif
      }
      }
      
      FastLED.show();
      unsigned long end_update = micros();
      last_led_update = millis();

#ifdef DEBUG_UPDATE
      Serial.print("update time LEDs [usecs]: ");
      Serial.print(end_update - start_update);
      //Serial.print(", led_number=");
      //Serial.print(led_number);
      Serial.println("");
#endif

#ifdef PATTERN_1
      led_number = (led_number + 1) % NUM_LEDS;
#else
      led_number = (led_number + 1) % 2;
#endif
    };

    resetButton.loop();

    if (resetButton.wasPressed()) {
       Serial.println("was pressed");
    switch (resetButton.read())
    {
      case single_click: {
        Serial.println("reset clicked");
      }
    }
    }

    for (uint8_t lane = 0; lane<2; ++lane) {
      if (!lane_passed[lane][0]) {
        lane_values[lane][0] = analogRead(lane_sensors[lane][0]);  
        if (lane_values[lane][0] < lane_sensor_thresh[lane][0]) {
          lane_micros[lane][0] = micros();
          lane_passed[lane][0] = true;
          iters[lane] = 0;
        }
      }
      else if (lane_passed[lane][0] && !lane_passed[lane][1]) {
        lane_values[lane][1] = analogRead(lane_sensors[lane][1]);
        if (lane_values[lane][1] < lane_sensor_thresh[lane][1]) {
          lane_micros[lane][1] = micros();
          lane_passed[lane][1] = true;
        }
        else {
          ++iters[lane];
        }
      }
      else if (lane_passed[lane][0] && lane_passed[lane][1]) {
        if (lane_micros[lane][0] > lane_micros[lane][1]) {
          Serial.println("end before start :/");  
        }
        else if (lane_micros[lane][1] - lane_micros[lane][0] < 1000)
        {
          // could be a long object
        }
        else if (micros() > lane_micros[lane][1] + 1E6) {
          Serial.print("LANE "); Serial.print(lane);
          Serial.print(": msec / 8 cm: ");
    
          unsigned long micros_diff = lane_micros[lane][1] - lane_micros[lane][0];
    
          Serial.println(0.001  * micros_diff);
          
          float diff1 = 1.f / micros_diff;
    
          Serial.print("m/s = ");
          Serial.println(TO_METER_PER_SECOND * diff1);
    
          Serial.print("km/h = ");
          Serial.println(TO_KMH * diff1);

          //lcd.clear();
          if (lane == 0) {
            lcd.setCursor(0, 0);
            for (uint8_t i = 0; i < 16; ++i) { lcd.print(" "); }
            lcd.setCursor(0, 0);
            lcd.print("< ");
          }
          else {
            lcd.setCursor(0, 1);
            for (uint8_t i = 0; i < 16; ++i) { lcd.print(" "); }
            lcd.setCursor(0, 1);
            lcd.print("> ");
          }
          lcd.print(TO_KMH * diff1);
          lcd.print(" km/h");
    
    
          Serial.print("km/h (unscaled) = ");
          Serial.println(TO_KMH_UNSCALED * diff1);
    
          Serial.print("V1: ");
          Serial.print(lane_values[lane][0]);
          Serial.print(" @ ");
          Serial.println(lane_micros[lane][0]);
          
          Serial.print("V2: ");
          Serial.print(lane_values[lane][1]);
          Serial.print(" @ ");
          Serial.println(lane_micros[lane][1]);
  
          Serial.print("iters: A: ");
          Serial.print(iters[0]);
          Serial.print(", B: ");
          Serial.println(iters[1]);
        
          Serial.println("reset\n");
          full_reset();
        }
      }
    }
#endif
}
