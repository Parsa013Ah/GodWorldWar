#!/usr/bin/env python3
"""Complete test of weapon production system"""

import sqlite3
import sys
import traceback

def test_weapon_production():
    """Test the complete weapon production flow"""
    try:
        # Import required classes
        from database import Database
        from game_logic import GameLogic
        from config import Config
        
        print("=== TESTING WEAPON PRODUCTION SYSTEM ===")
        
        # Initialize
        db = Database()
        game_logic = GameLogic(db)
        
        # Get a test user
        conn = sqlite3.connect('dragonrp.db')
        cursor = conn.cursor()
        
        # Find a user with some money and resources
        cursor.execute("""
            SELECT p.user_id, p.money, p.country_name 
            FROM players p 
            WHERE p.money > 100000 
            LIMIT 1
        """)
        user_data = cursor.fetchone()
        
        if not user_data:
            print("❌ No user found with enough money")
            return
            
        user_id, user_money, country = user_data
        print(f"Testing with User {user_id} ({country}) - Money: ${user_money:,}")
        
        # Check current weapons
        weapons_before = db.get_player_weapons(user_id)
        rifle_before = weapons_before.get('rifle', 0)
        print(f"Current rifles: {rifle_before}")
        
        # Check resources
        resources = db.get_player_resources(user_id)
        print(f"Current resources: iron={resources.get('iron', 0)}, copper={resources.get('copper', 0)}")
        
        # Get rifle config
        rifle_config = Config.WEAPONS.get('rifle', {})
        print(f"Rifle config: {rifle_config}")
        
        # Try to produce 1 rifle
        print("\n=== ATTEMPTING TO PRODUCE 1 RIFLE ===")
        result = game_logic.produce_weapon(user_id, 'rifle', 1)
        print(f"Production result: {result}")
        
        # Check weapons after
        weapons_after = db.get_player_weapons(user_id)
        rifle_after = weapons_after.get('rifle', 0)
        print(f"Rifles after production: {rifle_after}")
        
        # Check if rifle was actually added
        if rifle_after > rifle_before:
            print("✅ WEAPON PRODUCTION SUCCESSFUL!")
        else:
            print("❌ WEAPON PRODUCTION FAILED!")
            
            # Additional debugging
            print("\n=== ADDITIONAL DEBUGGING ===")
            
            # Check if user exists in weapons table
            cursor.execute("SELECT COUNT(*) FROM weapons WHERE user_id = ?", (user_id,))
            weapons_table_exists = cursor.fetchone()[0] > 0
            print(f"User exists in weapons table: {weapons_table_exists}")
            
            # Check raw database value
            cursor.execute("SELECT rifle FROM weapons WHERE user_id = ?", (user_id,))
            raw_rifle = cursor.fetchone()
            print(f"Raw rifle value in DB: {raw_rifle}")
            
            # Check weapons table structure
            cursor.execute("PRAGMA table_info(weapons)")
            columns = cursor.fetchall()
            has_rifle_column = any(col[1] == 'rifle' for col in columns)
            print(f"Weapons table has 'rifle' column: {has_rifle_column}")
        
        conn.close()
        
    except Exception as e:
        print(f"ERROR: {e}")
        traceback.print_exc()

def check_database_constraints():
    """Check for any database constraints or issues"""
    try:
        print("\n=== CHECKING DATABASE CONSTRAINTS ===")
        
        conn = sqlite3.connect('dragonrp.db')
        cursor = conn.cursor()
        
        # Check if there are any foreign key violations
        cursor.execute("PRAGMA foreign_key_check")
        fk_violations = cursor.fetchall()
        if fk_violations:
            print(f"Foreign key violations: {fk_violations}")
        else:
            print("No foreign key violations")
        
        # Check database integrity
        cursor.execute("PRAGMA integrity_check")
        integrity = cursor.fetchone()[0]
        print(f"Database integrity: {integrity}")
        
        # Check weapons table triggers or constraints
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='trigger' AND tbl_name='weapons'")
        triggers = cursor.fetchall()
        if triggers:
            print(f"Weapons table triggers: {triggers}")
        else:
            print("No triggers on weapons table")
            
        conn.close()
        
    except Exception as e:
        print(f"Database check error: {e}")

if __name__ == "__main__":
    test_weapon_production()
    check_database_constraints()