// ========================================================================
// Guttmacher Policy Tracker: Website Export Script
// Purpose: Automates export of policy tracking data to website-compatible format
// ========================================================================

// Configuration object to map field names between Airtable tables and export format
const CONFIG = {
    // Maps field names from the Bills table to make script resistant to field name changes
    FIELDS: {
        BILL_ID: 'BillID',                              // Unique identifier for the bill
        STATE: 'State',                                 // State abbreviation (select field)
        BILL_TYPE: 'BillType',                          // Type of bill (H/S/etc.)
        BILL_NUMBER: 'BillNumber',                      // The specific bill number
        LAST_ACTION: 'Last Action',                     // Most recent action date
        INTENT: 'Intent (access)',                      // Policy intent tags (Protective/Neutral/Restrictive)
        SPECIFIC_POLICIES_ACCESS: 'Specific Policies (access)', // Detailed policy categorization
        WEBSITE_BLURB: 'Website Blurb',                 // Public-facing description
        READY_FOR_WEBSITE: 'Ready for Website',         // Flag to indicate web-ready
        INTRODUCED_DATE: 'Introduction Date',           // When bill was introduced
        PASSED1_CHAMBER_DATE: 'Passed 1 Chamber Date',  // When passed first chamber
        PASSED2_CHAMBER_DATE: 'Passed 2 Chamber Date',  // When passed second chamber (added as required)
        PASSED_LEGISLATURE_DATE: 'Passed Legislature Date', // When passed both chambers
        VETOED_DATE: 'Vetoed Date',                     // When vetoed, if applicable
        ENACTED_DATE: 'Enacted Date',                   // When enacted, if applicable
        ACTION_TYPE: 'Action Type'                      // Type of legislative action
    },

    // Maps field names in the Website Exports table
    EXPORT_FIELDS: {
        EXPORT_DATE: 'Export Date',                     // When the export was generated
        EXPORT_BATCH: 'Batch ID',                       // Unique identifier for the export batch
        BILL_RECORD: 'Bill Record',                     // Link back to original bill
        EXPORTED_BY: 'Exported By'                      // Source of the export (automation)
    }
};

/**
 * Transforms a bill record into the website export format
 * @param {Object} record - An Airtable record object from the Bills table
 * @returns {Object|null} - Website-compatible record or null if transformation failed
 */
