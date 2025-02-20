import asyncio
import random
import os
import shutil
import tempfile
from pathlib import Path
from eth_account import Account
from loguru import logger
from primp import AsyncClient
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

from src.utils.config import Config
from src.utils.email_parser import SyncEmailChecker


class ThirdWeb:
    def __init__(
        self,
        account_index: int,
        proxy: str,
        private_key: str,
        email: str,
        config: Config,
        session: AsyncClient,
    ):
        self.account_index = account_index
        self.proxy = proxy
        self.private_key = private_key
        self.email_login = email.split(":")[0]
        self.email_password = email.split(":")[1]
        self.config = config
        self.session = session

        self.account: Account = Account.from_key(private_key=private_key)

        # Разбираем прокси
        proxy_parts = self.proxy.split("@")
        auth = proxy_parts[0].split(":")

        self.proxy_options = {
            "server": f"http://{proxy_parts[1]}",
            "username": auth[0],
            "password": auth[1],
        }

        # Создаем временную директорию
        self.temp_dir = tempfile.mkdtemp()
        self.user_data_dir = Path(self.temp_dir) / str(self.account_index)

        # Путь к расширению метамаск
        self.metamask_path = Path("src/extra/metamask_extension").resolve()

        if not self.metamask_path.exists():
            raise Exception(f"MetaMask extension not found at {self.metamask_path}")

    async def setup_browser(self) -> tuple[Browser, BrowserContext, Page]:
        """Настраивает браузер с Метамаском и прокси"""
        try:
            logger.info(f"[{self.account_index}] Setting up browser with MetaMask...")

            # Создаем директорию для данных браузера если её нет
            os.makedirs(self.user_data_dir, exist_ok=True)

            playwright = await async_playwright().start()

            # Пути к расширениям
            metamask_path = self.metamask_path
            capsolver_path = Path("src/extra/capsolver").resolve()

            if not capsolver_path.exists():
                raise Exception(f"Capsolver extension not found at {capsolver_path}")

            # Запускаем браузер с постоянным контекстом
            context = await playwright.chromium.launch_persistent_context(
                user_data_dir=str(self.user_data_dir),
                proxy=self.proxy_options,
                headless=False,
                args=[
                    f"--disable-extensions-except={metamask_path},{capsolver_path}",
                    f"--load-extension={metamask_path},{capsolver_path}",
                ],
                timeout=int(30000 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER),
            )

            # Создаем новую страницу для работы
            page = await context.new_page()

            # Даем время на загрузку расширения
            await asyncio.sleep(int(5 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER))

            # Ищем страницу метамаска среди открытых страниц
            metamask_page = None
            all_pages = context.pages
            for p in all_pages:
                if "chrome-extension://" in p.url and "/home.html" in p.url:
                    metamask_page = p
                    logger.info(
                        f"[{self.account_index}] Found MetaMask page at: {p.url}"
                    )
                    break

            if not metamask_page:
                # Если страница метамаска не найдена, пробуем открыть напрямую
                all_background_pages = context.background_pages
                for bg_page in all_background_pages:
                    if "chrome-extension://" in bg_page.url:
                        logger.info(
                            f"[{self.account_index}] Found background page: {bg_page.url}"
                        )
                        extension_id = bg_page.url.split("/")[2]
                        metamask_page = await context.new_page()
                        await metamask_page.goto(
                            f"chrome-extension://{extension_id}/home.html",
                            wait_until="networkidle",
                        )
                        break

            if not metamask_page:
                raise Exception("MetaMask extension page not found")

            logger.success(f"[{self.account_index}] Browser setup completed")
            return None, context, page

        except Exception as e:
            logger.error(f"[{self.account_index}] Error setting up browser: {e}")
            if "context" in locals():
                await context.close()
            raise

    async def _login_metamask(self, metamask_page: Page) -> bool:
        """Логин в MetaMask и импорт кошелька"""
        try:
            logger.info(f"[{self.account_index}] Logging into MetaMask...")
            await asyncio.sleep(int(4 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER))

            # Click "Get Started" button
            await metamask_page.click(
                "xpath=/html/body/div[1]/div/div[2]/div/div/div/ul/li[1]/div/input",
                timeout=int(30000 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER),
            )
            await asyncio.sleep(int(1 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER))

            await metamask_page.click(
                "xpath=/html/body/div[1]/div/div[2]/div/div/div/ul/li[2]/button",
                timeout=int(30000 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER),
            )
            await asyncio.sleep(int(1 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER))

            await metamask_page.click(
                "xpath=/html/body/div[1]/div/div[2]/div/div/div/div[2]/button[2]",
                timeout=int(30000 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER),
            )
            await asyncio.sleep(int(1 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER))

            # Fill password fields
            await metamask_page.fill(
                "xpath=/html/body/div[1]/div/div[2]/div/div/div/div[2]/form/div[1]/label/input",
                "00000000",
                timeout=int(30000 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER),
            )
            await metamask_page.fill(
                "xpath=/html/body/div[1]/div/div[2]/div/div/div/div[2]/form/div[2]/label/input",
                "00000000",
                timeout=int(30000 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER),
            )

            # Click through import flow
            await metamask_page.click(
                "xpath=/html/body/div[1]/div/div[2]/div/div/div/div[2]/form/div[3]/label/span[1]/input",
                timeout=int(30000 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER),
            )
            await asyncio.sleep(int(1 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER))

            await metamask_page.click(
                "xpath=/html/body/div[1]/div/div[2]/div/div/div/div[2]/form/button",
                timeout=int(30000 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER),
            )
            await asyncio.sleep(int(1 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER))

            await metamask_page.click(
                "xpath=/html/body/div[1]/div/div[2]/div/div/div/div[2]/button[1]",
                timeout=int(30000 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER),
            )
            await asyncio.sleep(int(1 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER))

            await metamask_page.click(
                "xpath=/html/body/div[2]/div/div/section/div[1]/div/div/label/input",
                timeout=int(30000 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER),
            )
            await asyncio.sleep(int(1 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER))

            await metamask_page.click(
                "xpath=/html/body/div[2]/div/div/section/div[2]/div/button[2]",
                timeout=int(30000 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER),
            )
            await asyncio.sleep(int(1 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER))

            await metamask_page.click(
                "xpath=/html/body/div[1]/div/div[2]/div/div/div/div[3]/button",
                timeout=int(30000 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER),
            )
            await asyncio.sleep(int(1 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER))

            await metamask_page.click(
                "xpath=/html/body/div[1]/div/div[2]/div/div/div/div[2]/button",
                timeout=int(30000 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER),
            )
            await asyncio.sleep(int(1 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER))

            await metamask_page.click(
                "xpath=/html/body/div[1]/div/div[2]/div/div/div/div[2]/button",
                timeout=int(30000 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER),
            )
            await asyncio.sleep(int(1 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER))

            await metamask_page.click(
                "xpath=/html/body/div[1]/div/div[2]/div/div[2]/button",
                timeout=int(30000 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER),
            )
            await asyncio.sleep(int(1 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER))

            await metamask_page.click(
                "xpath=/html/body/div[3]/div[3]/div/section/div[2]/button",
                timeout=int(30000 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER),
            )
            await asyncio.sleep(int(1 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER))

            await metamask_page.click(
                "xpath=/html/body/div[3]/div[3]/div/section/div/div[2]/button",
                timeout=int(30000 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER),
            )
            await asyncio.sleep(int(1 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER))

            # Import private key
            await metamask_page.fill(
                "xpath=/html/body/div[3]/div[3]/div/section/div/div/div[1]/div/input",
                self.private_key,
                timeout=int(30000 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER),
            )
            await asyncio.sleep(int(2 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER))

            await metamask_page.click(
                "xpath=/html/body/div[3]/div[3]/div/section/div/div/div[2]/button[2]",
                timeout=int(30000 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER),
            )
            await metamask_page.close()

            await asyncio.sleep(int(1 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER))
            logger.success(f"[{self.account_index}] Successfully logged into MetaMask")
            return True

        except Exception as e:
            logger.error(f"[{self.account_index}] Error logging into MetaMask: {e}")
            return False

    async def _login_thirdweb(self, page: Page, metamask_page: Page) -> bool:
        """Логин на thirdweb.com"""
        try:
            logger.info(f"[{self.account_index}] Logging into ThirdWeb...")

            # 1. Нажимаем на кнопку MetaMask
            await page.click(
                'text="MetaMask"',
                timeout=int(30000 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER),
            )
            await asyncio.sleep(int(2 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER))

            # 2. Ждем и обрабатываем всплывающее окно MetaMask для подключения
            metamask_popup = None
            for p in page.context.pages:
                if "chrome-extension://" in p.url and p != metamask_page:
                    metamask_popup = p
                    break

            if not metamask_popup:
                raise Exception("MetaMask popup not found")

            # Нажимаем Connect в попапе
            await metamask_popup.click(
                'button[data-testid="confirm-btn"]',
                timeout=int(30000 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER),
            )
            await asyncio.sleep(int(2 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER))

            # 3. Нажимаем Sign in на основной странице
            await page.click(
                'button[data-testid="sign-in-button"]',
                timeout=int(30000 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER),
            )
            await asyncio.sleep(int(2 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER))

            # 4. Ждем и обрабатываем второе всплывающее окно MetaMask
            metamask_popup = None
            for p in page.context.pages:
                if "chrome-extension://" in p.url and p != metamask_page:
                    metamask_popup = p
                    break

            if not metamask_popup:
                raise Exception("MetaMask signature popup not found")

            # Нажимаем Confirm в попапе
            await metamask_popup.click(
                'button[data-testid="confirm-footer-button"]',
                timeout=int(30000 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER),
            )
            await asyncio.sleep(
                int(10 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER)
            )  # Ждем загрузку страницы

            return True

        except Exception as e:
            logger.error(f"[{self.account_index}] Error logging into ThirdWeb: {e}")
            return False

    async def _thirdweb_registration(self, page: Page) -> bool:
        """Регистрация нового аккаунта на ThirdWeb"""
        try:
            logger.info(f"[{self.account_index}] Starting ThirdWeb registration...")

            # 1. Заполняем email
            await page.fill(
                'input[id="email"]',
                self.email_login,
                timeout=int(30000 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER),
            )
            await asyncio.sleep(int(2 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER))

            # 2. Генерируем и вводим имя компании (7-10 букв, первая заглавная)
            import random
            import string

            name_length = random.randint(7, 10)
            company_name = "".join(
                random.choice(string.ascii_lowercase) for _ in range(name_length - 1)
            )
            company_name = company_name.capitalize()

            await page.fill(
                'input[id="name"]',
                company_name,
                timeout=int(30000 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER),
            )
            await asyncio.sleep(int(2 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER))

            # 3. Нажимаем Get Started for Free
            await page.click(
                'button:has-text("Get Started for Free")',
                timeout=int(30000 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER),
            )
            await asyncio.sleep(
                int(5 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER)
            )  # Ждем письмо

            # 4. Получаем код с почты
            email_checker = SyncEmailChecker(self.email_login, self.email_password)
            verification_code = email_checker.check_email_for_code()
            if not verification_code:
                raise Exception("Verification code not found in email")

            logger.info(
                f"[{self.account_index}] Got verification code: {verification_code}"
            )

            # 5. Вводим код верификации - пробуем разные способы
            try:
                # Способ 1: Вводим посимвольно
                input_field = await page.query_selector(
                    'input[data-input-otp="true"]',
                    timeout=int(30000 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER),
                )
                if input_field:
                    # Сначала кликаем чтобы активировать поле
                    await input_field.click(
                        timeout=int(
                            30000 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER
                        )
                    )
                    await asyncio.sleep(
                        int(1 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER)
                    )

                    # Вводим каждый символ отдельно
                    for char in verification_code:
                        await page.keyboard.press(
                            char,
                            timeout=int(
                                30000 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER
                            ),
                        )
                        await asyncio.sleep(
                            int(0.2 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER)
                        )

                else:
                    # Способ 2: Ищем все поля для ввода кода
                    inputs = await page.query_selector_all(
                        'input[data-input-otp="true"]',
                        timeout=int(
                            30000 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER
                        ),
                    )
                    if inputs:
                        for i, char in enumerate(verification_code):
                            if i < len(inputs):
                                await inputs[i].fill(
                                    char,
                                    timeout=int(
                                        30000
                                        * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER
                                    ),
                                )
                                await asyncio.sleep(
                                    int(
                                        0.2
                                        * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER
                                    )
                                )

                    else:
                        # Способ 3: Пробуем через буфер обмена
                        await page.evaluate(
                            f"""
                            navigator.clipboard.writeText("{verification_code}").then(() => {{
                                document.execCommand('paste');
                            }});
                        """
                        )
                        await asyncio.sleep(
                            int(1 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER)
                        )

            except Exception as e:
                logger.warning(
                    f"[{self.account_index}] Error inputting verification code: {e}, trying alternative method"
                )
                # Способ 4: Пробуем через type
                await page.type(
                    'input[data-input-otp="true"]',
                    verification_code,
                    delay=int(100 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER),
                    timeout=int(30000 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER),
                )

            await asyncio.sleep(int(3 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER))

            # Проверяем, что код введен
            page_content = await page.content()
            if verification_code not in page_content:
                logger.warning(
                    f"[{self.account_index}] Code might not be entered correctly, trying to press Enter"
                )
                await page.keyboard.press(
                    "Enter",
                    timeout=int(30000 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER),
                )
                await asyncio.sleep(
                    int(1 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER)
                )

            # 6. Нажимаем Verify
            await page.click(
                'button:has-text("Verify")',
                timeout=int(30000 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER),
            )
            await asyncio.sleep(int(5 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER))

            # 7. Нажимаем Skip for now
            await page.click(
                'button:has-text("Skip for now")',
                timeout=int(30000 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER),
            )
            await asyncio.sleep(int(15 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER))

            # 8. Проверяем URL
            current_url = page.url
            if "login" not in current_url:
                logger.success(
                    f"[{self.account_index}] Successfully registered on ThirdWeb"
                )
                return True
            else:
                raise Exception(
                    f"Registration failed, still on login page: {current_url}"
                )

        except Exception as e:
            logger.error(f"[{self.account_index}] Error in ThirdWeb registration: {e}")
            return False

    async def faucet(self):
        for retry in range(self.config.SETTINGS.ATTEMPTS):
            context = None
            try:
                _, context, page = await self.setup_browser()

                # Находим страницу метамаска
                metamask_page = None
                for p in context.pages:
                    if "chrome-extension://" in p.url and "/home.html" in p.url:
                        metamask_page = p
                        break

                if not metamask_page:
                    raise Exception("MetaMask page not found")

                # Логинимся в метамаск
                if not await self._login_metamask(metamask_page):
                    raise Exception("Failed to login to MetaMask")

                # Переходим на thirdweb
                await page.goto(
                    "https://thirdweb.com/login",
                    timeout=int(30000 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER),
                )
                await asyncio.sleep(int(2 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER))

                # Логинимся на сайте
                if not await self._login_thirdweb(page, metamask_page):
                    raise Exception("Failed to login to ThirdWeb")

                # Проверяем URL после логина
                current_url = page.url
                if "thirdweb.com/login" in current_url:
                    logger.info(f"[{self.account_index}] Registration required")
                    if not await self._thirdweb_registration(page):
                        raise Exception("Failed to register on ThirdWeb")
                else:
                    logger.info(f"[{self.account_index}] Already registered, continuing...")

                # Запрашиваем токены
                if not await self._request_tokens(page):
                    raise Exception("Failed to request tokens from faucet")

                return True

            except Exception as e:
                random_pause = random.randint(
                    self.config.SETTINGS.RANDOM_PAUSE_BETWEEN_ACTIONS[0],
                    self.config.SETTINGS.RANDOM_PAUSE_BETWEEN_ACTIONS[1],
                )
                logger.error(
                    f"[{self.account_index}] Error in ThirdWeb faucet: {e}. Sleeping for {random_pause} seconds"
                )
                await asyncio.sleep(random_pause)
                return False
            finally:
                if context:
                    await context.close()
                try:
                    shutil.rmtree(self.temp_dir)
                    logger.info(f"[{self.account_index}] Temporary directory removed")
                except Exception as e:
                    logger.warning(
                        f"[{self.account_index}] Error removing temporary directory: {e}"
                    )
        return False

    async def _request_tokens(self, page: Page) -> bool:
        """Запрос токенов из фаусета"""
        try:
            logger.info(f"[{self.account_index}] Requesting tokens from faucet...")

            # 1. Открываем страницу фаусета
            await page.goto(
                "https://thirdweb.com/monad-testnet",
                timeout=int(30000 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER),
            )
            await asyncio.sleep(int(30 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER))

            # Пробуем нажать кнопку получения токенов до 3 раз
            for attempt in range(3):
                try:
                    logger.info(
                        f"[{self.account_index}] Attempt {attempt + 1} to claim tokens"
                    )

                    # Нажимаем кнопку
                    await page.click(
                        'button:has-text("Get 0.01 MON")',
                        timeout=int(
                            30000 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER
                        ),
                    )
                    await asyncio.sleep(
                        int(30 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER)
                    )

                    # Проверяем успешность
                    page_content = await page.content()
                    if "Your next claim is available in " in page_content:
                        logger.success(
                            f"[{self.account_index}] Successfully claimed tokens from faucet"
                        )
                        return True

                    logger.warning(
                        f"[{self.account_index}] Attempt {attempt + 1} failed, trying again..."
                    )

                except Exception as e:
                    logger.warning(
                        f"[{self.account_index}] Error in attempt {attempt + 1}: {e}"
                    )

                if attempt < 2:  # Не ждем после последней попытки
                    await asyncio.sleep(
                        int(30 * self.config.SETTINGS.BROWSER_PAUSE_MULTIPLIER)
                    )

            raise Exception("Failed to claim tokens after 3 attempts")

        except Exception as e:
            logger.error(f"[{self.account_index}] Error requesting tokens: {e}")
            return False
