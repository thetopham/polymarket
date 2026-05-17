# Polymarket Deposit Wallet Notes

Source: https://docs.polymarket.com/trading/deposit-wallets

V0 interpretation for this repo:

- Deposit wallet is stored as config metadata for future integration only.
- The address you supplied is configured in `configs/paper.example.toml`.
- The supplied API key is treated as an identifier and is redacted in operator output.
- No API secret, private key, session signer, relayer URL, RPC URL, or live order path is implemented.

Important Polymarket deposit-wallet details:

- New direct API users use a deposit wallet, not the older Safe/proxy path.
- Deposit wallets hold pUSD and conditional tokens.
- Funding must go to the deposit wallet address, not merely the owner EOA.
- Approvals must be submitted from the deposit wallet via relayer `WALLET` batches.
- CLOB balance sync for this flow uses `signature_type = 3`.
- Orders use `POLY_1271` / `signatureType = 3` with deposit wallet as funder/maker/signer.
- Deposit-wallet batch signatures and CLOB order signatures are different and not interchangeable.

Approval boundary:

Before this repo ever gets live trading support, require an explicit separate change that adds:

1. Secret loading from a local ignored `.env`, never from committed config.
2. A doctor check that prints only set/unset booleans.
3. Dry-run tests proving no order/relayer route is reachable in paper mode.
4. Separate user approval for wallet deployment, approvals, balance sync, and order posting.
