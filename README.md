# Telemetrix-Python-Flet-1.0 

This repository contains a collection of Python scripts and prototypes designed to control and monitor Arduino boards in real time. The project
combines the low-latency communication power of the Telemetrix library with modern graphical user interfaces developed in Flet (built on
Flutter). 

The ecosystem was designed primarily for educational and experimental purposes, integrating concepts of home automation, IoT (Internet of
Things), data acquisition, and industrial automation. 

## 🚀 Key Features 

- Interactive Graphical Interfaces: Built with Flet to create fluid, responsive, and visual control panels (GUIs).
- Real-Time Sensor Control: Reading and processing data from sensors such as LDR (light), DHT22 (temperature/humidity), and HC-SR04
(sonar/ultrasound).
- Actuator Manipulation: Ready-to-use code for controlling servomotors, relays, PWM outputs, and LED triggering (including traffic light
logic).
- Storage and Graphing: Automatic exporting of sensor data to .csv files and dynamic rendering of graphs for historical data analysis.
- Home Automation Modules: Includes a dedicated prototype for simulating and controlling a “Smart Home”. 

## 🛠️ Prerequisites

Before running the scripts, make sure you have properly configured your environment:

1. **On the Arduino:**
   - Upload the corresponding Telemetrix firmware to your board using the Arduino IDE. 
   - Typically, the `Telemetrix4Arduino` sketch is used (available in the official Telemetrix documentation).
  
2. **Telemetrix**

The **Telemetrix Project** is a modern-day replacement for Arduino StandardFirmata, equipped with many more built-in features than StandardFirmata. The project consists of Python APIs used to create Python client applications and C++ servers that communicate with the Python client over a serial or Wi-Fi link.

Installing Telemetrix

To install Telemetrix on Linux (including Raspberry Pi) and macOS:

```bash
sudo pip3 install telemetrix
```

For Windows users:

```bash
pip install telemetrix
```

To communicate Python with Arduino, you must upload a program to the Arduino following the instructions at:  
[Telemetrix Instructions for Arduino](https://mryslab.github.io/telemetrix/telemetrix4arduino/)

3. **On the Computer (VSCodium Setup):**
   - Open **VSCodium** and open the project folder (`File` > `Open Folder...`).
   - Open the integrated terminal (`Ctrl + Shift + \`` or `View` > `Terminal`).
   - Create a virtual environment to isolate the project dependencies:
     ```bash
     python -m venv venv
     ```
   - Activate the virtual environment:
     - **Windows (PowerShell):** `.\venv\Scripts\Activate.ps1`
     - **Linux / macOS:** `source venv/bin/activate`
   - *Tip:* When prompted by VSCodium to select the interpreter for the workspace, choose the one inside the `venv` folder.

4. **Install Dependencies:**
   - With the virtual environment activated in your terminal, install the required packages:
     ```bash
     pip install telemetrix flet pandas matplotlib
     ``` 

## 💻 How to Run 

Connect your Arduino board to your computer via a USB port.

Identify or allow Telemetrix to automatically detect the correct COM/serial port.

Run any of the available GUI scripts. Example: bash python telemetrix_flet_dht22.py 

## 🎓 Institutional Context 

This project is to test and to run several sensors in arduino platform and show it to students
