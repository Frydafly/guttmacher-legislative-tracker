// Guttmacher Policy Tracker: Website Export Script - Enhanced Version
// Purpose: Full export with real-time validation, quality reports, and change tracking
// Version: 3.0

// Configuration object for field mapping
const CONFIG = {
    // Source fields from Bills table
    FIELDS: {
        BILL_ID: 'BillID',
        STATE: 'State',
        BILL_TYPE: 'BillType',
        BILL_NUMBER: 'BillNumber',
        LAST_ACTION: 'Last Action',
        INTENT: 'Intent',
        SPECIFIC_POLICIES_ACCESS: 'Specific Policies',
        WEBSITE_BLURB: 'Website Blurb',
        INTRODUCED_DATE: 'Introduction Date',
        PASSED1_CHAMBER_DATE: 'Passed 1 Chamber Date',
        PASSED_LEGISLATURE_DATE: 'Passed Legislature Date',
        VETOED_DATE: 'Vetoed Date',
        ENACTED_DATE: 'Enacted Date',
        ACTION_TYPE: 'Action Type',
        DATE_VALIDATION: 'Date Validation',
        STATUS: 'Current Bill Status',
        LAST_MODIFIED: 'Last Modified Time'
    },
    
    // Quality tracking tables
    QUALITY_REPORTS_TABLE: 'Export Quality Reports',
    EXPORT_HISTORY_TABLE: 'Export History',
    
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
    ],
    
    // Quality thresholds (adjusted for realistic expectations)
    QUALITY_THRESHOLDS: {
        CRITICAL_SCORE: 50,        // Much lower threshold
        WARNING_SCORE: 70,         // More realistic warning level
        MAX_MISSING_BLURBS_PERCENT: 90,  // Most bills won't have blurbs
        MAX_DATE_ERRORS: 200       // Higher tolerance for date issues
    },
    
    // Fields where future dates are acceptable
    FUTURE_DATE_OK_FIELDS: [
        'ENACTED_DATE',            // Future enactment dates are normal
        'EFFECTIVE_DATE'           // Future effective dates are normal
    ]
};

/**
 * Quality metrics tracking class
 */
class QualityMetrics {
    constructor() {
        this.startTime = Date.now();
        this.metrics = {
            // Completeness metrics
            totalRecords: 0,
            recordsWithAllFields: 0,
            recordsMissingBlurb: 0,
            recordsMissingDates: 0,
            
            // Accuracy metrics
            dateValidationErrors: 0,
            duplicateBills: 0,
            dataFormatErrors: 0,
            
            // Coverage metrics
            statesRepresented: new Set(),
            policiesUsed: new Set(),
            intentDistribution: {
                positive: 0,
                neutral: 0,
                restrictive: 0,
                none: 0
            },
            
            // Processing metrics
            successfulTransforms: 0,
            failedTransforms: 0,
            warnings: []
        };
    }
    
    recordBill(record, success = true) {
        this.metrics.totalRecords++;
        if (success) {
            this.metrics.successfulTransforms++;
        } else {
            this.metrics.failedTransforms++;
        }
    }
    
    recordState(state) {
        if (state) {
            this.metrics.statesRepresented.add(state);
        }
    }
    
    recordPolicy(policies) {
        if (Array.isArray(policies)) {
            policies.forEach(p => {
                if (p) {
                  this.metrics.policiesUsed.add(p);
                }
            });
        }
    }
    
    recordIntent(hasPositive, hasNeutral, hasRestrictive) {
        if (hasPositive) {
          this.metrics.intentDistribution.positive++;
        }
        if (hasNeutral) {
          this.metrics.intentDistribution.neutral++;
        }
        if (hasRestrictive) {
          this.metrics.intentDistribution.restrictive++;
        }
        if (!hasPositive && !hasNeutral && !hasRestrictive) {
            this.metrics.intentDistribution.none++;
        }
    }
    
    recordMissingBlurb() {
        this.metrics.recordsMissingBlurb++;
    }
    
    recordDateError() {
        this.metrics.dateValidationErrors++;
    }
    
