curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | BINDIR=~/local/bin sh

~/local/bin/arduino-cli config init
~/local/bin/arduino-cli core update-index
~/local/bin/arduino-cli core install arduino:avr
~/local/bin/arduino-cli lib install Button2
~/local/bin/arduino-cli lib install FastLED
~/local/bin/arduino-cli lib install "LiquidCrystal I2C"
~/local/bin/arduino-cli compile -b arduino:avr:nano:cpu=atmega328old tinyrace
~/local/bin/arduino-cli upload -v -p /dev/ttyUSB0 -b arduino:avr:nano:cpu=atmega328old tinyrace


