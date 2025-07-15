# BigQuery User Guide for Non-Technical Users

This guide helps team members access and explore the Guttmacher legislative data in BigQuery without needing SQL knowledge.

## Getting Started

### 1. Accessing BigQuery
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Sign in with your Google account (ask IT for access if needed)
3. Select the project: **guttmacher-legislative-tracker**
4. Click on "BigQuery" from the left menu (or search for it)

### 2. Finding Our Data
Once in BigQuery, you'll see a sidebar on the left:
1. Look for **guttmacher-legislative-tracker** project
2. Expand it to see **legislative_tracker_historical** dataset
3. You'll see 30+ tables - these contain all our legislative data!

## Key Tables to Know

### ⭐ **Start Here** (Recommended):
- **`comprehensive_bills_authentic`** - Main dashboard view with all enhancements
- **`tracking_completeness_matrix`** - Shows what data is available by year (✅/⚠️/❌)

### For Detailed Research:
- **`all_historical_bills_unified`** - Every bill from 2002-2023 (20,221 bills)
- **`realistic_field_tracking_by_year`** - Understanding data availability evolution

### Individual Years:
- **`historical_bills_2002`** through **`historical_bills_2022`** - One table per year

## Exploring Data Without SQL

### Method 1: Preview Tables
1. Click on any table name in the left sidebar
2. Click the **"Preview"** tab to see sample data
3. Use the pagination at the bottom to browse through records

### Method 2: Use the Query Builder (Visual Interface)
1. Click on a table name
2. Click **"Query"** button
3. BigQuery will show a visual interface where you can:
   - Select which columns to show
   - Add filters (like "only show bills from Texas")
   - Sort the results

### Method 3: Export to Google Sheets
1. Click on a table
2. Click **"Export"**
3. Choose **"Export to Sheets"**
4. Analyze the data in Google Sheets with filters, pivot tables, etc.

## Understanding the Data

### Key Fields in Every Table:

**Basic Information:**
- `state` - Which state (always present)
- `bill_number` - The bill's official number
- `bill_type` - Type of legislation (bill, resolution, etc.)
- `description` - What the bill is about

**Dates:**
- `introduced_date` - When introduced (available 2016+)
- `last_action_date` - Most recent action
- `enacted_date` - When signed into law (if applicable)

**Status (TRUE/FALSE for each):**
- `introduced` - Bill was introduced
- `enacted` - Bill became law
- `vetoed` - Bill was vetoed
- `dead` - Bill failed/died
- `pending` - Bill is still active

**Policy Categories (TRUE/FALSE/NULL):**
- `abortion` - Relates to abortion
- `contraception` - Relates to contraception/birth control
- `minors` - Relates to minors/teen issues
- `sex_education` - Relates to sex education
- `insurance` - Relates to insurance coverage
- Plus many more specific categories

**Intent (TRUE/FALSE/NULL):**
- `positive` - Pro-reproductive rights
- `neutral` - Neutral impact
- `restrictive` - Restricts reproductive rights

### Data Notes:
- **NULL** means "not applicable" or "not tracked for this bill"
- **FALSE** means "definitely not" (for status fields)
- **TRUE** means "yes, this applies"

## Common Questions You Can Answer

### Without Writing SQL:

1. **"How many bills were introduced in Texas in 2022?"**
   - Open `historical_bills_2022`
   - Preview the data
   - Export to Sheets and filter by state = "TX"

2. **"What abortion-related bills were enacted last year?"**
   - Open `historical_bills_2022`
   - Export to Sheets
   - Filter: `abortion` = TRUE AND `enacted` = TRUE

3. **"Which states had the most reproductive health bills?"**
   - Open `looker_state_summary`
   - Preview to see state-by-state totals

### Using Simple Query Builder:
1. Click on `looker_bills_dashboard`
2. Click "Query"
3. Select columns you want to see
4. Add filters like:
   - `state` equals "CA"
   - `enacted` equals "true"
   - `data_year` equals "2022"

## Connecting to Looker Studio (Recommended)

For the best non-technical experience:
1. Go to [lookerstudio.google.com](https://lookerstudio.google.com)
2. Create a new report
3. Add BigQuery as a data source
4. Select our project: **guttmacher-legislative-tracker**
5. Choose **legislative_tracker_historical** dataset
6. Pick one of the `looker_*` tables

Looker Studio provides:
- Drag-and-drop charts and graphs
- Interactive filters
- Easy sharing with team members
- No SQL required!

## Getting Help

### If You're Stuck:
1. **Preview tables first** - This shows you what data looks like
2. **Start with `looker_bills_dashboard`** - It's designed to be user-friendly
3. **Export small samples to Sheets** - Easier to explore familiar tools
4. **Ask a technical team member** - They can write custom queries for you

### Common Beginner Mistakes:
- Don't try to preview `all_historical_bills_unified` - it's huge! Start with yearly tables
- Remember that NULL ≠ FALSE in our data
- Some fields (like `introduced_date`) are only available in recent years

### Sample Questions to Try:
- "Show me all enacted bills from my state"
- "What types of bills were most common in 2020?"
- "Which states had the most vetoed reproductive health bills?"

## Data Coverage

**What we have:**
- 18 years of data (2002-2022, missing 2014, 2015, 2024)
- 16,323 bills total
- All 50 states
- Consistent policy categories across all years
- Legislative status tracking for every bill

**What's most reliable:**
- State, bill numbers, policy categories: 99-100% complete
- Legislative status: 100% complete
- Recent bills (2016+): Nearly complete for all fields
- Early bills (2002-2010): Complete for core data, limited date information

## Need More Advanced Analysis?

If you need complex analysis that requires SQL:
1. Contact a technical team member
2. Provide clear questions in plain English
3. They can create custom views or reports for you
4. Consider setting up recurring reports in Looker Studio

Remember: You don't need to be technical to explore this data! Start simple and gradually work up to more complex analysis.