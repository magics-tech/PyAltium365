# PyAltium365 test harness

Local FastAPI + HTMX developer UI for exercising `AltiumApi`, workspace service discovery, vault browsing, and `JsonConSearchAsync` against a live Altium 365 tenant.

## Setup

```bash
cd PyAltium365
pip install -e ".[dev]" -r requirements.txt
```

Create a `.env` file (or export variables) with portal credentials:

```env
ALTIUM_USER=your@email
ALTIUM_PASS=your-password
ALTIUM_TOTP_SECRET=your-base32-authenticator-key
```

`ALTIUM_TOTP_SECRET` is the base32 key shown when setting up your authenticator app (the same value you would scan from a QR code). It is as sensitive as your password. Workspace connect uses it to generate TOTP codes automatically when Altium requires MFA.

## Run the harness

```bash
python -m test_interface
```

Open [http://127.0.0.1:8765](http://127.0.0.1:8765). The server binds to `127.0.0.1` only.

Equivalent via Nox:

```bash
nox -s harness
```

## Slice map

| Slice | UI / API | Library surface |
|-------|----------|-----------------|
| 0 | Portal login, status | `AltiumApi.login`, `get_user_workspaces` |
| 1 | Workspace picker, service URL table | `login_workspace`, `SoapyConServiceDiscovery` |
| 2 | Vault folder tree, item list, GUID lookup | `AltiumApiWorkspace` vault helpers |
| 3 | Search builder, count, paginated results | `JsonConSearchAsync` |
| 4 | Scenario export/import, request trace | `HarnessSession.export_scenario` / trace ring buffer |

## Tests

Unit tests (no network):

```bash
pytest test_interface/tests tests -m "not integration" -v
```

Live integration smoke (skipped when credentials are missing):

```bash
pytest -m integration -v
```

```bash
nox -s integration
```

## Architecture

Routes stay thin; orchestration lives in `test_interface/app/session.py` (`HarnessSession`). The UI never calls `AltiumApi` directly. HTTP calls made through `ConnectionHandler` are recorded in a trace ring buffer for debugging.
