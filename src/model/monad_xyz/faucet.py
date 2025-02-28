import asyncio
from typing import Dict, List
from patchright.async_api import async_playwright
from loguru import logger
import random
import primp
from src.utils.config import Config
from eth_account import Account
import os
from pathlib import Path
import tempfile
import uuid


def get_random_user_agent():
    chrome_versions = [
        "123.0.0.0",
        "124.0.0.0",
        "125.0.0.0",
        "126.0.0.0",
        "127.0.0.0",
        "128.0.0.0",
        "129.0.0.0",
        "130.0.0.0",
        "131.0.0.0",
        "132.0.0.0",
        "133.0.0.0",
    ]

    platforms = [
        ("Windows NT 10.0; Win64; x64", "Windows"),
        ("Macintosh; Intel Mac OS X 10_15_7", "macOS"),
        ("X11; Linux x86_64", "Linux"),
    ]

    platform, os_name = random.choice(platforms)
    chrome_version = random.choice(chrome_versions)

    return f"Mozilla/5.0 ({platform}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Safari/537.36", chrome_version


def get_random_viewport() -> Dict[str, int]:
    resolutions = [
        {"width": 1920, "height": 1080},
        {"width": 1366, "height": 768},
        {"width": 1536, "height": 864},
        {"width": 1440, "height": 900},
        {"width": 1280, "height": 720},
    ]
    return random.choice(resolutions)


def get_random_timezone() -> str:
    timezones = [
        "America/New_York",
        "America/Chicago",
        "America/Los_Angeles",
        "America/Phoenix",
        "Europe/London",
        "Europe/Paris",
        "Europe/Berlin",
        "Asia/Tokyo",
        "Asia/Singapore",
        "Australia/Sydney",
    ]
    return random.choice(timezones)


def get_random_launch_args(capsolver_path: str) -> List[str]:
    base_args = [
        "--disable-blink-features=AutomationControlled",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--password-store=basic",
        "--use-mock-keychain",
        "--disable-software-rasterizer",
        "--disable-gpu-sandbox",
        "--no-default-browser-check",
        "--allow-running-insecure-content",
    ]

    optional_args = [
        "--disable-web-security",
        "--disable-features=IsolateOrigins,site-per-process",
        "--disable-site-isolation-trials",
        "--disable-setuid-sandbox",
        "--ignore-certificate-errors",
        "--disable-accelerated-2d-canvas",
        "--disable-bundled-ppapi-flash",
        "--disable-logging",
        "--disable-notifications",
    ]

    # Randomly select 2-4 optional arguments
    selected_optional = random.sample(optional_args, random.randint(2, 4))

    # Add extension-specific arguments
    extension_args = [
        f"--disable-extensions-except={capsolver_path}",
        f"--load-extension={capsolver_path}",
        "--lang=en-US",
    ]

    viewport = get_random_viewport()
    window_size_arg = [f"--window-size={viewport['width']},{viewport['height']}"]

    return base_args + selected_optional + extension_args + window_size_arg


async def faucet(
    session: primp.AsyncClient,
    account_index: int,
    config: Config,
    wallet: Account,
    proxy: str,
) -> bool:
    for retry in range(config.SETTINGS.ATTEMPTS):
        try:
            capsolver_path = os.path.join(os.path.dirname(__file__), "capsolver")

            proxy_parts = proxy.split("@")
            auth = proxy_parts[0].split(":")
            proxy_options = {
                "server": f"http://{proxy_parts[1]}",
                "username": auth[0],
                "password": auth[1],
            }

            # Get random browser settings
            user_agent, chrome_version = get_random_user_agent()
            viewport = get_random_viewport()
            launch_args = get_random_launch_args(capsolver_path)

            async with async_playwright() as p:
                # Launch browser with enhanced settings
                browser = await p.chromium.launch_persistent_context(
                    user_data_dir=os.path.join(tempfile.gettempdir(), f"chrome_profile_{str(uuid.uuid4())}"),
                    channel="chrome",
                    proxy=proxy_options,
                    viewport=viewport,
                    user_agent=user_agent,
                    headless=False,
                    args=launch_args,
                    ignore_https_errors=True,
                    locale="en-US",
                    timezone_id="UTC",
                    bypass_csp=True,
                    accept_downloads=True,
                    timeout=int(30000 * config.SETTINGS.BROWSER_PAUSE_MULTIPLIER),
                )
                    
                # Create new page and navigate
                page = await browser.new_page()
                
                # Set custom headers
                await page.set_extra_http_headers({
                    "accept": "*/*",
                    "accept-language": "en-US,en;q=0.9",
                    "sec-ch-ua": f'"Chromium";v="{chrome_version}", "Google Chrome";v="{chrome_version}"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": '"Windows"',
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "cross-site",
                })
                
                await page.goto("https://testnet.monad.xyz/")

                await asyncio.sleep(5 * config.SETTINGS.BROWSER_PAUSE_MULTIPLIER)

                # 1. Click terms checkbox
                await page.click(
                    'button[role="checkbox"][aria-label="Accept terms and conditions"]',
                    timeout=int(30000 * config.SETTINGS.BROWSER_PAUSE_MULTIPLIER)
                )
                await asyncio.sleep(2 * config.SETTINGS.BROWSER_PAUSE_MULTIPLIER)

                # 2. Click Continue button
                await page.click(
                    'button:has-text("Continue")',
                    timeout=int(30000 * config.SETTINGS.BROWSER_PAUSE_MULTIPLIER)
                )
                
                # 3. Wait for captcha solving
                logger.info(f"[{account_index}] Waiting 30 seconds for captcha solving...")
                await asyncio.sleep(30 * config.SETTINGS.BROWSER_PAUSE_MULTIPLIER)

                # 4. Input wallet address
                await page.fill(
                    'input[placeholder*="0x8ce78"]',
                    wallet.address,
                    timeout=int(30000 * config.SETTINGS.BROWSER_PAUSE_MULTIPLIER)
                )
                
                # 5. Wait before clicking Get Testnet MON
                await asyncio.sleep(10 * config.SETTINGS.BROWSER_PAUSE_MULTIPLIER)

                # 6. Click Get Testnet MON button
                for _ in range(3):
                    await page.click(
                        'button:has-text("Get Testnet MON")',
                        timeout=int(30000 * config.SETTINGS.BROWSER_PAUSE_MULTIPLIER)
                    )
                    await asyncio.sleep(1 * config.SETTINGS.BROWSER_PAUSE_MULTIPLIER)


                logger.success(f"[{account_index}] Claimed tokens from faucet monad.xyz")

                await browser.close()
                return True

        except Exception as e:
            try:
                await browser.close()
            except:
                pass

            random_pause = random.randint(
                config.SETTINGS.PAUSE_BETWEEN_ATTEMPTS[0],
                config.SETTINGS.PAUSE_BETWEEN_ATTEMPTS[1],
            )
            logger.error(
                f"[{account_index}] | Error faucet to monad.xyz ({retry + 1}/{config.SETTINGS.ATTEMPTS}): {e}. Next faucet in {random_pause} seconds"
            )
            await asyncio.sleep(random_pause)
            continue
            
    return False


