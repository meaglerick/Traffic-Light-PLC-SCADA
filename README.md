# Traffic-Light-PLC-SCADA

dev 1

This project was developed to simulate an industrial control system (ICS) traffic light Supervisory Control And Data Acquisition (SCADA) system. It utilizes trafficPLC.py to act as a programmable logic controller (PLC). For use, the machine operating the PLC should have 4 network interfaces, on the 10.0.0.10, 10.0.0.20, 10.0.0.30, and 10.0.0.40 addresses. If this is not suitable comment out the section at the bottom that initializes the PLC's.

TrafficScada.py is the SCADA portion of the environment. This will interrogate up to 4 PLC's using the ModBus ICS protocol, utilizing the PyModBus package for python.

Future work: the HMI is designed to connect to the SCADA over an HTML websocket. This does not accurately imitate true Human Machine Interfaces. This could be changed to actually send ModBus from the browser to the SCADA to interrogate for data.


## Getting started

1. create a virtual environment

Windows - 

    `python -m venv .venv`

as2. Install the requirements

test - 


    `pip install -r requirements.txt`

    pip install -U pymodbus[tornado]
    pip install twisted
    pip install cryptography
    pip install autobahn
    pip install numpy