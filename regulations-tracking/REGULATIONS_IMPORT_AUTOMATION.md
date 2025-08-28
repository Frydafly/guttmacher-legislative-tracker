# Regulations Import Automation Guide

**Purpose**: Build StateNet regulation import automation similar to the existing Bills import
**Status**: Implementation guide for Airtable automation scripts

## Overview

This automation imports new regulation data from StateNet CSV exports into the existing Regulations table, following the same pattern as the Bills import automation but adapted for regulation-specific data structures.

## Architecture

### Data Flow
```
StateNet CSV Export → Raw Import Table → Processing Script → Regulations Table
```

### Key Components
1. **StateNet Regulations Raw Import** - Staging table for CSV data
2. **Processing Automation** - Script to match, dedupe, and transform data  
3. **Regulations Table** - Final destination with all relationships

## StateNet Regulations Raw Import Table

Create a staging table with all CSV columns mapped directly:

### Core Fields (from StateNet CSV)
- **Measure Type** (Text) - Always "REGULATION"
- **Jurisdiction** (Text) - State abbreviation
- **Number** (Number) - Regulation number
- **Year** (Number) - Year issued
- **State ID** (Text) - StateNet unique identifier
- **Title** (Long Text) - Regulation title
- **Summary** (Long Text) - Description from StateNet
- **Author/Source** (Long Text) - Issuing agency
- **Links** (URL) - StateNet URL
- **Contact** (Long Text) - Agency contact info
- **Citation** (Text) - Legal citation

### Date Fields
- **Adopted Date** (Date)
- **Emergency Adopted Date** (Date) 
- **Effective Date** (Date)
- **Last Status Date** (Date)

### Policy Classification (Checkboxes from CSV)
- **Abortion** (Checkbox)
- **FamilyPlanning** (Checkbox)
- **Insurance** (Checkbox)
- **Minors** (Checkbox)
- **Pregnancy** (Checkbox)
- **Providers** (Checkbox)
- **[Additional policy categories as needed]**

### Import Tracking
- **Newly Tracked** (Checkbox)
- **Change in Status** (Checkbox)
- **Import Date** (Created Time)

## Processing Automation Script

### Trigger
- When records are created in "StateNet Regulations Raw Import" table

### Core Logic

```javascript
const CONFIG = {
    TABLES: {
        RAW_IMPORT: 'StateNet Regulations Raw Import',
        REGULATIONS: 'Regulations',
        AGENCIES: 'Agencies'
    },
    FIELDS: {
        // Field mapping configuration
        RAW_TO_REG: {
            'Title': 'Title',
            'Summary': 'Description', 
            'Author/Source': 'Issuing Agency',
            'Adopted Date': 'Adopted Date',
            'Effective Date': 'Effective Date',
            'Emergency Adopted Date': 'Emergency Adopted Date',
            'Last Status Date': 'Last Action',
            'Citation': 'Citation',
            'Contact': 'Contact',
            'Links': 'StateNet Link',
            'State ID': 'StateNet ID'
        }
    }
};

// Main processing function
async function processRegulationImport() {
    let rawTable = base.getTable(CONFIG.TABLES.RAW_IMPORT);
    let regulationsTable = base.getTable(CONFIG.TABLES.REGULATIONS);
    
    // Get unprocessed records
    let rawQuery = await rawTable.selectRecordsAsync();
    let unprocessed = rawQuery.records.filter(record => 
        !record.getCellValue('Processed')
    );
    
    for (let rawRecord of unprocessed) {
        await processRecord(rawRecord, regulationsTable);
        
        // Mark as processed
        await rawTable.updateRecordAsync(rawRecord.id, {
            'Processed': true
        });
    }
}

async function processRecord(rawRecord, regulationsTable) {
    // Generate primary key
    let jurisdiction = rawRecord.getCellValue('Jurisdiction');
    let number = rawRecord.getCellValue('Number');
    let year = rawRecord.getCellValue('Year');
    let regId = `${jurisdiction}-REG-${number}-${year}`;
    
    // Check for existing regulation
    let existingQuery = await regulationsTable.selectRecordsAsync({
        filterByFormula: `{Reg-ID} = "${regId}"`
    });
    
    // Transform data
    let mappedFields = mapFields(rawRecord);
    
    if (existingQuery.records.length > 0) {
        // Update existing regulation
        let existing = existingQuery.records[0];
        let shouldUpdate = shouldUpdateRecord(rawRecord, existing);
        
        if (shouldUpdate) {
            await regulationsTable.updateRecordAsync(existing.id, mappedFields);
            console.log(`Updated regulation: ${regId}`);
        }
    } else {
        // Create new regulation
        await regulationsTable.createRecordAsync(mappedFields);
        console.log(`Created regulation: ${regId}`);
    }
}

function mapFields(rawRecord) {
    let mapped = {};
    
    // Map basic fields
    for (let [rawField, regField] of Object.entries(CONFIG.FIELDS.RAW_TO_REG)) {
        let value = rawRecord.getCellValue(rawField);
        if (value) {
            mapped[regField] = value;
        }
    }
    
    // Map core identifiers
    mapped['State'] = rawRecord.getCellValue('Jurisdiction');
    mapped['Number'] = rawRecord.getCellValue('Number');
    mapped['Year'] = rawRecord.getCellValue('Year');
    
    // Determine Current Status
    mapped['Current Status'] = determineStatus(rawRecord);
    
    // Determine Regulation Type
    mapped['Regulation Type'] = determineRegulationType(rawRecord);
    
    // Map policy categories to text fields for later linking
    mapped['Specific Policies (access)'] = buildPolicyString(rawRecord);
    
    return mapped;
}

function determineStatus(rawRecord) {
    let emergencyDate = rawRecord.getCellValue('Emergency Adopted Date');
    let adoptedDate = rawRecord.getCellValue('Adopted Date');
    let effectiveDate = rawRecord.getCellValue('Effective Date');
    
    if (emergencyDate) {
        return 'Emergency Adopted';
    } else if (effectiveDate && new Date(effectiveDate) <= new Date()) {
        return 'Effective';
    } else if (adoptedDate) {
        return 'Adopted';
    } else {
        return 'Proposed';
    }
}

function determineRegulationType(rawRecord) {
    if (rawRecord.getCellValue('Emergency Adopted Date')) {
        return 'Emergency Rule';
    }
    // Default to standard rulemaking
    return 'Standard Rulemaking';
}

function buildPolicyString(rawRecord) {
    let policies = [];
    
    // Policy category mapping
    const policyFields = [
        'Abortion', 'FamilyPlanning', 'Insurance', 
        'Minors', 'Pregnancy', 'Providers'
    ];
    
    for (let field of policyFields) {
        if (rawRecord.getCellValue(field)) {
            policies.push(field);
        }
    }
    
    return policies.join(', ');
}

function shouldUpdateRecord(rawRecord, existing) {
    let newStatusDate = rawRecord.getCellValue('Last Status Date');
    let existingStatusDate = existing.getCellValue('Last Action');
    
    // Update if new status date is more recent
    if (newStatusDate && existingStatusDate) {
        return new Date(newStatusDate) > new Date(existingStatusDate);
    }
    
    // Update if we have a new status date and existing doesn't
    if (newStatusDate && !existingStatusDate) {
        return true;
    }
    
    // Check for "Change in Status" flag
    return rawRecord.getCellValue('Change in Status') === true;
}

// Run the import
processRegulationImport();
```

