# How to Export Airtable Schema

Step-by-step guide to get your Airtable base structure for documentation verification.

## Method 1: Field Customization Panel (Easiest!)

This is the simplest way to see all your fields without any exports.

### For Each Table:

**Step 1: Open the table** (e.g., Bills)

**Step 2: Click any field header** with a dropdown arrow

**Step 3: Select "Customize field type"**

**Step 4: You'll see a panel** showing:
- Field name
- Field type (Formula, Single select, Date, etc.)
- Configuration details

**Step 5: Take screenshots** or write down:
```
Table: Bills
- BillID (Formula)
- State (Single select)
- BillType (Single select)
- BillNumber (Number)
- Description (Long text)
- Current Bill Status (Formula)
- etc...
```

**Step 6: Repeat** for each main table:
- Bills
- StateNet Raw Import
- Website Exports
- Policy Categories
- System Monitor

---

## Method 2: Base Schema (Hidden Feature)

**Step 1: Open your base**

**Step 2: Click the base name** in the top left corner

**Step 3: Look for one of these options**:
- "Base schema"
- "Print base"
- "Download base"
- "API documentation"

**Note**: This option may not be available on all Airtable plans.

If you see **"API documentation"**:
- Click it
- It will show you all tables and fields
- Has a "Show API key" option you can ignore
- Scroll through to see field types

---

## Method 3: Just Tell Me What You Have

Don't want to export anything? Just answer these questions:

### Main Tables

Do you have these tables?
- ✅ Bills
- ✅ StateNet Raw Import
- ✅ Website Exports
- ✅ Policy Categories
- ✅ System Monitor

Any others?

### Bills Table Fields

**Identification fields** - Check which you have:
- [ ] BillID (Formula? or Text?)
- [ ] State (Single select? or Text?)
- [ ] BillType (Single select? or Text?)
- [ ] BillNumber (Number? or Text?)

**Content fields** - Check which you have:
- [ ] Description (Long text?)
- [ ] Website Blurb (Long text?)
- [ ] Internal Notes (Long text?)
- [ ] History (Long text?)
- [ ] StateNet History (Long text?)

**Date fields** - Check which you have:
- [ ] Introduction Date (Date? or Formula?)
- [ ] Last Action (Date? or Formula?)
- [ ] Enacted Date (Date? or Formula?)
- [ ] Effective Date (Date?)

**Status/Classification** - Check which you have:
- [ ] Current Bill Status (Formula? or Single select?)
- [ ] Review Status (Single select?)
- [ ] Intent (Single select? or Multi-select?)
- [ ] Action Type (Single select?)

**Policy fields** - Check which you have:
- [ ] Specific Policies (Linked records?)
- [ ] Policy Categories (Lookup? or Text?)

**System fields** - Check which you have:
- [ ] Import Date (Created time?)
- [ ] Last Updated (Last modified time?)
- [ ] Imported By (Created by?)
- [ ] Last Updated By (Last modified by?)

---

## Method 4: Simple CSV Export

This won't show field types, but helps verify field names:

**Step 1: Open Bills table**

**Step 2: Click "..." menu** (next to Views)

**Step 3: Select "Download CSV"**

**Step 4: Open in Excel/Numbers**
- First row shows all field names
- Share just that first row!

---

## What I Need

Just need to know:

### 1. Field Names
Are these correct?
- `BillID` or `Bill ID`?
- `Current Bill Status` or `Status`?
- `Specific Policies` or something else?

### 2. Formula Fields
Which fields are formulas?
- BillID
- Current Bill Status
- Introduction Date
- Last Action Date
- Enacted Date

### 3. Key Relationships
- Does `Specific Policies` link to `Policy Categories` table?
- Does `StateNet Raw Import` link to `Bills` table?

### 4. Anything Missing
- New fields you added recently?
- Fields we documented that don't exist?

---

## Quick Way: Just Answer These

**Q1**: Is `BillID` a **formula field** that combines State-BillType-BillNumber?
- [ ] Yes
- [ ] No, it's entered manually
- [ ] No, it's something else

**Q2**: Is `Current Bill Status` a **formula field** that extracts from History?
- [ ] Yes
- [ ] No, it's selected manually
- [ ] No, it's something else

**Q3**: Does `Specific Policies` **link to** the Policy Categories table?
- [ ] Yes
- [ ] No, it's multi-select dropdown
- [ ] No, it's something else

**Q4**: Do you have these tables?
- [ ] Bills
- [ ] StateNet Raw Import
- [ ] Website Exports
- [ ] Policy Categories
- [ ] System Monitor

Answer just those 4 questions and we're 90% there!

---

## Why This Matters

Making sure docs match your actual Airtable means:
- ✅ Correct field names in scripts
- ✅ Accurate user guides
- ✅ Proper troubleshooting steps
- ✅ No confusion for new team members

**Take your time** - any method above works fine!
