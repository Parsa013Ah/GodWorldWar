#!/usr/bin/env python3
"""Fix weapon production for specific user"""

import sqlite3
from database import Database
from game_logic import GameLogic

def fix_user_production():
    user_id = 7716228404  # Your user ID
    
    print(f"=== FIXING PRODUCTION FOR USER {user_id} ===")
    
    db = Database()
    game_logic = GameLogic(db)
    
    # Test production step by step
    print("Testing rifle production...")
    
    # Get current state
    player = db.get_player(user_id)
    weapons_before = db.get_player_weapons(user_id)
    print(f"Money before: ${player['money']:,}")
    print(f"Rifles before: {weapons_before.get('rifle', 0)}")
    
    # Try production
    result = game_logic.produce_weapon(user_id, 'rifle', 1)
    print(f"Production result: {result}")
    
    # Check after
    player_after = db.get_player(user_id)
    weapons_after = db.get_player_weapons(user_id)
    print(f"Money after: ${player_after['money']:,}")
    print(f"Rifles after: {weapons_after.get('rifle', 0)}")
    
    # Check if it worked
    if weapons_after.get('rifle', 0) > weapons_before.get('rifle', 0):
        print("✅ Production works!")
    else:
        print("❌ Production failed!")
        
        # Check database directly
        conn = sqlite3.connect('dragonrp.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT rifle FROM weapons WHERE user_id = ?", (user_id,))
        raw_rifle = cursor.fetchone()
        print(f"Raw database rifle value: {raw_rifle}")
        
        # Try manual fix
        print("Trying manual database update...")
        cursor.execute("UPDATE weapons SET rifle = rifle + 1 WHERE user_id = ?", (user_id,))
        conn.commit()
        
        # Check again
        cursor.execute("SELECT rifle FROM weapons WHERE user_id = ?", (user_id,))
        new_rifle = cursor.fetchone()
        print(f"After manual update: {new_rifle}")
        
        conn.close()

if __name__ == "__main__":
    fix_user_production()