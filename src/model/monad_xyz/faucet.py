import asyncio
from loguru import logger
import random
import primp
from src.utils.config import Config
from eth_account import Account
import hashlib
from pynocaptcha import CloudFlareCracker, TlsV1Cracker


async def faucet(
    session: primp.AsyncClient,
    account_index: int,
    config: Config,
    wallet: Account,
    proxy: str,
) -> bool:
    for retry in range(config.SETTINGS.ATTEMPTS):
        try:
            logger.info(f"[{account_index}] | Starting faucet for account {wallet.address}...")
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
            href = "https://testnet.monad.xyz/"

            # First get the Vercel challenge token
            response = await session.post(
                "http://api.nocaptcha.io/api/wanda/vercel/universal",
                headers={
                    "User-Token": config.FAUCET.NOCAPTCHA_API_KEY,
                    "Developer-Id": "SWVtru",
                    },
                json={
                    "href": href,
                    "user_agent": user_agent,
                    "proxy": proxy,
                    "timeout": 30,
                },
            )

            vercel_resp = response.json()

            if vercel_resp.get("status") != 1:
                raise Exception(
                    f"Failed to solve Vercel challenge: {vercel_resp.get('msg')}"
                )

            extra = vercel_resp["extra"]

            # Prepare headers with Vercel token - exactly matching working example
            headers = {
                "sec-ch-ua": extra["sec-ch-ua"],
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": extra["sec-ch-ua-platform"],
                "upgrade-insecure-requests": "1",
                "user-agent": extra["user-agent"],
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "sec-fetch-site": "same-origin",
                "sec-fetch-mode": "navigate",
                "sec-fetch-dest": "document",
                "referer": href,
                "accept-encoding": "gzip, deflate, br, zstd",
                "accept-language": extra["accept-language"],
                "cookie": "_vcrcs=" + vercel_resp["data"]["_vcrcs"],
                "priority": "u=0, i",
            }

            # Solve Cloudflare challenge - matching working example configuration
            logger.info(f"[{account_index}] | Solving Cloudflare challenge...")
            cracker = CloudFlareCracker(
                internal_host=True,
                user_token=config.FAUCET.NOCAPTCHA_API_KEY,
                href=href,
                sitekey="0x4AAAAAAA-3X4Nd7hf3mNGx",
                proxy=proxy,
                debug=False,
                show_ad=False,
                timeout=60,
            )
            cf_result = cracker.crack()

            if not cf_result or "token" not in cf_result:
                raise Exception("Failed to solve Cloudflare challenge")

            logger.success(f"[{account_index}] | Cloudflare challenge solved")

            # Generate visitor ID the same way as working example
            visitor_id = hashlib.md5(str(random.random()).encode()).hexdigest()

            json_data = {
                "address": wallet.address,
                "visitorId": visitor_id,
                "cloudFlareResponseToken": cf_result["token"],
            }

            # Make claim request using TlsV1Cracker - matching working example configuration
            logger.info(f"[{account_index}] | Sending claim request...")
            claim_result = TlsV1Cracker(
                show_ad=False,
                user_token=config.FAUCET.NOCAPTCHA_API_KEY,
                url=f"{href}api/claim",
                method="post",
                headers=headers,
                json=json_data,
                http2=True,
                proxy=proxy,
                debug=False,
            ).crack()

            if not claim_result:
                raise Exception("Failed to send claim request")

            response_text = claim_result.get("response", {}).get("text", "")

            if "Claimed already" in response_text:
                logger.success(
                    f"[{account_index}] | Already claimed tokens from faucet"
                )
                return True

            if '"message":"Success"' in response_text:
                logger.success(
                    f"[{account_index}] | Successfully got tokens from faucet"
                )
                return True
            else:
                if "FUNCTION_INVOCATION_TIMEOUT" in response_text:
                    logger.error(
                        f"[{account_index}] | Failed to get tokens from faucet: server is not responding, wait..."
                    )
                elif 'Vercel Security Checkpoint' in response_text:
                    logger.error(
                        f"[{account_index}] | Failed to solve Vercel challenge, trying again..."
                    )
                    continue
                elif "Server error on QuickNode API" in response_text:
                    logger.error(
                        f"[{account_index}] | FAUCET DOES NOT WORK, QUICKNODE IS DOWN"
                    )
                elif "Over Enterprise free quota" in response_text:
                    logger.error(
                        f"[{account_index}] | MONAD IS SHIT, FAUCET DOES NOT WORK, TRY LATER"
                    )
                    return False
                elif "invalid-keys" in response_text:
                    logger.error(
                        f"[{account_index}] | PLEASE UPDATE THE BOT USING GITHUB"
                    )
                    return False
                else:
                    logger.error(
                        f"[{account_index}] | Failed to get tokens from faucet: {response_text}"
                    )
                await asyncio.sleep(3)

        except Exception as e:
            random_pause = random.randint(
                config.SETTINGS.RANDOM_PAUSE_BETWEEN_ACTIONS[0],
                config.SETTINGS.RANDOM_PAUSE_BETWEEN_ACTIONS[1],
            )
            logger.error(
                f"[{account_index}] | Error faucet to monad.xyz ({retry + 1}/{config.SETTINGS.ATTEMPTS}): {e}. Next faucet in {random_pause} seconds"
            )
            await asyncio.sleep(random_pause)
            continue
    return False
