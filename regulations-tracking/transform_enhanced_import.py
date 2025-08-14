#!/usr/bin/env python3
"""
Enhanced transform for regulations - adds missing valuable fields from proposal
Includes: Regulation Type, Expiration Date calculation, Enhanced Legal Status
"""

import csv
from datetime import datetime, timedelta

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

def parse_date_object(date_str):
    """Parse date string to datetime object for calculations"""
    if not date_str or date_str.strip() == '':
        return None
    try:
        return datetime.strptime(date_str.strip(), '%m/%d/%Y')
    except:
        try:
            return datetime.strptime(date_str.strip(), '%Y-%m-%d')
        except:
            return None

def determine_regulation_type(row):
    """Determine regulation type based on data patterns"""
    
    # Check for emergency adoption
    if row.get('Emergency Adopted Date', '').strip():
        return 'Emergency Rule'
    
    # Check status text for clues
    status_text = row.get('Last Status Date', '').lower()
    
    if 'emergency' in status_text:
        return 'Emergency Rule'
    elif 'temporary' in status_text or 'temp' in status_text:
        return 'Temporary Rule'
    elif 'guidance' in status_text or 'bulletin' in status_text:
        return 'Guidance/Bulletin'
    else:
        return 'Standard Rulemaking'

def calculate_expiration_date(row):
    """Calculate expiration date for emergency/temporary rules (typically 180 days)"""
    
    reg_type = determine_regulation_type(row)
    
    if reg_type == 'Emergency Rule':
        # Try emergency adopted date first
        emergency_date = parse_date_object(row.get('Emergency Adopted Date', ''))
        if emergency_date:
            # Emergency rules typically expire in 180 days
            expiration = emergency_date + timedelta(days=180)
            return expiration.strftime('%Y-%m-%d')
        
        # Fall back to effective date
        effective_date = parse_date_object(row.get('Effective Date', ''))
        if effective_date:
            expiration = effective_date + timedelta(days=180)
            return expiration.strftime('%Y-%m-%d')
    
    elif reg_type == 'Temporary Rule':
        # Temporary rules might have different expiration (90 days is common)
        effective_date = parse_date_object(row.get('Effective Date', ''))
        if effective_date:
            expiration = effective_date + timedelta(days=90)
            return expiration.strftime('%Y-%m-%d')
    
    return ''

def parse_enhanced_legal_status(row, current_status):
    """Determine more granular legal status"""
    
    status_text = row.get('Last Status Date', '').lower()
    
    # Check for legal challenges or court actions
    if any(word in status_text for word in ['enjoined', 'injunction', 'blocked', 'stayed']):
        return 'Enjoined'
    elif any(word in status_text for word in ['challenge', 'lawsuit', 'litigation', 'court']):
        return 'Under Challenge'
    elif any(word in status_text for word in ['vacated', 'struck', 'invalid', 'void']):
        return 'Vacated'
    elif any(word in status_text for word in ['expired', 'lapsed', 'ended']):
        return 'Expired'
    
    # Check expiration for emergency rules
    reg_type = determine_regulation_type(row)
    if reg_type == 'Emergency Rule':
        expiration = calculate_expiration_date(row)
        if expiration:
            exp_date = datetime.strptime(expiration, '%Y-%m-%d')
            if exp_date < datetime.now():
                return 'Expired'
    
    # Default based on current status
    if current_status in ["Adopted", "Effective", "Emergency Adopted"]:
        return "In Effect"
    elif current_status == "Proposed":
        return "Pending"
    elif current_status == "Comment Period":
        return "Comment Period"
    elif current_status == "Withdrawn":
        return "Withdrawn"
    else:
        return "Under Review"

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

