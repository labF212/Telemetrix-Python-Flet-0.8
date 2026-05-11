import time
import asyncio
import threading
import hardware

# ================= VENTOINHA =================
fan_state = {"manual": False}

def fan_on():
    fan_state["manual"] = True

def fan_off():
    fan_state["manual"] = False

def update_fan():
    now = time.time()
    auto_active = now < hardware.fan_auto_until

    if fan_state["manual"] or auto_active:
        hardware.board.digital_write(hardware.RELE_PIN, 1)
        return True, auto_active
    else:
        hardware.board.digital_write(hardware.RELE_PIN, 0)
        return False, False

# ================= SERVO =================
servo_flag = {"run": False}

def servo_write(angle: int):
    hardware.board.servo_write(hardware.SERVO_PIN, angle)

def servo_auto(update_ui):
    while servo_flag["run"]:
        for ang in range(0, 181, 5):
            if not servo_flag["run"]:
                return
            servo_write(ang)
            update_ui(ang)
            time.sleep(0.1)
        for ang in range(180, -1, -5):
            if not servo_flag["run"]:
                return
            servo_write(ang)
            update_ui(ang)
            time.sleep(0.1)

def start_servo_auto(update_ui):
    servo_flag["run"] = True
    threading.Thread(
        target=servo_auto,
        args=(update_ui,),
        daemon=True
    ).start()

def stop_servo_auto():
    servo_flag["run"] = False

# ================= PWM =================
pwm_state = {"mode": "manual", "task": None}

async def pwm_auto():
    while pwm_state["mode"] == "auto":
        for i in range(256):
            if pwm_state["mode"] != "auto": 
                return
            hardware.board.analog_write(hardware.PWM_PIN, i)
            await asyncio.sleep(0.03)
        for i in range(255, -1, -1):
            if pwm_state["mode"] != "auto": 
                return
            hardware.board.analog_write(hardware.PWM_PIN, i)
            await asyncio.sleep(0.03)

def pwm_manual(value):
    hardware.board.analog_write(hardware.PWM_PIN, int(value * 2.55))
import time
import asyncio
import threading
import hardware

# ================= VENTOINHA =================
fan_state = {"manual": False}

def fan_on():
    fan_state["manual"] = True

def fan_off():
    fan_state["manual"] = False

def update_fan():
    now = time.time()
    auto_active = now < hardware.fan_auto_until

    if fan_state["manual"] or auto_active:
        hardware.board.digital_write(hardware.RELE_PIN, 1)
        return True, auto_active
    else:
        hardware.board.digital_write(hardware.RELE_PIN, 0)
        return False, False

# ================= SERVO =================
servo_flag = {"run": False}

def servo_write(angle: int):
    hardware.board.servo_write(hardware.SERVO_PIN, angle)

def servo_auto(update_ui):
    while servo_flag["run"]:
        for ang in range(0, 181, 5):
            if not servo_flag["run"]:
                return
            servo_write(ang)
            update_ui(ang)
            time.sleep(0.1)
        for ang in range(180, -1, -5):
            if not servo_flag["run"]:
                return
            servo_write(ang)
            update_ui(ang)
            time.sleep(0.1)

def start_servo_auto(update_ui):
    servo_flag["run"] = True
    threading.Thread(
        target=servo_auto,
        args=(update_ui,),
        daemon=True
    ).start()

def stop_servo_auto():
    servo_flag["run"] = False

# ================= PWM =================
pwm_state = {"mode": "manual", "task": None}

async def pwm_auto():
    while pwm_state["mode"] == "auto":
        for i in range(256):
            if pwm_state["mode"] != "auto": 
                return
            hardware.board.analog_write(hardware.PWM_PIN, i)
            await asyncio.sleep(0.03)
        for i in range(255, -1, -1):
            if pwm_state["mode"] != "auto": 
                return
            hardware.board.analog_write(hardware.PWM_PIN, i)
            await asyncio.sleep(0.03)

def pwm_manual(value):
    hardware.board.analog_write(hardware.PWM_PIN, int(value * 2.55))

"""
async def on_exit(e):
        board.servo_write(SERVO_PIN, 90)
        await asyncio.sleep(0.3)
        board.digital_write(RELE_PIN, 0)
        board.shutdown()
        await page.window.destroy()
"""