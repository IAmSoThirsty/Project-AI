# ============================================================================ #
#                                                            DATE: 2026-03-10 #
#                                                          TIME: 15:01:58 PST #
#                                                        PRODUCTIVITY: Active #
# ============================================================================ #

#                                           [2026-03-03 13:45]
#                                          Productivity: Active
#!/bin/bash
# Legion Mini Auto-Launch for Linux/macOS
# Opens installation wizard in default browser

echo ""
echo "================================================"
echo "   LEGION MINI - Personal AI Assistant"
echo "================================================"
echo ""
echo "   Launching installation wizard..."
echo ""

# Detect platform and open browser
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open "$(dirname "$0")/autorun_wizard.html"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open "$(dirname "$0")/autorun_wizard.html" 2>/dev/null || \
    sensible-browser "$(dirname "$0")/autorun_wizard.html" 2>/dev/null || \
    firefox "$(dirname "$0")/autorun_wizard.html" 2>/dev/null || \
    google-chrome "$(dirname "$0")/autorun_wizard.html" 2>/dev/null
else
    echo "Unsupported platform. Please open autorun_wizard.html manually."
fi

sleep 1
