import asyncio
import random

from loguru import logger

import src.utils
from src.utils.logs import report_error, report_success
from src.utils.output import show_dev_info, show_logo
import src.model


async def start():
    async def launch_wrapper(index, proxy, private_key, discord_token, email):
        async with semaphore:
            await account_flow(
                index + 1,
                proxy,
                private_key,
                discord_token,
                email,
                config,
                lock,
            )

    show_logo()
    show_dev_info()
    config = src.utils.get_config()

    # Читаем все файлы
    proxies = src.utils.read_txt_file("proxies", "data/proxies.txt")
    private_keys = src.utils.read_txt_file("private keys", "data/private_keys.txt")

    # Определяем диапазон аккаунтов
    start_index = config.SETTINGS.ACCOUNTS_RANGE[0]
    end_index = config.SETTINGS.ACCOUNTS_RANGE[1]

    # Если оба 0, берем все аккаунты
    if start_index == 0 and end_index == 0:
        accounts_to_process = private_keys
        start_index = 1
        end_index = len(private_keys)
    else:
        # Python slice не включает последний элемент, поэтому +1
        accounts_to_process = private_keys[start_index - 1 : end_index]

    # Читаем токены только для нужных аккаунтов
    discord_tokens = []
    if "connect_discord" in config.FLOW.TASKS:
        all_discord_tokens = src.utils.read_txt_file(
            "discord tokens", "data/discord_tokens.txt"
        )
        discord_tokens = (
            all_discord_tokens[start_index - 1 : end_index]
            if all_discord_tokens
            else [""] * len(accounts_to_process)
        )
    else:
        discord_tokens = [""] * len(accounts_to_process)

    # То же самое для email
    emails = []
    if config.FAUCET.THIRDWEB:
        all_emails = src.utils.read_txt_file("emails", "data/emails.txt")
        emails = (
            all_emails[start_index - 1 : end_index]
            if all_emails
            else [""] * len(accounts_to_process)
        )
    else:
        emails = [""] * len(accounts_to_process)

    threads = config.SETTINGS.THREADS

    if len(proxies) == 0:
        logger.error("No proxies found in data/proxies.txt")
        return

    # Подготавливаем прокси для выбранных аккаунтов
    cycled_proxies = [
        proxies[i % len(proxies)] for i in range(len(accounts_to_process))
    ]

    logger.info(f"Starting with accounts {start_index} to {end_index}...")

    lock = asyncio.Lock()
    semaphore = asyncio.Semaphore(value=threads)
    tasks = []

    for index, private_key in enumerate(accounts_to_process):
        tasks.append(
            asyncio.create_task(
                launch_wrapper(
                    start_index + index - 1,  # Сохраняем оригинальный индекс
                    cycled_proxies[index],
                    private_key,
                    discord_tokens[index],
                    emails[index],
                )
            )
        )

    await asyncio.gather(*tasks)

    logger.success("Saved accounts and private keys to a file.")


async def account_flow(
    account_index: int,
    proxy: str,
    private_key: str,
    discord_token: str,
    email: str,
    config: src.utils.config.Config,
    lock: asyncio.Lock,
):
    try:
        report = False

        instance = src.model.Start(
            account_index, proxy, private_key, discord_token, email, config
        )

        result = await wrapper(instance.initialize, config)
        if not result:
            report = True

        result = await wrapper(instance.flow, config)
        if not result:
            report = True

        if report:
            await report_error(lock, private_key, proxy, discord_token)
        else:
            await report_success(lock, private_key, proxy, discord_token)

        pause = random.randint(
            config.SETTINGS.RANDOM_PAUSE_BETWEEN_ACCOUNTS[0],
            config.SETTINGS.RANDOM_PAUSE_BETWEEN_ACCOUNTS[1],
        )
        logger.info(f"Sleeping for {pause} seconds before next account...")
        await asyncio.sleep(pause)

    except Exception as err:
        logger.error(f"{account_index} | Account flow failed: {err}")


async def wrapper(function, config: src.utils.config.Config, *args, **kwargs):
    attempts = config.SETTINGS.ATTEMPTS
    for attempt in range(attempts):
        result = await function(*args, **kwargs)
        if isinstance(result, tuple) and result and isinstance(result[0], bool):
            if result[0]:
                return result
        elif isinstance(result, bool):
            if result:
                return True

        if attempt < attempts - 1:  # Don't sleep after the last attempt
            pause = random.randint(
                config.SETTINGS.PAUSE_BETWEEN_ATTEMPTS[0],
                config.SETTINGS.PAUSE_BETWEEN_ATTEMPTS[1],
            )
            logger.info(
                f"Sleeping for {pause} seconds before next attempt {attempt+1}/{config.SETTINGS.ATTEMPTS}..."
            )
            await asyncio.sleep(pause)

    return result


async def random_sleep(config: dict, task: str, address: str):
    pause = random.randint(
        config.SETTINGS.RANDOM_PAUSE_BETWEEN_ACTIONS[0],
        config.SETTINGS.RANDOM_PAUSE_BETWEEN_ACTIONS[1],
    )
    logger.info(f"{address} | Sleeping for {pause} seconds after {task}...")
    await asyncio.sleep(pause)
