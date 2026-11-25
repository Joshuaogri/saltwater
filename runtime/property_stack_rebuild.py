"""Rebuild Saltwater's property/business data stack in dependency order.

This is a deterministic, sequential refresh for the global-estate expansion.
It writes only generated GitHub datasets; it never connects to Neon.
"""
from __future__ import annotations

import subprocess
import sys

MODULES = (
    "runtime.property_world_generator",
    "runtime.business_registry_generator",
    "runtime.business_operations_generator",
    "runtime.property_tenure_generator",
    "runtime.building_services_generator",
    "runtime.property_maintenance_generator",
    "runtime.property_security_access_generator",
    "runtime.property_value_risk_tax_generator",
    "runtime.property_development_control_generator",
    "runtime.property_lifecycle_transactions_generator",
    "runtime.property_rights_boundaries_generator",
    "runtime.property_insurance_claims_generator",
    "runtime.property_facilities_operations_generator",
    "runtime.global_estate_capacity_audit",
)


def main() -> None:
    for module in MODULES:
        print(f"\n=== Rebuilding {module} ===", flush=True)
        subprocess.run([sys.executable, "-m", module], check=True)


if __name__ == "__main__":
    main()
