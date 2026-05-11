import flet as ft
import asyncio
from telemetrix import telemetrix

# ---------------- HARDWARE ----------------
PIN_PWM = 6

board = telemetrix.Telemetrix()
board.set_pin_mode_analog_output(PIN_PWM)

def pwm_write(value: int):
    board.analog_write(PIN_PWM, value)

# ---------------- APP ----------------
async def main(page: ft.Page):
    page.title = "PWM LED (Manual / Automático)"
    page.theme_mode = ft.ThemeMode.DARK
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # ---------------- ESTADO ----------------
    state = {
        "pwm": 0,
        "mode": "manual",
        "running": True,
        "auto_task": None,
    }

    # ---------------- UI ----------------
    pwm_text = ft.Text("0 PWM", size=16)

    slider = ft.Slider(
        min=0,
        max=100,
        value=0,
        divisions=100,
    )

    mode = ft.RadioGroup(
        content=ft.Row([
            ft.Radio(value="manual", label="Manual"),
            ft.Radio(value="auto", label="Automático"),
        ]),
        value="manual",
    )

    # ---------------- UI LOOP ----------------
    async def ui_loop():
        while state["running"]:
            pwm_text.value = f"{state['pwm']} PWM"
            page.update()
            await asyncio.sleep(0.1)

    # ---------------- AUTOMÁTICO ----------------
    async def automatic_loop():
        try:
            while state["mode"] == "auto":
                for i in range(256):
                    if state["mode"] != "auto":
                        return
                    state["pwm"] = i
                    pwm_write(i)
                    await asyncio.sleep(0.2)

                for i in range(255, -1, -1):
                    if state["mode"] != "auto":
                        return
                    state["pwm"] = i
                    pwm_write(i)
                    await asyncio.sleep(0.2)
        except asyncio.CancelledError:
            pass

    # ---------------- EVENTOS ----------------
    async def on_slider(e):
        if state["mode"] == "manual":
            value = int(slider.value * 2.55)
            state["pwm"] = value
            pwm_write(value)

    slider.on_change = on_slider

    async def on_mode_change(e):
        if state["auto_task"]:
            state["auto_task"].cancel()
            state["auto_task"] = None

        if mode.value == "manual":
            state["mode"] = "manual"
            slider.visible = True
            state["pwm"] = 0
            pwm_write(0)
        else:
            state["mode"] = "auto"
            slider.visible = False
            state["auto_task"] = asyncio.create_task(automatic_loop())

        page.update()

    mode.on_change = on_mode_change

    async def on_exit(e):
        state["running"] = False

        if state["auto_task"]:
            state["auto_task"].cancel()

        pwm_write(0)
        board.shutdown()
        await page.window.destroy()

    # ---------------- LAYOUT ----------------
    page.add(
        ft.Column(
            [
                ft.Text("LED PWM – Pin 6"),
                ft.Row([slider, pwm_text]),
                mode,
                ft.Button("Sair", icon=ft.Icons.EXIT_TO_APP, on_click=on_exit),
            ],
            spacing=25,
        )
    )

    page.on_window_close = on_exit

    # iniciar UI loop
    asyncio.create_task(ui_loop())


# ---------------- RUN ----------------
if __name__ == "__main__":
    ft.run(main)