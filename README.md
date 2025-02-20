# Monad Testnet Automation

This tool automates interactions with the Monad testnet, including faucet claims, Discord connections, and token swaps.

## Features
- 🌊 Connect Discord account
- 💧 Claim from faucet
- 💱 Perform token swaps
- 💰 Collect all tokens to MON

## Features Description

### Connect Discord
Connects your Discord account to Monad testnet for additional rewards.

### Faucet
Claims test tokens from the Monad testnet faucet.

### Swaps
Performs random swaps between available tokens (DAK, YAKI, CHOG) with configurable amounts.

### Collect All to Monad
Swaps all available tokens back to MON (native token).

## Requirements
- Python 3.11 or higher

## Installation

1. Clone the repository
```bash
git clone https://github.com/StarLabsTech/StarLabs-Monad.git
cd StarLabs-Monad
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Configure the bot in `config.yaml`

```yaml
SETTINGS:
# number of concurrent threads
THREADS: 1
# number of retries for ANY action
ATTEMPTS: 5
# pause between attempts
PAUSE_BETWEEN_ATTEMPTS: [5, 15]
# pause in seconds between accounts
RANDOM_PAUSE_BETWEEN_ACCOUNTS: [3, 10]
# pause in seconds between actions
RANDOM_PAUSE_BETWEEN_ACTIONS: [2, 5]
FLOW:
# Available tasks:
# "faucet" - request ETH from faucet
# "connect_discord" - connect discord account
# "swaps" - swaps tokens
# "collect_all_to_monad" - swaps all tokens to MON token
TASKS: ["connect_discord", "faucet", "swaps", "collect_all_to_monad"]
# number of swaps
NUMBER_OF_SWAPS: [1, 3]
# percent of balance to swap
PERCENT_OF_BALANCE_TO_SWAP: [30, 50]
CAPTCHA:
# Bestcaptchasolver.com API key
BESTCAPTCHA_API_KEY: "YOUR_API_KEY"
PROXY_FOR_CAPTCHA: ""
CAPTCHA_SOLVE_ATTEMPTS: 5
```

4. Add your data to the following files:
- `data/private_keys.txt` - One private key per line
- `data/proxies.txt` - One proxy per line (format: `user:pass@ip:port`)
- `data/discord_tokens.txt` - One Discord token per line


5. Run the bot
```bash
python main.py
```

## Support
- Telegram: https://t.me/StarLabsTech
- Chat: https://t.me/StarLabsChat