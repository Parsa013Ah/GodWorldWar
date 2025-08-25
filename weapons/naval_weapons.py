
# تسلیحات دریایی

NAVAL_WEAPONS = {
    'aircraft_carrier_full': {
        'name': 'ناو هواپیمابر (همراه با جنگنده)',
        'cost': 990000,
        'power': 60000,
        'range': 3000,
        'speed': 25,
        'armor': 8000,
        'resources': {'f35': 20, 'iron': 3000, 'aluminum': 1000, 'titanium': 50, 'uranium': 50, 'copper': 700},
        'category': 'naval',
        'description': 'ناو هواپیمابر کامل با جنگنده‌ها',
        'requirements': ['weapon_factory', 'refinery', 'power_plant'],
        'production_time': 600
    },
    'warship': {
        'name': 'ناو جنگی',
        'cost': 120000,
        'power': 9000,
        'range': 2000,
        'speed': 35,
        'armor': 3500,
        'resources': {'iron': 1200, 'aluminum': 300, 'titanium': 15, 'copper': 150, 'oil': 2100},
        'category': 'naval',
        'description': 'ناو جنگی سنگین',
        'requirements': ['weapon_factory', 'refinery'],
        'production_time': 240
    },
    'destroyer': {
        'name': 'ناوشکن',
        'cost': 90000,
        'power': 6000,
        'range': 1800,
        'speed': 45,
        'armor': 2500,
        'resources': {'iron': 900, 'aluminum': 210, 'titanium': 9, 'copper': 90, 'oil': 1500},
        'category': 'naval',
        'description': 'ناوشکن سریع',
        'requirements': ['weapon_factory', 'refinery'],
        'production_time': 200
    },
    'nuclear_submarine': {
        'name': 'زیردریایی هسته‌ای',
        'cost': 150000,
        'power': 12000,
        'range': 2500,
        'speed': 30,
        'armor': 4000,
        'resources': {'uranium': 12, 'iron': 900, 'titanium': 6, 'copper': 60, 'coal': 150},
        'category': 'naval',
        'description': 'زیردریایی با موتور هسته‌ای',
        'requirements': ['weapon_factory', 'refinery', 'power_plant'],
        'production_time': 300
    },
    'patrol_ship': {
        'name': 'کشتی گشتی',
        'cost': 60000,
        'power': 3000,
        'range': 1200,
        'speed': 50,
        'armor': 1500,
        'resources': {'iron': 600, 'aluminum': 240, 'oil': 1200, 'copper': 60, 'titanium': 3},
        'category': 'naval',
        'description': 'کشتی گشتی سریع',
        'requirements': ['weapon_factory', 'refinery'],
        'production_time': 150
    },
    'patrol_boat': {
        'name': 'قایق گشتی',
        'cost': 30000,
        'power': 1000,
        'range': 800,
        'speed': 65,
        'armor': 500,
        'resources': {'iron': 200, 'aluminum': 80, 'oil': 600, 'copper': 21, 'titanium': 1},
        'category': 'naval',
        'description': 'قایق گشتی سبک',
        'requirements': ['weapon_factory'],
        'production_time': 90
    },
    'amphibious_ship': {
        'name': 'کشتی آبی-خاکی',
        'cost': 90000,
        'power': 4500,
        'range': 1500,
        'speed': 40,
        'armor': 2000,
        'resources': {'iron': 600, 'aluminum': 240, 'oil': 1200, 'copper': 60, 'titanium': 3, 'coal': 1800},
        'category': 'naval',
        'description': 'کشتی عملیات آبی-خاکی',
        'requirements': ['weapon_factory', 'refinery'],
        'production_time': 180
    }
}
