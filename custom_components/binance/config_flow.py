import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME, CONF_API_KEY
import homeassistant.helpers.config_validation as cv
from .constants import DOMAIN, CONF_API_SECRET,CONF_DOMAIN, CONF_NATIVE_CURRENCY, CONF_BALANCES, CONF_EXCHANGES, CONF_ENABLE_BALANCES, CONF_ENABLE_EXCHANGES, CONF_ENABLE_EARN, CONF_ENABLE_FUNDING
from homeassistant.core import callback

class BinanceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        errors = {}

        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_NAME])
            self._abort_if_unique_id_configured()

            self.context['user_input'] = user_input  # Stockage des entrées initiales

            # Vérifier si les étapes supplémentaires sont nécessaires
            if user_input.get(CONF_ENABLE_BALANCES):
                return await self.async_step_balances()
            elif user_input.get(CONF_ENABLE_EXCHANGES):
                return await self.async_step_exchanges()
            else:
                return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        data_schema = vol.Schema({
            vol.Required(CONF_NAME): cv.string,
            vol.Required(CONF_API_KEY): cv.string,
            vol.Required(CONF_API_SECRET): cv.string,
            vol.Required(CONF_DOMAIN): cv.string,
            vol.Optional(CONF_NATIVE_CURRENCY, default="USDT"): cv.string,
            vol.Optional(CONF_ENABLE_BALANCES, default=False): cv.boolean,
            vol.Optional(CONF_ENABLE_EXCHANGES, default=False): cv.boolean,
            vol.Optional(CONF_ENABLE_FUNDING, default=False): cv.boolean,
            vol.Optional(CONF_ENABLE_EARN, default=False): cv.boolean,
        })

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    async def async_step_balances(self, user_input=None):
        """Handle the balances step."""
        errors = {}
        if user_input is not None:
            self.context['user_input'].update(user_input)

            if self.context['user_input'].get(CONF_ENABLE_EXCHANGES):
                return await self.async_step_exchanges()
            else:
                return self.async_create_entry(title=self.context['user_input'][CONF_NAME], data=self.context['user_input'])

        return self.async_show_form(
            step_id="balances",
            data_schema=vol.Schema({
                vol.Required(CONF_BALANCES): cv.string,
            }),
            errors=errors
        )

    async def async_step_exchanges(self, user_input=None):
        """Handle the exchanges step."""
        errors = {}
        if user_input is not None:
            self.context['user_input'].update(user_input)
            return self.async_create_entry(title=self.context['user_input'][CONF_NAME], data=self.context['user_input'])

        return self.async_show_form(
            step_id="exchanges",
            data_schema=vol.Schema({
                vol.Required(CONF_EXCHANGES): cv.string,
            }),
            errors=errors
        )
        
    @callback
    def async_get_options_flow(config_entry):
        return BinanceOptionsFlowHandler(config_entry)


class BinanceOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        """Initialize Binance options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the Binance options."""
        errors = {}

        if user_input is not None:
            updated_data = dict(self.config_entry.data)

            updated_data.update(user_input)

            self.hass.config_entries.async_update_entry(self.config_entry, data=updated_data)

            return self.async_create_entry(title="", data=user_input)

        current_config = {**self.config_entry.data, **self.config_entry.options}

        options_schema = vol.Schema({
            vol.Required(CONF_DOMAIN, default=current_config.get(CONF_DOMAIN, "")): cv.string,
            vol.Required(CONF_NATIVE_CURRENCY, default=current_config.get(CONF_NATIVE_CURRENCY, "USDT")): cv.string,
            vol.Optional(CONF_ENABLE_BALANCES, default=current_config.get(CONF_ENABLE_BALANCES, False)): cv.boolean,
            vol.Required(CONF_BALANCES, default=current_config.get(CONF_BALANCES, "")): cv.string,
            vol.Optional(CONF_ENABLE_EXCHANGES, default=current_config.get(CONF_ENABLE_EXCHANGES, False)): cv.boolean,
            vol.Required(CONF_EXCHANGES, default=current_config.get(CONF_EXCHANGES, "")): cv.string,
            vol.Optional(CONF_ENABLE_EARN, default=current_config.get(CONF_ENABLE_EARN, False)): cv.boolean,
            vol.Optional(CONF_ENABLE_FUNDING, default=current_config.get(CONF_ENABLE_FUNDING, False)): cv.boolean,
        })

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
            errors=errors
        )