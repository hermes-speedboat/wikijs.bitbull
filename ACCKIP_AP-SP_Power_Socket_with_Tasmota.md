---
title: ACCKIP AP-SP Power Socket with Tasmota
description: Notes on hacking the ACCKIP AP-SPI WiFi power socket to run Tasmota firmware
published: true
date: 2026-01-07T00:00:00.000Z
tags: hacking, iot
editor: markdown
dateCreated: 2026-01-07T00:00:00.000Z
---

# General
This is a short note about my ACCKIP AP-SPI WiFi powersocket hack to get it running with Tasmota.

# Buy
This is one of the WiFi power sockets that you can buy with swiss connectors.  
Price is about 12 USD, which is quite cheap.

- [https://de.aliexpress.com/item/4000316587977.html](https://de.aliexpress.com/item/4000316587977.html)

![ap-sp.png|300px](ap-sp.png)

# Flashing
I tried out the Tasmota Firmware which is doing an amazing job once it is running.

- [https://tasmota.github.io/docs/](https://tasmota.github.io/docs/) (Tasmota Homepage)

Tasmotizer is an all-in-one flasher which can flash esp-8266 based IoT devices out of the box

- [https://github.com/tasmota/tasmotizer](https://github.com/tasmota/tasmotizer) (Tasmotizer Homepage)

![Tasmotizer.png|400px](Tasmotizer.png)

Of course you need some basic soldering skills and a few dupont lines to get it running.  
For flashing, I used the tool I have for flashing ESP-01 modules, it worked as expected.  
Of course you can use any FTDI if it supports 3.3V logic level.

- [https://de.aliexpress.com/item/32971337222.html](https://de.aliexpress.com/item/32971337222.html) CH340 USB to ESP8266 Serial ESP-01 ESP-01S ESP01 ESP01S Wireless Wifi Development Board Module for Arduino Programmer Adapter

![esp01-flasher.jpg|400px](esp01-flasher.jpg)

# Soldering
To get the firmware into the ESP, just solder one end of the dupont lines into the esp temporarily. Once firmware is flashed, you can update it over the air later on.  
If you open the power socket, you can find the TWE2S chipset from Tuya which is mainly an ESP8266EX.

- [https://docs.tuya.com/en/iot/device-development/module/wifi-module/wifie2smodule?id=K9605u79tgxug](https://docs.tuya.com/en/iot/device-development/module/wifi-module/wifie2smodule?id=K9605u79tgxug) (TWE2S Homepage)

---

![twe2s-pinout.jpeg|500px](twe2s-pinout.jpeg)

---

![twe2s-socket.png|500px](twe2s-socket.png)

---

![esp-01-ftdi.jpeg|800px](esp-01-ftdi.jpeg)

---

# Configuration
Once you successfully flashed the powersocket before dying by an electric shock, you will see the Tasmota firmware boot an access point.  
Then you can log into the web interface at IP 192.168.4.1 as described on the Tasmota homepage.  
After you enter the credentials of your WiFi connection, you can log into the Tasmota web interface and configure the firmware so that it is working with all the features.  
For that go to: CONFIGURATION > CONFIGURE TEMPLATE and configure as shown below:

![tasmotas-ap-sp.png|300px](tasmotas-ap-sp.png)

It is important to configure the IOs exactly as given, but once done, you have a fully open source software based powersocket with all the features of Tasmota supported by your hardware.

![tasmotas-ap-sp-ui.png](tasmotas-ap-sp-ui.png)

- Wifi UI for controlling the powersocket
- URL Power Switch Triggers
- PowerConsumption counter
- Scheduled powerswitch
- MQTT client
- Syslog client
- Domoticz Support
- many more ....
