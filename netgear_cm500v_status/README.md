# Netgear CM500V Cable Modem Internet Connection Status

This custom component implements a simple binary sensor that scrapes the
Internet connection status from the Netgear CM500V Cable Modem's dashboard.

## Prerequisites

### Minimum Home Assistant version
The current code and file structure works with Home Assistant version 0.91 or 
later.

### Tested Modem
This custom component has been tested with a Netgear CM500V Cable Modem.

* Hardware Version: V02
* Firmware Version: V1.01.08

## Installation

### Install custom component code
In your [configuration folder](https://www.home-assistant.io/docs/configuration/)
create subfolder `<config>/custom_components` and copy the folder
`netgear_cm500v` into the new `custom_components` folder.

## Configuration Example


### Internet Connection Status Binary Sensor

The Netgear CM500V Cable Modem is typically connected to some sort of Wifi
router in your internal network. 

The default IP address of the modem is `192.168.100.1`, and you can access 
the dashboard via `http://192.168.100.1/`. If your modem is available under
a different IP address, please use config parameter `ip_address` to provide
the correct one.

This component assumes that a password is set on the modem and which must be 
provided as a required config parameter.

```yaml
binary_sensor:
  - platform: netgear_cm500v
    password: !secret netgear_cm500v_password
```

The above configuration will generate a sensor with entity id 
`binary_sensor.internet_connection_status`. Its state will be `Connected` or
`Disconnected`, and it will have a few device attributes:

| Attribute        | Description                                                                |
|------------------|----------------------------------------------------------------------------|
| device           | "Netgear CM500V"                                                           |
| ip_address       | Internal IP address (default: 192.168.100.1)                               |
| internet_comment | Descriptive state of the Internet connection, e.g. "In Progress" or "Good" |