    addWarning(warning) {
        this.metrics.warnings.push(warning);
    }
    
    calculateQualityScore() {
        // Adjusted scoring for realistic expectations
        
        // Completeness score (30%) - Focus on basic fields, not blurbs
        const fieldCompleteness = (this.metrics.recordsWithAllFields / this.metrics.totalRecords * 100);
        const completenessScore = fieldCompleteness; // Don't penalize missing blurbs heavily
        
        // Accuracy score (50%) - Most important for export
        const errorRate = (this.metrics.dateValidationErrors + this.metrics.dataFormatErrors) / this.metrics.totalRecords;
        const accuracyScore = Math.max(0, 100 - (errorRate * 20)); // Less harsh penalty
        
        // Consistency score (20%)
        const duplicateRate = this.metrics.duplicateBills / this.metrics.totalRecords;
        const consistencyScore = Math.max(0, 100 - (duplicateRate * 100));
        
        // Weighted total - emphasize what actually matters for export
        const totalScore = (completenessScore * 0.3) + (accuracyScore * 0.5) + (consistencyScore * 0.2);
        
        return {
            total: Math.round(totalScore),
            completeness: Math.round(completenessScore),
            accuracy: Math.round(accuracyScore),
            consistency: Math.round(consistencyScore),
            grade: this.getGrade(totalScore)
        };
    }
    
    getGrade(score) {
        if (score >= 95) {
          return 'A+';
        }
        if (score >= 90) {
          return 'A';
        }
        if (score >= 85) {
          return 'B';
        }
        if (score >= 80) {
          return 'C';
        }
        if (score >= 70) {
          return 'D';
        }
        return 'F';
    }
    
    getDuration() {
        return (Date.now() - this.startTime) / 1000; // seconds
    }
    
    generateReport() {
        const score = this.calculateQualityScore();
        const duration = this.getDuration();
        
        return {
            summary: {
                date: new Date().toISOString(),
                duration: duration,
                totalRecords: this.metrics.totalRecords,
                successRate: (this.metrics.successfulTransforms / this.metrics.totalRecords * 100).toFixed(1),
                qualityScore: score
            },
            completeness: {
                recordsWithAllFields: this.metrics.recordsWithAllFields,
                recordsMissingBlurb: this.metrics.recordsMissingBlurb,
                missingBlurbPercent: (this.metrics.recordsMissingBlurb / this.metrics.totalRecords * 100).toFixed(1)
            },
            accuracy: {
                dateValidationErrors: this.metrics.dateValidationErrors,
                dataFormatErrors: this.metrics.dataFormatErrors,
                errorRate: ((this.metrics.dateValidationErrors + this.metrics.dataFormatErrors) / this.metrics.totalRecords * 100).toFixed(1)
            },
            coverage: {
                statesCount: this.metrics.statesRepresented.size,
                policiesCount: this.metrics.policiesUsed.size,
                intentDistribution: this.metrics.intentDistribution
            },
            warnings: this.metrics.warnings,
            recommendations: this.generateRecommendations()
        };
    }
    
    generateRecommendations() {
        const recs = [];
        const score = this.calculateQualityScore();
        
        // Critical recommendations
        if (score.total < CONFIG.QUALITY_THRESHOLDS.CRITICAL_SCORE) {
            recs.push({
                priority: 'CRITICAL',
                message: `Quality score (${score.total}) is below critical threshold`,
                action: 'Review data entry processes immediately'
            });
        }
        
        // Missing blurbs (only recommend if extremely high)
        const missingBlurbPercent = (this.metrics.recordsMissingBlurb / this.metrics.totalRecords * 100);
        if (missingBlurbPercent > CONFIG.QUALITY_THRESHOLDS.MAX_MISSING_BLURBS_PERCENT) {
            recs.push({
                priority: 'MEDIUM',
                message: `${this.metrics.recordsMissingBlurb} bills (${missingBlurbPercent.toFixed(1)}%) missing website blurbs`,
                action: 'Consider adding descriptions for high-impact enacted/vetoed bills'
            });
        }
        
        // Date errors
        if (this.metrics.dateValidationErrors > CONFIG.QUALITY_THRESHOLDS.MAX_DATE_ERRORS) {
            recs.push({
                priority: 'HIGH',
                message: `${this.metrics.dateValidationErrors} bills have date validation errors`,
                action: 'Review and correct future-dated entries'
            });
        }
        
        // State coverage
        if (this.metrics.statesRepresented.size < 40) {
            recs.push({
                priority: 'MEDIUM',
                message: `Only ${this.metrics.statesRepresented.size} states have bills in the system`,
                action: 'Verify data imports for missing states'
            });
        }
        
        return recs;
    }
}

