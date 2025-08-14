# Regulations Tracking

This folder contains the planning and data for implementing regulations tracking in the Guttmacher Legislative Tracker system.

## Contents

- **`2025 tracked regs.csv`** - Current CSV file with 96 regulations being tracked across 29 states
- **`REGULATIONS_PROPOSAL_ENRICHED.md`** - Updated proposal document incorporating feedback from Candace Gibson
- **`Regulations Tracking Proposal.docx`** - Original proposal document with comments

## Quick Summary

We're adding regulations tracking to complement the existing bills tracking system. The implementation will:
- Track state regulations only (not federal or local)
- Focus on priority agencies: Health Departments, Medicaid, Medical/Pharmacist Licensing Boards, Insurance Commissioners
- Use a similar structure to the Bills table with regulation-specific additions
- Import the 96 regulations from the CSV as starting data

## Next Steps

1. Create new Airtable tables (Regulations and StateNet Regulations Import)
2. Import initial data from CSV
3. Build automation scripts following the bills import pattern
4. Train team on regulation-specific workflows

See `REGULATIONS_PROPOSAL_ENRICHED.md` for full implementation details.