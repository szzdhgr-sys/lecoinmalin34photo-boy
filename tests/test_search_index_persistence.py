"""Regression test: search index must survive bot restarts."""
import ast
import json
from pathlib import Path
import tempfile
import threading
import unittest


class SearchIndexPersistenceTests(unittest.TestCase):
    def test_search_index_written_to_target_not_tmp(self):
        source = Path(__file__).resolve().parents[1] / "bot.py"
        module = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
        fn = next(n for n in module.body if isinstance(n, ast.FunctionDef)
                  and n.name == "save_search_index")
        save_module = ast.Module(body=[fn], type_ignores=[])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "search_index_runtime.json"
            data = {"123": {"text": "Nike Air Max", "brands": ["Nike"]}}
            env = {
                "SEARCH_INDEX_FILE": path,
                "SEARCH_INDEX_LOCK": threading.RLock(),
                "SEARCH_INDEX": data,
                "json": json,
            }
            exec(compile(save_module, str(source), "exec"), env)
            env["save_search_index"]()
            self.assertTrue(path.exists())
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), data)
            self.assertFalse(path.with_suffix(".tmp").exists())


if __name__ == "__main__":
    unittest.main()
