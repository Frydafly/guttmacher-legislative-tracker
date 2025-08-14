#!/usr/bin/env python3
"""
Transform regulations CSV to EXACTLY match the Airtable Regulations table structure
Based on actual export from Airtable
"""

import csv
from datetime import datetime

def parse_date(date_str):
    """Convert MM/DD/YYYY to YYYY-MM-DD for Airtable"""
    if not date_str or date_str.strip() == '':
        return ''
    try:
        # Handle MM/DD/YYYY format
        date_obj = datetime.strptime(date_str.strip(), '%m/%d/%Y')
        return date_obj.strftime('%Y-%m-%d')
    except:
        try:
            # Handle YYYY-MM-DD format (already correct)
            date_obj = datetime.strptime(date_str.strip(), '%Y-%m-%d')
            return date_str.strip()
        except:
            return ''

def parse_status_from_text(status_text):
    """Extract status from Last Status Date text"""
    if not status_text:
        return "Unknown"
    
    status_lower = status_text.lower()
    
    if "rule adoption" in status_lower or "adopted" in status_lower:
        return "Adopted"
    elif "emergency" in status_lower:
        return "Emergency Adopted"
    elif "effective" in status_lower:
        return "Effective"
    elif "comment" in status_lower:
        return "Comment Period"
    elif "proposed" in status_lower:
        return "Proposed"
    elif "withdrawn" in status_lower:
        return "Withdrawn"
    elif "review" in status_lower:
        return "Under Review"
    else:
        return "Under Review"

def collect_specific_policies(row):
    """
    Collect all specific policy values from the CSV
    ALL policy fields can contain specific values, not just yes/no
    Returns comma-separated list for Specific Policies (access) field
    """
    policies = []
    
    # Process each policy field - they can contain specific values OR yes/no
    policy_fields = ['Abortion', 'AbortionBans', 'FamilyPlanning', 'Insurance', 'Minors', 'Providers', 'Pregnancy']
    
    for field in policy_fields:
        value = row.get(field, '').strip()
        
        # Skip empty or 'no' values
        if not value or value.lower() in ['no', '']:
            continue
            
        # If it's 'yes', add the field name as the policy
        if value.lower() == 'yes':
            # Use proper names
            if field == 'AbortionBans':
                policies.append('Abortion Bans')
            elif field == 'FamilyPlanning':
                policies.append('Family Planning')
            else:
                policies.append(field)
        else:
            # It contains specific policy values (like "STIs", "Misc", etc.)
            # Split by semicolon for multiple values
            parts = [p.strip() for p in value.split(';')]
            # Remove duplicates while preserving order
            unique_parts = list(dict.fromkeys(parts))
            for part in unique_parts:
                if part and part.lower() not in ['yes', 'no', '']:
                    policies.append(part)
    
    return ', '.join(policies) if policies else ''

def collect_policy_categories(row):
    """
    Map fields to Policy Categories (broader categories)
    Categories are derived from which fields have values
    """
    categories = []
    
    # Check each field - if it has ANY value (not just yes), include the category
    if row.get('Abortion', '').strip() and row.get('Abortion', '').strip().lower() not in ['no', '']:
        categories.append('Abortion')
    
    if row.get('AbortionBans', '').strip() and row.get('AbortionBans', '').strip().lower() not in ['no', '']:
        categories.append('Abortion')
    
    if row.get('FamilyPlanning', '').strip() and row.get('FamilyPlanning', '').strip().lower() not in ['no', '']:
        categories.append('Family Planning')
    
    if row.get('Insurance', '').strip() and row.get('Insurance', '').strip().lower() not in ['no', '']:
        categories.append('Insurance')
    
    if row.get('Minors', '').strip() and row.get('Minors', '').strip().lower() not in ['no', '']:
        categories.append('Minors')
    
    if row.get('Pregnancy', '').strip() and row.get('Pregnancy', '').strip().lower() not in ['no', '']:
        categories.append('Pregnancy')
    
    if row.get('Providers', '').strip() and row.get('Providers', '').strip().lower() not in ['no', '']:
        categories.append('Providers')
    
    # Remove duplicates while preserving order
    categories = list(dict.fromkeys(categories))
    
    return ', '.join(categories) if categories else ''

