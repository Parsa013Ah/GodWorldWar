
# بمب‌ها و مواد منفجره

BOMBS = {
    'simple_bomb': {
        'name': 'بمب ساده',
        'cost': 2000,
        'power': 60,
        'range': 0,
        'speed': 0,
        'armor': 0,
        'resources': {'nitro': 10, 'copper': 10, 'iron': 20, 'sulfur': 20},
        'category': 'bombs',
        'description': 'بمب دستی ساده',
        'requirements': ['weapon_factory'],
        'production_time': 15,
        'explosive_power': 'low'
    },
    'nuclear_bomb': {
        'name': 'بمب هسته‌ای ساده',
        'cost': 60000,
        'power': 2000,
        'range': 0,
        'speed': 0,
        'armor': 0,
        'resources': {'iron': 30, 'uranium': 6, 'sulfur': 36},
        'category': 'bombs',
        'description': 'بمب هسته‌ای کوچک',
        'requirements': ['weapon_factory', 'power_plant'],
        'production_time': 180,
        'explosive_power': 'nuclear',
        'radioactive': True
    }
}
