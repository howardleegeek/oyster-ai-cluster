#!/bin/bash
# Setup launchd for ClawPhones crash feedback loop
# Usage: bash ~/Downloads/scripts/setup_launchd.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLIST_DIR="$SCRIPT_DIR/launchd"
LAUNCH_AGENTS="$HOME/Library/LaunchAgents"

echo "=== ClawPhones Crash Feedback Loop Setup ==="

# 1. Set OpenRouter API key in crash-analyzer plist
read -p "Enter OpenRouter API key (or press Enter to skip): " OPENROUTER_KEY
if [ -n "$OPENROUTER_KEY" ]; then
    sed -i '' "s|SET_YOUR_KEY_HERE|$OPENROUTER_KEY|" "$PLIST_DIR/ai.clawphones.crash-analyzer.plist"
    echo "✓ API key set"
fi

# 2. Make scripts executable
chmod +x "$SCRIPT_DIR/crash_analyzer.py"
chmod +x "$SCRIPT_DIR/auto_fix_dispatcher.py"
echo "✓ Scripts made executable"

# 3. Create logs directory
mkdir -p "$SCRIPT_DIR/logs"
echo "✓ Logs directory ready"

# 4. Copy plists to LaunchAgents
cp "$PLIST_DIR/ai.clawphones.crash-analyzer.plist" "$LAUNCH_AGENTS/"
cp "$PLIST_DIR/ai.clawphones.auto-fix.plist" "$LAUNCH_AGENTS/"
echo "✓ Plists copied to $LAUNCH_AGENTS"

# 5. Load agents
launchctl load "$LAUNCH_AGENTS/ai.clawphones.crash-analyzer.plist"
launchctl load "$LAUNCH_AGENTS/ai.clawphones.auto-fix.plist"
echo "✓ Agents loaded"

echo ""
echo "=== Setup Complete ==="
echo "Crash Analyzer: runs every 30 min (and once now)"
echo "Auto-Fix Dispatcher: runs every 30 min"
echo ""
echo "Check status:"
echo "  launchctl list | grep clawphones"
echo ""
echo "View logs:"
echo "  tail -f ~/Downloads/scripts/logs/crash_analyzer.log"
echo "  tail -f ~/Downloads/scripts/logs/auto_fix_dispatcher.log"
echo ""
echo "Unload:"
echo "  launchctl unload ~/Library/LaunchAgents/ai.clawphones.crash-analyzer.plist"
echo "  launchctl unload ~/Library/LaunchAgents/ai.clawphones.auto-fix.plist"
