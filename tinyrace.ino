#include "Button2.h"
#include "FastLED.h"
#include "LiquidCrystal_I2C.h"

#define NUM_LEDS 16
#define LANE_LEDS 8

CRGB leds[NUM_LEDS];

// PINS
const int lane_sensors[2][2] = {{A0, A1}, {A2, A3}};
const int lane_sensor_thresh[2][2] = {{10, 10}, {10, 10}};
constexpr int neopixels_data_pin = 4;
constexpr int button_left_pin = 11;
constexpr int button_right_pin = 12;
constexpr int button_up_pin = 8;
constexpr int button_down_pin = 10;
constexpr unsigned long race_timeout_usecs = 5E6;

unsigned long lane_micros[2][2];
bool lane_passed[2][2];
int lane_values[2][2];
unsigned int iters[2];
unsigned long last_led_update;
uint8_t led_number;
bool display_speeds[2];

LiquidCrystal_I2C lcd(0x27, 16, 2);

constexpr float TO_METER_PER_SECOND = 0.08 * 1E6;
constexpr float TO_KMH = 0.08 * 1E6 * 3.6;
constexpr float TO_KMH_UNSCALED = 0.08 * 1E6 * 3.6 * 64;

Button2 button_left;
Button2 button_right;
Button2 button_up;
Button2 button_down;

//#define DEBUG_RACE
//#define DEBUG_UPDATE
#define BLINK_LEDS
#define DEBUG_PRINTS

void full_reset() {
  for (uint8_t lane = 0; lane < 2; ++lane) {
    for (uint8_t pos = 0; pos < 2; ++pos) {
      lane_micros[lane][pos] = 0;
      lane_values[lane][pos] = 0;
      lane_passed[lane][pos] = false;
    }
    iters[lane] = 0;
    display_speeds[lane] = false;
  }
  last_led_update = 0;
  led_number = 0;

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("JANNIS");
  lcd.setCursor(0, 1);
  lcd.print("Hotwheels Rennen");
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
#endif

  full_reset();

  button_left.begin(button_left_pin, INPUT, false);
  button_right.begin(button_right_pin, INPUT, false);
  button_up.begin(button_up_pin, INPUT, false);
  button_down.begin(button_down_pin, INPUT, false);

  Serial.begin(9600);
  while (!Serial) {
    ;
  }

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

  // Serial.println(resetButton.clickToString(resetButton.wait()));

  delay(50);
}

