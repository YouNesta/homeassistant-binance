import logging
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .constants import DOMAIN
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .binance.binance_sensor import BinanceSensor
from .binance.binance_exchange_sensor import BinanceExchangeSensor

_LOGGER = logging.getLogger(__name__)

def is_valid_string(value):
    return isinstance(value, str) and value.strip() != ""

async def async_setup_entry(hass: HomeAssistant, config: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Setup the Binance sensors."""

    try:
        entry_id = config.entry_id
        conf_name = config.data.get('name')

        if not all(is_valid_string(val) for val in [entry_id, conf_name]):
            _LOGGER.error("Invalid configuration data.")
            return

        coordinator = hass.data[DOMAIN].get(entry_id)
        if coordinator is None:
            _LOGGER.error("Coordinator for entry_id not found.")
            return
        coordinator.async_add_entities = async_add_entities

        sensors = []

        balances = coordinator.data.get("balances", [])
        for balance in balances:
            if not isinstance(balance, dict) or not all(key in balance for key in ["asset", "free", "locked"]):
                _LOGGER.error(f"Invalid balance data: {balance}")
                continue
            sensor = BinanceSensor(coordinator, conf_name, balance)

            if sensor.is_valid:
                sensors.append(sensor)

        funding_balances = coordinator.data.get("funding_balances", [])
        for balance in funding_balances:
            if not isinstance(balance, dict) or not all(key in balance for key in ["asset", "free", "locked"]):
                _LOGGER.error(f"Invalid balance data: {balance}")
                continue
            sensor = BinanceSensor(coordinator, conf_name, balance, 'funding')

            if sensor.is_valid:
                sensors.append(sensor)

        tickers = coordinator.data.get("tickers", {})
        for symbol, ticker in tickers.items():
            if not isinstance(ticker, dict) or "price" not in ticker:
                _LOGGER.error(f"Invalid ticker data for symbol {symbol}: {ticker}")
                continue
            sensor = BinanceExchangeSensor(coordinator, conf_name, ticker)
            if sensor.is_valid:
                sensors.append(sensor)

        async_add_entities(sensors, True)

    except ValueError as ve:
        _LOGGER.error(f"Value error during sensor setup: {ve}")
    except TypeError as te:
        _LOGGER.error(f"Type error during sensor setup: {te}")
    except Exception as e:
        _LOGGER.error(f"Unexpected error during sensor setup: {e}")
        
