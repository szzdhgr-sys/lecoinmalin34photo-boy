import tempfile
import unittest
from pathlib import Path
from bot_runtime import (
    DurableUpdateInbox, should_run_backfill, mark_backfill_complete
)


class DurableInboxTests(unittest.TestCase):
    def test_messages_persist_and_private_lane_is_separate(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "inbox.sqlite3"
            inbox = DurableUpdateInbox(path)
            self.assertEqual(inbox.accepted_offset(), 0)
            offset = inbox.store([
                {"update_id": 12, "message": {"chat": {"type": "supergroup"},
                                               "message_thread_id": 64, "photo": [{"file_id": "a"}]}},
                {"update_id": 13, "message": {"chat": {"type": "private"}, "text": "/start"}},
                {"update_id": 14, "callback_query": {"id": "1", "data": "topic:64"}},
            ])
            self.assertEqual(offset, 15)
            # Restart: update does not disappear when the process closes.
            reopened = DurableUpdateInbox(path)
            self.assertEqual(reopened.accepted_offset(), 15)
            self.assertEqual(reopened.pending(), {"catalog": 1, "private": 2})
            self.assertEqual(reopened.next("private")[0], 13)
            self.assertEqual(reopened.next("catalog")[0], 12)
            reopened.done(13)
            self.assertEqual(reopened.next("private")[0], 14)
            reopened.done(14)
            reopened.done(12)
            self.assertEqual(reopened.pending(), {})
            reopened.store([{"update_id": 12, "message": {"chat": {"type": "private"}}}])
            self.assertEqual(reopened.pending(), {})

    def test_failed_item_retried_and_dead_lettered_after_five_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            db = DurableUpdateInbox(Path(directory) / "updates.sqlite3")
            db.store([{"update_id": 1, "message": {"chat": {"type": "private"}}}])
            db.failed(1, "temporary Telegram error")
            self.assertEqual(db.pending(), {"private": 1})
            self.assertIsNone(db.next("private"))
            for _ in range(4):
                db.failed(1, "persistent error")
            self.assertEqual(db.pending(), {})
            with db._connect() as connection:
                self.assertEqual(connection.execute(
                    "SELECT COUNT(*) FROM dead_letters").fetchone()[0], 1)

    def test_backfill_marker_and_runtime_files(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            export = folder / "result.json"
            export.write_text('{"messages":[]}', encoding="utf-8")
            state = folder / "backfill.json"
            cat = folder / "catalog_runtime.json"
            search = folder / "search_index_runtime.json"
            self.assertTrue(should_run_backfill(state, export, cat, search))
            cat.write_text("{}", encoding="utf-8")
            search.write_text("{}", encoding="utf-8")
            mark_backfill_complete(state, export)
            self.assertFalse(should_run_backfill(state, export, cat, search))
            export.write_text('{"messages":[{"id":1}]}', encoding="utf-8")
            self.assertTrue(should_run_backfill(state, export, cat, search))


if __name__ == "__main__":
    unittest.main()
