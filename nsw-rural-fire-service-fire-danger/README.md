# NSW Rural Fire Service - Fire Danger

The NSW Rural Fire Service provides an [XML feed](http://www.rfs.nsw.gov.au/feeds/fdrToban.xml) that contains the fire danger
details for today and tomorrow for districts in the state.

This custom component is implemented as a simple sensor that fetches the feed
and stores all details of the configured district. You can then use template
sensors to present these details in Home Assistant.


## Installation

### Install custom component code
In your [configuration folder](https://www.home-assistant.io/docs/configuration/)
create subfolders `<config>/custom_components/sensor` and copy the file
`nsw_rural_fire_service_fire_danger.py` into that new folder.

### Install dependencies
This custom component uses one third-party library which you may need to install
manually:

```
pip install xmltodict
```

## Configuration Example


### Fire Danger Sensor

Have a look at the XML feed at http://www.rfs.nsw.gov.au/feeds/fdrToban.xml
and find your district. The district's name must be configured as 
`district_name` as shown in the following example:

```yaml
sensor:
  - platform: nsw_rural_fire_service_fire_danger
    district_name: Greater Sydney Region
```

The above configuration will generate a sensor with entity id 
`sensor.fire_danger_in_greater_sydney_region` which is further used in the
examples below.

The sensor's state will either be `ok` or `unknown` if no data could be retrieved.

The following attributes will be available for use in `template` sensors.

| Attribute             | Description                                 |
|-----------------------|---------------------------------------------|
| district              | District name                               |
| region_number         | Internal number of this district            |
| councils              | List of all councils in this district       |
| danger_level_today    | Today's danger level                        |
| danger_level_tomorrow | Tomorrow's danger level                     |
| fire_ban_today        | Indicates whether there is a fire ban today |
| fire_ban_tomorrow     | Indicates whether there is a fire ban today |

To hide this sensor you can add the following to your configuration:

```yaml
homeassistant:
  customize:
    sensor.fire_danger_in_greater_sydney_region:
      hidden: true
```

### Danger Level Today

```yaml
sensor:
  - platform: template
    sensors:
      fire_danger_level_today:
        friendly_name: "Danger Level Today"
        value_template: "{{ state_attr('sensor.fire_danger_in_greater_sydney_region', 'danger_level_today') }}"
        icon_template: mdi:speedometer
```

### Fire Ban Today
```yaml
binary_sensor:
  - platform: template
    sensors:
      fire_ban_today:
        friendly_name: "Fire Ban Today"
        value_template: "{{ state_attr('sensor.fire_danger_in_greater_sydney_region', 'fire_ban_today') }}"
        device_class: safety
```
