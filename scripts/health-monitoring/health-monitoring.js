// Policy Tracker Health Monitor - UPDATED VERSION
// This script runs health checks on the policy tracker database and tracks metrics over time
// It is designed to run weekly or after batch imports

// Configuration
const CONFIG = {
    TABLES: {
        BILLS: 'Bills',
        RAW_STATENET: 'StateNet Raw Import',
        SYSTEM_MONITOR: 'System Monitor',
        WEBSITE_EXPORTS: 'Website Exports'
    },
    BILLS_FIELDS: {
        BILL_ID: 'BillID',
        STATE: 'State',
        BILL_TYPE: 'BillType',
        BILL_NUMBER: 'BillNumber',
        STATUS: 'Current Bill Status', 
        PRIMARY_TOPICS: 'Policy Categories',
        INTENT: 'Intent',
        LAST_ACTION: 'Last Action',
        LAST_MODIFIED: 'Last Updated',
        WEBSITE_BLURB: 'Website Blurb',
        INTRODUCED_DATE: 'Introduction Date',
        SPECIFIC_POLICIES: 'Specific Policies',
        ACTION_TYPE: 'Action Type' // Added to detect Executive Orders
    },
    // Define which statuses are considered "active" for reporting
    ACTIVE_STATUSES: [
        'Introduced', 
        'In First Chamber', 
        'Passed First Chamber',
        'In Second Chamber',
        'Passed Both Chambers',
        'On Governor\'s Desk'
    ],
    // Define which statuses need website blurbs - MODIFIED to only include Enacted and Vetoed
    NEEDS_BLURB_STATUSES: [
        'Enacted',
        'Vetoed'
    ],
    // Define which bill types are exempt from certain checks
    EXEMPTIONS: {
        EXECUTIVE_ORDER: 'Executive Order'
    }
};

// Generate timestamp for this health check
const now = new Date();
const timestamp = now.toISOString();
let globalIssues = [];

