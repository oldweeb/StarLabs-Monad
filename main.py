import argparse

from loguru import logger
import urllib3
import sys
import asyncio
import platform

from process import start
import src
from src.model.run_config.run_config import RunConfiguration


# SETTING POLICY FOR WINDOWS
# config = src.utils.get_config()
# using_playwright = 'faucet' in str(config.FLOW.TASKS) or 'dusted' in str(config.FLOW.TASKS)


# if not using_playwright:
# if platform.system() == "Windows":
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def main():
    run_configuration = configure()
    await start(run_configuration)


log_format = (
    "<light-blue>[</light-blue><yellow>{time:HH:mm:ss}</yellow><light-blue>]</light-blue> | "
    "<level>{level: <8}</level> | "
    "<cyan>{file}:{line}</cyan> | "
    "<level>{message}</level>"
)


def configure() -> RunConfiguration:
    urllib3.disable_warnings()
    logger.remove()
    logger.add(
        sys.stdout,
        colorize=True,
        format=log_format,
    )
    logger.add(
        "logs/app.log",
        rotation="10 MB",
        retention="1 month",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{line} - {message}",
        level="INFO",
    )
    args_parser = argparse.ArgumentParser(description='StarLabs Monad')
    args_parser.add_argument('-p', '--proxy', type=str, required=True, help='Path to the txt file with proxy')
    args_parser.add_argument('-pk', '--privatekey', type=str, required=True, help='Path to the private key file')
    args_parser.add_argument('-t', '--taskpreset', type=str, required=False, help='Task Preset', default='default')
    args = args_parser.parse_args()

    configuration = RunConfiguration(
        proxy_file=args.proxy,
        private_key_file=args.privatekey,
        task_preset=args.taskpreset
    )
    return configuration

if __name__ == "__main__":
    asyncio.run(main())
