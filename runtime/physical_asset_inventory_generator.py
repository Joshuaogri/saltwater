"""Deterministic BP04-03 Stage E physical-asset design inventory.

All geometry and physical specifications are generated fictional design candidates.
This module deliberately creates no operational geography IDs, addresses,
ownership, tenancy, occupancy, business assignments or production records.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from shapely.geometry import Point, Polygon, box
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
    properties, buildings, premises, units, access_points = [], [], [], [], []
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
        property_class, use_code, floors, spaces_per_floor, unit_area = USE[land_use]
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

        building_code = f"SWB-STR-{slug}-B01"
        building_name = _name("BUILDING", parcel_id, occupied)
        storeys = floors
        footprint_area = footprint.area
        gross_floor_area = footprint_area * storeys
        building = {
            "candidate_building_id": building_code, "display_name": building_name,
            "property_id": property_code, "source_candidate_parcel_id": parcel_id,
            "building_use": use_code, "building_form": "other",
            "structure_class": "unknown", "construction_system": "unknown",
            "foundation_type": "unknown", "roof_form": "unknown",
            "roof_covering": "unknown", "facade_system": "unknown",
            "storeys_above": storeys, "storeys_below": 0,
            "height_m": round(storeys * 3.6, 3), "height_basis": "generated_design_value",
            "footprint_area_m2": round(footprint_area, 3),
            "gross_floor_area_m2": round(gross_floor_area, 3),
            "geometry": _rings(footprint),
            "geometry_status": "GENERATED_DESIGN_FOOTPRINT_NOT_SURVEYED",
            "source_ref": f"{SOURCE}:{parcel_id}:building-layout-v1",
            "actor_ref": ACTOR, "confidence_code": "estimated",
            "effective_from_tick": 0, "recorded_status": "generated_design_candidate",
        }
        buildings.append(building)

        # One separately identified premises per designed floor. These are
        # spatially subordinate spaces, not operator or occupancy assignments.
        for floor in range(storeys):
            premises_code = f"SWPR-{slug}-F{floor:02d}"
            premises_name = _name("PREMISES", f"{parcel_id}:F{floor:02d}", occupied)
            floor_area = footprint_area * 0.82
            premises_type = {
                "residential": "residential_common", "mixed_use": "suite", "commercial": "office",
                "civic": "civic_room", "education": "department", "industrial": "industrial_bay",
                "freight_logistics": "warehouse", "port_maritime": "warehouse",
                "waterfront": "suite", "utility": "plant_space",
            }.get(land_use, "other")
            premises.append({
                "candidate_premises_id": premises_code, "display_name": premises_name,
                "building_id": building_code, "property_id": property_code,
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
                unit_code = f"SWU-{slug}-F{floor:02d}-U{unit_no:02d}"
                unit_name = _name("UNIT", f"{parcel_id}:F{floor:02d}:U{unit_no:02d}", occupied)
                units.append({
                    "candidate_unit_id": unit_code, "display_name": unit_name,
                    "premises_id": premises_code, "building_id": building_code,
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
        road_point = None
        if frontage_candidates:
            nearest = min(frontage_candidates,
                          key=lambda a: ((a["candidate_x_m"]-footprint.centroid.x)**2 +
                                         (a["candidate_y_m"]-footprint.centroid.y)**2,
                                         a["access_candidate_id"]))
            road_point = Point(nearest["candidate_x_m"], nearest["candidate_y_m"])
        for access_no, fraction in ((1, .25), (2, .75)):
            boundary_point = (nearest_points(footprint.boundary, road_point)[0]
                              if access_no == 1 and road_point is not None
                              else footprint.boundary.interpolate(footprint.boundary.length * fraction))
            access_code = f"SWA-{slug}-B01-A{access_no:02d}"
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
                "road_link_candidate_id": nearest["access_candidate_id"] if road_point is not None else None,
                "source_ref": f"{SOURCE}:{building_code}:access:{access_no}",
                "actor_ref": ACTOR, "confidence_code": "estimated",
                "effective_from_tick": 0,
            })
        geometries.append({
            "property": property_code, "building": building_code,
            "footprint_area_m2": round(footprint_area, 3),
            "footprint_inside_property": bool(site.covers(footprint)),
        })

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
            "properties_without_buildings": len(properties)-len(buildings),
            "unresolved_source_spatial_mappings": 100,
            "operational_spatial_ids_assigned": 0,
            "canonical_addresses_created": 0,
            "operational_access_points_created": 0,
            "ownership_records_created": 0, "tenancy_records_created": 0,
            "occupancy_records_created": 0, "business_assignments_created": 0,
        },
        "properties": properties, "buildings": buildings,
        "premises": premises, "units": units, "access_points": access_points,
        "geometry_audit": geometries,
        "limitations": [
            "All property sites inherit non-operational parcel candidate geometry.",
            "Building footprints and access points are generated design candidates, not surveyed or approved facts.",
            "Premises and unit areas are generated space allocations, not measured floor plans.",
            "Construction materials, utilities, condition, defects, room layouts and capacity remain unknown or not assessed unless separately evidenced.",
            "Access candidates do not establish doors, public rights, emergency egress or a traversable route to a road.",
            "No canonical addresses, operational spatial IDs, ownership, tenancy, occupancy, residents, business operators or police appointments are created.",
            "All 100 source-to-spatial-ID mappings remain explicit and unresolved.",
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
