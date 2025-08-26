#!/usr/bin/env python3
"""Debug specific user's weapon production"""

import sqlite3
from database import Database
from game_logic import GameLogic

def debug_user_weapons():
    user_id = 7716228404  # User ID from logs
    
    print(f"=== DEBUGGING USER {user_id} ===")
    
    db = Database()
    
    # Check if user exists in players table
    conn = sqlite3.connect('dragonrp.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT user_id, country_name, money FROM players WHERE user_id = ?", (user_id,))
    player = cursor.fetchone()
    
    if player:
        print(f"Player found: {player}")
    else:
        print("❌ Player not found in players table!")
        return
    
    # Check if user exists in weapons table
    cursor.execute("SELECT COUNT(*) FROM weapons WHERE user_id = ?", (user_id,))
    weapons_exists = cursor.fetchone()[0] > 0
    print(f"User exists in weapons table: {weapons_exists}")
    
    if not weapons_exists:
        print("❌ User not found in weapons table! This is the problem!")
        print("Creating weapons entry for user...")
        cursor.execute("INSERT INTO weapons (user_id) VALUES (?)", (user_id,))
        conn.commit()
        print("✅ Weapons entry created!")
    
    # Get current weapons
    weapons = db.get_player_weapons(user_id)
    print(f"Current weapons: {weapons}")
    
    # Test adding a rifle directly
    print("\n=== TESTING DIRECT WEAPON ADD ===")
    current_rifles = weapons.get('rifle', 0)
    print(f"Current rifles: {current_rifles}")
    
    db.add_weapon(user_id, 'rifle', 1)
    
    new_weapons = db.get_player_weapons(user_id)
    new_rifles = new_weapons.get('rifle', 0)
    print(f"Rifles after add: {new_rifles}")
    
    if new_rifles > current_rifles:
        print("✅ Direct weapon add works!")
    else:
        print("❌ Direct weapon add failed!")
    
    conn.close()

if __name__ == "__main__":
    debug_user_weapons()