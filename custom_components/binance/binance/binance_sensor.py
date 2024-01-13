from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from ..constants import  DEFAULT_COIN_ICON, ATTRIBUTION, ATTR_FREE, ATTR_LOCKED, ATTR_NATIVE_BALANCE,  CURRENCY_ICONS, ATTR_NATIVE_UNIT, BinanceEntityFeature
import logging
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.core import callback

_LOGGER = logging.getLogger(__name__)

class BinanceSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Binance Sensor."""

    def __init__(self, coordinator, name, balance, account_type='spot'):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._name = f"{name} {balance['asset']} {account_type} Balance"
        self._asset = balance["asset"]
        self._state = balance["free"]
        self._free = balance["free"]
        self._locked = balance["locked"]
        self._native = coordinator.native_currency
        self._native_balance = None
        self._coordinator = coordinator
        self._attr_unique_id = f"{name}_{balance['asset']}_{account_type}_balance"

        self._attr_available = True
        self._attr_device_class = "monetary" 
        self.account_type = account_type 
        self._attr_supported_features = (
           BinanceEntityFeature.EXT_WITHDRAW
         )

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name
    @property
    def device_info(self):
        """Return the name of the sensor."""
        device_info = {}
        if self.account_type == 'spot':
            device_info = self.coordinator.device_info_spot_balances
        else: 
            device_info = self.coordinator.device_info_funding_balances
        return device_info

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._asset

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return CURRENCY_ICONS.get(self._asset, DEFAULT_COIN_ICON)

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the sensor."""
        return {
            ATTR_ATTRIBUTION: ATTRIBUTION,
            ATTR_NATIVE_BALANCE: f"{self._native_balance}",
            ATTR_NATIVE_UNIT: f"{self._native_balance}",
            ATTR_FREE: f"{self._free}",
            ATTR_LOCKED: f"{self._locked}",
        }

    @property
    def is_valid(self):
        """Validate sensor data."""
        try:
            return all(isinstance(self.__getattribute__(attr), str) for attr in ['_name', '_asset', '_state'])
        except Exception as e:
            _LOGGER.error(f"Invalid data for sensor {self._name}: {e}")
            return False

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        symbol = f"{self._asset}{self._native}"
        ticker = self._coordinator.data.get("tickers", {}).get(symbol)
        balances = {}

        if self.account_type == 'funding':
            balances = self._coordinator.data.get("funding_balances", {})
        else: 
            balances = self._coordinator.data.get("balances", {})

        for balance in balances:
          if balance["asset"] == self._asset: 
            self._state = balance["free"]
            self._free = balance["free"]
            self._locked = balance["locked"]
            if ticker:
                try:
                    self._native_balance = round(
                        float(ticker["price"]) * float(balance["free"]), 2
                    )
                except (ValueError, TypeError) as e:
                    _LOGGER.error(f"Error updating {self._name}: {e}")
                    self._native_balance = None
            else:
                self._native_balance = None

        self.async_write_ha_state()
    
