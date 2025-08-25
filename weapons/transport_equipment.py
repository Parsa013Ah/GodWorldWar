
# تجهیزات حمل و نقل

TRANSPORT_EQUIPMENT = {
    'armored_truck': {
        'name': 'کامیون زرهی',
        'cost': 250000,
        'power': 100,
        'range': 400,
        'speed': 80,
        'armor': 400,
        'resources': {'iron': 15, 'aluminum': 8, 'copper': 5},
        'category': 'transport',
        'description': 'کامیون زرهی برای حمل منابع',
        'requirements': ['weapon_factory'],
        'production_time': 45,
        'cargo_capacity': 1000,
        'convoy_security': 25
    },
    'cargo_helicopter': {
        'name': 'هلیکوپتر باری',
        'cost': 800000,
        'power': 200,
        'range': 600,
        'speed': 250,
        'armor': 150,
        'resources': {'aluminum': 20, 'copper': 12, 'lithium': 8},
        'category': 'transport',
        'description': 'هلیکوپتر برای حمل سریع',
        'requirements': ['weapon_factory'],
        'production_time': 90,
        'cargo_capacity': 500,
        'convoy_security': 40,
        'speed_bonus': 2
    },
    'cargo_plane': {
        'name': 'هواپیمای باری',
        'cost': 3000000,
        'power': 300,
        'range': 2000,
        'speed': 600,
        'armor': 200,
        'resources': {'aluminum': 40, 'titanium': 15, 'copper': 20},
        'category': 'transport',
        'description': 'هواپیمای باری برای انتقال بین‌المللی',
        'requirements': ['weapon_factory', 'power_plant'],
        'production_time': 180,
        'cargo_capacity': 2000,
        'convoy_security': 60,
        'speed_bonus': 3
    },
    'stealth_transport': {
        'name': 'ترابر پنهان‌کار',
        'cost': 8000000,
        'power': 500,
        'range': 3000,
        'speed': 800,
        'armor': 600,
        'resources': {'titanium': 40, 'lithium': 25, 'gold': 15, 'aluminum': 30},
        'category': 'transport',
        'description': 'وسیله نقلیه پنهان‌کار پیشرفته',
        'requirements': ['weapon_factory', 'power_plant', 'refinery'],
        'production_time': 300,
        'cargo_capacity': 1500,
        'convoy_security': 90,
        'speed_bonus': 4,
        'stealth': True
    }
}
