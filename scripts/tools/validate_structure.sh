#!/bin/bash
# JPAPI Structure Validator
# Ensures clean, consistent directory structure

echo "🏗️ JPAPI Structure Validation"
echo "=============================="

echo ""
echo "1. Top-level directory analysis..."
echo "---------------------------------"
echo "Current top-level directories:"
ls -1 | grep -v "^\." | sort

echo ""
echo "2. Checking for structural issues..."
echo "-----------------------------------"

# Check for too many top-level directories
dir_count=$(ls -1 | grep -v "^\." | wc -l)
if [ $dir_count -gt 15 ]; then
    echo "⚠️  Too many top-level directories ($dir_count). Consider consolidation."
else
    echo "✅ Reasonable number of top-level directories ($dir_count)"
fi

echo ""
echo "3. Checking for duplicates..."
echo "----------------------------"

# Check for duplicate directories
if [ -d "src/core" ] && [ -d "core" ]; then
    echo "❌ DUPLICATE: src/core/ and core/ - Remove one"
    echo "   Recommendation: Keep core/ (CLI imports from here)"
fi

if [ -d "src/lib" ] && [ -d "lib" ]; then
    echo "❌ DUPLICATE: src/lib/ and lib/ - Remove one"
    echo "   Recommendation: Keep lib/ (CLI imports from here)"
fi

if [ -d "src/framework" ] && [ -d "framework" ]; then
    echo "❌ DUPLICATE: src/framework/ and framework/ - Remove one"
    echo "   Recommendation: Remove framework/ (not used by CLI)"
fi

if [ -d "src/apps" ] && [ -d "apps" ]; then
    echo "❌ DUPLICATE: src/apps/ and apps/ - Remove one"
    echo "   Recommendation: Keep apps/ (top-level)"
fi

echo ""
echo "4. Checking CLI import paths..."
echo "------------------------------"
echo "CLI main.py imports from:"
grep -n "sys.path.insert" src/cli/main.py

echo ""
echo "5. Checking for clutter..."
echo "-------------------------"
clutter_dirs=("components" "dashboards" "gui" "addons" "assets" "bin_backup" "jpapi.egg-info" "private" "tmp")

for dir in "${clutter_dirs[@]}"; do
    if [ -d "$dir" ]; then
        echo "⚠️  Clutter directory found: $dir/"
        echo "   Consider removing or moving to appropriate location"
    fi
done

echo ""
echo "6. Recommended structure..."
echo "--------------------------"
echo "✅ Keep these directories:"
echo "   bin/           # Executables"
echo "   src/           # Main source code"
echo "   core/          # Core interfaces (CLI imports from here)"
echo "   lib/           # Library utilities (CLI imports from here)"
echo "   config/        # Configuration files"
echo "   data/          # Data files"
echo "   docs/          # Documentation"
echo "   tests/         # Test files"
echo "   scripts/       # Utility scripts"
echo "   exports/       # Export outputs"

echo ""
echo "7. Structure health score..."
echo "---------------------------"
score=100

# Deduct points for issues
if [ -d "src/core" ] && [ -d "core" ]; then
    score=$((score - 20))
fi
if [ -d "src/lib" ] && [ -d "lib" ]; then
    score=$((score - 20))
fi
if [ -d "src/framework" ] && [ -d "framework" ]; then
    score=$((score - 15))
fi
if [ $dir_count -gt 15 ]; then
    score=$((score - 10))
fi

echo "Structure Health Score: $score/100"

if [ $score -ge 90 ]; then
    echo "✅ Excellent structure!"
elif [ $score -ge 70 ]; then
    echo "⚠️  Good structure, minor improvements needed"
else
    echo "❌ Poor structure, refactoring recommended"
fi
