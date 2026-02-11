"""Tests for generate_mindboxes.py."""

import sys
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from generate_mindboxes import (
    Entry,
    build_mindboxes,
    parse_entries,
    slugify,
    write_mindboxes,
)


class TestSlugify:
    def test_simple_topic(self):
        assert slugify("yoda-quotes") == "yoda-quotes"

    def test_uppercase(self):
        assert slugify("Yoda-Quotes") == "yoda-quotes"

    def test_special_chars(self):
        assert slugify("foo@bar!baz") == "foo-bar-baz"

    def test_empty_string(self):
        assert slugify("") == "topic"

    def test_only_special_chars(self):
        assert slugify("@#$") == "topic"


class TestParseEntries:
    def test_basic_format(self):
        """Test standard format: # YYYY-MM-DD HHMM title"""
        lines = [
            "# 2025-11-09 2041 Sample",
            "Body line 1",
            "Body line 2",
        ]
        entries = list(parse_entries(lines))
        assert len(entries) == 1
        assert entries[0].date == "2025-11-09"
        assert entries[0].time == "2041"
        assert entries[0].title == "Sample"
        assert entries[0].body == ["Body line 1", "Body line 2"]
        assert entries[0].line_no == 1

    def test_mindbox_entry(self):
        """Test entry with mindbox marker."""
        lines = [
            "# 2025-11-09 2042 mindbox:yoda-quotes my first entry",
            "Do or do not.",
        ]
        entries = list(parse_entries(lines))
        assert len(entries) == 1
        assert entries[0].topic == "yoda-quotes"
        assert entries[0].is_mindbox is True

    def test_weekday_format(self):
        """Test weekday prefix format: # Di YYYY-MM-DD HHMM:SS title"""
        lines = [
            "# Di 2025-12-23 1424:21 mindbox:yoda-quotes und noch ein Eintrag",
            "Body text here.",
        ]
        entries = list(parse_entries(lines))
        assert len(entries) == 1
        assert entries[0].date == "2025-12-23"
        assert entries[0].time == "1424:21"
        assert entries[0].topic == "yoda-quotes"

    def test_weekday_format_with_dash(self):
        """Test weekday format with dash separator: # Mo YYYY-MM-DD HHMM:SS - title"""
        lines = [
            "# Mo 2025-10-13 0951:57 - irgendeintext",
            "Some body.",
        ]
        entries = list(parse_entries(lines))
        assert len(entries) == 1
        assert entries[0].date == "2025-10-13"
        assert entries[0].time == "0951:57"
        assert "irgendeintext" in entries[0].title

    def test_time_with_seconds(self):
        """Test time format with seconds: HHMM:SS"""
        lines = [
            "# 2025-10-04 0903:32 Budget check",
        ]
        entries = list(parse_entries(lines))
        assert len(entries) == 1
        assert entries[0].time == "0903:32"

    def test_multiple_entries(self):
        """Test parsing multiple entries."""
        lines = [
            "# 2025-11-09 2041 First entry",
            "Body 1",
            "# 2025-11-09 2042 Second entry",
            "Body 2",
        ]
        entries = list(parse_entries(lines))
        assert len(entries) == 2
        assert entries[0].title == "First entry"
        assert entries[1].title == "Second entry"

    def test_no_title(self):
        """Test entry without title."""
        lines = [
            "# 2025-10-03 1716",
            "Just body.",
        ]
        entries = list(parse_entries(lines))
        assert len(entries) == 1
        assert entries[0].title == ""


class TestBuildMindboxes:
    def test_groups_by_topic(self):
        """Test that entries are grouped by slugified topic."""
        entries = [
            Entry("2025-01-01", "1000", "mindbox:yoda-quotes first", "yoda-quotes", 1),
            Entry("2025-01-02", "1100", "mindbox:yoda-quotes second", "yoda-quotes", 5),
            Entry("2025-01-03", "1200", "mindbox:other topic", "other", 10),
        ]
        topics = build_mindboxes(entries)
        assert "yoda-quotes" in topics
        assert "other" in topics
        assert len(topics["yoda-quotes"]) == 2
        assert len(topics["other"]) == 1

    def test_ignores_non_mindbox(self):
        """Test that non-mindbox entries are ignored."""
        entries = [
            Entry("2025-01-01", "1000", "Regular entry", None, 1),
            Entry("2025-01-02", "1100", "mindbox:yoda topic", "yoda", 5),
        ]
        topics = build_mindboxes(entries)
        assert len(topics) == 1
        assert "yoda" in topics


class TestWriteMindboxes:
    def test_creates_mb_files(self, tmp_path):
        """Test that .mb files are created correctly."""
        entries = [
            Entry("2025-01-01", "1000", "mindbox:test-topic", "test-topic", 1, ["Body line"]),
        ]
        topics = build_mindboxes(entries)
        write_mindboxes(topics, tmp_path, "journal.txt")

        mb_file = tmp_path / "test-topic.mb"
        assert mb_file.exists()

        content = mb_file.read_text()
        assert "*mindbox-test-topic*" in content
        assert "2025-01-01 1000" in content
        assert "Body line" in content
        assert content.rstrip("\n").endswith("# vim: ft=plog:")

    def test_entries_in_reverse_order(self, tmp_path):
        """Test that entries appear newest-first in generated files."""
        entries = [
            Entry("2025-01-01", "1000", "mindbox:topic first", "topic", 1, ["old"]),
            Entry("2025-06-15", "1400", "mindbox:topic second", "topic", 5, ["new"]),
        ]
        topics = build_mindboxes(entries)
        write_mindboxes(topics, tmp_path, "journal.txt")

        content = (tmp_path / "topic.mb").read_text()
        pos_new = content.index("2025-06-15 1400")
        pos_old = content.index("2025-01-01 1000")
        assert pos_new < pos_old, "Newest entry should appear before oldest"

    def test_removes_stale_files(self, tmp_path):
        """Test that old .mb files not in current topics are removed."""
        # Create a stale file
        stale = tmp_path / "old-topic.mb"
        stale.write_text("stale content")

        entries = [
            Entry("2025-01-01", "1000", "mindbox:new-topic", "new-topic", 1),
        ]
        topics = build_mindboxes(entries)
        write_mindboxes(topics, tmp_path, "journal.txt")

        assert not stale.exists()
        assert (tmp_path / "new-topic.mb").exists()
