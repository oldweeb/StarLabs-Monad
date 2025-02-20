from loguru import logger
import primp

from src.model.bima.instance import Bima
from src.model.owlto.instance import Owlto
from src.model.magma.instance import Magma
from src.model.apriori import Apriori
from src.model.monad_xyz.instance import MonadXYZ
from src.utils.client import create_client
from src.utils.config import Config


class Start:
    def __init__(
        self,
        account_index: int,
        proxy: str,
        private_key: str,
        discord_token: str,
        config: Config,
    ):
        self.account_index = account_index
        self.proxy = proxy
        self.private_key = private_key
        self.discord_token = discord_token
        self.config = config

        self.session: primp.AsyncClient | None = None

    async def initialize(self):
        try:
            self.session = await create_client(self.proxy)

            return True
        except Exception as e:
            logger.error(f"[{self.account_index}] | Error: {e}")
            return False

    async def flow(self):
        try:
            monad = MonadXYZ(
                self.account_index,
                self.proxy,
                self.private_key,
                self.discord_token,
                self.config,
                self.session,
            )

            if "connect_discord" in self.config.FLOW.TASKS:
                await monad.connect_discord()

            if "faucet" in self.config.FLOW.TASKS:
                await monad.faucet()

            if "swaps" in self.config.FLOW.TASKS:
                await monad.swaps(type="swaps")

            if "collect_all_to_monad" in self.config.FLOW.TASKS:
                await monad.swaps(type="collect_all_to_monad")

            if "apriori" in self.config.FLOW.TASKS:
                apriori = Apriori(
                    self.account_index,
                    self.proxy,
                    self.private_key,
                    self.config,
                    self.session,
                )
                await apriori.stake_mon()

            if "magma" in self.config.FLOW.TASKS:
                magma = Magma(
                    self.account_index,
                    self.proxy,
                    self.private_key,
                    self.config,
                    self.session,
                )
                await magma.stake_mon()

            if "owlto" in self.config.FLOW.TASKS:
                owlto = Owlto(
                    self.account_index,
                    self.proxy,
                    self.private_key,
                    self.config,
                    self.session,
                )
                await owlto.deploy_contract()

            if "bima" in self.config.FLOW.TASKS:
                bima = Bima(
                    self.account_index,
                    self.proxy,
                    self.private_key,
                    self.config,
                    self.session,
                )
                # await bima.get_faucet_tokens()
                if self.config.BIMA.LEND:
                    await bima.lend()

            # if "kuru" in self.config.FLOW.TASKS:
            #     kuru = Kuru(self.account_index, self.proxy, self.private_key, self.config, self.session)
            #     await kuru.create_wallet()

            return True
        except Exception as e:
            logger.error(f"[{self.account_index}] | Error: {e}")
            return False
