# BigQuery Pipeline Setup Guide

## Prerequisites

1. **Python 3.8+**
2. **Google Cloud SDK** (for authentication)
3. **ODBC Driver** for Access databases

## Installation Steps

### 1. Create Virtual Environment (Required)

```bash
# From project root
cd bigquery
python -m venv venv

# Activate virtual environment
# Mac/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Upgrade pip to latest version
pip install --upgrade pip
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Note**: The `venv/` directory is excluded from git via `.gitignore`. Each developer creates their own virtual environment locally.

### 3. Install ODBC Drivers

#### macOS
```bash
# Install mdbtools as alternative
brew install mdbtools

# OR install actual ODBC driver
# Download from: https://www.microsoft.com/en-us/download/details.aspx?id=54920
```

#### Windows
- Already included with Windows
- Or download latest: https://www.microsoft.com/en-us/download/details.aspx?id=54920

#### Linux
```bash
# Ubuntu/Debian
sudo apt-get install mdbtools unixodbc-dev

# For pyodbc
sudo apt-get install python3-dev
```

### 4. Google Cloud Authentication

```bash
# Install gcloud CLI if not already installed
# https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth application-default login

# Set your project
gcloud config set project YOUR_PROJECT_ID
```

### 5. Create BigQuery Dataset

```bash
# Create staging dataset
bq mk --dataset --location=US YOUR_PROJECT_ID:legislative_tracker_staging
```

### 6. Configure Environment Variables

Create `.env` file in the bigquery directory:

```env
# Google Cloud
GCP_PROJECT_ID=your-project-id
BQ_DATASET_ID=legislative_tracker_staging

# Optional: specific credentials file
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
```

## Testing the Setup

```python
# Test script: test_connection.py
import pyodbc
from google.cloud import bigquery

# Test BigQuery connection
client = bigquery.Client()
print(f"Connected to project: {client.project}")

# List ODBC drivers
drivers = [x for x in pyodbc.drivers()]
print(f"Available ODBC drivers: {drivers}")

# Look for Access driver
access_drivers = [d for d in drivers if 'Access' in d or 'MDB' in d]
print(f"Access drivers found: {access_drivers}")
```

## Troubleshooting

### pyodbc installation fails on Mac
```bash
# Install prerequisites
brew install unixodbc
export LDFLAGS="-L/usr/local/opt/unixodbc/lib"
export CPPFLAGS="-I/usr/local/opt/unixodbc/include"
pip install pyodbc
```

### No Access drivers found
- Use mdbtools approach instead (see mdb-extraction-guide.md)
- Or export to CSV from Access manually for initial load

### Google Cloud authentication errors
```bash
# Check current authentication
gcloud auth list

# Re-authenticate if needed
gcloud auth application-default login
```