/**
 * Pre-flight validation with detailed reporting
 */
async function runPreflightValidation() {
    output.markdown('## 🔍 Pre-flight Validation\n');
    
    const validation = {
        passed: true,
        critical: [],
        warnings: [],
        info: []
    };
    
    const billsTable = base.getTable('Bills');
    
    // Create progress indicator
    output.markdown('Checking data quality...');
    
    // Check 1: Future dates (only flag non-enacted date fields)
    const futureDateCheck = await billsTable.selectRecordsAsync({
        filterByFormula: `AND(
            {Date Validation} != '',
            NOT(FIND('Enacted', {Date Validation}) > 0),
            NOT(FIND('Effective', {Date Validation}) > 0)
        )`,
        fields: [CONFIG.FIELDS.BILL_ID, CONFIG.FIELDS.DATE_VALIDATION, CONFIG.FIELDS.STATE]
    });
    
    if (futureDateCheck.records.length > 50) {  // Only flag if many bills affected
        validation.warnings.push({
            type: '⏰ Unusual Future Dates',
            count: futureDateCheck.records.length,
            severity: 'WARNING',
            impact: 'Some bills have unexpected future dates',
            examples: futureDateCheck.records.slice(0, 3).map(r => ({
                bill: r.getCellValue(CONFIG.FIELDS.BILL_ID),
                issue: r.getCellValue(CONFIG.FIELDS.DATE_VALIDATION)
            }))
        });
    }
    
    // Check 2: Website blurbs (informational only)
    const blurbCheck = await billsTable.selectRecordsAsync({
        filterByFormula: `AND(
            OR({Current Bill Status} = 'Enacted', {Current Bill Status} = 'Vetoed'),
            OR({Website Blurb} = '', {Website Blurb} = BLANK())
        )`,
        fields: [CONFIG.FIELDS.BILL_ID, CONFIG.FIELDS.STATUS, CONFIG.FIELDS.STATE]
    });
    
    if (blurbCheck.records.length > 0) {
        const states = new Set(blurbCheck.records.map(r => r.getCellValue(CONFIG.FIELDS.STATE)?.name).filter(s => s));
        validation.info.push({
            type: '📝 Website Descriptions Status',
            count: blurbCheck.records.length,
            severity: 'INFO',
            impact: 'Standard - most bills export without descriptions',
            statesAffected: Array.from(states).sort()
        });
    }
    
    // Check 3: Duplicate bills
    const allBills = await billsTable.selectRecordsAsync({
        fields: [CONFIG.FIELDS.STATE, CONFIG.FIELDS.BILL_TYPE, CONFIG.FIELDS.BILL_NUMBER]
    });
    
    const billMap = new Map();
    const duplicates = [];
    
    allBills.records.forEach(record => {
        const key = `${record.getCellValue(CONFIG.FIELDS.STATE)?.name}-${record.getCellValue(CONFIG.FIELDS.BILL_TYPE)?.name}${record.getCellValue(CONFIG.FIELDS.BILL_NUMBER)}`;
        if (billMap.has(key)) {
            duplicates.push(key);
        } else {
            billMap.set(key, record.id);
        }
    });
    
    if (duplicates.length > 0) {
        validation.critical.push({
            type: '🔁 Duplicate Bills Found',
            count: duplicates.length,
            severity: 'CRITICAL',
            impact: 'Only first instance will be exported',
            examples: duplicates.slice(0, 5)
        });
    }
    
    // Check 4: Severely incomplete data (only truly broken records)
    const incompleteCheck = await billsTable.selectRecordsAsync({
        filterByFormula: `AND(
            {State} = BLANK(),
            {BillType} = BLANK(),
            {BillNumber} = BLANK()
        )`,  // Only flag if ALL core fields are missing
        fields: [CONFIG.FIELDS.BILL_ID]
    });
    
    if (incompleteCheck.records.length > 0) {
        validation.warnings.push({
            type: '⚠️ Severely Incomplete Records',
            count: incompleteCheck.records.length,
            severity: 'WARNING',
            impact: 'These records are missing all basic identifiers'
        });
    }
    
    // Display validation results
    displayValidationResults(validation);
    
    // Ask user to proceed if issues found
    if (!validation.passed) {
        const proceed = await input.buttonsAsync(
            '⚠️ Critical validation issues found. Continue with export?',
            [
                {label: '✅ Continue Anyway', value: true, variant: 'danger'},
                {label: '❌ Cancel Export', value: false}
            ]
        );
        
        return proceed;
    }
    
    return true;
}

