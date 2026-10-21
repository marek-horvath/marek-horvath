"""Checks for privacy boundaries, API failures, pagination, and safe SVG text."""

import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from xml.etree import ElementTree as ET

SPEC = importlib.util.spec_from_file_location("generate", Path(__file__).resolve().parents[1] / "scripts/generate.py")
generate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(generate)


def repo(name="example", **changes):
    item = dict(name=name, language="Python", pushed_at="2026-10-10T12:00:00Z", private=False,
                visibility="public", fork=False, archived=False, disabled=False, size=10,
                owner={"login": "marek-horvath"}, sensitive_field="MUST NOT BE SAVED")
    item.update(changes)
    return item


class PublicSnapshotTests(unittest.TestCase):
    def test_excludes_private_forks_archived_other_owners_and_profile(self):
        items = [repo(), repo("secret", private=True), repo("fork", fork=True),
                 repo("archived", archived=True), repo("disabled", disabled=True),
                 repo("marek-horvath"), repo("other", owner={"login": "another-person"}),
                 repo("visibility-mismatch", visibility="private"), repo("empty", size=0)]
        with patch.object(generate, "request_json", return_value=items):
            snapshot = generate.fetch_snapshot()
        self.assertEqual(snapshot["repositories"], [{"name": "example", "language": "Python",
                                                    "pushed_at": "2026-10-10T12:00:00Z"}])
        self.assertNotIn("MUST NOT BE SAVED", str(snapshot))

    def test_fetches_second_page(self):
        with patch.object(generate, "request_json", side_effect=[
                [repo(f"repo-{i}") for i in range(100)], [repo("last-page")]]) as api:
            snapshot = generate.fetch_snapshot()
        self.assertEqual(len(snapshot["repositories"]), 101)
        self.assertIn("page=2", api.call_args.args[0])

    def test_rejects_unexpected_persisted_fields_and_invalid_dates(self):
        data = {"owner": "marek-horvath", "as_of": "2026-10-21", "repositories": [
            {"name": "example", "language": "Python", "pushed_at": "not-a-date"}]}
        with self.assertRaises(ValueError):
            generate.validate_snapshot(data)
        data["repositories"][0]["pushed_at"] = "2026-10-10T12:00:00Z"
        data["repositories"][0]["extra"] = "unexpected"
        with self.assertRaises(ValueError):
            generate.validate_snapshot(data)

    def test_rate_limit_fails_without_unbounded_wait(self):
        error = HTTPError("https://api.github.com/test", 403, "rate limit", {}, None)
        with patch.object(generate, "urlopen", side_effect=error), patch.object(generate.time, "sleep") as sleep:
            with self.assertRaisesRegex(RuntimeError, "HTTP 403"):
                generate.request_json("https://api.github.com/test")
        sleep.assert_not_called()

    def test_server_errors_have_bounded_retries(self):
        error = HTTPError("https://api.github.com/test", 503, "unavailable", {}, None)
        with patch.object(generate, "urlopen", side_effect=error) as api, patch.object(generate.time, "sleep") as sleep:
            with self.assertRaises(RuntimeError):
                generate.request_json("https://api.github.com/test")
        self.assertEqual(api.call_count, 3)
        self.assertEqual(sleep.call_count, 2)

    def test_refresh_failure_preserves_snapshot_and_date(self):
        with patch.object(generate, "fetch_snapshot", side_effect=RuntimeError("offline")), \
                patch.object(generate, "write_if_changed") as write, \
                patch.object(generate.sys, "argv", ["generate.py", "--refresh"]):
            self.assertEqual(generate.main(), 0)
        self.assertTrue(all(call.args[0] != generate.SNAPSHOT for call in write.call_args_list))

    def test_svg_escapes_text_and_handles_long_names(self):
        data = {"owner": "marek-horvath", "as_of": "2026-10-21", "repositories": [
            {"name": "x" * 90, "language": "A&B <language>", "pushed_at": "2026-10-10T12:00:00Z"}]}
        for document in generate.outputs(data).values():
            ET.fromstring(document)
            self.assertNotIn("<language>", document)
        self.assertEqual(len(generate.short_name("x" * 90, 33)), 33)


if __name__ == "__main__":
    unittest.main()
