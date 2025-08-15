# Final Import Steps for Regulations

**File to Import**: `regulations_IMPORT_READY.csv`

## 🎯 The Linked Field Problem & Solution

**Problem**: Airtable won't import text directly into linked fields
**Solution**: Import to text fields first, then convert to links

## Step 1: Create These Fields in Airtable

### New Fields to Add:
1. **Regulation Type** (Single Select)
   - Options: Standard Rulemaking, Emergency Rule, Temporary Rule, Guidance/Bulletin

2. **Expiration Date** (Date field)

3. **Superseded By** (Link to Regulations)
   - Rename the auto-created reverse field to "Supersedes"

### Temporary Text Fields for Import:
4. **Agency Name (for linking)** (Single Line Text or Long Text)
   - This will receive the agency names during import
   - After import, you'll copy this to the actual link field

## Step 2: Import the CSV

1. Import `regulations_IMPORT_READY.csv`
2. Choose "Update existing records"
3. Match by: `Reg-ID`
4. Map these fields:
   - **Agency Name (for linking)** → Maps to agency name text
   - All other fields map normally

## Step 3: Convert Text to Links

After import completes:

### For Agency Links:
1. View your table with all records
2. Select all cells in "Agency Name (for linking)" column
3. Copy (Ctrl/Cmd + C)
4. Click into "Issuing Agency Link" field
5. Paste (Ctrl/Cmd + V)
6. Airtable will match text to Agency records and create links
7. Once verified, hide or delete "Agency Name (for linking)" field

### For Policy Links:
1. Use "Specific Policies (access)" field as your guide
2. Manually link each regulation to appropriate Policy Categories records
3. Intent will auto-populate from these links

## Step 4: Verify Import

Check that you have:
- ✅ 96 total records
- ✅ 72 Standard Rulemaking
- ✅ 13 Emergency Rules with expiration dates
- ✅ 11 Guidance/Bulletins
- ✅ All agencies linked (lookup fields should populate)
- ✅ Enhanced Legal Status showing variety (not just "In Effect")

## 📊 What You'll See After Import

### Automatically Populated:
- Regulation Type for all records
- Expiration Dates for emergency rules
- Enhanced Legal Status (70 In Effect, 11 Expired, etc.)
- All specific policies in text field
- Agency names in text field ready for linking

### Manual Linking Required:
- Agency text → Agency links (copy/paste method)
- Specific Policies → Policy Categories links
- Superseded By relationships (when identified)

## 💡 Pro Tips

1. **Test First**: Try with 5-10 records before full import

2. **Bulk Link Agencies**: 
   - Sort by "Agency Name (for linking)"
   - Select all matching agencies at once
   - Link them together to save time

3. **Create a View**: 
   - Filter to show records where "Issuing Agency Link" is empty
   - Work through them systematically

4. **Keep Text Field Temporarily**:
   - Don't delete "Agency Name (for linking)" until all links are verified
   - Useful for troubleshooting non-matching names

## ⚠️ Common Issues

**Agency names don't match**:
- Check for exact spelling in Agencies table
- May need to standardize names (e.g., "Dept" vs "Department")

**Some agencies won't link**:
- Ensure agency exists in Agencies table first
- Check for extra spaces or special characters

## 🎉 Final Result

After these steps, you'll have:
- All regulations with proper field types
- Agencies linked (with lookups working)
- Regulation types categorized
- Emergency rules with expiration tracking
- Ready for policy linking and analysis

---

**Remember**: The two-step process (import as text, then convert to links) is the reliable way to handle linked fields in Airtable!