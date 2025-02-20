from dataclasses import dataclass
from typing import List, Tuple, Optional
import yaml
from pathlib import Path
import asyncio


@dataclass
class SettingsConfig:
    THREADS: int
    ATTEMPTS: int
    PAUSE_BETWEEN_ATTEMPTS: Tuple[int, int]
    PAUSE_BETWEEN_SWAPS: Tuple[int, int]
    RANDOM_PAUSE_BETWEEN_ACCOUNTS: Tuple[int, int]
    RANDOM_PAUSE_BETWEEN_ACTIONS: Tuple[int, int]

@dataclass
class FlowConfig:
    TASKS: List[str]
    NUMBER_OF_SWAPS: Tuple[int, int]
    PERCENT_OF_BALANCE_TO_SWAP: Tuple[int, int]

@dataclass
class AprioriConfig:
    AMOUNT_TO_STAKE: Tuple[float, float]

@dataclass
class MagmaConfig:
    AMOUNT_TO_STAKE: Tuple[float, float]

@dataclass
class BimaConfig:
    LEND: bool
    PERCENT_OF_BALANCE_TO_LEND: Tuple[int, int]

@dataclass
class Config:
    SETTINGS: SettingsConfig
    FLOW: FlowConfig
    APRIORI: AprioriConfig
    MAGMA: MagmaConfig
    BIMA: BimaConfig
    lock: asyncio.Lock = asyncio.Lock()

    @classmethod
    def load(cls, path: str = "config.yaml") -> "Config":
        """Load configuration from yaml file"""
        with open(path, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)

        return cls(
            SETTINGS=SettingsConfig(
                THREADS=data["SETTINGS"]["THREADS"],
                ATTEMPTS=data["SETTINGS"]["ATTEMPTS"],
                PAUSE_BETWEEN_ATTEMPTS=tuple(
                    data["SETTINGS"]["PAUSE_BETWEEN_ATTEMPTS"]
                ),
                PAUSE_BETWEEN_SWAPS=tuple(
                    data["SETTINGS"]["PAUSE_BETWEEN_SWAPS"]
                ),
                RANDOM_PAUSE_BETWEEN_ACCOUNTS=tuple(
                    data["SETTINGS"]["RANDOM_PAUSE_BETWEEN_ACCOUNTS"]
                ),
                RANDOM_PAUSE_BETWEEN_ACTIONS=tuple(
                    data["SETTINGS"]["RANDOM_PAUSE_BETWEEN_ACTIONS"]
                ),
            ),
            FLOW=FlowConfig(
                TASKS=data["FLOW"]["TASKS"],
                NUMBER_OF_SWAPS=tuple(data["FLOW"]["NUMBER_OF_SWAPS"]),
                PERCENT_OF_BALANCE_TO_SWAP=tuple(data["FLOW"]["PERCENT_OF_BALANCE_TO_SWAP"]),
            ),
            APRIORI=AprioriConfig(
                AMOUNT_TO_STAKE=tuple(data["APRIORI"]["AMOUNT_TO_STAKE"]),
            ),
            MAGMA=MagmaConfig(
                AMOUNT_TO_STAKE=tuple(data["MAGMA"]["AMOUNT_TO_STAKE"]),
            ),
            BIMA=BimaConfig(
                LEND=data["BIMA"]["LEND"],
                PERCENT_OF_BALANCE_TO_LEND=tuple(data["BIMA"]["PERCENT_OF_BALANCE_TO_LEND"]),
            ),
        )


# Singleton pattern
def get_config() -> Config:
    """Get configuration singleton"""
    if not hasattr(get_config, "_config"):
        get_config._config = Config.load()
    return get_config._config
