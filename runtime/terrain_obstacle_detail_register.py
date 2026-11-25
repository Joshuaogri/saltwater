"""Detailed geometry-only terrain and obstacle source register for BP04-03."""
from __future__ import annotations
import hashlib, json, math
from pathlib import Path
from shapely.geometry import Polygon, shape
GENERATOR="BP04-03-TERRAIN-OBSTACLE-DETAIL-REGISTER-V1"
REGISTER_ID="SW-TERRAIN-OBSTACLE-DETAIL-001"
OBSTACLE_TYPES=("retaining_structure","wall","fence","gate","drainage_structure","natural_barrier","other_physical_obstacle")
TERRAIN_TYPES=("terrain_feature","elevation_surface","contour_line","spot_elevation")
def _bearing(a,b): return round((math.degrees(math.atan2(b[0]-a[0],b[1]-a[1]))+360)%360,3)
def build_detail_register(source:dict, route_corridors:list[dict]|None=None, source_bytes:bytes|None=None)->dict:
 dataset=source.get("dataset_id")
 if not dataset: raise ValueError("Missing source dataset ID")
 features=source.get("features",[]); seen=set(); terrain=[]; obstacles=[]
 for f in features:
  p=f.get("properties") or {}; kind=p.get("entity_type")
  if kind not in TERRAIN_TYPES+OBSTACLE_TYPES: continue
  fid=f.get("id")
  if not fid or fid in seen: raise ValueError("Physical feature IDs must be unique and present")
  seen.add(fid)
  (terrain if kind in TERRAIN_TYPES else obstacles).append(f)
 routes=route_corridors or []
 districts=[(d["id"],d["name"],Polygon([(d["x0"],d["y0"]),(d["x1"],d["y0"]),(d["x1"],d["y1"]),(d["x0"],d["y1"])])) for d in source.get("districts",[])]
 neighbourhoods=[(n["id"],n["name"],n["district_id"],shape(n["geometry"])) for n in source.get("neighbourhoods",[])]
 terrain_rows=[]
 for f in sorted(terrain,key=lambda x:x["id"]):
  geom=shape(f["geometry"]); p=f.get("properties") or {}
  if geom.is_empty or not geom.is_valid or geom.area<=0: raise ValueError("Invalid terrain geometry: "+f["id"])
  rings=[]
  for ri,ring in enumerate([geom.exterior,*geom.interiors],1):
   coords=[(float(x),float(y)) for x,y,*_ in ring.coords]; edges=[]
   for ei,(a,b) in enumerate(zip(coords,coords[1:]),1):
    length=math.hypot(b[0]-a[0],b[1]-a[1])
    if length<=0: raise ValueError("Zero-length terrain boundary edge")
    edges.append({"edge_id":f["id"]+"-R"+str(ri).zfill(2)+"-E"+str(ei).zfill(3),"start_xy_m":[a[0],a[1]],"end_xy_m":[b[0],b[1]],"planar_length_m":round(length,3),"bearing_degrees_from_north_clockwise":_bearing(a,b)})
   rings.append({"ring_id":f["id"]+"-R"+str(ri).zfill(2),"ring_role":"exterior" if ri==1 else "interior","closed":coords[0]==coords[-1],"vertex_count_including_closure":len(coords),"planar_perimeter_m":round(ring.length,3),"edges":edges})
  dh=[]
  for did,dname,dg in districts:
   it=geom.intersection(dg)
   if not it.is_empty and it.area>0: dh.append({"district_id":did,"district_name":dname,"intersection_area_m2":round(it.area,3),"terrain_area_share_percent":round(it.area/geom.area*100,5)})
  nh=[]
  for nid,nname,did,ng in neighbourhoods:
   it=geom.intersection(ng)
   if not it.is_empty and it.area>0: nh.append({"neighbourhood_id":nid,"neighbourhood_name":nname,"district_id":did,"intersection_area_m2":round(it.area,3),"terrain_area_share_percent":round(it.area/geom.area*100,5)})
  rh=[]
  for r in routes:
   line=shape(r["centreline_geometry"]); it=line.intersection(geom)
   if not it.is_empty: rh.append({"route_corridor_candidate_id":r["candidate_route_corridor_id"],"source_connector_candidate_id":r["source_connector_candidate_id"],"intersection_geometry_type":it.geom_type,"centreline_length_within_terrain_m":round(it.length,3),"intersection_state":"CROSSES_OR_TOUCHES_TERRAIN_GEOMETRY"})
  terrain_rows.append({"terrain_record_id":f["id"],"source_dataset_id":dataset,"source_version":p.get("version",dataset),"name":p.get("name"),"terrain_code":p.get("terrain","unknown"),"orientation_code":p.get("orientation","unknown"),"source_geometry_type":geom.geom_type,"source_geometry":f["geometry"],"source_ref":dataset+":"+f["id"],"geometry_status":"SOURCE_PLANNING_GEOMETRY_UNREVIEWED","planar_area_m2":round(geom.area,3),"planar_perimeter_m":round(geom.length,3),"bounding_box_xy_m":[round(v,3) for v in geom.bounds],"centroid_xy_m":[round(geom.centroid.x,3),round(geom.centroid.y,3)],"exterior_vertex_count":len(list(geom.exterior.coords))-1,"interior_ring_count":len(geom.interiors),"boundary_rings":rings,"district_intersections":dh,"neighbourhood_intersections":nh,"route_corridor_intersections":rh,"elevation_m":None,"vertical_datum":None,"gradient_degrees":None,"slope_direction_degrees":None,"surface_material":None,"condition":"not_assessed","traversal_restriction":"unknown","pedestrian_passability":"not_assessed","vehicle_passability":"not_assessed","accessibility":"not_assessed","legal_access":"not_assessed","emergency_egress":"not_assessed","review_state":"UNREVIEWED_GEOMETRY_DERIVED_DETAIL","actor_ref":GENERATOR,"confidence_code":"derived_from_source_planning_geometry_only"})
 obstacle_rows=[]
 for f in sorted(obstacles,key=lambda x:x["id"]):
  p=f.get("properties") or {}
  obstacle_rows.append({"obstacle_record_id":f["id"],"obstacle_type":p["entity_type"],"source_dataset_id":dataset,"source_ref":dataset+":"+f["id"],"source_geometry_type":(f.get("geometry") or {}).get("type"),"source_geometry":f.get("geometry"),"source_attributes":p,"height_m":None,"width_m":None,"depth_m":None,"material":None,"condition":"not_assessed","continuity":"not_assessed","permeability":"not_assessed","traversal_restriction":"unknown","pedestrian_passability":"not_assessed","vehicle_passability":"not_assessed","accessibility":"not_assessed","legal_access":"not_assessed","emergency_egress":"not_assessed","review_state":"UNREVIEWED_SOURCE_FEATURE","actor_ref":GENERATOR})
 counts={k:sum((f.get("properties") or {}).get("entity_type")==k for f in features) for k in TERRAIN_TYPES+OBSTACLE_TYPES}
 raw=source_bytes if source_bytes is not None else json.dumps(source,sort_keys=True,separators=(",",":")).encode()
 checks={"source_physical_ids_unique":len(seen)==sum(counts.values()),"terrain_geometry_valid_and_positive_area":all(shape(f["geometry"]).is_valid and shape(f["geometry"]).area>0 for f in terrain),"terrain_boundary_rings_closed":all(all(r["closed"] for r in row["boundary_rings"]) for row in terrain_rows),"boundary_edge_lengths_positive":all(e["planar_length_m"]>0 for row in terrain_rows for ring in row["boundary_rings"] for e in ring["edges"]),"neighbourhood_overlay_area_reconciles":all(abs(sum(x["intersection_area_m2"] for x in row["neighbourhood_intersections"])-row["planar_area_m2"])<=0.01 for row in terrain_rows),"all_elevation_and_gradient_fields_unassessed":all(row["elevation_m"] is None and row["gradient_degrees"] is None and row["slope_direction_degrees"] is None for row in terrain_rows),"obstacle_assessments_not_inferred":all(row["height_m"] is None and row["width_m"] is None and row["condition"]=="not_assessed" and row["traversal_restriction"]=="unknown" for row in obstacle_rows)}
 coverage={k:{"source_record_count":counts[k],"coverage_state":"SOURCE_RECORDS_PRESENT" if counts[k] else "NO_SOURCE_RECORDS_SUPPLIED","absence_claim":False} for k in TERRAIN_TYPES+OBSTACLE_TYPES}
 return {"schema":"saltwater-bp04-03-terrain-obstacle-detail-register/1.0","register_id":REGISTER_ID,"source_dataset_id":dataset,"source_sha256":hashlib.sha256(raw).hexdigest(),"generator":GENERATOR,"coordinate_reference":source.get("coordinate_reference"),"operational_approval":False,"terrain_records":terrain_rows,"obstacle_records":obstacle_rows,"source_coverage":coverage,"summary":{"terrain_record_count":len(terrain_rows),"obstacle_record_count":len(obstacle_rows),"terrain_planar_area_total_m2":round(sum(r["planar_area_m2"] for r in terrain_rows),3),"terrain_boundary_edge_count":sum(len(ring["edges"]) for row in terrain_rows for ring in row["boundary_rings"]),"terrain_neighbourhood_intersection_count":sum(len(r["neighbourhood_intersections"]) for r in terrain_rows),"terrain_route_corridor_intersection_count":sum(len(r["route_corridor_intersections"]) for r in terrain_rows),"route_corridors_supplied_count":len(routes),"elevation_assessed_count":0,"gradient_assessed_count":0,"obstacle_condition_assessed_count":0,"traversability_assessed_count":0,"operational_obstacle_records_created":0},"checks":checks,"passed_checks":sum(checks.values()),"failed_checks":[k for k,v in checks.items() if not v],"operational_seed_eligible":False,"database_write_performed":False,"limitations":["Planar measurements describe fictional source geometry, not ground survey or elevation.","Boundary bearings are coordinate-plane directions, not slope directions.","A terrain polygon does not establish gradient, surface, passability or obstruction.","No source record for a barrier class is not proof that the feature is absent.","Route intersections are geometric overlays only and do not establish a physical path or traversability."]}
def main():
 root=Path(__file__).resolve().parents[1]; path=root/"data/geography/saltwater-geography-v1.json"; raw=path.read_bytes(); source=json.loads(raw)
 from runtime.building_access_route_corridor_audit import build_route_corridor_candidates
 routes=build_route_corridor_candidates(source)["route_corridors"]
 report=build_detail_register(source,routes,raw)
 (root/"bp04-03-terrain-obstacle-detail-register.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
 print(json.dumps({"summary":report["summary"],"checks":report["checks"],"failed_checks":report["failed_checks"],"source_coverage":report["source_coverage"],"output":"bp04-03-terrain-obstacle-detail-register.json"},indent=2,sort_keys=True))
if __name__=="__main__": main()
