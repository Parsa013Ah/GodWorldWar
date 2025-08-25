
# موشک‌ها

MISSILES = {
    'missile': {
        'name': 'موشک بالستیک',
        'cost': 5000000,
        'power': 8000,
        'range': 5000,
        'speed': 3000,
        'armor': 0,
        'resources': {'iron': 40, 'aluminum': 25, 'uranium': 15, 'nitro': 30},
        'category': 'missiles',
        'description': 'موشک بالستیک متوسط برد',
        'requirements': ['weapon_factory', 'refinery'],
        'production_time': 240,
        'destructive_power': 'high'
    },
    'nuclear_missile': {
        'name': 'موشک هسته‌ای',
        'cost': 25000000,
        'power': 50000,
        'range': 8000,
        'speed': 4000,
        'armor': 0,
        'resources': {'uranium': 100, 'plutonium': 25, 'titanium': 30, 'nitro': 50},
        'category': 'missiles',
        'description': 'موشک با کلاهک هسته‌ای',
        'requirements': ['weapon_factory', 'refinery', 'power_plant'],
        'production_time': 600,
        'destructive_power': 'extreme',
        'radioactive': True
    },
    'trident2_nuclear': {
        'name': 'ترایدنت-2 هسته‌ای',
        'cost': 50000000,
        'power': 120000,
        'range': 12000,
        'speed': 5000,
        'armor': 200,
        'resources': {'uranium': 200, 'plutonium': 50, 'titanium': 60, 'lithium': 40},
        'category': 'special_missiles',
        'description': 'موشک بین‌قاره‌ای آمریکا',
        'requirements': ['weapon_factory', 'refinery', 'power_plant'],
        'production_time': 720,
        'destructive_power': 'catastrophic',
        'submarine_launch': True
    },
    'satan2_nuclear': {
        'name': 'سارمات هسته‌ای',
        'cost': 60000000,
        'power': 150000,
        'range': 18000,
        'speed': 6000,
        'armor': 300,
        'resources': {'uranium': 250, 'plutonium': 60, 'titanium': 80, 'lithium': 50},
        'category': 'special_missiles',
        'description': 'موشک بین‌قاره‌ای روسیه',
        'requirements': ['weapon_factory', 'refinery', 'power_plant'],
        'production_time': 800,
        'destructive_power': 'world_ending',
        'multiple_warheads': True
    }
}
