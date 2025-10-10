#!/bin/bash
# JPAPI Dependency Checker
# Prevents refactoring disasters by analyzing dependencies

echo "🔍 JPAPI Dependency Analysis"
echo "=============================="

echo ""
echo "1. Checking for duplicate imports..."
echo "-----------------------------------"
echo "Core imports:"
find . -name "*.py" -exec grep -l "from core\." {} \; | sort | uniq -c | sort -nr

echo ""
echo "Lib imports:"
find . -name "*.py" -exec grep -l "from lib\." {} \; | sort | uniq -c | sort -nr

echo ""
echo "2. Checking for circular imports..."
echo "----------------------------------"
if python3 -c "import sys; sys.path.insert(0, 'src'); import cli.main" 2>/dev/null; then
    echo "✅ No circular imports detected"
else
    echo "❌ Circular imports detected!"
    echo "Run: python3 -c \"import sys; sys.path.insert(0, 'src'); import cli.main\""
fi

echo ""
echo "3. Checking CLI command consistency..."
echo "-------------------------------------"
pattern_count=$(grep -r "add_conversational_pattern" src/cli/commands/ | wc -l)
echo "Commands using conversational patterns: $pattern_count"

echo ""
echo "4. Checking for duplicate directories..."
echo "---------------------------------------"
echo "Top-level directories:"
ls -1 | grep -v "^\." | sort

echo ""
echo "Potential duplicates:"
if [ -d "src/core" ] && [ -d "core" ]; then
    echo "❌ DUPLICATE: src/core/ and core/"
fi
if [ -d "src/lib" ] && [ -d "lib" ]; then
    echo "❌ DUPLICATE: src/lib/ and lib/"
fi
if [ -d "src/framework" ] && [ -d "framework" ]; then
    echo "❌ DUPLICATE: src/framework/ and framework/"
fi

echo ""
echo "5. Checking CLI functionality..."
echo "-------------------------------"
commands=("list" "export" "search" "tools" "devices" "create" "delete" "move" "info" "experimental" "scripts" "update" "list-profiles-scoped" "safety" "roles" "advanced-searches" "extension-attributes" "user-groups" "mobile-apps" "packages" "backup")

working=0
broken=0

for cmd in "${commands[@]}"; do
    if python3 src/cli/main.py $cmd --help > /dev/null 2>&1; then
        echo "✅ $cmd"
        ((working++))
    else
        echo "❌ $cmd"
        ((broken++))
    fi
done

echo ""
echo "Summary:"
echo "--------"
echo "Working commands: $working"
echo "Broken commands: $broken"

if [ $broken -gt 0 ]; then
    echo "🚨 CLI has broken commands! Fix before proceeding with refactoring."
    exit 1
else
    echo "✅ All CLI commands working"
fi
