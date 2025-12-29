#!/usr/bin/env python3
"""Generate per-topic mindbox files from journal entries."""

from __future__ import annotations

import argparse
import re
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

ENTRY_RE = re.compile(
    r"^#\s+(?:[A-Za-z]{2}\s+)?"  # optional weekday prefix (Mo, Di, Mi, etc.)
    r"(?P<date>\d{4}-\d{2}-\d{2})\s+"
    r"(?P<time>\d{4}(?::\d{2})?)"  # HHMM or HHMM:SS
    r"(?:\s+(?P<title>.*))?$"
)
MINDBOX_RE = re.compile(r"mindbox:(?P<topic>[^\s#]+)")


def slugify(topic: str) -> str:
    slug = topic.strip().lower()
    slug = re.sub(r"[^a-z0-9_-]+", "-", slug)
    slug = slug.strip("-")
    return slug or "topic"


@dataclass
class Entry:
    date: str
    time: str
    title: str
    topic_raw: str | None
    line_no: int
    body: list[str] = field(default_factory=list)

    @property
    def is_mindbox(self) -> bool:
        return self.topic_raw is not None

    @property
    def topic(self) -> str | None:
        return self.topic_raw


def parse_entries(lines: Iterable[str]) -> Iterable[Entry]:
    current: Entry | None = None
    for idx, line in enumerate(lines, start=1):
        match = ENTRY_RE.match(line)
        if match:
            if current is not None:
                yield current
            title = match.group("title") or ""
            topic_match = MINDBOX_RE.search(title)
            topic = topic_match.group("topic") if topic_match else None
            current = Entry(
                date=match.group("date"),
                time=match.group("time"),
                title=title.strip(),
                topic_raw=topic,
                line_no=idx,
            )
        else:
            if current is not None:
                current.body.append(line.rstrip("\n"))
    if current is not None:
        yield current


def build_mindboxes(entries: Iterable[Entry]) -> dict[str, list[Entry]]:
    topics: dict[str, list[Entry]] = {}
    for entry in entries:
        if not entry.is_mindbox or entry.topic is None:
            continue
        slug = slugify(entry.topic)
        topics.setdefault(slug, []).append(entry)
    return topics


def write_mindboxes(topics: dict[str, list[Entry]], output_dir: Path, source_name: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    desired = set(topics.keys())
    for existing in output_dir.glob("*.mb"):
        if existing.stem not in desired:
            existing.unlink()

    for slug, entries in sorted(topics.items()):
        path = output_dir / f"{slug}.mb"
        display_topic = entries[0].topic or slug
        helptag = f"mindbox-{slug}"
        with path.open("w", encoding="utf-8") as fh:
            fh.write(f"*{helptag}* Mindbox topic: {display_topic}\n")
            fh.write("=" * 79 + "\n")
            for entry in entries:
                header = f"{entry.date} {entry.time} ({source_name}:{entry.line_no})"
                fh.write(header + "\n")
                if entry.title:
                    fh.write(f"Title: {entry.title}\n")
                if entry.body:
                    for body_line in entry.body:
                        fh.write(body_line + "\n")
                fh.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate mindbox files from journal")
    parser.add_argument("journal", nargs="?", default="journal.txt", help="Path to journal.txt")
    parser.add_argument(
        "--output",
        default="mindboxes",
        help="Directory for generated .mb files (default: mindboxes)",
    )
    args = parser.parse_args()

    journal_path = Path(args.journal)
    if not journal_path.exists():
        raise SystemExit(f"Journal not found: {journal_path}")

    entries = list(parse_entries(journal_path.read_text(encoding="utf-8").splitlines()))
    topics = build_mindboxes(entries)

    if not topics:
        print("No mindbox entries found.")
        return

    output_dir = Path(args.output)
    write_mindboxes(topics, output_dir, source_name=journal_path.name)
    print(f"Wrote {len(topics)} mindbox file(s) to {output_dir}")


if __name__ == "__main__":
    main()
