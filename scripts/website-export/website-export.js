// Guttmacher Policy Tracker: Website Export Script
// Purpose: Creates a clean export of ALL bills

// Configuration object for field mapping
const CONFIG = {
    // Source fields from Bills table
    FIELDS: {
        BILL_ID: 'BillID',
        STATE: 'State',
        BILL_TYPE: 'BillType',
        BILL_NUMBER: 'BillNumber',
        LAST_ACTION: 'Last Action',
        INTENT: 'Intent (access)',
        SPECIFIC_POLICIES_ACCESS: 'Specific Policies (access)',
        WEBSITE_BLURB: 'Website Blurb',
        INTRODUCED_DATE: 'Introduction Date',
        PASSED1_CHAMBER_DATE: 'Passed 1 Chamber Date',
        PASSED_LEGISLATURE_DATE: 'Passed Legislature Date',
        VETOED_DATE: 'Vetoed Date',
        ENACTED_DATE: 'Enacted Date',
        ACTION_TYPE: 'Action Type',
        DATE_VALIDATION: 'Date Validation' // Added Date Validation field
    },
    
    // Subpolicies that are no longer supported by the website team
    UNSUPPORTED_SUBPOLICIES: [
        "AB Misc Neutral",
        "AB Ban Partial-Birth Abortion",
        "CPC Misc Restrictive",
        "FP Funding Restricted Other",
        "FP Right to Contraception",
        "INS Misc Positive",
        "Pregnancy HIV Test for Preg Women",
        "Parental Leave",
        "Repeals Ban All or Most AB Ban",
        "Repeals Counsel Perinatal Hospice Info",
        "Sex Ed Misc Neutral",
        "Sex Ed Misc Positive",
        "Sex Ed Misc Restrictive",
        "STI Misc Positive",
        "STI Misc Restrictive",
        "Sed Ed STI Neutral",
        "Repeals Ban on D and E Method"
    ]
};

/**
 * Checks if a record has date validation issues
 * Uses the Date Validation field to detect any future dates
 */
function checkDateValidation(record) {
    // Get the Date Validation field value
    const dateValidation = record.getCellValue(CONFIG.FIELDS.DATE_VALIDATION);
    
    // If the field contains any text, there are validation issues
    if (dateValidation && dateValidation.trim() !== '') {
        return {
            valid: false,
            message: dateValidation
        };
    }
    
    // No validation issues found
    return {
        valid: true,
        message: null
    };
}

/**
 * Transforms a bill record into the website export format
 */
