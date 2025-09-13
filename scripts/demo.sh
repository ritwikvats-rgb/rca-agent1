#!/usr/bin/env bash
set -e

echo "🚀 RCA Agent Demo - Complete End-to-End Workflow"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_step() {
    echo -e "${BLUE}$1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "incidents/TCK-1001.json" ]; then
    echo -e "${RED}❌ Error: Please run this script from the project root directory${NC}"
    exit 1
fi

# Step 1: Initialize
print_step "Step 1: Initialize git repository and setup"
python -m rca.cli init

echo ""

# Step 2: Triage
print_step "Step 2: Triage incident and analyze candidates"
python -m rca.cli triage incidents/TCK-1001.json

echo ""

# Step 3: Initial RCA
print_step "Step 3: Generate initial RCA document"
python -m rca.cli rca incidents/TCK-1001.json --initial

echo ""

# Step 4: PR Draft
print_step "Step 4: Generate PR draft with proposed fixes"
python -m rca.cli draft-pr incidents/TCK-1001.json

echo ""

# Step 5: Create Ticket
print_step "Step 5: Create Linear ticket"
python -m rca.cli ticket incidents/TCK-1001.json --team FTS

echo ""

# Step 6: Apply Fix
print_step "Step 6: Apply fixes and create fix commit"
FIX_COMMIT=$(python -m rca.cli apply-fix incidents/TCK-1001.json | tail -n1)

echo ""

# Step 7: Final RCA
print_step "Step 7: Generate final RCA with fix information"
python -m rca.cli rca incidents/TCK-1001.json --final --fix-commit "$FIX_COMMIT"

echo ""

# Step 8: Comparison
print_step "Step 8: Generate before/after comparison"
python -m rca.cli compare incidents/TCK-1001.json

echo ""

# Summary
print_step "Demo Summary"
echo "============"

print_success "All steps completed successfully!"
print_info "Generated documents are available in the 'out/' directory:"

if [ -d "out" ]; then
    ls -la out/ | grep -E "\.(md|pdf)$" | while read -r line; do
        filename=$(echo "$line" | awk '{print $NF}')
        echo "  📄 $filename"
    done
fi

echo ""
print_info "Mock Linear tickets are saved in 'linear_mock/' directory:"

if [ -d "linear_mock" ]; then
    ls -la linear_mock/ | grep "\.json$" | while read -r line; do
        filename=$(echo "$line" | awk '{print $NF}')
        echo "  🎫 $filename"
    done
fi

echo ""
print_info "Git history created:"
git log --oneline -5 2>/dev/null || echo "  Git log not available"

echo ""
print_success "🎉 RCA Agent demo completed!"
print_info "This demonstrates how an RCA agent can automate incident response from detection to resolution."

echo ""
echo "Next steps:"
echo "- Review the generated RCA documents in out/"
echo "- Check the mock Linear ticket in linear_mock/"
echo "- Examine the git history to see the fix progression"
echo "- Customize the PRD files and guidelines for your use case"
