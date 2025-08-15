# Final Import Instructions for Regulations

**File to Import**: `regulations_final_best.csv`

## ✅ Pre-Import Checklist

### Fields to Create in Airtable FIRST:

1. **Regulation Type** (Single Select)
   - Options: Standard Rulemaking, Emergency Rule, Temporary Rule, Guidance/Bulletin

2. **Expiration Date** (Date field)

3. **Superseded By** (Link to another record - Regulations)
   - Links to: The newer regulation that replaces this one
   - This automatically creates a reverse field
   - **Rename the reverse field to**: "Supersedes" 
   - The reverse field will show which older regulations are replaced by this one
   
   **Why just one field?**
   - Creating "Superseded By" automatically gives you both directions
   - Forward: "This reg is superseded by..." (the new one)
   - Reverse: "This reg supersedes..." (the old ones)
   - Much simpler than managing two separate link fields!

## 📥 Import Process

### Step 1: Initial Import
1. Import `regulations_final_best.csv`
2. Choose "Update existing records" 
3. Match by: `Reg-ID`
4. Map these fields:
   - **Issuing Agency Link** → Import as TEXT (not as link)
   - This will contain the agency names as text

### Step 2: Convert Agency Text to Links
After import, you need to manually convert the agency text to links:

1. **Method A - Copy/Paste**:
   - Select all cells in "Issuing Agency Link" column
   - Copy (Cmd+C)
   - Click into the actual link field
   - Paste (Cmd+V)
   - Airtable will attempt to match the text to Agency records

2. **Method B - Drag and Drop**:
   - Filter to show a manageable number of records
   - Select cells and drag to the link field
   - Airtable will create the links

3. **Method C - Automation** (if available):
   - Create an automation that runs after import
   - When "Issuing Agency Link" contains text
   - Find matching Agency record
   - Link the records

### Step 3: Verify Links
- Check that all 96 regulations have linked agencies
- The lookup fields should populate:
  - Agency Type (from Issuing Agency Link)
  - Priority Level (from Issuing Agency Link)
  - Parent Agency (from Issuing Agency Link)

## 🔄 Fields That Will Need Manual Linking

### After Import, These Fields Need Manual Work:

1. **Specific Policies Record Link**
   - Use "Specific Policies (access)" as your guide
   - Link to the appropriate Policy Categories records
   - Intent will auto-populate from these links

2. **Related Bills** (when known)
   - Link to Bills table for enabling legislation

3. **Supersedes/Superseded By** (when identified)
   - Link to other Regulations records

## 📊 What You'll Have After Import

### Automatically Populated:
- ✅ All 96 regulations with complete data
- ✅ Regulation Type for all records (72 Standard, 13 Emergency, 11 Guidance)
- ✅ Expiration Dates for emergency rules
- ✅ Enhanced Legal Status (70 In Effect, 11 Expired, etc.)
- ✅ All specific policies in "Specific Policies (access)" field
- ✅ Agency names in text field ready for linking

### Needs Manual Linking:
- 🔗 Agency text → Agency links (copy/paste or drag)
- 🔗 Policy text → Policy Category links
- 🔗 Bills relationships (when researched)
- 🔗 Supersedes relationships (when identified)

## 💡 Pro Tips

1. **Test First**: Import 5-10 records first to verify mapping

2. **Agency Linking Shortcut**: 
   - Sort by "Issuing Agency Link" to group same agencies
   - Link all records from same agency at once

3. **Policy Linking Helper**:
   - Create a temporary view grouped by "Specific Policies (access)"
   - Link all records with same policies together

4. **Use Bulk Operations**:
   - Select multiple cells with same value
   - Link them all at once to save time

## ⚠️ Common Issues

### Issue: Agency names don't match
**Solution**: Ensure agencies_complete.csv was imported first and names match exactly

### Issue: Can't link to policies
**Solution**: Policy Categories table must have records matching the policy names

### Issue: Dates import as text
**Solution**: Ensure date fields are set to Date type before import

## 📝 Post-Import Tasks

1. **Convert agency text to links** (Priority 1)
2. **Link to Policy Categories** (Priority 2)
3. **Set up views for**:
   - Emergency rules nearing expiration
   - Regulations missing policy links
   - Expired regulations
4. **Create automations** from AIRTABLE_FORMULAS_AUTOMATIONS.md

---

**Remember**: The import gives you all the data, but linking records must be done within Airtable!