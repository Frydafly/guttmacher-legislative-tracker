#!/usr/bin/env python3
"""
One-off script to migrate only 2023 data
"""

from pathlib import Path
from migrate import GuttmacherMigration
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    print("=" * 70)
    print("MIGRATING 2023 DATA ONLY")
    print("=" * 70)
    
    # Create migrator instance
    migrator = GuttmacherMigration()
    
    # Process only the 2023 file
    db_file = migrator.data_path / "12-15-23.accdb"
    
    if not db_file.exists():
        print(f"❌ File not found: {db_file}")
        return
    
    print(f"📁 Processing: {db_file.name}")
    
    try:
        # Process the 2023 database file
        success = migrator.process_db_file(db_file)
        
        if success:
            print("✅ Successfully migrated 2023 data!")
            
            # Now recreate the unified views to include 2023
            print("\n🔄 Recreating unified views to include 2023...")
            migrator.create_unified_view()
            migrator.create_raw_data_tracking_view()
            
            # Recreate comprehensive view
            print("\n🔄 Recreating comprehensive view...")
            migrator.create_looker_table()
            
            print("\n✅ All views updated to include 2023 data!")
            
            # Show summary
            print("\n📊 Quick Summary:")
            print(f"- Total bills migrated: {migrator.stats['total_bills']}")
            print(f"- Files processed: {migrator.stats['files_processed']}")
            if migrator.stats['errors']:
                print(f"- Errors: {len(migrator.stats['errors'])}")
                for error in migrator.stats['errors']:
                    print(f"  - {error}")
        else:
            print("❌ Failed to migrate 2023 data")
            
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()