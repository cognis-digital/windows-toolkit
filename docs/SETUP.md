# Guided setup wizard

The fastest way in is the **Cognis Setup Wizard** — a zero-dependency,
standard-library-only Python TUI that walks you through installing the Cognis
tool suite. You never have to memorize a command; you type numbers.

## Launch

```bash
./setup.sh        # macOS / Linux / WSL / git-bash
```
```powershell
./setup.ps1       # Windows PowerShell
```

Or call the wizard directly:

```bash
python cognis_setup.py
```

## What it does

1. **Asks your familiarity (1–5)** once and remembers it (`~/.cognis/setup.json`).
   Level 1 explains everything in plain language; level 5 is terse.
2. **Briefs your environment** — OS, detected package managers, recommended
   install method.
3. **Numbered menu** — quick-install a starter bundle, browse by category, pick
   individual tools, install everything, set up the local AI fleet, configure,
   health-check, or read the glossary.
4. Every action **explains → shows the exact command → confirms `[Y/n]` → runs it**
   via `subprocess`, then returns to the menu. Nothing destructive runs
   unconfirmed.

## Flags

| Flag | Effect |
|---|---|
| `--dry-run` | Print every command but never execute it. |
| `--manifest PATH_OR_URL` | Use a specific `MANIFEST.json` (local path **or** `http(s)://` URL). |
| `--no-curses` | Force the plain ANSI numbered menu. |

## Tool catalog

This repo ships no catalog of its own, so the wizard falls back to the canonical
Cognis arsenal manifest:

```
https://raw.githubusercontent.com/cognis-digital/cognis-arsenal/master/MANIFEST.json
```

It is fetched once (stdlib `urllib`, best-effort) and cached at
`~/.cognis/MANIFEST.json`, so later runs work offline. If no catalog is
reachable, fleet-setup, configure, and help still work — only per-tool installs
need a manifest.

## Non-interactive / piped

The wizard detects a non-TTY and uses the plain ANSI menu, reading choices from
stdin. For example, to open the "pick individual tools" view and exit:

```bash
printf '3\n0\n' | ./setup.sh
```