void loop() {
#ifdef DEBUG_RACE
  debug_race();
#else

  if ((lane_passed[0][1] &&
       micros() > race_timeout_usecs + lane_micros[0][1]) ||
      (lane_passed[1][1] &&
       micros() > race_timeout_usecs + lane_micros[1][1])) {
    full_reset();
    Serial.println("Reset");

    Serial.println(lane_passed[0][0]);
  }

#ifdef BLINK_LEDS

  if (last_led_update + 1000 < millis()) {
    unsigned long start_update = micros();

    if (lane_micros[0][1] > 0 && lane_micros[1][1] > 0) {
      Serial.println("red/green leds");
      CRGB lane_a_color, lane_b_color;
      if (lane_micros[0][1] > lane_micros[1][1]) {
        lane_a_color = CRGB(0, 128, 0);
        lane_b_color = CRGB(128, 0, 0);
      } else {
        lane_a_color = CRGB(128, 0, 0);
        lane_b_color = CRGB(0, 128, 0);
      }
      for (uint8_t lane = 0; lane < 2; ++lane) {
        for (uint8_t i = 0; i < LANE_LEDS; ++i) {
          leds[LANE_LEDS * lane + i] =
              (lane == 0) ? lane_a_color : lane_b_color;
        }
      }
    } else {
      Serial.println("blinky leds");
      for (uint8_t lane = 0; lane < 2; ++lane) {
        for (uint8_t i = 0; i < LANE_LEDS; ++i) {
#ifdef PATTERN_1
          if (i == led_number)
            leds[LANE_LEDS * lane + i] =
                (lane == 0) ? CRGB(4, 0, 0) : CRGB(0, 4, 0);
          else
            leds[LANE_LEDS * lane + i] =
                (lane == 0) ? CRGB(0, 0, 4) : CRGB(4, 4, 0);
#else
          if (i % 2 == led_number)
            leds[LANE_LEDS * lane + i] =
                (lane == 0) ? CRGB(4, 0, 0) : CRGB(0, 4, 0);
          else
            leds[LANE_LEDS * lane + i] =
                (lane == 0) ? CRGB(0, 4, 0) : CRGB(0, 0, 4);
#endif
        }
      }
    }

    FastLED.show();
    unsigned long end_update = micros();
    last_led_update = millis();

#ifdef DEBUG_UPDATE
    Serial.print("update time LEDs [usecs]: ");
    Serial.print(end_update - start_update);
    // Serial.print(", led_number=");
    // Serial.print(led_number);
    Serial.println("");
#endif

#ifdef PATTERN_1
    led_number = (led_number + 1) % NUM_LEDS;
#else
    led_number = (led_number + 1) % 2;
#endif
  }
#endif

#if 1
  button_left.loop();
  button_right.loop();
  button_up.loop();
  button_down.loop();
  if (button_left.wasPressed()) {
    switch (button_left.read()) {
    case single_click:
      Serial.println("left single");
      break;
    case long_click:
      Serial.println("left long");
    }
  }
  if (button_right.wasPressed()) {
    switch (button_right.read()) {
    case single_click:
      Serial.println("right single");
      break;
    case long_click:
      Serial.println("right long");
    }
  }
  if (button_up.wasPressed()) {
    switch (button_up.read()) {
    case single_click:
      Serial.println("up single");
      break;
    case long_click:
      Serial.println("up long");
    }
  }
  if (button_down.wasPressed()) {
    switch (button_down.read()) {
    case single_click:
      Serial.println("down single");
      break;
    case long_click:
      Serial.println("down long");
    }
  }
#endif

  for (uint8_t lane = 0; lane < 2; ++lane) {
    if (!lane_passed[lane][0]) {
      lane_values[lane][0] = analogRead(lane_sensors[lane][0]);
      if (lane_values[lane][0] < lane_sensor_thresh[lane][0]) {
        lane_micros[lane][0] = micros();
        lane_passed[lane][0] = true;
        iters[lane] = 0;
      }
    } else if (lane_passed[lane][0] && !lane_passed[lane][1]) {
      lane_values[lane][1] = analogRead(lane_sensors[lane][1]);
      if (lane_values[lane][1] < lane_sensor_thresh[lane][1]) {
        lane_micros[lane][1] = micros();
        lane_passed[lane][1] = true;
      } else {
        ++iters[lane];
      }
    } else if (lane_passed[lane][0] && lane_passed[lane][1]) {
      if (lane_micros[lane][0] > lane_micros[lane][1]) {
        Serial.println("end before start :/");
      } else if (lane_micros[lane][1] - lane_micros[lane][0] < 1000) {
        // could be a long object
      } else if (!display_speeds[lane] &&
                 micros() > lane_micros[lane][1] + 1E6) {
        unsigned long micros_diff = lane_micros[lane][1] - lane_micros[lane][0];

        float diff1 = 1.f / micros_diff;

        display_speeds[lane] = true;

        // lcd.clear();
        if (lane == 0) {
          lcd.setCursor(0, 0);
          for (uint8_t i = 0; i < 16; ++i) {
            lcd.print(" ");
          }
          lcd.setCursor(0, 0);
          lcd.print("< ");
        } else {
          lcd.setCursor(0, 1);
          for (uint8_t i = 0; i < 16; ++i) {
            lcd.print(" ");
          }
          lcd.setCursor(0, 1);
          lcd.print("> ");
        }
        lcd.print(TO_KMH * diff1);
        lcd.print(" km/h");

#ifdef DEBUG_PRINTS
        Serial.print("LANE ");
        Serial.print(lane);
        Serial.print(": msec / 8 cm: ");

        Serial.println(0.001 * micros_diff);

        Serial.print("m/s = ");
        Serial.println(TO_METER_PER_SECOND * diff1);

        Serial.print("km/h = ");
        Serial.println(TO_KMH * diff1);

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
#endif

        // full_reset();
      }
    }
  }
#endif
}
