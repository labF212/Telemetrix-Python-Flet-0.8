
import time

temperature = 0.0
humidity = 0.0
ldr_value = 0
distance_cm = 0

fan_state = {"manual": False}
fan_auto_until = 0.0
FAN_AUTO_TIME = 5.0

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

def fan_auto_active(now):
    return now < fan_auto_until

def fan_should_run(now):
    return fan_state["manual"] or fan_auto_active(now)
