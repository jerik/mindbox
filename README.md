# Mindbox Journal Toolkit

This repo keeps a plain-text journal plus tooling to extract "mindbox" knowledge snippets and browse them from Vim (like mini help files).

## Generating mindboxes

Mindbox entries follow the pattern `# YYYY-MM-DD HH:MM mindbox:<topic>` inside `journal.txt`. Run:

```sh
python3 scripts/generate_mindboxes.py
```

The script rewrites `mindboxes/<topic>.mb` for every topic it finds, including timestamps and source line numbers. Re-run it whenever `journal.txt` changes or wire it into a build step.

## Vim integration

The plugin at `plugin/mindbox.vim` exposes three commands once loaded:

- `:MindboxList` – show all topics detected in `mindboxes/`
- `:Mindbox <topic>` – open a topic buffer (read-only, help-styled)
- `:MindboxSearch <pattern>` – run `vimgrep` across all topics and open the quickfix list

### Installing with vim-plug

If this repo is hosted online (e.g., GitHub) use the standard plug declaration in your `~/.vimrc` or `init.vim`:

```vim
call plug#begin('~/.vim/plugged')
Plug 'jerik/mindbox' " replace with the actual repo slug
call plug#end()
```

For a local checkout (useful while developing), point vim-plug at the absolute path:

```vim
call plug#begin('~/.vim/plugged')
Plug '/foo/bar/mindbox'
call plug#end()
```

After installing, restart Vim (or `:source` your config). The plugin automatically looks for mindbox files in `<repo>/mindboxes`. To override the location, set `let g:mindbox_directory = '/path/to/mindboxes'` *before* calling `plug#end()`.

### Workflow tips

1. Keep writing `mindbox:<topic>` entries in `journal.txt`.
2. Run `python3 scripts/generate_mindboxes.py` to refresh the topic files (consider a `make mindbox` wrapper).
3. In Vim, use `:MindboxList` to discover topics, `:Mindbox topic-name` to read them, and `:MindboxSearch keyword` to jump via the quickfix list.

Everything stays text-based and cross-platform, so the same workflow works on macOS, Linux, and Windows.
