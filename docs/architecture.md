# PyAltium365 architecture

## Overview

PyAltium365 reverse-engineers the Altium 365 web client protocol stack. It is **not** an official Altium SDK. The library speaks the same SOAP, JSON, and REST endpoints the browser uses.

```text
AltiumApi (portal)
    │
    ├─ SoapyConPortal          → portal login, global service URLs
    ├─ SoapyConWorkspace       → list user workspaces
    │
    └─ login_workspace()
            │
            ▼
    SoapyConServiceDiscovery   → workspace session, regional service URLs
            │
            ▼
    AltiumApiWorkspace
            ├─ JsonConSearchAsync     → searchasync JSON API (components, projects, …)
            ├─ SoapConVault           → folder tree, item GUID lookup
            ├─ ComponentsApiClient    → GET …/components/api/components (REST)
            └─ AltiumIdentityOAuth    → auth.altium.com tokens for REST
```

All HTTP traffic flows through a shared `ConnectionHandler` (`requests.Session` singleton). The developer test harness records calls in a trace ring buffer for debugging.

## Package layout

| Path | Responsibility |
|------|----------------|
| `altium_api.py` | Portal login, workspace list, `login_workspace()` |
| `altium_api_workspace.py` | Per-workspace facade: search, vault, components client |
| `connection/soapy_con_*.py` | SOAP/XML portal and workspace calls |
| `connection/json_con_search_async.py` | Typed search builder + paginated `SearchDataBase` results |
| `connection/components/components_api.py` | Components REST list, `list_recent`, `find_by_hrid` |
| `connection/oauth/altium_identity_oauth.py` | Browser-style OAuth against `auth.altium.com` |
| `connection/rest_list_client.py` | Generic paginated REST list helper |
| `connection/vault/` | Vault folder/item SOAP access |
| `base/connection_handler.py` | Shared HTTP session |
| `base/field_encoding.py` | Altium field-name suffix encoding for search/REST |

## Authentication

### Portal login

`AltiumApi.login(username, password)` calls the portal SOAP endpoint and stores a session GUID. `get_user_workspaces()` returns `UserWorkspaceInfo` objects with hosting URLs.

### Workspace login

`login_workspace(workspace_url, username, password)` runs service discovery against the workspace host, establishing a workspace session GUID used by search and vault calls.

### OAuth for REST

The Components REST API (`/components/api/components`) expects browser-style auth. By default `login_workspace(..., use_oauth_for_rest=True)` runs `AltiumIdentityOAuth.login_with_password()`, which completes the `auth.altium.com` redirect dance and stores cookies on the shared session.

For headless/service accounts you can pass refresh-token credentials instead:

```python
api.login_workspace(
    workspace_url,
    username,
    password,
    oauth_refresh_token="…",
    oauth_client_id="…",
    oauth_client_secret="…",
)
```

TOTP (`oauth_totp_code`) is supported when the tenant requires MFA.

## API surfaces

### Components REST (preferred for listing)

`AltiumApiWorkspace.create_components_client()` returns a `ComponentsApiClient` pointed at:

```text
{workspace_url}/components/api/components
```

Service discovery's `Library.Components.Api` regional gateway URL is **not** used — it exposes a different contract than the workspace endpoint above.

| Method | Use |
|--------|-----|
| `iter_pages(query)` | Full paginated scan |
| `list_recent(updated_after)` | Incremental poll sorted by Update Date descending |
| `find_by_hrid(hrid)` | Single-component lookup |

`ComponentRecord` fields: `item_guid`, `hrid`, `update_date`, `description`, `comment`, `revision_state`.

### JSON searchasync

`workspace.create_search_object()` returns `JsonConSearchAsync`. Build queries with typed condition objects, restrict content type via `SearchDataType`, then call `get_results()` or `get_results_page()`.

`SearchDataBase` carries `item_guid`, `hrid`, `folder_full_path`, `life_cycle`, `revision_id`, `parameters`, and related metadata. Use this when you need rich parameter facets or non-component content types.

### Vault SOAP

`get_all_folders()`, `get_items_in_folder()`, `get_item_from_guid()` expose the workspace vault tree. Useful for folder navigation and GUID resolution; less efficient than REST for bulk component listing.

## Field encoding

Altium encodes field names with GUID suffixes in search and REST payloads. `base/field_encoding.py` maps human-readable names (e.g. `"Update Date"`) to wire names. `ComponentsApiClient` and `JsonConSearchAsync` apply encoding automatically.

## Testing

| Layer | Location |
|-------|----------|
| Unit tests | `tests/` — mocked HTTP, no credentials |
| Integration | `tests/integration/` — live tenant; marker `integration` |
| Browser harness | `test_interface/` — see [test-harness.md](test-harness.md) |

```bash
pytest tests test_interface/tests -m "not integration" -v
pytest -m integration -v   # requires ALTIUM_USER / ALTIUM_PASS
```

## Versioning and stability

The package is **pre-alpha** (`Development Status :: 2 - Pre-Alpha`). Altium may change wire protocols without notice. AutomatedAltiumSystem pins an editable sibling install; pin a git SHA in production workers.
