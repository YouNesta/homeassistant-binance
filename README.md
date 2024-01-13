[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)

# Binance

This Home Assistant plugin is a custom plugin, offering a range of features and enhancements for more comprehensive management of your Binance account.

## Features

- **Multi-Account Management**: Supports managing multiple Binance accounts simultaneously.
- **Exchanges Price**: Get Ecxchanges prices
- **Exchanges Spot balance**: Get Spot Balance
- **Configuration via User Interface (UI)**: Simplified setup directly through the Home Assistant user interface.
- **Withdraw Service**: Perform withdrawals directly via Home Assistant.
- **EARN Subscriptions Retrieval**: Retrieve and manage your EARN subscriptions from Binance.

## Installation

Ensure that [HACS](https://hacs.xyz/) is installed. Add this repository as a custom repository in HACS and install it via `HACS -> Integrations`.

## Configuration

### Initial Configuration

1. Navigate to the Home Assistant integrations page.
2. Add "Binance" and fill in the required fields:
   - `Name`: A unique name for your Binance configuration.
   - `API Key`: Your Binance API key.
   - `API Secret`: Your Binance API secret.
   - `Native Currency` (optional, default: "USDT"): Your preferred currency for values.

### Advanced Configuration

- Enable balance management, exchange data, and EARN subscriptions as needed.
- Additional configuration steps will appear based on your selections.

#### Balances

- Specify the currencies for balance tracking, separated by commas (e.g., `BTC, ETH, SOL, USDT`).
- If no currency is specified and the balance option is enabled, all balances will be retrieved.

#### Exchanges

- Specify the trading pairs for exchange data, separated by commas (e.g., `SOLUSDT, SOLBTC, ETHUSDT`).
- If no tickers is specified and the tickers option is enabled, all tickers will be retrieved.

### Options Configuration

- Modify your settings anytime through the Home Assistant UI under "Integrations -> Binance -> Options".
- Options include balances, exchanges, and feature toggles.

## Using the Withdraw Service

The name of the service is based on the name of your configuration. Ensure that you have correctly configured the plugin with your Binance API keys.

Before using the Withdraw service, please note that you must first authorize the withdrawal address through the official Binance platform. This is a security measure to ensure the safety of your assets.

Don't forger to Enable Withdraw in your API restrictions on Binance

### How to Call the Withdraw Service

To perform a withdrawal, use the following service in Home Assistant:

```yaml
service: binance.{conf_name}_withdraw
data:
  coin: "BTC"
  amount: 0.01
  address: "your_BTC_address" #
  name: "optional_name"
  addressTag: "optional_address_tag"
```

## Screenshots

(Include screenshots of the configuration steps and UI here)

## Troubleshooting

(Include common issues and solutions related to the configuration flow)

## Updates and Maintenance

(Information about how updates to the plugin will affect the configuration flow)

## Support and Donations

If you find this plugin helpful and would like to support the ongoing development, any donations are greatly appreciated. You can support me through the following channels:

- **PayPal**: [Donate via PayPal](https://www.paypal.com/donate?hosted_button_id=QNB3RRABL6TKS)
- **Buy Me A Coffee**: [Support me on Buy Me A Coffee](https://www.buymeacoffee.com/younesta)
- **Crypto Transfers (BNB Smart Chain)**: `0xe2d737b0f76d05a0e077064492b7d24ffa3a2c16`

### Credits and Acknowledgments

---

This plugin is built upon the foundation of the custom [Binance plugin for Home Assistant](https://github.com/drinfernoo/homeassistant-binance). Special thanks to the original developers and contributors for their work.
