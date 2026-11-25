"""Deterministic BP04-03 Stage E physical-asset design inventory.

All geometry and physical specifications are generated fictional design candidates.
This module deliberately creates no operational geography IDs, addresses,
ownership, tenancy, occupancy, business assignments or production records.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import nearest_points

from runtime.parcel_candidate_generator import build_candidates
from runtime.parcel_dossier_generator import build_parcel_dossiers

GENERATOR = "BP04-03-STAGE-E-ASSET-INVENTORY-V1"
CRS = "SW-LOCAL-METRE-GRID-V1"
SOURCE = "BP04-03-STAGE-E-GENERATED-DESIGN"
ACTOR = "BP04-03-STAGE-E-GENERATOR-V1"

USE = {
    "residential": ("residential", "dwelling", 4, 6, 62.0),
    "mixed_use": ("mixed_use", "mixed_use", 5, 5, 85.0),
    "commercial": ("commercial", "office", 6, 5, 95.0),
    "civic": ("civic", "civic", 3, 3, 110.0),
    "education": ("institutional", "education", 3, 4, 90.0),
    "industrial": ("industrial", "industrial", 2, 2, 180.0),
    "freight_logistics": ("industrial", "warehouse", 2, 3, 160.0),
    "port_maritime": ("transport", "port_maritime", 2, 3, 150.0),
    "waterfront": ("mixed_use", "waterfront", 3, 4, 100.0),
    "utility": ("utility", "plant_space", 1, 2, 120.0),
    "open_space": ("open_space", "open_space", 1, 1, 150.0),
}

# Deterministic global-city vertical profiles. District-specific ranges create
# distinct financial, civic, university and harbour skylines while industrial,
# port-yard and utility assets retain appropriate low-rise forms.
STOREY_RANGES = {
    "residential": {"default": (10, 20), "SW-D05": (6, 12), "SW-D07": (14, 24)},
    "mixed_use": {"default": (16, 30), "SW-D03": (20, 34), "SW-D07": (26, 40)},
    "commercial": {"default": (18, 36), "SW-D02": (24, 40), "SW-D03": (30, 48), "SW-D07": (42, 58)},
    "civic": {"default": (7, 16), "SW-D03": (12, 24)},
    "education": {"default": (7, 16), "SW-D02": (12, 22)},
    "industrial": {"default": (3, 7), "SW-D06": (4, 9)},
    "freight_logistics": {"default": (3, 8), "SW-D04": (4, 10), "SW-D06": (4, 10), "SW-D08": (4, 10)},
    "port_maritime": {"default": (3, 8), "SW-D04": (4, 10), "SW-D08": (4, 9)},
    "waterfront": {"default": (12, 24), "SW-D04": (16, 30), "SW-D07": (18, 30), "SW-D08": (16, 28)},
    "utility": {"default": (1, 3)},
    "open_space": {"default": (1, 1)},
}

def _storey_count(land_use: str, district_id: str, parcel_id: str) -> int:
    profile = STOREY_RANGES[land_use]
    low, high = profile.get(district_id, profile["default"])
    digest = hashlib.sha256(
        f"saltwater:GLOBAL-ESTATE-VERTICAL-V1:{district_id}:{land_use}:{parcel_id}".encode()
    ).digest()
    return low + int.from_bytes(digest[:4], "big") % (high - low + 1)


SYLLABLES = (
    ("ba", "be", "bi", "bo", "bu", "ca", "ce", "ci", "co", "cu",
     "da", "de", "di", "do", "du", "fa", "fe", "fi", "fo", "fu",
     "ga", "ge", "gi", "go", "gu", "ka", "ke", "ki", "ko", "ku",
     "la", "le", "li", "lo", "lu", "ma", "me", "mi", "mo", "mu",
     "na", "ne", "ni", "no", "nu", "ra", "re", "ri", "ro", "ru",
     "sa", "se", "si", "so", "su", "ta", "te", "ti", "to", "tu",
     "va", "ve", "vi", "vo", "vu", "za", "ze", "zi", "zo", "zu"),
    ("n", "r", "l", "m", "s", "th", "nd", "st", "rn", "v", "k", ""),
)

def _name(entity_type: str, entity_key: str, occupied: set[str]) -> str:
    for attempt in range(1000):
        digest = hashlib.sha256(
            f"saltwater:{GENERATOR}:{entity_type}:{entity_key}:{attempt}".encode()
        ).digest()
        value = "".join(
            SYLLABLES[0][digest[i] % len(SYLLABLES[0])] +
            SYLLABLES[1][digest[i + 1] % len(SYLLABLES[1])]
            for i in (0, 2, 4)
        ).capitalize()
        if value.casefold() not in occupied:
            occupied.add(value.casefold())
            return value
    raise ValueError(f"Could not create a unique deterministic name for {entity_key}")

def _slug(value: str) -> str:
    return "".join(ch for ch in value.upper() if ch.isalnum())[:22]

def _rings(poly: Polygon) -> list:
    return [
        [[round(float(x), 6), round(float(y), 6)] for x, y in list(poly.exterior.coords)],
        *[[[round(float(x), 6), round(float(y), 6)] for x, y in list(r.coords)]
          for r in poly.interiors],
    ]

def _footprint(site: Polygon, land_use: str) -> Polygon | None:
    """Find a deterministic, wholly-contained rectangular design footprint."""
    if site.area < 1800:
        return None
    coverage = 0.018 if land_use in ("residential", "mixed_use", "commercial") else 0.012
    target = min(1800.0, max(144.0, site.area * coverage))
    width = (target * 1.35) ** 0.5
    height = target / width
    safe = site.buffer(-1.5)
    if safe.is_empty:
        safe = site
    minx, miny, maxx, maxy = safe.bounds
    if maxx - minx < 8 or maxy - miny < 8:
        return None
    # A bounded, deterministic 9x9 search avoids pathological work on
    # narrow candidate fragments while retaining reproducible placement.
    anchor = safe.representative_point()
    candidates = [(anchor.x, anchor.y)]
    for ix in range(9):
        for iy in range(9):
            candidates.append((
                minx + (maxx-minx) * (ix + 0.5) / 9,
                miny + (maxy-miny) * (iy + 0.5) / 9,
            ))
    sizes = []
    for scale in (1.0, .85, .7, .55, .4, .3):
        w, h = max(6.0, width * scale), max(6.0, height * scale)
        sizes.extend(((w, h), (h, w)))
    for cx, cy in candidates:
        for w, h in sizes:
            footprint = box(cx-w/2, cy-h/2, cx+w/2, cy+h/2)
            if safe.covers(footprint):
                return footprint
    return None


def _campus_building_target_count(site_area_m2: float, land_use: str) -> int:
    """Deterministic campus scale by site capacity and specialist land use."""
    eligible = {
        "residential", "mixed_use", "commercial", "civic", "education",
        "industrial", "freight_logistics", "port_maritime", "waterfront",
    }
    if land_use not in eligible:
        return 1
    if site_area_m2 >= 30000:
        return 4
    if site_area_m2 >= 18000:
        return 3
    if site_area_m2 >= 10000:
        return 2
    return 1


def _additional_campus_footprints(site: Polygon, land_use: str,
                                  existing: list[Polygon], count: int) -> list[Polygon]:
    """Place non-overlapping subsidiary buildings wholly inside one property site."""
    if count <= 0:
        return []
    safe = site.buffer(-2.0)
    if safe.is_empty:
        return []
    target = min(1200.0, max(200.0, site.area * 0.009))
    base_width = (target * 1.35) ** 0.5
    base_height = target / base_width
    minx, miny, maxx, maxy = safe.bounds
    centres = [
        (minx + (maxx-minx) * (ix + 0.5) / 15,
         miny + (maxy-miny) * (iy + 0.5) / 15)
        for ix in range(15) for iy in range(15)
    ]
    # Prefer the parts of the site furthest from existing footprints; stable
    # coordinate tie-breaks keep campus placement reproducible.
    centres.sort(key=lambda xy: (
        -min(poly.distance(Point(xy)) for poly in existing),
        round(xy[0], 6), round(xy[1], 6),
    ))
    sizes = []
    for scale in (1.0, 0.85, 0.7, 0.55, 0.4):
        w, h = max(8.0, base_width*scale), max(8.0, base_height*scale)
        sizes.extend(((w, h), (h, w)))
    placed = []
    occupied = list(existing)
    for cx, cy in centres:
        found = None
        for w, h in sizes:
            candidate = box(cx-w/2, cy-h/2, cx+w/2, cy+h/2)
            if not safe.covers(candidate):
                continue
            if any(candidate.distance(other) < 4.0 or candidate.intersects(other)
                   for other in occupied):
                continue
            found = candidate
            break
        if found is not None:
            placed.append(found)
            occupied.append(found)
            if len(placed) >= count:
                break
    return placed


def build_asset_inventory(source: dict, candidates: dict | None = None,
                          dossiers: dict | None = None) -> dict:
    candidates = candidates or build_candidates(source)
    dossiers = dossiers or build_parcel_dossiers(source, candidates)
    if candidates.get("operational_approval") is not False or dossiers.get("operational_approval") is not False:
        raise ValueError("Stage E accepts only unapproved candidate geography")
    if dossiers.get("candidate_manifest_sha256") != candidates.get("manifest_sha256"):
        raise ValueError("Stage E parcel dossier/candidate manifest mismatch")

    dossier_by_id = {r["dossier"]["candidate_parcel_id"]: r for r in dossiers["parcels"]}
    occupied: set[str] = set()
    properties, buildings, premises, units, access_points, access_connectors = [], [], [], [], [], []
    geometries = []
    for parcel in sorted(candidates["parcels"], key=lambda p: p["candidate_parcel_id"]):
        parcel_id = parcel["candidate_parcel_id"]
        slug = _slug(parcel_id)
        site = Polygon(parcel["geometry"][0], parcel["geometry"][1:])
        if not site.is_valid or site.is_empty or site.area <= 0:
            raise ValueError(f"Invalid property-site candidate: {parcel_id}")
        land_use = parcel["land_use_code"]
        if land_use not in USE:
            raise ValueError(f"Unsupported generated land use: {land_use}")
        property_class, use_code, _, spaces_per_floor, unit_area = USE[land_use]
        property_code = f"SWP-{slug}"
        property_name = _name("PROPERTY", parcel_id, occupied)
        properties.append({
            "candidate_property_id": property_code, "display_name": property_name,
            "source_candidate_parcel_id": parcel_id,
            "source_neighbourhood_id": parcel["source_neighbourhood_id"],
            "source_district_id": parcel["source_district_id"],
            "land_use_code": land_use, "property_class": property_class,
            "primary_use": use_code, "site_area_m2": round(site.area, 3),
            "site_perimeter_m": round(site.length, 3),
            "centroid_m": [round(site.centroid.x, 6), round(site.centroid.y, 6)],
            "representative_point_m": [round(site.representative_point().x, 6), round(site.representative_point().y, 6)],
            "geometry": _rings(site), "geometry_status": "PARCEL_CANDIDATE_NOT_OPERATIONAL",
            "boundary_status": "unverified", "site_state": "unknown",
            "terrain_code": "unknown", "drainage_state": "unknown",
            "perimeter_type": "unknown", "utility_availability": "unknown",
            "source_ref": parcel["source_ref"], "actor_ref": ACTOR,
            "confidence_code": "estimated", "effective_from_tick": 0,
            "recorded_status": "generated_design_candidate",
        })
        footprint = _footprint(site, land_use)
        if footprint is None or land_use == "open_space":
            geometries.append({"property": property_code, "building_count": 0})
            continue

        campus_target = _campus_building_target_count(site.area, land_use)
        campus_footprints = [footprint]
        campus_footprints.extend(_additional_campus_footprints(
            site, land_use, [footprint], campus_target - 1
        ))
        for building_index, campus_footprint in enumerate(campus_footprints, start=1):
            footprint = campus_footprint
            building_suffix = f"B{building_index:02d}"
            building_code = f"SWB-STR-{slug}-{building_suffix}"
            building_name = _name("BUILDING", f"{parcel_id}:{building_suffix}", occupied)
            storeys = _storey_count(land_use, parcel["source_district_id"], parcel_id if building_index == 1 else f"{parcel_id}:{building_suffix}")
            footprint_area = footprint.area
            gross_floor_area = footprint_area * storeys
            building = {
                "candidate_building_id": building_code, "display_name": building_name,
                "property_id": property_code, "source_candidate_parcel_id": parcel_id,
                "building_use": use_code, "building_form": ("high_rise" if storeys >= 20 else "mid_rise" if storeys >= 8 else "low_rise"),
                "height_profile_code": "GLOBAL-ESTATE-VERTICAL-V1",
                "structure_class": "unknown", "construction_system": "unknown",
                "foundation_type": "unknown", "roof_form": "unknown",
                "roof_covering": "unknown", "facade_system": "unknown",
                "storeys_above": storeys, "storeys_below": 0,
                "height_m": round(storeys * 3.6, 3), "height_basis": "generated_design_value",
                "footprint_area_m2": round(footprint_area, 3),
                "gross_floor_area_m2": round(gross_floor_area, 3),
                "geometry": _rings(footprint),
                "geometry_status": "GENERATED_DESIGN_FOOTPRINT_NOT_SURVEYED",
                "source_ref": f"{SOURCE}:{parcel_id}:{building_suffix}:building-layout-v1",
                "actor_ref": ACTOR, "confidence_code": "estimated",
                "effective_from_tick": 0, "recorded_status": "generated_design_candidate",
            }
            buildings.append(building)
    
            # One separately identified premises per designed floor. These are
            # spatially subordinate spaces, not operator or occupancy assignments.
            for floor in range(storeys):
                premises_code = f"SWPR-{slug}-F{floor:02d}" if building_index == 1 else f"SWPR-{slug}-{building_suffix}-F{floor:02d}"
                premises_name = _name("PREMISES", f"{parcel_id}:{building_suffix}:F{floor:02d}", occupied)
                floor_area = footprint_area * 0.82
                premises_type = {
                    "residential": "residential_common", "mixed_use": "suite", "commercial": "office",
                    "civic": "civic_room", "education": "department", "industrial": "industrial_bay",
                    "freight_logistics": "warehouse", "port_maritime": "warehouse",
                    "waterfront": "suite", "utility": "plant_space",
                }.get(land_use, "other")
                premises.append({
                    "candidate_premises_id": premises_code, "display_name": premises_name,
                    "building_id": building_code,
                    "floor_order": floor, "floor_code": "G" if floor == 0 else f"L{floor}",
                    "premises_type": premises_type, "primary_function": use_code,
                    "floor_area_m2": round(floor_area, 3),
                    "fitout_standard": "unknown", "occupancy_suitability": "unknown",
                    "security_boundary": "unknown", "accessibility_state": "unknown",
                    "source_ref": f"{SOURCE}:{building_code}:floor:{floor}",
                    "actor_ref": ACTOR, "confidence_code": "estimated",
                    "effective_from_tick": 0,
                })
                count = max(1, min(12, int(floor_area / unit_area)))
                for unit_no in range(1, count + 1):
                    unit_code = f"SWU-{slug}-F{floor:02d}-U{unit_no:02d}" if building_index == 1 else f"SWU-{slug}-{building_suffix}-F{floor:02d}-U{unit_no:02d}"
                    unit_name = _name("UNIT", f"{parcel_id}:{building_suffix}:F{floor:02d}:U{unit_no:02d}", occupied)
                    units.append({
                        "candidate_unit_id": unit_code, "display_name": unit_name,
                        "premises_id": premises_code,
                        "unit_class": {
                            "residential": "dwelling", "mixed_use": "other",
                            "commercial": "office", "civic": "room", "education": "room",
                            "industrial": "workshop", "freight_logistics": "storage",
                            "port_maritime": "storage", "waterfront": "other",
                            "utility": "plant_space",
                        }.get(land_use, "other"),
                        "floor_level": "Ground" if floor == 0 else f"Level {floor}",
                        "floor_area_m2": round(floor_area / count, 3),
                        "room_count": 1 if land_use in ("industrial", "freight_logistics", "utility") else 2,
                        "physical_capacity": None, "capacity_knowledge_state": "not_assessed",
                        "suitability_state": "unknown", "fitout_state": "unknown",
                        "accessibility_state": "unknown",
                        "source_ref": f"{SOURCE}:{premises_code}:unit:{unit_no}",
                        "actor_ref": ACTOR, "confidence_code": "estimated",
                        "effective_from_tick": 0,
                    })
    
            # Two distinct boundary access-location candidates per building. The
            # points are geometric proposals, not confirmed doors or usable routes.
            parcel_dossier = dossier_by_id[parcel_id]
            frontage_candidates = parcel_dossier["access_candidates"]
            frontage_points = [
                (row, Point(row["candidate_x_m"], row["candidate_y_m"]))
                for row in frontage_candidates
            ]
            first_access_boundary_point = None
            for access_no, fraction in ((1, .25), (2, .75)):
                if access_no == 1 and frontage_points:
                    # A01 selects the nearest boundary/frontage pair.
                    choices = []
                    for frontage_row, frontage_point in frontage_points:
                        boundary_candidate = nearest_points(footprint.boundary, frontage_point)[0]
                        gap = boundary_candidate.distance(frontage_point)
                        choices.append((round(gap, 9), frontage_row["access_candidate_id"],
                                        boundary_candidate, frontage_point))
                    _, linked_frontage_id, boundary_point, linked_frontage_point = min(
                        choices, key=lambda item: (item[0], item[1])
                    )
                    first_access_boundary_point = boundary_point
                elif access_no == 2 and frontage_points and first_access_boundary_point is not None:
                    # A02 searches deterministic samples around the footprint boundary.
                    # Reject any connector that enters the building interior or leaves
                    # the parent property. A minimum perimeter separation keeps A02
                    # distinct from A01 rather than duplicating its location.
                    boundary = footprint.boundary
                    perimeter = boundary.length
                    minimum_separation = max(5.0, perimeter * 0.10)
                    first_measure = boundary.project(first_access_boundary_point)
                    choices = []
                    for sample_no in range(128):
                        measure = perimeter * sample_no / 128
                        boundary_candidate = boundary.interpolate(measure)
                        separation = abs(measure - first_measure)
                        separation = min(separation, perimeter - separation)
                        if separation < minimum_separation:
                            continue
                        for frontage_row, frontage_point in frontage_points:
                            connector = LineString([
                                (boundary_candidate.x, boundary_candidate.y),
                                (frontage_point.x, frontage_point.y),
                            ])
                            if not site.covers(connector):
                                continue
                            if footprint.intersection(connector).length > 0.01:
                                continue
                            gap = boundary_candidate.distance(frontage_point)
                            choices.append((
                                round(gap, 9), frontage_row["access_candidate_id"],
                                sample_no, boundary_candidate, frontage_point,
                            ))
                    if choices:
                        _, linked_frontage_id, _, boundary_point, linked_frontage_point = min(
                            choices, key=lambda item: (item[0], item[1], item[2])
                        )
                    else:
                        # Keep an explicit blocked candidate rather than inventing
                        # a feasible access route when no sampled line is clear.
                        boundary_point = boundary.interpolate(perimeter * fraction)
                        nearest_row, linked_frontage_point = min(
                            frontage_points,
                            key=lambda item: (
                                round(boundary_point.distance(item[1]), 9),
                                item[0]["access_candidate_id"],
                            ),
                        )
                        linked_frontage_id = nearest_row["access_candidate_id"]
                else:
                    boundary_point = footprint.boundary.interpolate(
                        footprint.boundary.length * fraction
                    )
                    if frontage_points:
                        nearest_row, linked_frontage_point = min(
                            frontage_points,
                            key=lambda item: (
                                round(boundary_point.distance(item[1]), 9),
                                item[0]["access_candidate_id"],
                            ),
                        )
                        linked_frontage_id = nearest_row["access_candidate_id"]
                    else:
                        linked_frontage_id = None
                        linked_frontage_point = None
    
                linked_candidate = next(
                    (row for row in frontage_candidates
                     if row["access_candidate_id"] == linked_frontage_id), None
                )
                link_distance = (boundary_point.distance(linked_frontage_point)
                                 if linked_frontage_point is not None else None)
                proximity_link = bool(
                    linked_candidate
                    and linked_candidate.get("candidate_type") == "road_reserve_proximity_connection"
                )
                access_code = f"SWA-{slug}-{building_suffix}-A{access_no:02d}"
                access_name = _name("ACCESS_POINT", f"{parcel_id}:A{access_no:02d}", occupied)
                access_points.append({
                    "candidate_access_point_id": access_code, "display_name": access_name,
                    "building_id": building_code,
                    "access_type": "unknown", "access_modes": [],
                    "directionality": "unknown", "control_type": "unknown",
                    "availability_state": "not_assessed", "accessibility_state": "not_assessed",
                    "emergency_egress_state": "not_assessed",
                    "loading_capability_state": "not_assessed",
                    "point_m": [round(boundary_point.x, 6), round(boundary_point.y, 6)],
                    "point_status": "UNREVIEWED_BUILDING_BOUNDARY_CANDIDATE",
                    "road_link_candidate_id": linked_frontage_id,
                    "road_link_candidate_type": linked_candidate.get("candidate_type") if linked_candidate else None,
                    "road_link_road_id": linked_candidate.get("road_id") if linked_candidate else None,
                    "road_link_segment_ids": linked_candidate.get("road_segment_ids", []) if linked_candidate else [],
                    "road_link_contact_type": linked_candidate.get("contact_type") if linked_candidate else None,
                    "road_link_candidate_distance_m": round(link_distance, 3) if link_distance is not None else None,
                    "road_link_basis": (
                        "NEAREST_ROAD_RESERVE_PROXIMITY_CANDIDATE" if proximity_link
                        else "NEAREST_STRAIGHT_LINE_FRONTAGE_CANDIDATE" if linked_frontage_id
                        else "NO_FRONTAGE_CANDIDATE"
                    ),
                    "road_link_status": "UNREVIEWED_PROXIMITY_ONLY_NOT_A_CONFIRMED_ROUTE" if linked_frontage_id else "UNRESOLVED_NO_FRONTAGE",
                    "source_ref": f"{SOURCE}:{building_code}:access:{access_no}",
                    "actor_ref": ACTOR, "confidence_code": "estimated",
                    "effective_from_tick": 0,
                })
    
                # Persist the geometric connector as its own typed candidate. Its
                # geometry is not evidence of a constructed or legally usable route.
                if linked_candidate is not None and linked_frontage_point is not None:
                    connector_type = (
                        "BUILDING_TO_ROAD_RESERVE_PROXIMITY_CANDIDATE" if proximity_link
                        else "BUILDING_TO_FRONTAGE_CANDIDATE"
                    )
                    connector_id = f"SWAC-{slug}-{building_suffix}-A{access_no:02d}-C01"
                    connector_geometry = [
                        [round(boundary_point.x, 6), round(boundary_point.y, 6)],
                        [round(linked_frontage_point.x, 6), round(linked_frontage_point.y, 6)],
                    ]
                    access_connectors.append({
                        "candidate_connector_id": connector_id,
                        "access_point_candidate_id": access_code,
                        "road_access_candidate_id": linked_frontage_id,
                        "frontage_candidate_id": linked_candidate.get("frontage_candidate_id"),
                        "road_connection_candidate_id": linked_candidate.get("road_connection_candidate_id"),
                        "road_id": linked_candidate.get("road_id"),
                        "road_segment_ids": linked_candidate.get("road_segment_ids", []),
                        "connector_type": connector_type,
                        "contact_type": (
                            linked_candidate.get("contact_type") if proximity_link
                            else "FRONTAGE_CANDIDATE"
                        ),
                        "length_m": round(link_distance, 3),
                        "coordinate_reference": CRS,
                        "geometry_type": "LineString",
                        "geometry_coordinates": connector_geometry,
                        "geometry_status": "UNREVIEWED_GEOMETRIC_LINE_ONLY",
                        "review_status": "unreviewed_candidate",
                        "constructed_state": "unknown",
                        "surface_code": "unknown",
                        "slope_state": "not_assessed",
                        "barrier_state": "not_assessed",
                        "pedestrian_suitability": "not_assessed",
                        "vehicle_suitability": "not_assessed",
                        "accessibility_state": "not_assessed",
                        "legal_access_state": "not_assessed",
                        "public_access_state": "not_assessed",
                        "emergency_egress_state": "not_assessed",
                        "source_ref": f"{SOURCE}:{building_code}:connector:{access_no}:v1",
                        "actor_ref": ACTOR,
                        "confidence_code": "estimated",
                        "effective_from_tick": 0,
                        "reason": "Straight-line geometry derived from generated building-boundary and parcel road-connection candidates; construction, legal access, surface, gradient and route usability are not assessed.",
                    })
            geometries.append({
                "property": property_code, "building": building_code,
                "footprint_area_m2": round(footprint_area, 3),
                "footprint_inside_property": bool(site.covers(footprint)),
            })

    # Full BP04-02 profile and typed child-record layer. Design-derived values
    # are explicitly labelled; unavailable physical facts are not fabricated.
    property_profiles, building_profiles, premises_profiles = [], [], []
    unit_profiles, access_point_profiles = [], []
    measurements, building_levels, building_components = [], [], []
    premises_rooms, utility_systems, physical_features = [], [], []
    condition_assessments, physical_defects, asset_assertions = [], [], []

    def provenance(ref, reason):
        return {"source_ref": ref, "actor_ref": ACTOR,
                "confidence_code": "estimated", "effective_from_tick": 0,
                "reason": reason}

    def measure(entity_type, entity_id, code, value, unit, basis, ref):
        measurements.append({
            "entity_type": entity_type, "entity_id": entity_id,
            "measure_code": code, "numeric_value": round(float(value), 4),
            "unit_code": unit, "measurement_basis": basis,
            "precision_code": "estimated", "method_code": "estimate",
            **provenance(ref, "Deterministic generated design allocation; not a survey or instrument observation."),
        })

    def utility(entity_type, entity_id, utility_type, ref):
        utility_systems.append({
            "entity_type": entity_type, "entity_id": entity_id,
            "utility_type": utility_type, "availability_state": "not_assessed",
            "capacity_value": None, "capacity_unit": None, "service_point_ref": None,
            "source_ref": ref, "actor_ref": ACTOR, "effective_from_tick": 0,
            "confidence_code": "unknown",
            "reason": "No service connection, capacity or service-point inspection has been performed.",
        })

    def feature(entity_type, entity_id, feature_type, ref):
        physical_features.append({
            "entity_type": entity_type, "entity_id": entity_id,
            "feature_type": feature_type, "feature_label": None,
            "feature_state": "not_assessed", "source_ref": ref,
            "actor_ref": ACTOR, "effective_from_tick": 0,
            "confidence_code": "unknown",
            "reason": "Feature presence has not been physically assessed.",
        })

    def condition(entity_type, entity_id, element, ref):
        condition_assessments.append({
            "entity_type": entity_type, "entity_id": entity_id,
            "element_code": element, "condition_code": "not_assessed",
            "assessed_tick": 0, "assessor_ref": ACTOR, "source_ref": ref,
            "confidence_code": "unknown",
            "findings": "No physical inspection has been performed; generated design geometry is not evidence of condition.",
            "recommended_action": "Inspect and record a sourced assessment before operational use.",
        })

    def assertion(entity_type, entity_id, attribute, state, ref):
        asset_assertions.append({
            "entity_type": entity_type, "entity_id": entity_id,
            "attribute_code": attribute, "value_text": None,
            "knowledge_state": state, "effective_from_tick": 0,
            "source_ref": ref, "actor_ref": ACTOR,
            "confidence_code": "unknown",
            "reason": "No evidence has been supplied or assessment performed for this attribute.",
        })

    for p in properties:
        pid, ref = p["candidate_property_id"], p["source_ref"]
        property_profiles.append({
            "candidate_property_id": pid, "property_class": p["property_class"],
            "primary_use": p["primary_use"], "secondary_uses": [],
            "development_form": "other", "site_state": "unknown",
            "boundary_status": "unverified", "terrain_code": "unknown",
            "drainage_state": "not_assessed", "perimeter_type": "not_assessed",
            "utility_availability": "not_assessed", **provenance(ref, "Use class is generated from neighbourhood design; physical site condition is not assessed."),
        })
        measure("PROPERTY", pid, "site_area", p["site_area_m2"], "m2", "design", ref)
        for utility_type in ("electricity", "water", "wastewater", "telecommunications"):
            utility("PROPERTY", pid, utility_type, ref)
        for feature_type in ("yard", "parking", "security_perimeter"):
            feature("PROPERTY", pid, feature_type, ref)
        for element in ("site", "overall"):
            condition("PROPERTY", pid, element, ref)
        for attribute, state in (("boundary_survey", "not_assessed"),
                                 ("material_inventory", "not_assessed"),
                                 ("defect_inventory", "not_assessed")):
            assertion("PROPERTY", pid, attribute, state, ref)

    for b in buildings:
        bid, ref = b["candidate_building_id"], b["source_ref"]
        building_profiles.append({
            "candidate_building_id": bid, "building_use": b["building_use"],
            "building_form": b["building_form"], "structure_class": "unknown",
            "construction_system": "unknown", "foundation_type": "not_assessed",
            "roof_form": "unknown", "roof_covering": "unknown", "facade_system": "unknown",
            "storeys_above": b["storeys_above"], "storeys_below": b["storeys_below"],
            "height_m": b["height_m"], "height_datum": "generated_floor_height_assumption",
            "structural_capacity_persons": None, "authorised_capacity_persons": None,
            "construction_year": None, "completion_year": None,
            "heritage_status": "not_assessed",
            **provenance(ref, "Storeys and height are generated design assumptions; construction and capacity are unknown."),
        })
        measure("BUILDING", bid, "footprint_area", b["footprint_area_m2"], "m2", "design", ref)
        measure("BUILDING", bid, "gross_floor_area", b["gross_floor_area_m2"], "m2", "design", ref)
        measure("BUILDING", bid, "height", b["height_m"], "m", "design", ref)
        for floor in range(b["storeys_above"]):
            level_code = "G" if floor == 0 else f"L{floor}"
            building_levels.append({
                "candidate_building_id": bid, "level_code": level_code,
                "level_name": "Ground" if floor == 0 else f"Level {floor}",
                "level_order": floor, "level_type": "ground" if floor == 0 else "upper",
                "source_ref": ref, "actor_ref": ACTOR, "effective_from_tick": 0,
                "reason": "Floor schedule generated from the fictional building design profile.",
            })
        for component_type in ("foundation", "frame", "floor", "wall", "roof",
                               "facade", "glazing", "stair", "electrical",
                               "water", "fire_alarm", "security"):
            building_components.append({
                "candidate_building_id": bid, "level_code": None,
                "component_type": component_type, "material_code": "unknown",
                "condition_code": "not_assessed", "source_ref": ref,
                "actor_ref": ACTOR, "effective_from_tick": 0,
                "reason": "Component inventory and material inspection have not been performed.",
            })
        for utility_type in ("electricity", "water", "wastewater", "telecommunications", "hvac"):
            utility("BUILDING", bid, utility_type, ref)
        for feature_type in ("lobby", "corridor", "stairwell", "fire_escape"):
            feature("BUILDING", bid, feature_type, ref)
        for element in ("structure", "roof", "fire_safety", "accessibility"):
            condition("BUILDING", bid, element, ref)
        for attribute in ("construction_materials", "utility_connections", "structural_capacity", "defect_inventory"):
            assertion("BUILDING", bid, attribute, "not_assessed", ref)

    for p in premises:
        pid, ref = p["candidate_premises_id"], p["source_ref"]
        premises_profiles.append({
            "candidate_premises_id": pid, "premises_type": p["premises_type"],
            "primary_function": p["primary_function"], "floor_level": p["floor_code"],
            "orientation": "unknown", "fitout_standard": "not_assessed",
            "occupancy_suitability": "not_assessed", "security_boundary": "not_assessed",
            "accessibility_state": "not_assessed",
            **provenance(ref, "Premises function and floor association are generated; fit-out and suitability are not inspected."),
        })
        measure("PREMISES", pid, "net_floor_area", p["floor_area_m2"], "m2", "design", ref)
        measure("PREMISES", pid, "usable_area", p["floor_area_m2"] * 0.88, "m2", "design", ref)
        room_types = ("primary_space", "circulation_space", "service_space")
        for index, room_type in enumerate(room_types, start=1):
            premises_rooms.append({
                "candidate_premises_id": pid, "room_code": f"R{index:02d}",
                "room_type": room_type, "floor_level": p["floor_code"],
                "area_m2": round(p["floor_area_m2"] * (0.65 if index == 1 else 0.175), 3),
                "accessibility_state": "not_assessed", "source_ref": ref,
                "actor_ref": ACTOR, "effective_from_tick": 0,
                "reason": "Illustrative internal space allocation; no measured floor plan exists.",
            })
        for utility_type in ("electricity", "water", "telecommunications"):
            utility("PREMISES", pid, utility_type, ref)
        for feature_type in ("corridor", "toilet"):
            feature("PREMISES", pid, feature_type, ref)
        for element in ("overall", "accessibility"):
            condition("PREMISES", pid, element, ref)
        for attribute in ("fitout_inventory", "utility_service", "occupancy_suitability"):
            assertion("PREMISES", pid, attribute, "not_assessed", ref)

    for u in units:
        uid, ref = u["candidate_unit_id"], u["source_ref"]
        unit_profiles.append({
            "candidate_unit_id": uid, "unit_class": u["unit_class"],
            "local_locator": None, "floor_level": u["floor_level"],
            "room_count": u["room_count"], "physical_capacity": None,
            "suitability_state": "not_assessed", "fitout_state": "not_assessed",
            "accessibility_state": "not_assessed",
            **provenance(ref, "Unit area and classification are generated design allocations; capacity and suitability are not assessed."),
        })
        measure("UNIT", uid, "net_floor_area", u["floor_area_m2"], "m2", "design", ref)
        measure("UNIT", uid, "usable_area", u["floor_area_m2"] * 0.88, "m2", "design", ref)
        for utility_type in ("electricity", "water"):
            utility("UNIT", uid, utility_type, ref)
        feature("UNIT", uid, "other", ref)
        condition("UNIT", uid, "overall", ref)
        for attribute in ("occupancy_capacity", "accessibility", "defect_inventory"):
            assertion("UNIT", uid, attribute, "not_assessed", ref)

    for a in access_points:
        aid, ref = a["candidate_access_point_id"], a["source_ref"]
        access_point_profiles.append({
            "candidate_access_point_id": aid, "access_type": "unknown",
            "access_modes": [], "directionality": "unknown", "control_type": "unknown",
            "availability_state": "not_assessed", "accessibility_state": "not_assessed",
            "emergency_egress": None, "emergency_egress_state": "not_assessed",
            "loading_capable": None, "loading_capability_state": "not_assessed",
            **provenance(ref, "Boundary location is geometric only; no door, gate, access mode or egress inspection has occurred."),
        })
        for feature_type in ("security_perimeter",):
            feature("ACCESS_POINT", aid, feature_type, ref)
        for element in ("door", "gate", "accessibility"):
            condition("ACCESS_POINT", aid, element, ref)
        for attribute in ("access_mode", "emergency_egress", "loading_capability", "public_access"):
            assertion("ACCESS_POINT", aid, attribute, "not_assessed", ref)

    body = {
        "schema": "saltwater-bp04-03-stage-e-physical-asset-candidates/1.0",
        "inventory_set_id": "BP04-03-STAGE-E-ASSET-INVENTORY-001",
        "source_dataset": source["dataset_id"],
        "candidate_manifest_sha256": candidates["manifest_sha256"],
        "parcel_dossier_manifest_sha256": dossiers["manifest_sha256"],
        "operational_approval": False,
        "coordinate_reference": CRS,
        "generator": GENERATOR,
        "effective_tick": 0,
        "generation": {
            "property_count": len(properties), "building_count": len(buildings),
            "premises_count": len(premises), "unit_count": len(units),
            "access_point_candidate_count": len(access_points),
            "access_connector_candidate_count": len(access_connectors),
            "profile_record_count": sum(len(v) for v in (property_profiles, building_profiles, premises_profiles, unit_profiles, access_point_profiles)),
            "measurement_record_count": len(measurements), "building_level_count": len(building_levels),
            "building_component_count": len(building_components), "premises_room_count": len(premises_rooms),
            "utility_system_count": len(utility_systems), "physical_feature_count": len(physical_features),
            "condition_assessment_count": len(condition_assessments),
            "physical_defect_count": len(physical_defects), "asset_assertion_count": len(asset_assertions),
            "properties_without_buildings": len(properties)-len(buildings),
            "resolved_source_entity_code_mappings": 100,
            "unresolved_source_entity_code_mappings": 0,
            "unresolved_source_spatial_mappings": 0,
            "operational_spatial_ids_assigned": 0,
            "canonical_addresses_created": 0,
            "operational_access_points_created": 0,
            "ownership_records_created": 0, "tenancy_records_created": 0,
            "occupancy_records_created": 0, "business_assignments_created": 0,
        },
        "properties": properties, "buildings": buildings,
        "premises": premises, "units": units, "access_points": access_points,
        "access_connectors": access_connectors,
        "profiles": {"properties": property_profiles, "buildings": building_profiles,
                     "premises": premises_profiles, "units": unit_profiles,
                     "access_points": access_point_profiles},
        "details": {"measurements": measurements, "building_levels": building_levels,
                    "building_components": building_components, "premises_rooms": premises_rooms,
                    "utility_systems": utility_systems, "physical_features": physical_features,
                    "condition_assessments": condition_assessments,
                    "physical_defects": physical_defects, "asset_assertions": asset_assertions},
        "geometry_audit": geometries,
        "limitations": [
            "All property sites inherit non-operational parcel candidate geometry.",
            "Building footprints and access points are generated design candidates, not surveyed or approved facts.",
            "Premises and unit areas are generated space allocations, not measured floor plans.",
            "Construction materials, utilities, condition, defects, room layouts and capacity remain unknown or not assessed unless separately evidenced.",
            "Access-point and connector candidates are geometric only; they do not establish doors, constructed paths, public/legal rights, emergency egress or traversable routes.",
            "No canonical addresses, operational spatial IDs, ownership, tenancy, occupancy, residents, business operators or police appointments are created.",
            "All 100 source records resolve to stable entity_code values; production spatial_id surrogate values are database-generated and remain unassigned until operational geography activation. Resolve them by entity_code in the target database.",
        ],
    }
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    body["manifest_sha256"] = hashlib.sha256(canonical).hexdigest()
    return body

def main():
    root = Path(__file__).resolve().parents[1]
    source = json.loads((root / "data/geography/saltwater-geography-v1.json").read_text(encoding="utf-8"))
    result = build_asset_inventory(source)
    Path("bp04-03-stage-e-physical-assets.json").write_text(
        json.dumps(result, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n",
        encoding="utf-8")
    print(json.dumps(result["generation"] | {
        "manifest_sha256": result["manifest_sha256"],
        "candidate_manifest_sha256": result["candidate_manifest_sha256"],
    }, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
