import voluptuous as vol
from homeassistant.const import  CONF_NAME
import homeassistant.helpers.config_validation as cv
from homeassistant.core import HomeAssistant
import logging
from datetime import timedelta
from .constants import DOMAIN, UNDO_UPDATE_LISTENER, SERVICE_WITHDRAW, CONF_BALANCES, CONF_EXCHANGES
from homeassistant.config_entries import  ConfigEntry
from homeassistant.helpers import device_registry as dr
from homeassistant import config_entries 
from homeassistant.helpers import config_validation as cv
from .coordinator import BinanceCoordinator
from homeassistant.helpers import  entity_registry as er
from homeassistant.helpers.entity_component import EntityComponent
from binance.exceptions import BinanceAPIException


_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(minutes=1)
PLATFORMS = ["sensor"]

WITHDRAW_SERVICE_SCHEMA = vol.Schema({
    vol.Required("entity_id"):  cv.entity_id,
    vol.Required("amount"): cv.positive_float,
    vol.Required("address"): cv.string,
    vol.Optional("name"): cv.string,
    vol.Optional("address_tag"): cv.string,
})

async def async_setup(hass, config):
    hass.data[DOMAIN] = {}
    return True

@config_entries.HANDLERS.register(DOMAIN) 
async def async_update_options(hass, config_entry: ConfigEntry):
    """Update options for Binance."""
    await hass.config_entries.async_reload(config_entry.entry_id)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Binance from a config entry."""
    _LOGGER.debug("Setting up Binance config entry")

    data = hass.data.setdefault(DOMAIN, {})

    undo_listener = entry.add_update_listener(async_update_options)
    data[entry.entry_id] = {UNDO_UPDATE_LISTENER: undo_listener}

    coordinator = BinanceCoordinator(
        hass, 
        entry, 
        configured_balances=entry.data.get(CONF_BALANCES),
        configured_exchanges=entry.data.get(CONF_EXCHANGES)
    )


    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id] = coordinator

    async def handle_withdraw_service(call):
        """Gérer l'appel du service de retrait."""
        entity_id = call.data.get("entity_id")
        entity_registry = er.async_get(hass)
        try:
            entity_entry = entity_registry.entities.get(entity_id)
            if entity_entry is None:
                raise ValueError(f"Entité non trouvée pour l'ID: {entity_id}")

            coordinator = hass.data[DOMAIN].get(entity_entry.config_entry_id)
            if not coordinator:
                raise ValueError(f"Coordinateur non trouvé pour entry_id: {entity_entry.config_entry_id}")

            currency = entity_entry.unit_of_measurement
            account_type = entity_entry.account_type
            amount = call.data.get("amount")
            address = call.data.get("address")
            name = call.data.get("name", None) 
            address_tag = call.data.get("address_tag", None)  

            api_params = {
                "coin": currency,
                "amount": amount,
                "address": address,
            }

            if account_type == 'spot':
                api_params["walletType"] = 0
            else: 
                api_params["walletType"] = 1

            if name is not None:
                api_params["name"] = name
            if address_tag is not None:
                api_params["addressTag"] = address_tag
            try:
                result = await hass.async_add_executor_job(
                    lambda: coordinator.client.withdraw(**api_params)
                )
                _LOGGER.info(f"Retrait réussi: {result}")
            except BinanceAPIException as bae:  # Remplacez par l'exception appropriée
                raise _LOGGER.error(f"Erreur de l'API Binance: {bae}")
            except Exception as e:
                raise _LOGGER.error(f"Erreur lors du retrait: {e}")
        except ValueError as ve:
            raise _LOGGER.error(str(ve))
        except Exception as e:
            raise _LOGGER.error(f"Erreur inattendue lors du traitement du retrait: {e}", exc_info=True)


    if "withdraw_service_registered" not in hass.data[DOMAIN]:
        hass.services.async_register(
            DOMAIN, SERVICE_WITHDRAW, handle_withdraw_service, schema=WITHDRAW_SERVICE_SCHEMA
        )
        hass.data[DOMAIN]["withdraw_service_registered"] = True

    try:
        device_registry = dr.async_get(hass)
        device_info = coordinator.get_device_info('account', 'Account')

        device_args = {
            "config_entry_id": coordinator.config_entry.entry_id,
            "identifiers": device_info["identifiers"],
            "manufacturer": device_info["manufacturer"],
            "name": device_info["name"],
            "model": device_info["model"],
            "configuration_url": device_info["configuration_url"],
        }

        device_registry.async_get_or_create(**device_args )
        
    except Exception as e:
        _LOGGER.error(f"Error registering Binance Account device: {e}")

    name = entry.data[CONF_NAME] 
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(
            entry, "sensor"
        )
    )

    _LOGGER.info(f"Successfully set up Binance config entry: {name}")
    return True

async def async_unload_entry(hass, entry):
    """Unload a config entry."""
    try:
        unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
        if unload_ok:
            hass.data[DOMAIN].pop(entry.entry_id)
        return unload_ok
    except Exception as e:
        _LOGGER.error(f"Error unloading Binance config entry: {e}")
        return False
    