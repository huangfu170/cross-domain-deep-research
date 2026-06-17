#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None


SKIP_KEYS = {"_source_file", "uncertain"}


def load_yaml(path: Path):
    if yaml is None:
        raise RuntimeError("PyYAML is required to read fields.yaml")
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def iter_field_names(data):
    if isinstance(data, list):
        for item in data:
            yield from iter_field_names(item)
    elif isinstance(data, dict):
        if isinstance(data.get("name"), str) and (
            "description" in data or "detail_level" in data or "type" in data
        ):
            yield data["name"]
        for key, value in data.items():
            if key not in {"name", "description", "detail_level", "type"}:
                yield from iter_field_names(value)


def load_expected_fields(fields_path: Path):
    data = load_yaml(fields_path)
    candidates = []
    if "field_categories" in data:
        candidates.append(data["field_categories"])
    if "fields" in data:
        candidates.append(data["fields"])
    if not candidates:
        candidates.append(data)
    fields = []
    seen = set()
    for candidate in candidates:
        for name in iter_field_names(candidate):
            if name not in seen:
                seen.add(name)
                fields.append(name)
    return fields


def flatten_json(data, out=None):
    out = out or {}
    if isinstance(data, dict):
        for key, value in data.items():
            if key in SKIP_KEYS:
                continue
            if isinstance(value, dict):
                flatten_json(value, out)
            else:
                out[key] = value
    return out


def main():
    parser = argparse.ArgumentParser(description="Validate research JSON against fields.yaml")
    parser.add_argument("-f", "--fields", required=True, help="Path to fields.yaml")
    parser.add_argument("-j", "--json", required=True, help="Path to result JSON")
    args = parser.parse_args()

    fields_path = Path(args.fields)
    json_path = Path(args.json)

    expected = load_expected_fields(fields_path)
    with json_path.open("r", encoding="utf-8") as f:
        result = json.load(f)

    values = flatten_json(result)
    uncertain = set(result.get("uncertain", [])) if isinstance(result, dict) else set()
    missing = [name for name in expected if name not in values and name not in uncertain]

    if missing:
        print("Missing fields:")
        for name in missing:
            print(f"- {name}")
        return 1

    print(f"OK: {json_path} covers {len(expected)} fields")
    return 0


if __name__ == "__main__":
    sys.exit(main())
