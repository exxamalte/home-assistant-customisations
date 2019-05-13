# Pool Pump Manager

This custom component for Home Assistant can be used to automatically control
a pool pump that is turned on/off by a switch that Home Assistant can control.

## Minimum requirements

* This has been tested with Home Assistant 0.92.2.
* A switch supported in Home Assistant that can turn on/off power to your
  pool pump.

## Features

* Can control any switch that supports being turned on/off.
* Support for distinguishing three different switch modes:
** Auto: Turn switch on/off automatically based on rules and configuration.
** On: Turn switch on.
** Off: Turn switch off.
* Support for distinguishing between swimming season and off season.
* Separate target durations in hours configurable for each season type.
* Splits the target duration into two equal runs with a break in between.
* Automatically adjusts the runs to sunrise and sunset.
* Initialises an entity (`pool_pump.schedule`) that shows the current or next
  run of the pool pump.
* Support for a water level sensor to specify an entity that indicates if the
  pool has reached a critical water level in which case the pool pump should
  not run at all.

## Caveats

* Will limit the requested duration to the total amount of daylight 
  (sunrise to sunset) available that day.
* Does not currently consider solar electricity production.

## Configuration

In the following examples we are assuming that you have a switch that is
connected to your pool pump and can turn that on/off already. That switch
is already integrated into Home Assistant with entity id `switch.pool_pump`.

### Tri-state switch

The following configuration wraps the switch into a tri-state switch which
supports 3 modes - Auto, On, Off.
The automations are required to translate each state into an action on the
actual switch connected to the pool pump.

The last two automations are the ones that actually checks the pool pump state.
The first is triggered at regular intervals (5 minutes) from shortly before 
sunrise to shortly after sunset. And the second automation is triggered by 
certain events - the start of Home Assistant, immediately when you put the pool
pump into 'Auto' mode, and whenever several key levers and sensors change.

```yaml
input_select:
  pool_pump:
    name: Pool Pump mode
    options:
      - 'Auto'
      - 'On'
      - 'Off'
    initial: 'Auto'
    icon: mdi:water-pump
    
automation:
  - alias: 'Pool Pump On'
    trigger:
      - platform: state
        entity_id: input_select.pool_pump
        to: 'On'
    action:
      service: homeassistant.turn_on
      entity_id: switch.pool_pump
  - alias: 'Pool Pump Off'
    trigger:
      - platform: state
        entity_id: input_select.pool_pump
        to: 'Off'
    action:
      service: homeassistant.turn_off
      entity_id: switch.pool_pump
  - alias: 'Check Pool Pump Periodically'
    trigger:
      - platform: time_pattern
        minutes: '/5'
        seconds: 00
    condition:
      condition: and
      conditions:
        - condition: sun
          after: sunrise
          after_offset: '-1:00:00'
        - condition: sun
          before: sunset
          before_offset: '1:30:00'
    action:
      service: pool_pump.check
  - alias: 'Check Pool Pump on Event'
    trigger:
      - platform: homeassistant
        event: start
      - platform: state
        entity_id: input_select.pool_pump
        to: 'Auto'
      - platform: state
        entity_id:
          - input_boolean.swimming_season
          - input_number.run_pool_pump_hours_swimming_season
          - input_number.run_pool_pump_hours_off_season
          - binary_sensor.pool_water_level_critical
    action:
      service: pool_pump.check
```

### Swimming season

The following input boolean is there to distinguish between swimming season
and off season.

```yaml
input_boolean:
  swimming_season:
    name: Swimming Season
    icon: mdi:swim
```

### Number of hours to run the pool pump

The following configuration adds two sliders to select the number of hours
that the pool pump should run in swimming season and off season.
You may want to change min/max depending on your local needs.

```yaml
input_number:
  run_pool_pump_hours_swimming_season:
    name: Run Pool Pump in Swimming Season
    min: 1
    max: 8
    step: 1
  run_pool_pump_hours_off_season:
    name: Run Pool Pump in Off Season
    min: 1
    max: 6
    step: 1
```

### Critical Water Level

If the pool pump is fed through a skimmer then there is typically a minimum
water level under which the pool pump does not receive enough water anymore
and starts pulling in air which is not ideal.
 
The Pool Pump manager supports specifying an entity id using parameter
`water_level_critical_entity_id`. If that entity is `on` the pool pump will
not turn on, and if it is `off` then the manager will just follow its time/sun
based algorithm to turn the pool pump on or off.

## Pool Pump configuration

The pool pump component needs all the above entities as input to be able to 
make the right decision and turn the pool pump on or off automatically.

```yaml
pool_pump:
  switch_entity_id: switch.pool_pump
  pool_pump_mode_entity_id: input_select.pool_pump
  swimming_season_entity_id: input_boolean.swimming_season
  run_pool_pump_hours_swimming_season_entity_id: input_number.run_pool_pump_hours_swimming_season
  run_pool_pump_hours_off_season_entity_id: input_number.run_pool_pump_hours_off_season
  water_level_critical_entity_id: binary_sensor.pool_water_level_critical
```
