#!/bin/sh
# aura installer for macOS and Linux:
#   curl -fsSL https://raw.githubusercontent.com/umer-farooq230/aura/main/install.sh | sh
set -e

REPO="${AURA_REPO:-umer-farooq230/aura}"
DEST="${AURA_INSTALL_DIR:-$HOME/.local/bin}"

case "$(uname -s)-$(uname -m)" in
  Linux-x86_64)                 ASSET="aura-linux-x64" ;;
  Darwin-x86_64)                ASSET="aura-macos-x64" ;;
  Darwin-arm64|Darwin-aarch64)  ASSET="aura-macos-arm64" ;;
  *) echo "Sorry, no prebuilt aura for $(uname -s) $(uname -m). Try: pipx install aura-ascii" >&2; exit 1 ;;
esac

URL="https://github.com/$REPO/releases/latest/download/$ASSET"
mkdir -p "$DEST"

echo "Downloading $ASSET ..."
if command -v curl >/dev/null 2>&1; then
  curl -fsSL "$URL" -o "$DEST/aura"
elif command -v wget >/dev/null 2>&1; then
  wget -qO "$DEST/aura" "$URL"
else
  echo "Need curl or wget." >&2; exit 1
fi
chmod +x "$DEST/aura"

echo "Installed to $DEST/aura"
case ":$PATH:" in
  *":$DEST:"*) echo "All set - try:  aura --list" ;;
  *) echo "Add it to your PATH:  export PATH=\"$DEST:\$PATH\"   (put that line in ~/.bashrc or ~/.zshrc)" ;;
esac
