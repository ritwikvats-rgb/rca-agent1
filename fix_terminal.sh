#!/bin/bash

# VSCode Terminal Fix Script
# This script will help fix the "Shell Integration Unavailable" error

echo "🔧 VSCode Terminal Fix Script"
echo "=============================="

# Check current shell
echo "1. Checking current shell..."
echo "Current shell: $SHELL"

# Check if zsh is available
if command -v zsh &> /dev/null; then
    echo "✅ zsh is available"
else
    echo "❌ zsh not found, installing..."
    # On macOS, zsh should be pre-installed
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "zsh should be pre-installed on macOS. Please check your system."
    fi
fi

# Create VSCode settings directory if it doesn't exist
VSCODE_SETTINGS_DIR="$HOME/Library/Application Support/Code/User"
if [[ "$OSTYPE" == "darwin"* ]]; then
    mkdir -p "$VSCODE_SETTINGS_DIR"
    echo "✅ VSCode settings directory ready"
fi

# Create or update VSCode settings
SETTINGS_FILE="$VSCODE_SETTINGS_DIR/settings.json"

echo "2. Updating VSCode settings..."

# Backup existing settings if they exist
if [ -f "$SETTINGS_FILE" ]; then
    cp "$SETTINGS_FILE" "$SETTINGS_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    echo "✅ Backed up existing settings"
fi

# Create new settings with terminal configuration
cat > "$SETTINGS_FILE" << 'EOF'
{
    "terminal.integrated.defaultProfile.osx": "zsh",
    "terminal.integrated.shellIntegration.enabled": true,
    "terminal.integrated.shellIntegration.decorationsEnabled": "both",
    "terminal.integrated.shellIntegration.history": 100,
    "terminal.integrated.profiles.osx": {
        "zsh": {
            "path": "/bin/zsh",
            "args": ["-l"]
        },
        "bash": {
            "path": "/bin/bash",
            "args": ["-l"]
        }
    }
}
EOF

echo "✅ VSCode settings updated"

# Set default shell to zsh if not already
if [ "$SHELL" != "/bin/zsh" ]; then
    echo "3. Setting default shell to zsh..."
    chsh -s /bin/zsh
    echo "✅ Default shell set to zsh (restart terminal to take effect)"
else
    echo "3. ✅ Shell is already zsh"
fi

echo ""
echo "🎉 Terminal fix complete!"
echo ""
echo "Next steps:"
echo "1. Restart VSCode completely (Quit and reopen)"
echo "2. Open a new terminal in VSCode (CMD + \`)"
echo "3. If still not working, try: CMD + Shift + P → 'Terminal: Kill All Terminals'"
echo "4. Then open a new terminal again"
echo ""
echo "Test commands to verify it's working:"
echo "  pwd"
echo "  echo 'Terminal working!'"
echo "  cd /Users/ritwikvats/rca-agent"
echo "  source .venv/bin/activate"
echo ""
