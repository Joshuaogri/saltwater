"""Inventory every compressed Saltwater property/business source collection.

This is a read-only package inspection tool. It does not connect to PostgreSQL.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path

DATASETS = {
    "SW-PROPERTY-WORLD-V1": "data/property/saltwater-property-world-v1.json.gz",
    "SW-BUSINESS-REGISTRY-V1": "data/business/saltwater-business-registry-v1.json.gz",
    "SW-BUSINESS-OPERATIONS-V1": "data/business/saltwater-business-operations-v1.json.gz",
    "SW-BUILDING-SERVICES-V1": "data/property/saltwater-building-services-v1.json.gz",
    "SW-PROPERTY-DEVELOPMENT-CONTROL-V1": "data/property/saltwater-property-development-control-v1.json.gz",
    "SW-PROPERTY-FACILITIES-OPERATIONS-V1": "data/property/saltwater-property-facilities-operations-v1.json.gz",
    "SW-PROPERTY-INSURANCE-CLAIMS-V1": "data/property/saltwater-property-insurance-claims-v1.json.gz",
    "SW-PROPERTY-LIFECYCLE-TRANSACTIONS-V1": "data/property/saltwater-property-lifecycle-transactions-v1.json.gz",
    "SW-PROPERTY-MAINTENANCE-V1": "data/property/saltwater-property-maintenance-v1.json.gz",
    "SW-PROPERTY-RIGHTS-BOUNDARIES-V1": "data/property/saltwater-property-rights-boundaries-v1.json.gz",
    "SW-PROPERTY-SECURITY-ACCESS-V1": "data/property/saltwater-property-security-access-v1.json.gz",
    "SW-PROPERTY-TENURE-V1": "data/property/saltwater-property-tenure-v1.json.gz",
    "SW-PROPERTY-VALUE-RISK-TAX-V1": "data/property/saltwater-property-value-risk-tax-v1.json.gz",
    "SW-PROPERTY-GLOBAL-ESTATE-CAPACITY-AUDIT-V1": "data/property/saltwater-global-estate-capacity-audit-v1.json.gz",
}


def inspect_dataset(root: Path, dataset_id: str, relative_path: str) -> dict:
    path = root / relative_path
    raw = path.read_bytes()
    payload = gzip.decompress(raw) if path.suffix == ".gz" else raw
    document = json.loads(payload)
    if document.get("storage_format") != "textual_json_columnar_v1":
        raise ValueError(f"{relative_path}: unsupported storage format")
    metadata = document.get("metadata")
    if not isinstance(metadata, dict) or metadata.get("dataset_id") != dataset_id:
        raise ValueError(f"{relative_path}: dataset identity mismatch; expected={dataset_id!r}, found={metadata.get('dataset_id')!r}")
    tables = document.get("tables")
    if not isinstance(tables, dict):
        raise ValueError(f"{relative_path}: tables must be an object")

    collections = []
    total_rows = 0
    for collection_name, collection in sorted(tables.items()):
        if not isinstance(collection, dict):
            raise ValueError(f"{relative_path}:{collection_name}: collection must be an object")
        columns, values = collection.get("columns"), collection.get("rows")
        if not isinstance(columns, list) or not all(isinstance(c, str) for c in columns):
            raise ValueError(f"{relative_path}:{collection_name}: invalid columns")
        if len(columns) != len(set(columns)):
            raise ValueError(f"{relative_path}:{collection_name}: duplicate column names")
        if not isinstance(values, list):
            raise ValueError(f"{relative_path}:{collection_name}: rows must be an array")
        for index, row in enumerate(values):
            if not isinstance(row, list) or len(row) != len(columns):
                raise ValueError(f"{relative_path}:{collection_name}[{index}]: column/row width mismatch")
        total_rows += len(values)
        collections.append({
            "collection": collection_name,
            "row_count": len(values),
            "column_count": len(columns),
            "columns": columns,
            "identity_columns": [c for c in columns if c == "id" or c.endswith("_id")],
        })
    return {
        "dataset_id": dataset_id,
        "source_path": relative_path,
        "compressed_bytes": len(raw),
        "uncompressed_bytes": len(payload),
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "collection_count": len(collections),
        "record_count": total_rows,
        "collections": collections,
    }


def build_inventory(root: Path) -> dict:
    datasets = [inspect_dataset(root, dataset_id, path) for dataset_id, path in DATASETS.items()]
    return {
        "inventory_version": "SW-BP04-SOURCE-INVENTORY-001",
        "dataset_count": len(datasets),
        "collection_count": sum(d["collection_count"] for d in datasets),
        "record_count": sum(d["record_count"] for d in datasets),
        "compressed_bytes": sum(d["compressed_bytes"] for d in datasets),
        "uncompressed_bytes": sum(d["uncompressed_bytes"] for d in datasets),
        "datasets": datasets,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = build_inventory(args.root)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
