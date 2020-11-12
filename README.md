# ad-savitr
An AppDaemon application for Home Assistant to control Savitr electric heater through additional WiFi module

## Disclaimer
This is my very first Python script. Sorry for:
- code quality;
- overcommenting (I write comments before I write code);
- stupid function and variable names etc.
If you can (and want to) refactor it - please, open an issue or send me a pull request! Thank you!

I write everything in clumsy English because I need practice (hello, mother Russia!).

## Working heaters
Tested with:
- [Savitr Ultra Plus](http://www.savitr.ru/catalog/productid_63)

## Module
This small app is communicating with a [Savitr WiFi module](http://www.savitr.ru/catalog/productid_92 ) (sold separately), which controls the heater at CAN bus.

The WiFi module consists of:
- main MCU - STM32F072T8
- auxiliary MCU - ESP8266MOD (for WiFi connection)
- CAN-transceiver - **TODO: check**

It has:
- a RJ-45 connector for CAN-bus (probably CAN V2.0B) which is used to connect the heater;
- a USB connector (probably to flash firmware).
I didn't dump the firmware (neither from STM nor ESP), it's a black box for me.

It also has an official Android app [Savitr WIFI](https://play.google.com/store/apps/details?id=com.ez.savitr_wifi&hl=en_US).

## Module interfaces pinout

**TODO**

## How I reversed the protocol
1. Connect to module's AP (ssid is "SAVITR_WIFI") and obtain an IP-address from it's DHCP server.
2. Get the module's IP with `nmap`.
```
$ nmap -sP 192.168.0.1-255
```
3. Check open ports with `nmap`. Understand that port `8558/tcp` is open.
```
$ nmap -p 1-10000 192.168.0.1
```
4. Connect with netcat and understand that WiFi module sends every 1 second a TCP/IP message of 192 bytes.
```
$ nc 192.168.0.1 8558
```
5. Understand protocol by writing messages to files and `vbindiff` :)
6. Download the official Android app "Savitr WIFI" from your phone with `adb`, open it with [Bytecode Viewer](https://github.com/Konloch/bytecode-viewer) and understand the protocol much better!
7. ...
8. Get to know (suddenly) the protocol developer and ask him some questions -_-.

## Supported functions
- [ ] Set WiFi SSID and password - You can use the official app for that (**TODO: implement and test**)
- [ ] Set mail for alarms - You definitely don't need this feature (**TODO: implement and test**)
- [ ] Reset module to defaults - (**TODO: implement and test**)
- [X] Set heating mode
- [X] Set heating power
- [X] Set air indoor temp limits (for mail alarms.. don`t think you need this)
- [X] Set coolant temp limits (for mail alarms.. don`t think you need this)
- [X] Set air indoor temp setpoint
- [X] Set coolant temp setpoint
- [X] Set air indoor temp control

## Installation
1. Install AppDaemon for Home Assistant. [Instructions](https://appdaemon.readthedocs.io/en/latest/INSTALL.html). The simplest way is to use The official hass.io addon for AppDaemon by frenck.

2. Clone this repository to `config/appdaemon/apps` directory.

3. Copy package file `packages/ad-savitr-package.yaml` to your `config/packages` directory. Rename it, if you want.

4. Edit package file as you like. For example, give friendly names to sensors, etc. Do not change names of entities!

5. Enable this package in your `config/configuration.yaml` and restart Home Assistant:
```
packages:
  savitr: !include ad-savitr-package.yaml
```
You should see new entities after restart.

6. Enable this app in your config/appdaemon/apps/apps.yaml:
```
# Savitr electric heater app
savitr:
  module: ad-savitr
  class: SavitrHeater
  device_name: savitr  # Device name is prefix in entities, eg. sensor.savitr_something
  host: 192.168.3.72  # IP-address or Hostname.
  port: 8558  # TCP port number. Default is 8558.
  timeout: 10  # Timeout to wait in seconds.
  update_interval: 10  # Update interval, in seconds. Must be at least 5.
  log_level: INFO  # Log level can be INFO or DEBUG.
```

7. Create and adjust cards at Home Assistant frontend.

8. Have fun!

## TODO
- implement wifi and mail
- what if I have 2 or more heaters? 2 apps, 2 packages, savitr_1 in entity_id etc.
- somebody please refactor this!!!

## Credits
Eugeniy Zemtsov - the WiFi module developer.
