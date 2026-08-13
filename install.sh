#!/bin/bash

set -e

APP_NAME="gclone"
INSTALL_DIR="$HOME/.local/bin"
SOURCE_DIR="$(cd "$(dirname "$0")" && pwd)"

echo ""
echo "🚀 Installing $APP_NAME..."
echo ""

# Check Python
if ! command -v python3 >/dev/null 2>&1; then
    echo "❌ Python 3 tidak ditemukan."
    echo ""
    echo "Install Python 3 terlebih dahulu."
    exit 1
fi

# Check Git
if ! command -v git >/dev/null 2>&1; then
    echo "❌ Git tidak ditemukan."
    exit 1
fi

# Create bin directory
mkdir -p "$INSTALL_DIR"

# Copy executable
cp "$SOURCE_DIR/gclone.py" "$INSTALL_DIR/gclone.py"

chmod +x "$INSTALL_DIR/gclone.py"

# Create launcher
cat > "$INSTALL_DIR/gclone" <<EOF
#!/bin/bash
exec python3 "$INSTALL_DIR/gclone.py" "\$@"
EOF

chmod +x "$INSTALL_DIR/gclone"

echo "✓ Installed to:"
echo "  $INSTALL_DIR/gclone"
echo ""

# Add PATH to zsh
SHELL_CONFIG="$HOME/.zshrc"

if ! grep -q 'HOME/.local/bin' "$SHELL_CONFIG" 2>/dev/null; then
    echo '' >> "$SHELL_CONFIG"
    echo '# gclone' >> "$SHELL_CONFIG"
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_CONFIG"

    echo "✓ PATH ditambahkan ke ~/.zshrc"
fi

echo ""
echo "Installation selesai."
echo ""
echo "Reload shell:"
echo ""
echo "  source ~/.zshrc"
echo ""
echo "Kemudian:"
echo ""
echo "  gclone help"
echo ""