#!/bin/bash
# Setup script for BigQuery Migration Environment
# Run this before using the migration script each year

set -e  # Exit on any error

echo "🔧 Setting up BigQuery Migration Environment for Guttmacher Legislative Tracker"
echo "================================================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

PROJECT_ID="guttmacher-legislative-tracker"
ACCOUNT="fryda.guedes@gmail.com"

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Step 1: Check if gcloud is installed
echo "Step 1: Checking gcloud installation..."
if ! command -v gcloud &> /dev/null; then
    print_error "gcloud CLI is not installed. Please install it first:"
    echo "  macOS: brew install --cask google-cloud-sdk"
    echo "  Other: https://cloud.google.com/sdk/docs/install"
    exit 1
fi
print_status "gcloud CLI found"

# Step 2: Set correct account
echo ""
echo "Step 2: Setting correct Google Cloud account..."
gcloud config set account $ACCOUNT
print_status "Account set to $ACCOUNT"

# Step 3: Set correct project  
echo ""
echo "Step 3: Setting correct project..."
gcloud config set project $PROJECT_ID
print_status "Project set to $PROJECT_ID"

# Step 4: Ensure we're authenticated
echo ""
echo "Step 4: Checking authentication..."
if ! gcloud auth list --filter="status:ACTIVE" --format="value(account)" | grep -q $ACCOUNT; then
    print_warning "Not authenticated. Opening browser for login..."
    gcloud auth login
fi
print_status "User authentication confirmed"

# Step 5: Fix Application Default Credentials (the key fix!)
echo ""
echo "Step 5: Setting up Application Default Credentials..."
print_warning "Revoking existing ADC to ensure clean setup..."
gcloud auth application-default revoke --quiet 2>/dev/null || true

print_warning "Setting up ADC with correct project..."
gcloud auth application-default login --project=$PROJECT_ID
print_status "Application Default Credentials configured with correct quota project"

# Step 6: Verify BigQuery permissions
echo ""
echo "Step 6: Verifying BigQuery access..."
if python3 -c "
from google.cloud import bigquery
client = bigquery.Client(project='$PROJECT_ID')
datasets = list(client.list_datasets())
print(f'✅ Found {len(datasets)} datasets')
for ds in datasets:
    print(f'  - {ds.dataset_id}')
"; then
    print_status "BigQuery access verified"
else
    print_error "BigQuery access failed. Check permissions."
    exit 1
fi

# Step 7: Check mdbtools
echo ""
echo "Step 7: Checking mdbtools installation..."
if ! command -v mdb-tables &> /dev/null; then
    print_error "mdbtools not found. Installing..."
    if command -v brew &> /dev/null; then
        brew install mdbtools
    else
        print_error "Please install mdbtools manually:"
        echo "  macOS: brew install mdbtools"
        echo "  Ubuntu: sudo apt-get install mdbtools"
        exit 1
    fi
fi
print_status "mdbtools found"

# Step 8: Check Python dependencies
echo ""
echo "Step 8: Checking Python environment..."
if [ -d "venv" ]; then
    print_warning "Virtual environment found. Make sure to activate it:"
    echo "  source venv/bin/activate"
else
    print_warning "No virtual environment found. Consider creating one:"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
fi

# Check if we can import required packages
if python3 -c "import pandas, google.cloud.bigquery, yaml, dotenv" 2>/dev/null; then
    print_status "Required Python packages available"
else
    print_warning "Some Python packages missing. Run:"
    echo "  pip install -r requirements.txt"
fi

# Step 9: Check .env file
echo ""
echo "Step 9: Checking configuration..."
if [ -f ".env" ]; then
    print_status ".env file found"
    echo "Current configuration:"
    cat .env | grep -E "^(GCP_PROJECT_ID|BQ_DATASET_ID)" || true
else
    print_warning ".env file not found. Creating from template..."
    cp .env.example .env
    sed -i.bak "s/your-actual-project-id/$PROJECT_ID/g" .env
    print_status "Created .env file with correct project ID"
fi

echo ""
echo "================================================================="
print_status "Setup complete! You can now run the migration script:"
echo ""
echo "  python3 migrate.py                    # Full migration"
echo "  python3 migrate.py --test             # Test results"
echo "  python3 migrate.py --cleanup          # Clean up old objects"
echo ""
print_warning "Remember to activate your virtual environment if using one:"
echo "  source venv/bin/activate"
echo ""
echo "================================================================="