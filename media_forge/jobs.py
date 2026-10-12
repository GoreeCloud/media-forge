"""Durable sequential queue. Filesystem outputs remain authoritative."""
import json
import sqlite3
import threading
from contextlib import contextmanager
import uuid
from datetime import datetime, timezone
from pathlib import Path
from .engine import JobCanceled, execute_plan, validate_plan


def utc_now():
    return datetime.now(timezone.utc).isoformat()


class JobStore:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    @contextmanager
    def _connect(self):
        db = sqlite3.connect(self.path, timeout=20)
        try:
            db.row_factory = sqlite3.Row
            db.execute("PRAGMA busy_timeout=20000")
            with db:
                yield db
        finally:
            db.close()

    def _initialize(self):
        with self._connect() as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("""CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                state TEXT NOT NULL, stage TEXT, progress REAL NOT NULL DEFAULT 0,
                plan_json TEXT NOT NULL, outputs_json TEXT NOT NULL DEFAULT '[]', error TEXT
            )""")
            db.execute("UPDATE jobs SET state='interrupted', updated_at=? WHERE state IN ('running','verifying')", (utc_now(),))

    def submit(self, plan):
        plan = validate_plan(plan)
        id_ = uuid.uuid4().hex
        now = utc_now()
        with self._connect() as db:
            db.execute("INSERT INTO jobs(id,created_at,updated_at,state,plan_json) VALUES (?,?,?,?,?)", (id_, now, now, "queued", json.dumps(plan)))
        return self.get(id_)

    def get(self, id_):
        with self._connect() as db:
            row = db.execute("SELECT * FROM jobs WHERE id=?", (id_,)).fetchone()
        return self._decode(row) if row else None

    def list(self):
        with self._connect() as db:
            rows = db.execute("SELECT * FROM jobs ORDER BY created_at DESC LIMIT 200").fetchall()
        return [self._decode(r) for r in rows]

    def claim_next(self):
        # Atomic claim prevents a queued cancellation from being overwritten.
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT id FROM jobs WHERE state='queued' ORDER BY created_at ASC LIMIT 1").fetchone()
            if row is None:
                return None
            db.execute("UPDATE jobs SET state='running', stage='starting', updated_at=? WHERE id=? AND state='queued'", (utc_now(), row["id"]))
            return row["id"]

    def update(self, id_, **fields):
        allowed = {"state", "stage", "progress", "outputs_json", "error"}
        if not fields or not set(fields) <= allowed:
            raise ValueError("Invalid job update fields")
        fields["updated_at"] = utc_now()
        assignments = ",".join(f"{key}=?" for key in fields)
        with self._connect() as db:
            db.execute(f"UPDATE jobs SET {assignments} WHERE id=?", [*fields.values(), id_])

    def cancel_queued(self, id_):
        with self._connect() as db:
            result = db.execute("UPDATE jobs SET state='canceled', updated_at=? WHERE id=? AND state='queued'", (utc_now(), id_))
            return result.rowcount > 0

    @staticmethod
    def _decode(row):
        obj = dict(row)
        obj["plan"] = json.loads(obj.pop("plan_json"))
        obj["outputs"] = json.loads(obj.pop("outputs_json"))
        return obj


class JobWorker:
    def __init__(self, store: JobStore, logs: Path):
        self.store = store
        self.logs = logs
        self._stop = threading.Event()
        self._active_cancel = threading.Event()
        self._active = None
        self._lock = threading.Lock()
        self.thread = threading.Thread(target=self._run, daemon=True, name="media-forge-worker")

    def start(self):
        self.thread.start()

    def cancel(self, id_):
        if self.store.cancel_queued(id_):
            return True
        with self._lock:
            if self._active == id_:
                self._active_cancel.set()
                return True
        return False

    def stop(self):
        self._stop.set()
        self._active_cancel.set()
        if self.thread.is_alive():
            self.thread.join(timeout=8)

    def _run(self):
        while not self._stop.wait(0.25):
            id_ = self.store.claim_next()
            if id_ is None:
                continue
            with self._lock:
                self._active = id_
                self._active_cancel.clear()
            plan = self.store.get(id_)["plan"]
            try:
                def progress(stage, value, state):
                    self.store.update(id_, stage=stage, progress=round(value, 4), state=state)
                def saved_output(outputs):
                    self.store.update(id_, outputs_json=json.dumps(outputs))
                outputs = execute_plan(id_, plan, progress, self._active_cancel, self.logs, on_output=saved_output)
                self.store.update(id_, state="completed", stage="done", progress=1, outputs_json=json.dumps(outputs))
            except JobCanceled:
                preserved = bool(self.store.get(id_)["outputs"])
                self.store.update(id_, state="partial_success" if preserved else "canceled", stage="canceled")
            except Exception as exc:
                preserved = bool(self.store.get(id_)["outputs"])
                # Unexpected errors remain visible but must not crash the queue.
                self.store.update(id_, state="partial_success" if preserved else "failed", stage="error", error=str(exc)[:2000])
            finally:
                with self._lock:
                    self._active = None