/**
 * Display validation results in a formatted way
 */
function displayValidationResults(validation) {
    if (validation.critical.length > 0) {
        output.markdown('### ❌ Critical Issues\n');
        validation.critical.forEach(issue => {
            output.markdown(`**${issue.type}**`);
            output.markdown(`- Count: ${issue.count} records`);
            output.markdown(`- Impact: ${issue.impact}`);
            if (issue.examples && issue.examples.length > 0) {
                output.markdown(`- Examples:`);
                issue.examples.forEach(ex => {
                    if (typeof ex === 'string') {
                        output.markdown(`  - ${ex}`);
                    } else {
                        output.markdown(`  - ${ex.bill}: ${ex.issue}`);
                    }
                });
            }
            output.markdown('');
        });
    }
    
    if (validation.warnings.length > 0) {
        output.markdown('### ⚠️ Warnings\n');
        validation.warnings.forEach(warning => {
            output.markdown(`**${warning.type}**`);
            output.markdown(`- Count: ${warning.count} records`);
            output.markdown(`- Impact: ${warning.impact}`);
            if (warning.statesAffected) {
                output.markdown(`- States affected: ${warning.statesAffected.join(', ')}`);
            }
            output.markdown('');
        });
    }
    
    if (validation.info.length > 0) {
        output.markdown('### ℹ️ Information\n');
        validation.info.forEach(info => {
            output.markdown(`**${info.type}**`);
            output.markdown(`- Count: ${info.count} records`);
            output.markdown(`- Status: ${info.impact}`);
            output.markdown('');
        });
    }
    
    if (validation.critical.length === 0 && validation.warnings.length === 0) {
        output.markdown('### ✅ All Validation Checks Passed\n');
        output.markdown('No critical issues or warnings found. Ready to export!');
    } else if (validation.critical.length === 0) {
        output.markdown('### ✅ Ready to Export\n');
        output.markdown('No critical issues found. Warnings and info items noted above.');
    }
}

/**
 * Process bills with real-time progress tracking
 */
