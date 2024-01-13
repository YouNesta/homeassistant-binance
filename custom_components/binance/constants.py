# constants.py

from enum import IntFlag

# Domaine principal du composant
DOMAIN = 'binance'
DEFAULT_NAME = "Binance"
DATA_BINANCE = "binance_cache"

# Clés de configuration
CONF_API_SECRET = 'api_secret'
CONF_NATIVE_CURRENCY = 'native_currency'
CONF_BALANCES = 'balances'
CONF_EXCHANGES = 'exchanges'
CONF_DOMAIN = "domain"
CONF_ENABLE_BALANCES = 'enable_balances'
CONF_ENABLE_EXCHANGES = 'enable_exchanges'
CONF_ENABLE_EARN = 'enable_earn'
CONF_ENABLE_FUNDING = 'enable_funding'
DEFAULT_DOMAIN = "com"

# Autres constantes
DEFAULT_CURRENCY = 'USD'

#ENDPOINTS
ENDPOINT_EARN_FLEXIBLE='/sapi/v1/simple-earn/flexible/position'
ENDPOINT_EARN_LOCKED='/sapi/v1/simple-earn/locked/position'

SERVICE_WITHDRAW = "withdraw"


CURRENCY_ICONS = {
    "BTC": "mdi:currency-btc",
    "ETH": "mdi:currency-eth",
    "EUR": "mdi:currency-eur",
    "LTC": "mdi:litecoin",
    "USD": "mdi:currency-usd",
}

DEFAULT_COIN_ICON = "mdi:bitcoin"
ATTRIBUTION = "Data provided by Binance"
ATTR_UNIT = "unit"
ATTR_FREE = "free"
ATTR_LOCKED = "locked"
ATTR_NATIVE_BALANCE = "native_balance"
ATTR_NATIVE_UNIT = "native_unit"
ATTR_TOTAL_REWARDS = "total_rewards"
QUOTE_ASSETS = ["USD", "BTC", "USDT", "BUSD", "USDC"]
UNDO_UPDATE_LISTENER = "undo_update_listener"


class BinanceEntityFeature(IntFlag):
    """Supported features of the cover entity."""

    EXT_WITHDRAW = 1
