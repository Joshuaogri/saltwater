"""Read canonical BP04 datasets from their lossless compressed Neon archives.

The database stores gzip bytes once. Decompression and columnar row expansion happen
in the application process, not as duplicate permanent PostgreSQL rows.
"""
from __future__ import annotations

import gzip
import hashlib
import json
from typing import Any


def decode_archive(dataset_id: str, payload: bytes, expected_sha256: str) -> dict[str, Any]:
    actual = hashlib.sha256(payload).hexdigest()
    if actual != expected_sha256:
        raise ValueError(f"Archive digest mismatch for {dataset_id}: {actual}")
    try:
        document = json.loads(gzip.decompress(payload))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Invalid gzip JSON archive for {dataset_id}") from exc
    if document.get("metadata", {}).get("dataset_id") != dataset_id:
        raise ValueError(f"Dataset identity mismatch: expected {dataset_id}")
    if document.get("storage_format") != "textual_json_columnar_v1":
        raise ValueError(f"Unsupported dataset format for {dataset_id}")
    if not isinstance(document.get("tables"), dict):
        raise ValueError(f"Missing collection map for {dataset_id}")
    return document


def load_dataset(conn, dataset_id: str) -> dict[str, Any]:
    row = conn.execute(
        """SELECT a.compressed_payload, a.source_sha256
           FROM sw_property.source_dataset_archive a
           JOIN sw_property.import_dataset d ON d.source_sha256 = a.source_sha256
           JOIN sw_property.import_release r ON r.release_id = d.release_id
           WHERE d.dataset_id = %s
           ORDER BY r.imported_at DESC
           LIMIT 1""",
        (dataset_id,),
    ).fetchone()
    if row is None:
        raise KeyError(f"BP04 dataset not found: {dataset_id}")
    payload, digest = row
    return decode_archive(dataset_id, bytes(payload), digest)


def load_collection(conn, dataset_id: str, collection_name: str) -> list[dict[str, Any]]:
    document = load_dataset(conn, dataset_id)
    collection = document["tables"].get(collection_name)
    if collection is None:
        raise KeyError(f"Collection {dataset_id}.{collection_name} not found")
    columns, values = collection.get("columns"), collection.get("rows")
    if not isinstance(columns, list) or not isinstance(values, list):
        raise ValueError(f"Malformed collection {dataset_id}.{collection_name}")
    result = []
    for index, row in enumerate(values):
        if len(row) != len(columns):
            raise ValueError(f"Malformed row {dataset_id}.{collection_name}[{index}]")
        result.append(dict(zip(columns, row)))
    return result
