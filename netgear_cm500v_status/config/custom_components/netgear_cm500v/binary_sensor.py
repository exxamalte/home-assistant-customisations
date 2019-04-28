"""
Netgear CM500V Cable Modem Internet Connection Status.

https://github.com/exxamalte/home-assistant-customisations
"""
import ipaddress
import logging
import re
from datetime import timedelta

import voluptuous as vol
from requests.auth import HTTPBasicAuth

from homeassistant.components.binary_sensor import BinarySensorDevice
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.components.rest.sensor import RestData
import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_IP_ADDRESS, CONF_PASSWORD
from homeassistant.exceptions import PlatformNotReady

_LOGGER = logging.getLogger(__name__)

ATTR_DEVICE = 'device'
ATTR_INTERNET_COMMENT = 'internet_comment'
ATTR_IP_ADDRESS = 'ip_address'

DEFAULT_DEVICE = 'Netgear CM500V'
DEFAULT_DEVICE_CLASS = 'connectivity'
DEFAULT_IP_ADDRESS = '192.168.100.1'
DEFAULT_METHOD = 'GET'
DEFAULT_NAME = "Internet Connection Status"
DEFAULT_USERNAME = 'admin'

SCAN_INTERVAL = timedelta(minutes=1)

CONNECTION_STATUS_REGEX = r'function InitTagValue\(\)\s*{\s*' \
                          r'var tagValueList = \'(\d+)\|([\w\s]+)\|'

URL_TEMPLATE = "http://{}/DashBoard.htm"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_IP_ADDRESS, default=DEFAULT_IP_ADDRESS):
        vol.All(ipaddress.ip_address, cv.string),
    vol.Required(CONF_PASSWORD): cv.string,
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor."""
    ip_address = config[CONF_IP_ADDRESS]
    password = config[CONF_PASSWORD]

    auth = HTTPBasicAuth(DEFAULT_USERNAME, password)
    url = URL_TEMPLATE.format(ip_address)

    rest = RestData(DEFAULT_METHOD, url, auth, None, None, False)
    rest.update()
    if rest.data is None:
        raise PlatformNotReady

    # Must update the sensor now (including fetching the rest resource) to
    # ensure it's updating its state.
    add_entities([NetgearCm500vModemConnectionStatus(
            hass, rest, ip_address)], True)


class NetgearCm500vModemConnectionStatus(BinarySensorDevice):
    """Implementation of the sensor."""

    def __init__(self, hass, rest, ip_address):
        """Initialize the binary sensor."""
        self._hass = hass
        self.rest = rest
        self._ip_address = ip_address
        self._state = None
        self._attributes = {
            ATTR_DEVICE: DEFAULT_DEVICE,
            ATTR_IP_ADDRESS: ip_address
        }
        self._name = DEFAULT_NAME

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def device_class(self):
        """Return the class of this device, from component DEVICE_CLASSES."""
        return DEFAULT_DEVICE_CLASS

    @property
    def force_update(self) -> bool:
        """Return True"""
        return True

    def update(self):
        """Get the latest data from REST API and update the state."""
        self.rest.update()
        self._attributes = {
            ATTR_DEVICE: DEFAULT_DEVICE,
            ATTR_IP_ADDRESS: self._ip_address
        }
        value = self.rest.data
        if value:
            match = re.search(CONNECTION_STATUS_REGEX, value, re.MULTILINE)
            if match:
                internet_status = int(match.group(1))
                internet_comment = match.group(2)
                self._state = (internet_status == 0)
                self._attributes[ATTR_INTERNET_COMMENT] = internet_comment
                _LOGGER.info("Internet Connection: status=%s, comment=%s",
                             internet_status, internet_comment)
            else:
                self._state = None
        else:
            self._state = None

    @property
    def is_on(self):
        """Return true if sensor is on."""
        return self._state

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self._attributes
