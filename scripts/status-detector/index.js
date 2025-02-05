// Status Change Detector
// For use in Airtable Automations

// Configuration for status tracking
const STATUS_CONFIG = {
    // Status transitions that require immediate attention
    CRITICAL_CHANGES: [
        'Enacted',
        'Vetoed',
        'Dead'
    ],
    
    // Status transitions that need review but aren't urgent
    REVIEW_CHANGES: [
        'Passed First Chamber',
        'Passed Second Chamber',
        'On Govs Desk'
    ],
    
    // Important actions to detect in history
    SIGNIFICANT_ACTIONS: [
        'amended',
        'substituted',
        'chapter no',
        'signed by gov',
        'veto override',
        'conference committee'
    ]
};

// Field names from your table
const FIELDS = {
    BILL_ID: 'BillID',
    STATE: 'State',
    BILL_TYPE: 'BillType',
    BILL_NUMBER: 'BillNumber',
    CURRENT_STATUS: 'Current Bill Status',
    STATUS_HISTORY: 'Bill Status History',
    HISTORY: 'History',
    REVIEW_STATUS: 'Review Status',
    READY_FOR_WEBSITE: 'Ready for Website',
    INTERNAL_NOTES: 'Internal Notes',
    REVIEW_NOTES: 'Review Notes',
    ASSIGNED_TO: 'Assigned To'
};

module.exports = {
    STATUS_CONFIG,
    FIELDS
};

const { STATUS_CONFIG, FIELDS } = require('./config.js');

// Helper Functions
function formatBillId(record) {
    // For Single Select fields, need to get the name property
    const state = record.getCellValue(FIELDS.STATE)?.name || '';
    const type = record.getCellValue(FIELDS.BILL_TYPE)?.name || '';
    const number = record.getCellValue(FIELDS.BILL_NUMBER);
    return `${state} ${type}${number}`;
}

function formatReviewNote(type, details) {
    const timestamp = new Date().toLocaleString();
    return `[${timestamp}] ${type}: ${details}`;
}

function generateSummary(notifications) {
    if (notifications.length === 0) {
        return '**No significant changes detected**';
    }

    // Group notifications by type
    const grouped = notifications.reduce((acc, n) => {
        acc[n.type] = acc[n.type] || [];
        acc[n.type].push(n);
        return acc;
    }, {});

    let summary = '**Status Change Detection Summary**\n\n';

    if (grouped.CRITICAL) {
        summary += '🚨 **Critical Updates Needed**\n';
        grouped.CRITICAL.forEach(n => {
            summary += `- ${n.bill} (${n.status}): ${n.message}\n`;
        });
        summary += '\n';
    }

    if (grouped.ACTION) {
        summary += '📝 **Significant Actions**\n';
        grouped.ACTION.forEach(n => {
            summary += `- ${n.bill}: ${n.message}\n`;
        });
        summary += '\n';
    }

    if (grouped.REVIEW) {
        summary += '👀 **Review Needed**\n';
        grouped.REVIEW.forEach(n => {
            summary += `- ${n.bill} (${n.status}): ${n.message}\n`;
        });
    }

    return summary;
}

// Main function
async function detectStatusChanges() {
    output.markdown(`**Starting Status Change Detection**`);
    let table = base.getTable('Bills');

    // Get records
    const records = await table.selectRecordsAsync({
        fields: Object.values(FIELDS)
    });

    const updates = [];
    const notifications = [];

    for (let record of records.records) {
        const currentStatus = record.getCellValue(FIELDS.CURRENT_STATUS);
        const statusHistory = record.getCellValue(FIELDS.STATUS_HISTORY) || '';
        const history = record.getCellValue(FIELDS.HISTORY) || '';
        const billId = formatBillId(record);
        
        // Check for critical status changes (Enacted, Vetoed, Dead)
        if (STATUS_CONFIG.CRITICAL_CHANGES.includes(currentStatus)) {
            const needsWebsiteUpdate = currentStatus === 'Enacted' || currentStatus === 'Vetoed';
            const readyForWebsite = record.getCellValue(FIELDS.READY_FOR_WEBSITE);
            
            if (needsWebsiteUpdate && !readyForWebsite) {
                updates.push({
                    id: record.id,
                    fields: {
                        [FIELDS.REVIEW_STATUS]: { name: 'Needs Review' },
                        [FIELDS.REVIEW_NOTES]: formatReviewNote(currentStatus, 'Needs website blurb')
                    }
                });
                
                notifications.push({
                    type: 'CRITICAL',
                    status: currentStatus,
                    bill: billId,
                    message: 'Needs website update'
                });
            }
        }
        
        // Check for significant actions in recent history
        const recentHistory = history.split('\n')[0] || '';
        const hasSignificantAction = STATUS_CONFIG.SIGNIFICANT_ACTIONS.some(
            action => recentHistory.toLowerCase().includes(action)
        );
        
        if (hasSignificantAction) {
            updates.push({
                id: record.id,
                fields: {
                    [FIELDS.REVIEW_STATUS]: { name: 'Needs Review' },
                    [FIELDS.REVIEW_NOTES]: formatReviewNote('Action', recentHistory)
                }
            });
            
            notifications.push({
                type: 'ACTION',
                bill: billId,
                message: recentHistory
            });
        }
        
        // Check for movement through chambers
        const inReviewStatus = STATUS_CONFIG.REVIEW_CHANGES.some(
            status => statusHistory.includes(status) && !status.includes('Dead')
        );
        
        if (inReviewStatus) {
            updates.push({
                id: record.id,
                fields: {
                    [FIELDS.REVIEW_STATUS]: { name: 'Needs Review' },
                    [FIELDS.REVIEW_NOTES]: formatReviewNote('Movement', currentStatus)
                }
            });
            
            notifications.push({
                type: 'REVIEW',
                status: currentStatus,
                bill: billId,
                message: 'Chamber movement detected'
            });
        }
    }

    // Process updates in batches
    if (updates.length > 0) {
        try {
            for (let i = 0; i < updates.length; i += 50) {
                const batch = updates.slice(i, i + 50);
                await table.updateRecordsAsync(batch);
            }
        } catch (error) {
            output.markdown(`⚠️ **Error updating records:** ${error.message}`);
        }
    }

    // Generate summary report
    const summary = generateSummary(notifications);
    output.markdown(summary);
}

// Run the detector
await detectStatusChanges();

// Note: When copying to Airtable:
// 1. Copy the contents of config.js to replace the require statement at the top
// 2. Remove this comment block