async function transformRecord(record) {
    try {
        // Extract core bill information
        const state = record.getCellValue(CONFIG.FIELDS.STATE)?.name || '';
        const billType = record.getCellValue(CONFIG.FIELDS.BILL_TYPE)?.name || '';
        const billNumber = String(record.getCellValue(CONFIG.FIELDS.BILL_NUMBER) || '');
        
        // Sanitize website blurb to remove problematic newlines and other characters
        // that might interfere with CSV import
        let websiteBlurb = record.getCellValue(CONFIG.FIELDS.WEBSITE_BLURB) || '';
        // Replace all newlines, carriage returns, and tabs with spaces
        websiteBlurb = websiteBlurb.replace(/[\r\n\t]+/g, ' ');
        // Normalize multiple spaces to single spaces
        websiteBlurb = websiteBlurb.replace(/\s+/g, ' ').trim();
        
        // Format date function to ensure YYYY-MM-DD format
        const formatDate = (dateValue) => {
            if (!dateValue) {
              return null;
            }
            
            if (dateValue instanceof Date) {
                const year = dateValue.getFullYear();
                const month = String(dateValue.getMonth() + 1).padStart(2, '0');
                const day = String(dateValue.getDate()).padStart(2, '0');
                return `${year}-${month}-${day}`;
            }
            
            if (typeof dateValue === 'string') {
                const parsedDate = new Date(dateValue);
                if (!isNaN(parsedDate.getTime())) {
                    const year = parsedDate.getFullYear();
                    const month = String(parsedDate.getMonth() + 1).padStart(2, '0');
                    const day = String(parsedDate.getDate()).padStart(2, '0');
                    return `${year}-${month}-${day}`;
                }
                return dateValue;
            }
            
            return String(dateValue);
        };
        
        // Extract and format dates
        const lastActionDate = formatDate(record.getCellValue(CONFIG.FIELDS.LAST_ACTION));
        const introducedDate = formatDate(record.getCellValue(CONFIG.FIELDS.INTRODUCED_DATE));
        const passed1ChamberDate = formatDate(record.getCellValue(CONFIG.FIELDS.PASSED1_CHAMBER_DATE));
        const passedLegislatureDate = formatDate(record.getCellValue(CONFIG.FIELDS.PASSED_LEGISLATURE_DATE));
        const vetoedDate = formatDate(record.getCellValue(CONFIG.FIELDS.VETOED_DATE));
        const enactedDate = formatDate(record.getCellValue(CONFIG.FIELDS.ENACTED_DATE));

        // Derive boolean status from date fields - ensure they're "0" or "1" strings
        const vetoedStatus = vetoedDate ? '1' : '0';
        const enactedStatus = enactedDate ? '1' : '0';
        const passed2ChamberStatus = passedLegislatureDate ? '1' : '0';

        // Process intent flags
        const intent = record.getCellValue(CONFIG.FIELDS.INTENT) || [];
        const intentArray = Array.isArray(intent) ? intent.map(i => i.name) : [];
        
        // Determine if bill is a ballot initiative or court case
        const actionType = record.getCellValue(CONFIG.FIELDS.ACTION_TYPE) || [];
        const actionTypeArray = Array.isArray(actionType) 
            ? actionType.map(i => i.name) 
            : typeof actionType === 'string' 
                ? actionType.split(',').map(i => i.trim()) 
                : [];
        
        const ballotInitiative = actionTypeArray.includes('Ballot Initiative') ? '1' : '0';
        const courtCase = actionTypeArray.includes('Court Case') ? '1' : '0';

        // Get subpolicies with proper sanitization and filter out unsupported ones
        const specificPoliciesResult = getSpecificPolicies(record.getCellValue(CONFIG.FIELDS.SPECIFIC_POLICIES_ACCESS));
        
        // Track unsupported subpolicies for reporting
        if (specificPoliciesResult.unsupportedFound && specificPoliciesResult.unsupportedFound.length > 0) {
            // Store for later reporting
            record.unsupportedSubpolicies = specificPoliciesResult.unsupportedFound;
        }
        
        // Create an array of exactly 10 subpolicies (padding with empty strings if needed)
        const subpolicies = specificPoliciesResult.policies.slice(0, 10);
        while (subpolicies.length < 10) {
            subpolicies.push('');
        }

        // Return the transformed record - ensure field names match exactly what's expected
        return {
            State: state,
            BillType: billType,
            BillNumber: billNumber,
            "Ballot Initiative": ballotInitiative,
            "Court Case": courtCase,
            Subpolicy1: subpolicies[0],
            Subpolicy2: subpolicies[1],
            Subpolicy3: subpolicies[2],
            Subpolicy4: subpolicies[3],
            Subpolicy5: subpolicies[4],
            Subpolicy6: subpolicies[5],
            Subpolicy7: subpolicies[6],
            Subpolicy8: subpolicies[7],
            Subpolicy9: subpolicies[8],
            Subpolicy10: subpolicies[9],
            WebsiteBlurb: websiteBlurb,
            "Last Action Date": lastActionDate,
            IntroducedDate: introducedDate,
            Passed1ChamberDate: passed1ChamberDate,
            "Passed 2 Chamber": passed2ChamberStatus,
            PassedLegislature: passedLegislatureDate, 
            VetoedDate: vetoedDate,
            Vetoed: vetoedStatus,
            EnactedDate: enactedDate,
            Enacted: enactedStatus,
            Positive: intentArray.includes('Protective') ? '1' : '0',
            Neutral: intentArray.includes('Neutral') ? '1' : '0',
            Restrictive: intentArray.includes('Restrictive') ? '1' : '0'
        };
    } catch (error) {
        throw new Error(`Transformation error: ${error.message}`);
    }
}

