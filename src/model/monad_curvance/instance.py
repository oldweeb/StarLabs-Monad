

import asyncio
import random
from eth_account import Account
from loguru import logger
from primp import AsyncClient
from web3 import AsyncWeb3

from src.utils.config import Config
from src.utils.constants import RPC_URL


class MonadCurvance:
    def __init__(
        self,
        account_index: int,
        proxy: str,
        private_key: str,
        config: Config,
        session: AsyncClient,
    ):
        self.account_index = account_index
        self.proxy = proxy
        self.private_key = private_key
        self.config = config
        self.session = session

        self.account: Account = Account.from_key(private_key=private_key)
        self.web3 = AsyncWeb3(
             AsyncWeb3.AsyncHTTPProvider(
                 RPC_URL,
                 request_kwargs={"proxy": (f"http://{proxy}") if proxy else None, "ssl": False},
             )
        ) 

    async def login(self):
        for retry in range(self.config.SETTINGS.ATTEMPTS):
            try:
                return True

            except Exception as e:
                random_pause = random.randint(
                    self.config.SETTINGS.RANDOM_PAUSE_BETWEEN_ACTIONS[0],
                    self.config.SETTINGS.RANDOM_PAUSE_BETWEEN_ACTIONS[1],
                )
                logger.error(
                    f"[{self.account_index}] Error in login on Monad Curvance: {e}. Sleeping for {random_pause} seconds"
                )
                await asyncio.sleep(random_pause)
                continue

        return False
