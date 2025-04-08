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
        ACTION_TYPE: 'Action Type'
    }
};

/**
 * Transforms a bill record into the website export format
 */
async function transformRecord(record) {
    try {
        // Extract core bill information
        const state = record.getCellValue(CONFIG.FIELDS.STATE)?.name || '';
        const billType = record.getCellValue(CONFIG.FIELDS.BILL_TYPE)?.name || '';
        const billNumber = String(record.getCellValue(CONFIG.FIELDS.BILL_NUMBER) || '');
        const websiteBlurb = record.getCellValue(CONFIG.FIELDS.WEBSITE_BLURB) || '';
        
        // Format date function
        const formatDate = (dateValue) => {
            if (!dateValue) return null;
            
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

        // Derive boolean status from date fields
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

        // Get subpolicies
        const specificPoliciesAccess = getSpecificPolicies(record.getCellValue(CONFIG.FIELDS.SPECIFIC_POLICIES_ACCESS)) || [];
        
        // Website requires exactly 10 subpolicy fields
        const subpolicies = specificPoliciesAccess.slice(0, 10);
        while (subpolicies.length < 10) {
            subpolicies.push('');
        }

        // Return the transformed record
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
 * Extracts specific policy values from policy field
 */
function getSpecificPolicies(policyField) {
    if (!policyField) {
      return [];
    }
    
    const cleanPolicyString = (str) => {
        if (typeof str !== 'string') {
          return str;
        }
        return str.replace(/[\r\n]+/g, ' ').trim();
    };
    
    if (Array.isArray(policyField)) {
        return policyField.map(p => {
            const name = p.name || p;
            return cleanPolicyString(name);
        });
    }
    
    if (typeof policyField === 'string') {
        return policyField
            .split(',')
            .map(p => cleanPolicyString(p))
            .filter(p => p);
    }
    
    return [];
}

/**
 * Generates a summary of the export process
 */
function generateSummary(records, errors) {
    const summary = [`**Website Export Summary**\n`];
    
    // Record count statistics
    summary.push(`📊 **Statistics**`);
    summary.push(`- Total records processed: ${records.length + errors.length}`);
    summary.push(`- Successfully exported: ${records.length}`);
    summary.push(`- Errors encountered: ${errors.length}\n`);

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

    // Error details section
    if (errors.length > 0) {
        summary.push(`⚠️ **Errors**`);
        errors.forEach(({bill, error}) => {
            summary.push(`- Bill ${bill}: ${error}`);
        });
    }

    return summary.join('\n');
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

    // 3. PROCESS EACH BILL
    output.markdown(`Processing ${records.records.length} bills...`);
    
    for (const record of records.records) {
        try {
            const webRecord = await transformRecord(record);
            if (webRecord) {
                // Prepare record for the export table (simplified without batch connection)
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
                bill: record.getCellValue(CONFIG.FIELDS.BILL_ID),
                error: error.message
            });
        }
    }

    // 4. CREATE ALL EXPORT RECORDS IN BATCHES
    if (exportRecords.length > 0) {
        try {
            // Process in batches of 50 due to Airtable API limits
            for (let i = 0; i < exportRecords.length; i += 50) {
                const batch = exportRecords.slice(i, i + 50);
                await exportTable.createRecordsAsync(batch);
            }
            
            output.markdown(`✅ Created ${exportRecords.length} new export records`);
        } catch (error) {
            output.markdown(`⚠️ Error creating export records: ${error.message}`);
        }
    } else {
        output.markdown(`No records to export`);
    }

    // 5. GENERATE SUMMARY
    const summary = generateSummary(exportRecords, errors);
    output.markdown(summary);
    
    output.markdown(`\n**Export completed at ${new Date().toLocaleString()}**`);
}

// Execute the export process
await generateWebsiteExport();