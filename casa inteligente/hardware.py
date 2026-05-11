
from telemetrix import telemetrix

DHT_PIN = 11
LDR_PIN = 0
TRIG_PIN = 8
ECHO_PIN = 9
PWM_PIN = 6
RELE_PIN = 7
PIR_PIN = 2
SERVO_PIN = 10

board = telemetrix.Telemetrix()

def init_hardware(dht_cb, ldr_cb, sonar_cb, pir_cb):
    board.set_pin_mode_dht(DHT_PIN, dht_type=22, callback=dht_cb)
    board.set_pin_mode_analog_input(LDR_PIN, callback=ldr_cb)
    board.set_pin_mode_sonar(TRIG_PIN, ECHO_PIN, callback=sonar_cb)
    board.set_pin_mode_digital_input(PIR_PIN, callback=pir_cb)
    board.set_pin_mode_analog_output(PWM_PIN)
    board.set_pin_mode_digital_output(RELE_PIN)
    board.set_pin_mode_servo(SERVO_PIN)

def set_fan(state):
    board.digital_write(RELE_PIN, 1 if state else 0)

def shutdown():
    board.digital_write(RELE_PIN, 0)
    board.shutdown()
