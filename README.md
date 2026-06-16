# PyAltium365

Python client for Altium 365 (portal SOAP, workspace service discovery, vault, JSON searchasync, and Components REST).

**Documentation:** [docs/README.md](docs/README.md) · [architecture](docs/architecture.md) · [usage](docs/usage.md) · [AI index](AGENTS.md)

Primary consumer: [AutomatedAltiumSystem](../AutomatedAltiumSystem/) (MagHub Altium worker).

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

Then open **http://127.0.0.1:8765** and log in with `ALTIUM_USER` / `ALTIUM_PASS` from your environment or `.env`.

See [docs/test-harness.md](docs/test-harness.md) for setup, slice map, and integration test markers.

## Tests

```bash
pytest test_interface/tests tests -m "not integration" -v
pytest -m integration -v   # requires ALTIUM_USER / ALTIUM_PASS
```
