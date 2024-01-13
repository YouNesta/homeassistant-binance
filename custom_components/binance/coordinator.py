from datetime import timedelta
import logging
import aiohttp
import time
import hmac
import hashlib
from homeassistant.const import CONF_API_KEY, CONF_NAME
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers import device_registry as dr, entity_registry as er
from binance.client import Client
from .constants import (DOMAIN, CONF_API_SECRET, CONF_DOMAIN, DEFAULT_DOMAIN,
                         CONF_NATIVE_CURRENCY, DEFAULT_CURRENCY,
                         CONF_ENABLE_BALANCES, CONF_ENABLE_FUNDING,
                         CONF_ENABLE_EXCHANGES)
from .binance.binance_sensor import BinanceSensor

_LOGGER = logging.getLogger(__name__)
UPDATE_INTERVAL = timedelta(minutes=1)
SCAN_INTERVAL = timedelta(minutes=1)

class BinanceCoordinator(DataUpdateCoordinator):
    """Coordinator to retrieve data from Binance."""

    def __init__(self, hass: HomeAssistant, entry, configured_balances, configured_exchanges):
        """Initialize the coordinator."""
        self.hass = hass
        self.entry = entry
        self.api_key = entry.data[CONF_API_KEY]
        self.api_secret = entry.data[CONF_API_SECRET]
        self.tld = entry.data.get(CONF_DOMAIN, DEFAULT_DOMAIN)
        self.conf_name = entry.data.get(CONF_NAME)
        self.native_currency = entry.data.get(CONF_NATIVE_CURRENCY, DEFAULT_CURRENCY)
        self.enabled_feature = {feature: entry.data.get(feature_key) for feature, feature_key in 
                                [('balance', CONF_ENABLE_BALANCES), ('exchanges', CONF_ENABLE_EXCHANGES), ('funding', CONF_ENABLE_FUNDING)]}
        self.client = None
        self.balances,  self.funding_balances, self.tickers= ([], [],  {})
        self.configured_balances = self._parse_configured_items(configured_balances)
        self.configured_exchanges = self._parse_configured_items(configured_exchanges)

        super().__init__(
            hass,
            _LOGGER,
            name="Binance Coordinator",
            update_interval=SCAN_INTERVAL,
        )

    def _parse_configured_items(self, items):
        """Parse configured items from a comma-separated string."""
        if items is not None:
            return [item.strip() for item in items.split(',')] if items else []
        return None

    def _get_signature(self, params):
        """Generate a signature for API calls."""
        query_string = '&'.join([f"{key}={value}" for key, value in params.items()])
        return hmac.new(self.api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

    async def _api_call(self, method, url, params={}, is_post=False):
        """Make an API call to the Binance API."""
        try:
            params.update({'timestamp': int(time.time() * 1000), 'recvWindow': 5000})
            signature = self._get_signature(params)
            params['signature'] = signature
            headers = {'X-MBX-APIKEY': self.api_key}
            final_url = f"https://api.binance.com{url}"
            
            session = self.hass.helpers.aiohttp_client.async_get_clientsession()
            async with session.request("POST" if is_post else "GET", final_url, headers=headers, params=params) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            _LOGGER.error(f"Network error during API call to {url}: {e}" ,  exc_info=True)
            raise UpdateFailed(f"Network error: {e}")
        except Exception as e:
            _LOGGER.error(f"Error during API call to {url}: {e}")
            raise UpdateFailed(f"API call error: {e}")

    def get_device_info(self, device_type: str, name_suffix: str) -> DeviceInfo:
        identifiers={(DOMAIN, str(self.entry.entry_id) + "-" + device_type)}

        device_info_args = {
            "identifiers": identifiers,
            "manufacturer": "Binance",
            "name": f"{self.conf_name} Binance {name_suffix}",
            "model": f"Binance {name_suffix}",
            "configuration_url": "https://www.binance.com",
            "sw_version": "1.0",
            "entry_type": dr.DeviceEntryType.SERVICE,  # Utilisez DeviceEntryType ici
        }
        if device_type != "account":
            device_info_args["via_device"] = (DOMAIN, str(self.entry.entry_id) + "-account")

        return  device_info_args

    @property
    def device_info_spot_balances(self) -> DeviceInfo:
        """Device information for balances."""
        return self.get_device_info("balances", "Spot Balances")

    @property
    def device_info_funding_balances(self) -> DeviceInfo:
        """Device information for balances."""
        return self.get_device_info("funding", "Funding Balances")

    @property
    def device_info_exchanges(self) -> DeviceInfo:
        """Device information for exchanges."""
        return self.get_device_info("exchanges", "Exchanges")

    
    async def _update_feature_data(self, feature_name, update_method):
        """Update feature data based on enabled feature."""
        if self.enabled_feature.get(feature_name):
            try:
                await update_method()
            except Exception as e:
                _LOGGER.error(f"Error updating {feature_name}: {e}")

    async def _async_update_data(self):
        """Update data with better error handling and conditional updates."""
        if not self.client:
            await self.init_client()
        try:
            await self._update_feature_data('balance', self.update_balances)
            await self._update_feature_data('exchanges', self.update_tickers)
            await self._update_feature_data('funding', self.update_funding_balances)

            return {
                "balances": self.balances,
                "tickers": self.tickers,
                "funding_balances": self.funding_balances
            }
        except Exception as e:
            _LOGGER.error(f"Error updating Binance data: {e}")
            raise UpdateFailed(f"Error updating data: {e}")

    async def init_client(self):
        """Initialize Binance client with better error handling."""
        if self.client is not None:
            return  # Client is already initialized

        try:
            self.client = await self.hass.async_add_executor_job(
                lambda: Client(self.api_key, self.api_secret, tld=self.tld))
        except Exception as e:
            _LOGGER.error(f"Error initializing Binance client: {e}")
            self.client = None
            raise UpdateFailed(f"Could not initialize Binance client: {e}")

    async def update_balances(self):
        """Update balance data."""
        if self.client is None:
            await self.init_client()
        account_info = await self.hass.async_add_executor_job(self.client.get_account)
        self.balances = [balance for balance in account_info.get("balances", [])
                         if not self.configured_balances or balance['asset'] in self.configured_balances]

    async def update_tickers(self):
        """Update ticker data."""
        if self.client is None:
            await self.init_client()
        prices = await self.hass.async_add_executor_job(self.client.get_all_tickers)
        self.tickers = {ticker['symbol']: ticker for ticker in prices
                        if not self.configured_exchanges or ticker['symbol'] in self.configured_exchanges}


    async def update_funding_balances(self):
        """Méthode pour mettre à jour les soldes Funding."""
        try:
            self.funding_balances = await self.hass.async_add_executor_job(self.client.funding_wallet)
            for balance in self.funding_balances: 
                if balance:
                    sensor_name = f"sensor.{self.conf_name}_{balance['asset']}_funding_balance".lower().replace(" ", "_")
                    sensor_exist = await self.check_sensor_exists(sensor_name)
                    if not sensor_exist : 
                        self.hass.async_create_task(
                            self.add_new_sensor(balance, 'funding')
                        )
        except Exception as e:
            _LOGGER.error(f"Error during funding call: {e}")

    async def check_sensor_exists(self, entity_id):
        """Vérifie si un capteur avec un ID donné existe déjà."""
        entity_registry = er.async_get(self.hass)
        return entity_registry.async_get(entity_id) is not None    
    
    async def add_new_sensor(self, sensor_data, account_type):
        """Créer et ajouter un nouveau capteur."""
        sensor = BinanceSensor(self, self.conf_name, sensor_data, account_type)
        self.async_add_entities([sensor], True)

    async def universal_transfer(self, type, asset, amount, from_symbol=None, to_symbol=None):
        """Perform a universal transfer using the Binance API natively."""
        params = {
            "type": type,
            "asset": asset,
            "amount": amount
        }
        if from_symbol:
            params["fromSymbol"] = from_symbol
        if to_symbol:
            params["toSymbol"] = to_symbol

        return await self._api_call("POST", "/sapi/v1/asset/transfer", params, is_post=True)

    async def async_config_entry_first_refresh(self):
        """Initial data fetch from Binance API."""
        try:
            await self.async_refresh()
        except Exception as e:
            _LOGGER.error(f"Error during first refresh of Binance config entry: {e}")
            raise UpdateFailed(f"Initial data fetch error: {e}")