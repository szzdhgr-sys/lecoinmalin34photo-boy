import unittest

from bot_v6 import (
    configured_admin_ids,
    env_int,
    format_uptime,
    is_admin_user,
    ordered_message_ids,
)


class BotV6Tests(unittest.TestCase):
    def test_admin_fail_closed(self):
        self.assertFalse(is_admin_user(123, configured_admin_ids("")))
        self.assertTrue(is_admin_user(123, configured_admin_ids("123, 456")))
        self.assertFalse(is_admin_user(999, configured_admin_ids("123 456")))

    def test_page_size_bounds(self):
        self.assertEqual(env_int("abc", 8, 1, 20), 8)
        self.assertEqual(env_int("999", 8, 1, 20), 20)
        self.assertEqual(env_int("-5", 8, 1, 20), 1)

    def test_media_ids_sorted_unique(self):
        self.assertEqual(
            ordered_message_ids([42, 12, "12", 99, 0, -5, "invalid"]),
            [12, 42, 99],
        )

    def test_media_limit(self):
        self.assertEqual(len(ordered_message_ids(range(1, 150))), 100)

    def test_uptime(self):
        self.assertEqual(format_uptime(62), "1min 2s")
        self.assertEqual(format_uptime(3601), "1h 0min")


if __name__ == "__main__":
    unittest.main()
