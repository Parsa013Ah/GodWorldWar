
# جت‌های پیشرفته

ADVANCED_JETS = {
    'f22': {
        'name': 'اف-22 رپتور',
        'cost': 15000000,
        'power': 5500,
        'range': 3000,
        'speed': 2400,
        'armor': 800,
        'resources': {'titanium': 50, 'uranium': 10, 'lithium': 20, 'gold': 15},
        'category': 'advanced_jets',
        'description': 'جنگنده پنهان‌کار آمریکایی',
        'requirements': ['weapon_factory', 'power_plant', 'refinery'],
        'production_time': 360,
        'stealth': True,
        'air_superiority': 95
    },
    'f35': {
        'name': 'اف-35 لایتنینگ',
        'cost': 12000000,
        'power': 4800,
        'range': 2500,
        'speed': 1900,
        'armor': 600,
        'resources': {'titanium': 40, 'aluminum': 30, 'lithium': 15, 'gold': 12},
        'category': 'advanced_jets',
        'description': 'جنگنده چندمنظوره پیشرفته',
        'requirements': ['weapon_factory', 'power_plant'],
        'production_time': 300,
        'multirole': True,
        'air_superiority': 88
    },
    'su57': {
        'name': 'سوخو-57',
        'cost': 13500000,
        'power': 5200,
        'range': 2800,
        'speed': 2100,
        'armor': 750,
        'resources': {'titanium': 45, 'uranium': 8, 'aluminum': 35, 'lithium': 18},
        'category': 'advanced_jets',
        'description': 'جنگنده پنهان‌کار روسی',
        'requirements': ['weapon_factory', 'power_plant', 'refinery'],
        'production_time': 320,
        'stealth': True,
        'air_superiority': 92
    },
    'j20': {
        'name': 'جی-20',
        'cost': 11000000,
        'power': 4500,
        'range': 2200,
        'speed': 2000,
        'armor': 650,
        'resources': {'titanium': 38, 'aluminum': 32, 'lithium': 16, 'gold': 10},
        'category': 'advanced_jets',
        'description': 'جنگنده پنهان‌کار چینی',
        'requirements': ['weapon_factory', 'power_plant'],
        'production_time': 280,
        'stealth': True,
        'air_superiority': 85
    }
}
