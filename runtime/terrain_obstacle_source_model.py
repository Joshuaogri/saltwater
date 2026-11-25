"""Read-only terrain, elevation and physical-obstacle source inventory."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

GENERATOR = "BP04-03-TERRAIN-OBSTACLE-SOURCE-MODEL-V1"
MODEL_VERSION = "SW-TERRAIN-OBSTACLE-001"
SOURCE_TYPES = {"elevation_surface","contour_line","spot_elevation","terrain_feature","retaining_structure","wall","fence","gate","drainage_structure","natural_barrier","other_physical_obstacle"}
UNKNOWN_FIELDS = {"elevation_m":None,"vertical_datum":None,"gradient_degrees":None,"height_m":None,"width_m":None,"material":None,"condition":"not_assessed","continuity":"not_assessed","traversal_restriction":"unknown","pedestrian_passability":"not_assessed","vehicle_passability":"not_assessed","accessibility":"not_assessed","legal_access":"not_assessed","emergency_egress":"not_assessed"}

def build_source_inventory(source: dict, source_bytes: bytes | None = None) -> dict:
    dataset_id=source.get("dataset_id")
    if not dataset_id: raise ValueError("Source dataset must have a stable dataset_id")
    rows=[]; seen=set()
    for feature in source.get("features",[]):
        props=feature.get("properties") or {}; kind=props.get("entity_type")
        if kind not in SOURCE_TYPES: continue
        fid=feature.get("id")
        if not fid or fid in seen: raise ValueError("Physical source feature IDs must be present and unique")
        seen.add(fid)
        rows.append({"source_feature_id":fid,"source_dataset_id":dataset_id,"source_version":props.get("version",dataset_id),"source_entity_type":kind,"source_name":props.get("name"),"source_geometry_type":(feature.get("geometry") or {}).get("type"),"source_geometry":feature.get("geometry"),"source_attributes":props,"evidence_state":"SOURCE_FEATURE_PRESENT_UNASSESSED",**UNKNOWN_FIELDS,"source_ref":f"{dataset_id}:{fid}","actor_ref":GENERATOR,"confidence_code":"documented_source_feature","review_state":"UNREVIEWED_SOURCE_INVENTORY"})
    raw=source_bytes if source_bytes is not None else json.dumps(source,sort_keys=True,separators=(",",":")).encode()
    counts={kind:sum(r["source_entity_type"]==kind for r in rows) for kind in sorted(SOURCE_TYPES)}
    checks={
      "source_feature_ids_unique":len(seen)==len(rows),
      "all_rows_have_source_lineage":all(r["source_ref"].startswith(dataset_id+":") for r in rows),
      "all_unprovided_measurements_remain_null":all(all(r[k] is None for k in ("elevation_m","gradient_degrees","height_m","width_m","material")) for r in rows),
      "all_traversability_and_access_states_remain_unassessed":all(all(r[k] in ("unknown","not_assessed") for k in ("traversal_restriction","pedestrian_passability","vehicle_passability","accessibility","legal_access","emergency_egress")) for r in rows),
      "no_operational_approval":all(r["review_state"]=="UNREVIEWED_SOURCE_INVENTORY" for r in rows)}
    return {"schema":"saltwater-bp04-03-terrain-obstacle-source-inventory/1.0","model_id":MODEL_VERSION,"generator":GENERATOR,"source_dataset_id":dataset_id,"source_sha256":hashlib.sha256(raw).hexdigest(),"coordinate_reference":source.get("coordinate_reference"),"operational_approval":False,"summary":{"source_feature_count":len(rows),"source_type_counts":counts,"elevation_surfaces":counts["elevation_surface"],"contour_lines":counts["contour_line"],"spot_elevations":counts["spot_elevation"],"terrain_features":counts["terrain_feature"],"retaining_structures":counts["retaining_structure"],"walls":counts["wall"],"fences":counts["fence"],"gates":counts["gate"],"drainage_structures":counts["drainage_structure"],"natural_barriers":counts["natural_barrier"],"other_physical_obstacles":counts["other_physical_obstacle"],"elevation_assessed_count":0,"gradient_assessed_count":0,"obstacle_condition_assessed_count":0,"traversability_assessed_count":0},"records":sorted(rows,key=lambda r:r["source_feature_id"]),"checks":checks,"passed_checks":sum(checks.values()),"failed_checks":[k for k,v in checks.items() if not v],"operational_seed_eligible":False,"database_write_performed":False,"approval_note":"Source inventory only. A mapped terrain polygon is not an elevation model or barrier. Absence from this dataset is not proof of physical absence. No gradient, height, width, material, condition, obstruction, route passability, accessibility, legal access or egress is inferred."}

def main():
    root=Path(__file__).resolve().parents[1]; path=root/"data/geography/saltwater-geography-v1.json"; raw=path.read_bytes()
    print(json.dumps(build_source_inventory(json.loads(raw),raw),indent=2,sort_keys=True))
if __name__=="__main__": main()
