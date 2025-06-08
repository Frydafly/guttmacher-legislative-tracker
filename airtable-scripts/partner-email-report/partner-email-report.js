// Get records from the Partner Email Report view
const billsTable = base.getTable('Bills');
const emailView = billsTable.getView('Partner Email Report');

try {
    const queryResult = await emailView.selectRecordsAsync();
    console.log(`Found ${queryResult.records.length} records in the view`);
    
    // Organize bills by intent
    const positiveIntentBills = [];
    const restrictiveIntentBills = [];
    
    // Calculate date from two weeks ago
    const twoWeeksAgo = new Date();
    twoWeeksAgo.setDate(twoWeeksAgo.getDate() - 14);
    
    console.log(`Checking for actions since: ${twoWeeksAgo.toISOString().split('T')[0]}`);
    
    for (const record of queryResult.records) {
        try {
            // Get field values with proper object handling
            const state = record.getCellValue('State')?.name || 'Unknown';
            const billType = record.getCellValue('BillType')?.name || '';
            const billNumber = record.getCellValue('BillNumber') || '';
            
            const billId = `${state} ${billType} ${billNumber}`;
            console.log(`Processing bill: ${billId}`);
            
            // Get all date fields and check which ones have recent activity
            const passedFirstChamberDate = record.getCellValue('Passed 1 Chamber Date');
            const passedLegislatureDate = record.getCellValue('Passed Legislature Date');
            const enactedDate = record.getCellValue('Enacted Date');
            const vetoedDate = record.getCellValue('Vetoed Date');
            
            // Determine what action occurred in the last two weeks
            let recentActionDate = null;
            let statusText = '';
            
            if (enactedDate && new Date(enactedDate) >= twoWeeksAgo) {
                statusText = 'was enacted';
                recentActionDate = enactedDate;
                console.log(`Bill was enacted on ${recentActionDate}`);
            } else if (vetoedDate && new Date(vetoedDate) >= twoWeeksAgo) {
                statusText = 'was vetoed';
                recentActionDate = vetoedDate;
                console.log(`Bill was vetoed on ${recentActionDate}`);
            } else if (passedLegislatureDate && new Date(passedLegislatureDate) >= twoWeeksAgo) {
                statusText = 'passed the legislature';
                recentActionDate = passedLegislatureDate;
                console.log(`Bill passed legislature on ${recentActionDate}`);
            } else if (passedFirstChamberDate && new Date(passedFirstChamberDate) >= twoWeeksAgo) {
                statusText = 'passed the first chamber';
                recentActionDate = passedFirstChamberDate;
                console.log(`Bill passed first chamber on ${recentActionDate}`);
            }
            
            // Skip if no recent action
            if (!recentActionDate) {
                console.log(`No recent actions for bill ${billId}`);
                continue;
            }
            
            // Format the date properly (MM/DD/YYYY)
            const date = new Date(recentActionDate);
            const month = (date.getMonth() + 1).toString().padStart(2, '0');
            const day = date.getDate().toString().padStart(2, '0');
            const formattedDate = `${month}/${day}`;
            
            // Get description to use if Website Blurb is empty
            const websiteBlurb = record.getCellValue('Website Blurb') || 
                                record.getCellValue('Description') || 
                                'No description available';
            
            // Check Intent - use Intent field which is already an array of strings
            const intent = record.getCellValue('Intent') || [];  
            
            // Build the bill entry
            const billEntry = `${billId} ${statusText} on ${formattedDate}.\n${websiteBlurb}`;
            
            // Check intent - your Intent field contains strings like "Positive"
            const isPositive = intent.includes('Positive') || intent.includes('Protective');
            const isRestrictive = intent.includes('Restrictive');
            
            // Sort bills by intent
            if (isPositive) {
                positiveIntentBills.push(billEntry);
            } else if (isRestrictive) {
                restrictiveIntentBills.push(billEntry);
            }
        } catch (recordError) {
            console.log(`Error processing record: ${recordError.message}`);
        }
    }
    
    console.log(`Positive bills with recent actions: ${positiveIntentBills.length}`);
    console.log(`Restrictive bills with recent actions: ${restrictiveIntentBills.length}`);
    
    // If no bills have recent activity, provide a message
    if (positiveIntentBills.length === 0 && restrictiveIntentBills.length === 0) {
        output.set('formattedEmailBody', 'No legislative activity to report in the past two weeks.');
        output.set('formattedHtmlEmail', '<html><body><p>No legislative activity to report in the past two weeks.</p></body></html>');
        return;
    }
    
    // Build email body
    let emailBody = 'Bi-Weekly Legislative Update\n\n';
    
    if (positiveIntentBills.length > 0) {
        emailBody += '*Positive*\n\n';
        emailBody += positiveIntentBills.join('\n\n');
        emailBody += '\n\n';
    }
    
    if (restrictiveIntentBills.length > 0) {
        emailBody += '*Restrictive*\n\n';
        emailBody += restrictiveIntentBills.join('\n\n');
    }
    
    // Set output for use in the email step
    output.set('formattedEmailBody', emailBody);
    
    // Also create HTML version with underlining for the first line
    let htmlBody = '<html><body>';
    
    if (positiveIntentBills.length > 0) {
        htmlBody += '<p><strong><em>Positive</em></strong></p>';
        
        positiveIntentBills.forEach(entry => {
            const lines = entry.split('\n');
            const firstLine = lines[0];
            const rest = lines.slice(1).join('<br>');
            htmlBody += `<p><u>${firstLine}</u><br>${rest}</p>`;
        });
    }
    
    if (restrictiveIntentBills.length > 0) {
        htmlBody += '<p><strong><em>Restrictive</em></strong></p>';
        
        restrictiveIntentBills.forEach(entry => {
            const lines = entry.split('\n');
            const firstLine = lines[0];
            const rest = lines.slice(1).join('<br>');
            htmlBody += `<p><u>${firstLine}</u><br>${rest}</p>`;
        });
    }
    
    htmlBody += '</body></html>';
    output.set('formattedHtmlEmail', htmlBody);
    
} catch (error) {
    console.log(`Error: ${error.message}`);
}