// Main health check function
async function runSystemHealthCheck(checkType = 'Weekly', relatedImport = null) {
    console.log("## Starting System Health Check");
    console.log(`Check Type: ${checkType} | Time: ${now.toLocaleString()}`);
    
    try {
        // Get references to tables
        const billsTable = base.getTable(CONFIG.TABLES.BILLS);
        const systemMonitorTable = base.getTable(CONFIG.TABLES.SYSTEM_MONITOR);
        const exportTable = base.getTable(CONFIG.TABLES.WEBSITE_EXPORTS);
        const rawStateNetTable = base.getTable(CONFIG.TABLES.RAW_STATENET);
        
        // Find the most recent previous check
        const previousChecks = await systemMonitorTable.selectRecordsAsync({
            sorts: [{field: 'Check Date', direction: 'desc'}],
            fields: ['Check Date'],
            maxRecords: 1
        });
        
        let lastCheckDate = null;
        let daysSinceLastCheck = null;
        
        if (previousChecks.records.length > 0) {
            lastCheckDate = new Date(previousChecks.records[0].getCellValue('Check Date'));
            daysSinceLastCheck = Math.round((now - lastCheckDate) / (1000 * 60 * 60 * 24));
            console.log(`- Last check was ${daysSinceLastCheck} days ago on ${lastCheckDate.toLocaleDateString()}`);
        } else {
            // If no previous check, use 7 days ago as default
            lastCheckDate = new Date(now);
            lastCheckDate.setDate(lastCheckDate.getDate() - 7);
            daysSinceLastCheck = 7;
            console.log(`- This is the first health check (using ${daysSinceLastCheck} days as default window)`);
        }
        
        // Get all bills
        console.log("- Loading bills data...");
        const billsQuery = await billsTable.selectRecordsAsync({
            sorts: [
                {field: CONFIG.BILLS_FIELDS.LAST_MODIFIED, direction: 'desc'}
            ]
        });
        const bills = billsQuery.records;
        
        // Get all export records
        console.log("- Loading export data...");
        const exportsQuery = await exportTable.selectRecordsAsync({
            sorts: [{field: 'State', direction: 'asc'}],
        });
        const exports = exportsQuery.records;
        
        // Get import data if this is a post-import check
        let importInfo = null;
        if (checkType === 'Post-Import' && relatedImport) {
            const importQuery = await rawStateNetTable.selectRecordsAsync({
                filterByFormula: `{Import Batch} = '${relatedImport}'`
            });
            importInfo = {
                batchId: relatedImport,
                recordCount: importQuery.records.length
            };
            console.log(`- This check is associated with import batch: ${relatedImport} (${importInfo.recordCount} records)`);
        }
        
        // CORE METRICS
        console.log("- Calculating metrics...");
        
        // Bills count
        const totalBills = bills.length;
        
        // Bills by status
        const statusCounts = {};
        bills.forEach(bill => {
            const statusObj = bill.getCellValue(CONFIG.BILLS_FIELDS.STATUS);
            // Extract the name from the single select object, or use a default if null
            const status = statusObj ? statusObj.name : "No Status";
            statusCounts[status] = (statusCounts[status] || 0) + 1;
        });
        
        // Format status breakdown for display
        const statusBreakdown = Object.entries(statusCounts)
            .map(([status, count]) => `${status}: ${count}`)
            .join('\n');
        
        // Data Quality Metrics
        
        // 1. Bills missing required fields
        const billsMissingInfo = bills.filter(bill => {
            return !bill.getCellValue(CONFIG.BILLS_FIELDS.STATE) || 
                   !bill.getCellValue(CONFIG.BILLS_FIELDS.BILL_TYPE) || 
                   !bill.getCellValue(CONFIG.BILLS_FIELDS.BILL_NUMBER);
        }).length;
        
        // 2. Bills missing categories
        const billsMissingCategories = bills.filter(bill => {
            const topics = bill.getCellValue(CONFIG.BILLS_FIELDS.PRIMARY_TOPICS);
            return !topics || topics.length === 0;
        }).length;
        
        // 3. Bills missing website blurbs that should have them (enacted or vetoed only)
        const billsMissingBlurbs = bills.filter(bill => {
            const statusObj = bill.getCellValue(CONFIG.BILLS_FIELDS.STATUS);
            const status = statusObj ? statusObj.name : null;
            const needsBlurb = status && CONFIG.NEEDS_BLURB_STATUSES.includes(status);
            const hasBlurb = Boolean(bill.getCellValue(CONFIG.BILLS_FIELDS.WEBSITE_BLURB));
            
            return needsBlurb && !hasBlurb; // Count ALL enacted/vetoed bills without blurbs
        }).length;
        
        // Track details of bills missing blurbs for reporting
        const detailedMissingBlurbs = bills.filter(bill => {
            const statusObj = bill.getCellValue(CONFIG.BILLS_FIELDS.STATUS);
            const status = statusObj ? statusObj.name : null;
            const needsBlurb = status && CONFIG.NEEDS_BLURB_STATUSES.includes(status);
            const hasBlurb = Boolean(bill.getCellValue(CONFIG.BILLS_FIELDS.WEBSITE_BLURB));
            
            return needsBlurb && !hasBlurb;
        }).map(bill => {
            return {
                state: bill.getCellValue(CONFIG.BILLS_FIELDS.STATE)?.name || '',
                billType: bill.getCellValue(CONFIG.BILLS_FIELDS.BILL_TYPE)?.name || '',
                billNumber: bill.getCellValue(CONFIG.BILLS_FIELDS.BILL_NUMBER) || '',
                lastAction: bill.getCellValue(CONFIG.BILLS_FIELDS.LAST_ACTION) || ''
            };
        });
        
        // Recently modified since last check
        const recentlyModified = bills.filter(bill => {
            const modified = bill.getCellValue(CONFIG.BILLS_FIELDS.LAST_MODIFIED);
            return modified && new Date(modified) >= lastCheckDate;
        }).length;
        
        // New bills since last check
        const newBillsSinceLastCheck = bills.filter(bill => {
            const created = bill.getCellValue('Import Date');
            return created && new Date(created) >= lastCheckDate;
        }).length;
        
        // Status changes since last check
        const statusChangesSinceLastCheck = bills.filter(bill => {
            const lastAction = bill.getCellValue(CONFIG.BILLS_FIELDS.LAST_ACTION);
            return lastAction && new Date(lastAction) >= lastCheckDate;
        }).length;
        
        // State coverage
        const states = new Set();
        bills.forEach(bill => {
            const state = bill.getCellValue(CONFIG.BILLS_FIELDS.STATE);
            if (state) states.add(state.name);
        });
        
        const statesList = Array.from(states).sort().join(', ');
        
        // Active states (states with active bills)
        const activeStates = new Set();
        // For the active states check
        bills.forEach(bill => {
            const statusObj = bill.getCellValue(CONFIG.BILLS_FIELDS.STATUS);
            const status = statusObj ? statusObj.name : null;
            if (status && CONFIG.ACTIVE_STATUSES.includes(status)) {
                const state = bill.getCellValue(CONFIG.BILLS_FIELDS.STATE);
                if (state) {
                  activeStates.add(state.name);
                }
            }
        });
        
        const activeStatesList = Array.from(activeStates).sort().join(', ');
        
        // Category coverage - fixed for your field structure
        const categoryMap = new Map();
        let categorizedBillsCount = 0;

        bills.forEach(bill => {
            const topics = bill.getCellValue(CONFIG.BILLS_FIELDS.PRIMARY_TOPICS) || [];
            
            if (topics.length > 0) {
                categorizedBillsCount++;
                
                topics.forEach(topic => {
                    if (topic) {
                        // Handle if topic is already a string or if it's an object with name
                        const categoryName = typeof topic === 'string' ? topic : 
                                        (topic.name || String(topic));
                        
                        if (categoryName) {
                            if (categoryMap.has(categoryName)) {
                                categoryMap.set(categoryName, categoryMap.get(categoryName) + 1);
                            } else {
                                categoryMap.set(categoryName, 1);
                            }
                        }
                    }
                });
            }
        });

        // Format as category: count
        const categoriesList = Array.from(categoryMap.entries())
            .sort(([, a], [, b]) => b - a) // Sort by count (highest first)
            .map(([category, count]) => `${category}: ${count}`)
            .join('\n');
        
        // Intent breakdown - fixed for your field structure
        const intentMap = new Map();

        bills.forEach(bill => {
            const intentValues = bill.getCellValue(CONFIG.BILLS_FIELDS.INTENT) || [];
            
            // intentValues is an array of objects, each with a name property
            intentValues.forEach(intent => {
                if (intent) {
                    // Handle if intent is already a string or if it's an object with name
                    const intentName = typeof intent === 'string' ? intent : 
                                    (intent.name ? intent.name : String(intent));
                    
                    if (intentName) {
                        if (intentMap.has(intentName)) {
                            intentMap.set(intentName, intentMap.get(intentName) + 1);
                        } else {
                            intentMap.set(intentName, 1);
                        }
                    }
                }
            });
        });

        // Format intent breakdown
        const intentBreakdown = Array.from(intentMap.entries())
            .sort(([, a], [, b]) => b - a) // Sort by count (highest first)
            .map(([intent, count]) => `${intent}: ${count}`)
            .join('\n');
        
        // High priority items - just the missing blurbs for enacted/vetoed
        const highPriorityItems = billsMissingBlurbs;
        
        // Identify data quality issues
        const potentialIssues = [];
        
        // Check for bills with inconsistent status and dates
        const billsWithStatusDateIssues = bills.filter(bill => {
            const statusObj = bill.getCellValue(CONFIG.BILLS_FIELDS.STATUS);
            const status = statusObj ? statusObj.name : null;
            const enactedDate = bill.getCellValue('Enacted Date');
            
            // Check if this is an Executive Order (exempt from date check)
            const actionType = bill.getCellValue(CONFIG.BILLS_FIELDS.ACTION_TYPE) || [];
            const actionTypeArray = Array.isArray(actionType) 
                ? actionType.map(a => a.name || '') 
                : typeof actionType === 'string' ? [actionType] : [];
            
            const isExecutiveOrder = actionTypeArray.includes(CONFIG.EXEMPTIONS.EXECUTIVE_ORDER);
            
            // If it's an EO, exempt it from the check
            if (isExecutiveOrder) return false;
            
            // If status is Enacted but no enactedDate, that's an issue
            if (status === 'Enacted' && !enactedDate) {
                return true;
            }
            
            // Similar checks for other statuses could be added
            return false;
        });
        
        if (billsWithStatusDateIssues.length > 0) {
            potentialIssues.push(`${billsWithStatusDateIssues.length} bills have status/date inconsistencies`);
            
            // Track in global issues for detailed reporting
            globalIssues.push({
                type: 'Status Date Inconsistency',
                count: billsWithStatusDateIssues.length,
                examples: billsWithStatusDateIssues.slice(0, 3).map(bill => {
                    return `${bill.getCellValue(CONFIG.BILLS_FIELDS.STATE)?.name || ''}-${bill.getCellValue(CONFIG.BILLS_FIELDS.BILL_TYPE)?.name || ''}${bill.getCellValue(CONFIG.BILLS_FIELDS.BILL_NUMBER) || ''}`;
                })
            });
        }
        
        // Check for duplicate bill IDs
        const billIdMap = new Map();
        const duplicateBills = [];
        
        bills.forEach(bill => {
            const state = bill.getCellValue(CONFIG.BILLS_FIELDS.STATE)?.name;
            const billType = bill.getCellValue(CONFIG.BILLS_FIELDS.BILL_TYPE)?.name;
            const billNumber = bill.getCellValue(CONFIG.BILLS_FIELDS.BILL_NUMBER);
            
            if (state && billType && billNumber) {
                const billId = `${state}-${billType}${billNumber}`;
                
                if (billIdMap.has(billId)) {
                    duplicateBills.push(billId);
                } else {
                    billIdMap.set(billId, bill.id);
                }
            }
        });
        
        if (duplicateBills.length > 0) {
            potentialIssues.push(`${duplicateBills.length} duplicate bill IDs found`);
            
            // Track in global issues
            globalIssues.push({
                type: 'Duplicate Bills',
                count: duplicateBills.length,
                examples: duplicateBills.slice(0, 3)
            });
        }
        
        // Last export info
        let lastExportDate = null;
        
        // If there's a previous health check with an export date, use that
        const recentChecks = await systemMonitorTable.selectRecordsAsync({
            sorts: [{field: 'Check Date', direction: 'desc'}],
            fields: ['Check Date', 'Last Export Date']
        });
        
        if (recentChecks.records.length > 0 && recentChecks.records[0].getCellValue('Last Export Date')) {
            lastExportDate = recentChecks.records[0].getCellValue('Last Export Date');
        }
        
        // If we have exports, use the most recent
        if (exports.length > 0) {
            lastExportDate = now;
        }
        
        // Calculate data quality score (0-100)
        // This is a weighted score based on key quality metrics
        const qualityComponents = {
            // % of bills with complete required fields (30% of score)
            requiredFields: ((totalBills - billsMissingInfo) / totalBills) * 30,
            
            // % of bills with categories assigned (30% of score)
            categoriesAssigned: ((totalBills - billsMissingCategories) / totalBills) * 30,
            
            // % of enacted/vetoed bills with website blurbs (40% of score)
            blurbsComplete: 40 // Calculate below
        };
        
        // Calculate % of bills that need blurbs and have them
        const billsNeedingBlurbs = bills.filter(bill => {
            const statusObj = bill.getCellValue(CONFIG.BILLS_FIELDS.STATUS);
            const status = statusObj ? statusObj.name : null;
            
            return status && CONFIG.NEEDS_BLURB_STATUSES.includes(status);
        }).length;
        
        if (billsNeedingBlurbs > 0) {
            qualityComponents.blurbsComplete = ((billsNeedingBlurbs - billsMissingBlurbs) / billsNeedingBlurbs) * 40;
        }
        
        // Calculate final quality score (0-100)
        const qualityScore = Math.round(
            qualityComponents.requiredFields + 
            qualityComponents.categoriesAssigned + 
            qualityComponents.blurbsComplete
        );
        
        // Generate detailed report
        const reportSummary = generateDetailedReportSummary(
            totalBills, 
            statusCounts, 
            billsMissingInfo, 
            billsMissingCategories, 
            billsMissingBlurbs, 
            recentlyModified, 
            statusChangesSinceLastCheck, 
            highPriorityItems,
            qualityScore, 
            exports.length,
            newBillsSinceLastCheck,
            daysSinceLastCheck,
            categoryMap,
            intentMap,
            detailedMissingBlurbs
        );
        
        // Prepare the monitor record - include report for viewing in table
        const monitorData = {
            "Check Date": timestamp,
            "Check Type": checkType,
            "Related Import": relatedImport,
            "Days Since Last Check": daysSinceLastCheck,
            
            // Core Metrics
            "Bills Count": totalBills,
            "Bills by Status": statusBreakdown,
            "Bills Missing Info": billsMissingInfo,
            "Bills Missing Categories": billsMissingCategories,
            "Bills Missing Blurbs": billsMissingBlurbs,
            "Recently Modified": recentlyModified,
            "Last Export Date": lastExportDate,
            "Export Count": exports.length,
            "New Bills Since Last Check": newBillsSinceLastCheck,
            "Active States": activeStatesList,
            "All States": statesList,
            "Categories Coverage": categoriesList,
            "Status Changes Since Last Check": statusChangesSinceLastCheck,
            "Intent Breakdown": intentBreakdown,
            "High Priority Items": highPriorityItems,
            "Potential Issues": potentialIssues.join('\n'),
            "Quality Score": qualityScore,
            "Detailed Report": reportSummary // Add full report to table
        };
        
        // Create new monitor record
        await systemMonitorTable.createRecordAsync(monitorData);
        console.log(`✅ Created new health check record`);
        
        // Log the report summary
        console.log("Health check complete with the following results:");
        console.log(reportSummary);
        
        return {
            success: true,
            checkDate: timestamp,
            billsCount: totalBills,
            qualityScore: qualityScore,
            highPriorityItems: highPriorityItems,
            reportSummary: reportSummary
        };
        
    } catch (error) {
        console.error(`⚠️ Error running health check: ${error.message}`);
        console.error(error);
        return {
            success: false,
            error: error.message
        };
    }
}