def transform_to_airtable_format():
    """Transform all regulations to match exact Airtable structure"""
    input_file = "/Users/frydaguedes/Projects/guttmacher-legislative-tracker/regulations-tracking/2025 tracked regs.csv"
    output_file = "/Users/frydaguedes/Projects/guttmacher-legislative-tracker/regulations-tracking/regulations_airtable_import.csv"
    
    with open(input_file, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        
        with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            # Exact field names from Airtable export
            fieldnames = [
                'Reg-ID', 'State', 'Number', 'Year', 'Title', 'Description',
                'Current Status', 'History', 'StateNet History', 'Last Action Date',
                'Introduction Date', 'Comment Period End', 'Adopted Date',
                'Emergency Adopted Date', 'Effective Date', 'Expiration Date',
                'Specific Policies Record Link',
                'Categories (from Specific Policies Record Link)',
                'Subcategories (from Specific Policies Record Link)',
                'Headers (from Specific Policies Record Link)',
                'Specific Policies (from Specific Policies Record Link)',
                'Positive/Neutral/Restrictive (from Specific Policies Record Link)',
                'Category Intent (from Specific Policies Record Link)',
                'Specific Policies (access)', 'Policy Categories (Access)',
                'Issuing Agency Link', 'Agency Type Lookup',
                'State Reg ID', 'Citation', 'Contact', 'StateNet Link',
                'Related Bills', 'Legal Status', 'Review Status',
                'Website Blurb', 'Internal Notes', 'StateNet Regulations Import',
                'Import Date', 'Last Updated', 'Newly Tracked',
                'Change in Status', 'Last Status Date Text', 'Agency Name (raw)'
            ]
            
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in reader:
                # Get basic fields
                state = row['Jurisdiction']
                number = row['Number']
                year = row['Year']
                
                # Generate Reg-ID
                reg_id = f"{state}-REG-{number}-{year}"
                
                # Parse status
                current_status = parse_status_from_text(row['Last Status Date'])
                
                # Parse Last Action Date from the status text
                last_action_date = ''
                if row['Last Status Date']:
                    # Try to extract date from beginning of status text
                    parts = row['Last Status Date'].split(' - ')
                    if parts and '/' in parts[0]:
                        last_action_date = parse_date(parts[0])
                
                # Collect policies
                specific_policies = collect_specific_policies(row)
                policy_categories = collect_policy_categories(row)
                
                # Determine Legal Status
                legal_status = ''
                if current_status in ["Adopted", "Effective", "Emergency Adopted"]:
                    legal_status = "In Effect"
                elif current_status == "Proposed":
                    legal_status = "Pending"
                elif current_status == "Comment Period":
                    legal_status = "Comment Period"
                
                # Handle checkboxes - use "checked" for true, empty for false
                newly_tracked = "checked" if row.get('Newly Tracked', '').lower() == 'yes' else ''
                change_in_status = "checked" if row.get('Change in Status', '').lower() == 'yes' else ''
                
                transformed = {
                    'Reg-ID': reg_id,
                    'State': state,
                    'Number': number,
                    'Year': year,
                    'Title': row['Title'],
                    'Description': row['Summary'],
                    'Current Status': current_status,
                    'History': '',  # Will be populated manually
                    'StateNet History': row['Last Status Date'],
                    'Last Action Date': last_action_date,
                    'Introduction Date': parse_date(row['Intro Date']),
                    'Comment Period End': parse_date(row['Qualification Date']),
                    'Adopted Date': parse_date(row['Adopted Date']),
                    'Emergency Adopted Date': parse_date(row['Emergency Adopted Date']),
                    'Effective Date': parse_date(row['Effective Date']),
                    'Expiration Date': '',  # Not in source data
                    'Specific Policies Record Link': '',  # Will be linked in Airtable
                    'Categories (from Specific Policies Record Link)': '',  # Lookup field
                    'Subcategories (from Specific Policies Record Link)': '',  # Lookup field
                    'Headers (from Specific Policies Record Link)': '',  # Lookup field
                    'Specific Policies (from Specific Policies Record Link)': '',  # Lookup field
                    'Positive/Neutral/Restrictive (from Specific Policies Record Link)': '',  # Lookup field
                    'Category Intent (from Specific Policies Record Link)': '',  # Lookup field
                    'Specific Policies (access)': specific_policies,
                    'Policy Categories (Access)': policy_categories,
                    'Issuing Agency Link': '',  # Will be linked in Airtable
                    'Agency Type Lookup': '',  # Will be looked up from agency
                    'State Reg ID': row['State ID'],
                    'Citation': row['Citation'],
                    'Contact': row['Contact'],
                    'StateNet Link': row['Links'],
                    'Related Bills': '',  # Not in source data
                    'Legal Status': legal_status,
                    'Review Status': 'Needs Review',
                    'Website Blurb': '',  # Will be populated if needed
                    'Internal Notes': '',  # Will be populated manually
                    'StateNet Regulations Import': '',  # Will be linked after import
                    'Import Date': '',  # Will be auto-populated
                    'Last Updated': '',  # Will be auto-populated
                    'Newly Tracked': newly_tracked,
                    'Change in Status': change_in_status,
                    'Last Status Date Text': row['Last Status Date'],
                    'Agency Name (raw)': row['Author/Source']
                }
                
                writer.writerow(transformed)
    
    # Print summary
    print(f"✅ Transformed all regulations to: {output_file}")
    print("\nThis CSV exactly matches your Airtable structure with:")
    print("- All fields in the correct order")
    print("- Proper date formatting (YYYY-MM-DD)")
    print("- Checkboxes as 'checked' or empty")
    print("- Specific policies and categories properly extracted")
    print("- Legal status determined from current status")
    
    # Count records and show summary
    count = 0
    with open(output_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        policy_counts = {}
        status_counts = {}
        
        for row in reader:
            count += 1
            
            # Count policies
            if row['Specific Policies (access)']:
                for policy in row['Specific Policies (access)'].split(','):
                    policy = policy.strip()
                    policy_counts[policy] = policy_counts.get(policy, 0) + 1
            
            # Count statuses
            status = row['Current Status']
            status_counts[status] = status_counts.get(status, 0) + 1
    
    print(f"\n📊 Import Summary:")
    print(f"Total regulations: {count}")
    print(f"\nStatus distribution:")
    for status, cnt in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {status}: {cnt}")
    
    print(f"\nTop policies covered:")
    for policy, cnt in sorted(policy_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {policy}: {cnt} regulations")

if __name__ == "__main__":
    transform_to_airtable_format()