from dataclasses import dataclass

@dataclass
class RunConfiguration:
    proxy_file: str
    private_key_file: str
    task_preset: str