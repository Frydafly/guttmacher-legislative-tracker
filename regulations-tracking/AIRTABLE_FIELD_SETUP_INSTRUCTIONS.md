# Airtable Field Setup Instructions

## ⚠️ IMPORTANT: Fields Must Be Created BEFORE Import!

Airtable CSV imports will **NOT** create new fields automatically. You must manually add these fields to your Regulations table BEFORE importing the enhanced CSV.

## 🆕 New Fields to Add to Regulations Table

### 1. **Regulation Type** (REQUIRED)
- **Field Type**: Single Select
- **Options to add**:
  - Standard Rulemaking
  - Emergency Rule
  - Temporary Rule
  - Guidance/Bulletin
- **Location**: Add after "Year" field or near "Current Status"

### 2. **Expiration Date** (REQUIRED for emergency tracking)
- **Field Type**: Date
- **Format**: Same as other date fields (US format)
- **Location**: Add after "Effective Date" field
- **Purpose**: Tracks when emergency rules expire (auto-calculated as 180 days from emergency adoption)

### 3. **Intent (access)** (REQUIRED for policy analysis)
- **Field Type**: Single Select
- **Options to add**:
  - Protective
  - Restrictive
  - Neutral
  - Mixed
- **Location**: Add near other policy fields
- **Note**: Will be empty initially, needs manual review

### 4. **Supersedes** (OPTIONAL but valuable)
- **Field Type**: Link to another record (Regulations table)
- **Links to**: Same Regulations table (self-referential)
- **Purpose**: Links to older regulation this one replaces

### 5. **Superseded By** (OPTIONAL but valuable)
- **Field Type**: Link to another record (Regulations table)
- **Links to**: Same Regulations table (self-referential)
- **Purpose**: Links to newer regulation that replaces this one

## 📝 Step-by-Step Instructions

### Before Import:

1. **Open your Regulations table** in Airtable

2. **Add Regulation Type field**:
   - Click "+" to add field
   - Name: "Regulation Type"
   - Type: Single Select
   - Add options: Standard Rulemaking, Emergency Rule, Temporary Rule, Guidance/Bulletin
   - Click "Save"

3. **Add Expiration Date field**:
   - Click "+" to add field
   - Name: "Expiration Date"
   - Type: Date
   - Format: US (1/14/2025) or ISO (2025-01-14) - match your other dates
   - Click "Save"

4. **Add Intent (access) field**:
   - Click "+" to add field
   - Name: "Intent (access)"
   - Type: Single Select
   - Add options: Protective, Restrictive, Neutral, Mixed
   - Click "Save"

5. **Add Supersedes field** (optional):
   - Click "+" to add field
   - Name: "Supersedes"
   - Type: Link to another record
   - Link to: Regulations (same table)
   - Click "Save"

6. **Add Superseded By field** (optional):
   - Click "+" to add field
   - Name: "Superseded By"
   - Type: Link to another record
   - Link to: Regulations (same table)
   - Click "Save"

### During Import:

7. **Import the enhanced CSV**:
   - Use `regulations_enhanced_import.csv`
   - Choose "Update existing records" (match by Reg-ID)
   - Map fields carefully - new fields should now appear in mapping

### After Import:

8. **Verify the data**:
   - Check Regulation Type is populated (72 Standard, 13 Emergency, 11 Guidance)
   - Check Expiration Date is populated for Emergency Rules
   - Confirm Legal Status shows more variety (70 In Effect, 11 Expired, etc.)

9. **Manual tasks needed**:
   - Review and assign Intent (access) for each regulation
   - Research and link Related Bills where applicable
   - Identify and link Supersedes/Superseded By relationships

## 🔍 Field Mapping Reference

When importing, ensure these fields map correctly:

| CSV Column | Airtable Field | Notes |
|------------|---------------|-------|
| Regulation Type | Regulation Type | NEW - must create first |
| Expiration Date | Expiration Date | NEW - must create first |
| Intent (access) | Intent (access) | NEW - must create first |
| Supersedes | Supersedes | NEW - optional |
| Superseded By | Superseded By | NEW - optional |
| Legal Status | Legal Status | ENHANCED - more values |
| Issuing Agency Link | Issuing Agency Link | Should map to agency name |

## ⚡ Quick Check Before Import

- [ ] Created "Regulation Type" single select field
- [ ] Created "Expiration Date" date field
- [ ] Created "Intent (access)" single select field
- [ ] (Optional) Created "Supersedes" link field
- [ ] (Optional) Created "Superseded By" link field
- [ ] Have `regulations_enhanced_import.csv` ready
- [ ] Selected "Update existing records" in import settings

## 📊 What You'll Get

After successful import with new fields:
- **13 Emergency Rules** with calculated expiration dates
- **11 Expired regulations** properly identified
- **Enhanced legal status** showing In Effect, Expired, Pending, etc.
- **Regulation types** properly categorized
- **Ready for Intent assignment** by policy team

---

**File to Import**: `regulations_enhanced_import.csv`
**Records**: 96 regulations with enhanced data
**New Data Points**: Regulation Type, Expiration Dates, Enhanced Legal Status