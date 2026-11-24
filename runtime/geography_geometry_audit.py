"""Read-only geometric and routing QA for the fictional SW-GEO-V1 baseline."""
from __future__ import annotations

import json
import math
from pathlib import Path

EPS = 1e-7


def _distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def _area(ring):
    return abs(sum(ring[i][0] * ring[i + 1][1] - ring[i + 1][0] * ring[i][1]
                   for i in range(len(ring) - 1)) / 2)


def _centroid(ring):
    cross_sum = sum(ring[i][0] * ring[i + 1][1] - ring[i + 1][0] * ring[i][1]
                    for i in range(len(ring) - 1))
    if abs(cross_sum) <= EPS:
        return [sum(p[0] for p in ring[:-1]) / (len(ring) - 1),
                sum(p[1] for p in ring[:-1]) / (len(ring) - 1)]
    x = sum((ring[i][0] + ring[i + 1][0]) *
            (ring[i][0] * ring[i + 1][1] - ring[i + 1][0] * ring[i][1])
            for i in range(len(ring) - 1)) / (3 * cross_sum)
    y = sum((ring[i][1] + ring[i + 1][1]) *
            (ring[i][0] * ring[i + 1][1] - ring[i + 1][0] * ring[i][1])
            for i in range(len(ring) - 1)) / (3 * cross_sum)
    return [x, y]


