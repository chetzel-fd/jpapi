#!/bin/bash
# JPAPI Pre-Refactoring Checklist
# Run this before any major structural changes

echo "🚨 JPAPI Pre-Refactoring Checklist"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

echo "1. Creating backup..."
echo "-------------------"
backup_file="jpapi_backup_$(date +%Y%m%d_%H%M%S).tar.gz"
if tar -czf "$backup_file" . --exclude='.git' --exclude='venv' --exclude='.mypy_cache' --exclude='*.tar.gz' >/dev/null 2>&1; then
    print_status 0 "Backup created: $backup_file"
else
    print_status 1 "Failed to create backup"
    exit 1
fi

echo ""
echo "2. Testing current CLI functionality..."
echo "--------------------------------------"
working_commands=0
total_commands=0

commands=("list" "export" "search" "tools" "devices" "create" "delete" "move" "info" "experimental" "scripts" "update" "list-profiles-scoped" "safety" "roles" "advanced-searches" "extension-attributes" "user-groups" "mobile-apps" "packages" "backup")

for cmd in "${commands[@]}"; do
    total_commands=$((total_commands + 1))
    if python3 src/cli/main.py $cmd --help >/dev/null 2>&1; then
        working_commands=$((working_commands + 1))
    fi
done

echo "Working commands: $working_commands/$total_commands"
if [ $working_commands -eq $total_commands ]; then
    print_status 0 "All CLI commands working"
else
    print_status 1 "Some CLI commands broken - fix before refactoring"
    exit 1
fi

echo ""
echo "3. Checking for circular imports..."
echo "----------------------------------"
if python3 -c "import sys; sys.path.insert(0, 'src'); import cli.main" >/dev/null 2>&1; then
    print_status 0 "No circular imports"
else
    print_status 1 "Circular imports detected"
    echo "Run: python3 -c \"import sys; sys.path.insert(0, 'src'); import cli.main\""
    exit 1
fi

echo ""
echo "4. Analyzing current structure..."
echo "--------------------------------"
echo "Top-level directories:"
ls -1 | grep -v "^\." | sort

echo ""
echo "Checking for duplicates:"
duplicates_found=0

if [ -d "src/core" ] && [ -d "core" ]; then
    echo -e "${YELLOW}⚠️  DUPLICATE: src/core/ and core/${NC}"
    duplicates_found=1
fi

if [ -d "src/lib" ] && [ -d "lib" ]; then
    echo -e "${YELLOW}⚠️  DUPLICATE: src/lib/ and lib/${NC}"
    duplicates_found=1
fi

if [ -d "src/framework" ] && [ -d "framework" ]; then
    echo -e "${YELLOW}⚠️  DUPLICATE: src/framework/ and framework/${NC}"
    duplicates_found=1
fi

if [ $duplicates_found -eq 0 ]; then
    print_status 0 "No duplicate directories found"
else
    echo -e "${YELLOW}⚠️  Duplicates found - consider cleaning up before refactoring${NC}"
fi

echo ""
echo "5. Checking dependencies..."
echo "--------------------------"
echo "Core imports:"
core_imports=$(find . -name "*.py" -exec grep -l "from core\." {} \; | wc -l)
echo "Files importing from core: $core_imports"

echo "Lib imports:"
lib_imports=$(find . -name "*.py" -exec grep -l "from lib\." {} \; | wc -l)
echo "Files importing from lib: $lib_imports"

echo ""
echo "6. Pre-refactoring recommendations..."
echo "------------------------------------"
echo "✅ Safe to proceed with refactoring if:"
echo "   - All CLI commands are working"
echo "   - No circular imports"
echo "   - Backup is created"
echo "   - You have a clear plan"

echo ""
echo "⚠️  Consider before refactoring:"
echo "   - Remove duplicate directories first"
echo "   - Test each change incrementally"
echo "   - Keep working reference code"
echo "   - Document all changes"

echo ""
echo "7. Quick recovery commands..."
echo "----------------------------"
echo "If refactoring goes wrong:"
echo "   tar -xzf $backup_file"
echo "   git checkout HEAD -- src/cli/main.py"
echo "   python3 src/cli/main.py list --help"

echo ""
echo "🎯 Ready for refactoring!"
echo "========================="
echo "Backup: $backup_file"
echo "CLI Status: $working_commands/$total_commands commands working"
echo "Structure: $(ls -1 | grep -v "^\." | wc -l) top-level directories"