## Data Quality Checks

### Validation Rules
1. **Required Fields**: Title, State, Number, Year must be present
2. **Date Logic**: Effective Date >= Adopted Date (if both exist)  
3. **Emergency Rules**: Must have Emergency Adopted Date
4. **Contact Parsing**: Extract structured contact info
5. **Duplicate Detection**: Check Reg-ID uniqueness

### Error Handling
```javascript
function validateRecord(rawRecord) {
    let errors = [];
    
    if (!rawRecord.getCellValue('Title')) {
        errors.push('Missing title');
    }
    
    if (!rawRecord.getCellValue('Jurisdiction')) {
        errors.push('Missing jurisdiction'); 
    }
    
    if (!rawRecord.getCellValue('Number')) {
        errors.push('Missing regulation number');
    }
    
    // Date validation
    let adopted = rawRecord.getCellValue('Adopted Date');
    let effective = rawRecord.getCellValue('Effective Date');
    
    if (adopted && effective && new Date(effective) < new Date(adopted)) {
        errors.push('Effective date before adopted date');
    }
    
    return errors;
}
```

## Key Differences from Bills Import

### Regulation-Specific Logic
1. **No Legislative Process** - No committee dates, floor votes, etc.
2. **Agency Focus** - Issuing agency instead of sponsors/authors
3. **Emergency Rules** - Handle immediate effect and expiration dates
4. **Citation Format** - Parse regulatory citations (CFR, CCR, etc.)
5. **Status Determination** - Based on adoption/effective dates vs. legislative workflow

### Emergency Regulation Handling
```javascript
function calculateExpirationDate(emergencyDate) {
    // Most emergency rules expire in 180 days
    let expiration = new Date(emergencyDate);
    expiration.setDate(expiration.getDate() + 180);
    return expiration;
}

function handleEmergencyRule(rawRecord, mappedFields) {
    let emergencyDate = rawRecord.getCellValue('Emergency Adopted Date');
    
    if (emergencyDate) {
        mappedFields['Regulation Type'] = 'Emergency Rule';
        mappedFields['Expiration Date'] = calculateExpirationDate(emergencyDate);
        mappedFields['Current Status'] = 'Emergency Adopted';
    }
}
```

## Implementation Steps

### Phase 1: Setup
1. Create "StateNet Regulations Raw Import" table with all CSV fields
2. Add "Processed" checkbox field for tracking  
3. Test CSV import with sample data

### Phase 2: Automation Script
1. Create automation triggered on record creation
2. Implement core processing logic with error handling
3. Test with small batch of records

### Phase 3: Integration
1. Connect to existing Regulations table
2. Test field mapping and data transformation
3. Validate policy category linking

### Phase 4: Production
1. Schedule regular imports (weekly like Bills)
2. Set up monitoring and error alerts
3. Document operational procedures

## Operational Considerations

### Import Frequency
- **Weekly imports** - Same schedule as Bills import
- **Manual trigger** - For ad-hoc regulatory updates
- **Bulk processing** - Handle large CSV exports efficiently

### Monitoring
- **Import success rates** - Track processed vs. failed records
- **Data quality metrics** - Monitor validation errors
- **Status change tracking** - Alert on significant regulation updates

### Maintenance  
- **Field mapping updates** - When StateNet changes CSV format
- **Policy category expansion** - Add new regulation topics
- **Agency relationship management** - Keep agency linking current

## Testing Strategy

### Sample Data Testing
1. Use existing "2025 tracked regs.csv" as test data
2. Verify all 96 regulations process correctly  
3. Check field mapping accuracy
4. Validate policy category assignment

### Edge Case Testing
- Regulations without adoption dates
- Emergency rules with custom expiration
- Agency name variations and matching
- Policy categories with multiple values

---

**Next Steps**: 
1. Create the Raw Import table structure
2. Build the processing automation script  
3. Test with current regulation data
4. Deploy and schedule regular imports