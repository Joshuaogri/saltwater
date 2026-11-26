"""Read-only PostgreSQL adapter for BP12 incident location history."""
from __future__ import annotations

from typing import Any, Callable


class PostgresIncidentLocationHistoryReader:
    """Read event-backed incident location chronology without duplicating records."""

    def __init__(self, connect: Callable[[], Any]):
        if not callable(connect):
            raise TypeError("connect must be a trusted PostgreSQL connection factory")
        self._connect = connect

    def read(self, incident_id: int) -> list[dict]:
        if type(incident_id) is not int or incident_id < 1:
            raise ValueError("A positive incident ID is required.")
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT * FROM sw_incident.incident_location_history(%s)",
                        (incident_id,),
                    )
                    columns = [item.name if hasattr(item, "name") else item[0]
                               for item in cur.description]
                    rows = cur.fetchall()
            return [dict(zip(columns, row, strict=True)) for row in rows]
        except ValueError:
            raise
        except Exception as exc:
            raise RuntimeError("Incident location history is unavailable.") from exc
