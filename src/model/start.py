from loguru import logger
import primp
import random

from src.model.monadverse_mint.instance import MonadverseMint
from src.model.thirdweb.instance import ThirdWeb
from src.model.bima.instance import Bima
from src.model.owlto.instance import Owlto
from src.model.magma.instance import Magma
from src.model.apriori import Apriori
from src.model.monad_xyz.instance import MonadXYZ
from src.utils.client import create_client
from src.utils.config import Config
from src.model.help.stats import WalletStats


class Start:
    def __init__(
        self,
        account_index: int,
        proxy: str,
        private_key: str,
        discord_token: str,
        email: str,
        config: Config,
    ):
        self.account_index = account_index
        self.proxy = proxy
        self.private_key = private_key
        self.discord_token = discord_token
        self.email = email
        self.config = config

        self.session: primp.AsyncClient | None = None

    async def initialize(self):
        try:
            self.session = await create_client(self.proxy)

            # Добавляем получение статистики кошелька
            if "logs" in self.config.FLOW.TASKS:
                wallet_stats = WalletStats(self.config)
                await wallet_stats.get_wallet_stats(
                    self.private_key, self.account_index
                )

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

            # Создаем копию списка задач и перемешиваем их
            available_tasks = self.config.FLOW.TASKS.copy()
            random.shuffle(available_tasks)

            logger.info(f"[{self.account_index}] Tasks order: {available_tasks}")

            # Проходим по перемешанным задачам
            for task in available_tasks:
                if task == "connect_discord":
                    await monad.connect_discord()

                elif task == "faucet":
                    if self.config.FAUCET.MONAD_XYZ:
                        await monad.faucet()

                    if self.config.FAUCET.THIRDWEB:
                        thirdweb = ThirdWeb(
                            self.account_index,
                            self.proxy,
                            self.private_key,
                            self.email,
                            self.config,
                            self.session,
                        )
                        await thirdweb.faucet()

                elif task == "swaps":
                    await monad.swaps(type="swaps")

                elif task == "ambient":
                    await monad.swaps(type="ambient")

                elif task == "bean":
                    await monad.swaps(type="bean")

                elif task == "collect_all_to_monad":
                    await monad.swaps(type="collect_all_to_monad")

                elif task == "apriori":
                    apriori = Apriori(
                        self.account_index,
                        self.proxy,
                        self.private_key,
                        self.config,
                        self.session,
                    )
                    await apriori.stake_mon()

                elif task == "magma":
                    magma = Magma(
                        self.account_index,
                        self.proxy,
                        self.private_key,
                        self.config,
                        self.session,
                    )
                    await magma.stake_mon()

                elif task == "owlto":
                    owlto = Owlto(
                        self.account_index,
                        self.proxy,
                        self.private_key,
                        self.config,
                        self.session,
                    )
                    await owlto.deploy_contract()

                elif task == "bima":
                    bima = Bima(
                        self.account_index,
                        self.proxy,
                        self.private_key,
                        self.config,
                        self.session,
                    )
                    await bima.get_faucet_tokens()

                    if self.config.BIMA.LEND:
                        await bima.lend()

                elif task == "monadverse_mint":
                    monadverse_mint = MonadverseMint(
                        self.account_index,
                        self.proxy,
                        self.private_key,
                        self.config,
                        self.session,
                    )
                    await monadverse_mint.mint()

                elif task == "logs":
                    wallet_stats = WalletStats(self.config)
                    await wallet_stats.get_wallet_stats(
                        self.private_key, self.account_index
                    )

            # if "kuru" in self.config.FLOW.TASKS:
            #     kuru = Kuru(self.account_index, self.proxy, self.private_key, self.config, self.session)
            #     await kuru.create_wallet()

            return True
        except Exception as e:
            logger.error(f"[{self.account_index}] | Error: {e}")
            return False
