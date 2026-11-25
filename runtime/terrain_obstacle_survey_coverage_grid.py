"""Deterministic 500 m terrain/obstacle evidence coverage grid (non-operational)."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
from shapely.geometry import Polygon,box,shape,Point,LineString

GRID_M=500
GENERATOR="BP04-03-TERRAIN-OBSTACLE-SURVEY-COVERAGE-GRID-V1"
def _poly(rings): return Polygon(rings[0],rings[1:])
def build_coverage_grid(source:dict,properties:list[dict],buildings:list[dict],routes:list[dict],source_bytes:bytes|None=None)->dict:
 crs=source["coordinate_reference"]; minx,miny,maxx,maxy=crs["extent"]
 if (maxx-minx)%GRID_M or (maxy-miny)%GRID_M: raise ValueError("City extent must divide evenly into survey grid size")
 city=next(shape(f["geometry"]) for f in source["features"] if f.get("properties",{}).get("entity_type")=="city_state_boundary")
 districts=[(d["id"],d["name"],box(d["x0"],d["y0"],d["x1"],d["y1"])) for d in source.get("districts",[])]
 hoods=[(n["id"],n["name"],n["district_id"],shape(n["geometry"])) for n in source.get("neighbourhoods",[])]
 terrain=[(f["id"],shape(f["geometry"])) for f in source["features"] if f.get("properties",{}).get("entity_type")=="terrain_feature"]
 water=[(f["id"],shape(f["geometry"])) for f in source["features"] if f.get("properties",{}).get("entity_type") in ("harbour_water","constructed_water")]
 road_geoms=[(s["id"],s["road_id"],LineString(s["geometry"])) for s in source["network"]["segments"]]
 property_geoms=[(p["candidate_property_id"],p["source_candidate_parcel_id"],_poly(p["geometry"])) for p in properties]
 building_geoms=[(b["candidate_building_id"],b["property_id"],_poly(b["geometry"])) for b in buildings]
 route_geoms=[(r["candidate_route_corridor_id"],r["source_connector_candidate_id"],shape(r["centreline_geometry"])) for r in routes]
 cols=int((maxx-minx)/GRID_M); rows=int((maxy-miny)/GRID_M); cells=[]
 for iy in range(rows):
  for ix in range(cols):
   x0=minx+ix*GRID_M; y0=miny+iy*GRID_M; cell=box(x0,y0,x0+GRID_M,y0+GRID_M).intersection(city)
   if cell.is_empty or cell.area<=0: raise ValueError("Survey grid cell outside city or empty")
   dids=[{"district_id":i,"district_name":n,"intersection_area_m2":round(cell.intersection(g).area,3)} for i,n,g in districts if cell.intersection(g).area>0]
   nids=[{"neighbourhood_id":i,"neighbourhood_name":n,"district_id":d,"intersection_area_m2":round(cell.intersection(g).area,3)} for i,n,d,g in hoods if cell.intersection(g).area>0]
   pids=[{"property_candidate_id":pid,"parcel_candidate_id":parcel} for pid,parcel,g in property_geoms if cell.covers(g.representative_point())]
   bids=[{"building_candidate_id":bid,"property_candidate_id":pid} for bid,pid,g in building_geoms if cell.covers(g.representative_point())]
   roads=[]
   for sid,rid,g in road_geoms:
    inter=g.intersection(cell)
    if not inter.is_empty and inter.length>0: roads.append({"road_segment_id":sid,"road_id":rid,"centreline_length_in_cell_m":round(inter.length,3)})
   route_ids=[]
   for cid,connector,g in route_geoms:
    if cell.covers(g.interpolate(0.5,normalized=True)): route_ids.append({"route_corridor_candidate_id":cid,"source_connector_candidate_id":connector})
   terrain_ids=[fid for fid,g in terrain if g.intersects(cell)]
   water_ids=[fid for fid,g in water if g.intersects(cell)]
   cells.append({"survey_cell_id":f"SWSG-{iy+1:02d}-{ix+1:02d}","grid_row":iy+1,"grid_column":ix+1,"cell_bounds_xy_m":[x0,y0,x0+GRID_M,y0+GRID_M],"cell_geometry":{"type":"Polygon","coordinates":[[[x0,y0],[x0+GRID_M,y0],[x0+GRID_M,y0+GRID_M],[x0,y0+GRID_M],[x0,y0]]]},"cell_area_m2":round(cell.area,3),"district_intersections":dids,"neighbourhood_intersections":nids,"property_site_candidates":pids,"building_footprint_candidates":bids,"road_segment_intersections":roads,"route_corridor_midpoint_assignments":route_ids,"terrain_feature_intersections":terrain_ids,"water_feature_intersections":water_ids,"source_coverage":{"elevation_surfaces":0,"contours":0,"spot_elevations":0,"retaining_structures":0,"walls":0,"fences":0,"gates":0,"drainage_structures":0,"other_physical_obstacles":0},"assessment_state":{"elevation":"not_assessed_no_source","terrain_condition":"not_assessed","physical_obstacles":"not_assessed_no_source","drainage":"not_assessed_no_source","surface":"not_assessed","route_traversability":"not_assessed","accessibility":"not_assessed","legal_access":"not_assessed","emergency_egress":"not_assessed"},"survey_priority":"UNRANKED_NO_SURVEY_EVIDENCE","review_state":"UNREVIEWED_COVERAGE_PLANNING_CELL","source_ref":source["dataset_id"]+":survey-grid:"+f"{iy+1:02d}-{ix+1:02d}"})
 raw=source_bytes if source_bytes is not None else json.dumps(source,sort_keys=True,separators=(",",":")).encode()
 total_area=sum(c["cell_area_m2"] for c in cells)
 checks={"expected_cell_count":len(cells)==cols*rows,"all_cells_positive_area":all(c["cell_area_m2"]>0 for c in cells),"grid_area_reconciles_to_city":abs(total_area-city.area)<=0.01,"all_cells_have_neighbourhood_lineage":all(c["neighbourhood_intersections"] for c in cells),"all_property_candidates_assigned_once":sum(len(c["property_site_candidates"]) for c in cells)==len(properties),"all_building_candidates_assigned_once":sum(len(c["building_footprint_candidates"]) for c in cells)==len(buildings),"all_assessment_states_remain_unassessed":all(all(v in ("not_assessed","not_assessed_no_source") for v in c["assessment_state"].values()) for c in cells),"no_operational_survey_approval":all(c["review_state"]=="UNREVIEWED_COVERAGE_PLANNING_CELL" for c in cells)}
 return {"schema":"saltwater-bp04-03-terrain-obstacle-survey-coverage-grid/1.0","grid_id":"SW-TERRAIN-SURVEY-GRID-001","source_dataset_id":source["dataset_id"],"source_sha256":hashlib.sha256(raw).hexdigest(),"generator":GENERATOR,"coordinate_reference":crs,"cell_size_m":GRID_M,"grid_columns":cols,"grid_rows":rows,"operational_approval":False,"cells":cells,"summary":{"survey_cell_count":len(cells),"city_area_m2":round(city.area,3),"grid_area_m2":round(total_area,3),"property_candidates_assigned":sum(len(c["property_site_candidates"]) for c in cells),"building_candidates_assigned":sum(len(c["building_footprint_candidates"]) for c in cells),"road_segment_cell_intersections":sum(len(c["road_segment_intersections"]) for c in cells),"route_corridor_midpoint_assignments":sum(len(c["route_corridor_midpoint_assignments"]) for c in cells),"cells_with_terrain_feature":sum(bool(c["terrain_feature_intersections"]) for c in cells),"cells_with_water_features":sum(bool(c["water_feature_intersections"]) for c in cells),"cells_with_elevation_source":0,"cells_with_mapped_physical_obstacle_sources":0,"survey_priorities_assigned":0,"operational_survey_records_created":0},"checks":checks,"passed_checks":sum(checks.values()),"failed_checks":[k for k,v in checks.items() if not v],"operational_seed_eligible":False,"database_write_performed":False,"limitations":["Grid cells are planning/coverage units, not land parcels or physical assets.","Property and building references are generated geometry candidates, not surveyed or operational assets.","Road and route assignments are geometric overlays or midpoint allocations, not passability findings.","Zero source counts mean no evidence supplied in SW-GEO-V1, not that a feature is absent.","No survey priority, elevation, gradient, obstacle, condition, surface, access or egress facts are inferred."]}
def main():
 root=Path(__file__).resolve().parents[1]; path=root/"data/geography/saltwater-geography-v1.json"; raw=path.read_bytes(); source=json.loads(raw)
 from runtime.physical_asset_inventory_generator import build_asset_inventory
 from runtime.building_access_route_corridor_audit import build_route_corridor_candidates
 inventory=build_asset_inventory(source); routes=build_route_corridor_candidates(source,inventory=inventory)
 report=build_coverage_grid(source,inventory["properties"],inventory["buildings"],routes["route_corridors"],raw)
 (root/"bp04-03-terrain-obstacle-survey-coverage-grid.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
 print(json.dumps({"summary":report["summary"],"checks":report["checks"],"failed_checks":report["failed_checks"],"output":"bp04-03-terrain-obstacle-survey-coverage-grid.json"},indent=2,sort_keys=True))
if __name__=="__main__": main()
