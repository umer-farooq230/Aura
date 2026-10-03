"""Launcher used by PyInstaller to build the standalone `aura` binary."""

from ..src.aura.cli import main

raise SystemExit(main())
