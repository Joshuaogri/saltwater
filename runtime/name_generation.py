"""Versioned deterministic name candidate generation API for Saltwater.

All generated candidates remain proposals until accepted by the authoritative
PostgreSQL naming registry. This module does not write to the database.
"""
from runtime.naming import (
    GENERATOR_VERSION,
    GeneratedNameBatch,
    GeneratorConfig,
    generate_batch,
    generate_candidates,
)

__all__ = [
    "GENERATOR_VERSION",
    "GeneratedNameBatch",
    "GeneratorConfig",
    "generate_batch",
    "generate_candidates",
]