/**
 * Extracts specific policy values from policy field with proper sanitization
 * and filters out unsupported subpolicies
 */
function getSpecificPolicies(policyField) {
    if (!policyField) {
      return { policies: [], unsupportedFound: [] };
    }
    
    const cleanPolicyString = (str) => {
        if (typeof str !== 'string') {
          return str;
        }
        // Remove any newlines, tabs, or multiple spaces
        return str.replace(/[\r\n\t]+/g, ' ').replace(/\s+/g, ' ').trim();
    };
    
    let policies = [];
    
    if (Array.isArray(policyField)) {
        policies = policyField.map(p => {
            const name = p.name || p;
            return cleanPolicyString(name);
        });
    } else if (typeof policyField === 'string') {
        policies = policyField
            .split(',')
            .map(p => cleanPolicyString(p))
            .filter(p => p);
    }
    
    // Filter out unsupported subpolicies
    const unsupported = [];
    const filtered = policies.filter(policy => {
        if (CONFIG.UNSUPPORTED_SUBPOLICIES.includes(policy)) {
            unsupported.push(policy);
            return false;
        }
        return true;
    });
    
    // Return both the filtered policies and any that were removed
    return {
        policies: filtered,
        unsupportedFound: unsupported
    };
}

/**
 * Validates that a record has all required fields
 */
function validateRecord(record) {
    const missingFields = [];
    
    // Check required fields - WebsiteBlurb is NOT required
    const requiredFields = ['STATE', 'BILL_TYPE', 'BILL_NUMBER'];
    requiredFields.forEach(field => {
        if (!record.getCellValue(CONFIG.FIELDS[field])) {
            missingFields.push(CONFIG.FIELDS[field]);
        }
    });
    
    return {
        valid: missingFields.length === 0,
        missingFields: missingFields
    };
}

/**
 * Generates a summary of the export process
 */
function generateSummary(records, errors, dateValidationErrors) {
    const summary = [`**Website Export Summary**\n`];
    
    // Record count statistics
    summary.push(`📊 **Statistics**`);
    summary.push(`- Total records processed: ${records.length + errors.length}`);
    summary.push(`- Successfully exported: ${records.length}`);
    summary.push(`- Errors encountered: ${errors.length}`);
    
    // Count records missing website blurb
    const missingBlurb = records.filter(r => !r.fields.WebsiteBlurb || r.fields.WebsiteBlurb.trim() === '').length;
    summary.push(`- Records with empty Website Blurb: ${missingBlurb} (${Math.round((missingBlurb/records.length)*100)}%)\n`);

    // Intent breakdown statistics
    if (records.length > 0) {
        const intentStats = {
            Positive: 0,
            Neutral: 0,
            Restrictive: 0
        };

        records.forEach(record => {
            if (record.fields.Positive === '1') {
              intentStats.Positive++;
            }
            if (record.fields.Neutral === '1') {
              intentStats.Neutral++;
            }
            if (record.fields.Restrictive === '1') {
              intentStats.Restrictive++;
            }
        });

        summary.push(`📑 **Intent Breakdown**`);
        Object.entries(intentStats)
            .sort(([, a], [, b]) => b - a)
            .forEach(([intent, count]) => {
                if (count > 0) {
                    summary.push(`- ${intent}: ${count}`);
                }
            });
        summary.push('');
    }

    // State breakdown statistics
    if (records.length > 0) {
        const stateStats = {};
        records.forEach(record => {
            const state = record.fields.State;
            stateStats[state] = (stateStats[state] || 0) + 1;
        });

        if (Object.keys(stateStats).length > 0) {
            summary.push(`🌎 **State Breakdown**`);
            Object.entries(stateStats)
                .sort(([, a], [, b]) => b - a)
                .forEach(([state, count]) => {
                    summary.push(`- ${state}: ${count}`);
                });
            summary.push('');
        }
    }

    // Date validation errors section
    if (dateValidationErrors && dateValidationErrors.length > 0) {
        summary.push(`⏰ **Date Validation Issues**`);
        summary.push(`${dateValidationErrors.length} bills were skipped due to future dates:\n`);
        
        // Show the first 10 examples
        const maxToShow = Math.min(10, dateValidationErrors.length);
        for (let i = 0; i < maxToShow; i++) {
            summary.push(`- ${dateValidationErrors[i].bill}: ${dateValidationErrors[i].error}`);
        }
        
        if (dateValidationErrors.length > maxToShow) {
            summary.push(`... and ${dateValidationErrors.length - maxToShow} more`);
        }
        summary.push('');
    }

    // General error details section
    if (errors.length > 0) {
        summary.push(`⚠️ **Errors**`);
        errors.forEach(({bill, error}) => {
            summary.push(`- Bill ${bill}: ${error}`);
        });
    }

    return summary.join('\n');
}

