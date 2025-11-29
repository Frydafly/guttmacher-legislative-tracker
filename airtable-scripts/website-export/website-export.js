// Guttmacher Policy Tracker: Website Export Script
// Purpose: Full export with real-time validation, quality reports, and change tracking
// Version: Enhanced with Smart Validation & GitHub Integration (June 2025)
// Source: https://github.com/Frydafly/guttmacher-legislative-tracker
// 
// This script is version controlled in GitHub. For updates, bug reports, or questions:
// - Repository: https://github.com/Frydafly/guttmacher-legislative-tracker
// - Documentation: See README.md in the airtable-scripts/website-export/ directory
// - Issues: https://github.com/Frydafly/guttmacher-legislative-tracker/issues

// Configuration object for field mapping
const CONFIG = {
    // Source fields from Bills table
    FIELDS: {
        BILL_ID: 'BillID',
        WEBSITE_BILL_ID: 'Website Bill ID',
        YEAR: 'Year',
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
        STATUS: 'Current Bill Status'
    },
    
    // Quality tracking tables
    QUALITY_REPORTS_TABLE: 'Export Quality Reports',
    
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
    
    // Quality thresholds
    QUALITY_THRESHOLDS: {
        CRITICAL_SCORE: 50,        // Below this is critical
        WARNING_SCORE: 70,         // Below this is warning
        MAX_DATE_ERRORS: 0         // ANY date validation error is unacceptable
    }
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
            recordsWithSourceBlurb: 0,
            recordsWithExportedBlurb: 0,
            blurbProcessingFailures: 0,
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
            warnings: [],
            
            // Validation override tracking
            proceededDespiteCriticalIssues: false,
            criticalIssuesIgnored: []
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
    
    recordBlurbProcessing(hasSourceBlurb, hasExportedBlurb) {
        if (hasSourceBlurb) {
            this.metrics.recordsWithSourceBlurb++;
            if (hasExportedBlurb) {
                this.metrics.recordsWithExportedBlurb++;
            } else {
                this.metrics.blurbProcessingFailures++;
            }
        }
    }
    
    recordDateError() {
        this.metrics.dateValidationErrors++;
    }
    
    addWarning(warning) {
        this.metrics.warnings.push(warning);
    }
    
    recordCriticalIssuesIgnored(criticalIssues) {
        this.metrics.proceededDespiteCriticalIssues = true;
        this.metrics.criticalIssuesIgnored = criticalIssues.map(issue => ({
            type: issue.type,
            count: issue.count,
            impact: issue.impact
        }));
    }
    
    calculateQualityScore() {
        // Adjusted scoring for realistic expectations
        
        // Completeness score (30%) - Focus on basic fields plus blurb fidelity
        const fieldCompleteness = (this.metrics.recordsWithAllFields / this.metrics.totalRecords * 100);
        const blurbFidelity = this.metrics.recordsWithSourceBlurb > 0 ? 
            (this.metrics.recordsWithExportedBlurb / this.metrics.recordsWithSourceBlurb * 100) : 100;
        const completenessScore = (fieldCompleteness * 0.7) + (blurbFidelity * 0.3);
        
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
                recordsWithSourceBlurb: this.metrics.recordsWithSourceBlurb,
                recordsWithExportedBlurb: this.metrics.recordsWithExportedBlurb,
                blurbProcessingFailures: this.metrics.blurbProcessingFailures,
                blurbFidelityPercent: this.metrics.recordsWithSourceBlurb > 0 ? 
                    (this.metrics.recordsWithExportedBlurb / this.metrics.recordsWithSourceBlurb * 100).toFixed(1) : '100.0'
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
        
        // Blurb processing failures (should be 0 for 100% fidelity)
        if (this.metrics.blurbProcessingFailures > 0) {
            const fidelityPercent = this.metrics.recordsWithSourceBlurb > 0 ? 
                (this.metrics.recordsWithExportedBlurb / this.metrics.recordsWithSourceBlurb * 100) : 100;
            recs.push({
                priority: 'HIGH',
                message: `${this.metrics.blurbProcessingFailures} website blurbs failed to export (${(100 - fidelityPercent).toFixed(1)}% loss)`,
                action: 'CRITICAL: Review blurb processing logic - all existing blurbs must export'
            });
        }
        
        // Date errors - ANY date error is critical
        if (this.metrics.dateValidationErrors > 0) {
            recs.push({
                priority: 'CRITICAL',
                message: `${this.metrics.dateValidationErrors} bills have date validation errors`,
                action: 'CRITICAL: Fix all date validation issues before export'
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
 * 
 * Note: This function only adds issues to the critical array when there are actual problems.
 * If all checks pass (e.g., 0 missing fields), no critical issues are displayed and the
 * export proceeds automatically without user prompts.
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

    // Get current year for filtering - only validate bills we're about to export
    const currentYear = new Date().getFullYear().toString();

    // Create progress indicator
    output.markdown('Checking data quality...\n');

    // Check 1: Date validation issues - check for records with the 🚫 emoji (which means actual date issues)
    // NOTE: Fetch all and filter in JavaScript since filterByFormula on Year field is unreliable
    const dateIssueCheck = await billsTable.selectRecordsAsync({
        filterByFormula: `FIND('🚫', {Date Validation}) > 0`,
        fields: [CONFIG.FIELDS.BILL_ID, CONFIG.FIELDS.WEBSITE_BILL_ID, CONFIG.FIELDS.YEAR, CONFIG.FIELDS.DATE_VALIDATION, CONFIG.FIELDS.STATE]
    });

    if (dateIssueCheck.records.length > 0) {
        // Filter to current year and only include records that actually have the emoji in the text
        const actualIssues = dateIssueCheck.records.filter(r => {
            const yearField = r.getCellValue(CONFIG.FIELDS.YEAR);
            const recordYear = yearField?.name || yearField;
            if (recordYear != currentYear) return false;

            const val = r.getCellValue(CONFIG.FIELDS.DATE_VALIDATION);
            return val && typeof val === 'string' && val.includes('🚫');
        });

        if (actualIssues.length > 0) {
            validation.critical.push({
                type: '🚫 Future Date Issues',
                count: actualIssues.length,
                severity: 'CRITICAL',
                impact: 'Bills have future dates that need to be corrected',
                examples: actualIssues.slice(0, 10).map(r => ({
                    bill: r.getCellValue(CONFIG.FIELDS.WEBSITE_BILL_ID) || r.getCellValue(CONFIG.FIELDS.BILL_ID),
                    issue: r.getCellValue(CONFIG.FIELDS.DATE_VALIDATION)
                }))
            });
            validation.passed = false;
        }
    }
    
    // Check 2: Website blurbs (informational only)
    // NOTE: Fetch all and filter in JavaScript since filterByFormula on Year field is unreliable
    const blurbCheck = await billsTable.selectRecordsAsync({
        filterByFormula: `AND(
            OR({Current Bill Status} = 'Enacted', {Current Bill Status} = 'Vetoed'),
            OR({Website Blurb} = '', {Website Blurb} = BLANK())
        )`,
        fields: [CONFIG.FIELDS.BILL_ID, CONFIG.FIELDS.YEAR, CONFIG.FIELDS.STATUS, CONFIG.FIELDS.STATE]
    });

    if (blurbCheck.records.length > 0) {
        // Filter to current year in JavaScript
        const currentYearBlurbs = blurbCheck.records.filter(r => {
            const yearField = r.getCellValue(CONFIG.FIELDS.YEAR);
            const recordYear = yearField?.name || yearField;
            return recordYear == currentYear;
        });

        if (currentYearBlurbs.length > 0) {
            const states = new Set(currentYearBlurbs.map(r => r.getCellValue(CONFIG.FIELDS.STATE)?.name).filter(s => s));
            validation.info.push({
                type: '📝 Website Descriptions Status',
                count: currentYearBlurbs.length,
                severity: 'INFO',
                impact: 'Standard - most bills export without descriptions',
                statesAffected: Array.from(states).sort()
            });
        }
    }

    // Check 2b: Bills missing Year field entirely
    const missingYearCheck = await billsTable.selectRecordsAsync({
        filterByFormula: `{Year} = BLANK()`,
        fields: [CONFIG.FIELDS.BILL_ID, CONFIG.FIELDS.WEBSITE_BILL_ID, CONFIG.FIELDS.STATE, CONFIG.FIELDS.BILL_TYPE, CONFIG.FIELDS.BILL_NUMBER]
    });

    if (missingYearCheck.records.length > 0) {
        validation.warnings.push({
            type: '📅 Bills Missing Year Field',
            count: missingYearCheck.records.length,
            severity: 'WARNING',
            impact: `${missingYearCheck.records.length} bills have no Year assigned - they will not be exported`,
            examples: missingYearCheck.records.slice(0, 5).map(r =>
                r.getCellValue(CONFIG.FIELDS.WEBSITE_BILL_ID) ||
                r.getCellValue(CONFIG.FIELDS.BILL_ID) ||
                `${r.getCellValue(CONFIG.FIELDS.STATE)?.name || 'Unknown'}-${r.getCellValue(CONFIG.FIELDS.BILL_TYPE)?.name || ''}${r.getCellValue(CONFIG.FIELDS.BILL_NUMBER) || ''}`
            )
        });
    }

    // Check 3: Missing required fields - current year bills without BillID, Website Bill ID, State, BillType, or BillNumber
    // NOTE: Fetch all and filter in JavaScript since filterByFormula on Year field is unreliable
    const missingFieldsCheck = await billsTable.selectRecordsAsync({
        filterByFormula: `OR(
            {BillID} = BLANK(),
            {Website Bill ID} = BLANK(),
            {State} = BLANK(),
            {BillType} = BLANK(),
            {BillNumber} = BLANK()
        )`,
        fields: [CONFIG.FIELDS.BILL_ID, CONFIG.FIELDS.WEBSITE_BILL_ID, CONFIG.FIELDS.YEAR, CONFIG.FIELDS.STATE, CONFIG.FIELDS.BILL_TYPE, CONFIG.FIELDS.BILL_NUMBER]
    });

    if (missingFieldsCheck.records.length > 0) {
        // Filter to current year in JavaScript
        const currentYearMissing = missingFieldsCheck.records.filter(r => {
            const yearField = r.getCellValue(CONFIG.FIELDS.YEAR);
            const recordYear = yearField?.name || yearField;
            return recordYear == currentYear;
        });

        if (currentYearMissing.length > 0) {
            // Separate bills by what they're missing (Year is checked separately in Check 2b)
            const missingBillId = [];
            const missingWebsiteBillId = [];
            const missingState = [];
            const missingBillType = [];
            const missingBillNumber = [];

            currentYearMissing.forEach(r => {
                const billId = r.getCellValue(CONFIG.FIELDS.BILL_ID);
                const websiteBillId = r.getCellValue(CONFIG.FIELDS.WEBSITE_BILL_ID);
                const state = r.getCellValue(CONFIG.FIELDS.STATE);
                const billType = r.getCellValue(CONFIG.FIELDS.BILL_TYPE);
                const billNumber = r.getCellValue(CONFIG.FIELDS.BILL_NUMBER);

            const identifier = billId || websiteBillId || `${state?.name || 'Unknown'}-${billType?.name || ''}${billNumber || ''}`;

            if (!billId) {
                missingBillId.push(identifier);
            }
            if (!websiteBillId) {
                missingWebsiteBillId.push(identifier);
            }
            if (!state) {
                missingState.push(identifier);
            }
            if (!billType) {
                missingBillType.push(identifier);
            }
            if (!billNumber) {
                missingBillNumber.push(identifier);
            }
        });

        // Count total critical missing (all fields are critical for data integrity and export)
        const criticalMissingCount = missingBillId.length + missingWebsiteBillId.length + missingState.length + missingBillType.length + missingBillNumber.length;
        
        // Only add to critical issues if we actually found missing fields
        if (criticalMissingCount > 0) {
            // Build summary table showing only fields that are actually missing
            const summaryParts = [];
            if (missingBillId.length > 0) {
                summaryParts.push(`**BillID**: ${missingBillId.length} bills`);
            }
            if (missingWebsiteBillId.length > 0) {
                summaryParts.push(`**Website Bill ID**: ${missingWebsiteBillId.length} bills`);
            }
            if (missingState.length > 0) {
                summaryParts.push(`**State**: ${missingState.length} bills`);
            }
            if (missingBillType.length > 0) {
                summaryParts.push(`**BillType**: ${missingBillType.length} bills`);
            }
            if (missingBillNumber.length > 0) {
                summaryParts.push(`**BillNumber**: ${missingBillNumber.length} bills`);
            }

            // Create specific bills list
            const specificBills = [];
            if (missingBillId.length > 0) {
                missingBillId.forEach(identifier => {
                    specificBills.push(`${identifier}: Missing BillID`);
                });
            }
            if (missingWebsiteBillId.length > 0) {
                missingWebsiteBillId.forEach(identifier => {
                    specificBills.push(`${identifier}: Missing Website Bill ID`);
                });
            }
            if (missingState.length > 0) {
                missingState.forEach(identifier => {
                    specificBills.push(`${identifier}: Missing State`);
                });
            }
            if (missingBillType.length > 0) {
                missingBillType.forEach(identifier => {
                    specificBills.push(`${identifier}: Missing BillType`);
                });
            }
            if (missingBillNumber.length > 0) {
                missingBillNumber.forEach(identifier => {
                    specificBills.push(`${identifier}: Missing BillNumber`);
                });
            }
            
            validation.critical.push({
                type: '📋 Missing Required Fields',
                count: criticalMissingCount,
                severity: 'CRITICAL',
                impact: `${criticalMissingCount} bills missing critical fields will fail to export`,
                fieldSummary: summaryParts.join(', '),
                specificBills: specificBills
            });
            validation.passed = false;
        }
        }
    }
    
    // Check 4: Duplicate bills - using Website Bill ID as unique identifier for export
    // NOTE: Fetch all bills and filter in JavaScript since filterByFormula on Year field is unreliable
    const allBills = await billsTable.selectRecordsAsync({
        fields: [CONFIG.FIELDS.BILL_ID, CONFIG.FIELDS.WEBSITE_BILL_ID, CONFIG.FIELDS.YEAR, CONFIG.FIELDS.STATE, CONFIG.FIELDS.BILL_TYPE, CONFIG.FIELDS.BILL_NUMBER]
    });

    const websiteBillIdMap = new Map();
    const duplicateWebsiteBillIds = [];

    allBills.records.forEach(record => {
        // Filter to current year in JavaScript (more reliable than filterByFormula)
        const yearField = record.getCellValue(CONFIG.FIELDS.YEAR);
        const recordYear = yearField?.name || yearField;

        if (recordYear != currentYear) {
            return; // Skip bills from other years
        }

        const websiteBillId = record.getCellValue(CONFIG.FIELDS.WEBSITE_BILL_ID);
        const fullBillId = record.getCellValue(CONFIG.FIELDS.BILL_ID);
        if (websiteBillId) {
            if (websiteBillIdMap.has(websiteBillId)) {
                duplicateWebsiteBillIds.push({
                    websiteBillId: websiteBillId,
                    fullBillId: fullBillId,
                    year: recordYear,
                    descriptor: `${record.getCellValue(CONFIG.FIELDS.STATE)?.name || 'Unknown'}-${record.getCellValue(CONFIG.FIELDS.BILL_TYPE)?.name || ''}${record.getCellValue(CONFIG.FIELDS.BILL_NUMBER) || ''}`
                });
            } else {
                websiteBillIdMap.set(websiteBillId, record.id);
            }
        }
    });

    if (duplicateWebsiteBillIds.length > 0) {
        validation.critical.push({
            type: '🔁 Duplicate Website Bill IDs Found',
            count: duplicateWebsiteBillIds.length,
            severity: 'CRITICAL',
            impact: 'Only first instance will be exported',
            examples: duplicateWebsiteBillIds.slice(0, 5).map(d => `${d.websiteBillId} (Full ID: ${d.fullBillId}, Year: ${d.year}, ${d.descriptor})`)
        });
        validation.passed = false;
    }
    
    // Display validation results
    displayValidationResults(validation);
    
    // Ask user to proceed if critical issues found
    if (!validation.passed) {
        // Build a clear message about what critical issues were found
        let criticalMessage = '🚨 CRITICAL ISSUES FOUND:\n\n';
        
        validation.critical.forEach(issue => {
            criticalMessage += `❌ ${issue.type}: ${issue.count} ${issue.count === 1 ? 'record' : 'records'}\n`;
            criticalMessage += `   Impact: ${issue.impact}\n\n`;
        });
        
        criticalMessage += 'Do you want to continue with the export despite these critical issues?';
        
        const proceed = await input.buttonsAsync(
            criticalMessage,
            [
                {label: '✅ Continue Anyway', value: true, variant: 'danger'},
                {label: '❌ Cancel Export', value: false}
            ]
        );
        
        return {
            shouldProceed: proceed,
            criticalIssuesIgnored: proceed ? validation.critical : null
        };
    }
    
    return {
        shouldProceed: true,
        criticalIssuesIgnored: null
    };
}

/**
 * Display validation results in a formatted way
 */
function displayValidationResults(validation) {
    // Only show critical issues section if there are actual critical issues
    if (validation.critical.length > 0 && validation.critical.some(issue => issue.count > 0)) {
        output.markdown('### ❌ Critical Issues\n');
        validation.critical.forEach(issue => {
            // Only display issues that have a count > 0
            if (issue.count > 0) {
                output.markdown(`**${issue.type}**`);
                output.markdown(`- Count: ${issue.count} records`);
                output.markdown(`- Impact: ${issue.impact}`);
                if (issue.fieldSummary) {
                    // Display missing fields summary
                    output.markdown(`\n**Missing fields breakdown:** ${issue.fieldSummary}`);
                    
                    if (issue.specificBills) {
                        output.markdown(`\n**Specific bills to fix:**`);
                        issue.specificBills.forEach(bill => {
                            output.markdown(`- ${bill}`);
                        });
                    }
                } else if (issue.examples && issue.examples.length > 0) {
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
            }
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
            if (warning.examples && warning.examples.length > 0) {
                output.markdown(`- Examples:`);
                warning.examples.forEach(ex => {
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
    
    if (validation.info.length > 0) {
        output.markdown('### ℹ️ Information\n');
        validation.info.forEach(info => {
            output.markdown(`**${info.type}**`);
            output.markdown(`- Count: ${info.count} records`);
            output.markdown(`- Status: ${info.impact}`);
            output.markdown('');
        });
    }
    
    // Show success message when there are no actual critical issues
    const hasActualCriticalIssues = validation.critical.length > 0 && 
        validation.critical.some(issue => issue.count > 0);
    
    if (!hasActualCriticalIssues && validation.warnings.length === 0) {
        output.markdown('### ✅ All Validation Checks Passed\n');
        output.markdown('No critical issues or warnings found. Ready to export!');
    } else if (!hasActualCriticalIssues) {
        output.markdown('### ✅ Ready to Export\n');
        output.markdown('No critical issues found. Export can proceed without interruption.');
    }
}

/**
 * Process bills with real-time progress tracking
 */
async function processWithProgress(records, metrics) {
    const total = records.length;
    
    const exportRecords = [];
    const errors = [];
    
    output.markdown(`\n### 📊 Processing ${total} Bills\n`);
    
    for (let i = 0; i < records.length; i++) {
        const record = records[i];
        
        try {
            // Check date validation first
            const dateCheck = checkDateValidation(record);
            if (!dateCheck.valid) {
                metrics.recordDateError();
                metrics.recordBill(record, false);
                errors.push({
                    bill: record.getCellValue(CONFIG.FIELDS.WEBSITE_BILL_ID) || record.getCellValue(CONFIG.FIELDS.BILL_ID) ||
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
                    bill: record.getCellValue(CONFIG.FIELDS.WEBSITE_BILL_ID) || record.getCellValue(CONFIG.FIELDS.BILL_ID) || 'Unknown',
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
                bill: record.getCellValue(CONFIG.FIELDS.WEBSITE_BILL_ID) || record.getCellValue(CONFIG.FIELDS.BILL_ID) ||
                     `${record.getCellValue(CONFIG.FIELDS.STATE)?.name || 'Unknown'}-${record.getCellValue(CONFIG.FIELDS.BILL_TYPE)?.name || ''}${record.getCellValue(CONFIG.FIELDS.BILL_NUMBER) || ''}`,
                error: error.message
            });
        }
        
        // We'll show progress summary at the end instead of clearing output
    }
    
    return { exportRecords, errors };
}

/**
 * Enhanced transform function with quality tracking
 */
async function transformRecord(record, metrics) {
    // Extract website bill identifier FIRST - this is critical for preventing overwrites in export
    const websiteBillId = record.getCellValue(CONFIG.FIELDS.WEBSITE_BILL_ID) || '';

    // Extract core bill information
    const state = record.getCellValue(CONFIG.FIELDS.STATE)?.name || '';
    const billType = record.getCellValue(CONFIG.FIELDS.BILL_TYPE)?.name || '';
    const billNumber = String(record.getCellValue(CONFIG.FIELDS.BILL_NUMBER) || '');

    // Check for all required fields (including Website Bill ID for export uniqueness)
    const hasAllFields = websiteBillId && state && billType && billNumber;
    if (hasAllFields) {
        metrics.metrics.recordsWithAllFields++;
    }
    
    // Handle rich text fields - ensure 100% fidelity of existing blurbs
    let websiteBlurbValue = record.getCellValue(CONFIG.FIELDS.WEBSITE_BLURB);
    let websiteBlurb = '';
    
    // Check if there's a source blurb
    const hasSourceBlurb = websiteBlurbValue && 
        (typeof websiteBlurbValue === 'string' && websiteBlurbValue.trim() !== '') ||
        (typeof websiteBlurbValue === 'object' && websiteBlurbValue !== null && 
         (websiteBlurbValue.text || websiteBlurbValue.toString()));
    
    if (websiteBlurbValue) {
        if (typeof websiteBlurbValue === 'string') {
            websiteBlurb = websiteBlurbValue;
        } else if (typeof websiteBlurbValue === 'object' && websiteBlurbValue !== null) {
            websiteBlurb = websiteBlurbValue.text || websiteBlurbValue.toString() || '';
        }
    }
    
    websiteBlurb = websiteBlurb.replace(/[\r\n\t]+/g, ' ').replace(/\s+/g, ' ').trim();
    
    // Track blurb processing fidelity - ensure 100% coverage of existing blurbs
    const hasExportedBlurb = websiteBlurb && websiteBlurb.length > 0;
    metrics.recordBlurbProcessing(hasSourceBlurb, hasExportedBlurb);
    
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
        BillID: websiteBillId,  // CRITICAL: Website Bill ID (stripped of year) to prevent overwrites
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
        
        // Validate data before creating record
        const successRate = parseFloat(report.summary.successRate);
        if (isNaN(successRate)) {
            throw new Error('Success rate calculation resulted in NaN');
        }
        
        const recordData = {
            'Export Date': new Date(),
            'Quality Score': Math.round(report.summary.qualityScore.total),
            'Grade': report.summary.qualityScore.grade || 'F',
            'Total Records': report.summary.totalRecords || 0,
            'Success Rate': successRate,
            'Duration (seconds)': Math.round(report.summary.duration * 10) / 10, // Round to 1 decimal
            'Completeness Score': Math.round(report.summary.qualityScore.completeness),
            'Accuracy Score': Math.round(report.summary.qualityScore.accuracy),
            'Consistency Score': Math.round(report.summary.qualityScore.consistency),
            'Source Blurbs': report.completeness.recordsWithSourceBlurb || 0,
            'Exported Blurbs': report.completeness.recordsWithExportedBlurb || 0,
            'Blurb Failures': report.completeness.blurbProcessingFailures || 0,
            'Blurb Fidelity': parseFloat(report.completeness.blurbFidelityPercent) || 100,
            'Date Errors': report.accuracy.dateValidationErrors || 0,
            'States Count': report.coverage.statesCount || 0,
            'Critical Issues Ignored': metrics.metrics.proceededDespiteCriticalIssues ? 'YES' : 'NO',
            'Critical Issues Count': metrics.metrics.criticalIssuesIgnored.length || 0,
            'Critical Issues Details': metrics.metrics.proceededDespiteCriticalIssues ? 
                JSON.stringify(metrics.metrics.criticalIssuesIgnored).substring(0, 5000) : '',
            'Recommendations': JSON.stringify(report.recommendations).substring(0, 50000), // Limit size
            'Full Report': JSON.stringify(report, null, 2).substring(0, 100000) // Limit size
        };
        
        output.markdown(`\n📊 Creating quality report record...`);
        await reportTable.createRecordAsync(recordData);
        
        output.markdown('✅ Quality report saved to Export Quality Reports table');
        
    } catch (error) {
        output.markdown(`\n❌ Could not save quality report:`);
        output.markdown(`   Error: ${error.message}`);
        output.markdown(`   Make sure the '${CONFIG.QUALITY_REPORTS_TABLE}' table exists with correct field structure`);
        
        // List the required fields for user reference
        output.markdown(`\n📋 Required table structure:`);
        output.markdown(`   Table name: "${CONFIG.QUALITY_REPORTS_TABLE}"`);
        output.markdown(`   Fields needed: Export Date (Date), Quality Score (Number), Grade (Text), etc.`);
        output.markdown(`   See README.md for complete field specifications`);
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
    summary.push(`- **Processing Time**: ${report.summary.duration.toFixed(1)} seconds`);
    
    // Show if critical issues were ignored
    if (metrics.metrics.proceededDespiteCriticalIssues) {
        summary.push(`\n⚠️ **WARNING**: Export proceeded despite ${metrics.metrics.criticalIssuesIgnored.length} critical validation issue(s):`);
        metrics.metrics.criticalIssuesIgnored.forEach(issue => {
            summary.push(`   - ${issue.type}: ${issue.count} records`);
        });
    }
    summary.push('');
    
    // Coverage analysis
    summary.push(`## 🗺️ Coverage Analysis`);
    summary.push(`- **States Represented**: ${report.coverage.statesCount}/50`);
    summary.push(`- **Unique Policies**: ${report.coverage.policiesCount}`);
    summary.push(`- **Intent Distribution**:`);
    summary.push(`  - Positive: ${report.coverage.intentDistribution.positive}`);
    summary.push(`  - Neutral: ${report.coverage.intentDistribution.neutral}`);
    summary.push(`  - Restrictive: ${report.coverage.intentDistribution.restrictive}`);
    summary.push(`  - No Intent: ${report.coverage.intentDistribution.none}\n`);
    
    // Website blurb fidelity (critical metric)
    summary.push(`## 📝 Website Blurb Fidelity`);
    summary.push(`- **Bills with Source Blurbs**: ${report.completeness.recordsWithSourceBlurb}`);
    summary.push(`- **Successfully Exported**: ${report.completeness.recordsWithExportedBlurb}`);
    summary.push(`- **Processing Failures**: ${report.completeness.blurbProcessingFailures}`);
    summary.push(`- **Fidelity Rate**: ${report.completeness.blurbFidelityPercent}%`);
    
    if (report.completeness.blurbProcessingFailures > 0) {
        summary.push(`- ❌ **CRITICAL**: ${report.completeness.blurbProcessingFailures} existing blurbs failed to export!`);
    } else {
        summary.push(`- ✅ **Perfect fidelity**: All existing blurbs exported successfully`);
    }
    summary.push('');
    
    // Other data quality issues
    if (report.accuracy.dateValidationErrors > 0) {
        summary.push(`## ⚠️ Data Quality Issues`);
        summary.push(`- **Date Validation Errors**: ${report.accuracy.dateValidationErrors}`);
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

    // Website Bill ID is required to ensure unique exports
    const requiredFields = ['WEBSITE_BILL_ID', 'STATE', 'BILL_TYPE', 'BILL_NUMBER'];
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

function checkForDuplicates() {
    // Duplicate checking is handled in pre-flight validation using Website Bill IDs
    // This function is kept for backward compatibility but returns empty array
    return [];
}

// ===== MAIN EXPORT FUNCTION =====

async function generateWebsiteExport() {
    output.markdown('# 🌐 Website Export\n');
    output.markdown(`**Version:** Enhanced with Smart Validation & GitHub Integration (June 2025)\n`);
    output.markdown(`**Source:** [GitHub Repository](https://github.com/Frydafly/guttmacher-legislative-tracker)\n`);
    output.markdown(`Export started at ${new Date().toLocaleString()}\n`);
    
    // Initialize quality metrics
    const metrics = new QualityMetrics();
    
    // Run pre-flight validation
    const validationResult = await runPreflightValidation();
    if (!validationResult.shouldProceed) {
        output.markdown('\n❌ Export cancelled by user due to validation issues.');
        return;
    }
    
    // Track if critical issues were ignored
    if (validationResult.criticalIssuesIgnored) {
        metrics.recordCriticalIssuesIgnored(validationResult.criticalIssuesIgnored);
    }
    
    // Add separator before continuing with export
    output.markdown('\n---\n');
    output.markdown('## 📦 Starting Export Process\n');
    
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
    
    // Get bills for current year only
    // NOTE: Fetch all bills and filter in JavaScript since filterByFormula on Year field is unreliable
    const currentYear = new Date().getFullYear().toString();
    const allRecords = await billsTable.selectRecordsAsync();

    // Filter to current year in JavaScript
    const currentYearRecords = allRecords.records.filter(record => {
        const yearField = record.getCellValue(CONFIG.FIELDS.YEAR);
        const recordYear = yearField?.name || yearField;
        return recordYear == currentYear;
    });

    // Process bills with progress tracking
    const { exportRecords, errors } = await processWithProgress(currentYearRecords, metrics);
    
    // Show processing summary
    output.markdown(`\n✅ Processing complete: ${exportRecords.length} successful, ${errors.length} failed\n`);

    // Duplicate checking is now done in pre-flight validation using Website Bill IDs from the Bills table

    // Create export records
    let exportSuccessful = false;
    
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
            exportSuccessful = true;
            
        } catch (error) {
            output.markdown(`\n❌ Error creating export records: ${error.message}`);
            output.markdown(`\n⚠️ Export failed - no quality report will be saved`);
        }
    } else {
        output.markdown('\n⚠️ No records to export');
    }
    
    // Only save quality report if export was successful
    if (exportSuccessful) {
        await saveQualityReport(metrics);
    }
    
    // Generate and display enhanced summary
    const summary = generateEnhancedSummary(exportRecords, errors, metrics);
    output.markdown('\n' + summary);
    
    // Show completion time with GitHub link
    if (exportSuccessful) {
        output.markdown(`\n**✅ Export completed successfully at ${new Date().toLocaleString()}**`);
    } else {
        output.markdown(`\n**❌ Export failed at ${new Date().toLocaleString()}**`);
    }
    
    // Footer with GitHub information
    output.markdown(`\n---\n`);
    output.markdown(`💻 **Script Information:** Enhanced with Smart Validation & GitHub Integration | [View Source & Documentation](https://github.com/Frydafly/guttmacher-legislative-tracker/tree/main/airtable-scripts/website-export)`);
    output.markdown(`📋 **For issues or questions:** [Submit GitHub Issue](https://github.com/Frydafly/guttmacher-legislative-tracker/issues)`);
    output.markdown(`📖 **Documentation:** [README](https://github.com/Frydafly/guttmacher-legislative-tracker/blob/main/airtable-scripts/website-export/README.md)`);
}

// Execute the export
await generateWebsiteExport();