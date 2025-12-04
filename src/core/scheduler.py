# src/core/scheduler.py
from datetime import datetime, timedelta
from typing import List, Dict, Any


class Scheduler:
    def __init__(
        self,
        start_time: datetime | None = None,
        work_morning_start: int = 8,
        work_morning_end: int = 12,
        work_afternoon_start: int = 14,
        work_afternoon_end: int = 17,
    ):
        self.start_time = start_time
        self.work_morning_start = work_morning_start
        self.work_morning_end = work_morning_end
        self.work_afternoon_start = work_afternoon_start
        self.work_afternoon_end = work_afternoon_end

    def schedule(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        tasks: list of dicts:
        {
          "task": "Do X",
          "duration": 2,          # hours (float allowed)
          "depends_on": ["Other task"]
        }
        Returns tasks enriched with ISO8601 "start" and "end".
        """

        # --- Topological order by depends_on ---
        lookup = {t["task"]: t for t in tasks}
        completed = set()
        ordered: List[Dict[str, Any]] = []

        def visit(name: str):
            if name in completed:
                return
            deps = lookup[name].get("depends_on", []) or []
            for d in deps:
                if d in lookup:
                    visit(d)
            completed.add(name)
            ordered.append(lookup[name])

        for t in tasks:
            visit(t["task"])

        # max 5 tasks per scheduling run
        if len(ordered) > 5:
            ordered = ordered[:5]

        now = datetime.now()
        current = self.start_time or now
        current = self._next_work_start(current, now)

        for t in ordered:
            duration = float(t.get("duration", 1.0) or 1.0)

            start = self._next_work_start(current, now)
            end = self._add_work_hours(start, duration)

            t["start"] = start.isoformat()
            t["end"] = end.isoformat()

            # next task starts exactly when this one ends (no overlap)
            current = end

        return ordered

    # ---- helpers ----

    def _next_work_start(self, dt: datetime, now: datetime) -> datetime:
        """Move to the next valid work time (>= now, inside 8–12 or 14–17)."""
        if dt < now:
            dt = now

        # round UP to next whole hour to avoid starting in the past
        if dt.minute or dt.second or dt.microsecond:
            dt = dt.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)

        return self._align_to_business(dt)

    def _align_to_business(self, dt: datetime) -> datetime:
        """Snap dt forward into a valid work block (08–12 or 14–17)."""
        dt = dt.replace(minute=0, second=0, microsecond=0)

        while True:
            hour = dt.hour

            # Morning block
            if self.work_morning_start <= hour < self.work_morning_end:
                return dt

            # Afternoon block
            if self.work_afternoon_start <= hour < self.work_afternoon_end:
                return dt

            # Before morning: jump to 08:00 same day
            if hour < self.work_morning_start:
                return dt.replace(hour=self.work_morning_start)

            # Lunch break: jump to 14:00 same day
            if self.work_morning_end <= hour < self.work_afternoon_start:
                return dt.replace(hour=self.work_afternoon_start)

            # After 17:00: move to next day 08:00
            dt = (dt + timedelta(days=1)).replace(
                hour=self.work_morning_start, minute=0, second=0, microsecond=0
            )

    def _add_work_hours(self, start: datetime, hours: float) -> datetime:
        """Add work hours across days, staying inside 8–12 and 14–17."""
        current = self._align_to_business(start)
        remaining = float(hours)

        while remaining > 0:
            hour = current.hour

            # current block end
            if self.work_morning_start <= hour < self.work_morning_end:
                end_block = current.replace(
                    hour=self.work_morning_end, minute=0, second=0, microsecond=0
                )
            elif self.work_afternoon_start <= hour < self.work_afternoon_end:
                end_block = current.replace(
                    hour=self.work_afternoon_end, minute=0, second=0, microsecond=0
                )
            else:
                current = self._align_to_business(current)
                continue

            available = (end_block - current).total_seconds() / 3600.0

            if remaining <= available:
                return current + timedelta(hours=remaining)

            # consume this block and move on
            remaining -= available

            if end_block.hour == self.work_morning_end:
                # move to afternoon block same day
                current = end_block.replace(
                    hour=self.work_afternoon_start, minute=0, second=0, microsecond=0
                )
            else:
                # move to next day morning
                current = (end_block + timedelta(days=1)).replace(
                    hour=self.work_morning_start, minute=0, second=0, microsecond=0
                )

        return current
