// Supersedes Relationship Detector - BULK RUN VERSION
// One-time script to process ALL existing regulations
// Run this manually to detect supersedes relationships for all records

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
    },
    
    // Matching thresholds
    THRESHOLDS: {
        MIN_KEYWORD_LENGTH: 4,      // Minimum word length to consider
        MATCH_PERCENTAGE: 0.33,      // 33% of keywords must match (lowered from 50%)
        MAX_YEAR_DIFF: 5            // Only look back 5 years for matches
    }
};

// Main bulk processing function
async function bulkDetectSupersedes() {
    const startTime = Date.now();
    let processedCount = 0;
    let matchesFound = 0;
    
    try {
        console.log('🚀 Starting bulk supersedes detection...');
        
        // Get the regulations table
        const table = base.getTable(CONFIG.TABLES.REGULATIONS);
        
        // Query all regulations
        console.log('Loading all regulations...');
        const query = await table.selectRecordsAsync({
            fields: [
                CONFIG.FIELDS.REG_ID,
                CONFIG.FIELDS.STATE,
                CONFIG.FIELDS.YEAR,
                CONFIG.FIELDS.ISSUING_AGENCY,
                CONFIG.FIELDS.TITLE
            ]
        });
        
        console.log(`Found ${query.records.length} total regulations to process`);
        
        // Get some statistics first
        const stats = {
            byState: {},
            byYear: {},
            byAgency: {}
        };
        
        for (const record of query.records) {
            const state = record.getCellValue(CONFIG.FIELDS.STATE);
            const year = record.getCellValue(CONFIG.FIELDS.YEAR);
            const agency = record.getCellValue(CONFIG.FIELDS.ISSUING_AGENCY);
            
            // State might be an object if it's a select field
            const stateValue = typeof state === 'object' ? state.name : state;
            if (stateValue) stats.byState[stateValue] = (stats.byState[stateValue] || 0) + 1;
            
            // Year might be an object too
            const yearValue = typeof year === 'object' ? year.name : year;
            if (yearValue) stats.byYear[yearValue] = (stats.byYear[yearValue] || 0) + 1;
            
            if (agency && agency[0]) {
                const agencyName = agency[0].name;
                stats.byAgency[agencyName] = (stats.byAgency[agencyName] || 0) + 1;
            }
        }
        
        const multiRegAgencies = Object.entries(stats.byAgency).filter(([k,v]) => v >= 2);
        
        // Build overview as single string
        let overview = '📊 Dataset Overview:\n';
        overview += `States with regulations: ${Object.keys(stats.byState).length}\n`;
        overview += `States: ${Object.keys(stats.byState).sort().join(', ')}\n`;
        overview += `Years covered: ${Object.keys(stats.byYear).sort((a,b) => a-b).join(', ')}\n`;
        overview += `Unique agencies: ${Object.keys(stats.byAgency).length}\n`;
        overview += `Agencies with 2+ regulations: ${multiRegAgencies.length}\n`;
        
        if (multiRegAgencies.length > 0) {
            overview += '\nTop agencies by regulation count:\n';
            multiRegAgencies
                .sort((a, b) => b[1] - a[1])
                .slice(0, 5)
                .forEach(([agency, count]) => {
                    overview += `  - ${agency}: ${count} regulations\n`;
                });
        }
        
        console.log(overview);
        
        // Debug: Check if those multi-regulation agencies span multiple years
        let yearDiversityCheck = '🔍 Checking for year diversity in top agencies:\n';
        for (const [agencyName, count] of multiRegAgencies.slice(0, 3)) {
            const agencyRegs = query.records.filter(r => {
                const agency = r.getCellValue(CONFIG.FIELDS.ISSUING_AGENCY);
                return agency && agency[0] && agency[0].name === agencyName;
            });
            const years = new Set();
            const states = new Set();
            const agencyIds = new Set();
            agencyRegs.forEach(r => {
                const year = r.getCellValue(CONFIG.FIELDS.YEAR);
                const state = r.getCellValue(CONFIG.FIELDS.STATE);
                const agency = r.getCellValue(CONFIG.FIELDS.ISSUING_AGENCY);
                const yearValue = typeof year === 'object' ? year.name : year;
                const stateValue = typeof state === 'object' ? state.name : state;
                if (yearValue) years.add(yearValue);
                if (stateValue) states.add(stateValue);
                if (agency && agency[0]) agencyIds.add(agency[0].id);
            });
            yearDiversityCheck += `  ${agencyName}: ${count} regs across ${years.size} year(s) (${Array.from(years).sort().join(', ')}) in ${states.size} state(s) (${Array.from(states).join(', ')})\n`;
            if (agencyIds.size > 1) {
                yearDiversityCheck += `    ⚠️  Same name but ${agencyIds.size} different agency records!\n`;
            }
        }
        console.log(yearDiversityCheck);
        
        // Check for same state+agency combinations with multiple years
        const stateAgencyCombos = {};
        for (const record of query.records) {
            const state = record.getCellValue(CONFIG.FIELDS.STATE);
            const agency = record.getCellValue(CONFIG.FIELDS.ISSUING_AGENCY);
            const year = record.getCellValue(CONFIG.FIELDS.YEAR);
            
            if (state && agency && agency[0] && year) {
                const stateValue = typeof state === 'object' ? state.name : state;
                const yearValue = typeof year === 'object' ? year.name : year;
                const key = `${stateValue}|${agency[0].id}`;
                
                if (!stateAgencyCombos[key]) {
                    stateAgencyCombos[key] = {
                        state: stateValue,
                        agencyName: agency[0].name,
                        years: new Set(),
                        count: 0
                    };
                }
                stateAgencyCombos[key].years.add(yearValue);
                stateAgencyCombos[key].count++;
            }
        }
        
        const multiYearCombos = Object.values(stateAgencyCombos)
            .filter(combo => combo.years.size > 1)
            .sort((a, b) => b.count - a.count);
        
        let comboAnalysis = '🎯 Looking for state+agency combinations with multiple years:\n';
        if (multiYearCombos.length > 0) {
            comboAnalysis += `Found ${multiYearCombos.length} state+agency combinations with regulations across multiple years:\n`;
            multiYearCombos.slice(0, 5).forEach(combo => {
                comboAnalysis += `  ${combo.state} - ${combo.agencyName}: ${combo.count} regs across years ${Array.from(combo.years).sort().join(', ')}\n`;
            });
        } else {
            comboAnalysis += '  ❌ No state+agency combinations have regulations from different years\n';
            comboAnalysis += '  This explains why no supersedes relationships are found!';
        }
        console.log(comboAnalysis);
        
        // Track why no matches are found
        let debugInfo = {
            noTitle: 0,
            noKeywords: 0,
            noCandidates: 0,
            lowMatchScore: []
        };
        
        // Process each regulation
        for (const currentRecord of query.records) {
            processedCount++;
            
            // Show progress every 10 records
            if (processedCount % 10 === 0) {
                console.log(`Progress: ${processedCount}/${query.records.length} processed...`);
            }
            
            // Extract current record values
            const currentState = currentRecord.getCellValue(CONFIG.FIELDS.STATE);
            const currentAgency = currentRecord.getCellValue(CONFIG.FIELDS.ISSUING_AGENCY);
            const currentYearRaw = currentRecord.getCellValue(CONFIG.FIELDS.YEAR);
            const currentYear = typeof currentYearRaw === 'object' ? currentYearRaw.name : currentYearRaw;
            const currentTitle = currentRecord.getCellValue(CONFIG.FIELDS.TITLE);
            
            // Skip if missing required fields
            if (!currentState || !currentAgency || !currentYear || !currentTitle) {
                if (!currentTitle) debugInfo.noTitle++;
                continue;
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
            
            if (candidates.length === 0) {
                debugInfo.noCandidates++;
                continue;
            }
            
            // Extract keywords from current title
            const keywords = extractKeywords(currentTitle);
            
            if (keywords.length === 0) {
                debugInfo.noKeywords++;
                continue;
            }
            
            // Check title similarity for each candidate
            const matches = [];
            
            for (const candidate of candidates) {
                const candidateTitle = candidate.getCellValue(CONFIG.FIELDS.TITLE);
                if (!candidateTitle) continue;
                
                const matchScore = calculateTitleMatch(keywords, candidateTitle);
                
                if (matchScore >= CONFIG.THRESHOLDS.MATCH_PERCENTAGE) {
                    const candidateYear = candidate.getCellValue(CONFIG.FIELDS.YEAR);
                    const yearValue = typeof candidateYear === 'object' ? candidateYear.name : candidateYear;
                    matches.push({
                        record: candidate,
                        score: matchScore,
                        regId: candidate.getCellValue(CONFIG.FIELDS.REG_ID),
                        title: candidateTitle,
                        year: yearValue
                    });
                }
            }
            
            // Update Internal Notes with findings
            if (matches.length > 0) {
                matchesFound++;
                await updateInternalNotes(table, currentRecord, matches);
                console.log(`✅ Found ${matches.length} matches for ${currentRecord.getCellValue(CONFIG.FIELDS.REG_ID)}`);
            } else if (candidates.length > 0) {
                // Track why there were no matches despite having candidates
                const bestScore = Math.max(...candidates.map(c => {
                    const candidateTitle = c.getCellValue(CONFIG.FIELDS.TITLE);
                    return candidateTitle ? calculateTitleMatch(keywords, candidateTitle) : 0;
                }));
                if (bestScore > 0) {
                    debugInfo.lowMatchScore.push({
                        regId: currentRecord.getCellValue(CONFIG.FIELDS.REG_ID),
                        bestScore: (bestScore * 100).toFixed(0) + '%',
                        candidateCount: candidates.length
                    });
                }
            }
        }
        
        // Debug report
        let debugReport = '\n🔍 Debug Analysis:\n';
        debugReport += `Records with no title: ${debugInfo.noTitle}\n`;
        debugReport += `Records with no extractable keywords: ${debugInfo.noKeywords}\n`;
        debugReport += `Records with no candidates from earlier years: ${debugInfo.noCandidates}\n`;
        
        if (debugInfo.lowMatchScore.length > 0) {
            debugReport += `\nRecords with candidates but match score < 50%:\n`;
            debugInfo.lowMatchScore.slice(0, 5).forEach(item => {
                debugReport += `  ${item.regId}: Best score ${item.bestScore} from ${item.candidateCount} candidates\n`;
            });
            if (debugInfo.lowMatchScore.length > 5) {
                debugReport += `  ... and ${debugInfo.lowMatchScore.length - 5} more\n`;
            }
        }
        console.log(debugReport);
        
        // Final report
        const executionTime = (Date.now() - startTime) / 1000;
        const finalReport = `
=================================
📊 BULK PROCESSING COMPLETE
=================================
Total regulations processed: ${processedCount}
Regulations with matches found: ${matchesFound}
Execution time: ${executionTime.toFixed(2)} seconds
=================================`;
        console.log(finalReport);
        
    } catch (error) {
        console.error('Error in bulk supersedes detection:', error);
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
    
    // Sort matches by score and year
    const sortedMatches = matches.sort((a, b) => {
        if (b.score !== a.score) return b.score - a.score;
        return b.year - a.year;
    });
    
    // Add all matches (or limit if too many)
    const maxToShow = 10;
    const matchesToShow = sortedMatches.slice(0, maxToShow);
    
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

// Run the bulk detection
console.log('Starting bulk supersedes detection for all regulations...');
console.log('This may take several minutes depending on the number of records.\n');
await bulkDetectSupersedes();