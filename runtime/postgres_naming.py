"""PostgreSQL adapter for the authoritative Saltwater naming registry.

The caller owns the surrounding transaction. This adapter never commits or
rolls back, so domain creation and name reservation remain atomic.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from runtime.naming import NORMALIZER_VERSION, GeneratedNameBatch, normalize_name


@dataclass(frozen=True, slots=True)
class PersistentNameRecord:
    reservation_id: int
    entity_type: str
    entity_id: int
    name_form: str
    display_name: str
    status: str
    ambiguous: bool


class PostgresNameRegistry:
    """Thin, parameterized adapter over the disposable/production SQL contract."""

    def __init__(self, connection: Any):
        if connection is None or not callable(getattr(connection, "cursor", None)):
            raise TypeError("a DB-API compatible PostgreSQL connection is required")
        self._connection = connection

    def reserve(
        self, entity_type: str, entity_id: int, display_name: str, *,
        name_form: str = "canonical", source_ref: str, actor_ref: str,
        reason: str, effective_tick: int, generation_batch_id: int | None = None,
    ) -> int:
        normalize_name(display_name)  # fail fast; database remains authoritative
        with self._connection.cursor() as cursor:
            cursor.execute(
                """SELECT sw_names.reserve_name(
                     %s::text,%s::bigint,%s::text,%s::text,%s::text,%s::text,%s::text,%s::bigint,%s::bigint)""",
                (
                    entity_type.upper(), entity_id, name_form.lower(), display_name,
                    source_ref, actor_ref, reason, effective_tick, generation_batch_id,
                ),
            )
            row = cursor.fetchone()
        if not row:
            raise RuntimeError("name reservation returned no identifier")
        return int(row[0])

    def record_generation_batch(
        self, batch: GeneratedNameBatch, *, source_ref: str,
        actor_ref: str, reason: str,
    ) -> int:
        if not batch.candidates:
            raise ValueError("cannot persist an empty generator batch")
        with self._connection.cursor() as cursor:
            cursor.execute(
                """SELECT sw_names.record_generation_batch(
                     %s::text,%s::smallint,%s::smallint,%s::text,%s::bigint,%s::bytea,%s::integer,%s::text,%s::text,%s::text)""",
                (
                    batch.domain.upper(), batch.generator_version, NORMALIZER_VERSION,
                    batch.config_version, batch.seed,
                    bytes.fromhex(batch.manifest_sha256), len(batch.candidates),
                    source_ref, actor_ref, reason,
                ),
            )
            row = cursor.fetchone()
        if not row:
            raise RuntimeError("generator manifest registration returned no identifier")
        return int(row[0])

    def add_alias(
        self, entity_type: str, entity_id: int, alias: str, *,
        source_ref: str, actor_ref: str, reason: str, effective_tick: int,
    ) -> int:
        normalize_name(alias)
        with self._connection.cursor() as cursor:
            cursor.execute(
                """SELECT sw_names.add_alias(%s::text,%s::bigint,%s::text,%s::text,%s::text,%s::text,%s::bigint)""",
                (entity_type.upper(), entity_id, alias, source_ref, actor_ref, reason, effective_tick),
            )
            row = cursor.fetchone()
        if not row:
            raise RuntimeError("alias reservation returned no identifier")
        return int(row[0])

    def change_status(
        self, reservation_id: int, event_code: str, *, effective_tick: int,
        source_ref: str, actor_ref: str, reason: str,
    ) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                "SELECT sw_names.change_status(%s::bigint,%s::text,%s::bigint,%s::text,%s::text,%s::text)",
                (reservation_id, event_code.lower(), effective_tick, source_ref, actor_ref, reason),
            )

    def retire(
        self, reservation_id: int, *, effective_tick: int,
        source_ref: str, actor_ref: str, reason: str,
    ) -> None:
        self.change_status(
            reservation_id, "retired", effective_tick=effective_tick,
            source_ref=source_ref, actor_ref=actor_ref, reason=reason,
        )

    def search(self, value: str) -> tuple[PersistentNameRecord, ...]:
        normalize_name(value)
        with self._connection.cursor() as cursor:
            cursor.execute(
                """SELECT reservation_id,entity_type,entity_id,name_form,
                          display_name,status,ambiguous
                   FROM sw_names.search_name(%s)
                   ORDER BY entity_type,entity_id,reservation_id""",
                (value,),
            )
            rows = cursor.fetchall()
        return tuple(PersistentNameRecord(*row) for row in rows)
