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
        'description': 'اسیب کم و برد کم',
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
        'description': 'اسیب کم اما برد زیاد، بیشتر برای ساخت موشک هسته‌ای و یا بقیه موشک‌ها استفاده می‌شود',
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
        'description': 'ارزان‌ترین موشک هسته‌ای بازی',
        'requirements': ['weapon_factory', 'power_plant'],
        'production_time': 120,
        'destructive_power': 'high',
        'radioactive': True
    }
}