# Telemetrix-Python-Flet-1.0 

This repository contains a collection of Python scripts and prototypes designed to control and monitor Arduino boards in real time. The project
combines the low-latency communication power of the Telemetrix library with modern graphical user interfaces developed in Flet (built on
Flutter). 
The ecosystem was designed primarily for educational and experimental purposes, integrating concepts of home automation, IoT (Internet of
Things), data acquisition, and industrial automation. 

## 🚀 Key Features 

Interactive Graphical Interfaces: Built with Flet to create fluid, responsive, and visual control panels (GUIs).
Real-Time Sensor Control: Reading and processing data from sensors such as LDR (light), DHT22 (temperature/humidity), and HC-SR04
(sonar/ultrasound).

Actuator Manipulation: Ready-to-use code for controlling servomotors, relays, PWM outputs, and LED triggering (including traffic light
logic).

Storage and Graphing: Automatic exporting of sensor data to .csv files and dynamic rendering of graphs for historical data analysis.
Home Automation Modules: Includes a dedicated prototype for simulating and controlling a “Smart Home”. 

## 📂 Relevant File Structure 
casa inteligente/ / casa_inteligente.py: Scripts focused on simulating automated residential systems.
telemetrix_flet_scr04_...: Scripts dedicated to reading the ultrasonic sensor (HC-SR04 Sonar), logging data into multiple files, and
generating distance graphs.
telemetrix_flet_dht22.py: Interface for environmental temperature and humidity monitoring.
telemetrix_flet_A0_barra_horizontal_ldr.py: Analog reading of a light sensor with instantaneous visual feedback.
telemetrix_flet_sermovotor.py: Manual or automatic angular position control of a servomotor.
flet_read_csv6files_graphic.py: Utility to read historical data stored in CSV format and plot metrics for analysis. 
## 🛠️ Prerequisites 
Before running the scripts, ensure you have properly configured your environment: 
On the Arduino: 
Upload the corresponding Telemetrix firmware to your board using the Arduino IDE. Typically, the Telemetrix4Arduino sketch is
used (available in the official Telemetrix documentation).
On the Computer (Python): 
Install the required dependencies using your terminal: bash pip install telemetrix flet pandas matplotlib 
## 💻 How to Run 
Connect your Arduino board to your computer via a USB port.
Identify or allow Telemetrix to automatically detect the correct COM/serial port.
Run any of the available GUI scripts. Example: bash python telemetrix_flet_dht22.py 
## 🎓 Institutional Context 
This project is to test and to run several sensors in arduino platform and show it to students
