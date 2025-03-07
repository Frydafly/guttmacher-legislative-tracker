// Updated Website Export Script for Guttmacher Policy Tracker

const CONFIG = {
    // Field mappings based on current bills table structure - only fields used in the export
    FIELDS: {
        BILL_ID: 'BillID',
        STATE: 'State',
        BILL_TYPE: 'BillType',
        BILL_NUMBER: 'BillNumber',
        LAST_ACTION: 'Last Action',
        INTENT: 'Intent (access)',
        SPECIFIC_POLICIES_ACCESS: 'Specific Policies (access)',
        WEBSITE_BLURB: 'Website Blurb',
        READY_FOR_WEBSITE: 'Ready for Website',
        INTRODUCED_DATE: 'Introduction Date',
        PASSED1_CHAMBER_DATE: 'Passed 1 Chamber Date',
        VETOED_DATE: 'Vetoed Date',
        ENACTED_DATE: 'Enacted Date',
        ACTION_TYPE: 'Action Type'
    },

    // Export table field mapping
    EXPORT_FIELDS: {
        EXPORT_DATE: 'Export Date',
        EXPORT_BATCH: 'Batch ID',
        BILL_RECORD: 'Bill Record',
        EXPORTED_BY: 'Exported By'
    }
};

// Transform a single record for website export
async function transformRecord(record) {

    try {
        // Extract essential bill information
        const state = record.getCellValue(CONFIG.FIELDS.STATE)?.name || '';
        const billType = record.getCellValue(CONFIG.FIELDS.BILL_TYPE)?.name || '';
        const billNumber = String(record.getCellValue(CONFIG.FIELDS.BILL_NUMBER) || '');
        const websiteBlurb = record.getCellValue(CONFIG.FIELDS.WEBSITE_BLURB);
        // Format dates properly for export
        const formatDate = (dateValue) => {
            if (!dateValue) return null;
            
            // If it's already a string, return it as is
            if (typeof dateValue === 'string') return dateValue;
            
            // If it's a Date object, format it as YYYY-MM-DD
            if (dateValue instanceof Date) {
                return dateValue.toISOString().split('T')[0];
            }
            
            // If it's another format, try to convert to string
            return String(dateValue);
        };
        
        // Extract date fields directly from the table
        const lastActionDate = formatDate(record.getCellValue(CONFIG.FIELDS.LAST_ACTION));
        const introducedDate = formatDate(record.getCellValue(CONFIG.FIELDS.INTRODUCED_DATE));
        const passed1ChamberDate = formatDate(record.getCellValue(CONFIG.FIELDS.PASSED1_CHAMBER_DATE));
        const vetoedDate = formatDate(record.getCellValue(CONFIG.FIELDS.VETOED_DATE));
        const enactedDate = formatDate(record.getCellValue(CONFIG.FIELDS.ENACTED_DATE));

        // Get intent values (Protective, Neutral, Restrictive)
        const intent = record.getCellValue(CONFIG.FIELDS.INTENT) || [];
        const intentArray = Array.isArray(intent) ? intent.map(i => i.name) : [];
        
        // Check for Ballot Initiative based on Action Type field
        const actionType = record.getCellValue(CONFIG.FIELDS.ACTION_TYPE) || [];
        const actionTypeArray = Array.isArray(actionType) 
            ? actionType.map(i => i.name) 
            : typeof actionType === 'string' 
                ? actionType.split(',').map(i => i.trim()) 
                : [];
        
        const ballotInitiative = actionTypeArray.includes('Ballot Initiative') ? '1' : '0';
        
        // Court Case handling - assuming it's a similar field
        // Adjust this logic based on your actual data structure
        const courtCase = actionTypeArray.includes('Court Case') ? '1' : '0';

        // Extract subpolicies - ONLY from specific policies (access)
        const specificPoliciesAccess = getSpecificPolicies(record.getCellValue(CONFIG.FIELDS.SPECIFIC_POLICIES_ACCESS)) || [];
        
        // Create an array of exactly 10 subpolicies (padding with empty strings if needed)
        const subpolicies = specificPoliciesAccess.slice(0, 10);
        while (subpolicies.length < 10) {
            subpolicies.push('');
        }

        // Construct export record according to the website team's requirements
        return {
            State: state,
            BillType: billType,
            BillNumber: billNumber,
            "Ballot Initiative": ballotInitiative,
            "Court Case": courtCase,
            SubPolicy1: subpolicies[0],
            SubPolicy2: subpolicies[1],
            SubPolicy3: subpolicies[2],
            SubPolicy4: subpolicies[3],
            SubPolicy5: subpolicies[4],
            SubPolicy6: subpolicies[5],
            SubPolicy7: subpolicies[6],
            SubPolicy8: subpolicies[7],
            SubPolicy9: subpolicies[8],
            SubPolicy10: subpolicies[9],
            WebsiteBlurb: websiteBlurb,
            "Last Action Date": lastActionDate,
            IntroducedDate: introducedDate,
            Passed1ChamberDate: passed1ChamberDate,
            PassedLegislature: passed1ChamberDate, // Using the same field for now - adjust if needed
            VetoedDate: vetoedDate,
            EnactedDate: enactedDate,
            Positive: intentArray.includes('Protective') ? '1' : '0',
            Neutral: intentArray.includes('Neutral') ? '1' : '0',
            Restrictive: intentArray.includes('Restrictive') ? '1' : '0'
        };
    } catch (error) {
        throw new Error(`Transformation error: ${error.message}`);
    }
}

