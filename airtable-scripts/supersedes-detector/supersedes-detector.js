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
        INTERNAL_NOTES: 'Internal Notes',
        
        // Optional link fields (if using manual linking)
        SUPERSEDED_BY: 'Superseded By',
        SUPERSEDES: 'Supersedes'
    },
    
    // Matching thresholds
    THRESHOLDS: {
        MIN_KEYWORD_LENGTH: 4,      // Minimum word length to consider
        MATCH_PERCENTAGE: 0.5,       // 50% of keywords must match
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
                CONFIG.FIELDS.TITLE,
                CONFIG.FIELDS.INTERNAL_NOTES
            ]
        });
        
        // Extract current record values
        const currentState = currentRecord.getCellValue(CONFIG.FIELDS.STATE);
        const currentAgency = currentRecord.getCellValue(CONFIG.FIELDS.ISSUING_AGENCY);
        const currentYear = currentRecord.getCellValue(CONFIG.FIELDS.YEAR);
        const currentTitle = currentRecord.getCellValue(CONFIG.FIELDS.TITLE);
        
        // Validation - ensure we have required fields
        if (!currentState || !currentAgency || !currentYear || !currentTitle) {
            console.log('Missing required fields for comparison');
            return;
        }
        
        // Calculate year range for efficiency
        const minYear = currentYear - CONFIG.THRESHOLDS.MAX_YEAR_DIFF;
        
        // Find candidate regulations from same state/agency
        const candidates = query.records.filter(record => {
            // Skip the current record itself
            if (record.id === currentRecord.id) return false;
            
            const recordState = record.getCellValue(CONFIG.FIELDS.STATE);
            const recordAgency = record.getCellValue(CONFIG.FIELDS.ISSUING_AGENCY);
            const recordYear = record.getCellValue(CONFIG.FIELDS.YEAR);
            
            // Must be same state
            if (recordState !== currentState) return false;
            
            // Must be same agency (comparing linked record IDs)
            if (!recordAgency || !currentAgency) return false;
            if (recordAgency[0]?.id !== currentAgency[0]?.id) return false;
            
            // Must be from an earlier year (within range)
            if (!recordYear || recordYear >= currentYear || recordYear < minYear) return false;
            
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
                matches.push({
                    record: candidate,
                    score: matchScore,
                    regId: candidate.getCellValue(CONFIG.FIELDS.REG_ID),
                    title: candidateTitle,
                    year: candidate.getCellValue(CONFIG.FIELDS.YEAR)
                });
            }
        }
        
        // Sort matches by score (best matches first) and year (most recent first)
        matches.sort((a, b) => {
            if (b.score !== a.score) return b.score - a.score;
            return b.year - a.year;
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

// Update the Internal Notes field with findings
async function updateInternalNotes(table, currentRecord, matches) {
    // Get existing notes
    const existingNotes = currentRecord.getCellValue(CONFIG.FIELDS.INTERNAL_NOTES) || '';
    
    // Create new note about potential supersedes relationships
    const timestamp = new Date().toLocaleDateString();
    let newNote = `\n--- Supersedes Detection (${timestamp}) ---\n`;
    newNote += `Potential supersedes relationships found:\n`;
    
    // Add top matches (limit to 5 to avoid clutter)
    const topMatches = matches.slice(0, 5);
    for (const match of topMatches) {
        const confidence = match.score >= 0.75 ? 'High' : match.score >= 0.6 ? 'Medium' : 'Low';
        newNote += `• ${match.regId} (${match.year}) - ${confidence} confidence\n`;
        newNote += `  "${match.title}"\n`;
    }
    
    if (matches.length > 5) {
        newNote += `• ... and ${matches.length - 5} more potential matches\n`;
    }
    
    newNote += `\nReview these and create manual links if confirmed.\n`;
    newNote += `---\n`;
    
    // Combine with existing notes
    const updatedNotes = existingNotes + newNote;
    
    // Update the record
    await table.updateRecordAsync(currentRecord.id, {
        [CONFIG.FIELDS.INTERNAL_NOTES]: updatedNotes
    });
}

// Run the detection
await detectSupersedes();