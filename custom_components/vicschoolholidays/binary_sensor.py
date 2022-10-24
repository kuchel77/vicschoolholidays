"""Sensor to indicate whether the current day is a workday."""
from __future__ import annotations

from datetime import date, timedelta
import logging
from typing import Any

import voluptuous as vol

from homeassistant.components.binary_sensor import (
    PLATFORM_SCHEMA as PARENT_PLATFORM_SCHEMA,
    BinarySensorEntity,
)
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.util import dt

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "Date Range Binary Sensor"
DEFAULT_OFFSET = 0

CONF_OFFSET = "days_offset"

PLATFORM_SCHEMA = PARENT_PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_OFFSET, default=DEFAULT_OFFSET): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the daterange sensor."""
    days_offset: int = config[CONF_OFFSET]
    sensor_name: str = config[CONF_NAME]

    #Load holidays here
    obj_holidays = [{ "start": "2022-06-25", "end":"2022-07-10" }, { "start":"2022-09-17","end":"2022-10-02" }, { "start":"2022-12-12", "end":"2023-01-29"}]

    add_entities(
        [IsSchoolHolidaySensor(obj_holidays, days_offset, sensor_name)],
        True,
    )

def get_date(input_date: date) -> date:
    """Return date. Needed for testing."""
    return input_date


class IsSchoolHolidaySensor(BinarySensorEntity):
    """Implementation of a Workday sensor."""

    def __init__(
        self,
        obj_holidays,
        days_offset: int,
        name: str,
    ) -> None:
        """Initialize the Workday sensor."""
        self._attr_name = name
        self._obj_holidays = obj_holidays
        self._days_offset = days_offset
        self._attr_extra_state_attributes = {
            CONF_OFFSET: days_offset,
        }

    def is_school_holidays(self, now: date) -> bool:
        """Check if given day is in the includes list."""
        for dates in self._obj_holidays:
            if now >= dt.parse_datetime(dates["start"]).astimezone() and now <= dt.parse_datetime(dates["end"]).astimezone():
                return True
        
        return False

    async def async_update(self) -> None:
        """Get date and look whether it is a holiday."""
        self._attr_is_on = False
        adjusted_date = dt.now() + timedelta(days=int(self._days_offset))
        if self.is_school_holidays(adjusted_date):
            self._attr_is_on = True