// Helper function to extract specific policies from various fields
function getSpecificPolicies(policyField) {
    if (!policyField) return [];
    
    // Handle if it's an array of select options
    if (Array.isArray(policyField)) {
        return policyField.map(p => p.name || p);
    }
    
    // Handle if it's a string
    if (typeof policyField === 'string') {
        return policyField.split(',').map(p => p.trim()).filter(p => p);
    }
    
    return [];
}

// Generate a unique batch ID for this export
function generateBatchId() {
    const date = new Date();
    return `WEB_${date.getFullYear()}${
        String(date.getMonth() + 1).padStart(2, '0')
    }${String(date.getDate()).padStart(2, '0')}_${
        String(date.getHours()).padStart(2, '0')
    }${String(date.getMinutes()).padStart(2, '0')}`;
}

// Generate a summary of the export process
function generateSummary(records, errors, batchId) {
    const summary = [`**Website Export Summary**\n\n`];
    
    // Batch information
    summary.push(`📦 **Export Batch**`);
    summary.push(`- Batch ID: ${batchId}`);
    summary.push(`- Export Date: ${new Date().toLocaleString()}\n`);
    
    // Record statistics
    summary.push(`📊 **Statistics**`);
    summary.push(`- Total records processed: ${records.length + errors.length}`);
    summary.push(`- Successfully exported: ${records.length}`);
    summary.push(`- Errors encountered: ${errors.length}\n`);

    // Category breakdown by intent
    if (records.length > 0) {
        const intentStats = {
            Positive: 0,
            Neutral: 0,
            Restrictive: 0
        };

        records.forEach(record => {
            if (record.fields.Positive === '1') intentStats.Positive++;
            if (record.fields.Neutral === '1') intentStats.Neutral++;
            if (record.fields.Restrictive === '1') intentStats.Restrictive++;
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

    // State breakdown
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

    // Errors
    if (errors.length > 0) {
        summary.push(`⚠️ **Errors**`);
        errors.forEach(({bill, error}) => {
            summary.push(`- Bill ${bill}: ${error}`);
        });
    }

    return summary.join('\n');
}

// Update bills with export information
async function updateExportedBills(billsTable, exportedBillIds, batchId) {
    // Since 'Exported to Website Date' is a computed field, we don't need to update it directly
    // We could potentially log the exports separately if needed
    
    return exportedBillIds.length; // Just return the count of exported bills
}

// Main export function
async function generateWebsiteExport() {
    output.markdown(`**Starting Website Export Generation**`);
    
    // Get tables
    const billsTable = base.getTable('Bills');
    const exportTable = base.getTable('Website Exports');
    
    // Generate batch ID
    const batchId = generateBatchId();
    
   // Get all records without filtering
    const records = await billsTable.selectRecordsAsync();

    const exportRecords = [];
    const errors = [];
    const exportedBillIds = [];

    // Process each bill
    for (const record of records.records) {
        try {
            const webRecord = await transformRecord(record);
            if (webRecord) {
                // Create export history record
                const exportRecord = {
                    fields: {
                        [CONFIG.EXPORT_FIELDS.EXPORT_DATE]: new Date().toISOString(),
                        [CONFIG.EXPORT_FIELDS.EXPORT_BATCH]: batchId,
                        [CONFIG.EXPORT_FIELDS.BILL_RECORD]: [{id: record.id}],
                        [CONFIG.EXPORT_FIELDS.EXPORTED_BY]: 'Automation',
                        ...webRecord
                    }
                };
                
                exportRecords.push(exportRecord);
                exportedBillIds.push(record.id);
            }
        } catch (error) {
            errors.push({
                bill: record.getCellValue(CONFIG.FIELDS.BILL_ID),
                error: error.message
            });
        }
    }

    // Create export records in batches
    if (exportRecords.length > 0) {
        try {
            // Create export records
            for (let i = 0; i < exportRecords.length; i += 50) {
                const batch = exportRecords.slice(i, i + 50);
                await exportTable.createRecordsAsync(batch);
                output.markdown(`Created ${batch.length} export records`);
            }
            
            // No longer trying to update 'Exported to Website Date' since it's computed
            output.markdown(`Successfully exported ${exportedBillIds.length} bills`);
        } catch (error) {
            output.markdown(`⚠️ **Error creating export records:** ${error.message}`);
        }
    }

    // Generate and output summary
    const summary = generateSummary(exportRecords, errors, batchId);
    output.markdown(summary);
}

// Run the export
await generateWebsiteExport();