async function processWithProgress(records, metrics) {
    const total = records.length;
    const updateInterval = Math.max(1, Math.floor(total / 20)); // 5% increments
    
    const exportRecords = [];
    const errors = [];
    
    output.markdown(`\n### 📊 Processing ${total} Bills\n`);
    
    // Create progress tracking
    let lastUpdate = Date.now();
    
    for (let i = 0; i < records.length; i++) {
        const record = records[i];
        
        try {
            // Check date validation first
            const dateCheck = checkDateValidation(record);
            if (!dateCheck.valid) {
                metrics.recordDateError();
                metrics.recordBill(record, false);
                errors.push({
                    bill: record.getCellValue(CONFIG.FIELDS.BILL_ID) || 
                         `${record.getCellValue(CONFIG.FIELDS.STATE)?.name || ''}-${record.getCellValue(CONFIG.FIELDS.BILL_TYPE)?.name || ''}${record.getCellValue(CONFIG.FIELDS.BILL_NUMBER) || ''}`,
                    error: `Date validation: ${dateCheck.message}`
                });
                continue;
            }
            
            // Validate required fields
            const validation = validateRecord(record);
            if (!validation.valid) {
                metrics.recordBill(record, false);
                errors.push({
                    bill: record.getCellValue(CONFIG.FIELDS.BILL_ID) || 'Unknown',
                    error: `Missing required fields: ${validation.missingFields.join(', ')}`
                });
                continue;
            }
            
            // Transform the record
            const webRecord = await transformRecord(record, metrics);
            if (webRecord) {
                exportRecords.push({
                    fields: webRecord
                });
                metrics.recordBill(record, true);
                
                // Track state
                metrics.recordState(webRecord.State);
            }
            
        } catch (error) {
            metrics.recordBill(record, false);
            errors.push({
                bill: record.getCellValue(CONFIG.FIELDS.BILL_ID) || 
                     `${record.getCellValue(CONFIG.FIELDS.STATE)?.name || 'Unknown'}-${record.getCellValue(CONFIG.FIELDS.BILL_TYPE)?.name || ''}${record.getCellValue(CONFIG.FIELDS.BILL_NUMBER) || ''}`,
                error: error.message
            });
        }
        
        // Update progress at intervals or if 1 second has passed
        if (i % updateInterval === 0 || Date.now() - lastUpdate > 1000 || i === records.length - 1) {
            const progress = Math.round((i + 1) / total * 100);
            const processed = i + 1;
            const successful = exportRecords.length;
            const failed = errors.length;
            
            output.clear();
            output.markdown(`### 📊 Processing ${total} Bills\n`);
            output.markdown(`**Progress:** ${progress}% (${processed}/${total})`);
            output.markdown(`✅ Successful: ${successful} | ❌ Failed: ${failed}`);
            
            // Add progress bar
            const barLength = 20;
            const filled = Math.round(barLength * progress / 100);
            const bar = '█'.repeat(filled) + '░'.repeat(barLength - filled);
            output.markdown(`\n[${bar}]`);
            
            lastUpdate = Date.now();
        }
    }
    
    return { exportRecords, errors };
}

/**
 * Enhanced transform function with quality tracking
 */
