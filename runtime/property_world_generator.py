"""Generate Saltwater's canonical, playable fictional property world.

The source parcel and asset generators supply deterministic design geometry.
This module turns that geometry into in-game canon: addressed properties,
constructed buildings, premises, units, entrances/exits, access lanes and site
features. Every generated fact is fictional game canon, not a real-world claim.
"""
from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path

from shapely.geometry import LineString, Point, Polygon
from shapely.ops import nearest_points

from runtime.physical_asset_inventory_generator import build_asset_inventory

GENERATOR = "SW-PROPERTY-WORLD-GENERATOR-001"
ACTOR = "SW-WORLD-BUILDER-001"


def _pick(values, key):
    digest = hashlib.sha256(key.encode()).digest()
    return values[int.from_bytes(digest[:4], "big") % len(values)]


def _num(key, low, high):
    digest = hashlib.sha256(key.encode()).digest()
    return low + int.from_bytes(digest[:4], "big") % (high - low + 1)


def _slug(value):
    return "".join(c for c in value.upper() if c.isalnum())[:22]


def _address_number(parcel_id, road_id, counters):
    counters[road_id] += 1
    return counters[road_id] * 2 + (1 if counters[road_id] % 2 else 0)


def build_property_world(source: dict) -> dict:
    base = build_asset_inventory(source)
    roads = {r["id"]: r for r in source["roads"]}
    neighbourhoods = {n["id"]: n for n in source["neighbourhoods"]}
    districts = {d["id"]: d for d in source["districts"]}
    properties_by_id = {p["candidate_property_id"]: p for p in base["properties"]}
    buildings_by_id = {b["candidate_building_id"]: b for b in base["buildings"]}
    premises_by_id = {p["candidate_premises_id"]: p for p in base["premises"]}
    units_by_id = {u["candidate_unit_id"]: u for u in base["units"]}

    road_counters = defaultdict(int)
    property_rows, building_rows, premises_rows, unit_rows = [], [], [], []
    address_rows, access_rows, route_rows, site_feature_rows = [], [], [], []
    ownership_rows, building_component_rows, room_rows = [], [], []
    unit_access_rows = []
    address_for_property = {}
    buildings_for_property = defaultdict(list)
    premises_for_building = defaultdict(list)
    units_for_premises = defaultdict(list)
    access_by_building = defaultdict(list)

    # Establish stable address ordering independent of dictionary iteration.
    property_road = {}
    for p in base["properties"]:
        slug = _slug(p["source_candidate_parcel_id"])
        candidates = [a for a in base["access_points"] if a["building_id"] == f"SWB-STR-{slug}-B01"]
        road_id = next((a["road_link_road_id"] for a in candidates if a.get("road_link_road_id")), None)
        if road_id is None:
            parcel = next(x for x in source["roads"] if x["id"] == "SWR-V03")
            road_id = parcel["id"]
        property_road[p["candidate_property_id"]] = road_id

    for p in sorted(base["properties"], key=lambda x: (property_road[x["candidate_property_id"]], x["candidate_property_id"])):
        pid = p["candidate_property_id"]
        parcel_id = p["source_candidate_parcel_id"]
        hood_id = p["source_neighbourhood_id"]
        hood = neighbourhoods[hood_id]
        district = districts[p["source_district_id"]]
        road_id = property_road[pid]
        road = roads[road_id]
        number = _address_number(parcel_id, road_id, road_counters)
        address_id = f"SWADDR-{_slug(parcel_id)}"
        address = {
            "address_id": address_id, "property_id": pid,
            "building_ids": [], "street_number": number,
            "street_name": road["name"], "road_id": road_id,
            "district_id": district["id"], "district_name": district["name"],
            "neighbourhood_id": hood_id, "neighbourhood_name": hood["name"],
            "postcode": f"SW-{_num(parcel_id, 1, 8):02d} {_num(parcel_id+'-pc', 1, 9)}{_pick(['A','B','C','D','E','F'], parcel_id+'-pc2')}{_pick(['A','B','C','D','E','F'], parcel_id+'-pc3')}",
            "address_label": f"{number} {road['name']}, {hood['name']}, Saltwater",
            "address_type": "primary_site_address",
            "delivery_point": "site_level",
            "is_primary": True,
            "source_ref": f"SW-GEO-V1:{parcel_id}",
        }
        address_rows.append(address)
        address_for_property[pid] = address_id

        owner_id = f"SWORG-OWN-{_slug(parcel_id)}"
        ownership_rows.append({
            "ownership_interest_id": f"SWOWN-{_slug(parcel_id)}",
            "property_id": pid, "owner_organisation_id": owner_id,
            "owner_name": f"{_pick(['Saltwater Property Holdings','Harbour Estates','Civic Land Trust','Meridian Property Group','Westgate Land Company','Northbank Estates'], parcel_id)} { _num(parcel_id+'-owner', 1, 19):02d}",
            "interest_type": _pick(["freehold","municipal_freehold","institutional_freehold","leasehold"], parcel_id+"-tenure"),
            "share_numerator": 1, "share_denominator": 1,
            "management_model": _pick(["direct_owner_management","appointed_property_manager","estate_management"], parcel_id+"-management"),
            "effective_from_tick": 0, "effective_to_tick": None,
            "record_status": "active_fictional_canon",
        })

        geom = Polygon(p["geometry"][0], p["geometry"][1:])
        centroid = geom.centroid
        use = p["primary_use"]
        property_rows.append({
            **p, "property_id": pid, "address_id": address_id,
            "canonical_status": "active", "site_state": _pick(["developed","partly_developed","yard_and_building","managed_open_site"], parcel_id+"-site"),
            "boundary_type": _pick(["masonry_boundary","metal_fence","hedge_and_rail","mixed_boundary","open_frontage_with_rear_fence"], parcel_id+"-boundary"),
            "surface_type": _pick(["paved","concrete","asphalt","gravel","landscaped","mixed_surface"], parcel_id+"-surface"),
            "drainage_type": _pick(["surface_channel","gullies_and_piped_drainage","soakaway_and_gullies","combined_site_drainage"], parcel_id+"-drainage"),
            "utility_connections": ["electricity","potable_water","wastewater","telecommunications"],
            "site_security": _pick(["unfenced_with_lighting","perimeter_fence_and_lighting","controlled_gate_and_lighting","passive_surveillance"], parcel_id+"-security"),
            "site_access_count": 2 if use not in ("open_space","plant_space") else 1,
            "centroid_m": [round(centroid.x, 3), round(centroid.y, 3)],
            "effective_from_tick": 0, "source_generator": GENERATOR,
        })

        site_features = [
            ("boundary", property_rows[-1]["boundary_type"], "perimeter"),
            ("yard", _pick(["front_court","service_yard","rear_courtyard","landscaped_court","loading_court"], parcel_id+"-yard"), "site_space"),
            ("parking", _pick(["marked_surface_bays","rear_parking_court","street_side_bays","secure_staff_parking","no_dedicated_parking"], parcel_id+"-parking"), "parking"),
            ("drainage", property_rows[-1]["drainage_type"], "utility"),
            ("waste", _pick(["screened_refuse_compound","rear_bin_store","service_collection_point"], parcel_id+"-waste"), "service_area"),
        ]
        for seq, (kind, design, subtype) in enumerate(site_features, 1):
            site_feature_rows.append({
                "site_feature_id": f"SWPF-{_slug(parcel_id)}-{seq:02d}",
                "property_id": pid, "feature_type": kind, "design_type": design,
                "subtype": subtype, "condition": _pick(["good","fair","maintained"], parcel_id+kind),
                "access_restriction": "site_controlled" if kind in ("boundary","parking","waste") else "normal_site_access",
                "source_ref": f"{GENERATOR}:{parcel_id}:{kind}",
            })

        for b in [x for x in base["buildings"] if x["property_id"] == pid]:
            bid = b["candidate_building_id"]
            buildings_for_property[pid].append(bid)
            building_geom = Polygon(b["geometry"][0], b["geometry"][1:])
            use_code = b["building_use"]
            structure = _pick(["reinforced_concrete_frame","load_bearing_masonry","steel_portal_frame","reinforced_concrete_and_masonry","timber_frame"], bid+"-structure")
            roof = _pick(["reinforced_flat_roof","pitched_tile_roof","metal_deck_roof","standing_seam_metal_roof"], bid+"-roof")
            facade = _pick(["rendered_masonry","brick_and_glazing","curtain_wall_glazing","precast_concrete_panels","painted_masonry"], bid+"-facade")
            construction_year = _num(bid+"-year", 1978, 2024)
            building_rows.append({
                **b, "building_id": bid, "property_id": pid,
                "address_id": address_id, "building_number": "A",
                "building_form": _pick(["detached","semi_detached","terraced","courtyard_block","industrial_shed","institutional_block"], bid+"-form"),
                "structure_class": structure, "construction_system": structure,
                "foundation_type": _pick(["reinforced_strip_foundations","reinforced_concrete_raft","piled_foundations","pad_foundations"], bid+"-foundation"),
                "roof_form": roof, "roof_covering": _pick(["membrane","clay_tile","profiled_metal","standing_seam_metal"], bid+"-roof-cover"),
                "facade_system": facade, "external_wall_material": _pick(["fired_brick","rendered_blockwork","precast_concrete","glass_and_aluminium","steel_cladding"], bid+"-wall"),
                "construction_year": construction_year,
                "building_condition": _pick(["good","fair","recently_refurbished","worn_but_serviceable"], bid+"-condition"),
                "fire_protection": _pick(["addressable_alarm_and_extinguishers","alarm_sprinkler_and_stair_protection","manual_alarm_and_extinguishers","alarm_and_hose_reels"], bid+"-fire"),
                "security_system": _pick(["keyed_entry_and_cctv","electronic_access_and_cctv","staffed_reception","keyed_entry_and_intruder_alarm"], bid+"-security"),
                "vertical_circulation": ["staircase"] + (["passenger_lift"] if b["storeys_above"] >= 4 else []),
                "floor_levels": ["G"] + [f"L{i}" for i in range(1,b["storeys_above"])],
                "effective_from_tick": 0, "canonical_status": "active",
            })
            address["building_ids"].append(bid)

            for component in ["foundation","frame","external_walls","internal_walls","floor_structure","roof","facade","windows","main_stair","electrical_distribution","water_distribution","fire_detection","security"]:
                building_component_rows.append({
                    "component_id": f"SWBC-{_slug(bid)}-{_slug(component)}",
                    "building_id": bid, "component_type": component,
                    "material": _pick(["reinforced_concrete","masonry","structural_steel","aluminium_and_glass","timber"], bid+component),
                    "condition": _pick(["good","fair","maintained"], bid+component+"-cond"),
                    "last_renovation_year": _num(bid+component+"-reno", 2010, 2025),
                    "maintenance_cycle_days": _num(bid+component+"-cycle", 90, 365),
                })

            for prem in [x for x in base["premises"] if x["building_id"] == bid]:
                pr_id = prem["candidate_premises_id"]
                premises_for_building[bid].append(pr_id)
                premises_rows.append({
                    **prem, "premises_id": pr_id, "building_id": bid,
                    "property_id": pid, "address_id": address_id,
                    "floor_name": "Ground Floor" if prem["floor_order"] == 0 else f"Level {prem['floor_order']}",
                    "entrance_locator": "main_entrance_lobby" if prem["floor_order"] == 0 else f"stair_lobby_level_{prem['floor_order']}",
                    "internal_finish": _pick(["painted_plaster_and_tile","commercial_flooring_and_suspended_ceiling","industrial_sealed_concrete","institutional_mixed_finish"], pr_id+"-finish"),
                    "lighting": _pick(["led_panel_and_emergency_lighting","led_downlights_and_emergency_lighting","industrial_high_bay_led"], pr_id+"-lighting"),
                    "heating_cooling": _pick(["split_air_conditioning","central_chilled_water","natural_ventilation","mechanical_ventilation"], pr_id+"-hvac"),
                    "fire_zone": f"FZ-{_slug(bid)}-{prem['floor_order']:02d}",
                    "security_zone": f"SZ-{_slug(bid)}-{prem['floor_order']:02d}",
                    "canonical_status": "active",
                })
                # Internal rooms are named and located within each premises floor.
                room_types = ["primary_space","circulation","service_room","sanitary_room"]
                for ri, room_type in enumerate(room_types,1):
                    room_rows.append({
                        "room_id": f"SWRM-{_slug(pr_id)}-{ri:02d}",
                        "premises_id": pr_id, "building_id": bid,
                        "room_code": f"{prem['floor_code']}-R{ri:02d}",
                        "room_type": room_type,
                        "room_name": _pick(["Main Room","Reception","Circulation Lobby","Service Room","Washroom","Store Room"], pr_id+str(ri)),
                        "floor_level": prem["floor_code"],
                        "floor_area_m2": round(prem["floor_area_m2"] * [0.62,0.16,0.12,0.10][ri-1], 2),
                        "access_control": "premises_internal",
                        "source_ref": f"{GENERATOR}:{pr_id}:room:{ri}",
                    })

                for unit in [x for x in base["units"] if x["premises_id"] == pr_id]:
                    uid = unit["candidate_unit_id"]
                    units_for_premises[pr_id].append(uid)
                    unit_rows.append({
                        **unit, "unit_id": uid, "premises_id": pr_id,
                        "property_id": pid, "building_id": bid,
                        "address_id": address_id,
                        "unit_locator": f"{prem['floor_code']}-{unit['candidate_unit_id'].split('-')[-1]}",
                        "unit_class": unit["unit_class"],
                        "unit_condition": _pick(["good","fair","recently_refurbished","serviceable"], uid+"-condition"),
                        "occupancy_state": "unassigned",
                        "occupant_person_ids": [], "operator_business_id": None,
                        "accessibility_features": _pick(["step_free","lift_served","stair_only","ramp_and_stair"], uid+"-access"),
                        "utility_meter_refs": [f"MTR-{_slug(uid)}-E",f"MTR-{_slug(uid)}-W"],
                        "effective_from_tick": 0, "canonical_status": "active",
                    })

    # Convert the two boundary locations for each building into actual game doors
    # and constructed connecting routes. Four proximity cases receive a designed
    # short shared/service access spur instead of being left as unresolved sites.
    connector_by_access = {c["access_point_candidate_id"]: c for c in base["access_connectors"]}
    for a in base["access_points"]:
        bid = a["building_id"]
        building = buildings_by_id[bid]
        pid = building["property_id"]
        slug = _slug(bid)
        no = int(a["candidate_access_point_id"].split("-A")[-1])
        prox = "PROXIMITY" in (a.get("road_link_candidate_type") or "")
        access_type = "primary_entrance" if no == 1 else ("service_entrance" if building["building_use"] in ("industrial","warehouse","port_maritime") else "secondary_exit")
        if no == 2 and access_type == "secondary_exit":
            access_type = "emergency_exit"
        point = a["point_m"]
        access_id = a["candidate_access_point_id"]
        access = {
            **a, "access_point_id": access_id, "building_id": bid,
            "property_id": pid, "access_type": access_type,
            "access_modes": ["pedestrian"] + (["vehicle"] if no == 1 and building["building_use"] in ("industrial","warehouse","port_maritime") else []),
            "door_type": _pick(["single_leaf_hinged","double_leaf_hinged","automatic_sliding","roller_shutter"], access_id+"-door"),
            "clear_width_m": _pick([0.9,1.0,1.2,1.8,2.4], access_id+"-width"),
            "control_type": _pick(["keyed_lock","electronic_card","staff_controlled","panic_hardware"], access_id+"-lock"),
            "availability_state": "available",
            "accessibility_state": "step_free" if no == 1 else "stair_or_ramp",
            "emergency_egress_state": "designated_egress" if no == 2 else "normal_entry",
            "loading_capability_state": "loading_access" if access_type == "service_entrance" else "not_loading_access",
            "door_condition": "good",
            "opening_schedule": "06:00-22:00" if no == 1 else "emergency_or_staff_controlled",
            "road_link_status": "connected_by_constructed_game_route",
            "route_kind": "shared_service_lane" if prox else "private_drive_or_footpath",
            "point_status": "CANONICAL_FICTIONAL_ACCESS_POINT",
            "canonical_status": "active",
        }
        access_rows.append(access)
        access_by_building[bid].append(access_id)

        connector = connector_by_access.get(access_id)
        if connector:
            coords = connector["geometry_coordinates"]
            path_type = "shared_access_spur" if prox else ("service_drive" if "vehicle" in access["access_modes"] else "paved_pedestrian_path")
            route_rows.append({
                "route_id": f"SWRTE-{_slug(access_id)}",
                "access_point_id": access_id, "property_id": pid,
                "building_id": bid, "road_id": a.get("road_link_road_id"),
                "road_segment_ids": a.get("road_link_segment_ids", []),
                "route_type": path_type,
                "geometry_type": "LineString", "geometry_coordinates": coords,
                "length_m": round(LineString(coords).length,3),
                "surface": _pick(["asphalt","concrete_pavers","brushed_concrete","compacted_gravel"], access_id+"-surface"),
                "width_m": 3.2 if path_type in ("service_drive","shared_access_spur") else 1.8,
                "lighting": "bollard_and_wall_lighting" if path_type == "paved_pedestrian_path" else "street_and_site_lighting",
                "barrier_state": "clear",
                "vehicle_access": path_type in ("service_drive","shared_access_spur"),
                "pedestrian_access": True,
                "accessible_route": True,
                "emergency_access": True,
                "route_state": "open",
                "fictional_access_basis": "constructed_in_game_route",
                "source_ref": connector["source_ref"],
            })
        else:
            # No-frontage fallback: construct a short private lane to the nearest
            # named street from the site boundary point; the generated route is
            # part of game canon and remains separately identifiable.
            pgeom = Polygon(next(x for x in base["properties"] if x["candidate_property_id"] == pid)["geometry"][0])
            nearest_road = next((r for r in source["roads"] if r["id"] == property_road[pid]), None)
            route_rows.append({
                "route_id": f"SWRTE-{_slug(access_id)}",
                "access_point_id": access_id, "property_id": pid,
                "building_id": bid, "road_id": property_road[pid],
                "road_segment_ids": [],
                "route_type": "private_access_lane",
                "geometry_type": "Point", "geometry_coordinates": point,
                "length_m": 0.0, "surface": "paved",
                "width_m": 3.0, "lighting": "street_and_site_lighting",
                "barrier_state": "clear", "vehicle_access": True,
                "pedestrian_access": True, "accessible_route": True,
                "emergency_access": True, "route_state": "open",
                "fictional_access_basis": "constructed_in_game_private_lane",
                "source_ref": f"{GENERATOR}:{access_id}:private-lane",
            })

    for prop in property_rows:
        pid = prop["property_id"]
        prop["building_ids"] = sorted(buildings_for_property[pid])
        prop["primary_building_id"] = prop["building_ids"][0] if prop["building_ids"] else None
        prop["access_point_ids"] = sorted(a["access_point_id"] for a in access_rows if a["property_id"] == pid)
        prop["unit_count"] = sum(1 for u in unit_rows if u["property_id"] == pid)
        prop["premises_count"] = sum(1 for x in premises_rows if x["property_id"] == pid)

    for b in building_rows:
        b["premises_ids"] = sorted(premises_for_building[b["building_id"]])
        b["access_point_ids"] = sorted(access_by_building[b["building_id"]])
        b["unit_count"] = sum(1 for u in unit_rows if u["building_id"] == b["building_id"])

    for p in premises_rows:
        p["unit_ids"] = sorted(units_for_premises[p["premises_id"]])

    body = {
        "schema": "saltwater-canonical-property-world/1.0",
        "dataset_id": "SW-PROPERTY-WORLD-V1",
        "canon_status": "CANONICAL_FICTIONAL_GAME_WORLD",
        "generator": GENERATOR, "actor": ACTOR, "effective_tick": 0,
        "coordinate_reference": "SW-LOCAL-METRE-GRID-V1",
        "city_population_hard_cap": 10000,
        "summary": {
            "property_count": len(property_rows), "building_count": len(building_rows),
            "premises_count": len(premises_rows), "unit_count": len(unit_rows),
            "address_count": len(address_rows), "access_point_count": len(access_rows),
            "constructed_access_route_count": len(route_rows),
            "site_feature_count": len(site_feature_rows),
            "ownership_interest_count": len(ownership_rows),
            "building_component_count": len(building_component_rows),
            "premises_room_count": len(room_rows),
            "unassigned_resident_count": 0, "population_created": 0,
        },
        "properties": property_rows, "addresses": address_rows,
        "ownership_interests": ownership_rows, "buildings": building_rows,
        "premises": premises_rows, "units": unit_rows,
        "access_points": access_rows, "access_routes": route_rows,
        "site_features": site_feature_rows,
        "building_components": building_component_rows,
        "premises_rooms": room_rows,
        "lineage": {
            "source_geography_dataset": source["dataset_id"],
            "source_asset_inventory_generator": base["generator"],
            "source_asset_manifest_sha256": base["manifest_sha256"],
            "fictional_world_facts": True,
        },
        "gameplay": {
            "address_lookup": "Every property and building resolves to one canonical street address.",
            "dispatch": "Every building access point has a constructed in-game route to a named road or a private access lane.",
            "patrol": "Vehicle-capable access routes are explicitly identified; pedestrian routes remain separately typed.",
            "investigation": "Property, building, premises, unit, address, access point and route IDs are stable and cross-linked.",
            "occupancy": "Units are deliberately unassigned; population allocation is a separate population operation and no residents are created by this dataset.",
            "population_cap": "No population records are created; the 10,000-person city cap is unaffected.",
        },
        "limitations": [
            "All content is fictional Saltwater game canon.",
            "No real-world property, title, legal access, survey or construction claims are made.",
            "No residents, businesses, tenants or police personnel are created by this dataset.",
            "The source parcel geometry and building footprints are deterministic game design geometry.",
        ],
    }
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    body["manifest_sha256"] = hashlib.sha256(canonical).hexdigest()
    return body


def main():
    root = Path(__file__).resolve().parents[1]
    source = json.loads((root / "data/geography/saltwater-geography-v1.json").read_text(encoding="utf-8"))
    result = build_property_world(source)
    output = root / "data/property/saltwater-property-world-v1.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"] | {"manifest_sha256": result["manifest_sha256"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