async function transformRecord(record) {
    try {
        // Extract core bill information (handle potential null/undefined values)
        const state = record.getCellValue(CONFIG.FIELDS.STATE)?.name || '';
        const billType = record.getCellValue(CONFIG.FIELDS.BILL_TYPE)?.name || '';
        const billNumber = String(record.getCellValue(CONFIG.FIELDS.BILL_NUMBER) || '');
        const websiteBlurb = record.getCellValue(CONFIG.FIELDS.WEBSITE_BLURB);
        
        /**
         * Standardizes date values to YYYY-MM-DD format
         * Handles multiple input formats: Date objects, strings, or null
         * @param {Date|string|null} dateValue - The date value to format
         * @returns {string|null} - Formatted date string or null
         */
        const formatDate = (dateValue) => {
            if (!dateValue) {
              return null;
            }
            
            // If it's a Date object, format it as YYYY-MM-DD
            if (dateValue instanceof Date) {
                const year = dateValue.getFullYear();
                const month = String(dateValue.getMonth() + 1).padStart(2, '0');
                const day = String(dateValue.getDate()).padStart(2, '0');
                return `${year}-${month}-${day}`;
            }
            
            // If it's a string that looks like a date, try to convert to YYYY-MM-DD
            if (typeof dateValue === 'string') {
                // Try to parse the date string
                const parsedDate = new Date(dateValue);
                if (!isNaN(parsedDate.getTime())) {
                    const year = parsedDate.getFullYear();
                    const month = String(parsedDate.getMonth() + 1).padStart(2, '0');
                    const day = String(parsedDate.getDate()).padStart(2, '0');
                    return `${year}-${month}-${day}`;
                }
                return dateValue; // Return original if parsing fails
            }
            
            // If it's another format, try to convert to string
            return String(dateValue);
        };
        
        // Extract and format date fields to YYYY-MM-DD
        const lastActionDate = formatDate(record.getCellValue(CONFIG.FIELDS.LAST_ACTION));
        const introducedDate = formatDate(record.getCellValue(CONFIG.FIELDS.INTRODUCED_DATE));
        const passed1ChamberDate = formatDate(record.getCellValue(CONFIG.FIELDS.PASSED1_CHAMBER_DATE));
        const passed2ChamberDate = formatDate(record.getCellValue(CONFIG.FIELDS.PASSED2_CHAMBER_DATE));
        const passedLegislatureDate = formatDate(record.getCellValue(CONFIG.FIELDS.PASSED_LEGISLATURE_DATE));
        const vetoedDate = formatDate(record.getCellValue(CONFIG.FIELDS.VETOED_DATE));
        const enactedDate = formatDate(record.getCellValue(CONFIG.FIELDS.ENACTED_DATE));

        // Process intent flags (Protective/Neutral/Restrictive) from multiple select field
        const intent = record.getCellValue(CONFIG.FIELDS.INTENT) || [];
        // Convert to array of names regardless of input format
        const intentArray = Array.isArray(intent) ? intent.map(i => i.name) : [];
        
        // Determine if bill is a ballot initiative or court case from Action Type field
        const actionType = record.getCellValue(CONFIG.FIELDS.ACTION_TYPE) || [];
        // Handle action type whether it's an array, string, or empty
        const actionTypeArray = Array.isArray(actionType) 
            ? actionType.map(i => i.name) 
            : typeof actionType === 'string' 
                ? actionType.split(',').map(i => i.trim()) 
                : [];
        
        // Set as "1" for true or "0" for false (website format requirement)
        const ballotInitiative = actionTypeArray.includes('Ballot Initiative') ? '1' : '0';
        const courtCase = actionTypeArray.includes('Court Case') ? '1' : '0';

        // Get subpolicies from the access field using helper function
        const specificPoliciesAccess = getSpecificPolicies(record.getCellValue(CONFIG.FIELDS.SPECIFIC_POLICIES_ACCESS)) || [];
        
        // Website requires exactly 10 subpolicy fields (pad with empty strings if needed)
        const subpolicies = specificPoliciesAccess.slice(0, 10);
        while (subpolicies.length < 10) {
            subpolicies.push('');
        }

        // Return the transformed record in the format expected by the website
        return {
            State: state,
            BillType: billType,
            BillNumber: billNumber,
            "Ballot Initiative": ballotInitiative,
            "Court Case": courtCase,
            // Changed SubPolicy to Subpolicy as requested
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
            "Passed 2 Chamber": passed2ChamberDate, // Added back as requested
            PassedLegislature: passedLegislatureDate, 
            VetoedDate: vetoedDate,
            EnactedDate: enactedDate,
            // Map intent values to website's 1/0 flag format
            Positive: intentArray.includes('Protective') ? '1' : '0',
            Neutral: intentArray.includes('Neutral') ? '1' : '0',
            Restrictive: intentArray.includes('Restrictive') ? '1' : '0'
        };
    } catch (error) {
        throw new Error(`Transformation error: ${error.message}`);
    }
}

/**
 * Extracts specific policy values from policy field, handling multiple formats
 * @param {Array|string|null} policyField - The policy field value
 * @returns {Array} - Array of policy names
 */
function getSpecificPolicies(policyField) {
    if (!policyField) {
      return [];
    }
    
    // Helper function to clean policy strings (remove newlines and trim)
    const cleanPolicyString = (str) => {
        if (typeof str !== 'string') return str;
        // Replace any newlines with a space and trim extra spaces
        return str.replace(/[\r\n]+/g, ' ').trim();
    };
    
    // Handle if it's an array of select options (common in Airtable)
    if (Array.isArray(policyField)) {
        return policyField.map(p => {
            const name = p.name || p;
            return cleanPolicyString(name);
        });
    }
    
    // Handle if it's a comma-separated string
    if (typeof policyField === 'string') {
        return policyField
            .split(',')
            .map(p => cleanPolicyString(p))
            .filter(p => p);
    }
    
    return [];
}

/**
 * Generates a unique timestamp-based batch ID for tracking exports
 * Format: WEB_YYYYMMDD_HHMM
 * @returns {string} - Unique batch identifier
 */
function generateBatchId() {
    const date = new Date();
    return `WEB_${date.getFullYear()}${
        String(date.getMonth() + 1).padStart(2, '0')
    }${String(date.getDate()).padStart(2, '0')}_${
        String(date.getHours()).padStart(2, '0')
    }${String(date.getMinutes()).padStart(2, '0')}`;
}

/**
 * Creates a detailed summary report of the export process
 * @param {Array} records - Successfully exported records
 * @param {Array} errors - Error objects with bill and error message
 * @param {string} batchId - The batch identifier
 * @returns {string} - Formatted markdown summary
 */
