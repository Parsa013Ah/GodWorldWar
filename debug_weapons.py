#!/usr/bin/env python3
"""Debug script to check weapons table and player weapons data"""

import sqlite3
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_database():
    """Check database structure and player weapons"""
    try:
        conn = sqlite3.connect('dragonrp.db')
        cursor = conn.cursor()
        
        print("=== DATABASE STRUCTURE ===")
        
        # Check if weapons table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='weapons';")
        weapons_table = cursor.fetchone()
        print(f"Weapons table exists: {bool(weapons_table)}")
        
        if weapons_table:
            # Check weapons table structure
            cursor.execute("PRAGMA table_info(weapons);")
            columns = cursor.fetchall()
            print(f"\nWeapons table columns ({len(columns)}):")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
            
            # Check sample data
            cursor.execute("SELECT user_id, rifle, tank, fighter_jet FROM weapons LIMIT 5;")
            sample_data = cursor.fetchall()
            print(f"\nSample weapons data:")
            for row in sample_data:
                print(f"  User {row[0]}: rifle={row[1]}, tank={row[2]}, fighter_jet={row[3]}")
        
        # Check recent transactions
        print("\n=== RECENT BUILD TRANSACTIONS ===")
        cursor.execute("""
            SELECT builder_id, item_type, first_build_date 
            FROM build_tracking 
            ORDER BY first_build_date DESC 
            LIMIT 5
        """)
        builds = cursor.fetchall()
        for build in builds:
            print(f"  User {build[0]} built {build[1]} at {build[2]}")
        
        # Check marketplace listings
        print("\n=== MARKETPLACE LISTINGS ===")
        cursor.execute("""
            SELECT seller_id, item_type, quantity 
            FROM market_listings 
            WHERE item_category = 'weapon' AND status = 'active'
            LIMIT 5
        """)
        listings = cursor.fetchall()
        for listing in listings:
            print(f"  User {listing[0]} selling {listing[1]} x{listing[2]}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

def test_add_weapon():
    """Test adding weapon to a user"""
    try:
        from database import Database
        from marketplace import Marketplace
        db = Database()
        marketplace = Marketplace(db)
        
        # Get first user
        conn = sqlite3.connect('dragonrp.db')
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM players LIMIT 1;")
        result = cursor.fetchone()
        
        if result:
            user_id = result[0]
            print(f"\n=== TESTING ADD WEAPON FOR USER {user_id} ===")
            
            # Get current weapons
            weapons_before = db.get_player_weapons(user_id)
            rifle_before = weapons_before.get('rifle', 0)
            print(f"Rifles before: {rifle_before}")
            
            # Add a rifle
            db.add_weapon(user_id, 'rifle', 1)
            print("Added 1 rifle")
            
            # Check after
            weapons_after = db.get_player_weapons(user_id)
            rifle_after = weapons_after.get('rifle', 0)
            print(f"Rifles after: {rifle_after}")
            
            if rifle_after > rifle_before:
                print("✅ Weapon addition SUCCESSFUL")
            else:
                print("❌ Weapon addition FAILED")
            
            # Test marketplace verification
            print("\n=== TESTING MARKETPLACE VERIFICATION ===")
            has_rifles = marketplace.verify_seller_inventory(user_id, 'weapon', 'rifle', 1)
            print(f"Can sell 1 rifle: {has_rifles}")
            
            has_many_rifles = marketplace.verify_seller_inventory(user_id, 'weapon', 'rifle', 1000)
            print(f"Can sell 1000 rifles: {has_many_rifles}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error in test: {e}")

if __name__ == "__main__":
    check_database()
    test_add_weapon()