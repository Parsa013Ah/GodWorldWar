#!/usr/bin/env python3
"""Test the new distance-based attack system"""

from config import Config

def test_distance_system():
    print("=== TESTING DISTANCE-BASED ATTACK SYSTEM ===\n")
    
    # Test countries
    test_cases = [
        ('IR', 'TR'),   # Iran to Turkey (neighbors)
        ('IR', 'SA'),   # Iran to Saudi (regional)
        ('IR', 'US'),   # Iran to USA (intercontinental)
        ('KP', 'CN'),   # North Korea to China (neighbors)
        ('KP', 'JP'),   # North Korea to Japan (neighbors)
        ('US', 'RU'),   # USA to Russia (intercontinental)
    ]
    
    # Mock player weapons
    player_weapons = {
        'rifle': 100,
        'tank': 50,
        'f22': 25,
        'ballistic_missile': 10,
        'trident2_nuclear': 5
    }
    
    for country1, country2 in test_cases:
        print(f"🌍 {Config.COUNTRIES[country1]} -> {Config.COUNTRIES[country2]}")
        
        # Get distance type
        distance_type = Config.get_country_distance_type(country1, country2)
        print(f"   📏 فاصله: {distance_type}")
        
        # Get available weapons
        available_weapons = Config.get_available_weapons_for_attack(country1, country2, player_weapons)
        print(f"   ⚔️ سلاح‌های قابل استفاده: {len(available_weapons)} نوع")
        
        for weapon, count in available_weapons.items():
            weapon_name = Config.WEAPONS.get(weapon, {}).get('name', weapon)
            print(f"      - {weapon_name}: {count}")
        
        print()

if __name__ == "__main__":
    test_distance_system()