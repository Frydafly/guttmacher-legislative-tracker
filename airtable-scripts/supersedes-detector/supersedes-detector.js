// Supersedes Relationship Detector for Regulations
// Automatically identifies when newer regulations potentially replace older ones
// Runs when a regulation is created or updated

// AUTOMATION SETUP:
// When creating the automation, add an input variable:
// - Click the gear icon in the script editor
// - Add input variable named "recordId" 
// - Set value to: Record ID from trigger
// For testing: The script will use the first record in the table

// Configuration - Update these to match your field names
const CONFIG = {
    TABLES: {
        REGULATIONS: 'Regulations'  // Main regulations table
    },
    FIELDS: {
        // Identifiers
        REG_ID: 'Reg-ID',
        STATE: 'State',
        YEAR: 'Year',
        
        // Relationships
        ISSUING_AGENCY: 'Issuing Agency Link',
        TITLE: 'Title',
        
        // Output
        SUPERSEDES_DETECTION: 'Supersedes Detection',  // Create this Long Text field in Airtable
        
        // Optional link fields (if using manual linking)
        SUPERSEDED_BY: 'Superseded By',
        SUPERSEDES: 'Supersedes'
    },
    
    // Matching thresholds
    THRESHOLDS: {
        MIN_KEYWORD_LENGTH: 4,      // Minimum word length to consider
        MATCH_PERCENTAGE: 0.33,      // 33% of keywords must match (lowered from 50%)
        MAX_YEAR_DIFF: 5            // Only look back 5 years for matches
    }
};

// Main function
async function detectSupersedes() {
    const startTime = Date.now();
    
    try {
        // Get the regulations table
        const table = base.getTable(CONFIG.TABLES.REGULATIONS);
        
        // In Airtable automations, the trigger record is passed directly
        // For testing, we need to manually select a record
        let currentRecord;
        
        // Try to get record from automation trigger
        const inputConfig = input.config();
        
        // Check if we have a recordId from the trigger
        if (inputConfig.recordId) {
            // Automation mode - fetch the record using the ID from trigger
            currentRecord = await table.selectRecordAsync(inputConfig.recordId);
            console.log(`Processing regulation from trigger: ${currentRecord.name}`);
        } else if (inputConfig.record) {
            // Test mode with selected record
            currentRecord = inputConfig.record;
            console.log(`Processing test regulation: ${currentRecord.name}`);
        } else {
            // Fallback - use first record for testing
            console.log('No record provided - using first regulation for testing');
            const query = await table.selectRecordsAsync({
                maxRecords: 1
            });
            currentRecord = query.records[0];
            if (!currentRecord) {
                console.log('No records found in table');
                return;
            }
            console.log(`Testing with: ${currentRecord.name}`);
        }
        
        // Query all regulations (we'll filter in memory for better performance)
        const query = await table.selectRecordsAsync({
            fields: [
                CONFIG.FIELDS.REG_ID,
                CONFIG.FIELDS.STATE,
                CONFIG.FIELDS.YEAR,
                CONFIG.FIELDS.ISSUING_AGENCY,
                CONFIG.FIELDS.TITLE
            ]
        });
        
        // Extract current record values
        const currentState = currentRecord.getCellValue(CONFIG.FIELDS.STATE);
        const currentAgency = currentRecord.getCellValue(CONFIG.FIELDS.ISSUING_AGENCY);
        const currentYearRaw = currentRecord.getCellValue(CONFIG.FIELDS.YEAR);
        const currentYear = typeof currentYearRaw === 'object' ? currentYearRaw.name : currentYearRaw;
        const currentTitle = currentRecord.getCellValue(CONFIG.FIELDS.TITLE);
        
        // Validation - ensure we have required fields
        if (!currentState || !currentAgency || !currentYear || !currentTitle) {
            console.log('Missing required fields for comparison');
            return;
        }
        
        // Calculate year range for efficiency
        const currentYearNum = parseInt(currentYear);
        const minYear = currentYearNum - CONFIG.THRESHOLDS.MAX_YEAR_DIFF;
        
        // Find candidate regulations from same state/agency
        const candidates = query.records.filter(record => {
            // Skip the current record itself
            if (record.id === currentRecord.id) return false;
            
            const recordState = record.getCellValue(CONFIG.FIELDS.STATE);
            const recordAgency = record.getCellValue(CONFIG.FIELDS.ISSUING_AGENCY);
            const recordYearRaw = record.getCellValue(CONFIG.FIELDS.YEAR);
            const recordYear = typeof recordYearRaw === 'object' ? recordYearRaw.name : recordYearRaw;
            
            // Must be same state (handle select field objects)
            const currentStateValue = typeof currentState === 'object' ? currentState.name : currentState;
            const recordStateValue = typeof recordState === 'object' ? recordState.name : recordState;
            if (recordStateValue !== currentStateValue) return false;
            
            // Must be same agency (comparing linked record IDs)
            if (!recordAgency || !currentAgency) return false;
            if (recordAgency[0]?.id !== currentAgency[0]?.id) return false;
            
            // Must be from an earlier year (within range) - convert to numbers for comparison
            const currentYearNum = parseInt(currentYear);
            const recordYearNum = parseInt(recordYear);
            if (!recordYear || isNaN(recordYearNum) || isNaN(currentYearNum)) return false;
            if (recordYearNum >= currentYearNum || recordYearNum < minYear) return false;
            
            return true;
        });
        
        console.log(`Found ${candidates.length} candidate regulations to check`);
        
        // Extract keywords from current title
        const keywords = extractKeywords(currentTitle);
        
        if (keywords.length === 0) {
            console.log('No valid keywords found in title');
            return;
        }
        
        // Check title similarity for each candidate
        const matches = [];
        
        for (const candidate of candidates) {
            const candidateTitle = candidate.getCellValue(CONFIG.FIELDS.TITLE);
            if (!candidateTitle) continue;
            
            const matchScore = calculateTitleMatch(keywords, candidateTitle);
            
            if (matchScore >= CONFIG.THRESHOLDS.MATCH_PERCENTAGE) {
                const candidateYear = candidate.getCellValue(CONFIG.FIELDS.YEAR);
                // Handle different field types: select field (object), number, or string
                let yearValue;
                if (typeof candidateYear === 'object' && candidateYear !== null) {
                    yearValue = candidateYear.name || candidateYear;
                } else {
                    yearValue = candidateYear;
                }
                matches.push({
                    record: candidate,
                    score: matchScore,
                    regId: candidate.getCellValue(CONFIG.FIELDS.REG_ID),
                    title: candidateTitle,
                    year: yearValue
                });
            }
        }
        
        // Sort matches by score (best matches first) and year (most recent first)
        matches.sort((a, b) => {
            if (b.score !== a.score) return b.score - a.score;
            // Convert years to numbers for comparison
            const yearA = parseInt(a.year);
            const yearB = parseInt(b.year);
            return yearB - yearA;
        });
        
        // Update Internal Notes with findings
        if (matches.length > 0) {
            await updateInternalNotes(table, currentRecord, matches);
            console.log(`Found ${matches.length} potential supersedes relationships`);
        } else {
            console.log('No potential supersedes relationships found');
        }
        
        // Log execution time
        const executionTime = (Date.now() - startTime) / 1000;
        console.log(`Script completed in ${executionTime.toFixed(2)} seconds`);
        
    } catch (error) {
        console.error('Error in supersedes detection:', error);
        throw error;
    }
}

