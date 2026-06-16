# PyAltium365 usage guide

## Install

```bash
git clone git@github.com:krakdustten/PyAltium365.git
cd PyAltium365
pip install -e .
```

Developer extras (test harness, Nox):

```bash
pip install -e ".[dev]" -r requirements.txt
```

From **AutomatedAltiumSystem**, the sibling path is installed automatically:

```text
# requirements.txt
-e ../PyAltium365
```

## Credentials

Set environment variables or pass values directly:

| Variable | Purpose |
|----------|---------|
| `ALTIUM_USER` | Portal username |
| `ALTIUM_PASS` | Portal password |

Optional workspace URL can be passed to `login_workspace()` or discovered via `get_user_workspaces()`.

## Portal login and workspace selection

```python
from py_altium365.altium_api import AltiumApi

api = AltiumApi()
if api.login("user@example.com", "secret") is not True:
    raise RuntimeError("portal login failed")

for ws in api.get_user_workspaces():
    print(ws.name, ws.hosting_url)

workspace = api.login_workspace(ws.hosting_url, "user@example.com", "secret")
if workspace is None:
    raise RuntimeError("workspace login failed")
```

## List components (REST)

```python
from py_altium365.connection.components.components_api import ComponentsQuery

client = workspace.create_components_client()

# Full scan (paginated)
for record in client.iter_pages(ComponentsQuery(), page_size=500):
    print(record.hrid, record.revision_state, record.update_date)

# Incremental poll
from datetime import datetime, timedelta
since = datetime.utcnow() - timedelta(hours=1)
recent = client.list_recent(since, max_items=200)

# Lookup by HRID
cmp = client.find_by_hrid("CMP-0001234")
```

## Search components (JSON searchasync)

```python
from py_altium365.connection.json_con_search_async import JsonConSearchAsync, SearchDataType

search = workspace.create_search_object()
search.add_content_search_parameter(SearchDataType.COMPONENT)
search.set_free_text("resistor 0402")
results = search.get_results(max_amount=50)

for item in results:
    print(item.item_hrid, item.folder_full_path, item.life_cycle)
```

## Vault browsing

```python
folders = workspace.get_all_folders()
for folder in folders[:5]:
    items = workspace.get_items_in_folder(folder)
    print(folder.name, len(items))

item = workspace.get_item_from_guid("00000000-0000-0000-0000-000000000000")
```

## OAuth refresh token (service accounts)

```python
workspace = api.login_workspace(
    "https://your-workspace.365.altium.com",
    username,
    password,
    oauth_refresh_token="…",
    oauth_client_id="…",
    oauth_client_secret="…",
    use_oauth_for_rest=True,
)
```

## Explore interactively

Run the browser harness instead of ad-hoc scripts:

```bash
python -m test_interface
# → http://127.0.0.1:8765
```

See [test-harness.md](test-harness.md).

## Error handling

- `login()` returns `False` or an error string when `return_message=True`.
- `login_workspace()` returns `None` on failure.
- `AltiumApiWorkspace` raises `ConnectionError` when service discovery fails or required service URLs are missing.
- REST and search methods propagate HTTP errors from `requests`.

Always check return values before using a workspace object in production code.
