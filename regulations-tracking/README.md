# Regulations Tracking

This folder contains the implementation files for adding regulations tracking to the Guttmacher Legislative Tracker system.

## Key Files

### Data Files (Ready for Import)
- **`regulations_airtable_import.csv`** ✅ - 96 regulations ready for Airtable import
- **`agencies_complete.csv`** ✅ - 62 agencies with full categorization
- **`2025 tracked regs.csv`** - Original source data from StateNet

### Documentation
- **`REGULATIONS_TRACKING_PROPOSAL.md`** - Complete proposal with database structure
- **`IMPLEMENTATION_CHECKLIST.md`** - Step-by-step implementation guide

### Scripts
- **`transform_final_import.py`** - Transforms raw CSV to exact Airtable format

## Database Structure

We're creating three new tables in the existing Bills Airtable base:

1. **Regulations** - Main table mirroring Bills structure with regulation-specific fields
2. **Agencies** - Lookup table for agency hierarchy and categorization  
3. **StateNet Regulations Import** - Staging table for raw imports

## Key Design Decisions

- **Same base as Bills** - Enables cross-referencing and unified reporting
- **Linked records instead of checkboxes** - Proper relational structure matching Bills
- **Agency hierarchy** - Separate table for managing agency relationships
- **Formula-generated RegID** - `CONCATENATE(State,"-REG-",Number,"-",Year)`

## Import Process

1. Import `agencies_table.csv` to create Agencies table
2. Import `regulations_full_import.csv` to Regulations table
3. Set up RegID formula field
4. Link agencies and policy categories
5. Configure automation for ongoing imports

## What's Ready vs What Needs Answers

See `IMPLEMENTATION_CHECKLIST.md` for detailed breakdown of:
- 🟢 What we can implement now
- 🔴 Critical questions needing answers
- 🟡 Nice-to-have clarifications