// Generate a detailed report summary
function generateDetailedReportSummary(
    totalBills, 
    statusCounts, 
    billsMissingInfo, 
    billsMissingCategories, 
    billsMissingBlurbs, 
    recentlyModified, 
    statusChangesSinceLastCheck, 
    highPriorityItems,
    qualityScore, 
    exportCount,
    newBillsSinceLastCheck,
    daysSinceLastCheck,
    categoryMap,
    intentMap,
    detailedMissingBlurbs
) {
    // Build summary text
    let summary = [];
    
    summary.push(`System Health Report (${new Date().toLocaleString()})`);
    summary.push("");
    summary.push("DATABASE OVERVIEW");
    summary.push(`Total Bills Tracked: ${totalBills}`);
    summary.push(`New Bills: ${newBillsSinceLastCheck} (in the last ${daysSinceLastCheck} days)`);
    summary.push(`Modified Bills: ${recentlyModified} (in the last ${daysSinceLastCheck} days)`);
    summary.push(`Status Changes: ${statusChangesSinceLastCheck} (in the last ${daysSinceLastCheck} days)`);
    summary.push(`Latest Export: ${exportCount} bills`);
    summary.push("");
    
    summary.push("DATA QUALITY");
    summary.push(`Quality Score: ${qualityScore}/100`);
    summary.push(`Bills Missing Info: ${billsMissingInfo} (${Math.round((billsMissingInfo/totalBills)*100)}%)`);
    summary.push(`Bills Missing Categories: ${billsMissingCategories} (${Math.round((billsMissingCategories/totalBills)*100)}%)`);
    
    // Detailed breakdown of bills missing blurbs
    summary.push(`Bills Missing Blurbs: ${billsMissingBlurbs}`);
    if (detailedMissingBlurbs && detailedMissingBlurbs.length > 0) {
        summary.push("  Bills missing website blurbs:");
        detailedMissingBlurbs.forEach(bill => {
            summary.push(`  - ${bill.state}-${bill.billType}${bill.billNumber} (Last action: ${bill.lastAction || 'Unknown'})`);
        });
    }
    
    summary.push(`High Priority Items: ${highPriorityItems}`);
    summary.push("");
    
    summary.push("BILL STATUS BREAKDOWN");
    Object.entries(statusCounts)
        .sort(([, a], [, b]) => b - a) // Sort by count (highest first)
        .forEach(([status, count]) => {
            summary.push(`${status}: ${count} (${Math.round((count/totalBills)*100)}%)`);
        });
    
    // Add category breakdown if available
    if (categoryMap && categoryMap.size > 0) {
        summary.push("");
        summary.push("CATEGORY BREAKDOWN");
        Array.from(categoryMap.entries())
            .sort(([, a], [, b]) => b - a) // Sort by count (highest first)
            .forEach(([category, count]) => {
                summary.push(`${category}: ${count} (${Math.round((count/totalBills)*100)}%)`);
            });
    }
    
    // Add intent breakdown if available
    if (intentMap && intentMap.size > 0) {
        summary.push("");
        summary.push("INTENT BREAKDOWN");
        Array.from(intentMap.entries())
            .sort(([, a], [, b]) => b - a) // Sort by count (highest first)
            .forEach(([intent, count]) => {
                summary.push(`${intent}: ${count} (${Math.round((count/totalBills)*100)}%)`);
            });
    }
    
    // Add issue details if we have any
    if (globalIssues.length > 0) {
        summary.push("");
        summary.push("POTENTIAL ISSUES");
        globalIssues.forEach(issue => {
            summary.push(`${issue.type}: ${issue.count} occurrences${issue.examples ? ` (Examples: ${issue.examples.join(', ')})` : ''}`);
        });
    }
    
    // Note about Executive Orders
    summary.push("");
    summary.push("NOTES");
    summary.push("- Executive Orders are exempt from the enacted date requirement");
    
    // Recommendations based on metrics
    let recommendations = [];
    
    if (billsMissingBlurbs > 0) {
        recommendations.push(`Add website blurbs to ${billsMissingBlurbs} enacted/vetoed bills`);
    }
    
    if (billsMissingCategories > totalBills * 0.05) { // More than 5% missing categories
        recommendations.push(`Assign categories to ${billsMissingCategories} uncategorized bills`);
    }
    
    if (billsMissingInfo > 0) {
        recommendations.push(`Complete basic information for ${billsMissingInfo} bills with missing required fields`);
    }
    
    if (globalIssues.some(issue => issue.type === 'Duplicate Bills')) {
        recommendations.push(`Review and resolve duplicate bills found in the database`);
    }
    
    if (recommendations.length > 0) {
        summary.push("");
        summary.push("RECOMMENDED ACTIONS");
        recommendations.forEach(rec => {
            summary.push(`- ${rec}`);
        });
    }
    
    return summary.join("\n");
}

// Check for input parameters - allows this to be run from different automation types
let checkType = 'Weekly'; // Default
let relatedImport = null;

// Check if input parameters were provided
if (input && input.checkType) {
    checkType = input.checkType;
}

if (input && input.relatedImport) {
    relatedImport = input.relatedImport;
}

// Run the health check
return await runSystemHealthCheck(checkType, relatedImport);