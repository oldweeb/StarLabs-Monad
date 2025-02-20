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

    proxies = src.utils.read_txt_file("proxies", "data/proxies.txt")
    private_keys = src.utils.read_txt_file("private keys", "data/private_keys.txt")

    # Читаем токены только если соответствующие задачи есть в конфиге
    discord_tokens = (
        src.utils.read_txt_file("discord tokens", "data/discord_tokens.txt")
        if "connect_discord" in config.FLOW.TASKS
        else [""] * len(private_keys)
    )

    emails = (
        src.utils.read_txt_file("emails", "data/emails.txt")
        if config.FAUCET.THIRDWEB
        else [""] * len(private_keys)
    )

    threads = config.SETTINGS.THREADS

    if len(proxies) == 0:
        logger.error("No proxies found in data/proxies.txt")
        return

    proxies = [proxies[i % len(proxies)] for i in range(len(private_keys))]

    logger.info("Starting...")
    lock = asyncio.Lock()
    semaphore = asyncio.Semaphore(value=threads)
    tasks = []
    for index, private_key in enumerate(private_keys):
        proxy = proxies[index % len(proxies)]
        tasks.append(
            asyncio.create_task(
                launch_wrapper(
                    index,
                    proxy,
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
