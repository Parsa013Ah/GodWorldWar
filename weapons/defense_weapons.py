
# سلاح‌های دفاعی

DEFENSE_WEAPONS = {
    'air_defense': {
        'name': 'پدافند هوایی',
        'cost': 800000,
        'power': 1500,
        'range': 1000,
        'speed': 0,
        'armor': 600,
        'resources': {'iron': 25, 'aluminum': 15, 'copper': 12},
        'category': 'defense',
        'description': 'سیستم دفاع ضدهوایی',
        'requirements': ['weapon_factory'],
        'production_time': 90,
        'defense_bonus': 150
    },
    'missile_shield': {
        'name': 'سپر موشکی',
        'cost': 1500000,
        'power': 2500,
        'range': 1500,
        'speed': 0,
        'armor': 1000,
        'resources': {'titanium': 20, 'aluminum': 25, 'uranium': 5},
        'category': 'defense',
        'description': 'سیستم رهگیری موشک‌ها',
        'requirements': ['weapon_factory', 'power_plant'],
        'production_time': 150,
        'defense_bonus': 250
    },
    'cyber_shield': {
        'name': 'سپر سایبری',
        'cost': 900000,
        'power': 800,
        'range': 0,
        'speed': 0,
        'armor': 0,
        'resources': {'lithium': 15, 'gold': 8, 'copper': 20},
        'category': 'defense',
        'description': 'سیستم دفاع سایبری',
        'requirements': ['weapon_factory', 'power_plant'],
        'production_time': 80,
        'defense_bonus': 120,
        'cyber_defense': True
    }
}
