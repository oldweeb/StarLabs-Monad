import asyncio
from loguru import logger
from web3 import AsyncHTTPProvider, AsyncWeb3
from typing import List
import random

from src.utils.config import Config
from src.utils.constants import RPC_URL
from .utils import get_monad_balance, WalletInfo, get_all_balances


class DisperseFromOneWallet:
    def __init__(
        self, farm_key: str, main_keys: List[str], proxies: List[str], config: Config
    ):
        self.farm_key = farm_key
        self.main_keys = main_keys
        self.proxies = proxies
        self.config = config
        self.web3 = AsyncWeb3(AsyncHTTPProvider(RPC_URL))

    async def disperse(self):
        try:
            # Get farm wallet info
            farm_account = self.web3.eth.account.from_key(self.farm_key)
            farm_balance_wei, farm_balance_eth = await get_monad_balance(
                self.web3, farm_account.address
            )

            if farm_balance_eth is None or farm_balance_eth <= 0:
                logger.error("Farm wallet has no balance")
                return False

            # Get main wallets info
            main_wallets = await get_all_balances(
                web3=self.web3,
                private_keys=self.main_keys,
                max_threads=1,  # Use single thread
            )

            min_balance_range = self.config.DISPERSE.MIN_BALANCE_FOR_DISPERSE
            success_count = 0
            total_transfers = 0

            # Get initial nonce
            nonce = await self.web3.eth.get_transaction_count(farm_account.address)

            for wallet in main_wallets:
                # Generate random target balance for each wallet
                target_balance = random.uniform(
                    min_balance_range[0], min_balance_range[1]
                )

                # Skip if wallet already has enough balance
                if wallet.balance_eth >= target_balance:
                    continue

                amount_needed = target_balance - wallet.balance_eth

                # Check if farm wallet has enough balance
                if amount_needed > farm_balance_eth:
                    logger.warning(
                        "Farm wallet doesn't have enough balance for remaining transfers"
                    )
                    break

                # Process transfer
                success = await self.transfer_to_wallet(
                    farm_account, wallet.address, amount_needed, nonce
                )

                if success:
                    success_count += 1
                    farm_balance_eth -= amount_needed
                    nonce += 1

                total_transfers += 1

            if total_transfers == 0:
                logger.info("No transfers needed")
                return True

            logger.info(
                f"Disperse completed. Success: {success_count}/{total_transfers} transfers"
            )
            return success_count > 0

        except Exception as e:
            logger.error(f"Error in disperse from one: {str(e)}")
            return False

    async def transfer_to_wallet(
        self,
        farm_account,
        to_address: str,
        amount_eth: float,
        nonce: int,
    ) -> bool:
        """Process a single transfer from farm wallet to main wallet."""
        try:
            amount_wei = self.web3.to_wei(amount_eth, "ether")

            # Create transaction
            transaction = {
                "from": farm_account.address,
                "to": to_address,
                "value": amount_wei,
                "nonce": nonce,
                "gasPrice": await self.web3.eth.gas_price,
            }

            # Estimate gas and update transaction
            gas = await self.web3.eth.estimate_gas(transaction)
            transaction["gas"] = gas

            # Sign and send transaction
            signed_txn = self.web3.eth.account.sign_transaction(
                transaction, self.farm_key
            )
            tx_hash = await self.web3.eth.send_raw_transaction(
                signed_txn.raw_transaction
            )

            # Wait for transaction receipt
            receipt = await self.web3.eth.wait_for_transaction_receipt(tx_hash)

            if receipt["status"] == 1:
                random_pause = random.uniform(
                    self.config.SETTINGS.PAUSE_BETWEEN_SWAPS[0],
                    self.config.SETTINGS.PAUSE_BETWEEN_SWAPS[1],
                )
                logger.success(
                    f"Successfully transferred {amount_eth} MON to {to_address[:8]}... {random_pause} seconds pause"
                )
                await asyncio.sleep(random_pause)
                return True
            else:
                logger.error(f"Transaction failed for {to_address[:8]}...")
                return False

        except Exception as e:
            logger.error(f"Error processing transfer to {to_address[:8]}...: {str(e)}")
            return False
