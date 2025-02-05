// Website Export Formatter for Guttmacher Legislative Tracker

const CONFIG = {
    // Field mappings based on actual bills table structure
    FIELDS: {
        BILL_ID: 'BillID',
        ACCESS_ID: 'Access ID',
        STATE: 'State',
        BILL_TYPE: 'BillType', 
        BILL_NUMBER: 'BillNumber',
        DESCRIPTION: 'Description',
        CURRENT_BILL_STATUS: 'Current Bill Status',
        BILL_STATUS_HISTORY: 'Bill Status History',
        HISTORY: 'History',
        LAST_ACTION: 'Last Action',
        LAST_ACTION_DATE: 'Last Action',
        POLICY_CATEGORIES: 'Policy Categories',
        WEBSITE_BLURB: 'Website Blurb',
        READY_FOR_WEBSITE: 'Ready for Website',
        LAST_WEBSITE_EXPORT: 'Last Website Export'
    },

    // Mapping for website-friendly categories
    WEBSITE_CATEGORIES: {
        'Abortion': { 
            matches: ['Abortion', 'Abortion Medication', 'Fetal Issues', 'Fetal Tissue'],
            field: 'Abortion' 
        },
        'Contraception': { 
            matches: ['Contraception', 'Emergency Contraception'],
            field: 'Contraception' 
        },
        'Family Planning': { 
            matches: ['Family Planning', 'Reproductive Health'],
            field: 'FamilyPlanning' 
        },
        'Insurance': { 
            matches: ['Insurance', 'Coverage'],
            field: 'Insurance' 
        },
        'Youth Access': { 
            matches: ['Youth', 'Sex Ed', 'STIs'],
            field: 'YouthAccess' 
        },
        'Pregnancy Support': { 
            matches: ['Pregnancy', 'Appropriations'],
            field: 'PregnancySupport' 
        },
        'Crisis Pregnancy Centers': {
            matches: ['Crisis Pregnancy Centers', 'CPC'],
            field: 'CrisisPregnancyCenters'
        }
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
    // Validate record is ready for website
    if (!record.getCellValue(CONFIG.FIELDS.READY_FOR_WEBSITE)) return null;

    try {
        // Extract essential bill information
        const state = record.getCellValue(CONFIG.FIELDS.STATE)?.name || '';
        const billType = record.getCellValue(CONFIG.FIELDS.BILL_TYPE)?.name || '';
        const billNumber = String(record.getCellValue(CONFIG.FIELDS.BILL_NUMBER) || '');
        const summary = record.getCellValue(CONFIG.FIELDS.WEBSITE_BLURB);
        const policyCategoriesText = record.getCellValue(CONFIG.FIELDS.POLICY_CATEGORIES) || '';
        const currentStatus = record.getCellValue(CONFIG.FIELDS.CURRENT_BILL_STATUS)?.name || '';
        const billStatusHistory = record.getCellValue(CONFIG.FIELDS.BILL_STATUS_HISTORY)?.name || '';

        // Validate required fields
        const missingFields = [];
        ['STATE', 'BILL_TYPE', 'BILL_NUMBER', 'WEBSITE_BLURB']
            .forEach(field => {
                if (!record.getCellValue(CONFIG.FIELDS[field])) {
                    missingFields.push(field);
                }
            });
        
        if (missingFields.length > 0) {
            throw new Error(`Missing required fields: ${missingFields.join(', ')}`);
        }

        // Parse policy categories
        const policyCategories = Array.isArray(policyCategoriesText) 
            ? policyCategoriesText 
            : (policyCategoriesText || '')
                .toString()
                .split(',')
                .map(cat => cat.trim())
                .filter(cat => cat !== '');

        // Determine bill status
        const statusFlags = determineStatusFlags(currentStatus, billStatusHistory);

        // Map policy categories to flags
        const categoryFlags = mapPolicyCategories(policyCategories);

        // Construct export record
        return {
            ID: record.getCellValue(CONFIG.FIELDS.BILL_ID),
            State: state,
            BillType: billType,
            BillNumber: billNumber,
            BillDescription: record.getCellValue(CONFIG.FIELDS.DESCRIPTION),
            WebsiteBlurb: summary,
            LastActionDate: record.getCellValue(CONFIG.FIELDS.LAST_ACTION_DATE),
            History: record.getCellValue(CONFIG.FIELDS.HISTORY),
            ...categoryFlags,
            ...statusFlags
        };
    } catch (error) {
        throw new Error(`Transformation error: ${error.message}`);
    }
}

// Determine bill status flags
function determineStatusFlags(currentStatus, billStatusHistory) {
    return {
        Introduced: billStatusHistory.includes('Introduced') ? '1' : '0',
        Passed1Chamber: billStatusHistory.includes('Passed 1 Chamber') ? '1' : '0',
        Passed2Chamber: billStatusHistory.includes('Passed 2 Chamber') ? '1' : '0',
        OnGovDesk: billStatusHistory.includes('On Govs Desk') ? '1' : '0',
        Enacted: currentStatus === 'Enacted' ? '1' : '0',
        Vetoed: currentStatus === 'Vetoed' ? '1' : '0',
        Dead: currentStatus === 'Dead' ? '1' : '0'
    };
}

// Map policy categories to flags
function mapPolicyCategories(policyCategories) {
    const categoryMappings = {
        Abortion: ['Abortion', 'Abortion Medication'],
        Appropriations: ['Appropriations'],
        Contraception: ['Contraception'],
        FamilyPlanning: ['Family Planning'],
        Insurance: ['Insurance'],
        PeriodProducts: ['Period Products'],
        Pregnancy: ['Pregnancy'],
        Refusal: ['Refusal'],
        SexEd: ['Sex Ed'],
        STIs: ['STIs'],
        Youth: ['Youth'],
        CrisisPregnancyCenters: ['Crisis Pregnancy Centers']
    };

    return Object.fromEntries(
        Object.entries(categoryMappings).map(([key, matches]) => [
            key, 
            policyCategories.some(cat => matches.includes(cat)) ? '1' : '0'
        ])
    );
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

    // Category breakdown
    if (records.length > 0) {
        const categoryStats = {};
        const categoryFields = [
            'Abortion', 'Appropriations', 'Contraception', 
            'FamilyPlanning', 'Insurance', 'PeriodProducts', 
            'Pregnancy', 'Refusal', 'SexEd', 'STIs', 'Youth'
        ];

        records.forEach(record => {
            categoryFields.forEach(category => {
                if (record.fields[category] === 'Yes') {
                    categoryStats[category] = (categoryStats[category] || 0) + 1;
                }
            });
        });

        if (Object.keys(categoryStats).length > 0) {
            summary.push(`📑 **Category Breakdown**`);
            Object.entries(categoryStats)
                .sort(([, a], [, b]) => b - a)
                .forEach(([category, count]) => {
                    summary.push(`- ${category}: ${count}`);
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

// Main export function
async function generateWebsiteExport() {
    output.markdown(`**Starting Website Export Generation**`);
    
    // Get tables
    const billsTable = base.getTable('Bills');
    const exportTable = base.getTable('Website Exports');
    
    // Generate batch ID
    const batchId = generateBatchId();
    
    // Get records ready for website
    const records = await billsTable.selectRecordsAsync({
        filterByFormula: "AND({Ready for Website} = TRUE(), NOT({Website Blurb} = ''))"
    });

    const exportRecords = [];
    const errors = [];

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
                        ...Object.fromEntries(
                            Object.entries(webRecord).map(([key, value]) => [key, value])
                        )
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

    // Create export records in batches
    if (exportRecords.length > 0) {
        try {
            // Create export records
            for (let i = 0; i < exportRecords.length; i += 50) {
                const batch = exportRecords.slice(i, i + 50);
                await exportTable.createRecordsAsync(batch);
                output.markdown(`Created ${batch.length} export records`);
            }
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
