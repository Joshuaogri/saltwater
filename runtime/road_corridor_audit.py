"""Width-agnostic road-corridor inventory and source QA for BP04-03.

This deliberately preserves source road centre-lines without manufacturing
right-of-way widths, road-edge polygons, reserve areas or parcel frontage.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict, deque
from pathlib import Path


def _polyline_length(points):
    return sum(
        ((points[i][0] - points[i - 1][0]) ** 2
         + (points[i][1] - points[i - 1][1]) ** 2) ** 0.5
        for i in range(1, len(points))
    )


def build_road_corridor_audit(source: dict) -> dict:
    network = source["network"]
    nodes = {node["id"]: node for node in network["nodes"]}
    segments = network["segments"]
    roads = source["roads"]
    segment_by_id = {segment["id"]: segment for segment in segments}
    if len(segment_by_id) != len(segments):
        raise ValueError("Duplicate network segment IDs")
    road_by_id = {road["id"]: road for road in roads}
    if len(road_by_id) != len(roads):
        raise ValueError("Duplicate road IDs")

    membership = defaultdict(list)
    for road in roads:
        for segment_id in road["segment_ids"]:
            membership[segment_id].append(road["id"])

    errors = []
    for segment in segments:
        sid = segment["id"]
        if segment["road_id"] not in road_by_id:
            errors.append({"type": "unknown_road", "segment_id": sid})
        if len(membership.get(sid, [])) != 1:
            errors.append({
                "type": "road_membership_cardinality",
                "segment_id": sid,
                "road_ids": membership.get(sid, []),
            })
        if membership.get(sid, [None])[0] != segment["road_id"]:
            errors.append({"type": "road_membership_mismatch", "segment_id": sid})
        if segment["from_node_id"] not in nodes or segment["to_node_id"] not in nodes:
            errors.append({"type": "unknown_endpoint_node", "segment_id": sid})
            continue
        points = segment["geometry"]
        if len(points) < 2:
            errors.append({"type": "invalid_polyline", "segment_id": sid})
            continue
        start_node = nodes[segment["from_node_id"]]
        end_node = nodes[segment["to_node_id"]]
        if points[0] != [start_node["x"], start_node["y"]]:
            errors.append({"type": "from_node_geometry_mismatch", "segment_id": sid})
        if points[-1] != [end_node["x"], end_node["y"]]:
            errors.append({"type": "to_node_geometry_mismatch", "segment_id": sid})

    unreferenced = sorted(set(membership) - set(segment_by_id))
    if unreferenced:
        errors.append({"type": "road_references_unknown_segments", "segment_ids": unreferenced})

    degree = Counter()
    adjacency = {node_id: set() for node_id in nodes}
    for segment in segments:
        a, b = segment["from_node_id"], segment["to_node_id"]
        if a in nodes and b in nodes:
            degree[a] += 1
            degree[b] += 1
            adjacency[a].add(b)
            adjacency[b].add(a)
    degree_mismatches = [
        {"node_id": node_id, "declared_degree": node["degree"], "calculated_degree": degree[node_id]}
        for node_id, node in sorted(nodes.items())
        if node["degree"] != degree[node_id]
    ]

    components = 0
    visited = set()
    for node_id in sorted(nodes):
        if node_id in visited:
            continue
        components += 1
        queue = deque([node_id])
        visited.add(node_id)
        while queue:
            current = queue.popleft()
            for neighbour in adjacency[current]:
                if neighbour not in visited:
                    visited.add(neighbour)
                    queue.append(neighbour)

    corridor_segments = []
    length_exceptions = []
    for segment in sorted(segments, key=lambda item: item["id"]):
        measured = _polyline_length(segment["geometry"])
        delta = round(measured - segment["length_m"], 6)
        if abs(delta) > 0.01:
            length_exceptions.append({
                "segment_id": segment["id"],
                "road_id": segment["road_id"],
                "declared_length_m": segment["length_m"],
                "measured_polyline_length_m": round(measured, 6),
                "difference_m": delta,
            })
        corridor_segments.append({
            "segment_id": segment["id"],
            "road_id": segment["road_id"],
            "from_node_id": segment["from_node_id"],
            "to_node_id": segment["to_node_id"],
            "kind": segment["kind"],
            "road_class": segment["class"],
            "direction": segment["direction"],
            "modes": segment["modes"],
            "access": segment["access"],
            "surface": segment["surface"],
            "centreline_geometry": segment["geometry"],
            "declared_length_m": segment["length_m"],
            "measured_polyline_length_m": round(measured, 6),
            "length_reconciliation": "MATCH" if abs(delta) <= 0.01 else "SOURCE_EXCEPTION",
            "reserve_width_m": None,
            "reserve_area_m2": None,
            "reserve_polygon": None,
            "reserve_geometry_status": "BLOCKED_WIDTH_AND_ROAD_EDGE_UNSPECIFIED",
            "source_ref": f'{source["dataset_id"]}:{segment["id"]}',
        })

    road_records = []
    for road in sorted(roads, key=lambda item: item["id"]):
        own = [segment_by_id[sid] for sid in road["segment_ids"]]
        road_records.append({
            "road_id": road["id"],
            "name": road["name"],
            "axis": road["axis"],
            "road_class": road["class"],
            "segment_count": len(own),
            "declared_length_total_m": sum(s["length_m"] for s in own),
            "measured_polyline_length_total_m": round(sum(_polyline_length(s["geometry"]) for s in own), 6),
            "reserve_width_m": None,
            "reserve_area_m2": None,
            "reserve_polygon": None,
            "reserve_geometry_status": "BLOCKED_WIDTH_AND_ROAD_EDGE_UNSPECIFIED",
        })

    if errors:
        raise ValueError(f"Road corridor source integrity failed: {errors[:10]}")
    body = {
        "schema": "saltwater-bp04-03-road-corridor-register/1.0",
        "candidate_register_id": "BP04-03-STAGE-C-ROAD-CENTRELINE-REGISTER-001",
        "source_dataset": source["dataset_id"],
        "source_status": source["status"],
        "operational_approval": False,
        "road_reserve_polygon_generation": "BLOCKED",
        "road_reserve_width_source": None,
        "road_edge_source": None,
        "summary": {
            "road_count": len(roads),
            "segment_count": len(segments),
            "node_count": len(nodes),
            "connected_network_components": components,
            "network_connectivity": "CONNECTED" if components == 1 else "DISCONNECTED",
            "node_degree_mismatch_count": len(degree_mismatches),
            "road_membership_errors": 0,
            "endpoint_geometry_errors": 0,
            "length_reconciliation_exception_count": len(length_exceptions),
            "corridor_widths_unresolved": len(segments),
            "reserve_polygons_created": 0,
            "reserve_area_assigned_m2": 0,
        },
        "class_summary": dict(sorted(Counter(s["class"] for s in segments).items())),
        "roads": road_records,
        "segments": corridor_segments,
        "node_degree_exceptions": degree_mismatches,
        "length_exceptions": length_exceptions,
        "limitations": [
            "This register preserves source road centre-lines; it does not create road-reserve or right-of-way polygons.",
            "SW-GEO-V1 contains no surveyed road-edge geometry or road-reserve widths.",
            "No reserve width, road-edge offset, reserve area or land-use deduction is inferred.",
            "The declared lengths of bridge segments SWS-0684 and SWS-0685 do not reconcile to their stored polylines; source values are preserved and flagged.",
            "Centre-line intersection is not proof of legal frontage, driveway access, pedestrian access or emergency access.",
            "All records are non-operational candidates pending authoritative BP-02 geography approval.",
        ],
    }
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    body["manifest_sha256"] = hashlib.sha256(canonical).hexdigest()
    return body


def main():
    root = Path(__file__).resolve().parents[1]
    source = json.loads((root / "data/geography/saltwater-geography-v1.json").read_text(encoding="utf-8"))
    result = build_road_corridor_audit(source)
    target = Path("bp04-03-road-corridor-register.json")
    target.write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    print(json.dumps({
        "road_count": result["summary"]["road_count"],
        "segment_count": result["summary"]["segment_count"],
        "node_count": result["summary"]["node_count"],
        "connected_network_components": result["summary"]["connected_network_components"],
        "node_degree_mismatch_count": result["summary"]["node_degree_mismatch_count"],
        "length_reconciliation_exception_count": result["summary"]["length_reconciliation_exception_count"],
        "reserve_polygons_created": result["summary"]["reserve_polygons_created"],
        "corridor_widths_unresolved": result["summary"]["corridor_widths_unresolved"],
        "manifest_sha256": result["manifest_sha256"],
        "operational_approval": result["operational_approval"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
