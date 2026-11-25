"""Audit Saltwater's built-estate capacity against its global-hub canon."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
from collections import Counter, defaultdict
from runtime.property_tenure_generator import _expand_columnar
from runtime.property_world_generator import to_columnar_document

GENERATOR = "SW-GLOBAL-ESTATE-CAPACITY-AUDIT-001"

def _counts(rows, key):
    return dict(sorted(Counter(str(x.get(key) or "unspecified") for x in rows).items()))

def build_estate_capacity_audit(geography, world, businesses):
    properties, buildings = world["properties"], world["buildings"]
    premises, units = world["premises"], world["units"]
    establishments = businesses["establishments"]
    by_district = defaultdict(lambda: {"properties":0,"buildings":0,"premises":0,"units":0,"establishments":0})
    for x in properties: by_district[x["source_district_id"]]["properties"] += 1
    for x in buildings: by_district[next(p["source_district_id"] for p in properties if p["property_id"]==x["property_id"])]["buildings"] += 1
    prop_district = {x["property_id"]:x["source_district_id"] for x in properties}
    for x in premises: by_district[prop_district[x["property_id"]]]["premises"] += 1
    for x in units: by_district[prop_district[x["property_id"]]]["units"] += 1
    for x in establishments: by_district[x["district_id"]]["establishments"] += 1
    floors = [int(x.get("storeys_above") or 0) for x in buildings]
    gfa = sum(float(x.get("gross_floor_area_m2") or 0) for x in buildings)
    footprint = sum(float(x.get("footprint_area_m2") or 0) for x in buildings)
    sector_counts = _counts(businesses["businesses"], "sector")
    building_use = _counts(buildings, "building_use")
    land_use = _counts(properties, "land_use_code")
    unit_class = _counts(units, "unit_class")
    premises_type = _counts(premises, "premises_type")
    max_floors = max(floors, default=0)
    properties_with_buildings = {x["property_id"] for x in buildings}
    no_building = sum(1 for x in properties if x["property_id"] not in properties_with_buildings)
    district_rows = [{"district_id":k,**v} for k,v in sorted(by_district.items())]
    summary = {
      "district_count":len(geography["districts"]),
      "neighbourhood_count":len(geography["neighbourhoods"]),
      "mapped_land_extent_km2":(geography["coordinate_reference"]["extent"][2]-geography["coordinate_reference"]["extent"][0])*(geography["coordinate_reference"]["extent"][3]-geography["coordinate_reference"]["extent"][1])/1_000_000,
      "property_site_count":len(properties),"building_count":len(buildings),
      "properties_without_buildings":no_building,"premises_count":len(premises),
      "unit_count":len(units),"business_count":len(businesses["businesses"]),
      "establishment_count":len(establishments),
      "building_footprint_area_m2":round(footprint,3),
      "gross_floor_area_m2":round(gfa,3),
      "mean_storeys_above":round(sum(floors)/len(floors),3) if floors else 0,
      "maximum_storeys_above":max_floors,
      "vertical_profile_code":"GLOBAL-ESTATE-VERTICAL-V1",
      "buildings_at_least_10_storeys":sum(1 for x in floors if x>=10),
      "buildings_at_least_20_storeys":sum(1 for x in floors if x>=20),
      "establishments_per_building":round(len(establishments)/len(buildings),3) if buildings else 0,
      "businesses_by_sector":sector_counts,
      "properties_by_land_use":land_use,
      "buildings_by_use":building_use,
      "premises_by_type":premises_type,
      "units_by_class":unit_class,
      "district_asset_registers":district_rows,
      "people_records_created":0,"population_records_created":0
    }
    body={
      "schema":"saltwater-global-estate-capacity-audit/1.0",
      "dataset_id":"SW-GLOBAL-ESTATE-CAPACITY-AUDIT-V1",
      "canon_status":"CANONICAL_FICTIONAL_GAME_WORLD",
      "generator":GENERATOR,"city":"Saltwater","effective_tick":0,
      "summary":summary,
      "capacity_findings":[
        {"finding_id":"ESTATE-001","severity":"high","finding":"The first vertical-intensification phase establishes district-specific high-rise and mid-rise profiles, but the estate remains a single-building-per-property baseline and still lacks the multi-building campuses and specialised megasites expected of a world-leading global maritime, financial, corporate and logistics metropolis.","evidence":{"property_sites":len(properties),"buildings":len(buildings),"maximum_storeys":max_floors,"buildings_at_least_10_storeys":summary["buildings_at_least_10_storeys"],"buildings_at_least_20_storeys":summary["buildings_at_least_20_storeys"],"gross_floor_area_m2":summary["gross_floor_area_m2"]},"required_response":"Continue with multi-building property campuses, major port and bonded-logistics terminals, intermodal freight and passenger complexes, export-manufacturing estates, corporate headquarters campuses and specialist international institutions."},
        {"finding_id":"ESTATE-002","severity":"high","finding":"The current 10,000-business registry is a useful opening register but its physical capacity and sector depth must be tested against international parent groups, subsidiaries, branches, large employers and major operating establishments.","evidence":{"businesses":len(businesses["businesses"]),"establishments":len(establishments),"sectors":len(sector_counts)},"required_response":"Model corporate groups and legal entities separately from establishments; increase major international and national operating campuses without creating additional people records."},
        {"finding_id":"ESTATE-003","severity":"high","finding":"The current mapped extent is 108 square kilometres and the road/parcel estate must be assessed for port expansion, freight yards, customs, airport/intermodal interchange, financial district and high-density mixed-use capacity.","evidence":{"mapped_land_extent_km2":summary["mapped_land_extent_km2"],"districts":summary["district_count"],"neighbourhoods":summary["neighbourhood_count"]},"required_response":"Develop an integrated land-use and transport expansion plan within the single contiguous city-state; do not create a second city or off-map playable territory."}
      ],
      "design_constraints":{
        "population_cap":10000,
        "population_cap_does_not_limit":"business_entities, corporate scale, buildings, floor area, port throughput, cargo, vessel movements, passenger flows or transient activity",
        "one_city_only":True,"one_contiguous_city_state":True,
        "no_people_created":True,"no_geometry_mutated":True,
        "no_operational_property_records_created":True,
        "no_financial_postings_created":True
      },
      "lineage":{"geography":"SW-GEOGRAPHY-V1","property_world":"SW-PROPERTY-WORLD-V1","business_registry":"SW-BUSINESS-REGISTRY-V1"}
    }
    body["manifest_sha256"]=hashlib.sha256(json.dumps(body,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
    return body

def main():
    root=Path(__file__).resolve().parents[1]
    def load(path): return _expand_columnar(json.loads((root/path).read_text(encoding="utf-8")))
    geography=json.loads((root/"data/geography/saltwater-geography-v1.json").read_text(encoding="utf-8"))
    data=build_estate_capacity_audit(geography,load("data/property/saltwater-property-world-v1.json"),load("data/business/saltwater-business-registry-v1.json"))
    out=root/"data/property/saltwater-global-estate-capacity-audit-v1.json"
    doc=to_columnar_document(data);doc["schema"]="saltwater-global-estate-capacity-audit-columnar/1.0"
    out.write_text(json.dumps(doc,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(data["summary"]|{"manifest_sha256":data["manifest_sha256"],"output_bytes":out.stat().st_size,"capacity_findings":data["capacity_findings"]},indent=2,sort_keys=True))
if __name__=="__main__": main()
