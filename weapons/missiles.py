
# موشک‌ها

MISSILES = {
    'simple_missile': {
        'name': 'موشک ساده',
        'cost': 3000,
        'power': 60,
        'range': 500,
        'speed': 800,
        'armor': 0,
        'resources': {'nitro': 10, 'copper': 10, 'iron': 20, 'sulfur': 20, 'coal': 10},
        'category': 'missiles',
        'description': 'موشک کوتاه برد',
        'requirements': ['weapon_factory'],
        'production_time': 30,
        'destructive_power': 'low'
    },
    'ballistic_missile': {
        'name': 'موشک بالستیک ساده',
        'cost': 9000,
        'power': 80,
        'range': 2000,
        'speed': 1500,
        'armor': 0,
        'resources': {'nitro': 15, 'copper': 15, 'iron': 40, 'sulfur': 40, 'coal': 20},
        'category': 'missiles',
        'description': 'موشک بالستیک متوسط برد',
        'requirements': ['weapon_factory'],
        'production_time': 60,
        'destructive_power': 'medium'
    },
    'nuclear_missile': {
        'name': 'موشک هسته‌ای ساده',
        'cost': 9000,
        'power': 2000,
        'range': 2000,
        'speed': 1500,
        'armor': 0,
        'resources': {'nuclear_bomb': 1, 'ballistic_missile': 1, 'iron': 30, 'sulfur': 30},
        'category': 'missiles',
        'description': 'موشک با کلاهک هسته‌ای',
        'requirements': ['weapon_factory', 'power_plant'],
        'production_time': 120,
        'destructive_power': 'high',
        'radioactive': True
    },
    'missile': {
        'name': 'موشک بالستیک',
        'cost': 5000000,
        'power': 8000,
        'range': 5000,
        'speed': 3000,
        'armor': 0,
        'resources': {'iron': 40, 'aluminum': 25, 'uranium': 15, 'nitro': 30},
        'category': 'missiles',
        'description': 'موشک بالستیک پیشرفته',
        'requirements': ['weapon_factory', 'refinery'],
        'production_time': 240,
        'destructive_power': 'very_high'
    },
    'icbm': {
        'name': 'موشک قاره‌پیما',
        'cost': 25000000,
        'power': 6000,
        'range': 15000,
        'speed': 5000,
        'armor': 100,
        'resources': {'uranium': 30, 'titanium': 20, 'fuel': 40},
        'category': 'missiles',
        'description': 'موشک بین‌قاره‌ای',
        'requirements': ['weapon_factory', 'refinery', 'power_plant'],
        'production_time': 600,
        'destructive_power': 'extreme'
    }
}
