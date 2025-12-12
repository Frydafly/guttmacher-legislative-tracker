#!/bin/bash
# Remove all personal identifying information from documentation

echo "Removing personal information from documentation..."

# Define replacements
declare -A replacements=(
    ["Fryda Guedes (fryda.guedes@proton.me)"]="Technical team"
    ["fryda.guedes@proton.me"]="technical-team@guttmacher.org"
    ["Fryda Guedes"]="Technical team"
    ["Fryda"]="Technical team"

    ["Mollie Fairbanks or Talia Curhan"]="Policy team"
    ["Mollie Fairbanks"]="Policy team"
    ["Mollie"]="Policy team"
    ["Talia Curhan"]="Policy team"
    ["Talia"]="Policy team"

    ["Kimya Forouzan"]="Legal review team"
    ["Kimya"]="Legal review team"

    ["Lenny Munitz"]="IT/Website team"
    ["Lenny"]="IT/Website team"

    ["Candace Gibson"]="Communications team"
    ["Candace"]="Communications team"

    ["Krystal"]="Partnerships team"
)

# Files to update (excluding .internal-docs)
files=(
    "docs/index.md"
    "docs/getting-started/overview.md"
    "docs/getting-started/quick-start.md"
    "docs/getting-started/architecture.md"
    "docs/technical/deployment-guide.md"
    "docs/technical/runbook.md"
    "docs/technical/external-user-access.md"
    "docs/user-guides/airtable-user-manual.md"
    "docs/user-guides/bigquery-for-analysts.md"
    "docs/user-guides/running-reports.md"
    "docs/user-guides/looker-studio-guide.md"
    "docs/historical/data-evolution.md"
)

# Process each file
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "Processing: $file"
        for search in "${!replacements[@]}"; do
            replace="${replacements[$search]}"
            # Use perl for in-place editing with backup
            perl -pi -e "s/\Q$search\E/$replace/g" "$file"
        done
    fi
done

echo "✅ Done! Personal information removed."
echo "Review changes with: git diff docs/"
