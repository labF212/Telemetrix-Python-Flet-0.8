# hardware.py
import time
from telemetrix import telemetrix

# ================= PINOS =================
DHT_PIN = 11
LDR_PIN = 0
TRIG_PIN = 8
ECHO_PIN = 9
PWM_PIN = 6
RELE_PIN = 7
PIR_PIN = 2
SERVO_PIN = 10

# ================= BOARD =================
board = telemetrix.Telemetrix()

# ================= ESTADO DOS SENSORES =================
temperature = 0.0
humidity = 0.0
ldr_value = 0
distance_cm = 0

fan_auto_until = 0.0
FAN_AUTO_TIME = 5.0

# ================= CALLBACKS =================
def dht_callback(data):
    global temperature, humidity
    if data[1] == 0:
        humidity = data[4]
        temperature = data[5]

def ldr_callback(data):
    global ldr_value
    ldr_value = data[2]

def sonar_callback(data):
    global distance_cm
    distance_cm = data[2]

def pir_callback(data):
    global fan_auto_until
    if data[2] == 1:
        fan_auto_until = time.time() + FAN_AUTO_TIME

# ================= INIT =================
def init():
    board.set_pin_mode_dht(DHT_PIN, dht_type=22, callback=dht_callback)
    board.set_pin_mode_analog_input(LDR_PIN, callback=ldr_callback)
    board.set_pin_mode_sonar(TRIG_PIN, ECHO_PIN, callback=sonar_callback)
    board.set_pin_mode_digital_input(PIR_PIN, callback=pir_callback)

    board.set_pin_mode_analog_output(PWM_PIN)
    board.set_pin_mode_digital_output(RELE_PIN)
    board.set_pin_mode_servo(SERVO_PIN)
