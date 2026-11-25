"""Generate deterministic weekly operating schedules for every Saltwater business."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from runtime.business_registry_generator import build_business_registry
from runtime.property_tenure_generator import _expand_columnar
from runtime.property_world_generator import to_columnar_document

GENERATOR = "SW-BUSINESS-OPERATIONS-GENERATOR-001"
DAYS = [
    ("monday", 0), ("tuesday", 1), ("wednesday", 2), ("thursday", 3),
    ("friday", 4), ("saturday", 5), ("sunday", 6),
]

def _n(key: str, low: int, high: int) -> int:
    return low + int.from_bytes(hashlib.sha256(key.encode()).digest()[:4], "big") % (high-low+1)

def _time(hour: int, minute: int = 0) -> str:
    return f"{hour:02d}:{minute:02d}"

def _schedule(profile: str, sector: str, day: int, key: str) -> dict:
    if profile == "24_hour_or_shift_based":
        return {"open": True, "opens_at": "00:00", "closes_at": "23:59", "service_window": "continuous", "shift_pattern": "rotating_24_hour"}
    if profile == "appointment_only":
        if day == 6:
            return {"open": False, "opens_at": None, "closes_at": None, "service_window": "closed", "shift_pattern": "on_call"}
        return {"open": True, "opens_at": "09:00", "closes_at": "17:00", "service_window": "appointments", "shift_pattern": "scheduled"}
    if profile == "07:00-19:00":
        start, end = 7, 19
    elif profile == "08:00-17:00":
        start, end = 8, 17
    elif profile == "09:00-18:00":
        start, end = 9, 18
    else:
        start, end = 10, 22
    weekend_closed = day == 6 and sector not in {"food_hospitality", "transport_logistics", "health_wellness", "retail_trade"}
    if weekend_closed or (day == 5 and sector in {"professional_services", "finance_insurance", "education_training"}):
        return {"open": False, "opens_at": None, "closes_at": None, "service_window": "closed", "shift_pattern": "weekday"}
    shift = _n(key + f"-{day}-shift", -1, 1)
    start = max(5, min(12, start + shift))
    end = max(start + 6, min(23, end + shift))
    return {"open": True, "opens_at": _time(start), "closes_at": _time(end), "service_window": "standard", "shift_pattern": "single_or_split_day"}

def build_business_operations(source: dict, registry: dict | None = None) -> dict:
    registry = registry or build_business_registry(source)
    establishments = {x["business_id"]: x for x in registry["establishments"]}
    schedules = []
    for business in registry["businesses"]:
        site = establishments[business["business_id"]]
        status = business["status"]
        for day_name, day_number in DAYS:
            row = _schedule(site["opening_hours_profile"], business["sector"], day_number, business["business_id"])
            if status == "temporarily_inactive":
                row = {"open": False, "opens_at": None, "closes_at": None, "service_window": "temporarily_suspended", "shift_pattern": "none"}
            if status == "seasonal" and _n(business["business_id"] + "-season-" + str(day_number), 1, 10) <= 3:
                row = {"open": False, "opens_at": None, "closes_at": None, "service_window": "seasonal_closure", "shift_pattern": "none"}
            schedules.append({
                "business_schedule_id": f"SWBHS-{business['business_id'][-6:]}-{day_number+1}",
                "business_id": business["business_id"],
                "establishment_id": site["establishment_id"],
                "day_of_week": day_name,
                "day_number": day_number,
                "operating_status": status,
                "is_open_to_customers": row["open"],
                "customer_open_time": row["opens_at"],
                "customer_close_time": row["closes_at"],
                "service_window": row["service_window"],
                "staff_shift_pattern": row["shift_pattern"],
                "delivery_window_start": None if not row["open"] else ("06:00" if site["delivery_access"] == "loading_bay" else "08:00"),
                "delivery_window_end": None if not row["open"] else ("16:00" if site["delivery_access"] == "loading_bay" else "17:00"),
                "emergency_contact_route": "establishment_access_point",
                "valid_from_tick": 0,
                "valid_to_tick": None,
                "source_generator": GENERATOR,
            })
    schedules_by_business = {}
    for schedule in schedules:
        schedules_by_business.setdefault(schedule["business_id"], []).append(schedule)
    weekly_profiles = []
    for business in registry["businesses"]:
        rows = schedules_by_business[business["business_id"]]
        weekly_profiles.append({
            "business_id": business["business_id"],
            "establishment_id": establishments[business["business_id"]]["establishment_id"],
            "weekly_open_days": sum(1 for x in rows if x["is_open_to_customers"]),
            "weekly_closed_days": sum(1 for x in rows if not x["is_open_to_customers"]),
            "has_continuous_service": any(x["service_window"] == "continuous" for x in rows),
            "has_appointment_service": any(x["service_window"] == "appointments" for x in rows),
            "valid_from_tick": 0,
        })
    body = {
        "schema": "saltwater-business-operations/1.0",
        "dataset_id": "SW-BUSINESS-OPERATIONS-V1",
        "canon_status": "CANONICAL_FICTIONAL_GAME_WORLD",
        "generator": GENERATOR,
        "effective_tick": 0,
        "city": "Saltwater",
        "city_population_hard_cap": 10000,
        "summary": {
            "business_count": len(registry["businesses"]),
            "establishment_count": len(registry["establishments"]),
            "daily_schedule_count": len(schedules),
            "weekly_profile_count": len(weekly_profiles),
            "open_day_count": sum(1 for x in schedules if x["is_open_to_customers"]),
            "closed_day_count": sum(1 for x in schedules if not x["is_open_to_customers"]),
            "population_records_created": 0,
        },
        "weekly_profiles": weekly_profiles,
        "daily_schedules": schedules,
        "lineage": {"business_registry_dataset": "SW-BUSINESS-REGISTRY-V1", "business_count": len(registry["businesses"])},
        "gameplay": {
            "schedule_granularity": "one explicit local-time operating record per business per weekday",
            "dispatch_use": "Supports time-aware business occupancy, opening-hours checks, call-for-service context and scene access",
            "population_isolation": "Schedules do not create employees, customers or residents as person records.",
            "time_basis": "Saltwater local fictional city time",
        },
    }
    return body

def main():
    root = Path(__file__).resolve().parents[1]
    source = json.loads((root / "data/geography/saltwater-geography-v1.json").read_text(encoding="utf-8"))
    registry_document = json.loads((root / "data/business/saltwater-business-registry-v1.json").read_text(encoding="utf-8"))
    registry = _expand_columnar(registry_document)
    result = build_business_operations(source, registry=registry)
    output = root / "data/business/saltwater-business-operations-v1.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    document = to_columnar_document(result)
    output.write_text(json.dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"] | {"output_bytes": output.stat().st_size, "storage_format": document["storage_format"]}, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