function generateSummary(records, errors, batchId) {
    const summary = [`**Website Export Summary**\n\n`];
    
    // Batch information section
    summary.push(`📦 **Export Batch**`);
    summary.push(`- Batch ID: ${batchId}`);
    summary.push(`- Export Date: ${new Date().toLocaleString()}\n`);
    
    // Record count statistics
    summary.push(`📊 **Statistics**`);
    summary.push(`- Total records processed: ${records.length + errors.length}`);
    summary.push(`- Successfully exported: ${records.length}`);
    summary.push(`- Errors encountered: ${errors.length}\n`);

    // Intent breakdown statistics (Positive/Neutral/Restrictive)
    if (records.length > 0) {
        const intentStats = {
            Positive: 0,
            Neutral: 0,
            Restrictive: 0
        };

        // Count records by intent flag
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

        // Add intent breakdown to summary
        summary.push(`📑 **Intent Breakdown**`);
        Object.entries(intentStats)
            .sort(([, a], [, b]) => b - a) // Sort by count descending
            .forEach(([intent, count]) => {
                if (count > 0) {
                    summary.push(`- ${intent}: ${count}`);
                }
            });
        summary.push('');
    }

    // State breakdown statistics (counts by state)
    if (records.length > 0) {
        const stateStats = {};
        records.forEach(record => {
            const state = record.fields.State;
            stateStats[state] = (stateStats[state] || 0) + 1;
        });

        if (Object.keys(stateStats).length > 0) {
            summary.push(`🌎 **State Breakdown**`);
            Object.entries(stateStats)
                .sort(([, a], [, b]) => b - a) // Sort by count descending
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

    // Join all parts with newlines
    return summary.join('\n');
}

/**
 * Updates bills with export information
 * @param {Object} billsTable - Airtable table object
 * @param {Array} exportedBillIds - Array of exported bill IDs
 * @param {string} batchId - The batch identifier
 * @returns {number} - Count of exported bills
 */
async function updateExportedBills(billsTable, exportedBillIds, batchId) {
    // Currently just returns count, as export date is handled by computed fields
    // Could be expanded to update additional fields if needed
    return exportedBillIds.length;
}

/**
 * Main function to generate website export records
 * Processes all bills, transforms them to website format, and creates export records
 */
async function generateWebsiteExport() {
    output.markdown(`**Starting Website Export Generation**`);
    
    // Get references to the required tables
    const billsTable = base.getTable('Bills');
    const exportTable = base.getTable('Website Exports');
    
    // Generate a unique batch identifier for this export
    const batchId = generateBatchId();
    
    // Retrieve bills that are ready for the website
    const records = await billsTable.selectRecordsAsync({
        filterByFormula: "AND({Ready for Website} = TRUE(), NOT({Website Blurb} = ''))"
    });

    // Initialize tracking arrays
    const exportRecords = [];  // Successfully processed records
    const errors = [];         // Error tracking
    const exportedBillIds = []; // IDs of exported bills

    // Process each bill one by one
    for (const record of records.records) {
        try {
            const webRecord = await transformRecord(record);
            if (webRecord) {
                // Prepare record for the export table
                const exportRecord = {
                    fields: {
                        // Export metadata
                        [CONFIG.EXPORT_FIELDS.EXPORT_DATE]: new Date().toISOString(),
                        [CONFIG.EXPORT_FIELDS.EXPORT_BATCH]: batchId,
                        [CONFIG.EXPORT_FIELDS.BILL_RECORD]: [{id: record.id}], // Link to original bill
                        [CONFIG.EXPORT_FIELDS.EXPORTED_BY]: 'Automation',
                        // Transformed bill data
                        ...webRecord
                    }
                };
                
                exportRecords.push(exportRecord);
                exportedBillIds.push(record.id);
            }
        } catch (error) {
            // Track errors with bill ID for reporting
            errors.push({
                bill: record.getCellValue(CONFIG.FIELDS.BILL_ID),
                error: error.message
            });
        }
    }

    // Create export records if any were successfully processed
    if (exportRecords.length > 0) {
        try {
            // Process in batches of 50 due to Airtable API limits
            for (let i = 0; i < exportRecords.length; i += 50) {
                const batch = exportRecords.slice(i, i + 50);
                await exportTable.createRecordsAsync(batch);
                output.markdown(`Created ${batch.length} export records`);
            }
            
            output.markdown(`Successfully exported ${exportedBillIds.length} bills`);
        } catch (error) {
            output.markdown(`⚠️ **Error creating export records:** ${error.message}`);
        }
    }

    // Generate and display the summary report
    const summary = generateSummary(exportRecords, errors, batchId);
    output.markdown(summary);
}

// Execute the export process
await generateWebsiteExport();