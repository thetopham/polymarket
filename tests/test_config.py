from polyhedge.config.settings import DepositWalletConfig, load_config, redact_secret


def test_deposit_wallet_config_redacts_secret_and_keeps_public_fields():
    cfg = DepositWalletConfig(
        builder_api_key="019e33b9-871b-749b-81b6-d3844ae5a76a",
        deposit_wallet_address="0xc8dd2a8c0765160989ca5d3d432d74950a4e3952",
        live_trading_enabled=False,
    )

    safe = cfg.safe_summary()

    assert safe["builder_api_key"] == "019e…76a"
    assert safe["deposit_wallet_address"] == "0xc8dd2a8c0765160989ca5d3d432d74950a4e3952"
    assert safe["live_trading_enabled"] is False


def test_invalid_deposit_wallet_address_is_rejected():
    try:
        DepositWalletConfig(
            builder_api_key="019e33b9-871b-749b-81b6-d3844ae5a76a",
            deposit_wallet_address="not-an-address",
        )
    except ValueError as exc:
        assert "deposit_wallet_address" in str(exc)
    else:
        raise AssertionError("invalid address should fail")


def test_live_trading_requires_explicit_second_ack():
    try:
        DepositWalletConfig(
            builder_api_key="019e33b9-871b-749b-81b6-d3844ae5a76a",
            deposit_wallet_address="0xc8dd2a8c0765160989ca5d3d432d74950a4e3952",
            live_trading_enabled=True,
            live_trading_ack="paper-only",
        )
    except ValueError as exc:
        assert "LIVE_POLYMARKET_TRADING_ACK" in str(exc)
    else:
        raise AssertionError("live trading should require explicit acknowledgement")


def test_load_config_from_toml(tmp_path):
    path = tmp_path / "config.toml"
    path.write_text(
        "\n".join(
            [
                "[deposit_wallet]",
                'builder_api_key = "019e33b9-871b-749b-81b6-d3844ae5a76a"',
                'deposit_wallet_address = "0xc8dd2a8c0765160989ca5d3d432d74950a4e3952"',
                "[runtime]",
                'mode = "paper"',
            ]
        )
    )

    cfg = load_config(path)

    assert cfg.deposit_wallet.deposit_wallet_address.endswith("e3952")
    assert cfg.mode == "paper"


def test_redact_secret_handles_short_and_empty_values():
    assert redact_secret("") == ""
    assert redact_secret("abcd") == "****"
    assert redact_secret("abcdefghijk") == "abcd…ijk"