async function transformRecord(record, metrics) {
    // Extract core bill information
    const state = record.getCellValue(CONFIG.FIELDS.STATE)?.name || '';
    const billType = record.getCellValue(CONFIG.FIELDS.BILL_TYPE)?.name || '';
    const billNumber = String(record.getCellValue(CONFIG.FIELDS.BILL_NUMBER) || '');
    
    // Check for all required fields
    const hasAllFields = state && billType && billNumber;
    if (hasAllFields) {
        metrics.metrics.recordsWithAllFields++;
    }
    
    // Handle rich text fields
    let websiteBlurbValue = record.getCellValue(CONFIG.FIELDS.WEBSITE_BLURB);
    let websiteBlurb = '';
    
    if (websiteBlurbValue) {
        if (typeof websiteBlurbValue === 'string') {
            websiteBlurb = websiteBlurbValue;
        } else if (typeof websiteBlurbValue === 'object' && websiteBlurbValue !== null) {
            websiteBlurb = websiteBlurbValue.text || websiteBlurbValue.toString() || '';
        }
    }
    
    websiteBlurb = websiteBlurb.replace(/[\r\n\t]+/g, ' ').replace(/\s+/g, ' ').trim();
    
    // Track missing blurbs (but don't penalize heavily)
    const status = record.getCellValue(CONFIG.FIELDS.STATUS)?.name;
    if ((status === 'Enacted' || status === 'Vetoed') && !websiteBlurb) {
        metrics.recordMissingBlurb();
    }
    
    // Format dates
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
    
    // Extract dates
    const lastActionDate = formatDate(record.getCellValue(CONFIG.FIELDS.LAST_ACTION));
    const introducedDate = formatDate(record.getCellValue(CONFIG.FIELDS.INTRODUCED_DATE));
    const passed1ChamberDate = formatDate(record.getCellValue(CONFIG.FIELDS.PASSED1_CHAMBER_DATE));
    const passedLegislatureDate = formatDate(record.getCellValue(CONFIG.FIELDS.PASSED_LEGISLATURE_DATE));
    const vetoedDate = formatDate(record.getCellValue(CONFIG.FIELDS.VETOED_DATE));
    const enactedDate = formatDate(record.getCellValue(CONFIG.FIELDS.ENACTED_DATE));

    // Boolean statuses
    const vetoedStatus = vetoedDate ? '1' : '0';
    const enactedStatus = enactedDate ? '1' : '0';
    const passed2ChamberStatus = passedLegislatureDate ? '1' : '0';

    // Process intent with tracking
    const intent = record.getCellValue(CONFIG.FIELDS.INTENT) || [];
    let intentValues = [];

    if (Array.isArray(intent)) {
        intentValues = intent.map(i => i.name || i);
    } else if (typeof intent === 'object' && intent !== null) {
        intentValues = [intent.name || ''];
    } else if (typeof intent === 'string') {
        intentValues = [intent];
    }

    const hasPositive = intentValues.some(val => val.includes('Positive'));
    const hasNeutral = intentValues.some(val => val.includes('Neutral'));
    const hasRestrictive = intentValues.some(val => val.includes('Restrictive'));
    
    // Track intent distribution
    metrics.recordIntent(hasPositive, hasNeutral, hasRestrictive);
    
    // Process action types
    const actionType = record.getCellValue(CONFIG.FIELDS.ACTION_TYPE) || [];
    const actionTypeArray = Array.isArray(actionType) 
        ? actionType.map(i => i.name) 
        : typeof actionType === 'string' 
            ? actionType.split(',').map(i => i.trim()) 
            : [];
    
    const ballotInitiative = actionTypeArray.includes('Ballot Initiative') ? '1' : '0';
    const courtCase = actionTypeArray.includes('Court Case') ? '1' : '0';

    // Get subpolicies with tracking
    const specificPoliciesResult = getSpecificPolicies(record.getCellValue(CONFIG.FIELDS.SPECIFIC_POLICIES_ACCESS));
    metrics.recordPolicy(specificPoliciesResult.policies);
    
    // Track unsupported subpolicies
    if (specificPoliciesResult.unsupportedFound.length > 0) {
        metrics.addWarning({
            type: 'Unsupported Subpolicy',
            bill: `${state}-${billType}${billNumber}`,
            policies: specificPoliciesResult.unsupportedFound
        });
    }
    
    const subpolicies = specificPoliciesResult.policies.slice(0, 10);
    while (subpolicies.length < 10) {
        subpolicies.push('');
    }

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
        Positive: hasPositive ? '1' : '0',
        Neutral: hasNeutral ? '1' : '0',
        Restrictive: hasRestrictive ? '1' : '0'
    };
}

/**
 * Save quality report to table
 */
async function saveQualityReport(metrics) {
    try {
        const reportTable = base.getTable(CONFIG.QUALITY_REPORTS_TABLE);
        const report = metrics.generateReport();
        
        await reportTable.createRecordAsync({
            'Export Date': new Date(),
            'Quality Score': report.summary.qualityScore.total,
            'Grade': report.summary.qualityScore.grade,
            'Total Records': report.summary.totalRecords,
            'Success Rate': parseFloat(report.summary.successRate),
            'Duration (seconds)': report.summary.duration,
            'Completeness Score': report.summary.qualityScore.completeness,
            'Accuracy Score': report.summary.qualityScore.accuracy,
            'Consistency Score': report.summary.qualityScore.consistency,
            'Missing Blurbs': report.completeness.recordsMissingBlurb,
            'Date Errors': report.accuracy.dateValidationErrors,
            'States Count': report.coverage.statesCount,
            'Recommendations': JSON.stringify(report.recommendations),
            'Full Report': JSON.stringify(report, null, 2)
        });
        
        output.markdown('\n✅ Quality report saved to Export Quality Reports table');
        
    } catch (error) {
        output.markdown(`\n⚠️ Could not save quality report: ${error.message}`);
    }
}

