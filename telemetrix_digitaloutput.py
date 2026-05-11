import time
from telemetrix import telemetrix

board = telemetrix.Telemetrix()
PIN_RELE = 7

board.set_pin_mode_digital_output(PIN_RELE)

print("Liga (LOW)")
board.digital_write(PIN_RELE, 0)  # deve ligar
time.sleep(3)

print("Desliga (HIGH)")
board.digital_write(PIN_RELE, 1)  # deve desligar
time.sleep(3)

board.shutdown()
