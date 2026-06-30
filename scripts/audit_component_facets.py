#!/usr/bin/env python3
"""Audit Altium 365 workspace facet names against the Component Parameter Definition spec.

Requires ALTIUM_USER, ALTIUM_PASS, and optionally ALTIUM_WORKSPACE_URL.

Usage:
    python scripts/audit_component_facets.py
    python scripts/audit_component_facets.py --json report.json
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

# Allow running from repo root without install.
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "src"))

from py_altium365.altium_api import AltiumApi
from py_altium365.component_spec_catalog import (
    ALL_SPEC_PARAMETER_NAMES,
    AUDIT_FOLDER_PREFIXES,
)
from py_altium365.connection.json_con_search_async import SearchDataType


async def _audit(*, json_path: str | None) -> dict:
    user = os.environ.get("ALTIUM_USER")
    password = os.environ.get("ALTIUM_PASS")
    workspace_url = os.environ.get("ALTIUM_WORKSPACE_URL")
    if not user or not password:
        raise SystemExit("Set ALTIUM_USER and ALTIUM_PASS")

    api = AltiumApi()
    if api.login(user, password) is not True:
        raise SystemExit("Portal login failed")

    workspaces = api.get_user_workspaces()
    if not workspaces:
        raise SystemExit("No workspaces found")

    if workspace_url:
        ws_meta = next((w for w in workspaces if workspace_url.rstrip("/") in w.hosting_url), None)
        target_url = ws_meta.hosting_url if ws_meta else workspace_url
    else:
        target_url = workspaces[0].hosting_url

    workspace = api.login_workspace(target_url, user, password)
    if workspace is None:
        raise SystemExit("Workspace login failed")

    search = workspace.create_search_object()
    await search.add_content_search_parameter(SearchDataType.COMPONENT)
    facet_catalog = sorted(name for name, _ in await search.get_all_search_names_and_type())

    samples_by_folder: dict[str, list[dict]] = defaultdict(list)
    seen_hrids: set[str] = set()

    for prefix in AUDIT_FOLDER_PREFIXES:
        folder_search = workspace.create_search_object()
        await folder_search.add_content_search_parameter(SearchDataType.COMPONENT)
        folder_search.add_search_parameter_wildcard(prefix.split("/")[-1])
        results = await folder_search.get_results(max_amount=40)
        for result in results:
            path = (result.folder_full_path or "").replace("\\", "/")
            if prefix not in path and not path.endswith(prefix.split("/")[-1]):
                continue
            hrid = result.hrid or result.item_hrid
            if not hrid or hrid in seen_hrids:
                continue
            seen_hrids.add(hrid)
            keys = sorted(str(k) for k in result.parameters.keys())
            samples_by_folder[prefix].append(
                {
                    "hrid": hrid,
                    "folder": path,
                    "parameter_keys": keys,
                }
            )
            if len(samples_by_folder[prefix]) >= 3:
                break

    indexed_keys: set[str] = set(facet_catalog)
    for samples in samples_by_folder.values():
        for sample in samples:
            indexed_keys.update(sample["parameter_keys"])

    spec_missing_from_altium = sorted(ALL_SPEC_PARAMETER_NAMES - indexed_keys)
    altium_not_in_spec = sorted(
        k for k in indexed_keys if k not in ALL_SPEC_PARAMETER_NAMES and not k.endswith("_T@x^")
    )

    report = {
        "workspace_url": target_url,
        "facet_count": len(facet_catalog),
        "facet_catalog": facet_catalog,
        "samples_by_folder": dict(samples_by_folder),
        "spec_parameters_missing_from_altium_index": spec_missing_from_altium,
        "altium_facets_not_in_spec": altium_not_in_spec[:100],
    }

    if json_path:
        Path(json_path).write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"Wrote {json_path}")

    print(f"Workspace facets: {len(facet_catalog)}")
    print(f"Spec params not in Altium index: {len(spec_missing_from_altium)}")
    if spec_missing_from_altium[:20]:
        print("  sample:", ", ".join(spec_missing_from_altium[:20]))
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit Altium component facet names")
    parser.add_argument("--json", dest="json_path", default=None, help="Write JSON report path")
    args = parser.parse_args()
    asyncio.run(_audit(json_path=args.json_path))


if __name__ == "__main__":
    main()