/**
 * Checks for duplicate records in the export
 */
function checkForDuplicates(exportRecords) {
    const seenBills = new Map();
    const duplicates = [];
    
    exportRecords.forEach((record, index) => {
        const billKey = `${record.fields.State}-${record.fields.BillType}${record.fields.BillNumber}`;
        
        if (seenBills.has(billKey)) {
            duplicates.push({
                billKey,
                indexes: [seenBills.get(billKey), index]
            });
        } else {
            seenBills.set(billKey, index);
        }
    });
    
    return duplicates;
}

/**
 * Main function to generate website export
 */
async function generateWebsiteExport() {
    output.markdown(`**Starting Website Export Generation**`);
    
    // Get references to tables
    const billsTable = base.getTable('Bills');
    const exportTable = base.getTable('Website Exports');
    
    // 1. DELETE ALL EXISTING RECORDS FROM THE EXPORT TABLE
    try {
        // Get all existing records in the export table
        const existingRecords = await exportTable.selectRecordsAsync();
        
        if (existingRecords.records.length > 0) {
            output.markdown(`Deleting ${existingRecords.records.length} existing export records...`);
            
            // Delete in batches of 50 due to Airtable API limits
            const recordIds = existingRecords.records.map(r => r.id);
            for (let i = 0; i < recordIds.length; i += 50) {
                const batchIds = recordIds.slice(i, i + 50);
                await exportTable.deleteRecordsAsync(batchIds);
            }
            
            output.markdown(`✅ Cleared previous export data`);
        } else {
            output.markdown(`No existing export records to delete`);
        }
    } catch (error) {
        output.markdown(`⚠️ Error clearing export table: ${error.message}`);
        // Continue with export even if delete fails
    }
    
    // 2. GET ALL BILLS (NO FILTER)
    const records = await billsTable.selectRecordsAsync();

    // Initialize tracking arrays
    const exportRecords = [];  // Successfully processed records
    const errors = [];         // Error tracking
    const dateValidationErrors = []; // Track date validation issues specifically
    const billsWithUnsupportedSubpolicies = []; // Track bills with unsupported subpolicies

    // 3. PROCESS EACH BILL
    output.markdown(`Processing ${records.records.length} bills...`);
    
    for (const record of records.records) {
        try {
            // Check for date validation issues first
            const dateCheck = checkDateValidation(record);
            if (!dateCheck.valid) {
                // Store date validation errors separately for better reporting
                dateValidationErrors.push({
                    bill: record.getCellValue(CONFIG.FIELDS.BILL_ID) || 
                         `${record.getCellValue(CONFIG.FIELDS.STATE)?.name || ''}-${record.getCellValue(CONFIG.FIELDS.BILL_TYPE)?.name || ''}${record.getCellValue(CONFIG.FIELDS.BILL_NUMBER) || ''}`,
                    error: dateCheck.message
                });
                
                // Also add to general errors
                errors.push({
                    bill: record.getCellValue(CONFIG.FIELDS.BILL_ID) || 
                         `${record.getCellValue(CONFIG.FIELDS.STATE)?.name || ''}-${record.getCellValue(CONFIG.FIELDS.BILL_TYPE)?.name || ''}${record.getCellValue(CONFIG.FIELDS.BILL_NUMBER) || ''}`,
                    error: `Future date detected: ${dateCheck.message}`
                });
                
                // Skip this record
                continue;
            }
            
            // Validate record has required fields
            const validation = validateRecord(record);
            if (!validation.valid) {
                throw new Error(`Missing required fields: ${validation.missingFields.join(', ')}`);
            }
            
            const webRecord = await transformRecord(record);
            if (webRecord) {
                // Check if this record had unsupported subpolicies
                if (record.unsupportedSubpolicies && record.unsupportedSubpolicies.length > 0) {
                    billsWithUnsupportedSubpolicies.push({
                        billId: record.getCellValue(CONFIG.FIELDS.BILL_ID) || 
                               `${record.getCellValue(CONFIG.FIELDS.STATE)?.name || ''}-${record.getCellValue(CONFIG.FIELDS.BILL_TYPE)?.name || ''}${record.getCellValue(CONFIG.FIELDS.BILL_NUMBER) || ''}`,
                        unsupportedSubpolicies: record.unsupportedSubpolicies
                    });
                }
                
                // Prepare record for the export table
                const exportRecord = {
                    fields: {
                        // Only include the transformed bill data, no batch tracking
                        ...webRecord
                    }
                };
                
                exportRecords.push(exportRecord);
            }
        } catch (error) {
            errors.push({
                bill: record.getCellValue(CONFIG.FIELDS.BILL_ID) || `${record.getCellValue(CONFIG.FIELDS.STATE)?.name || 'Unknown'}-${record.getCellValue(CONFIG.FIELDS.BILL_TYPE)?.name || ''}${record.getCellValue(CONFIG.FIELDS.BILL_NUMBER) || ''}`,
                error: error.message
            });
        }
    }

    // Check for duplicates before creating records
    const duplicates = checkForDuplicates(exportRecords);
    if (duplicates.length > 0) {
        output.markdown(`⚠️ Found ${duplicates.length} duplicate bills in export:`);
        duplicates.forEach(dupe => {
            output.markdown(`- ${dupe.billKey} appears at positions ${dupe.indexes.join(' and ')}`);
        });
        
        // Option to remove duplicates if needed
        // We'll keep the first occurrence and remove any subsequent ones
        duplicates.forEach(dupe => {
            // Skip the first index (keep it)
            dupe.indexes.slice(1).forEach(indexToRemove => {
                exportRecords[indexToRemove] = null; // Mark for removal
            });
        });
        
        // Filter out null entries
        const filteredRecords = exportRecords.filter(r => r !== null);
        output.markdown(`Removed ${exportRecords.length - filteredRecords.length} duplicate entries`);
        exportRecords = filteredRecords;
    }

    // 4. CREATE ALL EXPORT RECORDS IN BATCHES
    if (exportRecords.length > 0) {
        try {
            // Process in batches of 50 due to Airtable API limits
            for (let i = 0; i < exportRecords.length; i += 50) {
                const batch = exportRecords.slice(i, i + 50);
                await exportTable.createRecordsAsync(batch);
                output.markdown(`Created batch ${Math.floor(i/50) + 1} of ${Math.ceil(exportRecords.length/50)} (${batch.length} records)`);
            }
            
            output.markdown(`✅ Created ${exportRecords.length} new export records`);
        } catch (error) {
            output.markdown(`⚠️ Error creating export records: ${error.message}`);
        }
    } else {
        output.markdown(`No records to export`);
    }

    // 5. GENERATE SUMMARY
    const summary = generateSummary(exportRecords, errors, dateValidationErrors);
    output.markdown(summary);
    
    // Report on duplicate checks
    output.markdown(`\n🔍 **Duplicate Bill Check**`);
    if (duplicates && duplicates.length > 0) {
        output.markdown(`Found and removed ${duplicates.length} duplicate bills during export.`);
        output.markdown(`Duplicate bills included:`);
        duplicates.slice(0, 10).forEach(dupe => {
            output.markdown(`- ${dupe.billKey} (appeared ${dupe.indexes.length} times)`);
        });
        if (duplicates.length > 10) {
            output.markdown(`... and ${duplicates.length - 10} more`);
        }
    } else {
        output.markdown(`✅ No duplicate bills found in the export.`);
    }
    
    // Report on unsupported subpolicies
    if (billsWithUnsupportedSubpolicies.length > 0) {
        output.markdown(`\n🔄 **Unsupported Subpolicies Removed**`);
        output.markdown(`The following ${billsWithUnsupportedSubpolicies.length} bills had unsupported subpolicies that were removed from the export:`);
        
        // Count frequency of each unsupported subpolicy
        const subpolicyCounts = {};
        billsWithUnsupportedSubpolicies.forEach(bill => {
            bill.unsupportedSubpolicies.forEach(subpolicy => {
                subpolicyCounts[subpolicy] = (subpolicyCounts[subpolicy] || 0) + 1;
            });
        });
        
        // Show frequency of each unsupported subpolicy
        output.markdown(`\nSubpolicy frequencies:`);
        Object.entries(subpolicyCounts)
            .sort(([, a], [, b]) => b - a) // Sort by frequency (highest first)
            .forEach(([subpolicy, count]) => {
                output.markdown(`- "${subpolicy}": found in ${count} bill(s)`);
            });
        
        // List first 10 bills with their unsupported subpolicies
        const maxToShow = Math.min(10, billsWithUnsupportedSubpolicies.length);
        output.markdown(`\nExample bills (showing ${maxToShow} of ${billsWithUnsupportedSubpolicies.length}):`);
        for (let i = 0; i < maxToShow; i++) {
            const bill = billsWithUnsupportedSubpolicies[i];
            output.markdown(`- ${bill.billId}: ${bill.unsupportedSubpolicies.join(', ')}`);
        }
        
        if (billsWithUnsupportedSubpolicies.length > maxToShow) {
            output.markdown(`... and ${billsWithUnsupportedSubpolicies.length - maxToShow} more`);
        }
    } else {
        output.markdown(`\n✅ No unsupported subpolicies found in the bills.`);
    }
    
    // Report on date validation issues
    if (dateValidationErrors.length > 0) {
        output.markdown(`\n⏰ **Date Validation Details**`);
        output.markdown(`${dateValidationErrors.length} bills had future dates and were skipped.`);
        
        // Count which fields had the most issues
        const fieldCounts = {};
        dateValidationErrors.forEach(error => {
            // Extract field names from the error message
            const message = error.error;
            const fieldMatches = message.match(/(?<=🚫s)[^0-9]+(?=s|$)/g);
            
            if (fieldMatches) {
                fieldMatches.forEach(field => {
                    const trimmedField = field.trim();
                    if (trimmedField) {
                        fieldCounts[trimmedField] = (fieldCounts[trimmedField] || 0) + 1;
                    }
                });
            }
        });
        
        // Show which fields had the most issues
        output.markdown(`\nField frequency:`);
        Object.entries(fieldCounts)
            .sort(([, a], [, b]) => b - a)
            .forEach(([field, count]) => {
                output.markdown(`- "${field}": found in ${count} bill(s)`);
            });
    }
    
    output.markdown(`\n**Export completed at ${new Date().toLocaleString()}**`);
}

// Execute the export process
await generateWebsiteExport();