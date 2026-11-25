"""Diagnose the four building access candidates without same-parcel road frontage."""
from __future__ import annotations
import json
from pathlib import Path
from shapely.geometry import Polygon, LineString, shape
from shapely.ops import nearest_points
from runtime.parcel_candidate_generator import build_candidates
from runtime.parcel_dossier_generator import build_parcel_dossiers
from runtime.physical_asset_inventory_generator import build_asset_inventory
from runtime.road_corridor_audit import build_road_corridor_audit
from runtime.road_reserve_topology import build_road_reserve_topology

def main():
    root=Path(__file__).resolve().parents[1]
    source=json.loads((root/"data/geography/saltwater-geography-v1.json").read_text())
    candidates=build_candidates(source); dossiers=build_parcel_dossiers(source,candidates)
    assets=build_asset_inventory(source,candidates,dossiers)
    candidate_by_id={p["candidate_parcel_id"]:p for p in candidates["parcels"]}
    dossier_by_id={r["dossier"]["candidate_parcel_id"]:r for r in dossiers["parcels"]}
    prop_by_id={p["candidate_property_id"]:p for p in assets["properties"]}
    building_by_id={b["candidate_building_id"]:b for b in assets["buildings"]}
    corridors=build_road_corridor_audit(source)
    topology=build_road_reserve_topology(source,corridors)
    reserve=shape(topology["city_road_reserve_geometry"])
    segs=[]
    for s in corridors["segments"]:
        segs.append((s["segment_id"],s["road_id"],s["road_class"],LineString(s["centreline_geometry"])))
    missing=[a for a in assets["access_points"] if not a.get("road_link_candidate_id")]
    rows=[]
    for a in missing:
        b=building_by_id[a["building_id"]]; prop=prop_by_id[b["property_id"]]
        parcel=candidate_by_id[b["source_candidate_parcel_id"]]
        pg=Polygon(parcel["geometry"][0],parcel["geometry"][1:])
        point=shape({"type":"Point","coordinates":a["point_m"]})
        nearest=sorted((round(pg.boundary.distance(line),3),sid,rid,cls) for sid,rid,cls,line in segs)[:5]
        p1,p2=nearest_points(pg.boundary,reserve.boundary)
        rows.append({
            "access_candidate_id":a["candidate_access_point_id"],
            "building_id":b["candidate_building_id"],
            "property_id":prop["candidate_property_id"],
            "parcel_id":parcel["candidate_parcel_id"],
            "neighbourhood_id":parcel["source_neighbourhood_id"],
            "parcel_area_m2":round(pg.area,3),
            "parcel_to_road_reserve_boundary_distance_m":round(pg.boundary.distance(reserve.boundary),3),
            "nearest_road_reserve_boundary_point_m":[round(p1.x,3),round(p1.y,3)],
            "nearest_parcel_boundary_point_m":[round(p2.x,3),round(p2.y,3)],
            "nearest_road_centreline_segments":[{"distance_m":d,"segment_id":sid,"road_id":rid,"road_class":cls} for d,sid,rid,cls in nearest],
            "dossier_frontage_count":len(dossier_by_id[parcel["candidate_parcel_id"]]["frontages"]),
            "dossier_access_candidate_count":len(dossier_by_id[parcel["candidate_parcel_id"]]["access_candidates"]),
        })
    print(json.dumps({"missing_count":len(missing),"records":rows},indent=2,sort_keys=True))
if __name__=="__main__": main()
