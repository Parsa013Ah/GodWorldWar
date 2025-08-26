#!/usr/bin/env python3
"""Test your specific user weapons"""

from database import Database

def test_your_weapons():
    user_id = 7716228404  # Your ID
    
    db = Database()
    
    print(f"=== CHECKING YOUR WEAPONS (User {user_id}) ===")
    
    # Get your current weapons
    weapons = db.get_player_weapons(user_id)
    
    print(f"Your current weapons:")
    print(f"🔫 Rifle: {weapons.get('rifle', 0)}")
    print(f"🚗 Tank: {weapons.get('tank', 0)}")
    print(f"✈️ Fighter Jet: {weapons.get('fighter_jet', 0)}")
    print(f"🚁 Drone: {weapons.get('drone', 0)}")
    print(f"🚀 Missile: {weapons.get('missile', 0)}")
    print(f"🚢 Warship: {weapons.get('warship', 0)}")
    print(f"🛡 Air Defense: {weapons.get('air_defense', 0)}")
    print(f"🚀 Missile Shield: {weapons.get('missile_shield', 0)}")
    print(f"💻 Cyber Shield: {weapons.get('cyber_shield', 0)}")
    print(f"💣 Nuclear Bomb: {weapons.get('nuclear_bomb', 0)}")
    
    # Now add one rifle manually to test
    print("\n=== ADDING 1 RIFLE FOR TEST ===")
    db.add_weapon(user_id, 'rifle', 1)
    
    # Check again
    weapons_after = db.get_player_weapons(user_id)
    print(f"Rifles after adding 1: {weapons_after.get('rifle', 0)}")
    
    if weapons_after.get('rifle', 0) > weapons.get('rifle', 0):
        print("✅ Manual add works!")
        print("The problem is likely in the UI refresh or bot message display")
    else:
        print("❌ Manual add failed!")

if __name__ == "__main__":
    test_your_weapons()