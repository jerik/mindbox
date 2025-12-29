# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Project Overview

Mindbox is a plain-text journal toolkit that extracts "mindbox" knowledge snippets from a journal file and makes them browsable in Vim as help-style buffers.

### Data Flow
```
journal.txt → generate_mindboxes.py → mindboxes/*.mb → Vim plugin
```

### Journal Entry Format
```
# YYYY-MM-DD HHMM [mindbox:<topic>] [optional title]
Body text here...
```
The `mindbox:<topic>` marker designates an entry for extraction. Multiple entries with the same topic are aggregated into a single `.mb` file.

**Examples from journal.txt:**
```
# 2025-11-09 2042 mindbox:yoda-quotes my first entry
# 2025-11-09 2051 mindbox:confucius-quotes here we go
# Di 2025-12-23 1424:21 mindbox:yoda-quotes und noch ein Eintrag
# 2025-10-01 2208 Sprint-Plan
# Mo 2025-10-13 0951:57 - irgendeintext
```

Variants: Weekday prefix (`Di`, `Mo`) and seconds (`:21`) are optional.

### Repo Layout
| Path | Description |
|------|-------------|
| `journal.txt` | Source journal (plain text) |
| `scripts/generate_mindboxes.py` | Parser/generator script |
| `mindboxes/*.mb` | Generated output (never edit manually) |
| `plugin/mindbox.vim` | Vim plugin entrypoint |

### Vim Commands
| Command | Description |
|---------|-------------|
| `:MindboxList` | List all topics |
| `:Mindbox <topic>` | Open topic in help-style buffer |
| `:MindboxSearch <pattern>` | Search via vimgrep, open quickfix |

Config: `g:mindbox_directory` overrides default `<repo>/mindboxes`.

## Non-goals
- No network calls
- No Neovim compatibility (for now)
- Keep everything text-based and cross-platform

---

## Quick Commands

```sh
# Generate
python3 scripts/generate_mindboxes.py

# Python checks
python -m ruff format . && python -m ruff check . && python -m pytest -q

# Vim tests
vim -Nu NONE -n -es -S test/run.vim
```

---

## Development Workflow

### Feature Development

1. **User** creates `USER-STORY.md` with feature description
2. **Dialog:** User + Claude refine together
   - Clarify requirements
   - Define technical details
   - Answer open questions
3. **Decision:** User gives go for implementation
4. **Claude** implements:
   - Reads: `CLAUDE.md`, `USER-STORY.md`, `BACKLOG.md`
   - Updates checkboxes in `USER-STORY.md`
   - Executes DoD
5. **Review:** User + Claude discuss result
6. **Next feature:** New `USER-STORY.md`

### Definition of Done (DoD)

**Before every commit:**
```sh
# 1. Python
python -m ruff format .
python -m ruff check .
python -m pytest -q

# 2. Vimscript
vint plugin/
vim -Nu NONE -n -es -S test/run.vim
```

On failure: Fix until all checks pass.

### Git Workflow
- Main branch: `main` (protected, never push directly)
- Feature branches: `claude/feature-name`
- Commits: English, clear and descriptive

---

## Code Standards

### General
- Code and comments: **English only**
- Prefer small, reviewable diffs
- Adjust tests with every behavioral change
- Maintain backward compatibility (unless explicitly bumping version)

### Python
- Follow **PEP 8** strictly
- **ruff** for formatting and linting
- **pytest** for tests (use `tmp_path` for file I/O)
- Type hints where useful
- Docstrings for public methods

Config in `pyproject.toml`:
- `tool.ruff` + `tool.ruff.format`
- `tool.pytest.ini_options`

### Vimscript
- Keep `plugin/` minimal (wiring only)
- Complex logic → `autoload/mindbox.vim`
- Internal helpers: `s:`-scoped
- Global state only for `g:mindbox_*` config
- Autocmds in dedicated augroup with `autocmd!`
- **vint** for linting (zero warnings)

### Vim Tests
- Headless: `vim -Nu NONE -n -es -S test/run.vim`
- Assertions: `assert_equal()`, `assert_match()`, `assert_true()`, `assert_fails()`
- Layout: `test/run.vim` + `test/test_*.vim`
- Isolation: temp directories, no user vimrc

---

## Tooling

| Tool | Purpose | Required |
|------|---------|----------|
| python3 | Script execution | Yes |
| ruff | Python format/lint | Yes |
| pytest | Python tests | Yes |
| vint | Vimscript lint | Yes |
| git | Version control | Yes |
| uv | Python execution | Optional |

---

## Communication

- Analyze content and prompts critically
- Ask questions when information is unclear
- Label questions as **f1, f2, ... fn**
- Style: **tl;dr** - precise and short
- Verbose answers only on explicit request

---

## Rules for Claude

1. **Never edit generated files** (`mindboxes/*.mb`)
2. **Never push directly to main**
3. **Follow DoD** - all checks green before commit
4. **On new user-facing behavior:** Update README
5. **On failures:** Iterate until green, don't abort