def _orient(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def _on_segment(a, b, p):
    return (abs(_orient(a, b, p)) <= EPS
            and min(a[0], b[0]) - EPS <= p[0] <= max(a[0], b[0]) + EPS
            and min(a[1], b[1]) - EPS <= p[1] <= max(a[1], b[1]) + EPS)


def _proper_intersection(a, b, c, d):
    return (_orient(a, b, c) * _orient(a, b, d) < -EPS
            and _orient(c, d, a) * _orient(c, d, b) < -EPS)


def _point_in_ring(point, ring):
    inside = False
    for i in range(len(ring) - 1):
        a, b = ring[i], ring[i + 1]
        if _on_segment(a, b, point):
            return True
        if (a[1] > point[1]) != (b[1] > point[1]):
            x_cross = (b[0] - a[0]) * (point[1] - a[1]) / (b[1] - a[1]) + a[0]
            if point[0] < x_cross:
                inside = not inside
    return inside


def _self_intersects(ring):
    for i in range(len(ring) - 1):
        for j in range(i + 1, len(ring) - 1):
            if j == i + 1 or (i == 0 and j == len(ring) - 2):
                continue
            if _proper_intersection(ring[i], ring[i + 1], ring[j], ring[j + 1]):
                return True
            if any(_on_segment(ring[i], ring[i + 1], p) for p in (ring[j], ring[j + 1])):
                return True
            if any(_on_segment(ring[j], ring[j + 1], p) for p in (ring[i], ring[i + 1])):
                return True
    return False


def _rings_overlap(a, b):
    for i in range(len(a) - 1):
        for j in range(len(b) - 1):
            if _proper_intersection(a[i], a[i + 1], b[j], b[j + 1]):
                return True
    probes = [a[0], _centroid(a), b[0], _centroid(b)]
    return (any(_point_in_ring(p, b) and not _on_any_boundary(p, b) for p in probes[:2])
            or any(_point_in_ring(p, a) and not _on_any_boundary(p, a) for p in probes[2:]))


def _on_any_boundary(point, ring):
    return any(_on_segment(ring[i], ring[i + 1], point) for i in range(len(ring) - 1))


def _polygon_contains(parent, child):
    return (all(_point_in_ring(p, parent) for p in child[:-1])
            and not any(_proper_intersection(child[i], child[i + 1], parent[j], parent[j + 1])
                        for i in range(len(child) - 1) for j in range(len(parent) - 1)))


def audit_geometry(path: str | Path) -> dict:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    features = data.get("features", [])
    feature_map = {f.get("id"): f for f in features}
    city_feature = next((f for f in features if f.get("properties", {}).get("entity_type") == "city_state_boundary"), None)
    city_ring = (city_feature or {}).get("geometry", {}).get("coordinates", [[]])[0]
    polygons = [f for f in features if f.get("geometry", {}).get("type") == "Polygon"]
    points = [f for f in features if f.get("geometry", {}).get("type") == "Point"]

    ring_errors = []
    for feature in polygons:
        for ring in feature.get("geometry", {}).get("coordinates", []):
            if (len(ring) < 4 or ring[0] != ring[-1] or _area(ring) <= EPS
                    or _self_intersects(ring)):
                ring_errors.append(feature.get("id"))
                break

    point_outside = [f.get("id") for f in points
                     if not city_ring or not _point_in_ring(f["geometry"]["coordinates"], city_ring)]

    district_rings = {d.get("id"): feature_map.get(d.get("id"), {}).get("geometry", {}).get("coordinates", [[]])[0]
                      for d in data.get("districts", [])}
    neighbourhoods = data.get("neighbourhoods", [])
    parent_failures = []
    for hood in neighbourhoods:
        child = hood.get("geometry", {}).get("coordinates", [[]])[0]
        parent = district_rings.get(hood.get("district_id"), [])
        if not parent or not child or not _polygon_contains(parent, child):
            parent_failures.append(hood.get("id"))

    hood_rings = [h.get("geometry", {}).get("coordinates", [[]])[0] for h in neighbourhoods]
    overlap_pairs = []
    for i in range(len(hood_rings)):
        for j in range(i + 1, len(hood_rings)):
            if _rings_overlap(hood_rings[i], hood_rings[j]):
                overlap_pairs.append([neighbourhoods[i].get("id"), neighbourhoods[j].get("id")])

    city_area = _area(city_ring) if city_ring else 0
    hood_area = sum(_area(r) for r in hood_rings if r)
    node_map = {n.get("id"): [n.get("x"), n.get("y")] for n in data.get("network", {}).get("nodes", [])}
    segments = data.get("network", {}).get("segments", [])
    segment_geometry_errors = []
    segment_outside = []
    adjacency = {node_id: [] for node_id in node_map}
    for segment in segments:
        line = segment.get("geometry", [])
        start, end = node_map.get(segment.get("from_node_id")), node_map.get(segment.get("to_node_id"))
        if (len(line) < 2 or start is None or end is None
                or _distance(line[0], start) > EPS or _distance(line[-1], end) > EPS):
            segment_geometry_errors.append(segment.get("id"))
        else:
            measured = sum(_distance(line[i], line[i + 1]) for i in range(len(line) - 1))
            if abs(measured - segment.get("length_m", -1)) > 0.01:
                segment_geometry_errors.append(segment.get("id"))
        if city_ring and any(not _point_in_ring(p, city_ring) for p in line):
            segment_outside.append(segment.get("id"))
        a, b = segment.get("from_node_id"), segment.get("to_node_id")
        if a in adjacency and b in adjacency:
            adjacency[a].append(b)
            adjacency[b].append(a)

    node_degrees = {n.get("id"): n.get("degree") for n in data.get("network", {}).get("nodes", [])}
    degree_mismatches = [node_id for node_id, neighbours in adjacency.items()
                         if node_degrees.get(node_id) != len(neighbours)]
    seen, component_sizes = set(), []
    for node_id in adjacency:
        if node_id in seen:
            continue
        stack, size = [node_id], 0
        seen.add(node_id)
        while stack:
            current = stack.pop()
            size += 1
            for neighbour in adjacency[current]:
                if neighbour not in seen:
                    seen.add(neighbour)
                    stack.append(neighbour)
        component_sizes.append(size)

    segment_by_id = {s.get("id"): s for s in segments}
    route_errors = []
    for route in data.get("network", {}).get("routes", []):
        route_nodes, route_segments = route.get("node_ids", []), route.get("segment_ids", [])
        if len(route_nodes) != len(route_segments) + 1:
            route_errors.append(route.get("id"))
            continue
        for i, segment_id in enumerate(route_segments):
            segment = segment_by_id.get(segment_id)
            if not segment or {segment.get("from_node_id"), segment.get("to_node_id")} != {route_nodes[i], route_nodes[i + 1]}:
                route_errors.append(route.get("id"))
                break

    checks = {
        "polygon_rings_valid_and_simple": not ring_errors,
        "point_features_inside_city_boundary": not point_outside,
        "neighbourhoods_contained_by_assigned_district": not parent_failures,
        "neighbourhood_interiors_do_not_overlap": not overlap_pairs,
        "neighbourhood_area_equals_city_area": abs(hood_area - city_area) <= 0.01,
        "road_segment_geometry_matches_nodes_and_lengths": not segment_geometry_errors,
        "road_segment_geometry_inside_city_boundary": not segment_outside,
        "node_degrees_match_segment_graph": not degree_mismatches,
        "road_network_single_connected_component": len(component_sizes) == 1 and len(seen) == len(node_map),
        "route_segment_sequences_are_contiguous": not route_errors,
    }
    return {
        "audit": "SW-GEO-V1-GEOMETRY-QA",
        "dataset_id": data.get("dataset_id"),
        "counts": {"polygon_features": len(polygons), "point_features": len(points),
                   "neighbourhoods": len(neighbourhoods), "nodes": len(node_map), "segments": len(segments)},
        "measurements": {"city_area_m2": round(city_area, 3), "neighbourhood_area_sum_m2": round(hood_area, 3),
                         "neighbourhood_overlap_pairs": len(overlap_pairs), "network_component_sizes": component_sizes},
        "exceptions": {"invalid_polygon_ids": ring_errors, "outside_point_feature_ids": point_outside,
                       "neighbourhood_parent_failures": parent_failures, "neighbourhood_overlap_pairs": overlap_pairs,
                       "segment_geometry_failures": segment_geometry_errors, "segments_outside_city": segment_outside,
                       "node_degree_mismatches": degree_mismatches, "route_sequence_failures": route_errors},
        "checks": checks,
        "passed_checks": sum(checks.values()),
        "failed_checks": [name for name, passed in checks.items() if not passed],
        "operational_seed_eligible": False,
        "geometry_import_performed": False,
        "database_write_performed": False,
        "approval_note": "Structural geometric QA only. Passing checks do not constitute user approval, cadastral acceptance, operational routing acceptance or production seed authority.",
    }


def main():
    root = Path(__file__).resolve().parents[1]
    report = audit_geometry(root / "data/geography/saltwater-geography-v1.json")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
