# PyAltium365

Python client for Altium 365 (portal SOAP, workspace service discovery, vault, and JSON searchasync).

## Install

```bash
pip install -e .
```

Developer harness and test extras:

```bash
pip install -e ".[dev]" -r requirements.txt
```

## Developer test harness

Replace ad-hoc `tests/manual.py` runs with the browser UI:

```bash
python -m test_interface
```

Then open **http://127.0.0.1:8765** and log in with `ALTIUM_USER` / `ALTIUM_PASS` from your environment or `.env`. If your account uses authenticator-app MFA, also set `ALTIUM_TOTP_SECRET` to the base32 setup key (not the 6-digit code).

See [docs/test-harness.md](docs/test-harness.md) for setup, slice map, and integration test markers.

## Tests

```bash
pytest test_interface/tests tests -m "not integration" -v
pytest -m integration -v   # requires ALTIUM_USER / ALTIUM_PASS; workspace OAuth also needs ALTIUM_TOTP_SECRET when MFA is enabled
```
