"""Durable Telegram inbox: fast private replies, reliable asynchronous catalog updates.

Each update is written to SQLite *before* getUpdates acknowledges its ID.
Private chat actions and source-group publications have independent workers.
"""
import json
import sqlite3
import time
from pathlib import Path


class DurableUpdateInbox:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("CREATE TABLE IF NOT EXISTS updates ("
                       "update_id INTEGER PRIMARY KEY, lane TEXT NOT NULL,"
                       "payload TEXT NOT NULL, attempts INTEGER NOT NULL DEFAULT 0,"
                       "retry_at REAL NOT NULL DEFAULT 0)")
            db.execute("CREATE INDEX IF NOT EXISTS updates_lane_idx "
                       "ON updates(lane, retry_at, update_id)")
            db.execute("CREATE TABLE IF NOT EXISTS state ("
                       "name TEXT PRIMARY KEY, value INTEGER NOT NULL)")
            db.execute("CREATE TABLE IF NOT EXISTS dead_letters ("
                       "update_id INTEGER PRIMARY KEY, lane TEXT NOT NULL,"
                       "payload TEXT NOT NULL, reason TEXT NOT NULL, failed_at REAL NOT NULL)")

    def _connect(self):
        db = sqlite3.connect(str(self.path), timeout=10)
        db.execute("PRAGMA busy_timeout=10000")
        return db

    def accepted_offset(self):
        with self._connect() as db:
            row = db.execute("SELECT value FROM state WHERE name='accepted_id'").fetchone()
            return int(row[0]) + 1 if row else 0

    def store(self, updates):
        """Atomically persist an entire Telegram batch and its ack cursor."""
        if not updates:
            return self.accepted_offset()
        with self._connect() as db:
            accepted_row = db.execute(
                "SELECT value FROM state WHERE name='accepted_id'").fetchone()
            accepted = int(accepted_row[0]) if accepted_row else -1
            for update in updates:
                uid = update.get("update_id")
                if not isinstance(uid, int):
                    continue
                # Updates the bot has already acknowledged cannot be replayed
                # after their completed rows have been deleted.
                if uid <= accepted:
                    continue
                lane = "private" if (
                    update.get("callback_query")
                    or (update.get("message") or {}).get("chat", {}).get("type") == "private"
                ) else "catalog"
                db.execute(
                    "INSERT OR IGNORE INTO updates(update_id, lane, payload) VALUES (?, ?, ?)",
                    (uid, lane, json.dumps(update, ensure_ascii=False)))
                accepted = max(accepted, uid)
            db.execute(
                "INSERT INTO state(name,value) VALUES('accepted_id',?) "
                "ON CONFLICT(name) DO UPDATE SET value=MAX(value,excluded.value)",
                (accepted,))
            return accepted + 1

    def next(self, lane):
        with self._connect() as db:
            row = db.execute(
                "SELECT update_id,payload FROM updates "
                "WHERE lane=? AND retry_at<=? ORDER BY update_id LIMIT 1",
                (lane, time.time())).fetchone()
            return (int(row[0]), json.loads(row[1])) if row else None

    def done(self, update_id):
        with self._connect() as db:
            db.execute("DELETE FROM updates WHERE update_id=?", (update_id,))

    def failed(self, update_id, reason):
        with self._connect() as db:
            row = db.execute(
                "SELECT lane,payload,attempts FROM updates WHERE update_id=?",
                (update_id,)).fetchone()
            if row is None:
                return
            lane, payload, previous = row
            attempts = previous + 1
            if attempts >= 5:
                db.execute(
                    "INSERT OR REPLACE INTO dead_letters "
                    "(update_id,lane,payload,reason,failed_at) VALUES (?,?,?,?,?)",
                    (update_id, lane, payload, str(reason)[:500], time.time()))
                db.execute("DELETE FROM updates WHERE update_id=?", (update_id,))
            else:
                db.execute("UPDATE updates SET attempts=?, retry_at=? WHERE update_id=?",
                           (attempts, time.time() + min(60, 2 ** attempts), update_id))

    def pending(self):
        with self._connect() as db:
            return dict(db.execute("SELECT lane,COUNT(*) FROM updates GROUP BY lane"))


def archive_signature(path):
    file = Path(path)
    stat = file.stat()
    return {"name": file.name, "size": stat.st_size, "mtime_ns": stat.st_mtime_ns}


def should_run_backfill(state_path, export_path, runtime_catalog, search_index):
    state_path = Path(state_path)
    if not (Path(runtime_catalog).exists() and Path(search_index).exists()):
        return True
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
        return state != archive_signature(export_path)
    except (OSError, ValueError):
        return True


def mark_backfill_complete(state_path, export_path):
    state_path = Path(state_path)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = state_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(archive_signature(export_path)), encoding="utf-8")
    tmp.replace(state_path)
