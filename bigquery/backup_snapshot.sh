#!/bin/bash
#
# Create BigQuery snapshots before risky changes
#
# BigQuery table snapshots:
# - Are FREE (no storage cost)
# - Expire after 7 days automatically
# - Provide point-in-time recovery
# - Are perfect for "oh crap" moments
#
# Usage:
#   cd /path/to/bigquery
#   ./backup_snapshot.sh
#
# This creates snapshots of all key tables with timestamp suffix.
# Example: all_historical_bills_unified@20251211_143022
#

set -e  # Exit on error

PROJECT_ID="guttmacher-legislative-tracker"
DATASET_ID="legislative_tracker_historical"
DATE=$(date +%Y%m%d_%H%M%S)

echo "📸 Creating BigQuery snapshots..."
echo "Project: $PROJECT_ID"
echo "Dataset: $DATASET_ID"
echo "Timestamp: $DATE"
echo ""

# Key tables to snapshot
TABLES=(
    "all_historical_bills_unified"
    "comprehensive_bills_authentic"
)

# Create snapshot for each table
for TABLE in "${TABLES[@]}"; do
    echo "Creating snapshot: ${TABLE}@${DATE}..."

    # Check if table exists first
    if bq show "${PROJECT_ID}:${DATASET_ID}.${TABLE}" &>/dev/null; then
        bq cp \
            "${PROJECT_ID}:${DATASET_ID}.${TABLE}" \
            "${PROJECT_ID}:${DATASET_ID}.${TABLE}@${DATE}"
        echo "✅ Snapshot created for $TABLE"
    else
        echo "⚠️  Table $TABLE does not exist, skipping"
    fi
    echo ""
done

echo "🎉 Snapshot process complete!"
echo ""
echo "To restore a snapshot later (within 7 days):"
echo "  bq cp \\"
echo "    ${PROJECT_ID}:${DATASET_ID}.all_historical_bills_unified@${DATE} \\"
echo "    ${PROJECT_ID}:${DATASET_ID}.all_historical_bills_unified_restored"
echo ""
echo "⏰ Snapshots expire automatically after 7 days (no manual cleanup needed)"
