# Monad Testnet Automation

This tool automates interactions with the Monad testnet, including various DeFi operations and token interactions.

TUTORIAL - https://star-labs.gitbook.io/star-labs/monad-ru

## Features
# All features are available in config.yaml
- 💎 MagicEden
- 💱 Perform token swaps
- 🏦 Stake MON on Apriori, Magma, Kintsu, Shmonad, Bima
- 📄 Mint NFT: accountable, lilchogstars, demask, monadking, monadking_unlocked
- 🦉 Deploy contract on Owlto
- 🌋 Gaszip
- 🌐 Orbiter
- 📄 Logs
- 📄 Nad domains
- And much more...

## Features Description

### Faucet
Using official Monad testnet faucet.

### Swaps
Performs random swaps between available tokens with configurable amounts.

### Apriori Staking
Stakes MON tokens on Apriori platform with configurable amounts.

### Magma Staking
Stakes MON tokens on Magma platform with configurable amounts.

### Owlto Contract Deployment
Deploys smart contracts on Owlto platform.

### Bima Operations
- Claims tokens from Bima faucet
- Performs lending operations with configurable percentage of balance

## Requirements
- Python 3.11 or higher

## Installation

1. Clone the repository
```bash
git clone https://github.com/0xStarLabs/StarLabs-Monad.git
cd StarLabs-Monad
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Configure the bot by starting it (py main.py) and choosing the edit config option`
![image](https://github.com/user-attachments/assets/c5ca3696-92db-4e48-89a8-e0cd46a57865)


```

4. Add your data to the following files:
- `data/private_keys.txt` - One private key per line
- `data/proxies.txt` - One proxy per line (format: `user:pass@ip:port`)


5. Run the bot
```bash
python main.py
```

## Support
- Telegram: https://t.me/StarLabsTech
- Chat: https://t.me/StarLabsChat