/**
 * Generate comprehensive export summary
 */
function generateEnhancedSummary(exportRecords, errors, metrics) {
    const report = metrics.generateReport();
    const summary = [`# 📊 Website Export Summary\n`];
    
    // Quality score banner
    const score = report.summary.qualityScore;
    const scoreEmoji = score.total >= 90 ? '🏆' : score.total >= 80 ? '✅' : score.total >= 70 ? '⚠️' : '❌';
    
    summary.push(`## ${scoreEmoji} Quality Score: ${score.total}/100 (${score.grade})\n`);
    
    // Score breakdown
    summary.push(`### Score Components`);
    summary.push(`- **Completeness**: ${score.completeness}% - Data field coverage`);
    summary.push(`- **Accuracy**: ${score.accuracy}% - Valid dates and formats`);
    summary.push(`- **Consistency**: ${score.consistency}% - No duplicates\n`);
    
    // Export statistics
    summary.push(`## 📈 Export Statistics`);
    summary.push(`- **Total Processed**: ${report.summary.totalRecords}`);
    summary.push(`- **Successfully Exported**: ${exportRecords.length}`);
    summary.push(`- **Failed**: ${errors.length}`);
    summary.push(`- **Success Rate**: ${report.summary.successRate}%`);
    summary.push(`- **Processing Time**: ${report.summary.duration.toFixed(1)} seconds\n`);
    
    // Coverage analysis
    summary.push(`## 🗺️ Coverage Analysis`);
    summary.push(`- **States Represented**: ${report.coverage.statesCount}/50`);
    summary.push(`- **Unique Policies**: ${report.coverage.policiesCount}`);
    summary.push(`- **Intent Distribution**:`);
    summary.push(`  - Positive: ${report.coverage.intentDistribution.positive}`);
    summary.push(`  - Neutral: ${report.coverage.intentDistribution.neutral}`);
    summary.push(`  - Restrictive: ${report.coverage.intentDistribution.restrictive}`);
    summary.push(`  - No Intent: ${report.coverage.intentDistribution.none}\n`);
    
    // Data quality issues
    if (report.completeness.recordsMissingBlurb > 0 || report.accuracy.dateValidationErrors > 0) {
        summary.push(`## ⚠️ Data Quality Issues`);
        if (report.completeness.recordsMissingBlurb > 0) {
            summary.push(`- **Missing Website Blurbs**: ${report.completeness.recordsMissingBlurb} (${report.completeness.missingBlurbPercent}%)`);
        }
        if (report.accuracy.dateValidationErrors > 0) {
            summary.push(`- **Date Validation Errors**: ${report.accuracy.dateValidationErrors}`);
        }
        summary.push('');
    }
    
    // Recommendations
    if (report.recommendations.length > 0) {
        summary.push(`## 💡 Recommendations`);
        report.recommendations.forEach(rec => {
            const icon = rec.priority === 'CRITICAL' ? '🚨' : rec.priority === 'HIGH' ? '⚠️' : 'ℹ️';
            summary.push(`${icon} **${rec.priority}**: ${rec.message}`);
            summary.push(`   → ${rec.action}`);
        });
        summary.push('');
    }
    
    // Error details (limited)
    if (errors.length > 0) {
        summary.push(`## ❌ Export Errors (First 10)`);
        errors.slice(0, 10).forEach(({bill, error}) => {
            summary.push(`- **${bill}**: ${error}`);
        });
        if (errors.length > 10) {
            summary.push(`- ... and ${errors.length - 10} more errors`);
        }
    }
    
    return summary.join('\n');
}

// ===== HELPER FUNCTIONS =====

function checkDateValidation(record) {
    const dateValidation = record.getCellValue(CONFIG.FIELDS.DATE_VALIDATION);
    
    if (dateValidation && dateValidation.trim() !== '') {
        return {
            valid: false,
            message: dateValidation
        };
    }
    
    return {
        valid: true,
        message: null
    };
}

