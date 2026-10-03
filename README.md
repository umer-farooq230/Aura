# aura ✨

ASCII portraits in your terminal.

```bash
aura --piccolo -1
```

## Install (pick whatever you like)

No Python needed for the first three.

| you are on | run this |
|---|---|
| macOS / Linux | `curl -fsSL https://raw.githubusercontent.com/umer-farooq230/aura/main/install.sh \| sh` |
| Windows (PowerShell) | `irm https://raw.githubusercontent.com/umer-farooq230/aura/main/install.ps1 \| iex` |
| Homebrew | `brew install umerfarooq-230/tap/aura` |
| Any OS, by hand | grab a file from the [Releases page](https://github.com/umer-farooq230/aura/releases), rename it `aura`, put it on your PATH |
| Python people | `pipx install aura-ascii` or `uv tool install aura-ascii` |

## Knobs

| flag | what it does | default |
|---|---|---|
| `--width N` | characters per row (more = more detail) | fits your terminal |
| `--contrast X` | higher = eyes and outlines pop | 1.3 |
| `--gamma X` | >1 darker, <1 brighter midtones | 1.0 |
| `--sharpen X` | 0 = off, crisp face details | 1.5 |
| `--ramp` | `dense`, `simple` or `blocks` | dense |
| `--invert` | flip light/dark (light terminals) | off |
| `--color` | colour the characters | off |
| `--crop L T R B` | zoom in, 0-1 fractions | none |
| `--out FILE` | also save plain text | - |

```bash
aura --piccolo -1 --width 200 --contrast 1.8 --color
aura --list
```

## Adding pictures (the easy way)

```bash
aura add goku https://site.com/goku.jpg      # from a link
aura add goku ~/Downloads/goku.png           # from a file
aura add goku ~/Downloads/goku-pack/         # a whole folder
aura add goku --clipboard                    # right-click > "Copy image", then run this
aura --file ~/Downloads/pic.jpg              # just try a picture, no saving
```

Each picture is auto-numbered, shrunk, has plain borders trimmed off, and is skipped
if you already have it. They're saved in `~/.aura/images` (change with the `AURA_HOME`
environment variable), so they work with the downloaded binaries too. Run
`aura --goku` with no number for a random one.

Maintainers can use `aura add goku <source> --bundle` from a source checkout to save
straight into the package so the picture ships with the next release.

## Adding pictures by hand

Drop files into `src/aura/images/` named `<name>_<number>.jpg` (png/webp work too):

```
piccolo_1.jpg  ->  aura --piccolo -1
piccolo_2.jpg  ->  aura --piccolo -2
goku_1.png     ->  aura --goku -1     (new flag, automatically)
```

Reinstall (or use `pip install -e .` while developing) and the new flags show up.

Want a character to always look its best? Add per-picture defaults
(crop, contrast, gamma...) in `src/aura/tuning.py`.

## Dev

```bash
pip install -e ".[dev]"
pytest
```