def transform_to_enhanced_format():
    """Transform all regulations with enhanced fields"""
    input_file = "/Users/frydaguedes/Projects/guttmacher-legislative-tracker/regulations-tracking/2025 tracked regs.csv"
    output_file = "/Users/frydaguedes/Projects/guttmacher-legislative-tracker/regulations-tracking/regulations_enhanced_import.csv"
    
    with open(input_file, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        
        with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            # Enhanced field names including new fields from proposal
            fieldnames = [
                'Reg-ID', 'State', 'Number', 'Year', 'Title', 'Description',
                'Regulation Type',  # NEW: Added from proposal
                'Current Status', 'History', 'StateNet History', 'Last Action Date',
                'Introduction Date', 'Comment Period End', 'Adopted Date',
                'Emergency Adopted Date', 'Effective Date', 
                'Expiration Date',  # ENHANCED: Calculate for emergency rules
                'Intent (access)',  # Added for future manual assignment
                'Specific Policies Record Link',
                'Categories (from Specific Policies Record Link)',
                'Subcategories (from Specific Policies Record Link)',
                'Headers (from Specific Policies Record Link)',
                'Specific Policies (from Specific Policies Record Link)',
                'Positive/Neutral/Restrictive (from Specific Policies Record Link)',
                'Category Intent (from Specific Policies Record Link)',
                'Specific Policies (access)', 'Policy Categories (Access)',
                'Issuing Agency Link', 'Agency Type (from Issuing Agency Link)',
                'Priority Level (from Issuing Agency Link)',
                'Parent Agency (from Issuing Agency Link)',
                'State Reg ID', 'Citation', 'Contact', 'StateNet Link',
                'Related Bills',  # For future linking
                'Supersedes',  # NEW: From proposal
                'Superseded By',  # NEW: From proposal
                'Legal Status',  # ENHANCED: More granular
                'Review Status',
                'Website Blurb', 'Internal Notes', 'StateNet Regulations Import',
                'Import Date', 'Last Updated', 'Last Updated By',
                'Newly Tracked', 'Change in Status', 'Last Status Date Text'
            ]
            
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            
            # Track statistics
            reg_type_counts = {}
            legal_status_counts = {}
            
            for row in reader:
                # Get basic fields
                state = row['Jurisdiction']
                number = row['Number']
                year = row['Year']
                
                # Generate Reg-ID
                reg_id = f"{state}-REG-{number}-{year}"
                
                # Parse status
                current_status = parse_status_from_text(row['Last Status Date'])
                
                # Determine regulation type
                reg_type = determine_regulation_type(row)
                reg_type_counts[reg_type] = reg_type_counts.get(reg_type, 0) + 1
                
                # Calculate expiration date
                expiration_date = calculate_expiration_date(row)
                
                # Parse enhanced legal status
                legal_status = parse_enhanced_legal_status(row, current_status)
                legal_status_counts[legal_status] = legal_status_counts.get(legal_status, 0) + 1
                
                # Parse Last Action Date from the status text
                last_action_date = ''
                if row['Last Status Date']:
                    parts = row['Last Status Date'].split(' - ')
                    if parts and '/' in parts[0]:
                        last_action_date = parse_date(parts[0])
                
                # Collect policies
                specific_policies = collect_specific_policies(row)
                policy_categories = collect_policy_categories(row)
                
                # Handle checkboxes
                newly_tracked = "checked" if row.get('Newly Tracked', '').lower() == 'yes' else ''
                change_in_status = "checked" if row.get('Change in Status', '').lower() == 'yes' else ''
                
                transformed = {
                    'Reg-ID': reg_id,
                    'State': state,
                    'Number': number,
                    'Year': year,
                    'Title': row['Title'],
                    'Description': row['Summary'],
                    'Regulation Type': reg_type,  # NEW
                    'Current Status': current_status,
                    'History': '',
                    'StateNet History': row['Last Status Date'],
                    'Last Action Date': last_action_date,
                    'Introduction Date': parse_date(row['Intro Date']),
                    'Comment Period End': parse_date(row['Qualification Date']),
                    'Adopted Date': parse_date(row['Adopted Date']),
                    'Emergency Adopted Date': parse_date(row['Emergency Adopted Date']),
                    'Effective Date': parse_date(row['Effective Date']),
                    'Expiration Date': expiration_date,  # ENHANCED
                    'Intent (access)': '',  # For manual assignment
                    'Specific Policies Record Link': '',
                    'Categories (from Specific Policies Record Link)': '',
                    'Subcategories (from Specific Policies Record Link)': '',
                    'Headers (from Specific Policies Record Link)': '',
                    'Specific Policies (from Specific Policies Record Link)': '',
                    'Positive/Neutral/Restrictive (from Specific Policies Record Link)': '',
                    'Category Intent (from Specific Policies Record Link)': '',
                    'Specific Policies (access)': specific_policies,
                    'Policy Categories (Access)': policy_categories,
                    'Issuing Agency Link': row['Author/Source'],
                    'Agency Type (from Issuing Agency Link)': '',
                    'Priority Level (from Issuing Agency Link)': '',
                    'Parent Agency (from Issuing Agency Link)': '',
                    'State Reg ID': row['State ID'],
                    'Citation': row['Citation'],
                    'Contact': row['Contact'],
                    'StateNet Link': row['Links'],
                    'Related Bills': '',  # For future linking
                    'Supersedes': '',  # NEW
                    'Superseded By': '',  # NEW
                    'Legal Status': legal_status,  # ENHANCED
                    'Review Status': 'Needs Review',
                    'Website Blurb': '',
                    'Internal Notes': '',
                    'StateNet Regulations Import': '',
                    'Import Date': '',
                    'Last Updated': '',
                    'Last Updated By': '',
                    'Newly Tracked': newly_tracked,
                    'Change in Status': change_in_status,
                    'Last Status Date Text': row['Last Status Date']
                }
                
                writer.writerow(transformed)
    
    # Print summary
    print(f"✅ Enhanced import created: {output_file}")
    print("\n🎯 NEW FIELDS ADDED:")
    print("- Regulation Type field populated for all records")
    print("- Expiration Date calculated for emergency/temporary rules")
    print("- Enhanced Legal Status with litigation tracking")
    print("- Supersedes/Superseded By fields (ready for linking)")
    print("- Intent (access) field (ready for manual assignment)")
    
    print(f"\n📊 Regulation Type Distribution:")
    for reg_type, count in sorted(reg_type_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {reg_type}: {count}")
    
    print(f"\n⚖️ Legal Status Distribution:")
    for status, count in sorted(legal_status_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {status}: {count}")

if __name__ == "__main__":
    transform_to_enhanced_format()