// Extract meaningful keywords from a title
function extractKeywords(title) {
    if (!title) return [];
    
    // Convert to lowercase and extract words
    const words = title.toLowerCase().match(/\b[a-z]+\b/g) || [];
    
    // Filter out short words and common stopwords
    const stopwords = [
        'the', 'and', 'or', 'of', 'to', 'for', 'in', 'on', 'at', 'by', 'with',
        'from', 'into', 'through', 'during', 'including', 'until', 'against',
        'among', 'throughout', 'despite', 'towards', 'upon', 'concerning',
        'rule', 'rules', 'regulation', 'regulations', 'emergency', 'temporary'
    ];
    
    return words.filter(word => 
        word.length >= CONFIG.THRESHOLDS.MIN_KEYWORD_LENGTH && 
        !stopwords.includes(word)
    );
}

// Calculate how well keywords match a candidate title
function calculateTitleMatch(keywords, candidateTitle) {
    if (!candidateTitle || keywords.length === 0) return 0;
    
    const candidateLower = candidateTitle.toLowerCase();
    let matchCount = 0;
    
    for (const keyword of keywords) {
        // Check if keyword appears in candidate title
        if (candidateLower.includes(keyword)) {
            matchCount++;
        }
    }
    
    // Return percentage of keywords that matched
    return matchCount / keywords.length;
}

// Update the Supersedes Detection field with findings
async function updateInternalNotes(table, currentRecord, matches) {
    // Create detection report
    const timestamp = new Date().toLocaleDateString();
    let detectionReport = `Last checked: ${timestamp}\n\n`;
    
    detectionReport += `Found ${matches.length} potential supersedes relationship${matches.length !== 1 ? 's' : ''}:\n\n`;
    
    // Add all matches (or limit if too many)
    const maxToShow = 10;
    const matchesToShow = matches.slice(0, maxToShow);
    
    for (const match of matchesToShow) {
        const confidence = match.score >= 0.75 ? 'HIGH' : match.score >= 0.6 ? 'MEDIUM' : 'LOW';
        detectionReport += `${confidence} CONFIDENCE:\n`;
        detectionReport += `• ${match.regId} (Year: ${match.year})\n`;
        detectionReport += `  Title: "${match.title}"\n`;
        detectionReport += `  Match Score: ${(match.score * 100).toFixed(0)}%\n\n`;
    }
    
    if (matches.length > maxToShow) {
        detectionReport += `... and ${matches.length - maxToShow} more potential matches\n\n`;
    }
    
    detectionReport += `Action: Review these suggestions and create manual links in the "Superseded By" or "Supersedes" fields if confirmed.`;
    
    // Update the dedicated field (replaces entirely each time)
    await table.updateRecordAsync(currentRecord.id, {
        [CONFIG.FIELDS.SUPERSEDES_DETECTION]: detectionReport
    });
}

// Run the detection
await detectSupersedes();