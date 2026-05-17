from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path

_ADDRESS_RE = re.compile(r"^0x[a-fA-F0-9]{40}$")
_LIVE_ACK = "I_UNDERSTAND_POLYMARKET_LIVE_ORDER_RISK"


def redact_secret(value: str) -> str:
    if not value:
        return ""
    if len(value) <= 4:
        return "****"
    return f"{value[:4]}…{value[-3:]}"


@dataclass(frozen=True)
class DepositWalletConfig:
    builder_api_key: str = ""
    deposit_wallet_address: str = ""
    live_trading_enabled: bool = False
    live_trading_ack: str = ""

    def __post_init__(self) -> None:
        if self.deposit_wallet_address and not _ADDRESS_RE.match(self.deposit_wallet_address):
            raise ValueError("deposit_wallet_address must be a 0x-prefixed 20-byte EVM address")
        if self.live_trading_enabled and self.live_trading_ack != _LIVE_ACK:
            raise ValueError(
                "live_trading_enabled requires LIVE_POLYMARKET_TRADING_ACK="
                f"{_LIVE_ACK!r}; v0 should remain paper-only"
            )

    def safe_summary(self) -> dict[str, object]:
        return {
            "builder_api_key": redact_secret(self.builder_api_key),
            "deposit_wallet_address": self.deposit_wallet_address,
            "live_trading_enabled": self.live_trading_enabled,
        }


@dataclass(frozen=True)
class AppConfig:
    mode: str
    deposit_wallet: DepositWalletConfig


def load_config(path: str | Path) -> AppConfig:
    data = tomllib.loads(Path(path).read_text())
    wallet = data.get("deposit_wallet", {})
    runtime = data.get("runtime", {})
    return AppConfig(
        mode=runtime.get("mode", "paper"),
        deposit_wallet=DepositWalletConfig(
            builder_api_key=wallet.get("builder_api_key", ""),
            deposit_wallet_address=wallet.get("deposit_wallet_address", ""),
            live_trading_enabled=bool(wallet.get("live_trading_enabled", False)),
            live_trading_ack=wallet.get("live_trading_ack", ""),
        ),
    )
