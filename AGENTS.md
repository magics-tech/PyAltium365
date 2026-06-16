# PyAltium365 — AI index

**Purpose:** Unofficial Python client for Altium 365 portal, workspace, vault, search, and Components REST APIs.

**Repo:** `git@github.com:krakdustten/PyAltium365.git`

**Consumer:** [AutomatedAltiumSystem](../AutomatedAltiumSystem/) (`pip install -e ../PyAltium365`).

## Run locally

```bash
pip install -e ".[dev]" -r requirements.txt
pytest tests test_interface/tests -m "not integration" -v
python -m test_interface   # browser harness on :8765
```

Live tests: `pytest -m integration -v` (needs `ALTIUM_USER`, `ALTIUM_PASS`).

## Layout

| Path | Contents |
|------|----------|
| `src/py_altium365/altium_api.py` | `AltiumApi` — portal login, workspace connect |
| `src/py_altium365/altium_api_workspace.py` | `AltiumApiWorkspace` — search, vault, components |
| `src/py_altium365/connection/components/` | `ComponentsApiClient`, `ComponentRecord` |
| `src/py_altium365/connection/json_con_search_async.py` | `JsonConSearchAsync`, `SearchDataBase`, `SearchDataType` |
| `src/py_altium365/connection/oauth/` | `AltiumIdentityOAuth` for REST auth |
| `src/py_altium365/connection/vault/` | SOAP vault folder/item access |
| `src/py_altium365/connection/soapy_con_*.py` | Portal/workspace SOAP |
| `src/py_altium365/base/connection_handler.py` | Shared `requests` session |
| `test_interface/` | FastAPI + HTMX developer harness |
| `tests/` | Unit + integration tests |

## Entry points

```python
from py_altium365.altium_api import AltiumApi

api = AltiumApi()
api.login(user, password)
workspace = api.login_workspace(workspace_url, user, password)

client = workspace.create_components_client()   # REST list
search = workspace.create_search_object()       # JSON searchasync
```

## Docs

| Document | Topic |
|----------|--------|
| [README.md](README.md) | Install, tests, harness link |
| [docs/architecture.md](docs/architecture.md) | Protocol layers, auth, API surfaces |
| [docs/usage.md](docs/usage.md) | Code examples |
| [docs/test-harness.md](docs/test-harness.md) | Browser UI slices |

## Conventions

- Workspace Components REST URL is `{workspace}/components/api/components` — not the regional gateway from service discovery.
- `login_workspace(..., use_oauth_for_rest=True)` is required for REST; uses `auth.altium.com` OAuth or refresh tokens.
- Field names in queries are human-readable; encoding happens in clients.
- Pre-alpha: wire protocol may change; pin git SHA when deploying workers.