function validateRecord(record) {
    const missingFields = [];
    
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

function getSpecificPolicies(policyField) {
    if (!policyField) {
        return { policies: [], unsupportedFound: [] };
    }
    
    const cleanPolicyString = (str) => {
        if (typeof str !== 'string') {
            return str;
        }
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
    
    const unsupported = [];
    const filtered = policies.filter(policy => {
        if (CONFIG.UNSUPPORTED_SUBPOLICIES.includes(policy)) {
            unsupported.push(policy);
            return false;
        }
        return true;
    });
    
    return {
        policies: filtered,
        unsupportedFound: unsupported
    };
}

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

// ===== MAIN EXPORT FUNCTION =====

async function generateWebsiteExport() {
    output.markdown('# 🌐 Website Export - Enhanced Version\n');
    output.markdown(`Export started at ${new Date().toLocaleString()}\n`);
    
    // Initialize quality metrics
    const metrics = new QualityMetrics();
    
    // Run pre-flight validation
    const shouldProceed = await runPreflightValidation();
    if (!shouldProceed) {
        output.markdown('\n❌ Export cancelled by user due to validation issues.');
        return;
    }
    
    // Get tables
    const billsTable = base.getTable('Bills');
    const exportTable = base.getTable('Website Exports');
    
    // Clear existing export records
    try {
        output.markdown('\n### 🗑️ Clearing Previous Export\n');
        const existingRecords = await exportTable.selectRecordsAsync();
        
        if (existingRecords.records.length > 0) {
            output.markdown(`Deleting ${existingRecords.records.length} existing records...`);
            
            const recordIds = existingRecords.records.map(r => r.id);
            for (let i = 0; i < recordIds.length; i += 50) {
                const batchIds = recordIds.slice(i, i + 50);
                await exportTable.deleteRecordsAsync(batchIds);
            }
            
            output.markdown('✅ Previous export cleared\n');
        } else {
            output.markdown('No existing records to delete\n');
        }
    } catch (error) {
        output.markdown(`⚠️ Error clearing export table: ${error.message}\n`);
    }
    
    // Get all bills
    const records = await billsTable.selectRecordsAsync();
    
    // Process bills with progress tracking
    const { exportRecords, errors } = await processWithProgress(records.records, metrics);
    
    // Check for duplicates
    const duplicates = checkForDuplicates(exportRecords);
    if (duplicates.length > 0) {
        metrics.metrics.duplicateBills = duplicates.length;
        output.markdown(`\n⚠️ Found ${duplicates.length} duplicate bills, keeping first occurrence of each\n`);
        
        // Remove duplicates
        duplicates.forEach(dupe => {
            dupe.indexes.slice(1).forEach(indexToRemove => {
                exportRecords[indexToRemove] = null;
            });
        });
        
        // Filter out nulls
        const filteredRecords = exportRecords.filter(r => r !== null);
        exportRecords.length = 0;
        exportRecords.push(...filteredRecords);
    }
    
    // Create export records
    if (exportRecords.length > 0) {
        output.markdown('\n### 💾 Creating Export Records\n');
        try {
            for (let i = 0; i < exportRecords.length; i += 50) {
                const batch = exportRecords.slice(i, i + 50);
                await exportTable.createRecordsAsync(batch);
                
                const progress = Math.round((i + 50) / exportRecords.length * 100);
                output.markdown(`Creating records: ${Math.min(progress, 100)}% complete`);
            }
            
            output.markdown(`\n✅ Successfully created ${exportRecords.length} export records`);
            
        } catch (error) {
            output.markdown(`\n❌ Error creating export records: ${error.message}`);
        }
    } else {
        output.markdown('\n⚠️ No records to export');
    }
    
    // Save quality report
    await saveQualityReport(metrics);
    
    // Generate and display enhanced summary
    const summary = generateEnhancedSummary(exportRecords, errors, metrics);
    output.markdown('\n' + summary);
    
    // Show completion time
    output.markdown(`\n**Export completed at ${new Date().toLocaleString()}**`);
}

// Execute the export
await generateWebsiteExport();